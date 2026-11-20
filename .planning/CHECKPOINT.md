# Checkpoint — v0.17.0 prepared on release/v0.17.0 — 2026-11-19
**Status:** local gate green; committed locally; NOT pushed, no PR, no tag. Waiting for the user's OK.

## Goal (user's words)
> "run the gate on master ; take care of loose-ends; tidy planning; decide on release - v0.17.0 and update refresh full documenation, examples, replace main README.md diagram with something more snazzy from our examples ; 4 - yes redraw"

## State of the world
- master = `5d27b28` (PR #28 merged). Latest tag v0.16.0 (on origin). v0.17.0 not tagged.
- Branch `release/v0.17.0` holds: MCP hardening (`src/diagrams_as_code/mcp.py`, `tests/test_mcp.py`), redrawn `examples/medical/01_heart_chambers.*`, README hero + gallery strip + counts, refreshed docs/ and examples/README.md, version 0.17.0 (pyproject, uv.lock, `__init__`, capabilities), CHANGELOG `[v0.17.0]`, new `CAP-MCP-SERVER`, planning refresh.

## Gate (run in the main tree on the branch)
- `uv run pytest` -> 1572 passed, 1 warning (expected LayoutWarning)
- `main.py` ok; `generate_icons.py --check` up to date; `audit_gallery.py --check` exit 0; `diagrams-as-code lint examples` exit 0
- `git diff --exit-code -- examples/ icons/` showed only the intended heart and examples/README changes (before commit)
- NOT run: Docker py3.10-3.13 matrix.

## Known limits (documented, not fixed)
- MCP: no timeout; a script can write to fd 1 or read stdin. Path confinement is not a sandbox. Planned fix: resource-limited subprocess.

## Next (needs the user's confirmation)
1. Push `release/v0.17.0`, open the PR, merge with a merge commit, tag `v0.17.0`.
2. Optionally run the Docker matrix first.
