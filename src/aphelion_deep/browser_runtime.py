"""Browser host adapter; runs the same Room, Session and rules as the local host."""
import hashlib
import json
import math
from pathlib import Path
from .engine import Blocked, load_cards
from .room import Room
from .session import Session


def json_digest(value, domain):
    """PlayTrace's version-1 canonical identity encoding for JSON values only."""
    def normalize(v):
        if v is None:
            return {'t': 'none'}
        if type(v) is bool:
            return {'t': 'bool', 'v': v}
        if type(v) is int:
            return {'t': 'int', 'v': str(v)}
        if type(v) is float and math.isfinite(v):
            return {'t': 'float', 'v': '0x0.0p+0' if v == 0 else v.hex()}
        if type(v) is str:
            return {'t': 'str', 'v': v}
        if type(v) is list:
            return {'t': 'list', 'v': [normalize(x) for x in v]}
        if type(v) is dict and all(type(k) is str for k in v):
            return {'t': 'map', 'v': [[normalize(k), normalize(v[k])] for k in sorted(v)]}
        raise Blocked('Unsupported canonical JSON value')
    envelope = {'schema': 'playtrace.identity', 'version': 1, 'domain': domain, 'value': normalize(value)}
    return hashlib.sha256(json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def verify_sources(root):
    root = Path(root)
    bindings = json.loads((root / 'aphelion_deep/data/bindings.json').read_text(encoding='utf8'))
    reviewed = json.loads((root / 'reviewed.json').read_text(encoding='utf8'))
    for source, digest in bindings['sources'].items():
        if reviewed['sources'].get(source) != digest:
            raise Blocked('Stale source mapping: ' + source)
    for entity, digest in bindings['entities'].items():
        if entity not in reviewed['entities'] or json_digest(reviewed['entities'][entity], 'aphelion-entity') != digest:
            raise Blocked('Stale or missing entity mapping: ' + entity)
    if json_digest(load_cards(), 'aphelion-cards') != bindings['package_cards']:
        raise Blocked('Packaged card definitions differ from reviewed bindings')


class BrowserSession(Session):
    cache_limit = 8

    def save(self):
        # The JS host commits this history to IndexedDB before broadcasting it.
        pass


class BrowserRoom(Room):
    def asset(self, peer, key, face):
        visible = self.view(peer)['cards'].get(key)
        if not visible or face != visible['face']:
            raise Blocked('This card face is not available to your player')
        names = self.session.view()['state']['card_names']
        image = self.manifest[names[key]['id']][face]
        return {'card': key, 'face': face, 'asset': image['path'], 'sha256': image['sha256']}


class BrowserHost:
    def __init__(self, root, binding, saved=None):
        verify_sources(root)
        self.session = BrowserSession(Path(root) / 'browser-save.json', binding)
        if saved is not None:
            self.session.data = self.session.validate(saved)
            self.session.result(saved['current'])
        self.room = BrowserRoom(root, self.session)

    def dispatch(self, path, data=None):
        data = data or {}
        room, reply, departed = self.room, {}, []
        if path == '/api/host':
            return {'token': 'browser', 'invite': room.invite, 'view': room.view()}
        if path == '/api/export':
            return self.session.data
        if path == '/api/start-room':
            room.start_room()
            reply = {'invite': room.invite}
        elif path == '/api/message':
            reply = room.command(data['peer'], data['message'])
            if data['message'].get('type') == 'asset':
                return {'reply': reply}
        elif path == '/api/facilitator-asset':
            return {'reply': room.asset(None, data['card'], data['face'])}
        elif path == '/api/disconnect':
            room.disconnect(data['peer'])
        elif path == '/api/release':
            departed = [p for p, m in room.members.items() if m['role'] == data['role']]
            room.release(data['role'])
        elif path == '/api/rewind':
            room.rewind(data['node'])
        else:
            raise Blocked('Unknown browser host operation')
        return {'reply': reply, 'views': room.views(), 'host': room.view('host'), 'departed': departed}
