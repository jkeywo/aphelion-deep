"""Reef Gardens turn 1, driven entirely by the cards' capability blocks.

The interpreter (mechanisms/card_effects.py) reads each card's front/back effect
blocks (game/reef_cards.gamespec.md) and works out what happens. `descend=True`
opens the gate regardless of the requirement (a labelled hypothetical) so the
caverns cards 16–21 and their upkeep verbs get exercised too.
"""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
for _rt in (os.path.join(HERE, "..", "..", "spec", "runtime"),
            os.path.join(HERE, "..", "spec", "runtime")):
    if os.path.isdir(os.path.join(_rt, "gamespec")):
        sys.path.insert(0, _rt); break
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

from gamespec.engine import iter_design_objects
from mechanisms import card_effects as CE
import reef_expedition as R

EFFECTS_FILE = os.path.join(HERE, "..", "game", "reef_cards.gamespec.md")


def _keywords():
    import openpyxl
    wb = openpyxl.load_workbook(R.WB, data_only=True)
    ws = wb["Cards"]; rows = list(ws.iter_rows(values_only=True))
    hdr = [str(c).strip() if c else "" for c in rows[0]]
    I, K = hdr.index("ID"), hdr.index("Keywords")
    out = {}
    for r in rows[1:]:
        if r and r[I]:
            out[str(r[I])] = [w.strip().lower() for w in re.split(r"[,\n]", str(r[K] or "")) if w.strip()]
    return out


def _disposition(e):
    for blk in (e.get("back", {}), e.get("front", {})):
        if isinstance(blk, dict):
            if blk.get("disposition"):
                return blk["disposition"]
            for step in CE._as_list(blk.get("on_reveal")):
                if isinstance(step, dict) and step.get("disposition"):
                    return step["disposition"]
    return "resolve_now"


def _play(board, effects, card, kw, trace, cultivator=None):
    cid = card["id"]; front = effects.get(cid, {}).get("front", {})
    ip = CE.InPlay(cid, front=dict(front))
    ip.front["_card_type"] = card["type"].lower()
    ip.front["_keywords"] = kw.get(cid, [])
    board.in_play[cid] = ip
    CE.apply_effects(effects.get(cid, {}).get("back", {}).get("on_reveal"), board, ip)
    trace.append(("play", card["name"], "tracks %s" % ip.tracks))
    if cultivator and ip.front["_card_type"] == "flora" and not cultivator[0]:
        for p in board.players:
            act = next((x["action"] for x in p.passives if "action" in x), None)
            if act and act.get("id") == "cultivator":
                CE.apply_effect({"change_track": act["change_track"]}, board, ip)
                cultivator[0] = True
                trace.append(("action", "%s uses Cultivator" % p.name, "%s.population -> %d" % (card["name"], ip.tracks["population"])))
                break
    return ip


def run(dilemma_choice="protect", descend=False):
    effects = CE.load_effects(iter_design_objects(EFFECTS_FILE))
    kw = _keywords()
    deck = R.load_reef()
    board = CE.Board(effects=effects, players=[CE.Player("Player 1"), CE.Player("Player 2")])
    trace = []; cultivator = [False]; opened = False
    i = 0
    while i < len(deck):
        card = deck[i]; cid = card["id"]; e = effects.get(cid, {})
        disp = _disposition(e); back = e.get("back", {}); front = e.get("front", {})

        if disp == "set_aside" and "gate" in back and not opened:
            _resolve_conditional_gains(board, effects)
            avail = CE.available_icons(board); req = back["gate"]["requires"]
            met = all(avail.get(k, 0) >= v for k, v in req.items())
            trace.append(("GATE", card["name"], "need %s · have %s · %s"
                          % (req, avail, "OPEN" if met else "CLOSED — cannot descend")))
            if not (met or descend):
                break
            if descend and not met:
                trace.append(("descent", "(hypothetical)", "gate forced open to exercise the caverns encoding"))
            opened = True; i += 1; continue

        if any("each_player_chooses" in s for s in CE._as_list(back.get("on_reveal"))):
            trace.append(("reveal", card["name"], "reveal role cards; each player chooses one"))
            for pi, p in enumerate(board.players):
                role = deck[i + 1 + pi]; p.role_id = role["id"]
                for pas in CE._as_list(effects.get(role["id"], {}).get("back", {}).get("passive")):
                    p.passives.append(pas)
                trace.append(("role", "%s = %s" % (p.name, role["name"]), _passive_desc(effects.get(role["id"], {}))))
            i += 1 + len(board.players); continue

        if disp == "play_at_location":
            _play(board, effects, card, kw, trace, cultivator)
        elif disp == "to_player_hand":
            board.players[0].hand.append(cid); trace.append(("to_hand", card["name"], "to a player's hand"))
        elif disp == "set_beside_deck":
            trace.append(("aside", card["name"], "set beside the deck" + (" (conditional gain)" if back.get("conditional_gain") else "")))
        elif "dilemma" in front:
            opt = next((o for o in front["dilemma"]["options"] if o["id"] == dilemma_choice), front["dilemma"]["options"][0])
            trace.append(("dilemma", card["name"], "group chose '%s'" % opt["label"]))
            CE.apply_effects(opt["do"], board, None)
            for d in opt["do"]:
                if "provides_icon" in d:
                    pi = d["provides_icon"]; board.tucked_icons[pi["icon"]] = board.tucked_icons.get(pi["icon"], 0) + pi.get("amount", 1)
        else:
            trace.append(("resolve", card["name"], "read / resolved"))
        i += 1

    _resolve_conditional_gains(board, effects)
    upkeep = _run_upkeep(board, effects)
    return board, trace, upkeep


def _run_upkeep(board, effects):
    out = []
    for ip in list(board.in_play.values()):
        if ip.removed:
            continue
        up = effects.get(ip.id, {}).get("front", {}).get("upkeep")
        before = dict(ip.tracks)
        unresolved = False
        if isinstance(up, dict) and "bands" in up:
            band = _pick_band(up["bands"], ip.tracks.get("population", 0))
            if band:
                CE.apply_effects(band.get("do"), board, ip)
                unresolved = any(isinstance(x, dict) and x.get("status") == "unresolved" for x in CE._as_list(band.get("do")))
        elif isinstance(up, dict) and "conditional" in up:
            for c in up["conditional"]:
                if CE.eval_condition(c.get("when"), board, ip):
                    CE.apply_effects(c.get("do"), board, ip)
        elif isinstance(up, list):
            CE.apply_effects(up, board, ip)
            unresolved = any(isinstance(x, dict) and x.get("status") == "unresolved" for x in up)
        else:
            continue
        tag = "upkeep-unresolved" if unresolved else "upkeep"
        out.append((tag, CE._short(ip.id), "tracks %s -> %s" % (before, ip.tracks)))
    return out


def _resolve_conditional_gains(board, effects):
    for cid, e in effects.items():
        for cg in CE._as_list(e.get("back", {}).get("conditional_gain")):
            if CE.eval_condition(cg.get("when"), board, None) and cid not in board.players[0].hand:
                board.players[0].hand.append(cid)
                board.note("gain", "%s gained" % cid)


def _pick_band(bands, pop):
    for b in bands:
        s = str(b["pop"])
        a, z = (map(int, s.split("-")) if "-" in s else (int(s), int(s)))
        a, z = (a, z) if isinstance(a, int) else (list(map(int, s.split("-"))))
        if a <= pop <= z:
            return b
    return None


def _passive_desc(e):
    out = []
    for p in CE._as_list(e.get("back", {}).get("passive")):
        if "provides_icon" in p:
            out.append("passive %d %s icon" % (p["provides_icon"].get("amount", 1), p["provides_icon"]["icon"]))
        if "action" in p:
            out.append("passive action: %s" % p["action"].get("id"))
    return "; ".join(out) or "—"


if __name__ == "__main__":
    descend = "--descend" in sys.argv
    board, trace, upkeep = run("protect", descend=descend)
    print("== EXPLORATION (driven by card capability blocks) ==")
    for k, w, d in trace:
        print("   %-9s %-30s %s" % (k, str(w)[:30], d))
    print("\n== UPKEEP ==")
    for k, w, d in upkeep:
        print("   %-18s %-26s %s" % (k, str(w)[:26], d))
    print("\n   icons: %s | resources: %s | rations: %s"
          % (CE.available_icons(board), board.resources, board.tracks.get("rations")))
