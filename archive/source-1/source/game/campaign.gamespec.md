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
