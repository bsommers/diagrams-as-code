---
gsd_state_version: 1.0
milestone: v0.8.4
milestone_name: Technical Figures Program
current_phase: 13
current_phase_name: Text Engine
status: ready_to_plan
stopped_at: Phase 12 complete on branch feat/technical-figures-m1 (not pushed, not tagged)
last_updated: "2026-11-12T00:00:00.000Z"
last_activity: 2026-11-12
last_activity_desc: Phase 12 complete - 14 defects fixed test-first, gallery audit gate added (602 tests)
progress:
  total_phases: 6
  completed_phases: 1
  percent: 17
---

# Project State

## Project Reference

See `.planning/PROJECT.md`, `.planning/ROADMAP.md`, and the approved plan
`docs/plans/2026-11-12-technical-figures-and-quality.md`.

**Current focus:** Phase 13 — Text Engine. Phase 12 is complete on branch `feat/technical-figures-m1`, awaiting push/PR and the v0.8.4 tag.

## Phase 12 result

Audit across 92 diagrams, before -> after: tangent arrivals 47 -> 0, edges through own endpoint 1 -> 0, overlapping edges 48 -> 22, edges through a badge 196 -> 188, badges over nodes 95 -> 80, badges over badges 37 -> 28. Unchanged and owned by later phases: label overflow 29 (Phase 13), mostly-empty canvas 90 and the remaining badge/overlap counts (Phase 14).

Known gap: the PNG backend ignores italic and serif switches inside a text run (found while prototyping); Phase 13 starts by settling the outline-glyph approach for math.

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
