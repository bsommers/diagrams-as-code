---
last_mapped_commit: 24c06772a5a54fc91d84877ee767ee933a39e761
---

# Testing Strategy & Test Suites

**Analysis Date:** 2026-09-22 (v0.4.0)

## Overview

The test suite consists of 431 automated tests executing in ~12 seconds with 100% pass rate. It serves as both behavioral verification and regression guard for the 88 domain diagrams.

## Test Runner Command

```bash
uv run pytest
```

Fast quiet execution:
```bash
uv run pytest -q
```

## Test Directory Organization (`tests/`)

| Suite File | Coverage Scope | Count |
|---|---|:---:|
| `test_geometry.py` | 2D points, rects, anchors, unit basis coordinates | 6 |
| `test_constraints.py` | Relative constraints (right_of, below), DAG solver, cycles | 15 |
| `test_groups.py` | Hierarchical containers, auto-bounding, flows, child deltas | 23 |
| `test_model_prep.py` | Explicit IDs, lenient solve, bounding boxes | 6 |
| `test_layout_layered.py` | Sugiyama ranking, barycenter ordering, rank spacing | 13 |
| `test_layout_graph.py` | Scope graph extraction, edge lifting, pinned detection | 8 |
| `test_layout_pipeline.py` | Full solve pipeline, idempotency, canvas growth | 17 |
| `test_layout_routes.py` | Edge route pre-computation in layout stage | 3 |
| `test_layout_sidecar.py` | Layout JSON export, import, overrides, round-trip | 11 |
| `test_routing.py` | Port deduction, orthogonal Manhattan waypoints | 18 |
| `test_renderer_svg.py` | Standalone SVG XML validation, shapes, contrast | 18 |
| `test_theme.py` | 13 theme presets, custom icon registration, palettes | 25 |
| `test_rasterize.py` | Headless rasterizer fallback chain ordering | 3 |
| `test_output.py` | Multi-format file emission (SVG, PNG, BOM) | 3 |
| `test_bom.py` | BOM table generation and markdown export | 13 |
| `test_cli.py` | CLI parsing, render, layout export, exit codes | 11 |
| `test_diagram_api.py` | Fluent context manager, >> operators, clone | 18 |
| `test_public_api.py` | Parity between diagrams_as_code and iiot_diagrams facade | 5 |
| `test_domain_examples.py` | Execution and SVG validation of all 88 gallery diagrams | 88 |
| `test_examples.py` | Standalone example script executions | 4 |
| `test_e2e.py` | Full end-to-end integration flows | 6 |
| `test_icon_catalog.py` | Verification of 60 icons against ShapeLibrary catalog | 75 |
| `test_icon_glyphs.py` | Pre-compiled icon SVG paths | 2 |
| `test_icon_provenance.py` | Upstream icon attribution and license validation | 6 |
| `test_dependency_catalog.py` | Verification of all external dependencies in sources.md | 4 |
| `test_module_boundaries.py` | AST enforcement of layered architectural imports | 26 |
| `test_repo_hygiene.py` | Duplicate files and filename case sensitivity | 2 |
| **Total** | | **431** |

## Quality Gates in CI

1. `uv run pytest` across Python 3.10, 3.11, 3.12, 3.13.
2. Multi-stage Docker build with DejaVu fonts.
3. `uv run python tools/generate_icons.py --check`.
4. `git diff --exit-code -- README.md docs/ icons/ output/`.
