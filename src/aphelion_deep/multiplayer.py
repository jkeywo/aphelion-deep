"""PeerJS host bridge. Python stays on loopback; guests use WebRTC data channels."""
import argparse
import base64
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import urlsplit
import webbrowser

from .engine import Blocked, ROLE_OWNERS
from .presentation import PLAYER_NAMES
from .play import Session, verify_workspace

PROTOCOL = 1


class Room:
    def __init__(self, root, session):
        self.root, self.session = Path(root), session
        self.invite = secrets.token_hex(12)
        self.members = {}
        self.revision = 0
        self.sequence = 0
        self.votes = {}
        self.assignments = {}
        self.manifest = json.loads((self.root / 'reports/cards/manifest.json').read_text(encoding='utf8'))['cards']

    def join(self, peer, message):
        if message.get('protocol') != PROTOCOL or message.get('invite') != self.invite:
            raise Blocked('Wrong room code or incompatible multiplayer page')
        resume = message.get('resume')
        if resume:
            match = next((m for m in self.members.values() if secrets.compare_digest(m['resume'], str(resume))), None)
            if match:
                old = next(k for k, v in self.members.items() if v is match)
                del self.members[old]
                self.members[peer] = {**match, 'online': True}
                self.sequence += 1
                return {'resume': resume}
        if peer in self.members:
            raise Blocked('This connection already has a seat')
        role = message.get('role')
        if role not in PLAYER_NAMES or any(m['role'] == role for m in self.members.values()):
            raise Blocked('That role is already reserved; reconnect with its original browser or ask the host to release it')
        name = message.get('name')
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 40:
            raise Blocked('Enter a name of 1–40 characters')
        token = secrets.token_hex(24)
        self.members[peer] = {'name': name.strip(), 'role': role, 'resume': token, 'online': True}
        self.sequence += 1
        return {'resume': token}

    def disconnect(self, peer):
        if peer in self.members:
            self.members[peer]['online'] = False
            self.votes.pop(self.members[peer]['role'], None)
            self.assignments.pop(self.members[peer]['role'], None)
            self.sequence += 1

    def ready(self):
        return {m['role'] for m in self.members.values() if m['online']} == set(PLAYER_NAMES)

    def role(self, peer):
        member = self.members.get(peer)
        if not member or not member['online']:
            raise Blocked('Join or reconnect to a player seat first')
        return member['role']

    def scope(self, prompt, state, value):
        """Return participating roles and whether their choice needs unanimity."""
        parts = prompt['key'].split(':')
        kind, subject = parts[1], parts[2] if len(parts) > 2 else ''
        players = state['players']
        def here(location):
            return [p for p, v in players.items() if v['at'] == location] or list(PLAYER_NAMES)
        if kind == 'assign':
            return [], False  # Separate per-player assignment command.
        if kind in ('explore-order', 'upkeep-location', 'finish'):
            return list(PLAYER_NAMES), True
        if kind == 'dilemma':
            return here(subject[0]), True
        if kind == 'eat':
            return [subject], False
        if kind == 'craft':
            if value is None:
                return list(PLAYER_NAMES), True
            return [value[1] if isinstance(value, list) else value['actor']], False
        if isinstance(value, dict) and value.get('actor'):
            return [value['actor']], False
        if kind in ('flip', 'resolve') and subject in ROLE_OWNERS:
            return [ROLE_OWNERS[subject]], False
        if kind == 'optional':
            owners = [p for p, v in players.items() if subject in v['hand']]
            return owners or here(subject[0]), False
        if kind in ('reveal', 'set-aside', 'gate', 'flip', 'resolve', 'place-reference', 'recipient', 'feed', 'convert', 'upkeep-card'):
            return here(subject[0]), False
        raise Blocked('No multiplayer ownership rule for this decision: ' + prompt['key'])

    def commit(self, prompt, value, trade=False):
        self.session.act(self.session.data['current'], prompt['key'] + (':trade' if trade else ''), value)
        self.revision += 1
        self.votes.clear()
        self.assignments.clear()

    def command(self, peer, message):
        if not isinstance(message, dict) or len(json.dumps(message)) > 65536:
            raise Blocked('Invalid multiplayer message')
        kind = message.get('type')
        if kind == 'join':
            return self.join(peer, message)
        role = self.role(peer)
        if kind == 'sync':
            return {}
        if kind == 'asset':
            return self.asset(peer, message.get('card'), message.get('face'))
        if not self.ready():
            raise Blocked('All three human players must be connected before play continues')
        result = self.session.view()
        prompt = result['prompt']
        if not prompt or message.get('revision') != self.revision or message.get('node') != result['current'] or message.get('key') != prompt['key']:
            raise Blocked('The game has moved on. Use the updated table and choose again')
        value = message.get('value')
        if kind == 'assign':
            if prompt.get('kind') != 'assignments' or value not in prompt['locations']:
                raise Blocked('Invalid destination')
            self.assignments[role] = value
            if set(self.assignments) == set(PLAYER_NAMES):
                self.commit(prompt, dict(self.assignments))
        elif kind == 'trade':
            if not isinstance(value, dict) or value.get('actor') != role or not any(o['value'] == value for o in prompt['trades']):
                raise Blocked('You can only give your own non-role cards to players at your location')
            self.commit(prompt, value, trade=True)
        elif kind == 'action':
            if not any(o['value'] == value for o in prompt['options']):
                raise Blocked('Unavailable action')
            eligible, unanimous = self.scope(prompt, result['state'], value)
            if role not in eligible:
                raise Blocked('This decision belongs to another player or expedition')
            if unanimous:
                self.votes[role] = value
                if all(p in self.votes and self.votes[p] == value for p in eligible):
                    self.commit(prompt, value)
            else:
                self.commit(prompt, value)
        else:
            raise Blocked('Unknown multiplayer command')
        self.sequence += 1
        return {}

    def rewind(self, node):
        self.session.checkout(node)
        self.revision += 1
        self.sequence += 1
        self.votes.clear()
        self.assignments.clear()

    def release(self, role):
        for peer in list(self.members):
            if self.members[peer]['role'] == role:
                del self.members[peer]
        self.votes.pop(role, None)
        self.assignments.pop(role, None)
        self.sequence += 1

    def start_room(self):
        self.members.clear()
        self.invite = secrets.token_hex(12)
        self.votes.clear()
        self.assignments.clear()
        self.revision += 1
        self.sequence += 1

    def view(self, peer=None):
        result = self.session.view()
        role = self.members.get(peer, {}).get('role')
        state = deepcopy(result['state'])
        table = result['table']['cards']
        visible = {}
        def show(key, face='front'):
            if key in ROLE_OWNERS and ROLE_OWNERS[key] != role:
                face = 'back'
            visible[key] = {'name': state['card_names'][key]['name'], 'face': face}
        for loc in state['locations'].values():
            top = loc['deck'][loc['position']] if loc['position'] < len(loc['deck']) else None
            loc['top'], loc['remaining'] = top, len(loc['deck']) - loc['position']
            del loc['deck']
            if top:
                show(top, 'back')
            for key in loc['cards']:
                show(key, table.get(key, {}).get('face', 'front'))
            for key in loc['set_aside'] + loc['recipes']:
                show(key, 'back')
            for key in loc['discard']:
                show(key)
        for player in state['players'].values():
            for key in player['hand']:
                show(key)
        if state.get('drawn_card'):
            show(state['drawn_card']['key'], state['drawn_card']['face'])
        state.pop('card_names')
        prompt = deepcopy(result['prompt'])
        if prompt:
            prompt['trades'] = [o for o in prompt['trades'] if o['value']['actor'] == role]
            for option in prompt['options']:
                eligible, unanimous = self.scope(prompt, state, option['value'])
                option['enabled'] = self.ready() and role in eligible
                option['unanimous'] = unanimous
                option['eligible'] = eligible
        return {'protocol': PROTOCOL, 'sequence': self.sequence, 'revision': self.revision,
                'node': result['current'], 'role': role, 'ready': self.ready(), 'turn': result['turn'],
                'status': result['status'], 'error': result['error'], 'state': state, 'cards': visible,
                'table': table, 'prompt': prompt, 'votes': deepcopy(self.votes), 'assignments': deepcopy(self.assignments),
                'roster': [{k: m[k] for k in ('name', 'role', 'online')} for m in self.members.values()],
                'history': [{'id': n['id'], 'parent': n['parent'], 'label': n['label']} for n in result['history']],
                'events': [e['data']['description'] for e in result['recent_events']]}

    def asset(self, peer, key, face):
        visible = self.view(peer)['cards'].get(key)
        if not visible or face != visible['face']:
            raise Blocked('This card face is not available to your player')
        names = self.session.view()['state']['card_names']
        path = self.root / 'reports/cards' / self.manifest[names[key]['id']][face]['path']
        return {'card': key, 'face': face, 'image': 'data:image/webp;base64,' + base64.b64encode(path.read_bytes()).decode()}

    def views(self):
        return {p: self.view(p) for p, m in self.members.items() if m['online']}


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
                    app = (root / 'reports/multiplayer.js').read_text(encoding='utf8')
                    page = page.replace('<script src="vendor/peerjs-1.5.5.min.js"></script>', '<script>' + vendor + '</script>')
                    page = page.replace('<script src="multiplayer.js"></script>', '<script>' + app + '</script>')
                    page = page.replace('data-host="auto"', 'data-host="guest"')
                return self.respond(page.encode(), mime='text/html', download='aphelion-multiplayer.html' if path == '/guest.html' else None)
            if path in ('/multiplayer.js', '/vendor/peerjs-1.5.5.min.js'):
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
