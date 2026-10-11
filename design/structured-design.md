# The Aphelion Deep Structured Design Annex

Consolidated from the supplied Aphelion Deep design sources. Working design; unresolved passages retain their original status. The tutorial amendments in Core Rules govern the declared three turn slice.

July GameSpec extensions are preserved below. These declarations describe the broader game and do not override the tutorial amendments.

# The Aphelion Deep — Outposts, Economy, and Drowned Tech (v0.1)

Persistent outposts and milestones (campaign), the closed economy (core resources), and the
Drowned technology deck (cards).

```yaml
# ---- persistent outposts + milestones (campaign) ----
persistent_effect:
  id: outpost
  kind: strategic_asset
  attaches_to: game.colony
  mechanical: { production: per_site, reactor_slow: if_adjacent }
  note: the main strategic unit of play; sustainable systems that grow stronger over time

progression_track:
  id: milestones
  scope: campaign
  state_ref: game.milestone_state
  note: permanent milestone consequences that mirror the fate of the Drowned

# Life support is produced by the Medical department's systems each upkeep.
subsystem: { id: medical_systems, team_ref: game.medical, produces: [game.life_support] }

# ---- closed economy (core resources; no external resupply) ----
resource: { id: production, sources: [game.run_upkeep], sinks: [game.slow_reactor_with_outpost, game.build_an_outpost], conserved: false }
resource: { id: life_support, sources: [game.medical_systems], sinks: [game.run_upkeep], conserved: false, note: the colony's living limit }

# ---- Drowned technology (cards): pure upside early, stranger and more dangerous deeper ----
zone: { id: drowned_deck, owner_scope: system, zone_role: draw_deck, visibility: hidden_all, ordered: true, accepts: [card] }
zone: { id: knowledge_display, owner_scope: shared, zone_role: market_row, visibility: public, ordered: true, accepts: [card] }

supply:
  id: drowned_tech
  kind: row
  source_deck: drowned_deck
  width: 4
  refill: on_reveal
  acquire_destination: knowledge_display
  note: deeper Drowned cards are more powerful and harder to use, with mounting warnings

card:
  id: drowned_relic_generic
  types: [drowned_tech]
  value_source: component.drowned_tech
  # effect resolution would be a core mechanism; left design-only in this draft (unresolved)
  abilities:
    - window: cards.upkeep
      unresolved: { question: Exact Drowned-tech effects and costs are not yet authored., status: open }
```


# The Aphelion Deep - Playtest Card System (v0.1)

Card faces, printed text, icon refs, track names, source IDs, designer notes, and deck
membership live in `source/components/components.xlsx`, imported from
`C:\AnalogueGames\TheAphelionDeep\abyssfall_cards_v3.xlsx`.

```yaml
# ---- zones ----
zone: { id: location_deck, owner_scope: system, zone_role: draw_deck, visibility: public_top, ordered: true, accepts: [card] }
zone: { id: revealed_location, owner_scope: shared, zone_role: in_play, visibility: public, ordered: true, accepts: [card] }
zone: { id: player_hand, owner_scope: player, zone_role: hand, visibility: hidden_owner, ordered: false, accepts: [card] }
zone: { id: challenge_deck, owner_scope: system, zone_role: draw_deck, visibility: hidden_all, ordered: true, accepts: [card] }
zone: { id: discard, owner_scope: shared, zone_role: discard, visibility: public, ordered: true, accepts: [card] }

# ---- imported playtest collections ----
supply: { id: reef_gardens_playtest_deck, kind: composed_deck, source_collection: component.playtest_reef_gardens, acquire_destination: revealed_location, note: "21 cards from abyssfall_cards_v3.xlsx" }
supply: { id: crash_flats_playtest_deck, kind: composed_deck, source_collection: component.playtest_crash_flats, acquire_destination: revealed_location, note: "14 cards from abyssfall_cards_v3.xlsx" }
supply: { id: kelp_cathedral_playtest_deck, kind: composed_deck, source_collection: component.playtest_kelp_cathedral, acquire_destination: revealed_location, note: "9 cards from abyssfall_cards_v3.xlsx" }
supply: { id: aphelion_salvage_deck, kind: composed_deck, source_collection: component.aphelion_salvage, acquire_destination: player_hand, note: "5 salvage/equipment cards from abyssfall_cards_v3.xlsx" }
supply: { id: knowledge_deck, kind: composed_deck, source_collection: component.knowledge_cards, acquire_destination: player_hand, note: "5 knowledge cards from abyssfall_cards_v3.xlsx" }
supply: { id: challenge_deck, kind: composed_deck, source_collection: component.challenge_cards, acquire_destination: revealed_location, note: "4 challenge/cascade/signal cards from abyssfall_cards_v3.xlsx" }

# ---- timing ----
timing_window: { id: exploration_reveal }
timing_window: { id: expedition_resolution }
timing_window: { id: upkeep }
timing_window: { id: crisis }

# ---- card families ----
card:
  id: imported_playtest_location_card
  types: [location, flora, fauna, mineral, dilemma, event, expedition, narrative, department, phase_reference]
  deck_role: location_playtest
  value_source: component.Cards
  abilities:
    - window: cards.exploration_reveal
      unresolved: { question: Convert each imported location card's instructions into mechanism refs where needed., status: open }

card:
  id: imported_playtest_hand_card
  types: [role, knowledge, equipment, outpost_upgrade]
  deck_role: player_hand
  value_source: component.Cards
  abilities:
    - window: cards.upkeep
      unresolved: { question: Convert role, knowledge, and salvage hand effects into mechanism refs where needed., status: open }

card:
  id: imported_playtest_challenge_card
  types: [challenge, cascade, signal, megafauna]
  deck_role: crisis
  value_source: component.Cards
  abilities:
    - window: cards.crisis
      unresolved: { question: Convert challenge and cascade resolution into Control/automated-opponent procedures., status: open }
```

## Imported Counts

- `component.playtest_reef_gardens`: 21 cards
- `component.playtest_crash_flats`: 14 cards
- `component.playtest_kelp_cathedral`: 9 cards
- `component.aphelion_salvage`: 5 cards
- `component.knowledge_cards`: 5 cards
- `component.challenge_cards`: 4 cards

Some cards intentionally belong to more than one collection, such as knowledge cards that
also sit inside a location deck.


# The Aphelion Deep — Departments and Hidden Philosophy (v0.1)

Six departments (core teams) with real early Command authority (facilitation), and a hidden
philosophy per player (briefings). Representative subset; the six follow one shape.

```yaml
# ---- departments (core teams) ----
team: { id: command,     display_name: Command,     design_intent: [distributes bounties; authority real early, scarce late] }
team: { id: engineering, display_name: Engineering, design_intent: [reactor containment and outpost construction] }
team: { id: exploration, display_name: Exploration, design_intent: [expeditions into deeper, stranger waters] }
team: { id: ecology,     display_name: Ecology,      design_intent: [permaculture systems; megafauna relations] }
team: { id: medical,     display_name: Medical,      design_intent: [life support; the colony's living limit] }
team: { id: corporate,   display_name: Corporate,    design_intent: [data and the Drowned-tech economy] }

# ---- Command authority via facilitation (Control adjudicates contested Command calls) ----
control_role:
  id: colony_control
  display_name: Colony Control
  responsibilities: [run the phases, resolve expedition outcomes, adjudicate megafauna and Drowned-tech consequences]
  adjudicates: [game.expedition_outcome]

adjudicated_input:
  id: expedition_outcome
  judge_ref: game.colony_control
  question: Given the site, the team, and the colony's standing with the Deep, how does this expedition resolve?
  output_block: expedition_result
  visibility: facilitator_only

# ---- hidden philosophy (briefings): each player's allegiance is private ----
# Generic recipient: every player receives the philosophy briefing.
role: { id: any_player, note: generic briefing recipient (every player) }

# The hidden allegiances pulling the colony apart — a primary pressure loop.
pressure_loop:
  id: philosophy_divergence
  summary: Hidden philosophies push players toward incompatible futures for the colony, creating friction under shared survival.

briefing:
  id: philosophy_brief_template
  recipient_ref: game.any_player
  information:
    knows: [your department's mandate]
    believes: [your philosophy is the right future for the colony]
    explicitly_does_not_know: [which other players share or oppose your philosophy]
  goals:
    - id: advance_philosophy
      visibility: private
      statement: Steer the colony's milestone decisions toward your philosophy without fracturing survival.

# the five philosophies are hidden allegiances assigned via briefings, surfacing through play
objective: { id: restorationist, scope: actor, visibility: private, statement: Heal the world; undo the crash's harm. }
objective: { id: settler,        scope: actor, visibility: private, statement: Build a permanent home here. }
objective: { id: preservationist,scope: actor, visibility: private, statement: Touch the Deep as little as possible. }
objective: { id: exploiter,      scope: actor, visibility: private, statement: Extract what you can; leave if you must. }
objective: { id: transcendence,  scope: actor, visibility: private, statement: Become something the Drowned became. }
```


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


# The Aphelion Deep — Game Contract (v0.1)

A largely cooperative survival megagame (~30 players, six departments) on the alien ocean
world of Abyssfall. Stabilise the sunken reactor before it goes critical, while philosophies
divide the colony over how to live on the world. Fiction (the Deep, the Drowned, megafauna,
the reactor) is the Abyssfall WorldSpec dependency; this package owns the game.

```yaml
game:
  id: aphelion_deep
  display_name: The Aphelion Deep
  game_family: cooperative_megagame
  active_extensions: [cooperative, automated-opponent, facilitation, briefings, cards, campaign]

  player_count: { min: 20, max: 30 }

  premise: |
    Survivors of a crashed colony ship must live on an alien ocean. The reactor has sunk and
    will go critical unless stabilised. Build sustainable systems, explore the deepening
    waters, recover Drowned technology, and decide — across clashing philosophies — what kind
    of future the colony is for.

  play_experience:
    - cooperative survival with meaningful friction between departments and philosophies
    - a visible endgame clock (the reactor) with permanent milestone consequences
    - exploration that grows stranger and more powerful as it goes deeper
    - megafauna as reactive pressure that forces negotiation, not just jeopardy

  core_design_goals:
    - id: outposts_are_the_lever
      statement: Outposts are the main strategic unit and the mechanism for slowing the reactor.
    - id: philosophy_is_hidden_allegiance
      statement: Each player's philosophy is a hidden layer that surfaces through megafauna and Drowned decisions.
    - id: command_scarce_late
      statement: Command authority is real early and scarce late.

  primary_pressure_loops:
    - game.reactor_countdown        # the shared loss clock
    - game.philosophy_divergence    # hidden allegiances pull the colony apart

setting_refs:
  - setting.the_reactor
  - setting.the_drowned
  - setting.megafauna

design_modules: [departments, the_deep, campaign, cards]
```

## Core loop

Expedition Phase (explore/discover) → Assignment Phase (Command directs) → Upkeep &
Production (systems produce, reactor advances). Control facilitates; the reactor clock and
megafauna are run by the automated opponent.

```yaml
turn_loop:
  id: colony_round
  phase_sequence: [game.expedition, game.assignment, game.upkeep]
phase: { id: expedition, display_name: Expedition, function: freeform_action }
phase: { id: assignment, display_name: Assignment, function: team_planning, design_intent: [Command distributes bounties and directs activity] }
phase: { id: upkeep,     display_name: Upkeep and Production, function: economy, design_intent: [systems produce; the reactor advances] }
```


# The Aphelion Deep — The Reactor, the Megafauna, the Shared Outcome (v0.1)

Cooperative structure (shared survival, pressure/recovery, anti-quarterbacking) over the
automated opponent (the reactor clock and the reactive megafauna).

```yaml
# ---- shared outcome (cooperative) ----
objective:
  id: stabilise_the_reactor
  scope: scenario
  shared: true
  visibility: public
  statement: Stabilise, contain, or otherwise resolve the sunken reactor before it goes critical.

cooperative_outcome:
  id: colony_outcome
  victory: { objective_ref: game.stabilise_the_reactor }
  defeat_conditions:
    - id: reactor_critical
      when: reactor_clock_reaches_final_phase_unresolved
    - id: colony_collapse
      when: life_support_fails
  scaling: { player_counts: [20, 25, 30], knobs: [reactor_phase_length, megafauna_aggression] }

# ---- reactor clock + megafauna (automated-opponent) ----
threat_system:
  id: reactor_countdown
  type: doom_clock
  escalation:
    source: end_of_upkeep
    procedure:
      - Advance the reactor one phase; apply its Phase effect (each phase is worse).
      - Outposts adjacent to the reactor may spend production to slow it.
  propagation: [each phase activates a new deep hazard and a stronger megafauna]
  defeat_conditions: [reactor_reaches_final_phase_unresolved]
  recovery_paths: [game.slow_reactor_with_outpost]

ai_controller:
  id: megafauna_ai
  mode: reactive
  activation_trigger: on_colony_action_against_the_deep
  priority:
    - respond to how the colony treats the ocean (removal, extraction, restoration)
    - escalate against Exploiter-leaning actions; ease toward Restorationist actions
  information_used: [recent colony actions, philosophy signals surfaced in play]
  note: megafauna are reactive pressure that create negotiation, not just jeopardy

pressure_source:
  id: the_reactor
  type: fixed_clock
  visible: true
  predictable: high
  threat_system_ref: automation.reactor_countdown
  recovery_paths: [game.slow_reactor_with_outpost]

recovery_path:
  id: slow_reactor_with_outpost
  cost: { outpost_production: 1 }
  effect: slow the reactor's advance
  opportunity_cost: production not spent on exploration or life support

quarterbacking_model:
  information_openness: partially_open      # philosophies are hidden
  role_ownership: high                      # distinct department mandates
  mitigations:
    - { id: hidden_philosophy, type: hidden_information, effect: no single player can solve the colony's optimal path }
```

## Actions and resolution wiring (executable)

The mechanical core now resolves via real Python mechanisms (`source/mechanisms/`, 16 tests).

```yaml
# Each action now BINDS its mechanism's inputs: state objects come from `state`,
# per-invocation values (player/adjudicated) from `context`, config from `constant`.
# Bindings only SELECT data — they never compute (that is the mechanism's job).
action:
  id: run_upkeep
  owner_role: game.colony_control
  requires_facts: [colony_operational]
  produces_facts: [upkeep_done]
  resolution:
    mechanism_ref: mechanism.produce_upkeep
    inputs:
      colony:      { select: { source: state, ref: game.colony } }
      per_outpost: { select: { source: constant, value: 1 } }
action:
  id: advance_the_reactor
  owner_role: game.colony_control
  requires_facts: []
  produces_facts: [reactor_advanced]
  resolution:
    mechanism_ref: mechanism.advance_reactor
    inputs:
      reactor: { select: { source: state, ref: game.reactor } }
      slow:    { select: { source: context, key: slow, default: 0 } }
action:
  id: slow_the_reactor
  invocation: outpost spends production
  owner_role: game.engineering
  requires_facts: [outpost_built]
  produces_facts: [reactor_slowed]
  resolution:
    mechanism_ref: mechanism.slow_reactor
    inputs:
      colony:           { select: { source: state, ref: game.colony } }
      production_spent: { select: { source: context, key: production_spent, default: 1 } }
action:
  id: attempt_stabilise_reactor          # distinct from the shared objective 'stabilise_the_reactor'
  invocation: Engineering + Drowned containment
  owner_role: game.engineering
  requires_facts: [outpost_built]
  produces_facts: [reactor_stabilised]
  resolution:
    mechanism_ref: mechanism.stabilise_reactor
    inputs:
      reactor:           { select: { source: state, ref: game.reactor } }
      containment_added: { select: { source: context, key: containment_added, default: 0 } }
action:
  id: build_an_outpost
  owner_role: game.engineering
  requires_facts: [colony_operational]
  produces_facts: [outpost_built]
  resolution:
    mechanism_ref: mechanism.build_outpost
    inputs:
      colony: { select: { source: state, ref: game.colony } }
      cost:   { select: { source: constant, value: 2 } }

# the megafauna controller and the shared outcome resolve via mechanisms too
ai_controller_resolution: { megafauna_ai: mechanism.megafauna_react }
cooperative_outcome_resolution: { colony_outcome: mechanism.check_endgame }
```


## Abyssfall world dependency

# Entities — Abyssfall

```yaml
species:
  id: megafauna
  name: Abyssal Megafauna
  summary: Enormous reactive creatures of the Deep; not merely hazards — their responses create negotiation over how the colony treats the ocean.
  canon_status: canon
polity:
  id: the_drowned
  name: The Drowned
  summary: A lost undersea civilisation whose ruins yield powerful, dangerous technology; their fate mirrors the players' choices.
  canon_status: canon
location:
  id: the_reactor
  name: The Sunken Reactor
  summary: The colony ship's reactor, sunk deep, on a countdown to going critical — the game's endgame clock.
  canon_status: canon
```


# World: Abyssfall (v0.1, worldspec-core)

The regular-science-fiction ocean world of The Aphelion Deep. A crashed colony ship's
survivors must live on an alien sea whose depths hold a drowned civilisation.

```yaml
world:
  id: abyssfall
  premise: |
    A colony ship crash-lands on an alien ocean world. Its reactor has sunk deep and will
    go critical unless stabilised. Survivors must build sustainable systems, explore deeper
    and stranger waters, and reckon with the Drowned — a lost civilisation whose fate mirrors
    the choices the survivors now face.
genre_profile:
  id: science_fiction
  tech_level: crashed colony technology; salvage and permaculture; recovered "Drowned" alien tech
  cosmology: a material alien ecology; the Drowned are gone but their works persist
  vocabulary_defaults: [outpost, expedition, the Drowned, megafauna, reactor, the Deep]
```
