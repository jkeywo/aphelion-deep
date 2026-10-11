"""The Aphelion Deep — 3-player, 3-turn expedition simulation.

Content (verified in components.xlsx): three locations (Reef Gardens, Crash Flats,
Kelp Cathedral) and three role cards — two Ecology (Lead Ecologist, Systems
Ecologist) and one Engineering (Fabrication Lead). Each turn every player is
assigned to an expedition; the assignment logic weighs role affinity, the colony's
current need, and crowding. Expedition yields feed the colony's production and life
support, and each player's philosophy (restore vs exploit) drives the megafauna —
all through the real GameSpec mechanisms. Location yield profiles are derived from
the actual card text.
"""
from __future__ import annotations
import os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
for _rt in (os.path.join(HERE, "..", "..", "spec", "runtime"),
            os.path.join(HERE, "..", "spec", "runtime")):
    if os.path.isdir(os.path.join(_rt, "gamespec")):
        sys.path.insert(0, _rt)
        break

from gamespec.engine import Engine, load_state_schema
from gamespec.components import load_components
from gamespec import ChangeValue
from mechanisms import reactor, colony
from mechanisms.reactor import Endgame

GAME = os.path.join(HERE, "..", "game")
WORKBOOK = os.path.join(HERE, "..", "components", "components.xlsx")
LOCATIONS = ["Reef Gardens", "Crash Flats", "Kelp Cathedral"]

# The three authored roles, their department, philosophy stance, and where they
# want to expedition (affinity). Two ecologists, one engineer.
PLAYERS = [
    {"id": "fabrication_lead", "name": "Fabrication Lead", "dept": "Engineering",
     "stance": "exploit", "affinity": {"Crash Flats": 3, "Kelp Cathedral": 1, "Reef Gardens": 0}},
    {"id": "lead_ecologist", "name": "Lead Ecologist", "dept": "Ecology",
     "stance": "restore", "affinity": {"Reef Gardens": 3, "Kelp Cathedral": 2, "Crash Flats": 0}},
    {"id": "systems_ecologist", "name": "Systems Ecologist", "dept": "Ecology",
     "stance": "restore", "affinity": {"Reef Gardens": 3, "Kelp Cathedral": 2, "Crash Flats": 1}},
]


def derive_profiles(comps):
    """Per-location yield profile from the card Front Text (data-grounded)."""
    cards = comps.tables["Cards"]
    icons = {"materials": r"material", "oxygen": r"oxygen", "biomass": r"biomass|abundance|coral",
             "reactor": r"reactor|hydrotherm", "pressure": r"pressure"}
    counts = {loc: defaultdict(int) for loc in LOCATIONS}
    finds = {loc: [] for loc in LOCATIONS}
    for cid, row in cards.items():
        loc = str(row.get("Location") or "")
        if loc not in LOCATIONS:
            continue
        txt = str(row.get("Front Text") or "").lower()
        for k, pat in icons.items():
            counts[loc][k] += len(re.findall(pat, txt))
        if str(row.get("Card Type")) in ("Flora", "Fauna", "Mineral"):
            finds[loc].append(row.get("Name"))
    prof = {}
    for loc in LOCATIONS:
        c = counts[loc]
        prof[loc] = {
            "prod": round(c["materials"] / 2),                 # materials -> production
            "life": max(1, round((c["oxygen"] + c["biomass"]) / 4)),  # oxygen+biomass -> life support
            "risk": c["reactor"] + c["pressure"],              # reactor/pressure -> clock heat
            "raw": dict(c), "finds": finds[loc],
        }
    return prof


def assign(players, prof, colony_state, rng):
    """Who goes on which expedition this turn: affinity + colony need - crowding."""
    life = colony_state["life_support"]
    prod = colony_state["production"]
    taken = defaultdict(int)
    result = []
    for p in players:
        best, best_loc, why = None, None, ""
        for loc in LOCATIONS:
            score = p["affinity"][loc]
            reasons = ["affinity %d" % p["affinity"][loc]]
            if life < 6 and prof[loc]["life"] >= 2:
                score += 2; reasons.append("colony short of life-support")
            if prod < 4 and prof[loc]["prod"] >= 2:
                score += 2; reasons.append("colony short of production")
            score -= 2 * taken[loc]
            if taken[loc]:
                reasons.append("%d already there" % taken[loc])
            score += rng.uniform(0, 0.3)                       # tiny tiebreak
            if best is None or score > best:
                best, best_loc, why = score, loc, ", ".join(reasons)
        taken[best_loc] += 1
        result.append((p, best_loc, why))
    return result


def _apply(state, ref, field, delta):
    return state.apply([ChangeValue(ref, field, delta)])


def run_expedition(seed, turns=3):
    import random
    rng = random.Random(seed)
    eng = Engine(load_state_schema(os.path.join(GAME, "state.schema.yaml")))
    eng.register_module(reactor); eng.register_module(colony); eng.load_actions(GAME)
    comps = load_components(WORKBOOK)
    prof = derive_profiles(comps)

    state = eng.new_state({"colony": {"production": 2, "life_support": 9, "headcount": 3, "outposts": 1}})
    trace = []
    for t in range(1, turns + 1):
        snap = state.values
        assigns = assign(PLAYERS, prof, snap["colony"], rng)
        turn = {"turn": t, "expeditions": [], "exploit": 0, "restore": 0}
        crash_exploited = False
        for p, loc, why in assigns:
            pr = prof[loc]
            prod_gain = pr["prod"] + (1 if p["stance"] == "exploit" else 0)
            life_gain = pr["life"] + (1 if p["stance"] == "restore" else 0)
            state = _apply(state, "game.colony", "production", prod_gain)
            state = _apply(state, "game.colony", "life_support", life_gain)
            # philosophy -> megafauna, via the real mechanism
            state = eng.step(state, "megafauna_react", stance=p["stance"],
                             aggression=state.values["megafauna"]["aggression"]).state
            if p["stance"] == "exploit":
                turn["exploit"] += 1
                if loc == "Crash Flats":
                    crash_exploited = True
            else:
                turn["restore"] += 1
            find = rng.choice(pr["finds"]) if pr["finds"] else "the site"
            turn["expeditions"].append({
                "player": p["name"], "dept": p["dept"], "loc": loc, "stance": p["stance"],
                "why": why, "prod": prod_gain, "life": life_gain, "find": find})
        # colony upkeep consumes life support by headcount
        state = _apply(state, "game.colony", "life_support", -state.values["colony"]["headcount"])
        # the reactor clock advances; exploiting the wreckage by the engine core stokes it
        state = eng.do(state, "advance_the_reactor", context={"slow": 0}).state
        reactor_extra = 0
        if crash_exploited:
            state = eng.do(state, "advance_the_reactor", context={"slow": 0}).state
            reactor_extra = 1
        outcome = eng.step(state, "check_endgame").outcome
        turn["reactor_extra"] = reactor_extra
        turn["state"] = {"production": state.values["colony"]["production"],
                         "life_support": state.values["colony"]["life_support"],
                         "reactor_phase": state.values["reactor"]["phase"],
                         "megafauna": state.values["megafauna"]["aggression"],
                         "outcome": outcome.value}
        trace.append(turn)
    return {"seed": seed, "profiles": prof, "turns": trace, "final": trace[-1]["state"]}


if __name__ == "__main__":
    r = run_expedition(0)
    print("LOCATION PROFILES (derived):")
    for loc, p in r["profiles"].items():
        print("  %-16s prod=%d life=%d risk=%d  raw=%s" % (loc, p["prod"], p["life"], p["risk"], p["raw"]))
    for t in r["turns"]:
        print("\n== Turn %d ==" % t["turn"])
        for e in t["expeditions"]:
            print("   %-18s -> %-14s [%s]  +%dprod +%dlife  (%s)  finds %s"
                  % (e["player"], e["loc"], e["stance"], e["prod"], e["life"], e["why"], e["find"]))
        s = t["state"]
        print("   colony: prod %d, life %d | reactor phase %d (+%d) | megafauna %d | %s"
              % (s["production"], s["life_support"], s["reactor_phase"], t["reactor_extra"],
                 s["megafauna"], s["outcome"]))
