---
last_mapped_commit: 24c06772a5a54fc91d84877ee767ee933a39e761
---

# Technology Stack

**Analysis Date:** 2026-09-22 (v0.4.0)

## Languages

**Primary:**
- Python 3.10+ - Pure Python standard library engine, layout, rendering, routing, CLI, and examples (`*.py`).

**Secondary:**
- Shell (Bash) - Container build and validation scripts (`docker-build-n-run.sh`).
- XML / SVG - Generated vector graphics format (W3C SVG 1.1 compliant).
- Markdown / JSON - Documentation, Bill of Materials (BOM), and capability manifests.

## Runtime

**Environment:**
- Python 3.10, 3.11, 3.12, 3.13 tested in CI.
- Multi-stage Docker container (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim` + `fonts-dejavu-core`).
- Zero external C-dependencies (no Graphviz `dot`, Cairo, or ImageMagick required for SVG rendering).

**Package Manager & Execution Tool:**
- `uv` (Astral) managing virtual environment (`.venv/`), lockfile (`uv.lock`), and execution (`uv run`).
- PEP 517 build backend via `hatchling` declared in `pyproject.toml`.

## Core Architectural Modules (Pure Python Stdlib)

- **`diagrams_as_code`**: Canonical package.
- **`iiot_diagrams`**: Backward-compatibility facade mirroring canonical exports.
- **`layout`**: Deterministic layered layout engine, graph builder, layout file sidecar, solve pipeline.
- **`geometry`**: Immutable 2D primitives, 9-point cardinal anchors, unit-basis coordinates.
- **`constraints`**: Relative positioning (right_of, left_of, below, above) & DAG solver.
- **`groups`**: Hierarchical containers, recursive auto-bounding, group flow placement.
- **`router`**: Manhattan orthogonal routing and automatic port deduction.
- **`theme`**: 13 theme presets (8 dark, 4 light, 1 high-contrast) and 60 vector icons.
- **`renderer_svg`**: Zero-binary SVG XML generator with multi-line wrapping and luminance contrast.
- **`rasterize`**: Multi-tier PNG fallback chain (resvg-py, CairoSVG, Inkscape, ImageMagick).
- **`output`**: Shared multi-format file writer (`render_all`).
- **`cli`**: Standalone CLI entrypoint (`diagrams-as-code` and `python -m diagrams_as_code`).

## Dependencies

**Runtime Dependencies:**
- `dependencies = []` (None. 100% Python standard library).

**Development Dependencies:**
- `pytest` (>=8.0) - Test suite runner.
- `resvg-py` (>=0.5.0) - Optional fast Rust-based SVG rasterizer for PNG generation.

**Test & QA Telemetry:**
- 431 automated tests passing across 100% test modules.
- Pre-commit & CI diff gate on `README.md`, `docs/`, `icons/`, `output/`.
