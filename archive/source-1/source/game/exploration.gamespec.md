# The Aphelion Deep — Exploration (package-owned model)

The card-driven exploration loop, authored **in the game** (not in a shared
extension): ordered, persistent, two-faced location decks turned one card at a
time; the expedition gate; Population and the icon vocabulary; Pop-banded upkeep.
It reuses the generic `cards` zone/`card_face` and core mechanisms/state; every
game-specific meaning lives here.

```yaml
# ── the location deck: a cards.zone, positioned by core state (persists across turns) ──
zone:
  id: reef_gardens_deck
  zone_role: ordered_deck
  ordered: true
  reshuffle: never
  source_collection: component.playtest_reef_gardens   # 21 cards, in ID order
  reveal_face: front
  play_face: back
  cursor_state_ref: game.reef_gardens                  # deck_position lives in state.schema

# ── what a turned card does, by its workbook Card Type (the game's own taxonomy) ──
card_disposition_rules:
  id: reef_disposition
  rules:
    flora: play_at_location
    fauna: play_at_location
    mineral: play_at_location
    outpost: play_at_location
    location: play_at_location
    knowledge: to_hand
    equipment: to_hand
    role: to_hand
    department: to_hand
    expedition: set_aside          # the gate
    narrative: resolve_now
    phase_reference: resolve_now
    dilemma: resolve_now
    event: resolve_now

# ── the game's icon vocabulary ──
icon_set:
  id: aphelion_icons
  # The single power/energy icon is `power` (confirmed). The Reef outpost's "per Energy
  # icon" refill and the Glow-Polyp Mat's icon were unified to `power` to match the
  # Crash Flats / Kelp Cathedral cards (Personal Generator, Thermal Generator, Engine Core).
  icons: [oxygen, knowledge, food, power, biomass, materials, pressure, reactor]

# ── the expedition gate (card 15) — turning stops here; descend only if paid ──
expedition:
  id: reef_caverns
  location_deck_ref: game.reef_gardens_deck
  marker_card: component.reef_gardens_15_reef_caverns
  gate:
    requirement: { oxygen: 2, knowledge: 2 }           # "2 [Oxygen] + 2 [Knowledge]"
    sourced_from: [hand, this_location]
    resolution: { mechanism_ref: mechanism.check_expedition_gate }
  on_open: continue_turning

# ── an outpost + play area at this location ──
outpost:
  id: reef_garden_outpost
  location_deck_ref: game.reef_gardens_deck
  upkeep_ref: game.reef_outpost_upkeep

# Outpost upkeep (Hydroponics + Rations) is free-form prose, not Pop-banded — declared
# but flagged unresolved so the port gap is tracked, not silently dropped.
upkeep:
  id: reef_outpost_upkeep
  card_ref: component.reef_gardens_9_reef_garden_outpost
  status: unresolved             # "Hydroponics: refill rations per Energy; Rations: each player pays food/…"
  bands: []

# ── structured, Pop-banded upkeep for the cards whose text is regular ──
# Filterweed parses fully; the population-dynamics fauna keep their bands but their
# effect ops are not yet encoded (flagged, not silently skipped).
upkeep:
  id: filterweed_upkeep
  card_ref: component.reef_gardens_10_shallowwater_filterweed
  resolution: { mechanism_ref: mechanism.resolve_pop_upkeep }
  provides_icons: [ { icon: oxygen, amount: 1, min_pop: 3 } ]
  bands:
    - { pop: 0,   ops: [] }
    - { pop: 1,   ops: [ { op: change_population, target: self, delta: 1 } ] }
    - { pop: "2-4", ops: [ { op: change_population, target: self, delta: 2 } ] }
    - { pop: 5,   ops: [] }

upkeep:
  id: grazers_upkeep
  card_ref: component.reef_gardens_11_spotted_grazers
  resolution: { mechanism_ref: mechanism.resolve_pop_upkeep }
  status: partial                # bands parsed; effect ops need hand-encoding (consume/else)
  bands:
    - { pop: 0,   ops: [] }
    - { pop: "1-2", ops: null }   # "-1 Population from Fauna then +1 Pop, else -1 Pop"
    - { pop: "3-4", ops: null }
    - { pop: 5,   ops: null }
```
