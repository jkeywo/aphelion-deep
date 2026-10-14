"""Rebuild the single-file guest page after changing multiplayer HTML or JavaScript."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / 'reports'
page = (reports / 'multiplayer.html').read_text(encoding='utf8').replace('data-host="auto"', 'data-host="guest"')
vendor = (reports / 'vendor/peerjs-1.5.5.min.js').read_text(encoding='utf8').replace('</script', '<\\/script')
app = (reports / 'multiplayer.js').read_text(encoding='utf8')
page = page.replace('<script src="vendor/peerjs-1.5.5.min.js"></script>', '<script>' + vendor + '</script>')
page = page.replace('<script src="browser-host.js"></script>', '<script>' + (reports / 'browser-host.js').read_text(encoding='utf8') + '</script>')
page = page.replace('<script src="multiplayer.js"></script>', '<script>' + app + '</script>')
(reports / 'aphelion-multiplayer.html').write_text(page, encoding='utf8')
print('Built reports/aphelion-multiplayer.html')
