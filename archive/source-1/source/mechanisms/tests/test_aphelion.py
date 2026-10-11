import sys, os
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "spec", "runtime"))  # vendored gamespec runtime
sys.path.insert(0, os.path.join(HERE, "..", ".."))                           # the source/ package root

from mechanisms.reactor import (resolve_advance_reactor, resolve_slow_reactor,
                                resolve_stabilise_reactor, resolve_check_endgame,
                                ReactorOutcome, SlowOutcome, StabiliseOutcome, Endgame)
from mechanisms.colony import (resolve_produce_upkeep, resolve_build_outpost,
                               resolve_megafauna_react, UpkeepOutcome, BuildOutcome, MegafaunaOutcome)
from mechanisms.types import ReactorState, Colony


def _ch(r):
    return {(c.reference, c.field): c.delta for c in r.changes}


def test_reactor_advances_one_phase():
    r = resolve_advance_reactor(ReactorState("game.reactor", phase=1))
    assert r.outcome is ReactorOutcome.ADVANCED and _ch(r)[("game.reactor", "phase")] == 1

def test_outpost_slows_reactor_to_hold():
    r = resolve_advance_reactor(ReactorState("game.reactor", phase=3), slow=1)
    assert r.outcome is ReactorOutcome.HELD and _ch(r)[("game.reactor", "phase")] == 0

def test_reactor_goes_critical_at_max():
    r = resolve_advance_reactor(ReactorState("game.reactor", phase=5, max_phase=6))
    assert r.outcome is ReactorOutcome.CRITICAL

def test_slow_reactor_spends_production():
    r = resolve_slow_reactor(Colony("game.colony", production=3), production_spent=2)
    assert r.outcome is SlowOutcome.SLOWED and _ch(r)[("game.colony", "production")] == -2

def test_slow_reactor_illegal_without_production():
    r = resolve_slow_reactor(Colony("game.colony", production=1), production_spent=2)
    assert r.status.value == "illegal"

def test_stabilise_reaches_victory_threshold():
    r = resolve_stabilise_reactor(ReactorState("game.reactor", phase=2, containment=2), containment_added=1)
    assert r.outcome is StabiliseOutcome.STABILISED
    assert _ch(r)[("game.reactor", "stabilised")] is True

def test_stabilise_partial_progress():
    r = resolve_stabilise_reactor(ReactorState("game.reactor", phase=2, containment=0), containment_added=1)
    assert r.outcome is StabiliseOutcome.PROGRESS

def test_endgame_victory_when_stabilised():
    r = resolve_check_endgame(ReactorState("game.reactor", phase=4, stabilised=True), Colony("game.colony", life_support=5))
    assert r.outcome is Endgame.VICTORY

def test_endgame_defeat_when_critical():
    r = resolve_check_endgame(ReactorState("game.reactor", phase=6, max_phase=6), Colony("game.colony", life_support=5))
    assert r.outcome is Endgame.DEFEAT_CRITICAL

def test_endgame_defeat_on_collapse():
    r = resolve_check_endgame(ReactorState("game.reactor", phase=2), Colony("game.colony", life_support=0))
    assert r.outcome is Endgame.DEFEAT_COLLAPSE

def test_upkeep_produces_and_consumes():
    r = resolve_produce_upkeep(Colony("game.colony", outposts=3, headcount=2))
    ch = _ch(r)
    assert ch[("game.colony", "production")] == 3 and ch[("game.colony", "life_support")] == -2

def test_build_outpost_pays_and_gains():
    r = resolve_build_outpost(Colony("game.colony", production=2))
    ch = _ch(r)
    assert r.outcome is BuildOutcome.BUILT and ch[("game.colony", "production")] == -2 and ch[("game.colony", "outposts")] == 1

def test_build_outpost_illegal_without_production():
    assert resolve_build_outpost(Colony("game.colony", production=1)).status.value == "illegal"

def test_megafauna_escalate_on_exploit():
    r = resolve_megafauna_react("exploit", aggression=1)
    assert r.outcome is MegafaunaOutcome.ESCALATED and _ch(r)[("game.megafauna", "aggression")] == 1

def test_megafauna_ease_on_restore():
    r = resolve_megafauna_react("restore", aggression=3)
    assert r.outcome is MegafaunaOutcome.EASED and _ch(r)[("game.megafauna", "aggression")] == -1

def test_megafauna_clamped_at_zero():
    r = resolve_megafauna_react("restore", aggression=0)
    assert r.outcome is MegafaunaOutcome.STEADY and _ch(r)[("game.megafauna", "aggression")] == 0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn(); print("PASS", fn.__name__)
    print("\nALL %d APHELION DEEP TESTS PASSED" % len(fns))
