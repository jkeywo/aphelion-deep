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
