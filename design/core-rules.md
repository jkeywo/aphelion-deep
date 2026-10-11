# The Aphelion Deep Core Rules

Consolidated from the supplied Aphelion Deep design sources. Working design; unresolved passages retain their original status. The tutorial amendments in Core Rules govern the declared three turn slice.

[PT-ID:ad-tutorial-rules] [WORKING] The tutorial is three players over three turns, with Exploration followed by Upkeep. Ordered location decks persist. Full colony Command, automatic reactor escalation and challenge injection are outside this tutorial.

[PT-ID:ad-source-authority] [WORKING] Unambiguous v3 printed card text overrides simulator behavior. The following agreed amendments are authoritative for the tutorial.

[PT-ID:ad-track-limits] [WORKING] Reef rations starts at 5. All card tracks use the artwork endpoints 0 and 5. Other setup values follow printed cards. Reactor starts at 0 and advances only through card effects; its actual value supplies Reactor thresholds.

[PT-ID:ad-cultivator] [WORKING] Cultivator is optional, once per turn during Exploration, targeting one explicitly selected Flora.

[PT-ID:ad-feeding] [WORKING] Spotted Grazers consume Flora. Carrier Crabs consume other Fauna. Full feeding payment is required before any population is consumed; otherwise apply starvation. Calcite Spires Population references mean Abundance.

[PT-ID:ad-upkeep] [WORKING] Resolve every revealed location once per turn, even if unoccupied. Only present players eat or craft. Optional crafting, harvesting and taking ecosystem cards into hand occur at most once per stated phase unless otherwise specified. Mandatory upkeep still resolves.

[PT-ID:ad-crafting] [WORKING] Use printed crafting costs. Fabricator discounts one chosen resource by one, with a zero floor. Salvage Manifest Knowledge applies only to crafting Aphelion Salvage items, never expedition gates.

[PT-ID:ad-cut-free] [WORKING] Cut it free gives Giant Lungweed Stalks 2 Population and the location 1 Materials, then removes the dilemma. Recover it and Document and leave remain unresolved.

[PT-ID:ad-route] [WORKING] Turn 1 Fabrication Lead visits Crash Flats and both Ecologists visit Reef Gardens; choose Restart and Protect. Turn 2 Fabrication Lead and Lead Ecologist visit Kelp Cathedral; Systems Ecologist stays at Reef. Choose Cut it free. Turn 3 all three regroup at Reef and attempt Reef Caverns with their actual accumulated capabilities. Missing choices and unsupported actions block execution; gates are never forced.

## Full colony design outside the tutorial

## Turn Structure

The game uses a shared mechanical core built around expeditions, outposts, and upkeep.

### 1. Expedition Phase
This is the majority of the turn.

Players arrange themselves into expedition groups and choose where to go. Expeditions may target known locations or attempt to discover new ones.

Expeditions can:
- Explore new terrain
- Find resources
- Reveal outpost locations
- Trigger encounters and hazards
- Discover information, blueprints, or alien systems

Expeditions should have limits:
- Capacity limits
- Equipment limits
- Oxygen or endurance limits
- Risk scaling with depth

This phase is the main driver of discovery and map growth.

### 2. Assignment Phase
Players then select which outpost they will remain at for the turn while upkeep happens.

At this stage:
- Players choose an outpost
- Outposts have limited capacity
- Teams are physically located at specific sites
- Some outposts are better for certain departments or philosophies

### 3. Upkeep and Production Phase
This is resolved simultaneously.

During upkeep:
- Players consume resources at the same time
- Outposts perform exactly one action per turn
- Systems process production, recycling, repair, or special effects
- Reactor pressure advances
- Events may trigger

This creates a strict shared timing structure and forces hard decisions.

---


## Outpost System

Outposts are the main strategic structure in the game.

Outposts:
- Can be built and upgraded once per turn
- Have capacity limits
- Have module slots
- Have a base trait tied to their location
- Are the place where long-term progress happens

Players must choose where they are physically stationed during upkeep.

### Starting Outposts
Each department begins with one ship-fragment outpost.

Suggested starting fragments:
- Command: Bridge Fragment
- Engineering: Engine Core Section
- Exploration: Sensor Mast
- Ecology: Hydroponics Bay
- Medical: Life Support Section
- Corporate: Data Core

These should bias the department mechanically, not just narratively.

### Outpost Functions
Outposts can:
- Produce resources
- Process resources
- Host players
- Provide special abilities
- Stabilize systems
- Support expeditions
- Interact with reactor or alien systems

### Outpost Growth
Players can:
- Build new outposts on discovered sites
- Upgrade existing outposts
- Specialize outposts toward a strategic role

---


## Depth and Outpost Scaling

Deeper outposts should become:
- stranger
- more powerful
- harder to use
- more conditional
- more risky

### Shallow Outposts
- Stable
- Predictable
- Easy to maintain
- Low output
- Good for early permaculture

### Mid-Depth Outposts
- More specialized
- Moderate risk
- Higher output
- Some instability or required inputs

### Deep / Abyssal Outposts
- Very powerful
- Strange and conditional
- Difficult to staff or sustain
- May alter local rules
- May interact with alien systems
- May require continuous attention

Deep outposts should not just produce more. They should introduce unusual rules.

---


## Permaculture and Closed Economy

The economy should be closed. Players do not receive new resources from outside the system.

### Core Principles
- Resources must be extracted, processed, recycled, or sustained locally
- Overharvesting should reduce future yield
- Good systems should be harder to bootstrap but better in the long run
- Waste should be a major strategic problem

### Suggested Resource Loops
- Food
- Water
- Oxygen
- Biomass
- Soil analogues
- Power
- Materials
- Knowledge

### Suggested System Properties
- Resource conversion chains
- Recycling and waste recovery
- Biodiversity bonuses
- Efficiency gains from integrated systems
- Stress and degradation from overuse

Permaculture should be a mechanically meaningful path, not only a theme.

---


## Reactor Clock

The reactor is the central endgame pressure.

The reactor has sunk deep underwater and will eventually go critical if not addressed.

### Reactor Phases
1. Dormant leak
2. Instability
3. Critical cascade
4. Meltdown or resolution

### Advancement and Slowdown

The reactor track advances automatically by one step each turn during Upkeep. It does not require anyone to do anything reckless — inaction is sufficient to doom the group. Reckless actions (deep disturbance, Drowned tech use, uncontained outpost construction near the reactor site) may advance it by additional steps.

The track can be slowed — but not reversed — by controlling specific outposts. Generic resource expenditure is not enough. The right infrastructure in the right location is required. This means the question of who controls reactor-relevant outposts is a genuine power question, not just a logistics one.

**Milestone damage is permanent.** Once a phase transition fires, its effect does not go away even if the reactor is later slowed. Players can only prevent the *next* milestone from firing; they cannot undo what has already happened. The only full resolution is a final endgame action.

### Milestone Effects

Each phase transition triggers an immediate, permanent map-wide effect. Different departments feel each milestone at different moments, which staggers the urgency rather than hitting everyone at once.

**Phase 1 → 2 (Dormant to Unstable)**
*The ecosystem layer feels it first.*
- All Tier 1 Mineral cards lose 1 Integrity immediately.
- Radiation tokens are placed on the two deepest currently-explored locations. These tokens remain and accumulate.
- The shallow megafauna stirs: place a Territory token at the Crash Flats.
- Ecology and Medical departments feel this immediately. Others may not notice yet.

**Phase 2 → 3 (Unstable to Critical)**
*The outpost layer feels it.*
- One Tier 2 or Tier 3 location deck gains a Cascade Event card, shuffled in now.
- All Fauna cards at Tier 3 and below lose 1 Population immediately.
- The mid-depth megafauna activates: place it on the map and begin its migration pattern.
- Engineering and Exploration feel this immediately. The reactor access window is visibly closing.

**Phase 3 → 4 (Critical to Cascade)**
*The map layer feels it.*
- The deepest currently-occupied outpost becomes unstable. Players must evacuate it or pay heavy upkeep each turn to hold it.
- The deep megafauna activates and moves to block reactor site access.
- A second Cascade Event card is injected into a Tier 4 location deck.
- The endgame is now mandatory. Everyone feels it.

### Outposts That Can Slow the Reactor

Slowing the reactor requires controlling outposts with specific capabilities. No single department owns all of them — requiring cross-philosophy cooperation to maintain the slowdown.

- **Engineering outpost at the Engine Core Section (upgraded):** Can hold Phase 1→2 for one additional turn per upgrade level.
- **Ecology biological filter outpost (mid-depth):** Reduces radiation token accumulation; can slow Phase 2→3 by one turn if at full capacity.
- **Deep Engineering containment outpost (Tier 3+):** Required to slow Phase 3→4. Cannot be built without Structural Engineer involvement and significant Materials.

Mitigating a late-phase transition will typically require a combination of outpost types controlled by players from opposing philosophy blocs — which is the point.

### Possible Responses
- Repair
- Contain
- Evacuate
- Abandon
- Transform the system through alien means (including Drowned technology — with consequences)

The reactor should not just be a countdown. It should reshape the map and the available options.

---


## Event System

Events should keep pressure on the game and force adaptation.

Examples:
- Fauna migration or aggression spikes
- Ecosystem collapse
- Radiation surges
- Equipment failures
- Flooding or pressure breaches
- Alien signals or structural activation

Events should:
- Interrupt stable plans
- Reward resilient systems
- Push players into negotiation
- Expose philosophical differences

---


## Negotiation and Command Authority

### Deals

All deals in Abyssfall are verbal and unenforceable. There are no formal trade cards, no mechanical enforcement, no penalty printed on a card for betrayal. Reputation is the only currency of trust, and it accumulates — or depletes — through play.

This means:
- Resource trades are fast and informal. Betrayal is possible and interesting.
- Outpost access promises, philosophy commitments, and expedition arrangements are also verbal. Breaking them has social consequences, not mechanical ones.
- Players who build reputations for reliability accumulate real influence. Players who betray deals become known for it.

Control does not arbitrate deals. They observe them.

### Command's Role

Command begins the game with the best overview of what every department can do and what the overall situation requires. They are the natural brokers — not because they have authority to compel, but because they have information everyone else needs and a structural incentive to coordinate the group.

**Command's primary leverage tool is the Bounty Hand.**

At game start, each Command player receives a hand of Bounty cards. These are equipment upgrades, outpost modules, and capability cards — items already in the card economy, representing real mechanical value. Command can offer them as prizes for achievements they want to incentivise: reaching a specific location, completing a resource chain, delivering a report, staffing a critical outpost.

**Bounty card rules:**
- Command receives their full hand at game start. There is no replenishment.
- Bounties are offered publicly or privately — Command's choice.
- The first player or team to complete the stated achievement claims the card.
- Command must spend their bounties wisely. They will run out before the game ends, and the late game is when their leverage is most needed.

This creates a natural power arc: early Command is flush and influential, directing activity across the board. Late Command is scraping for leverage just as the reactor and Drowned crises peak. The group's ability to coordinate in the endgame depends partly on whether Command spent their bounties well.

### Philosophy Blocs as Negotiating Parties

As the game develops, hidden philosophies become open secrets. Players stop pretending and start negotiating as blocs. The late game is not primarily a logistics problem — it is a political one.

The reactor milestone responses require specific outpost types controlled by specific players. Whoever controls those outposts has leverage over the whole group's survival options. Philosophy blocs that have been building quietly since turn one now reveal what they have constructed — and what they want in exchange for using it.

The most interesting late-game deals are not about resources. They are about the shape of the ending.

---
