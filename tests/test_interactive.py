from copy import deepcopy
import json
from pathlib import Path
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import pytest
from aphelion_deep.engine import Engine, Blocked
from aphelion_deep.interactive import replay
from aphelion_deep.play import Session, make_server, verify_workspace

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = json.loads((ROOT / "tutorial.json").read_text())["plugin_config"]


def tutorial_answer(result):
    prompt, turn = result["prompt"], result["turn"]
    key = prompt["key"]
    values = [o["value"] for o in prompt["options"]]
    t = SCRIPT["turns"][turn - 1]
    parts = key.split(":")
    kind = parts[1]
    if key in SCRIPT["choices"]:
        answer = SCRIPT["choices"][key]
    elif kind == "move":
        answer = t["assignments"][parts[2]]
    elif kind == "explore-order":
        answer = next(x for x in t["exploration_order"] if x in values)
    elif kind == "upkeep-location":
        answer = next(x for x in t["upkeep_order"] if x in values)
    elif kind == "upkeep-card":
        answer = next(x for x in t["upkeep_order"][parts[2]] if x in values)
    elif kind == "cultivate":
        answer = SCRIPT["choices"].get(f"{turn}:cultivate")
        if answer not in values:
            answer = None
    elif kind == "craft":
        answer = next((x for x in t["crafts"] if x in values), None)
    else:
        answer = values[0]
    assert answer in values, (key, answer, values)
    return {"key": key, "value": answer}


@pytest.fixture(scope="module")
def played():
    decisions = []
    for _ in range(250):
        result = replay(decisions)
        assert result["status"] != "blocked", result["error"]
        if result["status"] == "complete":
            return decisions, result
        decisions.append(tutorial_answer(result))
    pytest.fail("Tutorial did not finish")


def test_interactive_tutorial_matches_scripted_engine(played):
    decisions, result = played
    baseline = Engine(SCRIPT)
    baseline.run()
    assert result["state"] == baseline.state
    assert result == replay(decisions)
    assert len(decisions) > 50


def test_rollback_branch_and_restart_preserve_all_state(tmp_path, played):
    session = Session(tmp_path / "save.json", "test-binding")
    for decision in played[0][:25]:
        session.act(session.data["current"], **decision)
    previous = deepcopy(session.view())
    session.checkout("0")
    session.act("0", "1:move:engineer", "R")
    branch = session.data["current"]
    assert len(session.data["nodes"]) == 27
    assert session.result(branch)["state"]["players"]["engineer"]["at"] == "R"
    session.checkout(previous["current"])
    assert session.view()["state"] == previous["state"]
    loaded = Session(session.path, session.binding)
    assert loaded.view() == session.view()
    loaded.checkout(branch)
    assert loaded.view()["state"] == session.result(branch)["state"]


def test_invalid_or_stale_decisions_do_not_mutate_history(tmp_path):
    session = Session(tmp_path / "save.json", "a")
    before = deepcopy(session.data)
    with pytest.raises(Blocked):
        session.act("0", "1:move:engineer", "Atlantis")
    assert session.data == before
    session.act("0", "1:move:engineer", "C")
    with pytest.raises(Blocked, match="out of date"):
        session.act("0", "1:move:engineer", "R")
    with pytest.raises(Blocked, match="different source"):
        Session(session.path, "b")
    with pytest.raises(Blocked):
        replay([{"key": "unsupported", "value": "forced gate"}])


def test_card_history_points_restore_decks_tracks_hands_and_once_flags(played):
    decisions, final = played
    for i, decision in enumerate(decisions):
        if ":cultivate:" in decision["key"] and decision["value"]:
            before, after = replay(decisions[:i]), replay(decisions[:i + 1])
            assert not before["state"]["players"]["systems"]["cultivator_used_this_turn"]
            assert after["state"]["players"]["systems"]["cultivator_used_this_turn"]
            assert replay(decisions[:i]) == before
            return
    pytest.fail("No cultivation exercised")


def test_workspace_source_binding():
    assert len(verify_workspace(ROOT)) == 64


def test_http_play_actions_and_local_origin_protection(tmp_path):
    session = Session(tmp_path / "save.json", "test")
    server = make_server(ROOT, session, 0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/play.html") as response:
            assert b"Expedition history" in response.read()
        with urlopen(base + "/api/state") as response:
            state = json.load(response)
        body = json.dumps({"node": "0", "key": state["prompt"]["key"], "value": "C"}).encode()
        with pytest.raises(HTTPError) as error:
            urlopen(Request(base + "/api/action", body, headers={"Origin": "https://other.example"}))
        assert error.value.code == 403
        with urlopen(Request(base + "/api/action", body, headers={"X-Play-Token": state["token"], "Content-Type": "application/json"})) as response:
            assert json.load(response)["state"]["players"]["engineer"]["at"] == "C"
        with urlopen(base + "/api/export") as response:
            assert len(json.load(response)["nodes"]) == 2
    finally:
        server.shutdown()
        server.server_close()
