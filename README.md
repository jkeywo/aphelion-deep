# The Aphelion Deep

Canonical editing takes place in [Google Drive](https://drive.google.com/drive/folders/1mM3AK6DfZrgYH4auLBugy6NZB9TKBdwo). This private repository preserves source provenance, decisions, a verified Workspace capture and the installable PlayTrace tutorial plugin. Original source folders remain untouched.

## Start here

- [Card Catalogue](https://docs.google.com/spreadsheets/d/1o4X96xXOTL-vQAZq7RghdJBM0fvN2xKH74dnzVRxec4/edit): 46 current rows, both faces, stable IDs, quantities, metadata, source references, full historical pacing and map names.
- [Project Manifest](https://docs.google.com/spreadsheets/d/1Qiex0faSwhdS9gj2lJcBHqkESvZdcLWcZmY-MLMxdOE/edit?usp=drivesdk): canonical source registry, all 339 source dispositions and prioritised gaps.
- [Earlier 178 card catalogue](https://docs.google.com/spreadsheets/d/19XLeUHKHXpm23DYFVk9iQIwO2oRuO1HYZ-itpYn9K-4/edit?usp=drivesdk): historical drafts outside the active ruleset.
- [Tutorial replay](reports/tutorial.html), [assessment](design/tutorial-assessment.md), [source selection](design/source-selection.md), [gaps](design/gaps.md).

## Install and replay

Use Python 3.12 or newer. Install PlayTrace with the plugin-state support from [PlayTrace PR 1](https://github.com/jkeywo/playtrace/pull/1), branch `codex/plugin-simulation-state`, commit `9b3288af94bcaa5802bb28b60caa33f007424973`, then this package. From this game repository:

```powershell
uv venv
uv pip install --python .venv/Scripts/python.exe -e C:/Coding/playtrace -e ".[dev]"
.venv/Scripts/playtrace.exe snapshot . --fixture provenance/workspace-capture.json --db .playtrace/playtrace.db --output provenance/snapshot.json
.venv/Scripts/playtrace.exe simulate . --fixture provenance/workspace-capture.json --config tutorial.json --db .playtrace/playtrace.db --output provenance/tutorial-run.json
.venv/Scripts/playtrace.exe simulation-report --run provenance/tutorial-run.json --output reports/tutorial.html
.venv/Scripts/python.exe -m pytest
```

On other platforms use the local PlayTrace checkout path and `.venv/bin` executables. The installed game package has no dependency on original source paths, GameSpec, Excel or PyYAML at runtime. Editable installs of both projects resolve the unpublished PlayTrace dependency locally.

For a fresh live capture use `--access-token-env GOOGLE_ACCESS_TOKEN` instead of `--fixture`. Supply credentials through the environment. Changes to bound cards or Core Rules intentionally block simulation until their mappings are reviewed. Do not blindly regenerate bindings. The files in `tools/initial_*` record this one-time migration and its machine-specific source paths; they are not runtime dependencies or a routine sync command.

## Reading the replay

Open `reports/tutorial.html` in a browser, or download the [Drive copy](https://drive.google.com/file/d/1oK5hNP6hsca6R9dtJBXQcCLCxNNNk5Xl/view). Each action has a plain-language description. Choose a player or location tab to inspect its state after that action; gold badges identify every affected tab and highlighted fields show before/after values. Use Previous, Next, the slider or the action history to move through the trace. Highlights always compare adjacent actions, even when jumping through the history.

Location tabs show resources, capabilities, players present and cards in play. Expand the deck section for ordered cards, the next card, recipes and piles. Technical details retain exact checkpoints and source references. Presentation text is owned by `src/aphelion_deep/presentation.py`; it never applies game effects.

## Authority and scope

The v3 printed faces are preserved verbatim. Core Rules records the user-approved amendments: 0–5 card tracks, corrected feeding and Calcite references, explicit Cultivator timing, global upkeep, optional actions, printed crafting costs, card-driven Reactor advancement and restored Cut it free.

`tutorial.json` contains every player-policy choice, including recipients, conversions, upkeep order and declined optional actions. The current strict interpreter covers this tutorial only. It never forces gates, invents unresolved outcomes or injects challenges. Full-colony Command, deeper decks and unselected actions remain design work. Unsupported requests fail with explicit blockers.

## Editing documents

- [The Aphelion Deep Overview](https://docs.google.com/document/d/1A_8GxEFiVcre4EyWqR4vQG3_pHd3oiQojCTFv_cVNl4/edit?usp=drivesdk)
- [The Aphelion Deep Core Rules](https://docs.google.com/document/d/11Ybx_vdKQzybtNP8omCdH1oA1ASrhMZ1BWdKqywp1nE/edit?usp=drivesdk)
- [The Aphelion Deep Departments](https://docs.google.com/document/d/1izCPb-W03rSOQZVvFOc6Cl311SBQh5YOtOEAnDz8NSI/edit?usp=drivesdk)
- [The Aphelion Deep Engineering Briefs](https://docs.google.com/document/d/1Ja4RZRTiWKD17hLgChLKZWOBVsanMsgynxDMfzlIvQM/edit?usp=drivesdk)
- [The Aphelion Deep Ecology Briefs](https://docs.google.com/document/d/16CLBWcBSEMz4LgXzFnYL924LsYlc9U2NjMMxiWVRadw/edit?usp=drivesdk)
- [The Aphelion Deep Medical Briefs](https://docs.google.com/document/d/1EwSrbfg93HLi4rsEAH3uGlhMDDUn1Q9ISxMoNTODWT8/edit?usp=drivesdk)
- [The Aphelion Deep Philosophies](https://docs.google.com/document/d/1RoEC8Ktm4hdHyAT-z9xjgkE8-1uYsAe2nXSsFkoTaOE/edit?usp=drivesdk)
- [The Aphelion Deep Locations](https://docs.google.com/document/d/1gCMO_uUkQIe6nr9FnJZkrn4jxoK_vVbqzk1tqRGbsVo/edit?usp=drivesdk)
- [The Aphelion Deep Player Lore](https://docs.google.com/document/d/1XvteBEgiqW3S50i7cNX-swaYWP4kduHOX8Uelvc_hKQ/edit?usp=drivesdk)
- [The Aphelion Deep Facilitator Lore](https://docs.google.com/document/d/1scEyod5y4H1CKZsseru6hGezecz9MJK9NCv47PDye4M/edit?usp=drivesdk)
- [The Aphelion Deep Facilitator Guidance](https://docs.google.com/document/d/1P9hhTNPieNIc6Twqs0GHqByBzEPUfjTzGYkLMLcPSjM/edit?usp=drivesdk)
- [The Aphelion Deep Card Design Reference](https://docs.google.com/document/d/1gIJlk_cpoqx-qVMY61b_xdd2ZjYsGrUHv3hon-pUUmw/edit?usp=drivesdk)
- [The Aphelion Deep Sensory Vocabulary](https://docs.google.com/document/d/1MY5TGuPMeD9sJn0Q7xuZJ7jymdLlZSNaGC8aOY6C8Ok/edit?usp=drivesdk)
- [The Aphelion Deep Deeper Knowledge Drafts](https://docs.google.com/document/d/1RpMBiY0UO6NvjtIU9-N7jB8bj-jpozN7b_g2QB45mGY/edit?usp=drivesdk)
- [The Aphelion Deep Structured Design Annex](https://docs.google.com/document/d/13aMqvCqVN7QB-ZIG5SevdgPp9LJl9ugfjHetwps7V_E/edit?usp=drivesdk)

## Preservation

`archive/` preserves 63 unique non-art source files. `assets/` contains 44 unique local art files; their Drive destinations or archive members are in `provenance/inventory.json`. Assets are omitted from Git to avoid duplicating the large editable art files. The two map exports and editable Playmat are directly accessible in Drive; remaining editable art and icons are in a hash-verified ZIP. Identical assets share one preserved destination. Excluded vendored tooling and caches are recorded with their original paths and hashes.

The capture contains actual provider IDs, document revision IDs and observed modified times. Native imports were read back and compared with staged content, allowing only added stable paragraph IDs and paragraph-edge whitespace. The manifest itself is also checked by PlayTrace on snapshot creation.
