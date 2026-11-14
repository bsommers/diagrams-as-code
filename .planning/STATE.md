---
gsd_state_version: "1.0"
milestone: v0.8.4
milestone_name: → v0.13.0)
status: phase_complete
stopped_at: "Phase 17 complete on feat/phase17-vector-pdf (local commits, not pushed); Phases 12-16 merged to master and tagged v0.8.4..v0.12.0; v0.13.0 not tagged"
last_updated: "2026-11-14T08:00:00.000Z"
state_head: 0f0e46b
last_activity: 2026-11-14
current_phase: 17
current_phase_name: Vector PDF Export
last_activity_desc: Phase 17 complete - pure-stdlib vector PDF export, render_pdf, --format pdf (1121 tests)
progress:
  total_phases: 6
  completed_phases: 6
  total_plans: 0
  completed_plans: 0
  percent: 100
---

# Project State

## Project Reference

See `.planning/PROJECT.md`, `.planning/ROADMAP.md`, and the approved plan
`docs/plans/2026-11-12-technical-figures-and-quality.md`.

**Current focus:** All six phases (12–17) are done. Phases 12–16 are merged to master (PRs #19, #20, #21) and tagged v0.8.4, v0.9.0, v0.10.0, v0.11.0, v0.12.0. Phase 17 (v0.13.0) is complete on `feat/phase17-vector-pdf`, committed locally; pushing it, opening its PR and tagging v0.13.0 each need the user's go-ahead.

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

## Phase 17 result

v0.13.0. PDF-01..03 done in `pdf.py` (layer 4, imports only `drawing` and `text`). Design: the PDF is drawn from the SVG the renderer writes rather than from a second display list, so nothing in the renderer changed and gallery SVG is byte-identical. `ELEMENTS` / `ATTRIBUTES` list the SVG vocabulary the writer knows; anything else raises `PDFExportError`, and `tests/test_pdf.py` fails if the gallery uses a construct outside them. Text: standard 14 fonts with `/Widths` and a descriptor, WinAnsi plus Symbol fallback, serif placed with `text/_serif_metrics.py` (Tinos widths, OFL 1.1). Group opacity is a transparency-group form XObject. Shadows are six translucent stroke rings plus a fill.

Verified: 1121 tests on macOS (py3.14); 1107 pass + 14 skip on Linux arm64 py3.10–3.13 (2 hygiene skips without git, 12 rendered-comparison skips without `pdftoppm`); all 113 gallery PDFs clean in `pdfinfo` and Ghostscript; reference figure checked by eye in poppler, Ghostscript and Quartz.

Known limits: fonts are not embedded (not PDF/A); a character outside Windows-1252 and Symbol is drawn as `?` with a warning; Symbol glyphs sit at the left of the slot the sans metrics give them; stroke-only shapes and text cast no shadow; compressed bytes may differ between zlib builds. Homebrew poppler on macOS draws Helvetica-Bold with the regular face (its font substitution; Ghostscript and Quartz draw bold). Found on the way, not fixed: resvg-py 0.5.0 drops every shadowed node when rasterizing `output/cloud/09_iot_cloud_fleet_management.svg` to PNG (the SVG and PDF are correct; PNGs are untracked).

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

**Last session:** 2026-11-14T08:00:00.000Z
**Stopped at:** Phase 17 complete on feat/phase17-vector-pdf (local commits, not pushed); Phases 12-16 merged to master and tagged v0.8.4..v0.12.0; v0.13.0 not tagged
**Resume file:** .planning/CHECKPOINT.md
