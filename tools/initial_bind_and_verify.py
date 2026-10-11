from pathlib import Path
import json,re,shutil
from playtrace.canonical import canonical_digest
from docx import Document
root=Path(r'C:\AnalogueGames\aphelion-deep');stage=Path(__file__).parent
cap=json.loads((root/'provenance/workspace-capture.json').read_text(encoding='utf8'));reg=json.loads((root/'provenance/provider-registry.json').read_text())
checks=[]
for slug,d in reg['documents'].items():
 expected=[p.text.strip() for p in Document(root/'.staging'/f'{slug}-import.docx').paragraphs if p.text.strip()]
 actual=[]
 for tab in cap['documents'][d['fileId']]['tabs']:
  for x in tab['body']['content']:
   p=x.get('paragraph',{});s=''.join(e.get('textRun',{}).get('content','') for e in p.get('elements',[])).strip()
   if s:actual.append(re.sub(r' \[PT-ID:ad:[^\]]+:p\d+\]$','',s).strip())
 assert actual==expected,(slug,len(actual),len(expected),next(((a,b) for a,b in zip(actual,expected) if a!=b),None))
 checks.append({'document':slug,'paragraphs':len(actual),'provider_id':d['fileId'],'exact_text_match_after_removing_added_identity_markers':True})
staged=json.loads((root/'provenance/card-table.json').read_text(encoding='utf8'))
readback=cap['spreadsheets'][reg['cards']]['ranges']['Cards!A1:X47']
assert staged==readback,'Card catalogue readback mismatch'
pacing=cap['spreadsheets'][reg['cards']]['ranges']['Pacing!A1:D6']
assert '\n\n'.join(r[3] for r in pacing[1:])==(root/'design/legacy-pacing.md').read_text(encoding='utf8')
snapshot=json.loads((root/'provenance/snapshot.json').read_text(encoding='utf8'));snapshot=snapshot.get('snapshot',snapshot)
bindings={'sources':{r['source_id']:r['content_digest'] for r in snapshot['source_revisions'] if r['source_id'] in ('ad:core-rules','ad:cards')},'entities':{e['id']:canonical_digest(e['attributes'],domain='aphelion-entity') for e in snapshot['entities'] if e['kind']=='card' or e['id'].startswith('ad-') and e['kind']=='passage'},'package_cards':canonical_digest(json.loads((root/'src/aphelion_deep/data/cards.json').read_text(encoding='utf8')),domain='aphelion-cards'),'review':'Initial implementation of user-approved tutorial rules. Rebinding requires source comparison and regression validation.'}
(root/'src/aphelion_deep/data/bindings.json').write_text(json.dumps(bindings,indent=2),encoding='utf8')
shutil.copy2(stage/'plugin.py',root/'src/aphelion_deep/plugin.py')
(root/'provenance/import-verification.json').write_text(json.dumps({'documents':checks,'card_rows':46,'card_fields':24,'all_card_cells_match':True,'full_pacing_matches':True},indent=2),encoding='utf8')
print('Verified all 15 Docs, 46 cards, 24 fields and full pacing; bound',len(bindings['entities']),'entities')
