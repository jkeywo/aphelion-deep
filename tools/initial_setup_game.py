from pathlib import Path
import json,shutil,re,yaml
root=Path(r'C:\AnalogueGames\aphelion-deep');stage=Path(__file__).parent
def save(path,obj):
 p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
def text(path,s):
 p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
text('src/aphelion_deep/__init__.py','__version__ = "0.1.0"\n')
shutil.copy2(stage/'engine.py',root/'src/aphelion_deep/engine.py')
text('pyproject.toml','''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "aphelion-deep"
version = "0.1.0"
description = "The Aphelion Deep PlayTrace tutorial plugin"
requires-python = ">=3.12"
dependencies = ["playtrace>=0.1.0"]
[project.optional-dependencies]
dev = ["pytest>=8.3,<10", "PyYAML>=6", "openpyxl>=3.1"]
[project.entry-points."playtrace.simulation_plugins"]
aphelion_deep = "aphelion_deep.plugin:AphelionPlugin"
[tool.hatch.build.targets.wheel]
packages = ["src/aphelion_deep"]
[tool.pytest.ini_options]
testpaths = ["tests"]
''')
turns=[
 {'assignments':{'engineer':'C','lead':'R','systems':'R'},'exploration_order':['C','R'],'upkeep_order':{'C':['C9','C10','C11','C12'],'R':['R9','R10','R11','R12']},'crafts':[['Cs1','engineer'],['Cs3','engineer'],['Rs1','lead'],['Rs2','lead']],'optional_actions':{'R13':'decline','R11:harvest':'decline'}},
 {'assignments':{'engineer':'K','lead':'K','systems':'R'},'exploration_order':['K','R'],'upkeep_order':{'C':['C9','C10','C11'],'R':['R9','R10','R11'],'K':['K1','K2','K3','K4']},'crafts':[],'optional_actions':{'R13':'decline','R11:harvest':'decline','K5':'decline'}},
 {'assignments':{'engineer':'R','lead':'R','systems':'R'},'exploration_order':['R'],'upkeep_order':{'C':['C9','C10'],'R':['R9','R10','R11','R16','R17','R18','R20'],'K':['K1','K2','K3','K4']},'crafts':[],'optional_actions':{'R13':'decline','R21':'decline','R11:harvest':'decline','K5':'decline'}}]
choices={'1:recipient:C3':'engineer','1:recipient:R3':'lead','1:recipient:R4':'systems','1:recipient:R13':'lead','3:recipient:R21':'lead','1:dilemma:C14':'Restart','1:dilemma:R14':'Protect','2:dilemma:K8':'Cut it free','1:convert:C12':{'Materials':5},'1:convert:R12':{'Materials':4},'1:feed:C11':[],'3:feed:R17':['R11']}
for n in (1,2,3):
 choices[f'{n}:cultivate']='R10';choices[f'{n}:feed:R11']=['R10']
 for p in ('engineer','lead','systems'):choices[f'{n}:eat:{p}']='C9' if n==1 and p=='engineer' else 'K2' if n==2 and p!='systems' else 'R9'
save('tutorial.json',{'id':'aphelion-tutorial-v1','scenario_id':'tutorial-three-turns','ruleset_id':'aphelion-tutorial-v1','character_ids':['engineer','lead','systems'],'seed':0,'max_turns':3,'player_policy':'plugin_scripted','strict_semantics':True,'plugin_config':{'turns':turns,'choices':choices}})
effects={}
for p in (root/'archive/source-1/source/game').glob('*_cards.gamespec.md'):
 for block in re.findall(r'```yaml\s*\n(.*?)```',p.read_text(encoding='utf8'),re.S):
  loader=yaml.SafeLoader(block)
  try:
   node=loader.get_single_node()
   for kn,vn in node.value:
    if loader.construct_object(kn,deep=True)=='card_effects':
     obj=loader.construct_object(vn,deep=True);effects[obj['id']]=obj
  finally:loader.dispose()
save('provenance/legacy-capability-definitions.json',effects)
shutil.copy2(stage/'provider-registry-v3.json',root/'provenance/provider-registry.json')
shutil.copy2(stage/'capture.json',root/'provenance/workspace-capture.json')
reg=json.loads((root/'provenance/provider-registry.json').read_text())
manifest=f'''manifest_version = 1
project_id = "aphelion-deep"
name = "The Aphelion Deep"
repository = "."
drive_folder_id = "{reg['root']}"
capabilities = ["cards", "simulation"]
'''
for slug,d in reg['documents'].items():
 manifest+=f'''\n[[sources]]
id = "ad:{slug}"
file_id = "{d['fileId']}"
kind = "google_doc"
role = "{'tutorial_rules' if slug=='core-rules' else 'design_reference'}"
title = "{d['title']}"
schema_id = "aphelion-document-v1"
'''
manifest+=f'''\n[[sources]]
id = "ad:cards"
file_id = "{reg['cards']}"
kind = "google_sheet"
role = "card_catalogue"
title = "The Aphelion Deep Card Catalogue"
schema_id = "aphelion-cards-v1"
'''
for sheet,range_,kind in [('Cards','Cards!A1:X47','card'),('Pacing','Pacing!A1:D6','historical_pacing'),('Map Names',"'Map Names'!A1:E41",'location_name')]:
 manifest+=f'''\n[[sources.tables]]
sheet = "{sheet}"
range = "{range_}"
entity_kind = "{kind}"
entity_id_column = "ID"
'''
text('playtrace.toml',manifest)
print('Game package scaffold, tutorial and manifests created; legacy definitions:',len(effects))
