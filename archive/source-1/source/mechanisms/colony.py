"""The Aphelion Deep — closed economy, outposts, and reactive megafauna."""
from __future__ import annotations
from enum import Enum

from gamespec import ChangeValue, MechanismResult, mechanism
from .types import Colony


class UpkeepOutcome(Enum):
    PRODUCED = "produced"


@mechanism(id="produce_upkeep", pattern="resource_generation", calls=[],
           inputs={"colony": "Colony", "per_outpost": "int"},
           reads=["colony"], writes=["colony"])
def resolve_produce_upkeep(colony: Colony, per_outpost: int = 1):
    """Upkeep: each outpost yields production; life support is consumed by headcount."""
    production_gain = colony.outposts * per_outpost
    life_support_delta = -max(0, colony.headcount)
    return MechanismResult.legal(
        UpkeepOutcome.PRODUCED,
        changes=(
            ChangeValue(colony.reference, "production", production_gain),
            ChangeValue(colony.reference, "life_support", life_support_delta),
        ),
        trace_steps=(("upkeep", "Outposts produce; headcount consumes life support.",
                      {"production": production_gain, "life_support": life_support_delta}),),
    )


class BuildOutcome(Enum):
    BUILT = "built"


@mechanism(id="build_outpost", pattern="pay_and_gain", calls=[],
           inputs={"colony": "Colony", "cost": "int"},
           reads=["colony"], writes=["colony"])
def resolve_build_outpost(colony: Colony, cost: int = 2):
    """Spend production to build an outpost (a persistent strategic asset)."""
    if colony.production < cost:
        return MechanismResult.illegal("Not enough production to build an outpost.")
    return MechanismResult.legal(
        BuildOutcome.BUILT,
        changes=(
            ChangeValue(colony.reference, "production", -cost),
            ChangeValue(colony.reference, "outposts", 1),
        ),
    )


class MegafaunaOutcome(Enum):
    ESCALATED = "escalated"
    EASED = "eased"
    STEADY = "steady"


@mechanism(id="megafauna_react", pattern="control_adjudicated", calls=[],
           inputs={"stance": "str", "aggression": "int", "cap": "int"},
           reads=["megafauna"], writes=["megafauna"])
def resolve_megafauna_react(stance: str, aggression: int, cap: int = 5):
    """Megafauna are reactive pressure: exploitative actions escalate them, restorative
    actions ease them. Aggression is clamped to [0, cap]."""
    delta = {"exploit": 1, "restore": -1}.get(stance, 0)
    new = max(0, min(cap, aggression + delta))
    applied = new - aggression
    outcome = (MegafaunaOutcome.ESCALATED if applied > 0
               else MegafaunaOutcome.EASED if applied < 0 else MegafaunaOutcome.STEADY)
    return MechanismResult.legal(
        outcome,
        changes=(ChangeValue("game.megafauna", "aggression", applied),),
        trace_steps=(("react", "Megafauna respond to how the colony treats the Deep.",
                      {"stance": stance, "delta": applied, "aggression": new}),),
    )
