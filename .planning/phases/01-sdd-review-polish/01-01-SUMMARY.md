---
phase: 01-sdd-review-polish
plan: 01
subsystem: layout-cli-hygiene
tags: [cli, graph, pipeline, router, hygiene]
provides:
  - CLI upfront --out path validation reporting exit code 2 when pointing to an existing file
  - Graph builder memoization for enclosing IDs in pinned_ids
  - Direct Edge.waypoints attribution and layout pipeline assignment
  - Cleaned up unused Diagram import in test_dependency_catalog and alphabetized diagram.py imports
affects: [02-architectural-followups]
tech-stack:
  added: []
  patterns: [memoized-traversal, direct-attribute-assignment, upfront-cli-validation]
key-files:
  created: []
  modified:
    - src/diagrams_as_code/cli.py
    - src/diagrams_as_code/connections.py
    - src/diagrams_as_code/diagram.py
    - src/diagrams_as_code/layout/graph.py
    - src/diagrams_as_code/layout/pipeline.py
    - src/diagrams_as_code/renderer_svg.py
    - tests/test_cli.py
    - tests/test_dependency_catalog.py
    - tests/test_layout_routes.py
key-decisions:
  - "Maintain diagram.routes[id(edge)] dictionary for backwards compatibility alongside direct edge.waypoints"
duration: 15min
completed: 2026-09-23
status: complete
---

# Phase 1: SDD Review Polish & Edge Robustness Summary

**Executed deferred minors from auto-layout/CLI review: CLI --out error targeting, graph traversal memoization, direct edge waypoints, and import hygiene.**

## Accomplishments
- **CLI --out check:** If `--out` points to an existing file, the CLI reports `error: --out: <path> is an existing file, not a directory` with exit code 2 without attempting to discover and execute scripts.
- **Graph memoization:** `pinned_ids` in `layout/graph.py` memoizes `_enclosing_ids` lookups for relative constraint targets, preventing repetitive ancestor walks.
- **Edge waypoints:** `Edge` now has `self.waypoints: Optional[list[Point]] = None`. `pipeline.py` computes routes and assigns them directly to each edge; `renderer_svg.py` checks `e.waypoints` first.
- **Import hygiene:** Removed unused `Diagram` import in `tests/test_dependency_catalog.py` and restored alphabetical import ordering in `diagram.py`.

## Verification
- `uv run pytest`: 432 passed in 11.66s (1 new test).
- `git diff --exit-code -- output/ icons/ README.md docs/`: clean.
