from pathlib import Path
import json,shutil,hashlib,sys
import openpyxl
root=Path(r'C:\AnalogueGames\aphelion-deep');stage=Path(__file__).parent
for src,dest in [('capture-final-v2.json','provenance/workspace-capture.json'),('provider-complete.json','provenance/provider-registry.json'),('earlier-catalogue-readback.json','provenance/earlier-catalogue-readback.json')]:shutil.copy2(stage/src,root/dest)
reg=json.loads((root/'provenance/provider-registry.json').read_text());cap=json.loads((root/'provenance/workspace-capture.json').read_text(encoding='utf8'))
tables=json.loads((root/'provenance/project-tables.json').read_text(encoding='utf8'))
for name,range_ in [('Manifest','Manifest!A1:J17'),('Sources','Sources!A1:L340'),('Gaps','Gaps!A1:E11')]:
 got=cap['spreadsheets'][reg['manifest']['fileId']]['ranges'][range_]
 expected=tables[name]
 assert len(got)==len(expected)
 for a,b in zip(got,expected):assert a+['']*(len(b)-len(a))==b,(name,a,b)
old=json.loads((root/'provenance/earlier-catalogue-readback.json').read_text(encoding='utf8'))['values']
w=openpyxl.load_workbook(root/'archive/source-2/abyssfall_cards.xlsx',read_only=True,data_only=True)
expected=[[v if v is not None else '' for v in r] for r in w['All Cards'].iter_rows(max_row=179,max_col=14,values_only=True)]
for a,b in zip(old,expected):assert [v if v is not None else '' for v in a]+['']*(len(b)-len(a))==b
assert len(old)==179
m=root/'playtrace.toml';s=m.read_text();s=s.replace('capabilities = ',f'drive_manifest_file_id = "{reg["manifest"]["fileId"]}"\ndrive_manifest_range = "Manifest!A1:J17"\ncapabilities = ',1);m.write_text(s,encoding='utf8')
with (root/'.gitignore').open('a') as f:f.write('assets/\n')
(root/'tools').mkdir(exist_ok=True)
for p in stage.glob('*.py'):
 if p.name not in ('engine.py','plugin.py','test_tutorial.py'):shutil.copy2(p,root/'tools'/('initial_'+p.name))
for p in stage.glob('*.mjs'):shutil.copy2(p,root/'tools'/('initial_'+p.name))
docs='\n'.join(f"- [{d['title']}]({d['url']})" for d in reg['documents'].values())
(root/'README.md').write_text(f'''# The Aphelion Deep

Canonical editing takes place in [Google Drive](https://drive.google.com/drive/folders/{reg['root']}). This private repository preserves source provenance, decisions, a verified Workspace capture and the installable PlayTrace tutorial plugin. Original source folders remain untouched.

## Start here

- [Card Catalogue](https://docs.google.com/spreadsheets/d/{reg['cards']}/edit): 46 current rows, both faces, stable IDs, quantities, metadata, source references, full historical pacing and map names.
- [Project Manifest]({reg['manifest']['url']}): canonical source registry, all 339 source dispositions and prioritised gaps.
- [Earlier 178 card catalogue]({reg['earlier_catalogue']['url']}): historical drafts outside the active ruleset.
- [Tutorial replay](reports/tutorial.html), [assessment](design/tutorial-assessment.md), [source selection](design/source-selection.md), [gaps](design/gaps.md).

## Install and replay

Use Python 3.12 or newer. Install PlayTrace with the plugin-state support from its accompanying branch/PR, then this package. From this game repository:

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

## Authority and scope

The v3 printed faces are preserved verbatim. Core Rules records the user-approved amendments: 0–5 card tracks, corrected feeding and Calcite references, explicit Cultivator timing, global upkeep, optional actions, printed crafting costs, card-driven Reactor advancement and restored Cut it free.

`tutorial.json` contains every player-policy choice, including recipients, conversions, upkeep order and declined optional actions. The current strict interpreter covers this tutorial only. It never forces gates, invents unresolved outcomes or injects challenges. Full-colony Command, deeper decks and unselected actions remain design work. Unsupported requests fail with explicit blockers.

## Editing documents

{docs}

## Preservation

`archive/` preserves 63 unique non-art source files. `assets/` contains 44 unique local art files; their Drive destinations or archive members are in `provenance/inventory.json`. Assets are omitted from Git to avoid duplicating the large editable art files. The two map exports and editable Playmat are directly accessible in Drive; remaining editable art and icons are in a hash-verified ZIP. Identical assets share one preserved destination. Excluded vendored tooling and caches are recorded with their original paths and hashes.

The capture contains actual provider IDs, document revision IDs and observed modified times. Native imports were read back and compared with staged content, allowing only added stable paragraph IDs and paragraph-edge whitespace. The manifest itself is also checked by PlayTrace on snapshot creation.
''',encoding='utf8')
(root/'design/design-intent.md').write_text('''# Design intent

Preserve the cooperative survival megagame, six departments, five philosophies, alien ocean ecology, Drowned discovery and five-tier depth progression described in the source material. Consolidation is not a redesign.

The executable slice teaches how persistent decks, local ecosystems and portable capabilities combine across three players and three turns. Success here means completing a faithful tutorial trace, not declaring colony victory or proving full-game balance.
''',encoding='utf8')
(root/'design/decisions').mkdir(exist_ok=True)
(root/'design/decisions/001-authority-and-tutorial.md').write_text('''# Authority and tutorial decisions

Accepted by the user in the implementation plan on 11 October 2026. The v3 card faces govern over conflicting simulator behavior. Core Rules lists every agreed mechanical amendment. No earlier workbook or simulator report silently overrides those amendments.

Cards remain verbatim in the editing catalogue, with stable IDs from components.xlsx. Effects are game-owned Python handlers, bound to the exact canonical card and Core Rules fingerprints in data/bindings.json. The 41 earlier capability definitions are retained in provenance for comparison. Their generic track, gate, icon and feeding interpreter concepts have been ported without a vendored GameSpec dependency.

Script policy: cultivate Filterweed each turn; convert all initial Coral Shelf and Wreckage abundance into Materials in turn 1; feed from the explicitly named legal local sources; use rations at the two shallow outposts and Lungweed at Kelp. Engineer receives the Crash role, tank and database. Lead receives the Reef role, Notes, tank, welder and Pollination; Systems receives its role. Craft the four affordable starter items in turn 1. Decline ecosystem transport, biomass harvesting and Drone repair. These are player decisions, not additional game rules.

Mandatory upkeep uses the listed card order even at sites with no players. The absence of a third Crash recipe leaves Salvage Manifest unclaimed. The earlier automatic gain, crafting, first-choice fallback and gate-assistance behaviors are not retained.

Energy and Power, and Wreck and Wreckage, follow the July capability aliases for this tutorial; the wording discrepancies remain in the gap register. Mineral exhaustion and ecosystem removal follow the preserved card-design reference. No position-based equivalence is asserted between artwork and prose map labels.
''',encoding='utf8')
(root/'design/tutorial-assessment.md').write_text('''# Tutorial assessment

The strict three-player, three-turn script completes. Reef Caverns opens on turn 3 using 4 Oxygen and 2 Knowledge available at the gate. Reactor remains at 1 from Restart; there is no automatic countdown or challenge injection. Crash Engine Core remains unopened because the first visit has insufficient Oxygen, and the script does not return there.

The Engineer carries its role, Oxygen Tank and Scan Database. Lead carries its role, Reef Notes, Oxygen Tank, Field Welder and Pollination. Systems retains its role. Local Crash Power never travels with the Engineer.

At the end, Crash has 13 Materials and 4 Rations; Reef has 2 Materials and 1 Ration; Kelp has 1 Materials and 1 Biomass available for its crafting phase. All revealed locations received upkeep each turn. Reef ends with Filterweed 2, Grazers 3, Glow Polyp 3, Snapper 2 and Calcite Abundance 2. Kelp Lungweed, Lure Fish and Hush Mussels each end at 2. Repeated runs produce identical events and checkpoints.

The major exposed content gap is Salvage Manifest: its three-recipe prerequisite cannot be met by Crash's two current recipes. Its Knowledge is not awarded. Coral and Wreckage are exhausted by the explicitly chosen conversions. Carrier Crabs starve and are later removed; they do not consume Flora. No unsupported outcome or forced gate is needed for the declared route.

This trace is evidence for the tutorial's rules and policy only. See gaps.md for department completion, missing outcomes, map names, quantities, stale references, deeper mechanics and full-colony balancing work.
''',encoding='utf8')
with (root/'design/gaps.md').open('a',encoding='utf8') as f:f.write('\nP1 Salvage Manifest: Crash has two current recipes, but requires three to gain this card. The tutorial does not invent a third recipe.\n')
print('Drive manifest and all 178 historical rows verified; repository documentation written')
