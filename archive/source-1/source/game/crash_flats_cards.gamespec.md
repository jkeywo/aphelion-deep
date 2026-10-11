# The Aphelion Deep — Crash Flats card capabilities (front / back effect blocks)

The Engineering department's tutorial location, captured as **data** the same way as
Reef Gardens: one block for the **front** (in play), one for the **back** (setup /
in-play state). The interpreter (`mechanisms/card_effects.py`) reads them — no
per-card logic in the sim. `gsx` (L6) validates every verb, icon, track and
reference; `status: unresolved` is an honest, tracked gap.

Crash Flats is a **Wreckage** site: several cards' rules key off *Wreckage-keyword
cards' Abundance*, encoded with the `keyword_track_ge` condition. The salvage
recipes (`s1`, `s3`), the reactor cascade (`c2`) and the Engine-Core sub-location
descent are **not** part of the ordered turn-deck — they enter play by crafting /
triggers / a paid flip, so their economy is flagged `unresolved` while their icons
and tracks are still captured.

```yaml
# 1 — tutorial narrative (the back drives setup)
card_effects:
  id: crash_flats_1_a_rough_landing
  front: { narrative: true }
  back:  { on_reveal: [ { instruction: read_aloud }, { disposition: discard } ] }

# 2 — Engineering Department: reveal the role card; each player keeps one
card_effects:
  id: crash_flats_2_engineering_department
  front: { narrative: true }
  back:
    on_reveal:
      - { reveal_cards: { positions: [3] } }
      - { each_player_chooses: { from: revealed, keep: 1, read_back_privately: true } }

# 3 — Fabrication Lead: passive Power icon (Personal Generator)
card_effects:
  id: crash_flats_3_fabrication_lead
  front: { role: true, hidden: true }
  back:
    disposition: to_player_hand
    passive:
      - { provides_icon: { icon: power, amount: 1 } }

# 8 — Phase Reference (informational)
card_effects:
  id: crash_flats_8_phase_reference
  front: { narrative: true }
  back:  { on_reveal: [ { instruction: read_aloud }, { disposition: set_beside_deck } ] }

# 9 — Crash Flats Outpost (Fabrication Bay): Fabricator discount + Rations obligation
card_effects:
  id: crash_flats_9_crash_flats_outpost_fabrication_bay
  front:
    upkeep:
      - { status: unresolved, text: "Fabricator: items crafted here cost 1 fewer resource (crafting economy not modelled)" }
      - player_obligation:
          each_player:
            - { has_icon: food }
            - { change_track: { track: population, target: { type: flora, at: location, choose: player } } }
            - { change_track: { track: rations } }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_location_track: { track: rations, value: 5 } }

# 10 — Tidal Rust Bloom (Flora, Wreckage): produces on Pop bands, Wreckage-gated growth
card_effects:
  id: crash_flats_10_tidal_rust_bloom
  front:
    upkeep:
      conditional:
        - { when: { self_pop_ge: 2 }, do: [ { produce_resource: { resource: materials, amount: 1 } } ] }
        - { when: { self_pop_ge: 4 }, do: [ { produce_resource: { resource: food, amount: 1 } } ] }
        - { when: { keyword_track_ge: { keyword: wreckage, track: abundance, value: 3 } },
            do: [ { change_track: { track: population, target: self, delta: 1 } } ] }
        - { when: { not: { keyword_present: { keyword: wreckage } } },
            do: [ { change_track: { track: population, target: self, delta: -1 } } ] }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: population, value: 2 } }

# 11 — Carrier Crabs (Fauna, Prey, Wreckage): Materials while fed; consume-from-Fauna dynamics
card_effects:
  id: crash_flats_11_carrier_crabs
  front:
    upkeep:
      - conditional:
          - { when: { all: [ { self_pop_ge: 3 },
                             { keyword_track_ge: { keyword: wreckage, track: abundance, value: 3 } } ] },
              do: [ { produce_resource: { resource: materials, amount: 1 } } ] }
          - { when: { not: { keyword_track_ge: { keyword: wreckage, track: abundance, value: 2 } } },
              do: [ { change_track: { track: population, target: self, delta: -1 } } ] }
      - bands:
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

# 12 — Aphelion Wreckage Field (Mineral, Wreckage): convert Abundance to 2x Materials
card_effects:
  id: crash_flats_12_aphelion_wreckage_field
  front:
    upkeep:
      - { convert_track: { from: abundance, to: materials, amount: all, rate: 2 } }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: abundance, value: 5 } }

# 13 — Salvage Manifest (Knowledge): 2 Knowledge (when crafting Salvage), conditional gain
card_effects:
  id: crash_flats_13_salvage_manifest
  front:
    provides_icon:
      - { icon: knowledge, amount: 2 }        # printed "when creating Aphelion Salvage items"
    upkeep:
      - { status: unresolved, text: "the 2 Knowledge apply only while crafting Aphelion Salvage (crafting not modelled)" }
  back:
    on_reveal:
      - { disposition: set_beside_deck }
    conditional_gain:
      - { to: player_hand, when: { keyword_count_ge: { keyword: aphelion_salvage, count: 3 } } }

# 14 — The Power Question (Dilemma, Wreckage): unanimous, three real options
card_effects:
  id: crash_flats_14_the_power_question
  front:
    dilemma:
      choose: unanimous
      options:
        - { id: restart, label: "Restart it",
            do: [ { provides_icon: { icon: power, amount: 2 } },
                  { status: unresolved, text: "the Reactor track advances 1 (board reactor clock — mechanisms/reactor.py, not wired to card dilemmas)" } ] }
        - { id: strip, label: "Strip for parts",
            do: [ { set_track: { track: abundance, target: card.crash_flats_12_aphelion_wreckage_field, value: 5 } } ] }
        - { id: seal, label: "Seal it", do: [ { instruction: inform_control } ] }
  back: { on_reveal: [ { disposition: resolve_now } ] }

# 15 — Engine Core Section (Sub-Location, Hydrothermal): the flip-to-explore gate
card_effects:
  id: crash_flats_15_engine_core_section
  front: { narrative: true }
  back:
    gate:
      requires: { oxygen: 1, power: 3 }
      sourced_from: [hand, location]
      on_meet: { open_expedition: true }

# ── not in the ordered turn-deck: recipes crafted at an outpost, and a reactor cascade ──

# s1 — Oxygen Tank (Equipment, Aphelion Salvage recipe): craft 1 Materials -> an Oxygen icon
card_effects:
  id: crash_flats_s1_oxygen_tank
  front:
    provides_icon: [ { icon: oxygen, amount: 1 } ]
    craft: { cost: { materials: 1 }, to: player_hand }     # "Spend 1 Materials to take into hand"
  back: { on_reveal: [ { disposition: set_beside_deck } ] }

# s3 — Aphelion Scan Database (Equipment, Aphelion Salvage recipe): craft needs 3 Power -> Knowledge
card_effects:
  id: crash_flats_s3_aphelion_scan_database
  front:
    provides_icon: [ { icon: knowledge, amount: 1 } ]
    craft: { requires: { power: 3 }, to: player_hand }     # "Requires 3 Power; take into hand"
  back: { on_reveal: [ { disposition: set_beside_deck } ] }

# c2 — Reactor Pulse (Cascade): a Tier-1-wide shock (per-board here); triggered, not turned
card_effects:
  id: crash_flats_c2_reactor_pulse
  front:
    on_reveal:
      - { for_each: { filter: { type: flora }, do: [ { change_track: { track: population, target: self, delta: -1 } } ] } }
      - { for_each: { filter: { type: mineral }, do: [ { change_track: { track: abundance, target: self, delta: -1 } } ] } }
  back: { on_reveal: [ { disposition: resolve_now } ] }
```
