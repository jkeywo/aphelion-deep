from copy import deepcopy
import json
import runpy
from pathlib import Path
import pytest
from aphelion_deep.browser_runtime import BrowserHost, json_digest
from aphelion_deep.engine import Blocked
from playtrace.canonical import canonical_digest
from test_interactive import ROOT, tutorial_answer


@pytest.fixture(scope="module")
def browser_bundle():
    runpy.run_path(str(ROOT / "tools/build_pages.py"), run_name="__main__")
    return json.loads((ROOT / '.pages-site/browser-bundle.json').read_text(encoding='utf8'))


@pytest.fixture
def browser_host(tmp_path, browser_bundle):
    bundle = browser_bundle
    for name, file in bundle['files'].items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file['text'], encoding='utf8')
    return BrowserHost(tmp_path, bundle['binding'])


def test_browser_source_identity_matches_playtrace():
    values = [None, True, False, 0, -9, 1.25, -0.0, 'Reef 🐟', [1, 'x'], {'b': [False], 'a': None}]
    for value in values:
        assert json_digest(value, 'test') == canonical_digest(value, domain='test')


def test_browser_three_turns_save_restore_rewind_and_assets(browser_host):
    host = browser_host
    host.dispatch('/api/start-room')
    for role in ('engineer', 'lead', 'systems'):
        host.dispatch('/api/message', {'peer': role, 'message': dict(type='join', protocol=1, invite=host.room.invite, role=role, name=role)})
    for _ in range(400):
        result = host.session.view()
        if result['status'] == 'complete':
            break
        assert result['status'] != 'blocked', result['error']
        prompt, value = result['prompt'], tutorial_answer(result)['value']
        roles, unanimous = host.room.scope(prompt, result['state'], value)
        kind = 'action'
        if prompt.get('kind') == 'assignments':
            roles, unanimous, kind = list(value), True, 'assign'
        for role in roles if unanimous else roles[:1]:
            packet = host.dispatch('/api/message', {'peer': role, 'message': dict(type=kind, key=prompt['key'], node=result['current'], revision=host.room.revision, value=value[role] if kind == 'assign' else value)})
    assert host.session.view()['status'] == 'complete'
    saved = deepcopy(host.dispatch('/api/export'))
    restored = BrowserHost(host.room.root, host.session.binding, saved)
    assert restored.session.view() == host.session.view()
    assert not restored.room.members
    restored.dispatch('/api/rewind', {'node':'0'})
    assert restored.session.view()['current'] == '0'
    assert len(restored.session.data['nodes']) == len(saved['nodes'])
    image = restored.dispatch('/api/facilitator-asset', {'card':'C1', 'face':'back'})['reply']
    assert image['asset'].endswith('-back.webp') and len(image['sha256']) == 64
    with pytest.raises(Blocked):
        restored.dispatch('/api/facilitator-asset', {'card':'C3', 'face':'front'})
    with pytest.raises(Blocked, match='different source'):
        BrowserHost(host.room.root, 'changed-binding', saved)


def test_browser_rejects_stale_source_bundle(browser_host):
    path = browser_host.room.root / 'reviewed.json'
    data = json.loads(path.read_text(encoding='utf8'))
    data['sources']['ad:core-rules'] = 'changed'
    path.write_text(json.dumps(data), encoding='utf8')
    with pytest.raises(Blocked, match='Stale source mapping'):
        BrowserHost(browser_host.room.root, browser_host.session.binding)
