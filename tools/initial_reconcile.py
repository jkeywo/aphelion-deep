from pathlib import Path
import json,tomllib,hashlib,zipfile,shutil
root=Path(r'C:\AnalogueGames\aphelion-deep');stage=Path(__file__).parent
reg=json.loads((stage/'provider-final.json').read_text(encoding='utf8'))
items=json.loads((root/'provenance/inventory.json').read_text(encoding='utf8'))
derived={
 'megagame_design_outline.md':['overview','core-rules','departments','philosophies','locations','facilitator-lore','facilitator-guide'],
 'abyssfall_engineering_briefs.md':['engineering-briefs'],'abyssfall_ecology_briefs.md':['ecology-briefs'],'abyssfall_medical_briefs.md':['medical-briefs'],
 'abyssfall_drowned_brief.md':['player-lore','facilitator-lore'],'abyssfall_sensory_vocabulary.md':['sensory-vocabulary'],'abyssfall_card_design.md':['card-design'],'abyssfall_tier4_knowledge_cards.md':['deeper-knowledge']}
for i in items:
 dest=i['destination'];i['canonical_links']=[]
 if dest:
  assert hashlib.sha256((root/dest).read_bytes()).hexdigest()==i['sha256']
  if dest.startswith('assets/'):
   d=reg['assets'].get(i['sha256'],reg['art_archive'])
  else:d=reg['earlier_archive']
  i['drive_file_id']=d['id'];i['drive_url']=d['url'];i['archive_member']=dest if i['sha256'] not in reg['assets'] else None
  if Path(i['original_path']).name in derived:
   i['canonical_links']=[reg['documents'][s]['url'] for s in derived[Path(i['original_path']).name]]
  if i['relative_path']=='source/components/components.xlsx' or Path(i['original_path']).name=='abyssfall_cards_v3.xlsx':i['canonical_links']=[f"https://docs.google.com/spreadsheets/d/{reg['cards']}/edit"]
  if i['canonical_links'] and i['disposition']=='archived':i['disposition']='imported';i['reason']='Native editing copy verified against staged content; original bytes also archived'
for name in ['Earlier Source Drafts','Editable Artwork and Icons']:
 with zipfile.ZipFile(root/'.staging'/(name+'.zip')) as z:
  assert z.testzip() is None
  for member in z.namelist():assert hashlib.sha256(z.read(member)).hexdigest()==hashlib.sha256((root/member).read_bytes()).hexdigest()
(root/'provenance/inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(stage/'provider-final.json',root/'provenance/provider-registry.json')
manifest=tomllib.loads((root/'playtrace.toml').read_text())
rows=[['Source ID','File ID','Kind','Role','Schema','Title','URL','Status','Tables','Notes']]
for s in manifest['sources']:
 rows.append([s['id'],s['file_id'],s['kind'],s['role'],s['schema_id'],s['title'],'https://drive.google.com/open?id='+s['file_id'],'current',json.dumps(s.get('tables',[])),'Tutorial executable scope is defined by Core Rules and tutorial.json'])
inv=[['Source ID','Original Path','Modified UTC','SHA256','Bytes','Disposition','Reason','Local Destination','Drive File ID','Drive URL','Archive Member','Canonical Links']]
for i in items:inv.append([i['source_id'],i['original_path'],i['modified_utc'],i['sha256'],i['bytes'],i['disposition'],i['reason'],i['destination'] or '',i.get('drive_file_id') or '',i.get('drive_url',''),i.get('archive_member') or '', '\n'.join(i['canonical_links'])])
gaps=[['ID','Priority','Name','Status','Details']]
for n,p in enumerate((root/'design/gaps.md').read_text().split('\n\n')):
 if p.startswith('P'):gaps.append([f'ad-gap-{n}',p[:2],p.split(':')[0][3:],'open',p])
gaps.append(['ad-gap-salvage','P1','Salvage Manifest unlock','open','Crash has two current salvage recipes. The requirement for three does not fire in the tutorial. No third recipe is invented.'])
(root/'provenance/project-tables.json').write_text(json.dumps({'Manifest':rows,'Sources':inv,'Gaps':gaps},ensure_ascii=False),encoding='utf8')
print('Reconciled',len(items),'source records; byte hashes and both archives verified')
