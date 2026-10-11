# AGENTS.md — The Aphelion Deep

You are working on **The Aphelion Deep**, a project written in the **GameSpec** family of
DSLs. This file tells you how to work here. Read it first.

## What this project is

- Base: **gamespec-core** (game = `gamespec-core`, prose = `storyspec-core`, world = `worldspec-core`).
- Extensions loaded: **cooperative, facilitation, briefings, cards, campaign** (the manifest `source/package.spec.yaml` is authoritative).
- The language it is written in lives in **`spec/`** — the vendored GameSpec DSL. Start with
  `spec/README.md`, then the relevant `spec/*_core_spec_v0_6.md` and the loaded extensions'
  `spec/extensions/<id>/spec.md`.

## Layout (see `spec/PROJECT_STRUCTURE.md`)

- `source/` — canonical truth: manifest, `game/` design modules, `mechanisms/` (Python),
  `components/` (card/data catalogue), `scenarios/`, `design/`, `proposals/`.
- `export/` — derived deliverables (rulebook, cards, PDFs). Never treat these as truth.
- `spec/` — read-mostly. **Do not edit the spec to fit this game.**

## Operating rules

1. **Canonical truth lives in `source/`.** Edit design there; regenerate exports, never hand-edit them.
2. **Bindings select; mechanisms transform.** Put outcome logic in `source/mechanisms/*.py`
   (the `gamespec` runtime is in `spec/runtime/`), not in the design YAML.
3. **Fiction is a dependency, not content.** Characters/places/setting truth belong to a
   WorldSpec dependency; reference them, do not restate them here.
4. **When the spec is missing something, do not bend the spec or fake it.** Write a
   **proposal** in `source/proposals/` per `spec/guides/spec_patches.md`. It documents the gap
   for this project and doubles as a feature proposal for the main spec.
5. **Declare incomplete work.** Use `unresolved:` / open items; never leave a dangling ref as a placeholder.

## Commands (run from the project root)

```bash
python3 spec/tools/spec_validator.py --package source/package.spec.yaml --extensions spec/extensions
python3 spec/tools/check_mechanism_refs.py source          # mechanism refs resolve to real Python
python3 source/mechanisms/tests/test_*.py                  # mechanism tests
python3 spec/tools/generate_cards.py source/components/cards.yaml export/cards.html
python3 spec/tools/check_materials.py source               # materials coverage + readability
```

## Definition of done for a change

- `source/` updated (design + mechanisms + components as needed);
- validator passes; mechanism refs resolve; mechanism tests pass;
- affected `export/` regenerated; material map still covers the rules;
- any spec gap encountered captured as a `source/proposals/` patch.
