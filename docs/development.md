# Development Guidelines

[← Back to Documentation Hub](README.md) · [Project README](../README.md)

How to work on **diagrams-as-code** itself. Agent-facing rules are in [AGENTS.md](../AGENTS.md) (also reachable as `CLAUDE.md` and `GEMINI.md`); this page is the human-readable version. For internals read [architecture.md](architecture.md) first.

## Table of Contents
- [Ground rules](#ground-rules)
- [Setup](#setup)
- [Repository layout](#repository-layout)
- [Daily workflow](#daily-workflow)
- [Local-first verification](#local-first-verification)
- [Testing](#testing)
- [Architecture constraints](#architecture-constraints)
- [Generated artifacts](#generated-artifacts)
- [Documentation sync](#documentation-sync)
- [Commits, branches and releases](#commits-branches-and-releases)

## Ground rules

1. **Always use `uv`.** Never run bare `pip`, `python` or `pytest` outside it.
2. **Zero runtime dependencies.** The core engine is pure standard library; do not add to `dependencies = []` in `pyproject.toml` without an explicit decision. Dev-only tools go in the `dev` dependency group.
3. **Verify locally before pushing.** Remote CI minutes are constrained.
4. **Deterministic output.** Rendering the same input must give byte-identical SVG and BOM files.

## Setup

```bash
git clone https://github.com/bsommers/diagrams-as-code
cd diagrams-as-code
uv sync                    # creates .venv and installs the dev group (pytest, resvg-py)
```

Python 3.10 to 3.13 are exercised in CI. Docker is optional: `./docker-build-n-run.sh` or `docker compose run --rm diagram-gen`.

## Repository layout

| Path | Contents |
|---|---|
| `src/diagrams_as_code/` | The engine: geometry, elements, shapes, groups, constraints, router, theme, layout/, renderer_svg, rasterize, bom, output, cli |
| `src/iiot_diagrams/` | Backward-compatibility facade that re-exports the engine |
| `examples/` | Runnable diagram scripts, grouped by domain (ai, business_process, cloud, computer, cybersecurity, datacenter, iiot, network_engineering) |
| `icons/` | Source SVG icons, `icons.yaml` and `icons.csv` catalogs |
| `tools/` | `generate_icons.py`, `eval_bezier.py` |
| `output/` | Committed reference renders; must not drift |
| `tests/` | pytest suite, including module-boundary and repo-hygiene checks |
| `docs/` | Living documentation; `docs/plans`, `docs/reviews` and `docs/superpowers` are historical working notes |
| `legacy/` | Archived prototypes; do not build on them |
| `.planning/`, `.issues/` | Agent and planning notes; ignored by CI triggers |

## Daily workflow

1. Branch from the default branch; keep one logical change per branch.
2. Write or update a failing test first (`tests/`).
3. Implement the smallest change that passes.
4. Run the [verification gate](#local-first-verification).
5. Update docs in the same change ([sync checklist](#documentation-sync)).

## Local-first verification

Run all of these before pushing or opening a PR:

```bash
uv run pytest                                   # full suite must pass
uv run python main.py                           # regenerate reference output
uv run python tools/generate_icons.py --check   # icons match their catalog
git diff --exit-code -- output/ icons/ README.md docs/   # must produce no diff
```

Do not push WIP or intermediate commits; batch work and push only green changesets. Planning notes and agent files do not trigger CI (`paths-ignore` in `.github/workflows/`).

## Testing

- `tests/test_module_boundaries.py` enforces that imports point downward and that every module is classified. A new module must be added to its layer table.
- `tests/test_repo_hygiene.py` rejects case-only path collisions and tracked duplicate files.
- `tests/test_domain_examples.py` and `tests/test_examples.py` render every example and check for stacked or clipped elements.
- Layout, routing, theme, icon, BOM, CLI and renderer each have a dedicated test file.

Run a subset with `uv run pytest tests/test_routing.py -v`. Prefer asserting geometry and structure over comparing whole SVG strings.

## Architecture constraints

- Layering: geometry at the bottom, then elements/shapes/groups, constraints, layout and routing, then rendering and output, then CLI. Imports may only point down.
- Coordinates resolve at `solve()`; renderers must not mutate the model.
- Edge routing detail lives in `router.py`; layout strategies live under `layout/` (`LayeredLayout`, `GridLayout`, flow layouts).
- All text written into SVG must be XML-escaped.

Rationale and invariants: [architecture.md](architecture.md#6-key-architectural-invariants).

## Generated artifacts

`output/*.svg`, `output/*_README.md`, `icons/icons.csv` and `icons/README.md` are generated. Regenerate them with `uv run python main.py` and `tools/generate_icons.py`; never hand-edit. PNG output is opt-in and not byte-compared because backends differ.

## Documentation sync

| You changed | Update |
|---|---|
| CLI flags or commands | `docs/running.md`, `docs/user-guide.md`, `README.md`, `docs/CHANGELOG.md` |
| Public API, shape or edge options | `docs/user-guide.md`, `docs/how-to.md`, `docs/CAPABILITIES.md` |
| Modules or subsystems | `docs/architecture.md`, `docs/diagrams/`, the layer table in `tests/test_module_boundaries.py` |
| Themes, icons or example counts | `README.md`, `docs/CAPABILITIES.md`, `docs/capabilities.json`; derive counts, do not guess them |
| Behaviour or limits | `docs/purpose.md`, `docs/how-to.md` troubleshooting matrix |

Use relative links only. Mark old plans and reviews as historical rather than editing them to look current.

## Commits, branches and releases

- Imperative, scoped commit subjects (for example `fix(router): ...`, `docs: ...`).
- Record user-visible changes in `docs/CHANGELOG.md` with the commands you ran and their results.
- The version lives in `pyproject.toml`; bump it with the changelog entry.
- Confirm before pushing, tagging or other outward-facing actions.
