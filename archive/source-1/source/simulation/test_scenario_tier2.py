"""Tier-2 scenario: the authored crash_landing sequence, executed through the engine.

The scenario carries both tiers in one file:
  * Tier 1 (facts) — gsx L5 proves the step sequence is legal and reachable.
  * Tier 2 (numbers) — this test runs the SAME steps through the engine over the
    state schema and asserts the numeric end-state (`tier2.assert_state`).

So a single authored scenario is both a reachability check and an integration test
of the actual rules.

    python3 test_scenario_tier2.py
    pytest test_scenario_tier2.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
for _rt in (os.path.join(HERE, "..", "..", "spec", "runtime"),
            os.path.join(HERE, "..", "spec", "runtime")):
    if os.path.isdir(os.path.join(_rt, "gamespec")):
        sys.path.insert(0, _rt)
        break

from gamespec.engine import Engine, load_state_schema, run_scenario, iter_design_objects
from mechanisms import reactor, colony

GAME = os.path.join(HERE, "..", "game")
SCENARIO = os.path.join(HERE, "..", "scenarios", "crash_landing.gamespec.md")


def _engine():
    eng = Engine(load_state_schema(os.path.join(GAME, "state.schema.yaml")))
    eng.register_module(reactor); eng.register_module(colony)
    eng.load_actions(GAME)
    return eng


def _load_scenario():
    for typ, val in iter_design_objects(SCENARIO):
        if typ == "scenario" and isinstance(val, dict) and val.get("tier2"):
            return val
    raise AssertionError("no tier2 scenario found")


def _to_engine_scenario(scn):
    """Turn the fact-machine steps + the tier2 block into a run_scenario dict."""
    t2 = scn["tier2"]
    ctx = t2.get("context") or {}
    steps = []
    for s in scn.get("steps", []):
        aid = str(s["ref"]).split(".")[-1]
        steps.append({"do": aid, "context": ctx.get(aid, {}),
                      "expect": t2.get("expect_all", "applied")})
    return {"initial": t2.get("initial"), "steps": steps, "assert_state": t2.get("assert_state")}


def test_tier2_playthrough():
    scn = _to_engine_scenario(_load_scenario())
    rep = run_scenario(_engine(), scn)
    assert rep.ok, rep.failures


if __name__ == "__main__":
    scn = _to_engine_scenario(_load_scenario())
    rep = run_scenario(_engine(), scn)
    print("== crash_landing (Tier-2 numeric playthrough) ==")
    for mid, status, info in rep.steps:
        print("   %-24s %-9s %s" % (mid, status, info))
    print("   final reactor:", rep.final.get("reactor"))
    print("   final colony: ", rep.final.get("colony"))
    print("   VERDICT:", "PASS" if rep.ok else "FAIL " + str(rep.failures))
    sys.exit(0 if rep.ok else 1)
