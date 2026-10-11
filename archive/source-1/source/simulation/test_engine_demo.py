"""End-to-end demonstration of the M3 engine on The Aphelion Deep, driven by the
DESIGN BINDINGS (M1+): each step names an ACTION; the engine resolves the
mechanism's inputs from the action's `resolution.inputs` binding (state objects
from live state, scalars from context, config from constants). Mechanisms stay
pure; the engine applies proposed changes and enforces schema bounds.

    python3 test_engine_demo.py        # trace + exit code
    pytest test_engine_demo.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))                       # the source/ package root
for _rt in (os.path.join(HERE, "..", "..", "spec", "runtime"),     # source/simulation -> aphelion_deep/spec/runtime
            os.path.join(HERE, "..", "spec", "runtime")):          # flattened layout
    if os.path.isdir(os.path.join(_rt, "gamespec")):
        sys.path.insert(0, _rt)
        break

from gamespec.engine import Engine, load_state_schema, run_scenario
from mechanisms import reactor, colony
from mechanisms.reactor import Endgame

GAME = os.path.join(HERE, "..", "game")
SCHEMA = os.path.join(GAME, "state.schema.yaml")


def _engine():
    eng = Engine(load_state_schema(SCHEMA))
    eng.register_module(reactor)
    eng.register_module(colony)
    eng.load_actions(GAME)                 # <-- loads the action bindings from the design
    return eng


# A full cooperative victory expressed as ACTIONS; the engine resolves each
# mechanism's inputs from the design binding. Only per-invocation values (the
# adjudicated containment) are supplied as context.
VICTORY = {
    "initial": {"colony": {"production": 4, "life_support": 10, "headcount": 3, "outposts": 2}},
    "steps": [
        {"do": "run_upkeep"},                                        # colony<-state, per_outpost<-const 1
        {"do": "build_an_outpost"},                                  # colony<-state, cost<-const 2
        {"do": "advance_the_reactor"},                               # reactor<-state, slow<-context(default 0)
        {"do": "attempt_stabilise_reactor", "context": {"containment_added": 3}},
        {"do": "check_endgame"},                                     # mechanism id -> auto state inputs
    ],
    "assert_state": {"reactor": {"stabilised": True, "containment": 3}},
}

ILLEGAL_BUILD = {
    "initial": {"colony": {"production": 0, "outposts": 0}},
    "steps": [{"do": "build_an_outpost", "expect": "rejected"}],
    "assert_state": {"colony": {"production": 0, "outposts": 0}},
}

CLAMP = {
    "initial": {"colony": {"production": 0, "life_support": 2, "headcount": 9, "outposts": 0}},
    "steps": [{"do": "run_upkeep"}],
    "assert_state": {"colony": {"life_support": 0}},
}


def test_cooperative_victory_via_bindings():
    rep = run_scenario(_engine(), VICTORY)
    assert rep.ok, rep.failures
    assert rep.steps[-1][2] is Endgame.VICTORY, rep.steps


def test_binding_supplies_config():
    # run_upkeep binds per_outpost=constant 1, colony from state; outposts=2 -> +2 production
    eng = _engine()
    st = eng.new_state({"colony": {"production": 0, "outposts": 2, "headcount": 0, "life_support": 10}})
    res = eng.do(st, "run_upkeep")
    assert res.state.values["colony"]["production"] == 2


def test_illegal_action_rejected():
    assert run_scenario(_engine(), ILLEGAL_BUILD).ok


def test_bounds_clamp():
    eng = _engine()
    res = eng.do(eng.new_state(CLAMP["initial"]), "run_upkeep")
    assert res.state.values["colony"]["life_support"] == 0
    assert res.state.clamps


def _run(name, scn):
    rep = run_scenario(_engine(), scn)
    print("== %s ==" % name)
    for mid, status, info in rep.steps:
        print("   %-24s %-9s %s" % (mid, status, info))
    print("   final: reactor=%s colony=%s" % (rep.final.get("reactor"), rep.final.get("colony")))
    print("   VERDICT:", "PASS" if rep.ok else ("FAIL " + str(rep.failures)))
    return rep.ok


if __name__ == "__main__":
    ok = True
    for name, scn in (("cooperative victory (via bindings)", VICTORY),
                      ("illegal build rejected", ILLEGAL_BUILD),
                      ("bounds clamp", CLAMP)):
        ok = _run(name, scn) and ok
    sys.exit(0 if ok else 1)
