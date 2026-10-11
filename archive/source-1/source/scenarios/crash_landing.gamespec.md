# The Aphelion Deep — Scenario: Crash Landing (v0.1)

The opening state: the colony scattered across ship fragments, the reactor freshly sunk,
the shallows only beginning to stir.

```yaml
scenario:
  id: crash_landing
  display_name: Crash Landing
  setting_ref: setting.the_reactor

  active_roles:
    include: [game.command, game.engineering, game.exploration, game.ecology, game.medical, game.corporate]

  starting_state:
    game.reactor_countdown.phase: 1
    game.production.value: 0

  objectives:
    - ref: game.stabilise_the_reactor
      tier: shared

  briefing_assignments:
    - recipient_ref: game.command
      compose: [game.philosophy_brief_template]   # each player also draws a hidden philosophy

  component_selection:
    include_collections:
      - component.playtest_crash_flats
      - component.playtest_reef_gardens
      - component.playtest_kelp_cathedral
      - component.aphelion_salvage
      - component.knowledge_cards
      - component.challenge_cards

  scaling: { by_player_count: [20, 25, 30] }

  # Tier-1 executable acceptance path (fact state-machine). Actions carry the
  # rule (owner_role / requires_facts / produces_facts in game/the_deep); this is
  # the ordered sequence. gsx L5 proves each step's actor owns it, its
  # preconditions hold, and every required fact is reachable from initial_facts.
  initial_facts: [colony_operational]
  steps:
    - { kind: action, ref: game.build_an_outpost,        actor: game.engineering }
    - { kind: action, ref: game.run_upkeep,              actor: game.colony_control }
    - { kind: action, ref: game.slow_the_reactor,        actor: game.engineering }
    - { kind: action, ref: game.attempt_stabilise_reactor, actor: game.engineering }

  # Tier-2: the SAME sequence executed through the engine over the state schema.
  # gsx L5 proves the sequence is legal & reachable (facts); tier2 proves it also
  # produces the intended numeric end-state. per-step values that are adjudicated
  # (the containment applied) are supplied as context.
  tier2:
    initial:
      colony: { production: 4, life_support: 10, headcount: 3, outposts: 2 }
    context:
      attempt_stabilise_reactor: { containment_added: 3 }
    expect_all: applied
    assert_state:
      reactor: { stabilised: true, containment: 3 }
      colony:  { outposts: 3 }
```
