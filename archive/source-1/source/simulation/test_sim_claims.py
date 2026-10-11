"""M4 — Monte-Carlo balance harness for The Aphelion Deep.

Runs many games under a *naive* policy through the real engine, aggregates the
outcomes, and checks the authored `design_claim`s (from design/claims.gamespec.md)
against the result. A balance regression fails the run — the 98.6%-win-rate class
of finding becomes a regressible assertion.

    python3 test_sim_claims.py       # prints the distribution + claim verdicts
    pytest test_sim_claims.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
for _rt in (os.path.join(HERE, "..", "..", "spec", "runtime"),
            os.path.join(HERE, "..", "spec", "runtime")):
    if os.path.isdir(os.path.join(_rt, "gamespec")):
        sys.path.insert(0, _rt)
        break

from gamespec.engine import Engine, load_state_schema, iter_design_objects
from gamespec import sim
from mechanisms import reactor, colony
from mechanisms.reactor import Endgame

GAME = os.path.join(HERE, "..", "game")
DESIGN = os.path.join(HERE, "..", "design", "claims.gamespec.md")
# Not stabilising the reactor before the campaign ends is a loss (the reactor wins
# by exhaustion), so an unresolved game at the round limit is a defeat.
_OUTCOME = {Endgame.VICTORY: "victory", Endgame.DEFEAT_CRITICAL: "defeat_critical",
            Endgame.DEFEAT_COLLAPSE: "defeat_collapse", Endgame.ONGOING: "defeat_timeout"}
MAX_ROUNDS = 6


def _engine():
    eng = Engine(load_state_schema(os.path.join(GAME, "state.schema.yaml")))
    eng.register_module(reactor); eng.register_module(colony)
    eng.load_actions(GAME)
    return eng


def _naive_run(rng):
    """One game: upkeep, a random colony action, the reactor advances, check outcome."""
    eng = _naive_run.engine
    st = eng.new_state({"colony": {"production": 3, "life_support": 10, "headcount": 1, "outposts": 1}})
    for _ in range(MAX_ROUNDS):
        st = eng.do(st, "run_upkeep").state
        prod = st.values["colony"]["production"]
        choices = ["stabilise", "slow", "pass"] + (["build"] if prod >= 2 else [])
        pick = rng.choice(choices)
        if pick == "build":
            st = eng.do(st, "build_an_outpost").state
        elif pick == "stabilise":
            st = eng.do(st, "attempt_stabilise_reactor", context={"containment_added": rng.randint(0, 3)}).state
        elif pick == "slow":
            st = eng.do(st, "slow_the_reactor", context={"production_spent": min(1, prod)}).state
        st = eng.do(st, "advance_the_reactor", context={"slow": 1 if pick == "slow" else 0}).state
        out = eng.step(st, "check_endgame").outcome
        if out is not Endgame.ONGOING:
            return _OUTCOME[out]
    return _OUTCOME[eng.step(st, "check_endgame").outcome]


def _load_claims():
    claims = []
    for typ, val in iter_design_objects(DESIGN):
        if typ == "design_claim" and isinstance(val, dict):
            claims.append(val)
    return claims


def run(verbose=False):
    _naive_run.engine = _engine()
    claims = _load_claims()
    runs = max((c.get("runs", 500) for c in claims), default=500)
    stats = sim.monte_carlo(_naive_run, runs=runs, seed=1234)
    results = [sim.evaluate_claim(stats, c) for c in claims]
    if verbose:
        print("naive policy —", stats.summary())
        for r in results:
            print("   claim %-24s %s  (%s %s, actual %.3f)"
                  % (r.id, "OK " if r.ok else "VIOLATED", r.metric, r.bound, r.value))
    return stats, results


def test_design_claims_hold():
    _stats, results = run()
    bad = [r for r in results if not r.ok]
    assert not bad, ["%s: %s %s but %.3f" % (r.id, r.metric, r.bound, r.value) for r in bad]


def test_harness_detects_violation():
    # a deliberately false claim must be reported as violated
    _naive_run.engine = _engine()
    stats = sim.monte_carlo(_naive_run, runs=200, seed=7)
    bogus = sim.evaluate_claim(stats, {"id": "bogus", "metric": "win_rate", "bound": "> 0.99"})
    assert not bogus.ok


if __name__ == "__main__":
    _stats, results = run(verbose=True)
    sys.exit(0 if all(r.ok for r in results) else 1)
