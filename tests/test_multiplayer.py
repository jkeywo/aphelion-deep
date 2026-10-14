from copy import deepcopy
from pathlib import Path
import pytest
from aphelion_deep.engine import Blocked
from aphelion_deep.multiplayer import Room
from aphelion_deep.play import Session
from test_interactive import tutorial_answer, ROOT


def room_with_players(tmp_path):
    room = Room(ROOT, Session(tmp_path / 'multiplayer.json', 'test'))
    for role in ('engineer', 'lead', 'systems'):
        room.command(role, dict(type='join', protocol=1, invite=room.invite, name=role, role=role))
    return room


def message(room, value, kind='action'):
    view = room.view('engineer')
    return dict(type=kind, value=value, node=view['node'], revision=view['revision'], key=view['prompt']['key'])


def advance(room):
    result = room.session.view()
    choice = tutorial_answer(result)['value']
    prompt = result['prompt']
    if prompt.get('kind') == 'assignments':
        for role, destination in choice.items():
            room.command(role, message(room, destination, 'assign'))
    else:
        roles, unanimous = room.scope(prompt, result['state'], choice)
        for role in roles if unanimous else roles[:1]:
            room.command(role, message(room, choice))


def test_three_human_tutorial_and_atomic_assignments(tmp_path):
    room = room_with_players(tmp_path)
    saw_assignment = saw_private = False
    for _ in range(400):
        result = room.session.view()
        if result['status'] == 'complete':
            break
        assert result['status'] != 'blocked', result['error']
        for role in ('engineer', 'lead', 'systems'):
            view = room.view(role)
            assert 'deck' not in view['state']['locations']['C']
            assert 'resume' not in str(view['roster'])
        if 'C3' in result['state']['players']['engineer']['hand']:
            assert room.view('engineer')['cards']['C3']['face'] == 'front'
            assert room.view('lead')['cards']['C3']['face'] == 'back'
            with pytest.raises(Blocked):
                room.command('lead', dict(type='asset', card='C3', face='front'))
            assert room.command('engineer', dict(type='asset', card='C3', face='front'))['image'].startswith('data:image/webp')
            saw_private = True
        if result['prompt'].get('kind') == 'assignments':
            saw_assignment = True
            choices = tutorial_answer(result)['value']
            before = deepcopy(result['state'])
            for role in ('engineer', 'lead'):
                room.command(role, message(room, choices[role], 'assign'))
                assert room.session.view()['state'] == before
            room.command('systems', message(room, choices['systems'], 'assign'))
        else:
            advance(room)
    assert room.session.view()['status'] == 'complete'
    assert room.session.view()['turn'] == 3
    assert saw_assignment and saw_private
    loaded = Session(room.session.path, 'test')
    assert loaded.view() == room.session.view()


def test_permissions_unanimity_disconnect_resume_and_stale_rewind(tmp_path):
    room = room_with_players(tmp_path)
    command = message(room, 'C')
    room.command('engineer', command)
    room.command('lead', command)
    assert room.session.data['current'] == '0'
    room.command('systems', command)
    assert room.session.data['current'] == '1'
    with pytest.raises(Blocked, match='another player'):
        room.command('lead', message(room, room.view('lead')['prompt']['options'][0]['value']))
    room.rewind('0')
    with pytest.raises(Blocked, match='moved on'):
        room.command('engineer', command)
    token = room.members['lead']['resume']
    room.disconnect('lead')
    with pytest.raises(Blocked, match='All three'):
        room.command('engineer', message(room, 'C'))
    room.command('new-peer', dict(type='join', protocol=1, invite=room.invite, resume=token))
    assert room.ready() and room.role('new-peer') == 'lead'
    with pytest.raises(Blocked, match='Join or reconnect'):
        room.command('lead', dict(type='sync'))
    with pytest.raises(Blocked):
        room.command('stranger', dict(type='join', protocol=1, invite=room.invite, role='lead', name='intruder'))
    with pytest.raises(Blocked):
        room.command('stranger', dict(type='join', protocol=1, invite='wrong', role='lead', name='intruder'))


def test_trade_ownership_and_private_assets(tmp_path):
    room = room_with_players(tmp_path)
    for _ in range(300):
        prompt = room.session.view()['prompt']
        if prompt['trades']:
            break
        advance(room)
    trade = prompt['trades'][0]['value']
    other = next(p for p in ('engineer','lead','systems') if p != trade['actor'])
    with pytest.raises(Blocked, match='your own'):
        room.command(other, message(room, trade, 'trade'))
    before = room.session.data['current']
    room.command(trade['actor'], message(room, trade, 'trade'))
    state = room.session.view()['state']
    assert trade['card'] not in state['players'][trade['actor']]['hand']
    assert trade['card'] in state['players'][trade['recipient']]['hand']
    room.rewind(before)
    assert trade['card'] in room.session.view()['state']['players'][trade['actor']]['hand']
    with pytest.raises(Blocked):
        room.command(other, dict(type='asset', card='K20', face='front'))


def test_new_room_preserves_history_but_clears_claims_and_votes(tmp_path):
    room = room_with_players(tmp_path)
    advance(room)
    before = deepcopy(room.session.data)
    old_invite = room.invite
    room.start_room()
    assert room.session.data == before
    assert not room.ready() and not room.members and not room.votes
    assert old_invite != room.invite
    with pytest.raises(Blocked):
        room.command('engineer', dict(type='sync'))


def test_host_http_boundary_and_standalone_guest(tmp_path):
    from threading import Thread
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    import json
    from aphelion_deep.multiplayer import make_server
    room = room_with_players(tmp_path)
    server = make_server(ROOT, room, 0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}'
    try:
        boot = json.load(urlopen(url + '/api/host'))
        body = json.dumps({'node':'0'}).encode()
        for headers in ({}, {'X-Host-Token':boot['token'], 'Origin':'https://untrusted.example'}):
            with pytest.raises(HTTPError) as exc:
                urlopen(Request(url + '/api/rewind', data=body, headers=headers))
            assert exc.value.code == 403
        html = urlopen(url + '/guest.html').read().decode()
        assert 'data-host="guest"' in html
        assert '<script src=' not in html
        assert html == (ROOT / 'reports/aphelion-multiplayer.html').read_text(encoding='utf8')
        result = json.load(urlopen(Request(url + '/api/start-room', data=b'{}', headers={'X-Host-Token':boot['token']})))
        assert result['reply']['invite'] == room.invite
        assert not result['views']
    finally:
        server.shutdown()
        thread.join()
