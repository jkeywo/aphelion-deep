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
