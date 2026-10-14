# The Aphelion Deep

Canonical editing takes place in [Google Drive](https://drive.google.com/drive/folders/1mM3AK6DfZrgYH4auLBugy6NZB9TKBdwo). This public repository preserves source provenance, decisions, a verified Workspace capture and the installable PlayTrace tutorial plugin. Original source folders remain untouched.

## Start here

- [Card Catalogue](https://docs.google.com/spreadsheets/d/1o4X96xXOTL-vQAZq7RghdJBM0fvN2xKH74dnzVRxec4/edit): 46 current rows, both faces, stable IDs, quantities, metadata, source references, full historical pacing and map names.
- [Project Manifest](https://docs.google.com/spreadsheets/d/1Qiex0faSwhdS9gj2lJcBHqkESvZdcLWcZmY-MLMxdOE/edit?usp=drivesdk): canonical source registry, all 339 source dispositions and prioritised gaps.
- [Earlier 178 card catalogue](https://docs.google.com/spreadsheets/d/19XLeUHKHXpm23DYFVk9iQIwO2oRuO1HYZ-itpYn9K-4/edit?usp=drivesdk): historical drafts outside the active ruleset.
- [Tutorial replay](reports/tutorial.html), [assessment](design/tutorial-assessment.md), [source selection](design/source-selection.md), [gaps](design/gaps.md).

## Install and replay

Use Python 3.12 or newer. Install PlayTrace with the plugin-state support from [PlayTrace PR 1](https://github.com/jkeywo/playtrace/pull/1), branch `codex/plugin-simulation-state`, commit `7167e4e43fc231b7863865d0a2655586ddae57fd`, then this package. From this game repository:

```powershell
uv venv
uv pip install --python .venv/Scripts/python.exe -e C:/Coding/playtrace -e ".[dev]"
.venv/Scripts/playtrace.exe snapshot . --fixture provenance/workspace-capture.json --db .playtrace/playtrace.db --output provenance/snapshot.json
.venv/Scripts/playtrace.exe simulate . --fixture provenance/workspace-capture.json --config tutorial.json --db .playtrace/playtrace.db --output provenance/tutorial-run.json
.venv/Scripts/playtrace.exe simulation-report --run provenance/tutorial-run.json --output reports/tutorial.html --card-images reports/cards/manifest.json
.venv/Scripts/python.exe -m pytest
```

On other platforms use the local PlayTrace checkout path and `.venv/bin` executables. The installed game package has no dependency on original source paths, GameSpec, Excel or PyYAML at runtime. Editable installs of both projects resolve the unpublished PlayTrace dependency locally.

For a fresh live capture use `--access-token-env GOOGLE_ACCESS_TOKEN` instead of `--fixture`. Supply credentials through the environment. Changes to bound cards or Core Rules intentionally block simulation until their mappings are reviewed. Do not blindly regenerate bindings. The files in `tools/initial_*` record this one-time migration and its machine-specific source paths; they are not runtime dependencies or a routine sync command.

## Play interactively

Double-click `Start Play.cmd`, or run this from the game workspace:

```powershell
.venv/Scripts/python.exe -m aphelion_deep.play --open
```

The separate player page opens at `http://127.0.0.1:8768/play.html`. It needs the local Python rules server; opening `reports/play.html` directly shows launch instructions. The existing replay remains a standalone read-only report.

The first landing is fixed by department: Fabrication Lead starts at Crash Flats, and Lead Ecologist and Systems Ecologist start together at Reef Gardens. Whole-party expedition assignments begin on turn two. At the start of every Upkeep, assign the whole party again to revealed sites. Drag player tokens between site panels (or use their destination selectors), then confirm once; drafts do not move players or create history entries. The confirmed arrangement is one reversible history action. Choose exploration order, reveals, recipients, cultivation targets, feeding order, conversion amounts, upkeep order and affordable crafting. Assignment and exploration-order boards show the back of each destination’s current top card, using its persistent deck position. Draw a card to read the back. Ordinary cards can then flip to the front; conditional cards are placed beside the deck with their backs up and remain there until their printed condition and phase allow activation. Salvage Manifest requires three Aphelion Salvage recipes, not three Materials. Crash Flats currently has only two recipes in the imported slice, so the Manifest remains locked unless that requirement is actually met. The Sunken Survey Drone can be activated for 2 local Materials during the optional Upkeep window, starting at Scanning 4; subsequent upkeep advances Scanning. Reading steps and card actions are saved history points; ordinary card effects wait until you continue from the front, while deferred cards wait for their specific activation action. Rewinding restores those previews too. The table keeps one selected location and one selected player’s hand visible together. Click the top deck card to draw; click cards in play, beside the deck, or in hand to inspect and use available actions. Colocated players share usable card actions and icons without transferring ownership; Cultivator remains once per turn across the party. Switch either the location or hand independently. This is local shared-table control of the three tutorial characters, not network multiplayer. It supports the reviewed three-turn slice; unfinished dilemma outcomes and optional effects are labelled unavailable. Gates, mandatory upkeep and payment restrictions still apply.

Every decision automatically saves to `.playtrace/player-session.json`. Click any history point to restore its exact continuation; choosing again adds a branch without deleting the old future. Back selects the parent decision; Start selects the original setup. History points are player decisions, with automatic effects shown beneath each step. Reopening the launcher resumes the selected point, including all branches. Save files are deliberately excluded from Git.

Export downloads the complete history tree. To reopen an exported history, use `--session C:/path/to/aphelion-expedition.json`. Use a different, new `--session` path for a separate expedition. The server binds only to this computer. Closing its console stops it; saved decisions remain on disk. A second launcher cannot take over an already running server, so use its existing browser page or stop that console first.

The interactive controller replays explicit decisions through the same Python effects as the strict tutorial. Its history is bound to the source snapshot and executable engine fingerprints; changed rules reject incompatible saves rather than silently reinterpret them. Tests compare the entire three-turn final state with the scripted tutorial and cover branching, restart recovery, once-per-turn restoration, stale choices and HTTP action validation.

Hold **Alt** while hovering over any card image to see that face at full size, fitted to the window. Release Alt or move away to close the preview. Alt-clicking only inspects; it never takes an action.

Taking a role card puts it directly into the matching player's hand: Fabrication Lead, Lead Ecologist, or Systems Ecologist. The visible hand switches to its owner so the result is visible immediately. Other cards retain their recipient choices.

Phase Reference stays in play at its location once used. Its back shows Exploration and its front shows Upkeep; it flips automatically at each phase change, including when returning to earlier history. Reference cards do not require an upkeep action.

Dilemma cards show their choices and consequences together. The Power Question offers Restart, Strip for parts (restore Aphelion Wreckage Field to 5 Abundance, as clarified on 12 October 2026), and Seal it away (no immediate effect; a local note records the decision for Control). Spawning Ground offers Harvest (1 local Food), Protect (+2 Population to both named cards), and Tag & Monitor (1 local Knowledge). Harvest and Tag & Monitor remain tucked under Reef Garden Outpost; their icons stay at that location. The two unfinished Echoing Drowned Mass alternatives remain visible as “???” and unavailable. The scripted tutorial retains its original chosen route.

Eligible set-aside Knowledge cards, including Salvage Manifest, ask which player at the site takes them into hand. Salvage Manifest retains its printed requirement of three local Aphelion Salvage recipes; the two current Crash Flats recipes do not satisfy it. While choosing actions in Exploration or Upkeep, use **Give to…** on a non-role card in the selected player's hand to transfer it to another player at that location. Trades retain card identity and capabilities, appear in history, and can be rewound or branched. Role cards cannot be traded.

## Multiplayer with PeerJS

Remote players can join at **https://jkeywo.github.io/aphelion-deep/**. Start a room locally, then use **Copy invitation link** to send a link with the room code filled in. The code is carried in the URL fragment, not sent to the Pages server. Guests choose a name and role before joining. The local host and Python rules server must stay open: GitHub Pages serves the guest interface only.

The repository deploys the public guest page automatically using `.github/workflows/pages.yml`. The website publishes only the generated guest HTML and PeerJS license; game source documents, card artwork, saves and facilitator content are not included in the website artifact. Card images arrive from the host after a player joins. Run `python tools/build_pages.py` to reproduce the deployment artifact.

Run **Start Multiplayer.cmd**, or `.venv/Scripts/python.exe -m aphelion_deep.multiplayer --open`, on the host computer. Open `http://127.0.0.1:8770/multiplayer.html`, click **Create room**, and send the displayed room code and **Download guest HTML** file to the other players. The same standalone file is saved as `reports/aphelion-multiplayer.html`. Guests open that file in a modern browser, enter their name and room code, and claim a role. Guests need no Python installation or game files. Three people each control one character; the host can be one of them or facilitate with all three seats remote.

Keep the host page and rules server running throughout play. PeerJS 1.5.5 is bundled locally, with its MIT license. Its default public signaling service needs internet access; game messages and card images travel over WebRTC data channels. Different computers and networks are supported, but restrictive firewalls/NAT may need your own TURN relay in **Connection settings**. That field accepts PeerJS options, including `config.iceServers` and custom PeerServer settings. No TURN credentials are supplied and no hosted relay is provisioned. Python listens only on the host computer, so guests do not use the host's localhost URL or expose its rules server to the internet.

All three seats must be connected to act. Each player chooses only their own destination; all three destinations apply together as one history action. Location order, finishing crafting and completing a turn require all three players to agree. Dilemmas require agreement from everyone present. Other site actions are available to people at that site; personal feeding and crafting decisions belong to the relevant player. Mandatory upkeep at an unoccupied site can be resolved by any player. These are multiplayer control policies, not changes to printed card effects.

Each player has one location and their own hand visible. Colocated cards remain usable together; only their owner can give a non-role card to another player there. Other players see role-card backs. The host validates every decision, image request and history revision. Drawing, flipping, dilemma consequences, phase references, deferred requirements and Alt-hover previews follow the existing interface. All unfinished effects remain explicit blockers.

Decisions save automatically to `.playtrace/multiplayer-session.json`, separate from local play. The host can select any history point and resume from it; former branches remain saved and pending votes/destinations are cleared. **Export history** downloads the complete tree. Reopen an export with `--session C:/path/to/history.json`; use a new path for a separate game. Disconnecting reserves a player's seat. Reopen the same guest file/browser, use the same room code and role, and click **Join as this player** to recover it. The host can release a reserved seat when necessary. Restarting or reloading the host creates a new room code: reconnect everyone to that room and reclaim roles; saved decisions survive, pending votes do not. There is no automatic host migration.

Tests play the full three-turn tutorial through three independently authorized seats, including atomic assignments, unanimous decisions, stale requests after rewind, disconnect/reconnect, trading, private role images and saved-game reload. The game remains the reviewed three-player slice, not the unfinished full-colony game.

Rebuild the standalone guest file after editing the interface with `.venv/Scripts/python.exe tools/build_multiplayer_guest.py`. The HTTP download is checked against that generated file in the test suite. Browser QA verified three PeerJS-connected seats, synchronized votes and card images, and guest reconnection on one computer; cross-network TURN traversal and opening the downloaded file on another physical computer still need a real remote-player check.

## Reading the replay

Open `reports/tutorial.html` in a browser, or download the [Drive copy](https://drive.google.com/file/d/1oK5hNP6hsca6R9dtJBXQcCLCxNNNk5Xl/view). Each action has a plain-language description. Choose a player or location tab to inspect its state after that action; gold badges identify every affected tab and highlighted fields show before/after values. Use Previous, Next, the slider or the action history to move through the trace. Highlights always compare adjacent actions, even when jumping through the history.

The action gallery includes directly referenced cards and cards changed indirectly, including feeding targets and removed cards. Select Front or Back, click a card to enlarge it, or use the full-size download link. All 92 images are embedded in the report so the downloaded Drive copy works offline. These are clearly labelled reference renders of the 46 consolidated source cards, using existing location artwork; they preserve printed text, with tutorial amendments applied separately.

To rebuild the reference images, install `.[render]` and run `.venv/Scripts/python.exe tools/render_cards.py`, then regenerate the report with `--card-images reports/cards/manifest.json`. Rendering requires the preserved `assets/source-2/Art` files. Arial is the default font; set `APHELION_FONT` and `APHELION_FONT_BOLD` to explicit font files on other platforms. The manifest binds each face to its text and image fingerprints and to the tutorial source snapshot.

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
