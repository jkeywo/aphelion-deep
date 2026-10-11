"""The 3-player, 2-turn game is derived from the card capability blocks, not scripted.

Asserts the faithful outcomes (roles assigned by the reveal cards, gates gated by the
real icon tallies, decks persisting turn 1 -> turn 2) and that --assist exercises the
gated deep.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))


def _have():
    try:
        import openpyxl; return True
    except Exception:
        return False


def _loc(turn, name):
    return next(L for L in turn["locations"] if L["name"] == name)


def test_faithful_game():
    if not _have():
        print("SKIP: openpyxl not installed"); return
    import game_3p2t as G
    res = G.run(assist=False)
    t1, t2, t3 = res["turns"]

    # roles assigned by the department-reveal cards, with their passives
    roles = {p.name: p.role_id for p in res["players"]}
    assert roles["Player 1"] == "crash_flats_3_fabrication_lead", roles
    assert roles["Player 2"] == "reef_gardens_3_lead_ecologist", roles
    assert roles["Player 3"] == "reef_gardens_4_systems_ecologist", roles

    # turn 1: both starter expeditions reach their gate and it holds
    crash1, reef1 = _loc(t1, "Crash Flats"), _loc(t1, "Reef Gardens")
    assert crash1["status"] == "gate-closed"          # Engine Core needs Oxygen the wreck lacks
    assert reef1["status"] == "gate-closed"           # Reef Caverns 1 Knowledge short
    assert reef1["icons"].get("oxygen") == 2 and reef1["icons"].get("knowledge") == 1

    # Wreckage Field converts Abundance to 2x Materials (rate); the Oxygen Tank craft
    # then spends 1 -> the Engineer carries an Oxygen icon out of Crash Flats
    assert crash1["resources"].get("materials", 0) >= 9, crash1["resources"]
    p1 = next(p for p in res["players"] if p.name == "Player 1")
    assert "crash_flats_s1_oxygen_tank" in p1.hand, p1.hand

    # the catalogue separates site icons from portable icons
    cat = res["catalogue"]
    assert cat["sites"]["Crash Flats"].get("power") == 2         # tucked (dilemma) stays at the site
    p1c = next(c for c in cat["players"] if c["name"] == "Player 1")
    assert p1c["icons"].get("oxygen") == 1 and p1c["icons"].get("power") == 1   # tank + role, portable

    # decks persist: turn 2 resumes Reef exactly where turn 1 stopped
    reef2 = _loc(t2, "Reef Gardens")
    assert reef2["cursor"] == reef1["cursor"], (reef1["cursor"], reef2["cursor"])

    # turn 2: the crafted Oxygen Tank makes Kelp's 2-Oxygen entry — it OPENS
    kelp2 = _loc(t2, "Kelp Cathedral")
    assert kelp2["status"] == "exhausted", kelp2["status"]
    assert kelp2["cursor"] == kelp2["of"]

    # turn 3: the team converges on Reef and the pooled icons crack the Reef Caverns
    reef3 = _loc(t3, "Reef Gardens")
    assert reef3["icons"].get("oxygen", 0) >= 2 and reef3["icons"].get("knowledge", 0) >= 2, reef3["icons"]
    assert reef3["status"] == "exhausted", reef3["status"]      # gate opened, all 18 turned
    assert reef3["cursor"] == reef3["of"]


def test_assist_exercises_the_deep():
    if not _have():
        print("SKIP: openpyxl not installed"); return
    import game_3p2t as G
    res = G.run(assist=True)
    t1 = res["turns"][0]
    # forced open, Reef turns all 18 numbered cards in turn 1 and produces a caverns resource
    reef1 = _loc(t1, "Reef Gardens")
    assert reef1["cursor"] == reef1["of"], (reef1["cursor"], reef1["of"])
    assert reef1["resources"], reef1["resources"]


if __name__ == "__main__":
    for fn in (test_faithful_game, test_assist_exercises_the_deep):
        fn(); print("PASS", fn.__name__)
    print("all passed")
