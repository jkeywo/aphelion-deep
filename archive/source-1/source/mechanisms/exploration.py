"""The Aphelion Deep — exploration mechanisms (package-owned).

These are the game's own mechanisms for its card-driven exploration: resolving a
card's Pop-banded upkeep, deriving the icons a card provides from its Population,
and testing an expedition gate. They use the generic runtime (pure functions that
return proposed changes) and carry v0.7 contracts so gsx validates them.

Everything with game meaning — Population, icons, the op vocabulary — lives here in
the package, not in the shared `cards` extension.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

from gamespec import ChangeValue, MechanismResult, mechanism


@dataclass(frozen=True)
class CardState:
    reference: str            # e.g. "card.reef_gardens_10_shallowwater_filterweed"
    population: int = 0


class UpkeepOutcome(Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"     # the card's upkeep is not yet encoded (prose only)


def _band_for(bands, pop):
    for b in bands:
        if b["lo"] <= pop <= b["hi"]:
            return b
    return None


@mechanism(id="resolve_pop_upkeep", pattern="banded_outcome", calls=[],
           inputs={"card": "CardState", "bands": "list"},
           reads=["card_population"], writes=["card_population"])
def resolve_pop_upkeep(card: CardState, bands: list):
    """Select the Population band for this card and apply its encoded ops. Ops are
    the closed vocabulary; a band whose ops are unencoded (prose only) is reported
    UNRESOLVED so the gap is explicit rather than silently skipped."""
    band = _band_for(bands, card.population)
    if band is None:
        return MechanismResult.illegal("no upkeep band covers population %d" % card.population)
    if band.get("ops") is None:
        return MechanismResult.legal(UpkeepOutcome.UNRESOLVED, changes=(),
                                     trace_steps=(("unresolved", band.get("raw", ""), {}),))
    changes = []
    for op in band["ops"]:
        if op["op"] == "change_population":
            changes.append(ChangeValue(card.reference, "population", op["delta"]))
        elif op["op"] == "no_effect":
            pass
        else:                                   # produce_icon / consume_population / … not yet wired
            return MechanismResult.legal(UpkeepOutcome.UNRESOLVED, changes=(),
                                         trace_steps=(("unresolved_op", op["op"], {}),))
    return MechanismResult.legal(UpkeepOutcome.RESOLVED, changes=tuple(changes),
                                 trace_steps=(("upkeep", band["pop"], {"delta_ops": band["ops"]}),))


@mechanism(id="provide_icons", pattern="derivation", calls=[],
           inputs={"card": "CardState", "rules": "list"}, reads=["card_population"], writes=[])
def resolve_provide_icons(card: CardState, rules: list):
    """Derive the icons a card contributes right now from its Population — e.g.
    Filterweed provides 1 Oxygen while Population >= 3. No state change."""
    icons = {}
    for rule in rules or []:
        if card.population >= rule.get("min_pop", 0):
            icons[rule["icon"]] = icons.get(rule["icon"], 0) + rule.get("amount", 1)
    return MechanismResult.legal(icons, changes=())


@mechanism(id="check_expedition_gate", pattern="threshold_test", calls=[],
           inputs={"requirement": "dict", "available": "dict"}, reads=[], writes=[])
def resolve_check_expedition_gate(requirement: dict, available: dict):
    """The expedition gate: legal iff the available icons (from hand + this location)
    meet the marker's requirement. Illegal -> the location offers no expedition."""
    short = {k: v for k, v in requirement.items() if available.get(k, 0) < v}
    if short:
        return MechanismResult.illegal("gate requirement not met; short of %s" % short)
    return MechanismResult.legal("gate_open", changes=())
