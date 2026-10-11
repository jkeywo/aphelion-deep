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
