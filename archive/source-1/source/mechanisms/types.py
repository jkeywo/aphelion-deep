from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ReactorState:
    reference: str
    phase: int
    max_phase: int = 6
    stabilised: bool = False
    containment: int = 0            # progress toward stabilisation
    containment_needed: int = 3


@dataclass(frozen=True)
class Colony:
    reference: str
    production: int = 0
    life_support: int = 0
    headcount: int = 0
    outposts: int = 0
