from pathlib import Path
import json,zipfile
root=Path(r'C:\AnalogueGames\aphelion-deep');inventory=json.loads((root/'provenance/inventory.json').read_text())
uploaded=json.loads((Path(__file__).parent/'provider-assets-1.json').read_text())['assets']
for name,kind in [('Earlier Source Drafts','archived'),('Editable Artwork and Icons','asset')]:
 with zipfile.ZipFile(root/'.staging'/(name+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for item in inventory:
   if item['disposition']!=kind:continue
   if kind=='asset' and item['sha256'] in uploaded:continue
   if kind=='asset' and item['destination'] in ('assets/source-3/Playmat.af','assets/source-3/Art/Playmat.jpg'):continue
   z.write(root/item['destination'],item['destination'])
 print(name, (root/'.staging'/(name+'.zip')).stat().st_size)
