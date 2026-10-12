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
    elif kind == "assign":
        answer = t["assignments"]
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
    for _ in range(400):
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
    session.act("0", "1:explore-order:2", "R")
    branch = session.data["current"]
    assert len(session.data["nodes"]) == 27
    assert session.result(branch)["prompt"]["key"] == "1:reveal:R1"
    assert session.result(branch)["state"]["players"]["engineer"]["at"] == "C"
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
    session.act("0", "1:explore-order:2", "C")
    with pytest.raises(Blocked, match="out of date"):
        session.act("0", "1:explore-order:2", "R")
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


def test_fixed_department_landings_and_later_movement(played):
    initial = replay([])
    assert {p: value["at"] for p, value in initial["state"]["players"].items()} == {
        "engineer": "C", "lead": "R", "systems": "R"
    }
    assert initial["prompt"]["key"] == "1:explore-order:2"
    assert [o["value"] for o in initial["prompt"]["options"]] == ["C", "R"]
    with pytest.raises(Blocked):
        replay([{"key": "1:move:engineer", "value": "K"}])
    decisions, _ = played
    assert not any(d["key"].startswith("1:move:") for d in decisions)
    index = next(i for i, d in enumerate(decisions) if d["key"] == "2:assign:Exploration")
    second_turn = replay(decisions[:index])
    assert second_turn["prompt"]["locations"] == ["C", "R", "K"]
    alternative = {"engineer": "R", "lead": "C", "systems": "K"}
    alternate = replay(decisions[:index] + [{"key": "2:assign:Exploration", "value": alternative}])
    assert {p: v["at"] for p, v in alternate["state"]["players"].items()} == alternative


def test_draw_back_flip_front_and_rollback(tmp_path):
    session = Session(tmp_path / "save.json", "test")
    session.act("0", "1:explore-order:2", "C")
    session.act("1", "1:reveal:C1", "reveal")
    back = session.view()
    assert back["prompt"]["face"] == "back"
    assert back["state"]["drawn_card"] == {"key": "C1", "face": "back"}
    session.act("2", "1:flip:C1", True)
    assert session.view()["prompt"]["face"] == "front"
    session.checkout("2")
    assert session.view()["state"] == back["state"]
    session.checkout("3")
    session.act("3", "1:resolve:C1", True)
    assert session.view()["state"]["locations"]["C"]["position"] == 1
    assert "drawn_card" not in session.view()["state"]


def test_upkeep_assignment_is_atomic_validated_and_reversible(tmp_path, played):
    decisions, _ = played
    index = next(i for i, d in enumerate(decisions) if d["key"] == "1:assign:Upkeep")
    session = Session(tmp_path / "save.json", "test")
    for decision in decisions[:index]:
        session.act(session.data["current"], **decision)
    before = session.view()
    assert before["prompt"]["locations"] == ["C", "R"]
    for invalid in [{"engineer": "C"}, {"engineer": "K", "lead": "C", "systems": "R"}]:
        with pytest.raises(Blocked):
            session.act(before["current"], "1:assign:Upkeep", invalid)
        assert session.view() == before
    assignment = {"engineer": "R", "lead": "C", "systems": "C"}
    session.act(before["current"], "1:assign:Upkeep", assignment)
    after = session.view()
    assert len(after["history"]) == len(before["history"]) + 1
    assert {p: v["at"] for p, v in after["state"]["players"].items()} == assignment
    session.act(after["current"], after["prompt"]["key"], "C")
    selected = session.view()
    session.act(selected["current"], selected["prompt"]["key"], "C9")
    eating = session.view()
    assert eating["prompt"]["key"] == "1:eat:lead"
    session.act(eating["current"], eating["prompt"]["key"], "C9")
    assert session.view()["prompt"]["key"] == "1:eat:systems"
    session.checkout(before["current"])
    assert session.view()["state"] == before["state"]
