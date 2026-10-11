"""The Aphelion Deep — a 3-player, 2-turn game across all three Tier-1 locations,
driven entirely by the cards' capability blocks (no invented site yields).

Three survivors: one Engineer (→ Fabrication Lead) and two Ecologists (→ Lead
Ecologist, Systems Ecologist). Roles and their passives are assigned by the
department-reveal cards as the decks are turned. Each turn the team states a
coordinated plan (who goes where); every CONSEQUENCE — what turns up, whether a
gate opens, how the ecosystem shifts in upkeep — is computed by the interpreter
from the card data. Location decks persist between turns.

  Turn 1  Engineer → Crash Flats,  both Ecologists → Reef Gardens  (canonical split)
  Turn 2  the team regroups: Crash's expedition is spent, so they pool Oxygen to
          try the unexplored Kelp Cathedral, one Ecologist holding Reef.

`--assist` re-runs with every gate forced open (a labelled hypothetical), so the
gated cards (Reef caverns, Kelp's inner reef, Engine Core) are exercised too.

    python3 game_3p2t.py            # the faithful game
    python3 game_3p2t.py --assist   # + the hypothetical deep-dive
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import explore as X                       # sets up the runtime path
from mechanisms import card_effects as CE


def _player(name, dept):
    p = CE.Player(name); p.dept = dept; return p


def new_game():
    eff = X.load_all_effects()
    locs = {n: X.Location(n, eff) for n in X.EFFECT_FILES}
    players = [_player("Player 1", "Engineering"),
               _player("Player 2", "Ecology"),
               _player("Player 3", "Ecology")]
    return locs, players


ROLE_NAME = {"crash_flats_3_fabrication_lead": "Fabrication Lead",
             "reef_gardens_3_lead_ecologist": "Lead Ecologist",
             "reef_gardens_4_systems_ecologist": "Systems Ecologist"}


# Per-turn coordinated plan: {location: [player indices]} + a one-line rationale.
def plan(turn, players, locs):
    if turn == 1:
        return {"Crash Flats": [0], "Reef Gardens": [1, 2]}, (
            "Canonical split — Engineering surveys its own wreck (Crash Flats) while "
            "both Ecologists work the Reef Gardens.")
    if turn == 2:
        # exploit the salvage crafted in turn 1's team phase: the Oxygen Tank opens Kelp.
        why = ("The Engineer crafted an Oxygen Tank at Crash Flats (spending the Wreckage Field's Materials). "
               "Carrying it to Kelp Cathedral alongside Lead Ecologist's own Oxygen makes the 2 Oxygen its "
               "entry gate needs — so the team opens Kelp. Systems Ecologist holds the Reef gate attempt.")
        return {"Kelp Cathedral": [0, 1], "Reef Gardens": [2]}, why
    # turn 3: the whole team converges on Reef Gardens to crack the Reef Caverns. The
    # Engineer brings the Oxygen Tank + Scan Database (Oxygen + Knowledge); Lead Ecologist
    # brings her Oxygen + the Reef Ecologist's Notes (Knowledge). Pooled with the reef's
    # own Filterweed Oxygen, that finally meets 2 Oxygen + 2 Knowledge.
    why = ("Kelp is surveyed and Crash's deep needs Power the team can't spare, so all three converge on "
           "the Reef Caverns. The Engineer's crafted Oxygen Tank + Scan Database and Lead Ecologist's "
           "Notes pool with the reef's Filterweed Oxygen to meet the caverns' 2 Oxygen + 2 Knowledge.")
    return {"Reef Gardens": [0, 1, 2]}, why


def catalogue(locs, players, where):
    """Snapshot the icon economy: site icons per location + portable icons per player."""
    sites = {name: loc.site_icons() for name, loc in locs.items()}
    eff = next(iter(locs.values())).effects
    people = []
    for i, p in enumerate(players):
        people.append({"name": p.name, "role": ROLE_NAME.get(p.role_id, "—"),
                       "at": where.get(i, "—"), "icons": X.player_icons(p, eff),
                       "hand": [CE._short(c) for c in p.hand]})
    return {"sites": sites, "players": people}


def run(assist=False, turns_n=3):
    locs, players = new_game()
    turns = []
    cats = {}
    for t in range(1, turns_n + 1):
        assign, why = plan(t, players, locs)
        where = {}
        turn = {"turn": t, "why": why, "locations": []}
        for loc_name, idxs in assign.items():
            loc = locs[loc_name]
            here = [players[i] for i in idxs]
            for i in idxs:
                where[i] = loc_name
            trace = [("--", "%s — %s" % (loc_name, ", ".join(p.name for p in here)),
                      "cursor at %d" % loc.cursor)]
            loc.resolve_gains(trace)                     # gains that already hold (e.g. from last turn)
            loc.explore(here, trace, assist=assist)
            loc.resolve_gains(trace)
            trace.append(("--", "Team phase — upkeep + crafting", ""))
            loc.upkeep(trace)
            loc.craft_phase(trace)                       # build affordable salvage
            loc.resolve_gains(trace)
            turn["locations"].append({
                "name": loc_name, "team": [p.name for p in here], "status": loc.status,
                "cursor": loc.cursor, "of": len(loc.deck), "icons": loc.icons(),
                "resources": dict(loc.board.resources), "trace": trace})
        cats[t] = catalogue(locs, players, where)
        turns.append(turn)
    return {"assist": assist, "turns": turns, "players": players, "locs": locs,
            "catalogue": cats.get(1), "catalogues": cats}


def _fmt(icons):
    return ", ".join("%s %d" % (k, v) for k, v in sorted(icons.items())) or "—"


def _print(res):
    for ti, turn in enumerate(res["turns"]):
        print("\n" + "=" * 74)
        print("TURN %d" % turn["turn"])
        print("  plan: %s" % turn["why"])
        for L in turn["locations"]:
            print("\n  %s  [%s]  — %s  (cursor %d/%d)"
                  % (L["name"], ", ".join(L["team"]), L["status"], L["cursor"], L["of"]))
            for k, w, d in L["trace"]:
                if k == "--":
                    print("     -- %s %s" % (w, d))
                else:
                    print("     %-10s %-32s %s" % (k, str(w)[:32], d))
            print("     => icons %s | resources %s" % (L["icons"], L["resources"]))
        c = res.get("catalogues", {}).get(turn["turn"])
        if c and (ti == 0 or ti == len(res["turns"]) - 1):
            print("\n  " + "-" * 60)
            print("  ICON CATALOGUE after Turn %d" % turn["turn"])
            print("  per location (site icons — stay with the place):")
            for name, ic in c["sites"].items():
                print("     %-16s %s" % (name, _fmt(ic)))
            print("  per player (portable icons — carried anywhere):")
            for p in c["players"]:
                print("     %-10s %-18s @ %-14s %s   hand: %s"
                      % (p["name"], p["role"], p["at"], _fmt(p["icons"]), ", ".join(p["hand"]) or "—"))


if __name__ == "__main__":
    assist = "--assist" in sys.argv
    _print(run(assist=assist))
