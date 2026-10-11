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
