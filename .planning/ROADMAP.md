# Roadmap: Technical Figures Program (v0.8.4 → v0.13.0)

Full rationale, review findings and decisions: `docs/plans/2026-11-12-technical-figures-and-quality.md`.

## Milestone History

- **[v0.8.0](milestones/v0.8.0-ROADMAP.md)** — Phases 8–11: curved and Bezier edge routing, fillets, obstacle deflection, routing configuration hierarchy.
- **[v0.7.0](milestones/v0.7.0-ROADMAP.md)**, **[v0.6.0](milestones/v0.6.0-ROADMAP.md)**, **[v0.5.0](milestones/v0.5.0-ROADMAP.md)** — earlier milestones.

## Overview

Fix the defects the engine ships today, then make it able to produce precise, paper-style technical figures (typeset math, sharp monochrome boxes, dashed layer bands, 3D solids, leader lines, captions), with a technical example set and vector PDF export. Runtime stays pure standard library.

## Phase gate (applies to every phase)

A phase is not done until all of these pass locally:

1. `uv run pytest`
2. `uv run python main.py` and `uv run python tools/generate_icons.py --check`
3. `uv run python tools/audit_gallery.py --check` — visual defect counts must not rise above `tools/audit_baseline.json` (available from Phase 12)
4. Golden-image comparison passes or goldens are deliberately regenerated (available from Phase 16)
5. Rendered PNGs of changed diagrams are looked at, not only tested
6. `git diff --exit-code -- output/ icons/ README.md docs/` after regeneration

Process: one plan per phase, no separate research / plan-check / Nyquist documents. One PR per phase, pushed only when the gate is green.

## Phases

- [x] **Phase 12 (v0.8.4): Baseline & Bug Fixes** — router, layout, CLI and model defects fixed test-first; gallery defect audit added as a ratchet.
- [x] **Phase 13 (v0.9.0): Text Engine** — font metrics, rich text runs, math markup with outline glyphs from an open-licensed font, fit-to-text sizing.
- [ ] **Phase 14 (v0.10.0): Style Model & Layout Correctness** — `Style` cascade, `paper` theme, fit-to-content canvas, badge and port collision fixes, renderer split.
- [ ] **Phase 15 (v0.11.0): Technical Drawing Primitives** — text, caption, bands, nesting, polygons, projected solids, arrow styles, leaders, fractional anchors, alignment helpers.
- [ ] **Phase 16 (v0.12.0): Technical Examples & Visual Regression** — reference reproduction plus ten technical figures, golden images, `lint` command, docs.
- [ ] **Phase 17 (v0.13.0): Vector PDF Export** — pure-stdlib PDF writer for all primitives and text.

## Phase Details

### Phase 12: Baseline & Bug Fixes

**Requirements:** FIX-01 … FIX-14, AUDIT-01, AUDIT-02
**Success criteria:**
1. Every defect R1–R13 in the plan has a regression test that failed before the fix.
2. `tools/audit_gallery.py --check` runs in the test suite and fails when any defect count rises.
3. No gallery edge ends tangent to its target or passes through its own endpoints.

### Phase 13: Text Engine

**Requirements:** TEXT-01 … TEXT-06
**Success criteria:**
1. Every formula in the reference figure renders correctly in SVG and PNG, identically across viewers.
2. One `measure()` function is the only source of text width; measured vs rendered width within 1px.
3. Node label overflow count is 0 across the gallery.

### Phase 14: Style Model & Layout Correctness

**Requirements:** STYLE-01 … STYLE-04, LAYOUT-01 … LAYOUT-04
**Success criteria:**
1. All audit counts are 0 across the gallery.
2. A `paper`-themed diagram has no shadows, 1px strokes and square corners with no per-element overrides.
3. Existing themes are visually unchanged apart from the fixes.

### Phase 15: Technical Drawing Primitives

**Requirements:** PRIM-01 … PRIM-09
**Success criteria:**
1. Each primitive has unit tests and one focused example.
2. Module-boundary tests still pass.

### Phase 16: Technical Examples & Visual Regression

**Requirements:** EX-01, EX-02, VIS-01, VIS-02, DOC-01
**Success criteria:**
1. The reference reproduction matches the reference element for element (checklist in the PR), with its slips corrected.
2. Golden-image tests cover every technical example; `lint` reports zero defects on all examples.

### Phase 17: Vector PDF Export

**Requirements:** PDF-01 … PDF-03
**Success criteria:**
1. `render_pdf()` output for every technical example opens in standard viewers and matches the SVG.
2. No runtime dependency added.
