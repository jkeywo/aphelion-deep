# The Aphelion Deep - Source Import Audit

This audit records material found in `C:\AnalogueGames\TheAphelionDeep` that was not fully
represented in the converted GameSpec project.

## Imported Now

- `abyssfall_cards_v3.xlsx`: imported into `source/components/components.xlsx`.
  - `Cards` tab: 46 card definitions.
  - `Collections` tab: 7 deck/collection definitions.
  - `Turn Pacing` tab: preserved as source pacing reference.
- `abyssfall_cards_v3.xlsx` playtest deck structure is represented in
  `source/game/cards.gamespec.md`.

## Indexed For Follow-Up Conversion

The following source documents are indexed in `source/components/components.xlsx` on the
`Source Documents` tab with their original paths and heading outlines:

- `abyssfall_card_design.md`
- `abyssfall_drowned_brief.md`
- `abyssfall_ecology_briefs.md`
- `abyssfall_engineering_briefs.md`
- `abyssfall_medical_briefs.md`
- `abyssfall_sensory_vocabulary.md`
- `abyssfall_tier4_knowledge_cards.md`
- `megagame_design_outline.md`
- `AGENTS.md`

## Still Needs Real Conversion

- Department role briefs should become `briefing:` entries and/or `Role Briefs`
  component rows, not just indexed source references.
- Tier 4 knowledge cards should be converted into the card catalogue once the main
  playtest deck import is reviewed.
- The card design requirements should be folded into validation/audit notes for the
  Aphelion card system.
- The Drowned brief and sensory vocabulary belong mainly in the Abyssfall WorldSpec
  dependency, with game-facing hooks back into The Aphelion Deep where they drive
  objectives, milestones, or cards.
