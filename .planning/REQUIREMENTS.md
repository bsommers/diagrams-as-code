# Requirements: Technical Figures Program (v0.8.4 → v0.13.0)

**Defined:** 2026-11-12
**Core Value:** Zero external binary dependencies producing deterministic, publication-grade diagrams and technical figures from clean Python code.
**Source:** `docs/plans/2026-11-12-technical-figures-and-quality.md` (defect IDs R1–R14 are defined there)

## Requirements

### Phase 12 — Baseline & Bug Fixes

- [x] **FIX-01** (R1): Orthogonal routes arrive perpendicular to the target port; no final segment runs along a node border.
- [x] **FIX-02** (R2): Routes never pass through their own source or target.
- [x] **FIX-03** (R3): Self-loops are drawn as an external loop.
- [x] **FIX-04** (R4): A curve that still collides falls back to a rounded orthogonal route; any edge left colliding emits a `LayoutWarning`.
- [x] **FIX-05** (R5): Layout files with non-finite numbers are rejected.
- [x] **FIX-06** (R6): An explicitly passed layout file that does not exist is an error.
- [x] **FIX-07** (R7): Auto-layout spacing accounts for label and badge widths.
- [x] **FIX-08** (R8): Opposite edges between the same pair are offset, with separate badges.
- [x] **FIX-09** (R9): Adding or changing shapes and edges after a solve invalidates it.
- [x] **FIX-10** (R10): Re-solving keeps user changes to element size.
- [x] **FIX-11** (R11): Manual-waypoint edges take part in the style cascade.
- [x] **FIX-12** (R12): The BOM reports the resolved routing.
- [x] **FIX-13** (R13): CLI: no silent output overwrite, sibling imports work, `SystemExit` in a script is contained, correct blame for `-o`, empty input is reported.
- [x] **FIX-14** (R14): Rasterizer never returns a stale PNG; obstacles touching a port anchor are kept.
- [x] **AUDIT-01**: `tools/audit_gallery.py` counts visual defects across all examples and `--check` fails if any count exceeds the stored baseline.
- [x] **AUDIT-02**: The audit also counts edge-on-edge overlap, tangent arrivals and routes through own endpoints.

### Phase 13 — Text Engine

- [x] **TEXT-01**: Bundled font metric tables and a single `measure()` used by layout, badges, wrapping and rendering.
- [x] **TEXT-02**: Rich text runs (bold, italic, size, font role, baseline shift) with exact line boxes.
- [x] **TEXT-03**: Math markup inside `$…$`: sub/superscripts, grouping, Greek, operators, relations, `\mathrm`, `\text`, limits under big operators.
- [x] **TEXT-04**: Math glyphs drawn as vector outlines generated at development time from an open-licensed font; no runtime dependency.
- [x] **TEXT-05**: All labels accept the markup and explicit line breaks.
- [x] **TEXT-06**: Shapes grow to fit their text by default (`fit_label` / `fit_labels` to opt out, `font_size` to pin).

### Phase 14 — Style Model & Layout Correctness

- [x] **STYLE-01**: `Style` value object resolved theme → group → element; legacy `metadata` keys still work.
- [x] **STYLE-02**: `paper` theme.
- [x] **STYLE-03**: Renderer split into passes; dead route fallbacks removed.
- [x] **STYLE-04**: Fixed-precision coordinates; optional half-pixel alignment.
- [x] **LAYOUT-01**: Fit-to-content canvas with margin, on by default.
- [x] **LAYOUT-02**: Badges avoid nodes and other badges.
- [x] **LAYOUT-03**: Edges sharing a node side are spread across it.
- [x] **LAYOUT-04**: Labels do not overlap a shape's own artwork.

### Phase 15 — Technical Drawing Primitives

- [x] **PRIM-01**: `Text`, `Caption`, `Bracket`.
- [x] **PRIM-02**: `Polygon`, `Polyline`, `Path`.
- [x] **PRIM-03**: `Band` layer container (dashed, title, side notes).
- [x] **PRIM-04**: Shapes nested in shapes; double border.
- [x] **PRIM-05**: Edge stroke weight, arrowhead styles and sizes, two-way arrows.
- [x] **PRIM-06**: Edge endpoints at points and fractional anchors; shared-trunk fan-out; leaders; free splines; ellipsis connector.
- [x] **PRIM-07**: Projected solids (oblique, isometric) with hidden-edge dashing and translucent faces.
- [x] **PRIM-08**: Z-order control.
- [x] **PRIM-09**: `align()`, `distribute()`, grid snap, px/pt/mm lengths.

### Phase 16 — Technical Examples & Visual Regression

- [x] **EX-01**: Reproduction of the reference figure, slips corrected.
- [x] **EX-02**: Ten further technical figures.
- [x] **VIS-01**: Golden-image regression tests.
- [x] **VIS-02**: `diagrams-as-code lint`.
- [x] **DOC-01**: Technical-figures guide and math markup reference.

### Phase 17 — Vector PDF Export

- [ ] **PDF-01**: Pure-stdlib PDF writer covering paths, fills, dashes, arrowheads and opacity.
- [ ] **PDF-02**: Text and math in PDF match the SVG.
- [ ] **PDF-03**: `Diagram.render_pdf()` and CLI `--format pdf`.

## Deferred

- Fuller math (fractions, radicals, matrices).
- EDGE-01 curvature tuning, EDGE-02 bridge jumps, EDGE-03 edge bundling (carried from v0.8.0).

## Out of Scope

| Feature | Reason |
|---|---|
| Runtime dependencies of any kind | Core architectural rule |
| Full TeX layout | Far beyond what figures need |
| Literal copy of the reference's errors | Decided 2026-11-12: match style and structure, correct slips |
