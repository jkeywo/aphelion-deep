# The Aphelion Deep — Kelp Cathedral card capabilities (front / back effect blocks)

The third Tier-1 location, captured as **data** like the others. Kelp Cathedral is
an **entry-gated** location: its own card (1) carries the gate — you need
`2 Oxygen` to explore here at all (contrast Reef, whose gate sits mid-deck at the
Reef Caverns). The interpreter reads these blocks; `gsx` (L6) validates them.

New to this location and now in the vocabulary: the **Pressure** icon, the
**Scanning** track (the Survey Drone), and cross-card triggers by card name
(`card_track_ge`) and by ecosystem role (`keyword_present`, `keyword_track_ge`).
The Survey Drone's movement and the Thermal Generator's install economy are honest
`unresolved` gaps.

```yaml
# 1 — Kelp Cathedral (Location): an Oxygen icon, Kelp biomass + Rations upkeep, entry gate
card_effects:
  id: kelp_cathedral_1_kelp_cathedral
  front:
    provides_icon:
      - { icon: oxygen, amount: 1 }
    upkeep:
      - { produce_resource: { resource: biomass, amount: 1 } }     # "Kelp: 1 biomass per turn for crafting"
      - player_obligation:
          each_player:
            - { has_icon: food }
            - { change_track: { track: population, target: { type: flora, at: location, choose: player } } }
            - { change_track: { track: rations } }
  back:
    on_reveal:
      - { disposition: play_at_location }
    gate:
      requires: { oxygen: 2 }
      sourced_from: [hand, location]
      on_meet: { open_expedition: true }

# 2 — Giant Lungweed Stalks (Flora, Kelp): Oxygen/Pressure by Pop, cross-card growth
card_effects:
  id: kelp_cathedral_2_giant_lungweed_stalks
  front:
    provides_icon:
      - { icon: oxygen, amount: 1, when: { self_pop_ge: 2 } }
      - { icon: pressure, amount: 1, when: { self_pop_ge: 3 } }
    upkeep:
      conditional:
        - { when: { card_track_ge: { card: kelp_cathedral_4_hush_mussels, track: population, value: 3 } },
            do: [ { change_track: { track: population, target: self, delta: 1 } } ] }
        - { when: { board_icon_ge: { icon: reactor, value: 3 } },
            do: [ { change_track: { track: population, target: self, delta: -1 } } ] }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: population, value: 2 } }

# 3 — Resonating Lure Fish (Fauna, Kelp): a Pressure icon when fed; Flora-gated
card_effects:
  id: kelp_cathedral_3_resonating_lure_fish
  front:
    provides_icon:
      - { icon: pressure, amount: 1,
          when: { all: [ { self_pop_ge: 2 },
                         { keyword_track_ge: { keyword: prey, track: population, value: 2 } } ] } }
    upkeep:
      conditional:
        - { when: { card_track_ge: { card: kelp_cathedral_2_giant_lungweed_stalks, track: population, value: 3 } },
            do: [ { change_track: { track: population, target: self, delta: 1 } } ] }
        - { when: { not: { keyword_present: { type: flora } } },
            do: [ { change_track: { track: population, target: self, delta: -1 } } ] }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: population, value: 2 } }

# 4 — Hush Mussels (Flora, Kelp): grows near the Lure Fish, wanes without a Mineral
card_effects:
  id: kelp_cathedral_4_hush_mussels
  front:
    upkeep:
      conditional:
        - { when: { card_track_ge: { card: kelp_cathedral_3_resonating_lure_fish, track: population, value: 2 } },
            do: [ { change_track: { track: population, target: self, delta: 1 } } ] }
        - { when: { not: { keyword_present: { type: mineral } } },
            do: [ { change_track: { track: population, target: self, delta: -1 } } ] }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: population, value: 2 } }

# 5 — Sunken Survey Drone (Wreckage, Item): Scanning track drives Knowledge
card_effects:
  id: kelp_cathedral_5_sunken_survey_drone
  front:
    provides_icon:
      - { icon: knowledge, amount: 1, when: { self_track_ge: { track: scanning, value: 3 } } }
      - { icon: knowledge, amount: 1, when: { self_track_ge: { track: scanning, value: 5 } } }
    upkeep:
      - { change_track: { track: scanning, target: self, delta: 1 } }
      - { status: unresolved, text: "can be moved between locations; on move reset Scanning to 2 (card movement not modelled)" }
  back:
    on_reveal:
      - { disposition: set_beside_deck }
      - { status: unresolved, text: "craft: spend 2 Materials to flip and set Scanning to 4 (crafting not modelled)" }

# 6 — The Bloom (Event, Kelp): every Kelp Flora here gains a Pop
card_effects:
  id: kelp_cathedral_6_the_bloom
  front:
    on_reveal:
      - { for_each: { filter: { type: flora, keyword: kelp },
            do: [ { change_track: { track: population, target: self, delta: 1 } } ] } }
  back:
    on_reveal:
      - { disposition: set_aside }
      - { status: unresolved, text: "flip the next time an exploration starts here (deferred event trigger not modelled)" }

# 7 — Cathedral Hymn (Knowledge, Kelp): a Fauna boost, dual-prerequisite gain
card_effects:
  id: kelp_cathedral_7_cathedral_hymn
  front:
    upkeep:
      conditional:
        - { when: { keyword_present: { type: flora, keyword: kelp } },
            do: [ { change_track: { track: population, target: { type: fauna, choose: player }, delta: 2 } } ] }
  back:
    on_reveal:
      - { disposition: set_beside_deck }
    conditional_gain:
      - { to: player_hand, when: { all: [
            { card_track_ge: { card: kelp_cathedral_2_giant_lungweed_stalks, track: population, value: 5 } },
            { card_track_ge: { card: kelp_cathedral_3_resonating_lure_fish, track: population, value: 5 } } ] } }

# 8 — Echoing Drowned Mass (Dilemma, Kelp, Wreckage): three options, effects unprinted
card_effects:
  id: kelp_cathedral_8_echoing_drowned_mass
  front:
    dilemma:
      choose: unanimous
      options:
        - { id: cut_free, label: "Cut it free",  do: [ { status: unresolved, text: "effect unprinted on the card (???)" } ] }
        - { id: recover, label: "Recover it",     do: [ { status: unresolved, text: "effect unprinted on the card (???)" } ] }
        - { id: document, label: "Document and leave", do: [ { status: unresolved, text: "effect unprinted on the card (???)" } ] }
  back: { on_reveal: [ { disposition: resolve_now } ] }

# s4 — Thermal Power Generator (Outpost Upgrade, Aphelion Salvage): craft 3 Materials -> 2 Power
card_effects:
  id: kelp_cathedral_s4_thermal_power_generator
  front:
    provides_icon: [ { icon: power, amount: 2 } ]
    craft: { cost: { materials: 3 }, to: tuck }            # "Spend 3 Materials to install, tuck under outpost"
  back: { on_reveal: [ { disposition: set_beside_deck } ] }
```
