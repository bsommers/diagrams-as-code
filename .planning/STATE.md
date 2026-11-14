---
gsd_state_version: "1.0"
milestone: v0.8.4
milestone_name: → v0.13.0)
status: ready_to_plan
stopped_at: Phase 15 complete (v0.11.0) on branch feat/phase15-drawing-primitives, gate green, audit all zero; Phase 16 not started; Phases 12-14 are in PR 19; Phase 15 branch not pushed; no tags
last_updated: "2026-11-13T12:00:00.000Z"
state_head: 338b56095d23021d4ae337698a68bf6666be855f
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 0
  completed_plans: 0
  percent: 67
last_activity: 2026-11-13
current_phase: 16
current_phase_name: Technical Examples & Visual Regression
last_activity_desc: Phase 15 complete - drawing primitives, edge options, solids, bands, nesting, z-order, arranging (881 tests)
---

# Project State

## Project Reference

See `.planning/PROJECT.md`, `.planning/ROADMAP.md`, and the approved plan
`docs/plans/2026-11-12-technical-figures-and-quality.md`.

**Current focus:** Phase 16 — Technical Examples & Visual Regression. Phases 12 (v0.8.4), 13 (v0.9.0) and 14 (v0.10.0) are in PR #19 from `feat/technical-figures-m1`. Phase 15 (v0.11.0) is complete on `feat/phase15-drawing-primitives`, stacked on that branch and not yet pushed. Tags follow the merges.

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
**Stopped at:** Phase 14 complete at 338b560 (v0.10.0), gate green, 5 residual audit defects carried; Phase 15 not started; nothing pushed or tagged
**Resume file:** .planning/CHECKPOINT.md
