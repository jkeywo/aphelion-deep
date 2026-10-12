"""Render both source-text faces with existing location art; never changes rules.

Run from the game repository: python tools/render_cards.py
The report embeds these images, so its Drive copy also works offline.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
W, H = 900, 1260
INK = '#183a3f'
COLORS = {'Reef Gardens':'#286d62','Crash Flats':'#73553d','Kelp Cathedral':'#365c75','Challenge':'#813f40'}
ART = {'Reef Gardens':'reef-gardens-painterly.png','Crash Flats':'crash-flats.png','Kelp Cathedral':'kelp-cathedrals.png','Challenge':'crash-flats.png'}


def font(size, bold=False):
    # Explicit font files can be supplied on other systems for reproducible output.
    import os
    path = os.environ.get('APHELION_FONT_BOLD' if bold else 'APHELION_FONT')
    return ImageFont.truetype(path or ('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),size)


def wrap(draw,text,f,width):
    lines=[]
    for paragraph in text.split('\n'):
        if not paragraph:
            lines.append('');continue
        line=''
        for word in paragraph.split():
            trial=(line+' '+word).strip()
            if draw.textlength(trial,font=f)>width and line:
                lines.append(line);line=word
            else: line=trial
        lines.append(line)
    return lines


def render(card, face, target):
    color=COLORS[card['Location']]
    im=Image.new('RGB',(W,H),'#f8f6ee');d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,46),fill=color)
    d.text((38,10),card['Location'].upper(),font=font(23,True),fill='white')
    d.text((W-150,10),f"{card['Source ID']} / {face.upper()}",font=font(23,True),fill='white')
    artwork=ROOT/'assets/source-2/Art'/ART[card['Location']]
    with Image.open(artwork) as art:
        im.paste(ImageOps.fit(art.convert('RGB'),(W,235)),(0,46))
    title=wrap(d,card['Name'],font(43,True),800)
    y=312
    for line in title:
        d.text((48,y),line,font=font(43,True),fill=INK);y+=51
    d.text((48,y+8),card['Card Type'].upper(),font=font(23,True),fill=color);y+=55
    d.line((48,y,852,y),fill='#bbc7c0',width=2);y+=25
    text=card.get(face.title()+' Text') or ''
    bottom=1060 if card.get('Track Name') else 1130
    for size in range(31,17,-1):
        lines=wrap(d,text,font(size),798)
        line_height=round(size*1.36)
        if y+len(lines)*line_height<=bottom: break
    else: raise ValueError(f"Text will not fit: {card['ID']} {face}")
    for line in lines:
        d.text((50,y),line,font=font(size),fill=INK);y+=line_height
    if card.get('Track Name'):
        d.text((50,1070),card['Track Name']+' · unmarked printed track',font=font(22,True),fill=color)
        for n in range(6):
            x=78+n*140
            d.ellipse((x-27,1113,x+27,1167),outline=color,width=3)
            d.text((x,1140),str(n),font=font(28,True),fill=INK,anchor='mm')
    d.rectangle((0,1196,W,H),fill=color)
    d.text((35,1205),'THE APHELION DEEP  /  CONSOLIDATED REFERENCE CARD',font=font(21,True),fill='white')
    d.text((35,1231),'Source text preserved. Tutorial rule amendments apply separately.',font=font(18),fill='white')
    im.save(target,format='WEBP',quality=92,method=6)
    return {'path':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'font_size':size}


def main():
    cards=json.loads((ROOT/'src/aphelion_deep/data/cards.json').read_text(encoding='utf8'))
    from playtrace.canonical import canonical_digest
    bindings=json.loads((ROOT/'src/aphelion_deep/data/bindings.json').read_text(encoding='utf8'))
    if canonical_digest(cards,domain='aphelion-cards') != bindings['package_cards']:
        raise ValueError('Card text differs from reviewed source bindings')
    run=json.loads((ROOT/'provenance/tutorial-run.json').read_text(encoding='utf8'))['simulation']
    out=ROOT/'reports/cards';out.mkdir(parents=True,exist_ok=True)
    manifest={'snapshot_digest':run['provenance']['snapshot_digest'],'render_kind':'Consolidated source reference, not an original Affinity export','cards':{}}
    for card in cards:
        entry={'name':card['Name'],'source_fingerprint':card['Source Fingerprint'],
               'note':'Reference render from consolidated card text and existing location artwork. Both source faces are preserved; the agreed tutorial amendments apply separately.'}
        for face in ['front','back']:
            entry[face]=render(card,face,out/f"{card['ID']}-{face}.webp")
        manifest['cards'][card['ID']]=entry
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(f'Rendered {len(cards)*2} faces for {len(cards)} cards to {out}')


if __name__=='__main__': main()
