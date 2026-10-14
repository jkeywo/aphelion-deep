"""Build the unified browser-hosted game, exact Python rules and card assets."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from aphelion_deep.browser_runtime import json_digest
from aphelion_deep.engine import load_cards

bindings = json.loads((root / 'src/aphelion_deep/data/bindings.json').read_text(encoding='utf8'))
capture = json.loads((root / 'provenance/snapshot.json').read_text(encoding='utf8'))
snapshot = capture.get('snapshot', capture)
reviewed = {
    'sources': {r['source_id']: r['content_digest'] for r in snapshot['source_revisions'] if r['source_id'] in bindings['sources']},
    'entities': {e['id']: e['attributes'] for e in snapshot['entities'] if e['id'] in bindings['entities']},
}
assert reviewed['sources'] == bindings['sources'], 'Stale source mapping'
assert {k: json_digest(v, 'aphelion-entity') for k, v in reviewed['entities'].items()} == bindings['entities'], 'Stale entity mapping'
assert json_digest(load_cards(), 'aphelion-cards') == bindings['package_cards'], 'Stale packaged cards'

runpy.run_path(str(root / 'tools/build_multiplayer_guest.py'), run_name='__main__')
site = root / '.pages-site'
site.mkdir(exist_ok=True)
allowed = {'index.html', 'peerjs-license.txt', '.nojekyll', 'browser-bundle.json', 'host-worker.mjs', 'cards'}
assert all(p.name in allowed for p in site.iterdir()), 'Unexpected files in Pages staging directory'
page = (root / 'reports/aphelion-multiplayer.html').read_text(encoding='utf8').replace('data-host="guest"', 'data-host="browser"')
(site / 'index.html').write_text(page, encoding='utf8')
(site / 'peerjs-license.txt').write_bytes((root / 'reports/vendor/PeerJS-LICENSE').read_bytes())
(site / '.nojekyll').write_text('', encoding='utf8')
(site / 'host-worker.mjs').write_text((root / 'reports/host-worker.mjs').read_text(encoding='utf8'), encoding='utf8')
files = {}
def include(name, text):
    files[name] = {'text': text, 'sha256': hashlib.sha256(text.encode()).hexdigest()}
for name in ('__init__', 'engine', 'interactive', 'presentation', 'session', 'room', 'browser_runtime'):
    include('aphelion_deep/' + name + '.py', (root / 'src/aphelion_deep' / (name + '.py')).read_text(encoding='utf8'))
for name in ('cards', 'bindings'):
    include('aphelion_deep/data/' + name + '.json', (root / 'src/aphelion_deep/data' / (name + '.json')).read_text(encoding='utf8'))
include('reviewed.json', json.dumps(reviewed, ensure_ascii=False, sort_keys=True))
manifest_text = (root / 'reports/cards/manifest.json').read_text(encoding='utf8')
include('reports/cards/manifest.json', manifest_text)
binding = hashlib.sha256(json.dumps({k: v['sha256'] for k, v in sorted(files.items())}, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
(site / 'browser-bundle.json').write_text(json.dumps({'binding': binding, 'files': files}, ensure_ascii=False), encoding='utf8')
cards = site / 'cards'
cards.mkdir(exist_ok=True)
paths = set()
for card in json.loads(manifest_text)['cards'].values():
    for face in ('front', 'back'):
        image = card[face]
        assert Path(image['path']).name == image['path']
        data = (root / 'reports/cards' / image['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == image['sha256']
        (cards / image['path']).write_bytes(data)
        paths.add(image['path'])
assert {p.name for p in cards.iterdir()} == paths
assert {p.name for p in site.iterdir()} == allowed
print(f'Browser host built: verified rules, {len(paths)} card faces, unified Start / Join page.')
