from pathlib import Path
import json
from copy import deepcopy
import pytest
from aphelion_deep.engine import Engine, Blocked
from aphelion_deep.plugin import AphelionPlugin
from playtrace.simulation import SimulationConfig, SimulationRun
from playtrace.models import DesignSnapshot

ROOT = Path(__file__).resolve().parents[1]


def config():
    return SimulationConfig.model_validate_json((ROOT / "tutorial.json").read_text())


def snapshot():
    d = json.loads((ROOT / "provenance/snapshot.json").read_text(encoding="utf8"))
    return DesignSnapshot.model_validate(d.get("snapshot", d))


def run(c=None, s=None):
    return AphelionPlugin().run(s or snapshot(), c or config(), runner="test")


def engine():
    return Engine(config().plugin_config)


def track(e, key, n, kind="Flora"):
    e.loc(key[0])["cards"][key] = {
        "type": kind,
        "track": "Abundance" if kind == "Mineral" else "Population",
        "value": n,
    }


def test_strict_three_turns_reproducible_and_roundtrippable():
    a, b = run(), run()
    assert not a.blockers and a.semantic_audit.passed
    assert a.metrics.turns_completed == 3 and a.final_state.status == "max_turns"
    assert a.events == b.events and a.state_trace == b.state_trace
    assert SimulationRun.model_validate_json(a.model_dump_json()) == a
    assert a.final_state.data["reactor"] == 1
    assert a.final_state.data["players"]["systems"]["actions"] == ["Cultivator"]
    assert a.final_state.data["players"]["lead"]["capabilities"]["Power"] == 1
    gates = [e for e in a.events if e.event_type == "exploration.gate"]
    assert [e.data["open"] for e in gates] == [False, False, True, False, True]
    assert gates[-1].data["available"]["Knowledge"] == 2
    assert (
        sum(
            e.event_type == "card.revealed"
            and e.entity_ids == ("reef_gardens_1_a_rough_landing",)
            for e in a.events
        )
        == 1
    )
    assert a.final_state.data["locations"]["R"]["position"] == 18


def test_all_revealed_locations_upkeep_without_players():
    a = run()
    data = a.final_state.data
    assert data["locations"]["C"]["resources"]["Materials"] == 13
    assert data["locations"]["C"]["cards"]["C9"]["value"] == 4
    assert any(
        e.turn == 3 and e.event_type == "card.upkeep" and e.data["location"] == "K"
        for e in a.events
    )
    assert not any(
        e.turn == 3 and e.event_type == "player.ate" and e.data["payment"] == "K2"
        for e in a.events
    )


def test_local_power_does_not_travel_and_knowledge_is_scoped():
    e = engine()
    e.state["players"]["engineer"].update(at="R", hand=["C3", "C13", "Cs1"])
    e.loc("C")["local_icons"]["Power"] = 2
    assert e.icons("R").get("Power") == 1
    assert e.icons("R").get("Knowledge", 0) == 0
    assert e.icons("R", True)["Knowledge"] == 2
    assert e.icons("R")["Oxygen"] == 1


def test_fabricator_discount_has_zero_floor():
    e = engine()
    e.phase = "Upkeep"
    e.state["players"]["engineer"]["at"] = "C"
    track(e, "C9", 5, "Location")
    e.craft("Cs1", "engineer")
    assert e.loc("C")["resources"]["Materials"] == 0
    with pytest.raises(Blocked):
        e.craft("Cs1", "engineer")


def test_crafting_costs_and_power_prerequisite():
    e = engine()
    e.phase = "Upkeep"
    e.state["players"]["lead"]["at"] = "R"
    with pytest.raises(Blocked, match="Insufficient"):
        e.craft("Rs2", "lead")
    e = engine()
    e.phase = "Upkeep"
    e.state["players"]["engineer"]["at"] = "C"
    with pytest.raises(Blocked, match="3 Power"):
        e.craft("Cs3", "engineer")


def test_full_payment_or_no_consumption():
    e = engine()
    e.turn = 1
    track(e, "R10", 1)
    track(e, "R11", 5, "Fauna")
    e.script["choices"]["1:feed:R11"] = ["R10"]
    e.feed("R11", "flora", 3, 0, 2)
    assert e.value("R10") == 1 and e.value("R11") == 3
    assert e.events[-1]["data"]["consumed"] == 0


def test_grazers_flora_and_crabs_other_fauna():
    e = engine()
    e.turn = 1
    track(e, "R10", 3)
    track(e, "R11", 2, "Fauna")
    e.upkeep_card("R11")
    assert e.value("R10") == 2 and e.value("R11") == 3
    track(e, "C11", 2, "Fauna")
    track(e, "C10", 3)
    track(e, "C12", 5, "Mineral")
    e.upkeep_card("C11")
    assert e.value("C10") == 3 and e.value("C11") == 1


def test_feeding_cannot_silently_omit_available_food():
    e = engine()
    e.turn = 1
    track(e, "R10", 5)
    track(e, "R11", 2, "Fauna")
    e.script["choices"]["1:feed:R11"] = []
    with pytest.raises(Blocked, match="omits available"):
        e.feed("R11", "flora", 1, 1, 1)


def test_track_endpoints_and_exhaustion():
    e = engine()
    track(e, "R10", 4)
    e.change("R10", 100)
    assert e.value("R10") == 5
    e.change("R10", -100)
    assert e.card("R10") is None and "R10" in e.loc("R")["discard"]


def test_cultivator_phase_target_and_frequency():
    e = engine()
    e.turn = 1
    e.phase = "Exploration"
    e.state["players"]["systems"].update(at="R", hand=["R4"])
    track(e, "R10", 2)
    e.cultivate("R")
    e.cultivate("R")
    assert e.value("R10") == 3
    e.phase = "Upkeep"
    with pytest.raises(Blocked, match="Exploration"):
        e.cultivate("R")


def test_calcite_uses_abundance_and_actual_reactor():
    e = engine()
    track(e, "R18", 2, "Mineral")
    e.state["reactor"] = 3
    e.upkeep_card("R18")
    assert e.loc("R")["resources"]["Materials"] == 1 and e.value("R18") == 1


def test_cut_free_restored_and_no_challenge_injection():
    a = run()
    index = next(
        i
        for i, e in enumerate(a.events)
        if e.event_type == "dilemma.resolved" and e.data["choice"] == "Cut it free"
    )
    s = a.state_trace[index].state.data["locations"]["K"]
    assert (
        s["cards"]["K2"]["value"] == 4
        and s["resources"]["Materials"] == 1
        and "K8" in s["discard"]
    )
    assert not any("wraith" in x for e in a.events for x in e.entity_ids)


@pytest.mark.parametrize(
    "mutation", ["missing", "unsupported", "optional", "unoccupied", "extra"]
)
def test_script_errors_block_explicitly(mutation):
    raw = config().model_dump(mode="json")
    p = raw["plugin_config"]
    if mutation == "missing":
        del p["choices"]["1:dilemma:C14"]
    if mutation == "unsupported":
        p["choices"]["2:dilemma:K8"] = "Recover it"
    if mutation == "optional":
        del p["turns"][0]["optional_actions"]["R13"]
    if mutation == "unoccupied":
        del p["turns"][1]["upkeep_order"]["C"]
    if mutation == "extra":
        p["choices"]["unrequested"] = "invented"
    a = run(SimulationConfig.model_validate(raw))
    assert a.blockers and not a.semantic_audit.passed


@pytest.mark.parametrize("mutation", ["card", "source", "missing"])
def test_stale_source_mappings_fail(mutation):
    raw = snapshot().model_dump(mode="json")
    if mutation == "card":
        next(e for e in raw["entities"] if e["kind"] == "card")["attributes"]["fields"][
            "Front Text"
        ] = "changed"
    if mutation == "source":
        next(r for r in raw["source_revisions"] if r["source_id"] == "ad:core-rules")[
            "content_digest"
        ] = "changed"
    if mutation == "missing":
        raw["entities"] = [e for e in raw["entities"] if e["id"] != "ad-cut-free"]
        raw["assertions"] = [
            a for a in raw["assertions"] if a["subject_id"] != "ad-cut-free"
        ]
    a = run(s=DesignSnapshot.model_validate(raw))
    assert a.blockers and "mapping" in a.blockers[0].message


def test_unreachable_three_recipe_unlock_is_not_fabricated():
    a = run()
    assert "C13" in a.final_state.data["locations"]["C"]["set_aside"]
