---
gsd_state_version: "1.0"
milestone: v0.8.4
milestone_name: → v0.13.0)
status: ready_to_plan
stopped_at: Phase 16 complete (v0.12.0) on branch feat/phase16-technical-examples (stacked on feat/phase15-drawing-primitives, PR 20), gate green, 935 tests, lint 0 findings; PR 19 merged; Phase 16 branch not pushed; no tags; Phase 17 not started
last_updated: "2026-11-13T12:00:00.000Z"
state_head: 338b56095d23021d4ae337698a68bf6666be855f
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 0
  completed_plans: 0
  percent: 67
last_activity: 2026-11-13
current_phase: 17
current_phase_name: Vector PDF Export
last_activity_desc: Phase 16 complete - eleven technical figures, lint command, golden images, technical-figures guide and math reference (935 tests)
---

# Project State

## Project Reference

See `.planning/PROJECT.md`, `.planning/ROADMAP.md`, and the approved plan
`docs/plans/2026-11-12-technical-figures-and-quality.md`.

**Current focus:** Phase 17 — Vector PDF Export. Phases 12–14 (v0.8.4, v0.9.0, v0.10.0) are merged to master via PR #19. Phase 15 (v0.11.0) is PR #20 from `feat/phase15-drawing-primitives`. Phase 16 (v0.12.0) is complete on `feat/phase16-technical-examples`, stacked on the Phase 15 branch and not yet pushed. Tags follow the merges.

## Phase 12 result

Audit across 92 diagrams, before -> after: tangent arrivals 47 -> 0, edges through own endpoint 1 -> 0, overlapping edges 48 -> 22, edges through a badge 196 -> 188, badges over nodes 95 -> 80, badges over badges 37 -> 28. Unchanged and owned by later phases: label overflow 29 (Phase 13), mostly-empty canvas 90 and the remaining badge/overlap counts (Phase 14).

## Phase 13 result

Audit, v0.8.4 -> v0.9.0: label overflow 29 -> 0, badges over nodes 80 -> 21, badges over badges 28 -> 16, edges through a badge 188 -> 183. Remaining for Phase 14: overlapping edges 22, mostly-empty canvas 90, the remaining badge counts, and labels drawn over a shape's own artwork (server rack, database, cloud).

Font spike outcome: the PNG backend (resvg-py) does honour italic, bold, serif and `textLength`. The earlier failed prototype was caused by a quoted family name inside a tspan fallback list, not a backend limit. Math is still drawn as outlines (STIX Two Math, OFL 1.1) for viewer independence and symbol coverage.

Behaviour change to be aware of: shapes now grow when their label cannot fit (`fit_label=False` / `Diagram(fit_labels=False)` restores fixed sizes). One existing test needed `fit_label=False`; three renderer tests that asserted exact text markup were loosened to assert intent.

Phase 14 outcome (v0.10.0, `338b560`): STYLE-01..04 and LAYOUT-01..04 done. Audit, v0.9.0 -> v0.10.0: mostly-empty canvas 90 -> 0 (root cause: 1200x800 default that could only grow), overlapping edges 22 -> 0, badges over nodes 21 -> 0, badges over badges 16 -> 0, edges through a badge 183 -> 4, title overflow 29 -> 0 (new check). The `paper` theme uses the Arial-compatible stack.

Carried into Phase 15: the five remaining audit defects (4 edges through a badge in computer/01, datacenter/01, network_engineering/09; 1 edge through a group title in cloud/06), per-diagram font-size consistency (sibling nodes can get 13px and 12px labels), edges crossing unrelated group frames in tight hand-placed examples (not yet an audit count).

## Phase 15 result

v0.11.0. PRIM-01..09 done: `drawing.py` (backend-neutral path and text items, SVG path parser, arrowheads), `solids.py` (projection, hidden edges, hull, sections), `primitives.py` (Text, Caption, Bracket, Polygon, Polyline, Path, SolidShape, Band), `arrange.py` (align, distribute); nesting via `shape.inside()`, `Style(double=, fill_opacity=)`, edge `width/head/tail/arrow_size/two_way/ellipsis/via/trunk/z`, `box.anchor(side, fraction)`, point endpoints and `Junction`, `Routing.SPLINE`, `Diagram(grid=)`, unit lengths. Nine examples in `examples/primitives/`. 881 tests on Python 3.10 and 3.14. Audit across 101 diagrams: all zero (the five carried defects were fixed by widening three hand-placed examples and raising one edge's clearance).

Design points Phase 16 and 17 rely on: every primitive draws itself as `PathItem`/`TextItem` with absolute M/L/C/Z commands (the PDF writer needs only those); ordinary shapes and default edges still emit SVG strings directly and will need the same treatment in Phase 17. Edges with default weight and head still use SVG markers, whose tip overshoots the endpoint by a fifth of the head; custom edges draw exact heads.

Known limits: serif text is measured with the sans metrics and pinned with `textLength`; a cutting plane is drawn over the whole solid rather than hidden behind its near faces; overlapping 1 px trunk lines look heavier unless `pixel_snap=True`; `tests/test_domain_examples.py` still hard-codes 88 scripts / 8 domains (now scoped to those domains).

## Phase 16 result

v0.12.0. EX-01, EX-02, VIS-01, VIS-02, DOC-01 done. `examples/technical/01..11` (the reference reproduction and ten more), each lint-clean with a golden image in `tests/golden/technical/`. `audit.audit_findings()` returns named `Finding`s; `diagrams-as-code lint` prints them and exits 1 on any. `tools/golden_images.py` renders at 800 px with only the fonts in `tests/fixtures/fonts` (Latin subset of Arimo, OFL 1.1) and compares within a tolerance; the renders were byte-identical on macOS arm64, Linux arm64 and Linux x86-64. Docs: `docs/technical-figures.md`, `docs/math-markup.md`. 935 tests.

Engine fixes found by writing the figures: `\n` inside math was treated as a line break (`\nabla`, `\neq`, `\nu`); a caption wider than the drawing was clipped on the left. Audit now exempts a line ending at a bare point inside a shape, a bracket beside shapes nested in a panel, and free outlines (path, polygon, polyline).

Gaps the figure authors worked around, candidates for later: no circle/ellipse shape kind (an unknown `kind` silently draws a box); no self-loop helper; no text-beside-the-line edge label (figures place `text()` by hand); anchor names `left_center`/`right_center` versus `top_center` with no aliases; no math accents (`\hat`, `\bar`, `\overline`), `\mathcal`, `\triangle`; no monospace text; no dimension-line or circle/arc helper; projected solid corners are not exposed for attaching lines; the audit tests a solid's bounding rectangle, not its outline; a translucent filled outline declared before edges is painted over them unless given `z=-1`; edge-label badge text size is not adjustable.

## Decisions

- 2026-11-12: v0.8.0 milestone closed; Phase 11 was merged via PRs #16–#18 while this file still said "ready to plan".
- 2026-11-12: Fonts — math as vector outlines generated from an open-licensed font; ordinary text stays live SVG text measured from bundled metrics.
- 2026-11-12: Fit-to-content canvas on by default; gallery output regenerated once in Phase 14.
- 2026-11-12: Reference figure reproduced in style and structure with its slips corrected.
- 2026-11-12: Vector PDF export in scope (Phase 17).
- 2026-11-12: Stay on 0.x versions.
- 2026-11-12: GSD used for roadmap, requirements, state and atomic commits only. Research, plan-check and Nyquist steps turned off in `config.json`. Visual gates (gallery audit, golden images, looking at renders) added to the phase gate in `ROADMAP.md`.

## Blockers / Concerns

- None.

## Session

**Last session:** 2026-11-13T03:56:00.722Z
**Stopped at:** Phase 16 complete (v0.12.0), gate green; PR 19 merged, PR 20 open (Phase 15), Phase 16 branch local only; no tags; Phase 17 not started
**Resume file:** .planning/CHECKPOINT.md
