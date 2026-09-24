# Diagrams as Code (Directed IIoT & Architecture Engine)

## What This Is

A pure-Python directed diagramming engine featuring deterministic layered auto-layout, Manhattan orthogonal edge routing, 13 theme presets, 60 vector icons across 8 domains, a standalone CLI (`diagrams-as-code`), and automated living Bill of Materials (BOM) documentation.

## Core Value

Zero external binary dependencies (no Graphviz `dot`, Cairo, or ImageMagick required for SVG rendering) producing deterministic, publication-quality architecture diagrams from clean Python code.

## Requirements

### Validated

- [x] Pure-Python SVG vector renderer with drop shadows, arrowheads, multi-line `<tspan>` wrapping, and contrast text coloring (`v0.1.0`).
- [x] Decoupled shape lifecycle, 9-point cardinal anchors, normalized unit-basis coordinates, and DAG constraint solver (`v0.1.0`).
- [x] Orthogonal Manhattan routing with automatic cardinal port deduction and collinear line simplification (`v0.1.0`).
- [x] Hierarchical groups with bottom-up auto-bounding and child coordinate delta propagation (`v0.1.0`).
- [x] Living documentation and BOM table export (Markdown + JSON) (`v0.1.0`).
- [x] 13 theme presets and 60 vector icons across 8 domains (`v0.2.0` / `v0.3.0`).
- [x] Canonical package rename to `diagrams_as_code` with backward-compatible `iiot_diagrams` facade (`v0.3.0`).
- [x] Deterministic layered auto-layout (`layout="auto"`, `direction="LR"`|`"TB"`) (`v0.4.0`).
- [x] Editable JSON layout file export and override application (`v0.4.0`).
- [x] Standalone `diagrams-as-code` CLI with `render`, `layout export`, `themes`, `icons` (`v0.4.0`).
- [x] Unconditional canvas growth on content overflow (`v0.4.0`).
- [x] Enforced layered module boundaries via AST import tests (`v0.4.0`).
- [x] Typed constraint dataclasses (`AbsoluteConstraint`, `RelativeConstraint`, `AlignConstraint`) with multi-axis alignment (`v0.5.0`).
- [x] Pluggable group flow layout engines (`VerticalFlowLayout`, `HorizontalFlowLayout`, `GridLayout`) decoupled from `Group` (`v0.5.0`).
- [x] Client-side interactive SVG pan/zoom and collapsible group header toggles with zero external runtime dependencies (`v0.5.0`).
- [x] Local-first testing directives and GitHub Actions CI quota conservation controls (`v0.5.0`).

### Active Scope (Next Milestone: v0.6.0)

- [ ] **CLI Interactive Export (`CAP-DIAG-CLI-INTERACTIVE`)**: Expose `--interactive` CLI flag for `diagrams-as-code render` and batch exports.
- [ ] **Interactive Enhancements**: Minimap viewport navigator, search/highlight node filters, and smooth CSS transitions on group toggles.
- [ ] **Layout Refinements**: Compound group edge routing optimizations and ranking adjustments.

### Out of Scope

- External runtime dependencies (`dependencies = []` in `pyproject.toml` remains strictly empty).
- Declarative JSON/YAML diagram specification (diagrams remain pure Python code).
- Complex obstacle-avoiding edge routing (v1 Manhattan orthogonal routing remains canonical).

## Context

- Evolved from legacy mingrammer/diagrams Graphviz wrapper into an independent pure-Python directed engine.
- 88 gallery reference diagrams across 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`).
- Shipped `v0.5.0` with 439 unit/integration tests passing in ~11 seconds.

## Constraints

- **Tooling:** Always use `uv` for all environment management, script execution, and testing.
- **Dependencies:** Strictly zero runtime dependencies. Stdlib only.
- **Verification:** Pre-commit and CI diff gate on `README.md`, `docs/`, `icons/`, `output/`.
- **Compatibility:** Tested and passing on Python 3.10, 3.11, 3.12, and 3.13.

## Key Decisions

- 2026-09-21: Rename canonical root package to `diagrams_as_code`; maintain `iiot_diagrams` as facade.
- 2026-09-22: Route edges in layout stage (`layout/pipeline.py`) so renderer only draws.
- 2026-09-22: Unconditional canvas growth applies across all layout modes (`manual`, `auto`, layout file).
- 2026-09-22: Commit trailers truthfully attribute the model that performed the work.
- 2026-09-22: Transition planning workflow from superpowers to GSD (`.planning/`).
