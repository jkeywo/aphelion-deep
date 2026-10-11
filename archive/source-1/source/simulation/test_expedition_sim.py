"""Regression guard for the Aphelion expedition sim (skips if openpyxl absent)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _have_openpyxl():
    try:
        import openpyxl  # noqa
        return True
    except Exception:
        return False


def test_expedition_runs_three_turns():
    if not _have_openpyxl():
        print("SKIP: openpyxl not installed"); return
    import expedition_sim as sim
    r = sim.run_expedition(0, turns=3)
    assert len(r["turns"]) == 3
    # all three players expedition every turn; the three sites are covered turn 1
    assert all(len(t["expeditions"]) == 3 for t in r["turns"])
    assert {e["loc"] for e in r["turns"][0]["expeditions"]} == set(sim.LOCATIONS)
    # deterministic reactor trajectory
    assert r["final"]["reactor_phase"] == 6 and r["final"]["outcome"] == "defeat_critical"


if __name__ == "__main__":
    test_expedition_runs_three_turns(); print("PASS")
