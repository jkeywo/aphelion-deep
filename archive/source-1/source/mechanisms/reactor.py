"""The Aphelion Deep — reactor clock and the cooperative endgame."""
from __future__ import annotations
from enum import Enum

from gamespec import ChangeValue, MechanismResult, mechanism
from .types import ReactorState, Colony


class ReactorOutcome(Enum):
    ADVANCED = "advanced"
    HELD = "held"
    CRITICAL = "critical"


@mechanism(id="advance_reactor", pattern="doom_clock", calls=[],
           inputs={"reactor": "ReactorState", "slow": "int"},
           reads=["reactor"], writes=["reactor"])
def resolve_advance_reactor(reactor: ReactorState, slow: int = 0):
    """Each upkeep the reactor advances one phase; outposts may spend production to slow it
    (each `slow` cancels one phase of advance). Reaching max phase unresolved is critical."""
    advance = max(0, 1 - max(0, slow))
    new_phase = min(reactor.max_phase, reactor.phase + advance)
    if new_phase >= reactor.max_phase and not reactor.stabilised:
        outcome = ReactorOutcome.CRITICAL
    else:
        outcome = ReactorOutcome.HELD if advance == 0 else ReactorOutcome.ADVANCED
    return MechanismResult.legal(
        outcome,
        changes=(ChangeValue(reactor.reference, "phase", advance),),
        trace_steps=(("advance", "Reactor advances (after outpost slowing).",
                      {"slow": slow, "advance": advance, "phase": new_phase}),),
    )


class SlowOutcome(Enum):
    SLOWED = "slowed"


@mechanism(id="slow_reactor", pattern="recovery", calls=[],
           inputs={"colony": "Colony", "production_spent": "int"},
           reads=["colony"], writes=["colony"])
def resolve_slow_reactor(colony: Colony, production_spent: int):
    """Spend outpost production to slow the reactor. Returns the spend and the slow amount
    to feed advance_reactor. Illegal if the colony lacks the production."""
    if colony.production < production_spent:
        return MechanismResult.illegal("Not enough production to slow the reactor.")
    return MechanismResult.legal(
        SlowOutcome.SLOWED,
        changes=(ChangeValue(colony.reference, "production", -production_spent),),
        trace_steps=(("slow", "Production spent to slow the reactor.", {"slow": production_spent}),),
    )


class StabiliseOutcome(Enum):
    STABILISED = "stabilised"
    PROGRESS = "progress"


@mechanism(id="stabilise_reactor", pattern="threshold_test", calls=[],
           inputs={"reactor": "ReactorState", "containment_added": "int"},
           reads=["reactor"], writes=["reactor"])
def resolve_stabilise_reactor(reactor: ReactorState, containment_added: int):
    """Engineering + Drowned tech add containment; enough containment stabilises the reactor
    (the shared victory condition)."""
    total = reactor.containment + containment_added
    changes = [ChangeValue(reactor.reference, "containment", containment_added)]
    if total >= reactor.containment_needed:
        changes.append(ChangeValue(reactor.reference, "stabilised", True))
        return MechanismResult.legal(StabiliseOutcome.STABILISED, changes=tuple(changes))
    return MechanismResult.legal(StabiliseOutcome.PROGRESS, changes=tuple(changes))


class Endgame(Enum):
    VICTORY = "victory"
    DEFEAT_CRITICAL = "defeat_critical"
    DEFEAT_COLLAPSE = "defeat_collapse"
    ONGOING = "ongoing"


@mechanism(id="check_endgame", pattern="banded_outcome", calls=[],
           inputs={"reactor": "ReactorState", "colony": "Colony"},
           reads=["reactor", "colony"], writes=[])
def resolve_check_endgame(reactor: ReactorState, colony: Colony):
    """The cooperative outcome: win by stabilising the reactor; lose to a critical reactor
    or to life-support collapse."""
    if reactor.stabilised:
        outcome = Endgame.VICTORY
    elif reactor.phase >= reactor.max_phase:
        outcome = Endgame.DEFEAT_CRITICAL
    elif colony.life_support <= 0:
        outcome = Endgame.DEFEAT_COLLAPSE
    else:
        outcome = Endgame.ONGOING
    return MechanismResult.legal(outcome, changes=())
