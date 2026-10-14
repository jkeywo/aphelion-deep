"""PeerJS host bridge. Python stays on loopback; guests use WebRTC data channels."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import urlsplit
import webbrowser

from .engine import Blocked
from .play import Session, verify_workspace

from .room import Room, PROTOCOL


def make_server(root, room, port):
    token = secrets.token_urlsafe(32)
    root = Path(root)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def trusted(self):
            expected = f'127.0.0.1:{self.server.server_port}'
            return self.headers.get('Host') == expected and self.headers.get('Origin', 'http://' + expected) == 'http://' + expected

        def respond(self, value, status=200, mime='application/json', download=None):
            body = json.dumps(value, ensure_ascii=False).encode() if mime == 'application/json' else value
            self.send_response(status)
            self.send_header('Content-Type', mime + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https: wss:; frame-ancestors 'none'")
            if download:
                self.send_header('Content-Disposition', 'attachment; filename="' + download + '"')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if not self.trusted():
                return self.respond({'error': 'Local origin required'}, 403)
            path = urlsplit(self.path).path
            if path in ('/', '/multiplayer.html', '/guest.html'):
                page = (root / 'reports/multiplayer.html').read_text(encoding='utf8')
                if path == '/guest.html':
                    vendor = (root / 'reports/vendor/peerjs-1.5.5.min.js').read_text(encoding='utf8').replace('</script', '<\\/script')
                    browser = (root / 'reports/browser-host.js').read_text(encoding='utf8')
                    page = page.replace('<script src="browser-host.js"></script>', '<script>' + browser + '</script>')
                    app = (root / 'reports/multiplayer.js').read_text(encoding='utf8')
                    page = page.replace('<script src="vendor/peerjs-1.5.5.min.js"></script>', '<script>' + vendor + '</script>')
                    page = page.replace('<script src="multiplayer.js"></script>', '<script>' + app + '</script>')
                    page = page.replace('data-host="auto"', 'data-host="guest"')
                return self.respond(page.encode(), mime='text/html', download='aphelion-multiplayer.html' if path == '/guest.html' else None)
            if path in ('/multiplayer.js', '/browser-host.js', '/vendor/peerjs-1.5.5.min.js'):
                return self.respond((root / 'reports' / path[1:]).read_bytes(), mime='text/javascript')
            if path == '/api/host':
                return self.respond({'token': token, 'invite': room.invite, 'view': room.view()})
            if path == '/api/export':
                return self.respond(room.session.data)
            self.respond({'error': 'Not found'}, 404)

        def do_POST(self):
            if not self.trusted() or self.headers.get('X-Host-Token') != token:
                return self.respond({'error': 'Host origin and token required'}, 403)
            try:
                size = int(self.headers.get('Content-Length', 0))
                if not 0 < size <= 70000:
                    raise Blocked('Message too large')
                data = json.loads(self.rfile.read(size))
                path = urlsplit(self.path).path
                reply = {}
                departed = []
                if path == '/api/message':
                    peer = data['peer']
                    if not isinstance(peer, str) or not 1 <= len(peer) <= 120:
                        raise Blocked('Invalid peer identity')
                    reply = room.command(peer, data['message'])
                    if data['message'].get('type') == 'asset':
                        return self.respond({'reply': reply})
                elif path == '/api/facilitator-asset':
                    return self.respond({'reply': room.asset(None, data['card'], data['face'])})
                elif path == '/api/disconnect':
                    room.disconnect(data['peer'])
                elif path == '/api/rewind':
                    room.rewind(data['node'])
                elif path == '/api/release':
                    departed = [p for p, m in room.members.items() if m['role'] == data['role']]
                    room.release(data['role'])
                elif path == '/api/start-room':
                    room.start_room()
                    reply = {'invite': room.invite}
                else:
                    raise Blocked('Unknown host operation')
                self.respond({'reply': reply, 'views': room.views(), 'host': room.view('host'), 'departed': departed})
            except (Blocked, KeyError, ValueError, TypeError) as exc:
                self.respond({'error': str(exc)}, 400)

    return HTTPServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path.cwd())
    parser.add_argument('--session', type=Path)
    parser.add_argument('--port', type=int, default=8770)
    parser.add_argument('--open', action='store_true')
    args = parser.parse_args()
    root = args.workspace.resolve()
    session = Session(args.session or root / '.playtrace/multiplayer-session.json', verify_workspace(root))
    room = Room(root, session)
    server = make_server(root, room, args.port)
    url = f'http://127.0.0.1:{server.server_port}/multiplayer.html'
    print('Multiplayer host: ' + url, flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
