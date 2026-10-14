"""Build only the public multiplayer guest interface for GitHub Pages."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / 'tools/build_multiplayer_guest.py'), run_name='__main__')
site = root / '.pages-site'
site.mkdir(exist_ok=True)
allowed = {'index.html', 'peerjs-license.txt', '.nojekyll'}
if any(p.name not in allowed for p in site.iterdir()):
    raise RuntimeError('Unexpected files in Pages staging directory; refusing to publish them')
page = (root / 'reports/aphelion-multiplayer.html').read_text(encoding='utf8')
assert 'data-host="guest"' in page and '<script src=' not in page
(site / 'index.html').write_text(page, encoding='utf8')
(site / 'peerjs-license.txt').write_bytes((root / 'reports/vendor/PeerJS-LICENSE').read_bytes())
(site / '.nojekyll').write_text('', encoding='utf8')
assert {p.name for p in site.iterdir()} == allowed
print('Pages artifact: guest HTML, PeerJS license and .nojekyll only.')
