"""Installable, source-bound Aphelion tutorial plugin."""

import json
from importlib.resources import files
from importlib.metadata import version
from playtrace.canonical import canonical_digest
from playtrace.simulation import (
    SimulationRun,
    SimulationConfig,
    SimulationProvenance,
    SimulationMetrics,
    SimulationEvent,
    SimulationCheckpoint,
    PluginSimulationState,
    SimulationStatus,
    SimulationBlocker,
    BlockerKind,
    PlayerPolicyKind,
    content_digest,
    snapshot_content_digest,
)
from playtrace.semantics import SemanticUsage, SemanticOrigin, audit_semantics
from .engine import Engine, Blocked, load_cards


class AphelionPlugin:
    id = "aphelion-deep"
    version = "0.1.1"
    project_ids = ("aphelion-deep",)

    def run(self, snapshot, config, *, runner):
        blockers = []
        engine = None
        events = []
        checkpoints = []
        initial = None
        final = None
        completed = 0
        bindings = json.loads(
            files("aphelion_deep")
            .joinpath("data/bindings.json")
            .read_text(encoding="utf8")
        )
        entities = {e.id: e for e in snapshot.entities}
        revisions = {r.source_id: r for r in snapshot.source_revisions}
        try:
            if snapshot.project_id != "aphelion-deep":
                raise Blocked("Wrong project")
            if (
                config.player_policy != PlayerPolicyKind.PLUGIN_SCRIPTED
                or config.max_turns != 3
                or config.scenario_id != "tutorial-three-turns"
                or config.ruleset_id != "aphelion-tutorial-v1"
            ):
                raise Blocked("Unsupported tutorial configuration")
            if (
                tuple(config.character_ids) != ("engineer", "lead", "systems")
                or config.overrides
                or config.deck_order
                or config.scripted_steps
            ):
                raise Blocked(
                    "Tutorial roles, deck order and rules cannot be overridden"
                )
            if set(config.plugin_config) != {"turns", "choices"} or not isinstance(
                config.plugin_config["choices"], dict
            ):
                raise Blocked("Missing or unsupported player policy fields")
            for sid, digest in bindings["sources"].items():
                if sid not in revisions or revisions[sid].content_digest != digest:
                    raise Blocked(
                        "Stale source mapping: "
                        + sid
                        + "; review changed canonical content before rebuilding bindings"
                    )
            for eid, digest in bindings["entities"].items():
                if (
                    eid not in entities
                    or canonical_digest(
                        entities[eid].attributes, domain="aphelion-entity"
                    )
                    != digest
                ):
                    raise Blocked("Stale or missing entity mapping: " + eid)
            if (
                canonical_digest(load_cards(), domain="aphelion-cards")
                != bindings["package_cards"]
            ):
                raise Blocked("Packaged card definitions differ from reviewed bindings")
            engine = Engine(config.plugin_config)
            engine.run()
        except (Blocked, KeyError, TypeError, ValueError) as exc:
            blockers.append(
                SimulationBlocker(
                    id="aphelion:blocker",
                    kind=BlockerKind.UNSUPPORTED_RULE,
                    message=str(exc),
                    required_input="Provide the exact supported choice or review changed canonical source mappings. No fallback is applied.",
                )
            )
        if engine:
            completed = sum(e["event_type"] == "turn.completed" for e in engine.events)
            engine.emit(
                "simulation.blocked" if blockers else "simulation.completed",
                blockers=[b.message for b in blockers],
            )
            for i, (event, data) in enumerate(
                zip(engine.events, engine.checkpoints, strict=True)
            ):
                references = tuple(
                    a.id
                    for a in snapshot.assertions
                    if a.subject_id in event["entity_ids"]
                )
                events.append(
                    SimulationEvent(
                        sequence=i,
                        **event,
                        assertion_ids=references,
                        semantic_ids=("ad:tutorial-interpreter-v1",),
                    )
                )
                status = (
                    SimulationStatus.BLOCKED
                    if blockers and i == len(engine.events) - 1
                    else SimulationStatus.MAX_TURNS
                    if not blockers and i == len(engine.events) - 1
                    else SimulationStatus.RUNNING
                )
                checkpoints.append(
                    SimulationCheckpoint(
                        sequence=i,
                        state=PluginSimulationState(
                            plugin_id=self.id,
                            turn=event["turn"],
                            status=status,
                            data=data,
                        ),
                    )
                )
            initial = checkpoints[0].state
            final = checkpoints[-1].state
        usage = SemanticUsage(
            id="ad:tutorial-interpreter-v1",
            origin=SemanticOrigin.PLUGIN_EXTENSION,
            description="Closed tutorial interpreter bound to exact canonical source and entity fingerprints; outside-slice actions fail explicitly.",
            entity_ids=tuple(bindings["entities"]),
            source_revision_ids=tuple(
                r.id
                for r in snapshot.source_revisions
                if r.source_id in bindings["sources"]
            ),
            executed=bool(events),
            execution_count=len(events),
            provenance=("aphelion_deep.engine", "data/bindings.json"),
        )
        usages = [usage]
        if blockers:
            usages.append(
                SemanticUsage(
                    id="ad:blocked",
                    origin=SemanticOrigin.MISSING_AMBIGUOUS,
                    description=blockers[0].message,
                )
            )
        return SimulationRun(
            id="aphelion-run:"
            + content_digest(
                {
                    "snapshot": snapshot_content_digest(snapshot),
                    "config": config.model_dump(mode="json"),
                }
            )[:20],
            config=config,
            provenance=SimulationProvenance(
                snapshot_id=snapshot.id,
                snapshot_digest=snapshot_content_digest(snapshot),
                backend_version=version("playtrace"),
                plugin_id=self.id,
                plugin_version=self.version,
                config_digest=content_digest(config.model_dump(mode="json")),
                player_policy=config.player_policy,
                seeds=(config.seed,),
                runner=runner,
            ),
            initial_state=initial,
            final_state=final,
            events=tuple(events),
            state_trace=tuple(checkpoints),
            blockers=tuple(blockers),
            metrics=SimulationMetrics(
                turns_completed=completed,
                cards_resolved=sum(e.event_type == "card.revealed" for e in events),
                escalation_steps=engine.state["reactor"] if engine else 0,
                improves=0,
                worsens=0,
                maximum_tableau_cubes=0,
                blocker_count=len(blockers),
                player_actions=sum(e.event_type.startswith("player.") for e in events),
            ),
            semantic_audit=audit_semantics(
                tuple(usages), strict=config.strict_semantics
            ),
        )
