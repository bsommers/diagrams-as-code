# Plan: Quality Pass and Publication-Grade Technical Figures

**Status:** APPROVED 2026-11-12 (decisions in section 4). Tracked in `.planning/ROADMAP.md` as Phases 12–17.
**Date:** 2026-11-12
**Baseline:** v0.8.3, `master` @ e1f3896, 572 tests passing

## Goal

1. Fix the bugs and visual defects the engine ships today.
2. Make the engine able to produce precise, paper-style technical figures like the
   reference (`Gemini_Generated_Image_ujvhivujvhivujvh.jpeg`: four dashed layer bands,
   sharp black-on-white boxes, typeset math, 3D solids, leader lines, figure caption).
3. Add a technical-figure example set, including a reproduction of the reference.

Constraints carried over: pure standard library at runtime, `uv` for everything,
`src/iiot_diagrams` facade keeps working, local-first verification, no intermediate pushes.

---

## 1. What the review found

### 1.1 Measured gallery defects (all 92 example diagrams, solved and inspected)

| Defect | Count | Diagrams affected |
|---|---|---|
| Canvas more than 40% empty (no fit-to-content) | 90 | 90 of 92 |
| Edge label badge drawn over a node | 95 | 36 |
| Edge label badge overlapping another badge | 37 | 27 |
| Node label taller than its box | 29 | 21 |

Seen by eye in rendered output, not yet counted:

- Two edges sharing one port run on top of each other (`ai/08`: "Verified Safe Response"
  leaves the same port "Draft Response" enters, and strikes through that badge).
- An edge arrives along a node's border instead of into it (`ai/08`, top-left node).
- A label is drawn across the shape's own artwork (`04_curves_and_fillets`: "Primary DB"
  over the database tiers; the cloud icon over the cloud outline).

### 1.2 Code defects

Router, layout and CLI, from a separate review pass. Each was reproduced with a script
unless marked; I re-ran R3 and R9 myself and have not independently re-run the others.

| # | Where | Defect |
|---|---|---|
| R1 | `router.py:1002-1047` | Orthogonal detour ignores the target port's direction, so the last segment runs along the node border with a tangent arrowhead. 48 of 498 gallery edges. |
| R2 | `router.py:720-727`, `888-906`, `208-235` | Routes back through their own source or target: ports are chosen from centre deltas and endpoints are never obstacles. Hits `04_curves_and_fillets` ("Auth Service" → "Primary DB"). |
| R3 | `router.py:721` | A self-loop (`connect(a, a)`) draws a straight line across the node. |
| R4 | `router.py:652`, `703` | Curve router silently returns splines that still collide (27 of 3116 fuzzed edges crossed another node). |
| R5 | `layout/sidecar.py:47`, `61` | Layout file accepts `NaN`/`Infinity`; the SVG then contains `nan` and an infinite canvas height. |
| R6 | `layout/sidecar.py:44-45` | A mistyped `--layout-file` path is silently ignored, exit 0. |
| R7 | `layout/graph.py:95-101`, `layered.py` | Auto-layout ignores label and badge widths: long labels clip at the canvas edge and overlap neighbours. |
| R8 | `router.py:720-727` | A→B and B→A get the identical path and the identical badge position. |
| R9 | `diagram.py` | Adding a shape or edge after the first solve does not invalidate it: the shape stays at (0,0) and the edge has no route. |
| R10 | `layout/pipeline.py:140-145` | Re-solving restores first-solve sizes, discarding a later `shape.width = …`. |
| R11 | `layout/pipeline.py:108`, `router.py:1178` | Edges with manual waypoints skip the diagram-level style cascade (`corner_radius` comes out 0). |
| R12 | `connections.py:131-141`, `bom.py:57` | BOM reports `Diagram(routing="direct")` edges as "orthogonal". |
| R13 | `cli.py:125`, `136-140`, `180-196` | Same-named scripts overwrite each other's output; sibling helper imports fail; `sys.exit()` in one script aborts the batch; `-o` errors blame the script; empty directory exits 0 silently. |
| R14 | `rasterize.py:36`, `router.py:844-845` | Inferred only: stale PNG returned if a converter exits 0 without writing; obstacles touching a port anchor are dropped. |

Still open from the 2026-09-28 routing review: the `min_top <= 30` canvas guess,
north-only escape corridor (P1.2), mirrored corridor code (P1.3), handle clamping (P1.5),
conservative `intersects_rect` (P1.6), no gallery routing-invariant test (P2.1), and
`routes` keyed under both `edge` and `id(edge)`.

Renderer and model, from my own reading:

- `renderer_svg.py` applies the drop shadow to every node unconditionally, hard-codes
  edge stroke width (2), group corner radius (8), all font sizes and weights. None of it
  is reachable from `Theme` or per-element style.
- Text width is guessed as `0.62 × font_size` per character in three separate places
  (`render_badge`, the badge sizing in `render`, `wrap_text` budgets). Layout and drawing
  can disagree, which is the root of the overflow and badge-overlap counts above.
- `render()` is one 470-line method with six fallback branches for finding an edge's path;
  after Phase 11 the pipeline always supplies `routes`, so most of those are dead weight.
- `.planning/STATE.md` says Phase 11 is "ready to plan"; git shows it merged
  (PRs #16–#18). The GSD state is stale.
- `CHANGELOG.md` / `CAPABILITIES.md` exist in both the root and `docs/` and must be kept
  in sync by hand.

### 1.3 Gap to the reference figure

| Reference feature | Today | Needed |
|---|---|---|
| Math: italic variables, sub/superscripts, ∀ ∧ ⊆ ∩ Ω Π, limits under ⋂ | Plain escaped strings only | Rich text runs plus a small math markup |
| Text sized and placed exactly | Character-count guess | Real font metric tables |
| Free text annotations, bold headings, italic notes | Every label belongs to a box | Standalone text element with alignment |
| Thin sharp black boxes, no shadow, grey panels | Rounded, shadowed, 2px accent stroke | Style model and a `paper` theme |
| Dashed layer bands with a title and side notes | Solid rounded group, fixed header | Band container with dash, title and note slots |
| Nested and double-bordered boxes | Not expressible | Shapes as children of shapes, inset border |
| 3D cuboid, polyhedron, clipping plane, hidden dashed edges | None | Polygon/path primitives plus a projection helper |
| Heavy spine arrows, thin leaders, two-way arrows, free curves | One stroke width, one arrowhead, node-to-node only | Per-edge weight, arrowhead styles, point endpoints |
| Lines attached anywhere on a box edge | Four ports (N/S/E/W midpoints) | Fractional anchors |
| "FIGURE 1: …" caption | None | Caption element |
| Small-caps serif caption, serif italic math | One sans font stack | Font roles per theme |

### 1.4 One technical risk found while prototyping

I rendered a test SVG with italic serif `<tspan>` runs through the PNG backend
(`resvg-py`). Subscripts worked; the italic and serif switches were ignored and everything
came out upright sans. So "let the viewer pick the fonts" will not give reliable math.
Milestone 2 starts with a short spike to settle this; my expected answer is in section 4.

---

## 2. Milestones

Each milestone ends green: `uv run pytest`, `uv run python main.py`,
`uv run python tools/generate_icons.py --check`, clean `git diff` on generated output, and
a visual check of rendered PNGs by me. One PR per milestone, pushed only when verified.

### M1 — v0.8.4: Baseline and bug fixes

- Fix the code defects in 1.2 (router and layout items first), each with a failing test first.
- Turn the defect audit into `tools/audit_gallery.py` and a test that fails if any count
  rises. Counts can only ratchet down from here.
- Add the two unmeasured checks (edges overlapping edges, labels over shape artwork).
- Bring `.planning/` up to date (close Phase 11 and v0.8.0, open the new milestones).

**Done when:** every listed code defect has a regression test; audit runs in CI's test job.

### M2 — v0.9.0: Text engine

- Spike (half a day): decide the font strategy (section 4, decision A).
- `text/metrics.py`: width tables for the chosen fonts; one `measure()` used by layout,
  badges, wrapping and the renderer. Delete the three `0.62` guesses.
- `text/rich.py`: styled runs (bold, italic, size, family role, baseline shift) and line
  layout with exact bounding boxes.
- `text/math.py`: a LaTeX-like subset inside `$…$`: `_`, `^`, `{}`, Greek letters,
  operators and relations, `\mathrm`, `\text`, limits under big operators. Not full TeX:
  no fractions-in-fractions, matrices or radicals in this milestone.
- Labels everywhere accept the markup; explicit `\n` line breaks are honoured.
- Nodes can size themselves to their text (`width="fit"`), which clears the overflow count.

**Done when:** every formula in the reference renders correctly in SVG and PNG; label
overflow count is 0; measured width matches rendered width within 1px on test strings.

### M3 — v0.10.0: Style model and layout correctness

- `Style` value object (fill, stroke, stroke width, dash, radius, shadow, opacity, font
  role and size) resolved theme → group → element, the same way routing options already
  cascade. `metadata["fill"]`-style keys keep working.
- `paper` theme: white, 1px black strokes, square corners, no shadow, serif caption font.
- Fit-to-content canvas with a margin (default for new diagrams; see decision C).
- Badge placement that avoids nodes and other badges; slide along the edge, then offset.
- Port spreading so edges sharing a side do not overlap; arrows enter perpendicular.
- Split `SVGRenderer.render` into group, edge, node and text passes; remove dead fallbacks.
- Coordinates emitted with fixed precision; optional half-pixel alignment for 1px strokes.

**Done when:** all four audit counts are 0 across the gallery; existing themes look
unchanged apart from the fixes (checked by image diff, reviewed by eye).

### M4 — v0.11.0: Technical drawing primitives

- `Text` element (no box), `Caption`, `Bracket`, `Polygon`, `Polyline`, `Path`.
- `Band`: dashed layer container with title, optional side-note column, inner content area.
- Nesting shapes in shapes; `double` border option.
- Edges: stroke weight, arrowhead styles and sizes, two-way arrows, endpoints at arbitrary
  points or fractional anchors (`box.anchor("right", 0.25)`), shared-trunk fan-out,
  leader lines with a text end, free splines through given points, ellipsis connector.
- `solids.py`: oblique and isometric projection of boxes and convex polyhedra, with
  visible/hidden edge classification (hidden edges dashed) and translucent faces.
- Z-order control.
- Alignment helpers: `align()`, `distribute()`, grid snap, lengths in px/pt/mm.

**Done when:** each primitive has unit tests and one focused example; module-boundary
tests still pass (primitives are Layer 0/1, no renderer imports).

### M5 — v0.12.0: Technical example set and visual regression

- `examples/technical/01_composition_enforcement.py`: the reference figure.
- Ten more: control loop with transfer functions, transformer block, state machine,
  protocol stack, memory layout, timing diagram, pipeline with equations, 3D tensor
  shapes, geometric construction, system model with constraint region.
- Golden-image regression: rendered PNG compared to a stored golden with a tolerance,
  so visual changes show up in review. Uses the existing dev-only `resvg-py`.
- `diagrams-as-code lint <script>`: runs the audit on a user's own diagram.
- Docs: user-guide chapter on technical figures, math markup reference, gallery update.

**Done when:** the reproduction sits beside the reference and matches it element for
element (checklist in the PR); lint reports zero defects on all examples.

### M6 — v0.13.0: Vector PDF export

- Pure standard-library PDF writer: paths, fills, dashes, arrowheads, opacity.
- Text and math placed from the same metrics and outlines as the SVG, so both match.
- `Diagram.render_pdf()` and CLI `--format pdf`.

**Done when:** every technical example exports to a PDF that opens in standard viewers
and matches its SVG; no runtime dependency added.

### Later

- Fuller math: fractions, radicals, matrices.

---

## 3. About reproducing the reference

The reference is AI-generated and has slips: "Sinks and sources flow boundary limits"
appears twice, "Taint Tracking Tracker", a few leader lines that point at nothing, and an
unexplained outer rectangle behind "Registered Intent". The reproduction matches its structure and
style and corrects those slips.

---

## 4. Decisions (made 2026-11-12)

- **Fonts:** math glyphs are vector outlines generated at development time from an
  open-licensed math font; ordinary text stays live SVG text measured from bundled metrics.
- **Gallery output:** fit-to-content is on by default; all gallery output is regenerated
  once in M3.
- **Reference slips:** match structure and style, correct the slips.
- **PDF export:** in scope, as M6.
- **Versions:** stay on 0.x (plan ends at v0.13.0).
- **GSD:** used for roadmap, requirements, state and atomic commits. Research, plan-check
  and Nyquist steps are off. The gallery audit, golden images and looking at renders are
  written into the phase gate in `.planning/ROADMAP.md`.

---
