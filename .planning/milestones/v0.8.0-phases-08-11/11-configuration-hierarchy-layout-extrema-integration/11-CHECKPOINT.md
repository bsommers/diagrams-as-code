# Phase 11 Checkpoint — 2026-09-28

## Goal
Write the Phase 11 implementation plan, now that the edge-routing architecture review's Batches 1–2 are folded into `11-CONTEXT.md`.

## User decisions (verbatim, in order)
- To "should we do a /code-architecture-review to complement this other review?" → ran `/code-architecture-review`, scoped to the routing pipeline. The user declined the graphify run, so the code was read by hand.
- "do as you recommend" → fold review Batches 1–2 into the Phase 11 context, starting with D-07. Done in commit `4a96c68`.
- "yes" → commit, then start the Phase 11 plan in **two waves**:
  1. **Data model + style resolution:** D-13–D-19, plus D-05, D-07, D-08.
  2. **Canvas growth:** D-06, D-09–D-12, built on wave 1.
- Standing preferences (memory): use superpowers specs/plans (GSD onboarding deferred); present review triage as numbered batches.

## Sources of truth
- `.planning/phases/11-configuration-hierarchy-layout-extrema-integration/11-CONTEXT.md`: the decisions. Where `11-RESEARCH.md` conflicts, CONTEXT wins (a note in RESEARCH says so).
- `docs/reviews/2026-09-28-edge-routing-architecture.md`: target architecture, P0.1–P0.6, the CR-n → roadmap table.
- The code-review findings CR-1..CR-15 are summarised in the review doc's mapping table. The raw review output is not saved; the review doc is enough.

## Key facts established (do not re-derive)
- Routing currently happens in three places: `layout/pipeline.py:66` (`OrthogonalRouter`, which forwards CURVE at `router.py:636`), the renderer fallback at `renderer_svg.py:693–715`, and the `EdgeRouter` facade (exported, unused internally).
- `solver.all_elements()` already includes groups.
- `Edge._clearance` defaults to 15.0 (not None). `corner_radius` already uses None to mean inherit.
- `CurveRouter.route` writes `edge.waypoints`. `run_layout` writes both `edge.waypoints` and `diagram.routes` (keyed by `id(edge)`).
- Routing runs after `_grow_canvas` today (cause of CR-2).
- The layer test is `tests/test_module_boundaries.py` (router = 3, renderer_svg = 4, layout = 4, geometry = 0).
- Baseline: `uv run pytest` → **520 passed** (2026-09-28, before any code change).

## Dead ends
- None. The graphify AST run was declined by the user, so don't retry it.

## Working tree
- Branch `master`, local only (nothing pushed). Commits this session: `4a96c68` (the review and Phase 11 context revision) and this checkpoint.
- No background processes.

## Authorizations
- Commit: granted for this session's planning/doc changes. **Push: not granted.** Ask before pushing (CLAUDE.md: push only verified green changesets).

## Next step
Invoke `superpowers:writing-plans` for Phase 11, using `11-CONTEXT.md` and the review doc as the spec, with two waves as above. Save to `docs/superpowers/plans/2026-09-28-phase-11-routing-model-and-extrema.md` (the user prefers superpowers plans).
