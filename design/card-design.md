# The Aphelion Deep Card Design Reference

Consolidated from the supplied Aphelion Deep design sources. Working design; unresolved passages retain their original status. The tutorial amendments in Core Rules govern the declared three turn slice.

# Abyssfall — Card Design Requirements

*Reference document for writing new location decks, Control event cards, and role cards*

---

## Table of Contents

1. [Core System Summary](#1-core-system-summary)
2. [Card Anatomy — Universal Rules](#2-card-anatomy--universal-rules)
3. [Location Deck Requirements](#3-location-deck-requirements)
4. [Card Type Specifications](#4-card-type-specifications)
5. [Depth Markers and Gate Requirements](#5-depth-markers-and-gate-requirements)
6. [Icon and Resource Reference](#6-icon-and-resource-reference)
7. [Challenge Deck](#7-challenge-deck)
8. [Auxiliary Decks](#8-auxiliary-decks)
9. [Cross-Deck Combination Rules](#9-cross-deck-combination-rules)
10. [Design Checklist](#10-design-checklist)

---

## 1. Core System Summary

Each explorable location in Abyssfall is represented by a self-contained card deck. The deck *is* the location — there is no separate map. Exploring a location means drawing from its deck.

**Three card states:**
- **In sequence** — not yet drawn; face-down in the deck
- **In play** — drawn, placed on the table, tracked with tokens
- **In hand** — taken by a player as a role card, knowledge card, or device; reusable

**Resources** are physical tokens that flow, accumulate, and deplete: Food, Water, Biomass, Materials.

**Icons** are printed on cards (in play, at outposts, or in hand) and checked as capability gates. They are never consumed: Oxygen, Power, Knowledge, Pressure Rating, Bioluminescence, Resonance, Toxin Tolerance, Alien Attunement.

**Exploration cost** is paid in resources to draw the next card. This is the primary action economy limiter. Players gain resources each turn from outposts and ecosystems.

Every card (with the exception of Role Cards) has two sides: a light **content face** and a dark **instruction face**. Players read the instruction face when a card is first drawn; they interact with the content face while the card is in play.

---

## 2. Card Anatomy — Universal Rules

### 2.1 Two-sided card structure

Every card except Role Cards has two sides:

**Content face** (light background)

The game-mechanical side. Always face-up when the card is in play. Contains all fields listed in Section 2.2.

**Instruction face** (dark background, white text, Aphelion logo at bottom)

The setup and teaching side. Read when the card is first drawn. Tells the player what to do with the card and, in depth-1 and depth-2 decks, explains the mechanic being introduced. Always ends with either a stock phrase (see Section 2.4) or an explicit "Next:" instruction.

Tutorial text on instruction faces should be richest in depth-1 decks, lighter in depth-2, minimal in depth-3, and absent in depth-4 and depth-5. By depth-3, players are expected to recognise card types on sight. See Section 3.7 for tutorialisation guidelines.

**Role Card exception**

Role Cards (cards 3–7 in depth-1 decks) have a public content face and a private brief face. They have no dark instruction back. See Section 4.10.

### 2.2 Content face fields

Every card regardless of type must include the following fields. Empty fields are left blank, not omitted.

| Field | Required for | Notes |
|---|---|---|
| **Card #** | All | Integer. Displayed in top-right corner. |
| **Deck label** | All | Bottom-right corner. Format: `Location Name – N` (e.g., `Reef Garden – 9`). |
| **Name** | All | Short, evocative. Avoid generic scientific names for shallow tiers. |
| **Type tag** | All | Below the title, right-aligned. See Section 4 for type names. |
| **In Play / Effect** | All | What the card does while active, including icon provision. |
| **Token Track** | Flora, Fauna, Mineral, Outpost | Format: `[Track Name] 0–[max] (starts at [n])`. One track per card. Only include if the card uses tokens. |
| **Triggers** | Flora, Fauna, Mineral | Interactions with other in-play cards at the same location. State both positive and negative triggers. |
| **Degradation** | Flora, Fauna, Mineral | What happens when the token track reaches 0. Usually: trash this card. Some Mineral cards trash permanently. |
| **Outpost Use** | Outpost Blueprints, some Mineral/Flora | `Portrait: [effect]. Landscape: [effect].` Portrait is primary; Landscape is simpler or cheaper. |
| **Hand Version** | Flora, Fauna, Knowledge | Format: `[Card Name]: Reusable — [effect]. Trash: [one-time larger effect].` |
| **Icons** | Flora, Fauna, Knowledge, Role | Icons provided by this card, listed with their symbol. |
| **Notes** | All | Design intent, read-aloud text for Events, Control guidance, removal-after-resolution flag. |

### 2.3 Instruction face conventions

Instruction face text must:

- Be written in plain imperative prose addressed directly to the players ("Draw this card," "Set the rations track to 5," "Each player chooses one card to keep")
- Introduce the mechanic being demonstrated before stating the action, in depth-1 and depth-2 decks
- End with either a stock phrase (Section 2.4) or a clear "Next:" instruction pointing to the following card
- Never repeat content already on the content face
- Use italic text for rules context that explains *why* something works the way it does
- Be short enough to read aloud in under 30 seconds

In depth-1 and depth-2 decks, the instruction face is the primary teaching tool. In depth-3+ decks it is a reminder only.

### 2.4 Stock phrases

The following phrases appear verbatim on instruction faces. Players will come to recognise them through repetition. Do not paraphrase these.

| Situation | Stock phrase |
|---|---|
| Auto-draw and set track | `Immediately draw this card and set its [track name] to [N].` |
| Set aside as reference | `Set this card aside with this side up.` |
| Gain to hand | `Take this card into your hand.` |
| Conditional gain to hand | `Gain this card when [condition].` |
| Remove after resolution | `Remove this card from the game.` |
| Exploration gate (instruction face) | `You can start an exploration here if you meet the requirements shown on the other side.` |
| Flip for other phase | `Once [phase] is over, flip this card to see the [other phase] rules.` |
| Private role brief | `Do not show this side to other players.` (displayed in red at top and bottom of Role Card private face) |

When a new auto-draw card appears in a depth-1 deck for the first time, the instruction face may precede the stock phrase with a one-sentence explanation of what a token track is. This explanation should not appear again in the same deck.

### 2.5 Provisional colour system

*This colour system is provisional and subject to change as visual design is finalised.*

| Card category | Content face | Instruction face |
|---|---|---|
| Intro narrative (cards 1–2) | Light with pink-red gradient at base | Dark grey |
| Role Cards (cards 3–7) | Light with green border | Green (private brief face) |
| Phase reference (card 8) | Cream / off-white | Dark grey |
| All location/ecosystem cards | Light blue | Dark grey |

All instruction faces share the same dark grey background and white text. The Aphelion logo appears at the base of every instruction face.

---

## 3. Location Deck Requirements

### 3.1 Deck sizes

All decks are 36 cards. Depth Markers are physical dividers inserted at setup and are not counted in the card total.

| Tier | Cards per deck | Number of decks |
|---|---|---|
| 1 — Sunlit Shallows | 36 (8 intro + 28 location) | 6 |
| 2 — Kelp & Ruins | 36 | 5 |
| 3 — Twilight Shelf | 36 | 4 |
| 4 — Blackwater Depths | 36 | 3 |
| 5 — Abyssal Core | 36 | 2 |

Depth-1 decks are the only decks to include the department intro and character selection cards. All other tiers are pure location decks with all 36 cards available for ecosystem content.

### 3.2 Internal structure

#### Depth-1 decks

**Fixed intro (cards 1–8)**

Always played in sequence. Not shuffled. Teach the game and establish the department.

| Card | Content | Notes |
|---|---|---|
| 1 | Narrative intro | Sets the scene for the crash and the department's situation. Content face only. No mechanics. |
| 2 | Department card | Public face: department name, brief description, department goals. Instruction face: tells players to reveal cards 3–7. |
| 3–7 | Role Cards | Five roles for the department. Players reveal all five, each player chooses one, reads the private face, and sets it aside as their hand card. Unchosen cards are removed from the game. See Section 4.10. |
| 8 | Phase reference | Double-sided: Exploration Phase on one side, Upkeep Phase on the other. Set aside permanently as a table reference. One is included in every depth-1 deck. |

**Location content (cards 9–36)**

The remaining 28 cards form the location's ecosystem. Cards 9–12 are always auto-drawn in sequence as part of location setup (the instruction face of card 8 triggers this). After card 12, the first exploration phase begins.

The standard setup sub-sequence is:
- Card 9: Location Outpost (auto-drawn, track set to starting value)
- Cards 10–12: Starting ecosystem (auto-drawn, tracks set to starting values — typically one Flora, one Fauna, one Mineral)
- Card 13+: The remainder enters the shuffled draw pool, with any Knowledge or Dilemma cards set beside the deck face-down until conditions are met

#### Depth-2+ decks

All 36 cards are location content. The internal structure follows the same four-section architecture:

**Opening sequence** (6–8 cards, fixed order)

The first cards are dealt in printed sequence. They introduce the location and its foundational ecosystem. Each has a `Next:` instruction chaining to the following card. The sequence ends with an Event card that shuffles the remainder into a draw pile.

> The opening sequence must be completable with base resources alone. No icons required to draw cards 1–6.

**Early ecosystem** (cards ~7 to first Depth Marker)

No icon gate. Cards are drawn by spending resources. Ecosystem grows more complex. The first Outpost Blueprint should appear here.

**Mid ecosystem and complications** (between first and second Depth Marker)

Harder unlock costs. At least one Dilemma. Strange or conditional effects. Philosophy pressure increases.

**Endgame cards** (after final Depth Marker, 3–5 cards)

Most powerful cards in the deck. Some gated by ecosystem health conditions in addition to the icon gate. Final card is always a Knowledge card that goes to hand immediately and cannot be trashed. It carries a read-aloud line connecting to the broader narrative.

### 3.3 Card type distribution (approximate)

#### Depth-1 decks (28 location cards, cards 9–36)

| Type | Count |
|---|---|
| Outpost | 1 (card 9, always) |
| Flora | 3–5 |
| Fauna | 3–5 |
| Mineral | 2–3 |
| Knowledge | 3–4 |
| Outpost Blueprint | 2–3 |
| Dilemma | 2–3 |
| Event | 2–3 |
| Depth Markers | 2 (not counted in total) |

#### Depth-2+ decks (all 36 cards)

| Type | Count |
|---|---|
| Flora | 4–6 |
| Fauna | 5–7 |
| Mineral | 2–4 |
| Knowledge | 4–6 |
| Outpost Blueprint | 2–4 |
| Dilemma | 3–5 |
| Event | 2–3 |
| Depth Markers | 2–3 (not counted in total) |

Deeper decks (Tiers 3–5) should shift balance away from basic Flora/Fauna toward Dilemmas, conditional Events, and Knowledge cards. The ecosystem becomes harder to read and more philosophically charged.

### 3.4 Department–location pairing (depth-1 only)

Each depth-1 location deck belongs to one department. The intro cards (1–8) are specific to that department; the location content (9–36) is specific to that location. They are produced and stored together as a single deck.

| Department | Depth-1 location |
|---|---|
| Ecology | Reef Garden |
| Engineering | Crash Flats |
| *(further departments TBD)* | *(further locations TBD)* |

### 3.5 Biome identity

Each deck has a biome identity that shapes every card in it. Before writing a deck, define:

- **What does this place look like?** One vivid paragraph.
- **What is this place's dominant mechanical role?** (e.g. Tier 1: basic sustainability; Tier 3: specialisation without collapse)
- **What is the dominant question this place asks?** (e.g. Reef Garden: *Can we survive?* Lantern Drop: *Can we specialise without collapsing?*)
- **What new icon does this deck introduce, if any?** (See Section 6)

All card names, read-aloud text, and Dilemma situations should feel like they belong to the same place.

### 3.6 Ecosystem logic

Cards within a deck must form a believable food web or geological system. The standard chain is:

**Mineral → Flora → Fauna → Apex Fauna**

Each layer should have at least one positive trigger from the layer below and at least one negative trigger when that layer collapses. This means:

- Fauna that depend on Flora. Flora that benefits from Fauna presence.
- Minerals that are maintained or degraded by biological activity.
- At least one dual-prerequisite unlock (requires two cards at high tokens simultaneously) in the mid or late deck.

Every ecosystem should be able to *thrive* under good management and *collapse* under bad management, with visible intermediate states.

### 3.7 Reactor integration

At least one card per deck must reference the reactor track. The standard effects are:

- **Phase 2+:** a Flora or Mineral card loses tokens per turn (acidification, seismic instability)
- **Phase 3+:** a Flora card loses Health immediately and stops regenerating
- **On construction of a Portrait outpost:** reactor track advances 1 step

Deeper decks should have more reactor sensitivity. By Tier 4, reactor Phase 2 should be actively dangerous to the local ecosystem.

### 3.8 Tutorial card guidelines

Depth-1 and depth-2 decks can and should dedicate instruction face space — and in some cases, whole cards — to tutorialising new mechanics as they are first encountered. The goal is that every mechanic a player needs to understand is taught the first time it appears.

**Depth-1 decks** teach:
- The two-sided card structure (card 1 or 2)
- Department and role selection (card 2 and the role cards)
- The Exploration Phase and Upkeep Phase turn structure (card 8)
- Token tracks and how to set/adjust them (cards 10–12, via instruction face)
- The difference between auto-drawn cards and exploration-drawn cards
- Outpost rules (card 9)
- Dilemma resolution (card 14 or equivalent)
- Knowledge cards and how they are gained (card 13 or equivalent)
- Exploration gates and icon requirements (card 15 or equivalent)
- Crafting (introduced via Mineral instruction face, card 12 or equivalent)

**Depth-2 decks** teach:
- Any new icons introduced at this tier (Pressure Rating)
- Depth Marker checks
- Cross-deck transplanting

**Depth-3 decks** may include brief reminders for:
- New icons (Bioluminescence, Resonance)
- Any mechanics not yet encountered by typical play groups

**Depth-4+ decks** assume full rules literacy. Instruction faces are minimal — stock phrases only.

Tutorial text should always be in italic on the instruction face to distinguish it from the action instruction.

### 3.9 Location keywords

Cards can carry keywords that restrict or unlock other cards. Keywords are printed on the content face below the type tag.

**Existing keywords** (card types that double as keywords): Flora, Fauna, Mineral, Outpost, Knowledge, Dilemma, Prey.

**Location keywords** are a separate category of keyword applied to persistent sub-location cards (see Section 4.1) and to the Location Outpost card itself. They describe what a place *has*, not what a card *is*.

Examples: `Hydrothermal`, `Shallow`, `Reef`, `Wreckage`, `Alien Structure`, `Cavern`.

**How keywords unlock things:**
- A crafting card (Aphelion or Alien Salvage) may list a keyword in its recipe requirements. That recipe can only be built at a location that currently has that keyword present among its in-play cards.
- A Depth Marker or entry requirement may be reduced or waived if a specific keyword is present.
- Some Dilemma or Event outcomes may add a keyword card to a location permanently, changing what can be built or unlocked there going forward.

When writing a new location deck, define the location's intrinsic keywords (printed on the Location Outpost or Location card) and any keywords that can be gained through play. At least one Tier-3+ location should provide a keyword that unlocks a meaningful Alien Salvage recipe.

---

## 4. Card Type Specifications

### 4.1 Location cards

**Location Outpost (depth-1 decks, card 9)**

The first card of the location content sub-sequence. Always auto-drawn. Sets up the base outpost with a starting track value. Carries the location's intrinsic keywords.

**Location card (depth-2+ decks, card 1)**

One per deck. Always free to draw (no unlock cost).

- States that the location is accessible.
- Lists any **entry requirement** (icons checked on arrival, not paid). Entry requirements begin at Tier 2.
- Provides both Portrait and Landscape outpost options for the location's base infrastructure.
- Carries the location's intrinsic keywords.
- Instruction face ends with `Next:` pointing to card 2.

**Sub-location cards**

Persistent cards within a location deck that represent a distinct feature within the broader location — a reef cavern, a hydrothermal vent, an alien ruin. They are drawn during exploration (not auto-drawn) and remain in play permanently once discovered.

- Type tag: `Location`
- Carry one or more location keywords that are added to the location's active keywords once the card is in play.
- May have an exploration gate requirement on the instruction face (players must meet the requirement to flip the card and activate it).
- May provide icons, passive resource effects, or unlock crafting options via their keywords.
- Remain in play indefinitely — they are not trashed, consumed, or sent to hand.

Entry requirements by tier:

| Tier | Minimum entry requirement |
|---|---|
| 1 | None |
| 2 | 2 Oxygen icons |
| 3 | 4 Oxygen + 2 Power + 1 Knowledge icons |
| 4 | 6 Oxygen + 3 Power + 2 Knowledge + 1 Pressure Rating icon |
| 5 | 8 Oxygen + 4 Power + 3 Knowledge + 2 Pressure Rating + 1 Bioluminescence icon |

### 4.2 Flora cards

Represent plant-analogues, algae, mats, polyps, and other sessile producers.

- Produce at least one resource per turn (Food, Water, or Biomass) or provide at least one icon.
- Always have a Population token track.
- Have at least one positive trigger (gaining Population) and one degradation trigger (losing Population).
- Degradation: Population 0 → trash this card.
- Hand version typically enables **transplanting** — introducing this species to another location.

Flora cards are the ecosystem's base layer. They should be among the first cards unlocked in any opening sequence.

### 4.3 Fauna cards

Represent mobile organisms — fish, crawlers, predators, filter feeders, and stranger things in deeper tiers.

- Usually consume one resource per turn and produce a different one (e.g. consume Biomass, produce Food or Materials).
- Or provide icons (Oxygen, Pressure Rating, Bioluminescence) as their primary value.
- Always have a Population token track.
- Prey-type Fauna can have their population spent voluntarily to yield resources (e.g. Biomass).
- Thrive when their food source (usually a Flora card) is healthy. Collapse when it disappears.
- Degradation: Population 0 → trash this card.
- Hand version typically provides a **behaviour study** — a tool for navigating or protecting ecosystems.

Apex Fauna (large predators, keystone species) should have dual-prerequisite unlocks and passive effects that protect the whole ecosystem while present.

### 4.4 Mineral cards

Represent geological features, alien structures, thermal systems, crystalline formations.

- Produce Materials, Power, or Knowledge per turn.
- Have an Abundance token track. Abundance degrades from biological neglect or reactor activity.
- Unlike Flora and Fauna, some Mineral cards trash **permanently** when Abundance reaches 0 — the resource is exhausted.
- Deeper Mineral cards increasingly provide Resonance or other alien-tier icons.
- Outpost use is common for Mineral cards — they represent sites worth building on.
- The instruction face of the first Mineral card in a depth-1 deck introduces crafting: *Minerals, Coral, and other crafting ingredients can be used to craft items, found on the crafting table and made at an outpost during the Upkeep phase.*

### 4.5 Knowledge cards

Represent research, observations, decoded data, and accumulated understanding.

- Go directly to hand when drawn OR are set beside the deck with the instruction face up, to be gained when a stated condition is met.
- Always have a hand version with a **Reusable** effect and a **Trash** effect.
- The Trash effect should be noticeably more powerful — using it is a real decision.
- Some Knowledge cards cannot be trashed (final cards, philosophy-critical cards). State this explicitly.
- Knowledge cards at higher tiers should provide **cross-location utility** — asking Control questions, modifying other decks, bridging to deeper tiers.

The instruction face of the first Knowledge card in a depth-1 deck introduces the concept: *Knowledge cards can be gained to a player's hand during an expedition when certain conditions are met.*

Do not use Knowledge cards to deliver rules. They deliver capability, information, and narrative.

### 4.6 Outpost Blueprint cards

Represent sites, structures, or systems that can be converted from ecosystem assets into infrastructure.

- Always offer two orientations: **Portrait** (primary, more powerful) and **Landscape** (simpler, more autonomous).
- Portrait effects often require ongoing maintenance (Engineering upkeep, staffing, or a linked ecosystem card at minimum tokens).
- Landscape effects are reliable but lower yield.
- If not claimed as an outpost, the card remains in play in the ecosystem and provides a modest passive benefit.
- Claiming an outpost removes the card from the ecosystem — this is a real trade-off.

### 4.7 Dilemma cards

Represent moments of genuine choice with philosophical stakes.

- Always offer **two or three options** (A, B, and optionally C), displayed as labelled side-panels on the content face.
- Each option has a clear mechanical effect, including any icon it tucks beneath the outpost card.
- The options should map to different philosophies without naming them. One option should favour Preservation/protection; one should favour extraction or pragmatism; a third (if present) should favour knowledge, contact, or settler-oriented investment.
- Removed from the deck after resolution. Never stays in play.
- Control notes who argued for what, even if that instruction isn't printed on the card.

The instruction face of the first Dilemma card in a depth-1 deck introduces the concept: *Some cards have decisions to make during an expedition. The group must choose an option unanimously.*

**Dilemma design rules:**
- The situation must be specific and vivid. Abstract moral questions don't work at the table.
- No option should be obviously correct. If one option is clearly best, it's not a dilemma.
- Mechanical consequences should be real but not catastrophic. The point is philosophy surfacing, not player punishment.
- At least one option per dilemma should cost nothing — choosing it still reveals something.

### 4.8 Event cards

Represent sudden changes to the local ecosystem, reactor pulses, or global shifts.

Two sub-types:

**Sequence-ender Events** (always card 6 or 7 in depth-2+ opening sequences)
- Read aloud a flavour line.
- Apply a simple positive effect (usually: all Flora gain 1 Population).
- Formally end the fixed sequence and shuffle the remainder into a draw pile.
- Removed after resolution.

**Draw-pool Events** (shuffled into the open draw pile)
- May be triggered always-on (drawn as normal) or conditionally (only if an ecosystem health condition is met).
- Apply effects that create pressure: token losses, reactor advancement, resource costs, forced choices.
- Some Events set up future Dilemmas by placing Control tokens (Watcher, Megapredator Territory, etc.).
- Conditional reward Events are only triggerable if the ecosystem is thriving — they should feel like the location acknowledging the players' stewardship.
- Removed after resolution.

### 4.9 Phase Reference card

One per depth-1 deck. Always card 8.

- Double-sided: Exploration Phase rules on one side, Upkeep Phase rules on the other.
- Both sides carry a `flip` stock phrase directing players to the other side at the appropriate moment.
- Background is cream/off-white (provisional — see Section 2.5).
- Set aside permanently after being drawn. It is a table reference for the rest of the game.
- Not subject to any unlock cost — it is triggered automatically by card 8's position in the opening sequence.

### 4.10 Role cards

Role Cards are the depth-1 equivalent of starting hand cards. Cards 3–7 in every depth-1 deck.

**Public face (content face)**
- Light background with green border (provisional).
- Fields: role title, role description (what this person does and why they matter), icons provided, passive effect, reusable hand effect, trash effect.
- The `????` and `???` placeholders in the template indicate game stats and abilities still to be designed.

**Private face (brief face)**
- Green background.
- `Do not show this side to other players.` in red at top and bottom.
- Fields: character brief (1–2 sentences of personality/motivation), Personal Goals (1–3 bullet points).
- No dark instruction back. This side replaces the instruction face.

**Selection and removal**
- During card 2's instruction, all five Role Cards (3–7) are revealed. Each player chooses one, reads the private face, and keeps it as their hand card for the rest of the game.
- Unchosen Role Cards are removed from the game.
- Players with fewer than five in their department use **Proxy Role Cards** (see Section 4.11).

**Role card design rules**

- **Icon assignment** — the icon provided should reflect professional orientation:

| Archetype | Appropriate icon |
|---|---|
| Biological / ecological roles | Oxygen |
| Engineering / technical roles | Power |
| Research / analytical roles | Knowledge |
| Medical / support roles | Oxygen or Knowledge |
| Command / coordination roles | Knowledge |
| Corporate / data roles | Knowledge |
| Exploration / navigation roles | Oxygen or Pressure Rating |

- **Philosophy integration** — the card must signal the player's hidden philosophy through its *mechanics*, not its text. The philosophy should never be mechanically revealed by using the card — only philosophically implied.

| Philosophy | Mechanical signal |
|---|---|
| Preservationist | Abilities that protect existing ecosystem cards from harm |
| Settler | Abilities that reduce costs for others or document system connections |
| Restorationist | Abilities focused on repair, reactor interaction, recovery |
| Exploiter | Abilities that recover value from damaged or exhausted systems |
| Transcendence | Abilities that interact with alien systems or ask Control unusual questions |

- The passive effect must be **immediately useful on turn 1** with no setup required.
- The reusable hand effect should scale in value as the game develops.
- The trash effect should be memorable and represent the philosophy's core value. It is a moment of commitment.
- No Role Card may provide more than one icon.
- No two Role Cards within the same department may duplicate each other's mechanical function.

### 4.11 Proxy Role cards

Used when a department has fewer than five players. Drawn from the **Proxy Role Deck** (see Section 8.3).

- One Proxy Role Card per absent player.
- Provides the missing role's icon and passive mechanical benefit only — no reusable effect, no trash effect, no private face.
- Held by any willing player in the department (they may hold their own Role Card and a Proxy simultaneously).
- Not a secret — the Proxy's role is written on the front.
- Kept as simple as possible. The intent is to make the missing power available without adding decision weight.

---

## 5. Depth Markers and Gate Requirements

Depth Markers are physical dividers inserted into the shuffled draw pile at setup. When an expedition draws a Depth Marker, they check their current icon total across all sources (hand cards, outpost modules, in-play ecosystem cards at this location). If the check passes, remove the marker and continue. If it fails, return it to the top of the deck — exploration halts for this turn.

### 5.1 Gate positions within a deck

For depth-1 decks, positions are counted from card 9 (the start of location content):

| Tier | Gate 1 | Gate 2 | Gate 3 |
|---|---|---|---|
| 1 (depth-1 decks, 28 location cards) | After location card 10 | After location card 18 | After location card 25 |
| 2–5 (36-card decks) | After card 15 | After card 24 | After card 30 |

### 5.2 Icon requirements by tier and gate

| Tier | Gate 1 | Gate 2 | Gate 3 |
|---|---|---|---|
| 1 | 2 Oxygen + 1 Power | 4 Oxygen + 2 Power + 1 Knowledge | 6 Oxygen + 3 Power + 2 Knowledge + 1 Pressure Rating |
| 2 | 3 Pressure Rating | 5 Pressure Rating + 1 Knowledge | — |
| 3 | 4 Bioluminescence + 2 Resonance | 6 Bioluminescence + 3 Resonance + 1 Knowledge | — |
| 4 | 4 Toxin Tolerance + 3 Bioluminescence + 2 Resonance | — | — |
| 5 | (To be defined — Alien Attunement required) | — | — |

Later tiers have fewer gates because the entry requirement already filters for significant capability.

### 5.3 Gate design principles

- Gates should be passable with reasonable ecosystem investment in the current tier, plus some material from one tier deeper.
- No gate should require icons that only exist two or more tiers beyond the current one.
- Passing a gate should feel like an achievement, not like checking a box.
- The cards immediately after a gate should reward having made it — they should be visibly more interesting than the cards before.

---

## 6. Icon and Resource Reference

### 6.1 Resources (tracked with tokens)

| Resource | Primary source | Primary use |
|---|---|---|
| Food | Flora cultivation, Fauna | Expedition costs, upkeep, unlock costs |
| Water | Filtration Flora, Mineral conversion | Unlock costs, system maintenance |
| Biomass | Fauna, thermal vents | Mid-tier unlock costs, conversion feedstock |
| Materials | Mineral cards, Fauna (shells, casings) | Outpost construction, deep-tier costs |

Resources are **consumed** when spent. They must be replenished each turn from outposts and ecosystems.

### 6.2 Icons (printed on cards — checked, never consumed)

| Icon | Introduced | Primary sources |
|---|---|---|
| Oxygen | Tier 1 | Shallow Flora (Filterweed, Bladder Fish, Sunfan Coral), outpost modules |
| Power | Tier 1–2 | Bioluminescent Polyps, Anemones, Thermal Upwelling, outpost modules |
| Knowledge | Tier 2 | Mineral ruins, Knowledge hand cards, outpost modules |
| Pressure Rating | Tier 2 | Deep Flora (Kelp, Lungweed), Mineral networks, outpost modules |
| Bioluminescence | Tier 3 | Lantern Polyps, Void Drifters, deep outpost modules |
| Resonance | Tier 3 | Resonance Nodes, alien structure cards |
| Toxin Tolerance | Tier 4 | Calcified Bloom, Marrow Crawler, Medical department hand cards |
| Alien Attunement | Tier 5 | Not yet defined — reserved for Abyssal tier |

### 6.3 Icon provisioning rules

- **In-play ecosystem cards** provide icons to any expedition present at that location.
- **Outpost modules** (tucked Blueprint cards) provide icons permanently at that outpost.
- **Hand cards** (Role Cards, Knowledge cards) provide icons wherever the holder is present.
- Icons stack across all three sources.
- A single card may provide multiple different icons (e.g. Fissure Crawler provides both Bioluminescence and Pressure Rating).

When writing a new deck, map out the icon provision curve: how many of each icon can a fully-developed ecosystem provide? This determines what depth gates are reachable from within the location itself versus requiring cross-location investment.

---

## 7. Challenge Deck

The Challenge Deck is held by the GM team and injected into the game as needed. Cards are never shuffled into location decks. It replaces the old Control Event system entirely.

**36 cards.** Weighted approximately: 50% Intrusion, 25% Cascade, 25% Signal.

### 7.1 Three Challenge card types

**Intrusion Events**

Something unwanted enters a location — megafauna, hostile organisms, equipment failures. Players must choose between spending resources to respond or accepting consequences.

- Name a specific creature or phenomenon.
- State a clear trigger condition for play (e.g. "play when two or more Fauna cards are at Population 4+").
- Provide 2–3 response options with different mechanical and philosophical costs.
- At least one option should plant a future consequence — a token or a card added to another deck.

**Cascade Events**

Systemic pressure across one or more locations. Token losses, reactor advancement, icon reduction.

- Affect a defined scope (one location, all Tier 2 locations, all Mineral cards globally).
- Should feel like a natural consequence of the world's instability, not an arbitrary punishment.
- Include a read-aloud line.

**Signal Events**

Narrative injections with no mandatory mechanical effect. Designed to surface hidden philosophies and create table drama.

- Describe something discovered or overheard. Make it specific.
- State: "No mechanical effect." or give a very minor optional action.
- Always include: "Control notes who investigates, who ignores it, and who tries to suppress it."

### 7.2 Challenge Deck design rules

- **Play condition** must be printed on the card. GMs should never have to judge whether to play a card — the condition tells them.
- At least one option in any Intrusion Event should **cross deck boundaries** — seeding a consequence in another location's deck or creating a token that appears in a future Dilemma.
- Signal Events should never feel like rewards or punishments. They are observations that create pressure by existing.
- Challenge cards should be paced: 1–2 per turn at most, more during moments of false stability.

---

## 8. Auxiliary Decks

Four physical decks sit outside the location deck system. They are set up separately at the start of the game and interact with location play without belonging to any single location.

| Deck | Cards | Setup |
|---|---|---|
| Aphelion Salvage Deck | 36 | Distributed to Tier-1 locations after Turn 1 (Engineering receives theirs in Turn 1) |
| Alien Salvage Deck | 36 | Unlocked in chunks at Tier-3 locations when alien structures are discovered |
| Proxy Role Deck | 30 | Held by GM; cards drawn as needed for absent players |

### 8.1 Aphelion Salvage Deck

Represents craftable items salvaged from the wreckage of the E.S.S. Aphelion. The wreck is a finite resource — once a copy of a card is claimed, it is gone.

**Physical setup**

After Turn 1, the GM distributes subsets of Aphelion Salvage cards face-up (recipe/instruction face showing) to each Tier-1 location. Each location receives a thematically appropriate selection. Cards are visible at all times so players know what can be built.

**Exception:** The Engineering department receives their subset during Turn 1 as part of their tutorial, learning the crafting mechanism before other departments.

**Card counts**

Most cards have 3 copies. Range is 1–6, based on how broadly useful or situational the item is. Scarcer items (1–2 copies) represent limited-run components from the wreck; common items (4–6 copies) represent modular components in wider supply.

**Crafting procedure**

1. A player identifies a recipe they want to build (instruction face of the Salvage card, currently at some location).
2. They ensure that, during the Upkeep phase, the recipe card and all required ingredients (resources, keywords) are present at the same location.
3. At Upkeep, if all requirements are met, the player takes the Salvage card into their hand — content face now active as an equipment or outpost upgrade card.
4. If the recipe requires a location keyword (e.g. `Hydrothermal`), the recipe card must be physically at a location where that keyword is currently active.

**Moving recipe cards**

Salvage cards can be moved between locations during the Exploration phase, like any other portable item. Trickier recipes will need to be brought to better-equipped locations before they can be built. This is intentional — logistics is part of the challenge.

**Example items**

| Item | Notes |
|---|---|
| Oxygen Tank | Provides an Oxygen icon; consumable version possible |
| Harpoon Gun | Expedition equipment; combat or harvest use |
| Submarine | The ultimate vehicle; functions as a portable outpost |
| Thermal Power Generator | Requires `Hydrothermal` keyword; provides Power icons to an outpost |
| *(further items TBD)* | |

**Card anatomy**

Aphelion Salvage cards follow standard two-sided card anatomy (Section 2.1):
- **Content face:** item name, type tag (`Equipment` or `Outpost Upgrade`), effect, any ongoing cost or keyword provided.
- **Instruction face (recipe):** ingredients required (resources, icons, keywords), outpost requirement if any, and the stock phrase `Meet these requirements during Upkeep to take this card into your hand.`

### 8.2 Alien Salvage Deck

Functions identically to the Aphelion Salvage Deck but represents recovered alien technology from drowned structures. Introduced later in the game when players reach Tier-3 locations.

**Unlock mechanism**

When players first discover an alien structure (a sub-location card with the `Alien Structure` keyword at Tier 3 or deeper), they report to a GM. The GM hands them a number of Alien Salvage cards face-down, proportional to the significance of the discovery. If 2–3 alien structures exist, each unlocks a separate chunk of the Alien Salvage Deck.

Alien Salvage cards are placed face-down at the discovering location. Players must study them (flip them during an expedition at that location) before they can be built — unlike Aphelion Salvage cards, which are always visible.

**Design principles**

- Alien Salvage items should be more powerful than Aphelion Salvage equivalents, requiring rarer ingredients or alien-tier keywords.
- At least one Alien Salvage item should require `Alien Structure` as a location keyword to build — tying construction to proximity to the source.
- Items should feel qualitatively different from Aphelion salvage: less mechanical repair, more transformation or augmentation.

### 8.3 Proxy Role Deck

A 30-card deck containing one simplified proxy card for every player role across all departments (6 departments × 5 roles = 30 cards).

Used when a department has fewer than five players. The GM hands the relevant proxy card(s) to the department at the start of the game.

**Card anatomy**

Proxy Role Cards are simplified, single-sided cards (no private brief face, no instruction face):
- Role title and department
- Icon provided (matching the full Role Card)
- Passive mechanical benefit (matching the full Role Card)
- No reusable effect, no trash effect

The card reads plainly so any player can pick it up mid-session and understand it immediately.

**Design rules**

- Each Proxy Role Card must be mechanically identical to the passive layer of its corresponding full Role Card.
- When a Role Card is updated, its proxy must be updated to match.
- Proxy cards are never secret. Their role and department are clearly visible.

---

## 9. Cross-Deck Combination Rules

Any player may take a card from one location's ecosystem and introduce it to another. This is a universal action — not restricted to any department, though Ecology hand cards make it easier.

### 9.1 How transplanting works

A Flora or Fauna card can be taken into hand as its hand-card version. The hand version includes a **transfer cost** (the resource cost to introduce it to a new location). When introduced:

- The card enters the new location's ecosystem at Population/Health 1.
- It immediately begins interacting with in-play cards at its new location via its Triggers.
- It does not re-enter the original location's deck.

### 9.2 Cross-deck interaction design rules

When writing triggers for a new card, consider whether they should respond to **transplanted cards from other decks**. This creates emergent cross-location ecosystems.

- Triggers should reference **card types** (Flora, Fauna, Mineral) or **icon types** rather than specific card names where possible, so they respond to anything introduced.
- Specific card-name triggers are acceptable for iconic interactions (e.g. "Giant Kelp at Population 3+") but should be treated as bonuses, not dependencies.
- A Tier 3 ecosystem that has received a transplanted Tier 1 organism should behave plausibly — the Tier 1 card's triggers still apply, even if the ecology is strange.

### 9.3 Challenge Deck cross-deck seeding

Control Events may place cards into other location decks as a consequence of player choices. When writing such an Event:

- Name the card that gets placed (e.g. "Megapredator Territory").
- Specify where it goes: "place on top of the next Tier 2 deck drawn" or "shuffle into the current Tier 3 deck."
- The seeded card should be self-explanatory when drawn — players should not need to know its origin to resolve it.
- Seeded cards are always removed after resolution.

---

## 10. Design Checklist

Use this checklist before finalising any new card or deck.

### For every card

- [ ] All required fields are populated or explicitly blank
- [ ] Content face and instruction face are both written
- [ ] Instruction face ends with a stock phrase or explicit `Next:` instruction
- [ ] Unlock cost is stated clearly — resource amounts, or a named trigger condition
- [ ] In-play effect is unambiguous — no "may" without specifying when and how
- [ ] Token track is stated with track name, min, max, and starting value
- [ ] Triggers reference only cards that plausibly co-exist in this location
- [ ] Degradation condition is stated; permanent trash is flagged explicitly
- [ ] Hand version has both Reusable and Trash effects (where applicable)
- [ ] Deck label is in the format `Location Name – N`
- [ ] Notes include any read-aloud text, removal instruction, or Control guidance

### For a complete depth-1 deck

- [ ] Cards 1–2 establish the department narrative and goals
- [ ] Cards 3–7 are Role Cards — five roles, each with public and private face
- [ ] No two Role Cards in the same department share a mechanical function
- [ ] Card 8 is a Phase Reference card, double-sided
- [ ] Cards 9–12 are auto-drawn setup cards (Outpost + starting ecosystem)
- [ ] Opening mechanics (token tracks, outpost rules, dilemma resolution, knowledge cards, exploration gates, crafting) are each tutorialised on the instruction face of the card that first introduces them
- [ ] Tutorial text on instruction faces is in italic
- [ ] All stock phrases used verbatim

### For a complete depth-2+ location deck

- [ ] Card 1 is a Location card with entry requirement, outpost options, and first unlock cost
- [ ] Cards 2–6 (approximately) form a complete opening sequence, each chaining to the next
- [ ] Card 6 or 7 is a sequence-ending Event
- [ ] Opening sequence is completable with base resources only — no icons required
- [ ] At least one Depth Marker per 10–12 cards (approximate)
- [ ] At least one Outpost Blueprint in the early ecosystem
- [ ] At least one Dilemma with genuinely contested options
- [ ] At least one dual-prerequisite unlock (requires two cards at threshold simultaneously)
- [ ] At least one reactor-sensitive card (loses tokens when reactor advances)
- [ ] Final card is a Knowledge card that goes to hand immediately and cannot be trashed
- [ ] Final card has a read-aloud line connecting to the broader narrative
- [ ] All icons provided map correctly to the tier's icon introduction table (Section 6.2)
- [ ] Depth gate requirements match the tier table (Section 5.2)
- [ ] Card type distribution is within range for the tier (Section 3.3)
- [ ] Every ecosystem card has at least one positive and one negative trigger

### For a Challenge Deck card

- [ ] Play condition is explicit and printed on the card
- [ ] All options have distinct mechanical and philosophical costs
- [ ] At least one option plants a cross-deck consequence
- [ ] Signal Events end with "Control notes..." instruction
- [ ] Card type is clearly stated (Intrusion / Cascade / Signal)

### For a Salvage card (Aphelion or Alien)

- [ ] Recipe on instruction face lists all required resources, icons, and keywords
- [ ] Instruction face ends with the crafting stock phrase
- [ ] Content face states item type (`Equipment` or `Outpost Upgrade`) and full effect
- [ ] Copy count (1–6) is determined and justified by scarcity logic
- [ ] Any keyword requirement references a keyword that exists in the location keyword system (Section 3.9)
- [ ] Alien Salvage cards: clearly distinguishable in theme and power from Aphelion equivalents

### For a Proxy Role Card

- [ ] Icon and passive effect match the corresponding full Role Card exactly
- [ ] No reusable effect, trash effect, or private face present
- [ ] Role title and department are clearly readable
- [ ] Updated whenever the corresponding full Role Card changes

### For a Role Card

- [ ] Icon provided is appropriate to the role archetype (Section 4.10)
- [ ] Passive effect is useful on turn 1 with no setup
- [ ] Philosophy is mechanically implied, not stated in the effect text
- [ ] Trash effect is memorable and represents the philosophy's core value
- [ ] No mechanical duplication within the same department
- [ ] Public face and private face are clearly distinct
- [ ] `Do not show this side to other players.` appears in red on the private face

### For a Proxy Role Card

- [ ] Provides only the missing role's icon and passive effect
- [ ] No reusable effect, trash effect, or private face
- [ ] Role identity is visible on the front

---

*This document covers the vertical slice: Reef Garden (Tier 1, Ecology), Crash Flats (Tier 1, Engineering), Kelp Cathedrals (Tier 2), Lantern Drop (Tier 3), and Bone Fields (Tier 4), plus all four auxiliary decks. Requirements for Tier 5 (Abyssal Core), Alien Attunement icons, and remaining department role cards are reserved pending further design.*
