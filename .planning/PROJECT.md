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
- [x] Standalone CLI `--interactive` flag, client-side search/highlight filter, and viewport minimap navigator (`v0.6.0`).
- [x] Obstacle-aware orthogonal Manhattan routing with clearance corridors and multi-rank crossing minimization (`v0.7.0`).

## Current Milestone: v0.8.0 Curved & Bezier Edge Routing Engine

**Goal:** Provide deterministic, publication-quality cubic Bezier and curved edge routing with obstacle deflection, rounded corner fillets for orthogonal paths, and unified diagram/edge routing controls with zero external dependencies.

**Target features:**
- Cubic Bezier curve routing with port tangent vector calculation and control point generation (`Routing.CURVE`).
- Rounded corner fillets (`arc_radius`) on orthogonal Manhattan routing paths (`Routing.ORTHOGONAL`).
- Obstacle-aware Bezier splines routing through intermediate avoidance waypoints.
- Diagram-level default routing configuration (`Diagram(routing=...)`) and per-edge override (`Edge(..., routing=...)`).
- SVG renderer support for cubic Bezier path (`C`) commands and fillet arcs (`A`/`Q`).

### Out of Scope

- External runtime dependencies (`dependencies = []` in `pyproject.toml` remains strictly empty).
- Declarative JSON/YAML diagram specification (diagrams remain pure Python code).
- Dynamic interactive physics-based force-directed simulation (diagrams are statically compiled SVG).

## Context

- Evolved from legacy mingrammer/diagrams Graphviz wrapper into an independent pure-Python directed engine.
- 88 gallery reference diagrams across 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`).
- Shipped `v0.7.0` with obstacle-aware routing and crossing minimization.

## Constraints

- **Tooling:** Always use `uv` for all environment management, script execution, and testing.
- **Dependencies:** Strictly zero runtime dependencies. Stdlib only.
- **Verification:** Pre-commit and CI diff gate on `README.md`, `docs/`, `icons/`, `output/`.
- **Compatibility:** Tested and passing on Python 3.10, 3.11, 3.12, and 3.13.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

## Key Decisions

- 2026-09-21: Rename canonical root package to `diagrams_as_code`; maintain `iiot_diagrams` as facade.
- 2026-09-22: Route edges in layout stage (`layout/pipeline.py`) so renderer only draws.
- 2026-09-22: Unconditional canvas growth applies across all layout modes (`manual`, `auto`, layout file).
- 2026-09-22: Commit trailers truthfully attribute the model that performed the work.
- 2026-09-22: Transition planning workflow from superpowers to GSD (`.planning/`).
- 2026-09-24: Add obstacle avoidance and detour channel search to orthogonal router.
- 2026-09-24: Implement cubic Bezier curves and rounded orthogonal fillets for v0.8.0.

---
*Last updated: 2026-09-24 for Milestone v0.8.0*

