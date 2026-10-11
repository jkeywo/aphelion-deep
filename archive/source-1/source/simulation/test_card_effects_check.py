"""The L6 card-effects validator: the real blocks pass, and malformed blocks are
caught. Guards the closed effect vocabulary — a new verb must be taught to the
interpreter AND the validator, or it fails here.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))


def _find_gsx_tools():
    """Locate the tools dir holding the `gsx` package across checkout layouts:
    the flat scratch tree (repo/tools/gsx) and the device tree
    (AIWriting/DSL/tools/gsx, a sibling of GameProjects/…/source/simulation)."""
    d = HERE
    for _ in range(8):
        for cand in (os.path.join(d, "tools"), os.path.join(d, "DSL", "tools")):
            if os.path.isdir(os.path.join(cand, "gsx")):
                return cand
        d = os.path.dirname(d)
    return None


_tools = _find_gsx_tools()
if _tools and _tools not in sys.path:
    sys.path.insert(0, _tools)

from gsx.card_effects_check import check_card_effects
from gsx.findings import Report, Severity


class _Obj:
    def __init__(self, type, id, value, location="test:0"):
        self.type, self.id, self.value, self.location = type, id, value, location


def _errs(rep):
    return [f for f in rep.findings if f.severity is Severity.ERROR]


def _codes(rep):
    return {f.rule for f in rep.findings}


ICONS = _Obj("icon_set", None, {"icons": ["oxygen", "knowledge", "energy", "food", "reactor"]})


def test_real_blocks_pass():
    """The authored Reef Gardens blocks validate cleanly (only INFO gaps)."""
    from gsx.yamlblocks import read_objects
    game = os.path.join(HERE, "..", "game")
    l1 = Report("parse")
    objects = []
    for f in ("reef_cards.gamespec.md", "exploration.gamespec.md"):
        p = os.path.join(game, f)
        if os.path.exists(p):
            objects.extend(read_objects(p, l1))
    rep = Report("L6")
    ran = check_card_effects(objects, rep)
    assert ran, "no card_effects blocks found — did the file move?"
    assert not _errs(rep), "real blocks should have no L6 errors: %s" % [f.render() for f in _errs(rep)]


def test_unknown_verb_is_caught():
    bad = _Obj("card_effects", "c1", {"id": "c1", "front": {"teleport": {"to": "moon"}}})
    rep = Report("L6")
    check_card_effects([ICONS, bad], rep)
    assert "cardfx.unknown-key" in _codes(rep)


def test_unknown_icon_is_caught():
    bad = _Obj("card_effects", "c1",
               {"id": "c1", "front": {"provides_icon": [{"icon": "plutonium", "amount": 1}]}})
    rep = Report("L6")
    check_card_effects([ICONS, bad], rep)
    assert "cardfx.unknown-icon" in _codes(rep)


def test_unknown_track_is_caught():
    bad = _Obj("card_effects", "c1",
               {"id": "c1", "front": {"set_track": {"track": "morale", "value": 2}}})
    rep = Report("L6")
    check_card_effects([ICONS, bad], rep)
    assert "cardfx.unknown-track" in _codes(rep)


def test_dangling_card_reference_is_caught():
    bad = _Obj("card_effects", "c1", {"id": "c1", "front": {
        "change_track": {"track": "population", "target": "card.does_not_exist", "delta": 1}}})
    rep = Report("L6")
    check_card_effects([ICONS, bad], rep)
    assert "cardfx.card-ref-unresolved" in _codes(rep)


def test_gate_requires_icon_validated():
    bad = _Obj("card_effects", "c1", {"id": "c1", "back": {
        "gate": {"requires": {"unobtainium": 2}, "on_meet": {"open_expedition": True}}}})
    rep = Report("L6")
    check_card_effects([ICONS, bad], rep)
    assert "cardfx.unknown-icon" in _codes(rep)


def test_unresolved_is_info_not_error():
    gap = _Obj("card_effects", "c1", {"id": "c1", "front": {
        "upkeep": [{"status": "unresolved", "text": "prose not yet encoded"}]}})
    rep = Report("L6")
    check_card_effects([ICONS, gap], rep)
    assert not _errs(rep)
    assert "cardfx.unresolved" in _codes(rep)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn(); print("PASS", fn.__name__)
    print("all %d passed" % len(fns))
