# The Aphelion Deep — Reef Gardens card capabilities (front / back effect blocks)

Each card's rules captured as **data**, from its printed text: one block for the
**front** (what it shows / does in play) and one for the **back** (its in-play state
and setup instructions). The sim's interpreter (`mechanisms/card_effects.py`) reads
these and works out what to do — no per-card logic in the sim.

Effect verbs are a closed vocabulary (see `docs/card_effects_vocabulary.md`);
`gsx` validates that every icon/track/reference resolves and every verb is known.
`status: unresolved` on an effect is an honest, tracked gap.

```yaml
# 1 — tutorial narrative (no mechanic; the back drives setup)
card_effects:
  id: reef_gardens_1_a_rough_landing
  front: { narrative: true }
  back:  { on_reveal: [ { instruction: read_aloud }, { disposition: discard } ] }

# 2 — Department: reveal the two role cards; each player keeps one
card_effects:
  id: reef_gardens_2_ecology_department
  front: { narrative: true }
  back:
    on_reveal:
      - { reveal_cards: { positions: [3, 4] } }
      - { each_player_chooses: { from: revealed, keep: 1, read_back_privately: true } }

# 3 — Lead Ecologist: passive Oxygen icon (persistent, not consumed)
card_effects:
  id: reef_gardens_3_lead_ecologist
  front: { role: true, hidden: true }
  back:
    disposition: to_player_hand
    passive:
      - { provides_icon: { icon: oxygen, amount: 1 } }

# 4 — Systems Ecologist: passive Cultivator (a player action, not an icon)
card_effects:
  id: reef_gardens_4_systems_ecologist
  front: { role: true, hidden: true }
  back:
    disposition: to_player_hand
    passive:
      - { action: { id: cultivator,
                    change_track: { track: population, target: { type: flora, at: location, choose: player }, delta: 1 } } }

# 8 — Phase Reference (informational)
card_effects:
  id: reef_gardens_8_phase_reference
  front: { narrative: true }
  back:  { on_reveal: [ { instruction: read_aloud }, { disposition: set_beside_deck } ] }

# 9 — Reef Garden Outpost: Hydroponics + Rations, now encoded.
card_effects:
  id: reef_gardens_9_reef_garden_outpost
  front:
    upkeep:
      - refill_track: { track: rations, per_icon: power }
      - player_obligation:
          each_player:
            - { has_icon: food }
            - { change_track: { track: population, target: { type: flora, at: location, choose: player } } }
            - { change_track: { track: rations } }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_location_track: { track: rations, value: 3 } }

# 10 — Shallowwater Filterweed: Oxygen while Pop 3+, Pop-banded upkeep
card_effects:
  id: reef_gardens_10_shallowwater_filterweed
  front:
    provides_icon:
      - { icon: oxygen, amount: 1, when: { self_pop_ge: 3 } }
    upkeep:
      bands:
        - { pop: 0,   do: [] }
        - { pop: 1,   do: [ { change_track: { track: population, target: self, delta: 1 } } ] }
        - { pop: "2-4", do: [ { change_track: { track: population, target: self, delta: 2 } } ] }
        - { pop: 5,   do: [] }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: population, value: 2 } }

# 11 — Spotted Grazers: consume-from-Fauna / else, now encoded.
# DESIGN NOTE: the card text says "−N Population from Fauna", but the flavour says
# Grazers graze the Filterweed (a Flora). Encoded LITERALLY as Fauna (other fauna
# at the location). Confirm the intended pool (Fauna vs Flora).
card_effects:
  id: reef_gardens_11_spotted_grazers
  front:
    upkeep:
      bands:
        - { pop: 0, do: [] }
        - { pop: "1-2", do: [ { consume_population: { from: { type: fauna, exclude_self: true }, amount: 1,
              then: [ { change_track: { track: population, target: self, delta: 1 } } ],
              else: [ { change_track: { track: population, target: self, delta: -1 } } ] } } ] }
        - { pop: "3-4", do: [ { consume_population: { from: { type: fauna, exclude_self: true }, amount: 2,
              then: [ { change_track: { track: population, target: self, delta: 2 } } ],
              else: [ { change_track: { track: population, target: self, delta: -2 } } ] } } ] }
        - { pop: 5, do: [ { consume_population: { from: { type: fauna, exclude_self: true }, amount: 3,
              then: [],
              else: [ { change_track: { track: population, target: self, delta: -2 } } ] } } ] }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: population, value: 2 } }

# 12 — Coral Shelf Formation: choose-one upkeep, now encoded (convert or grow Abundance)
card_effects:
  id: reef_gardens_12_coral_shelf_formation
  front:
    upkeep:
      - { choose_one: [ { convert_track: { from: abundance, to: materials, amount: all } },
                        { change_track: { track: abundance, target: self, delta: 1 } } ] }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: abundance, value: 2 } }

# 13 — Reef Ecologist's Notes: Knowledge icon, CONDITIONAL gain
card_effects:
  id: reef_gardens_13_reef_ecologist_s_notes
  front:
    provides_icon:
      - { icon: knowledge, amount: 1 }        # once gained to a hand
    upkeep:
      - { status: unresolved, text: "Take 1 Reef Fauna/Flora into hand" }
  back:
    on_reveal:
      - { disposition: set_beside_deck }
    conditional_gain:
      - { to: player_hand, when: { location_cards_pop_ge: { pop: 4, count: 2 } } }

# 14 — Spawning Ground: unanimous dilemma, each option a real effect
card_effects:
  id: reef_gardens_14_spawning_ground
  front:
    dilemma:
      choose: unanimous
      options:
        - { id: harvest, label: "Harvest",
            do: [ { provides_icon: { icon: food, amount: 1 } }, { tuck: { under: outpost } } ] }
        - { id: protect, label: "Protect",
            do: [ { change_track: { track: population, target: card.reef_gardens_10_shallowwater_filterweed, delta: 2 } },
                  { change_track: { track: population, target: card.reef_gardens_11_spotted_grazers, delta: 2 } } ] }
        - { id: tag_monitor, label: "Tag & Monitor",
            do: [ { provides_icon: { icon: knowledge, amount: 1 } }, { tuck: { under: outpost } } ] }
  back: { on_reveal: [ { disposition: resolve_now } ] }

# 15 — Reef Caverns: the expedition gate (presence test)
card_effects:
  id: reef_gardens_15_reef_caverns
  front: { on_reveal: [ { instruction: read_aloud }, { disposition: set_aside } ] }
  back:
    gate:
      requires: { oxygen: 2, knowledge: 2 }
      sourced_from: [hand, location]
      on_meet: { open_expedition: true }

# ── The caverns (revealed only after the gate is paid) ──

# 16 — Glow-Polyp Mat (Flora): its "Power token" is a Power icon at Pop 4+.
card_effects:
  id: reef_gardens_16_glow_polyp_mat
  front:
    provides_icon:
      - { icon: power, amount: 1, when: { self_pop_ge: 4 } }
    upkeep:
      conditional:
        - { when: { card_track_ge: { card: reef_gardens_18_echoing_calcite_spires, track: abundance, value: 2 } },
            do: [ { change_track: { track: population, target: self, delta: 1 } } ] }
        - { when: { board_icon_ge: { icon: reactor, value: 2 } },
            do: [ { change_track: { track: population, target: self, delta: -1 } } ] }
  back:
    on_reveal: [ { disposition: play_at_location }, { set_track: { track: population, value: 2 } } ]

# 17 — Crystalblind Snapper (Fauna, apex predator): consumes Prey population
card_effects:
  id: reef_gardens_17_crystalblind_snapper
  front:
    upkeep:
      bands:
        - { pop: 0, do: [] }
        - { pop: "1-3", do: [ { consume_population: { from: { keyword: prey }, amount: 1,
              then: [ { change_track: { track: population, target: self, delta: 1 } } ],
              else: [ { change_track: { track: population, target: self, delta: -1 } } ] } } ] }
        - { pop: "4-5", do: [ { consume_population: { from: { keyword: prey }, amount: 2,
              then: [ { change_track: { track: population, target: self, delta: 1 } } ],
              else: [ { change_track: { track: population, target: self, delta: -1 } } ] } } ] }
  back:
    on_reveal: [ { disposition: play_at_location }, { set_track: { track: population, value: 2 } } ]

# 18 — Echoing Calcite Spires (Mineral). NOTE: upkeep says "Population 2+" but the card
# tracks Abundance; encoded against Abundance — confirm.
card_effects:
  id: reef_gardens_18_echoing_calcite_spires
  front:
    upkeep:
      conditional:
        - { when: { self_track_ge: { track: abundance, value: 2 } },
            do: [ { produce_resource: { resource: materials, amount: 1 } } ] }
        - { when: { card_track_ge: { card: reef_gardens_16_glow_polyp_mat, track: population, value: 4 } },
            do: [ { change_track: { track: abundance, target: self, delta: 1 } } ] }
        - { when: { board_icon_ge: { icon: reactor, value: 3 } },
            do: [ { change_track: { track: population, target: self, delta: -1 } } ] }
  back:
    on_reveal: [ { disposition: play_at_location }, { set_track: { track: abundance, value: 2 } } ]

# 19 — Drowned Survey Cache (Knowledge): icon + conditional gain across two cards
card_effects:
  id: reef_gardens_19_drowned_survey_cache
  front:
    provides_icon: [ { icon: knowledge, amount: 1 } ]
    action: { id: trash_ask_control, status: unresolved, text: "Trash: ask Control any question (adjudicated)" }
  back:
    on_reveal: [ { disposition: set_beside_deck } ]
    conditional_gain:
      - { to: player_hand, when: { all: [
            { card_track_ge: { card: reef_gardens_16_glow_polyp_mat, track: population, value: 4 } },
            { card_track_ge: { card: reef_gardens_18_echoing_calcite_spires, track: abundance, value: 4 } } ] } }

# 20 — The Watcher in the Dark (Event): an area effect that removes itself when it does nothing
card_effects:
  id: reef_gardens_20_the_watcher_in_the_dark
  front:
    upkeep:
      - { for_each: { filter: { type: fauna }, where: { self_pop_ge: 3 },
            do: [ { change_track: { track: population, target: self, delta: -1 } } ],
            if_none: [ { remove_self: true } ] } }
  back:
    on_reveal: [ { disposition: play_at_location } ]

# 21 — Bioluminescent Pollination (Knowledge): movement/Depth trigger not yet modelled
card_effects:
  id: reef_gardens_21_bioluminescent_pollination
  front:
    upkeep:
      - { status: unresolved, text: "A Flora you move gains +1 Pop on arrival if at Depth 3+ (movement/Depth not modelled)" }
  back:
    on_reveal: [ { disposition: to_player_hand } ]
```
