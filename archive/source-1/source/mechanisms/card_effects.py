"""Card-effects interpreter — the sim reads each card's capability blocks (front /
back) and works out what to do. No per-card logic lives in the sim; the cards are
self-describing data (game/reef_cards.gamespec.md).

Effect-verb vocabulary (closed):
  disposition            to_player_hand | play_at_location | set_aside |
                         set_beside_deck | resolve_now | discard
  set_track/change_track {track, value|target,delta}
  provides_icon          {icon, amount, when?}   (presence icon, not consumed)
  produce_resource       {resource, amount}      (materials / biomass / power …)
  consume_population     {from: <filter>, amount, then:[…], else:[…]}
  convert_track          {from, to, amount}      (choose_one option)
  refill_track           {track, per_icon}
  player_obligation      {each_player: [ {option}, … ]}
  for_each               {filter, do:[…], if_none: [remove_self | …]}
  passive                [ provides_icon | {action: …} ]
  reveal_cards/each_player_chooses/conditional_gain/dilemma/choose_one
  tuck / instruction / narrative / remove_self
  status: unresolved     (a tracked gap)

Conditions (structured):
  { self_pop_ge: N }
  { location_cards_pop_ge: { pop: P, count: C } }
  { card_track_ge: { card: <id>, track: <t>, value: V } }
  { board_icon_ge: { icon: <i>, value: V } }
  { all: [ … ] } / { any: [ … ] }

Targets: 'self' | 'card.<id>' | a filter {type|keyword, at: location, exclude_self, choose}.

Cross-card / keyword conditions (added for Crash Flats + Kelp Cathedral):
  { keyword_track_ge: { keyword: <k>, track: <t>, value: V } }  (any keyword card at threshold)
  { keyword_present: { type?: <t>, keyword?: <k> } }             (any such card in play here)
  { keyword_count_ge: { keyword: <k>, count: C } }               (C+ such cards present)
  { not: <condition> }                                           (negation, e.g. 'no Flora here')
"""
from __future__ import annotations
from dataclasses import dataclass, field

TRACK_MAX = {"population": 5, "abundance": 5, "rations": 8, "scanning": 6}


@dataclass
class InPlay:
    id: str
    tracks: dict = field(default_factory=dict)
    front: dict = field(default_factory=dict)
    removed: bool = False


@dataclass
class Player:
    name: str
    role_id: str | None = None
    hand: list = field(default_factory=list)
    passives: list = field(default_factory=list)


@dataclass
class Board:
    effects: dict
    players: list = field(default_factory=list)
    in_play: dict = field(default_factory=dict)
    tucked_icons: dict = field(default_factory=dict)
    board_icons: dict = field(default_factory=dict)     # e.g. reactor icons present
    resources: dict = field(default_factory=dict)       # materials / biomass / power pools
    tracks: dict = field(default_factory=dict)          # location tracks (rations …)
    built: list = field(default_factory=list)           # salvage recipes crafted/installed here
    gained: list = field(default_factory=list)          # knowledge cards already taken to a hand
    log: list = field(default_factory=list)

    def note(self, kind, msg):
        self.log.append((kind, msg))


def _as_list(x):
    return [] if x is None else (x if isinstance(x, list) else [x])


def _short(cid):
    return cid.split("_", 3)[-1] if cid.count("_") >= 3 else cid


# ----------------------------------------------------------------- conditions
def eval_condition(cond, board: Board, subject: InPlay | None):
    if cond is None:
        return True
    if "all" in cond:
        return all(eval_condition(c, board, subject) for c in cond["all"])
    if "any" in cond:
        return any(eval_condition(c, board, subject) for c in cond["any"])
    if "self_pop_ge" in cond:
        return subject is not None and subject.tracks.get("population", 0) >= cond["self_pop_ge"]
    if "self_track_ge" in cond:
        s = cond["self_track_ge"]
        return subject is not None and subject.tracks.get(s["track"], 0) >= s["value"]
    if "location_cards_pop_ge" in cond:
        s = cond["location_cards_pop_ge"]
        n = sum(1 for ip in board.in_play.values() if not ip.removed and ip.tracks.get("population", 0) >= s["pop"])
        return n >= s["count"]
    if "card_track_ge" in cond:
        s = cond["card_track_ge"]
        ip = board.in_play.get(s["card"])
        return ip is not None and not ip.removed and ip.tracks.get(s["track"], 0) >= s["value"]
    if "board_icon_ge" in cond:
        s = cond["board_icon_ge"]
        return board.board_icons.get(s["icon"], 0) >= s["value"]
    if "not" in cond:
        return not eval_condition(cond["not"], board, subject)
    if "keyword_track_ge" in cond:
        s = cond["keyword_track_ge"]
        pool = resolve_target({"keyword": s.get("keyword"), "type": s.get("type")}, board, subject)
        return any(ip.tracks.get(s["track"], 0) >= s["value"] for ip in pool)
    if "keyword_present" in cond:
        s = cond["keyword_present"]
        return len(resolve_target({"keyword": s.get("keyword"), "type": s.get("type")}, board, subject)) > 0
    if "keyword_count_ge" in cond:
        s = cond["keyword_count_ge"]
        pool = resolve_target({"keyword": s.get("keyword"), "type": s.get("type")}, board, subject)
        return len(pool) >= s["count"]
    return False


# ----------------------------------------------------------------- targeting
def resolve_target(target, board: Board, subject: InPlay | None):
    if target == "self":
        return [subject] if subject else []
    if isinstance(target, str) and target.startswith("card."):
        cid = target.split(".", 1)[1]
        ip = board.in_play.get(cid)
        return [ip] if ip and not ip.removed else []
    if isinstance(target, dict):
        want_type = target.get("type"); want_kw = target.get("keyword")
        hits = []
        for ip in board.in_play.values():
            if ip.removed or ip is subject and target.get("exclude_self"):
                continue
            ct = ip.front.get("_card_type")
            kws = ip.front.get("_keywords") or []
            if (want_type is None or ct == want_type) and (want_kw is None or want_kw in kws):
                hits.append(ip)
        if target.get("choose") == "player" and hits:
            return [hits[0]]
        return hits
    return []


# ----------------------------------------------------------------- icons (presence)
def available_icons(board: Board):
    icons = {}

    def add(spec, subj):
        if eval_condition(spec.get("when"), board, subj):
            icons[spec["icon"]] = icons.get(spec["icon"], 0) + spec.get("amount", 1)

    for ip in board.in_play.values():
        if ip.removed:
            continue
        for pi in _as_list(ip.front.get("provides_icon")):
            add(pi, ip)
    for p in board.players:
        for pas in p.passives:
            if "provides_icon" in pas:
                add(pas["provides_icon"], None)
        for cid in p.hand:
            for pi in _as_list(board.effects.get(cid, {}).get("front", {}).get("provides_icon")):
                add(pi, board.in_play.get(cid))
    for icon, amt in board.tucked_icons.items():
        icons[icon] = icons.get(icon, 0) + amt
    return icons


# ----------------------------------------------------------------- effect execution
def _clamp(track, v):
    return max(0, min(TRACK_MAX.get(track, 5), v))


def apply_effect(eff, board: Board, subject: InPlay | None):
    if not isinstance(eff, dict):
        return
    if eff.get("status") == "unresolved":
        board.note("unresolved", eff.get("text", "prose effect not encoded"))
        return
    if "set_track" in eff:
        s = eff["set_track"]
        for t in resolve_target(s.get("target", "self"), board, subject):
            t.tracks[s["track"]] = s["value"]
            board.note("set_track", "%s.%s = %d" % (_short(t.id), s["track"], s["value"]))
    elif "set_location_track" in eff:
        s = eff["set_location_track"]
        board.tracks[s["track"]] = s["value"]
    elif "choose_one" in eff:
        # policy: prefer an option that grows a track (change_track +delta) within range; else the first
        opts = eff["choose_one"]
        pick = None
        for o in opts:
            ct = o.get("change_track") if isinstance(o, dict) else None
            if ct and ct.get("delta", 0) > 0:
                tgt = resolve_target(ct.get("target", "self"), board, subject)
                if tgt and tgt[0].tracks.get(ct["track"], 0) < TRACK_MAX.get(ct["track"], 5):
                    pick = o; break
        apply_effect(pick or opts[0], board, subject)
    elif "change_track" in eff:
        s = eff["change_track"]
        for t in resolve_target(s["target"], board, subject):
            t.tracks[s["track"]] = _clamp(s["track"], t.tracks.get(s["track"], 0) + s["delta"])
            board.note("change_track", "%s.%s -> %d (%+d)" % (_short(t.id), s["track"], t.tracks[s["track"]], s["delta"]))
    elif "consume_population" in eff:
        s = eff["consume_population"]
        need = s["amount"]
        pool = [t for t in resolve_target(s.get("from", {}), board, subject) if t.tracks.get("population", 0) > 0]
        got = 0
        for t in pool:
            if got >= need:
                break
            take = min(t.tracks["population"], need - got)
            t.tracks["population"] -= take; got += take
            board.note("consume", "%s.population -%d" % (_short(t.id), take))
        branch = s.get("then") if got >= need else s.get("else")
        apply_effects(branch, board, subject)
    elif "convert_track" in eff:
        s = eff["convert_track"]
        if subject:
            amt = subject.tracks.get(s["from"], 0) if s.get("amount") == "all" else s.get("amount", 0)
            rate = s.get("rate", 1)                     # e.g. Wreckage Field: 1 Abundance -> 2 Materials
            subject.tracks[s["from"]] = _clamp(s["from"], subject.tracks.get(s["from"], 0) - amt)
            board.resources[s["to"]] = board.resources.get(s["to"], 0) + amt * rate
            board.note("convert", "%d %s -> %d %s" % (amt, s["from"], amt * rate, s["to"]))
    elif "produce_resource" in eff:
        s = eff["produce_resource"]
        board.resources[s["resource"]] = board.resources.get(s["resource"], 0) + s.get("amount", 1)
        board.note("produce", "+%d %s" % (s.get("amount", 1), s["resource"]))
    elif "refill_track" in eff:
        s = eff["refill_track"]
        per = available_icons(board).get(s["per_icon"], 0)
        board.tracks[s["track"]] = board.tracks.get(s["track"], 0) + per
        board.note("refill", "%s +%d (per %s)" % (s["track"], per, s["per_icon"]))
    elif "player_obligation" in eff:
        opts = eff["player_obligation"].get("each_player", [])
        for p in board.players:
            board.note("obligation", "%s: %s" % (p.name, _fulfil(p, opts, board)))
    elif "for_each" in eff:
        s = eff["for_each"]
        affected = 0
        for t in resolve_target(s["filter"], board, subject):
            if not eval_condition(s.get("where"), board, t):
                continue
            before = dict(t.tracks)
            apply_effects(s.get("do"), board, t)
            if t.tracks != before:
                affected += 1
        if affected == 0 and s.get("if_none"):
            apply_effects(s["if_none"], board, subject)
    elif "remove_self" in eff:
        if subject:
            subject.removed = True
            board.note("remove", "%s moves on" % _short(subject.id))
    elif "tuck" in eff:
        board.note("tuck", "under %s" % eff["tuck"].get("under"))
    # provides_icon / instruction / narrative: no direct state change here


def _fulfil(player, options, board):
    # policy: satisfy the obligation the cheapest way available
    for o in options:
        if "has_icon" in o and available_icons(board).get(o["has_icon"], 0) > 0:
            return "has %s icon" % o["has_icon"]
    for o in options:
        if "change_track" in o and o["change_track"].get("track") == "rations" and board.tracks.get("rations", 0) > 0:
            board.tracks["rations"] -= 1
            return "reduced rations"
    for o in options:
        if "change_track" in o:  # reduce a flora pop as last resort
            for t in resolve_target(o["change_track"].get("target", {}), board, None):
                if t.tracks.get("population", 0) > 0:
                    t.tracks["population"] -= 1
                    return "reduced %s pop" % _short(t.id)
    return "unmet"


def apply_effects(effs, board, subject):
    for e in _as_list(effs):
        apply_effect(e, board, subject)


# ----------------------------------------------------------------- upkeep
def pick_band(bands, pop):
    """Select the band whose 'pop' key (an int or an 'a-b' range) contains pop."""
    for b in bands:
        s = str(b["pop"])
        a, z = (map(int, s.split("-")) if "-" in s else (int(s), int(s)))
        a, z = int(a), int(z)
        if a <= pop <= z:
            return b
    return None


def _run_upkeep_group(group, board, subject):
    """Run one upkeep group: a {bands:…}, a {conditional:…}, or a plain verb.
    Returns True if it hit a status:unresolved step (a tracked gap)."""
    if not isinstance(group, dict):
        return False
    if "bands" in group:
        band = pick_band(group["bands"], subject.tracks.get("population", 0) if subject else 0)
        if band:
            apply_effects(band.get("do"), board, subject)
            return any(isinstance(x, dict) and x.get("status") == "unresolved" for x in _as_list(band.get("do")))
        return False
    if "conditional" in group:
        unresolved = False
        for c in group["conditional"]:
            if eval_condition(c.get("when"), board, subject):
                apply_effects(c.get("do"), board, subject)
                unresolved = unresolved or any(
                    isinstance(x, dict) and x.get("status") == "unresolved" for x in _as_list(c.get("do")))
        return unresolved
    apply_effect(group, board, subject)
    return group.get("status") == "unresolved"


def run_upkeep(up, board, subject):
    """Resolve a card's whole upkeep, whatever shape it takes:
      dict {bands:…} | dict {conditional:…} | list of any of {bands}/{conditional}/verb.
    Returns (before_tracks, unresolved_flag)."""
    before = dict(subject.tracks) if subject else {}
    if up is None:
        return before, False
    unresolved = False
    if isinstance(up, dict) and ("bands" in up or "conditional" in up):
        unresolved = _run_upkeep_group(up, board, subject)
    else:
        for group in _as_list(up):
            unresolved = _run_upkeep_group(group, board, subject) or unresolved
    return before, unresolved


# ----------------------------------------------------------------- crafting
def try_craft(cid, board, player):
    """Attempt to build a salvage recipe during the team phase.
      craft: { cost?: {resource: n}, requires?: {icon: n}, to: player_hand | tuck }
    Spends `cost` from the location's resource pool and checks `requires` icons are
    present. On success the recipe becomes active — to a player's hand (its icon then
    counts) or tucked under the outpost (its icons are added to the site). Returns a
    result string, or None if unaffordable/already built."""
    craft = board.effects.get(cid, {}).get("front", {}).get("craft")
    if not craft:
        return None
    if any(cid in p.hand for p in board.players) or cid in board.built:
        return None                                         # already built
    cost = craft.get("cost", {}); need = craft.get("requires", {})
    if any(board.resources.get(r, 0) < n for r, n in cost.items()):
        return None
    have = available_icons(board)
    if any(have.get(i, 0) < n for i, n in need.items()):
        return None
    for r, n in cost.items():
        board.resources[r] = board.resources.get(r, 0) - n
    front = board.effects.get(cid, {}).get("front", {})
    icons = ", ".join("%d %s" % (pi.get("amount", 1), pi["icon"]) for pi in _as_list(front.get("provides_icon")))
    if craft.get("to") == "tuck":
        for pi in _as_list(front.get("provides_icon")):
            board.tucked_icons[pi["icon"]] = board.tucked_icons.get(pi["icon"], 0) + pi.get("amount", 1)
        board.built.append(cid)
        board.note("craft", "%s installed (%s)" % (_short(cid), icons))
    else:
        (player or board.players[0]).hand.append(cid)
        board.note("craft", "%s built to hand (%s)" % (_short(cid), icons))
    spent = ", ".join("%d %s" % (n, r) for r, n in cost.items()) or "no resources"
    gated = (" [needed %s]" % ", ".join("%d %s" % (n, i) for i, n in need.items())) if need else ""
    return "spent %s -> %s%s" % (spent, icons, gated)


def load_effects(objects):
    eff = {}
    for typ, val in objects:
        if typ == "card_effects" and isinstance(val, dict) and val.get("id"):
            eff[val["id"]] = val
    return eff
