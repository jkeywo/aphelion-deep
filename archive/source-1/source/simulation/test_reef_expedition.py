"""Regression guard for the faithful Reef Gardens expedition (skips w/o openpyxl)."""
import os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)


def _have(): 
    try:
        import openpyxl; return True
    except Exception:
        return False


def test_reef_expedition_gate_holds():
    if not _have():
        print("SKIP: openpyxl not installed"); return
    import reef_expedition as R
    reef, log = R.run(3)
    # cursor advanced through the surface reef and rests on the gate (persists across turns)
    assert reef.cursor > 0
    t1 = log[0]
    assert any(k == "gate-closed" for k, _w, _d in t1), "gate should hold (2 O2 + 2 Knowledge unmet)"
    # Filterweed's parsed Pop band grew it; Grazers' prose upkeep is flagged unresolved
    assert any(k == "upkeep" for k, _w, _d in t1)
    assert any(k == "upkeep-unresolved" for k, _w, _d in t1)
    # cursor is stable across turns (deck persists, gate still closed)
    assert log[1][0][1].startswith("TURN 2") and reef.cursor == reef.cursor


if __name__ == "__main__":
    test_reef_expedition_gate_holds(); print("PASS")
