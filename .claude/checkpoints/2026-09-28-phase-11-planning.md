# Checkpoint — Phase 11 planning (2026-09-28)

## Goal
Write the Phase 11 implementation plan with `superpowers:writing-plans`, in **two waves**:
1. **Data model + style resolution:** D-05, D-07, D-08, D-13–D-19.
2. **Canvas growth:** D-06, D-09–D-12, built on wave 1.

Save it to `docs/superpowers/plans/2026-09-28-phase-11-routing-model-and-extrema.md`.

## User decisions (verbatim, in order)
- Asked "should we do a /code-architecture-review to complement this other review?", then ran `/code-architecture-review`, scoped to the routing pipeline. **The user declined the graphify AST run**, so the code was read by hand. Don't retry graphify.
- "do as you recommend" → fold review Batches 1–2 into the Phase 11 context, starting with D-07. Done in `4a96c68`.
- "yes" → commit, then start the Phase 11 plan in two waves.
- **The user rejected** moving `.planning/.../11-CHECKPOINT.md` to `docs/plans/` with `git mv` and committing that. Don't move or rename planning files to satisfy tooling.
- "run preflight for compacting-context-safely" → this file.
- Standing preferences (memory): superpowers specs/plans (GSD onboarding deferred); review triage as numbered batches.

## Sources of truth
- `.planning/phases/11-configuration-hierarchy-layout-extrema-integration/11-CONTEXT.md`: the decisions. D-05–D-08 were revised and D-13–D-19 added on 2026-09-28. CONTEXT beats `11-RESEARCH.md` (a note in RESEARCH says so).
- `docs/reviews/2026-09-28-edge-routing-architecture.md`: target blueprint, P0.1–P0.6 with before/after snippets, and the table mapping CR-1..CR-15 to the roadmap.
- `.planning/phases/11-.../11-CHECKPOINT.md`: an earlier copy of this checkpoint (committed in `7522d42`).

## Facts established (do not re-derive)
- Routing currently happens in three places:
  - `layout/pipeline.py:66` (`OrthogonalRouter`, which forwards CURVE at `router.py:636`);
  - the renderer fallback at `renderer_svg.py:693–715`;
  - the `EdgeRouter` facade (exported and tested, unused internally).
- `solver.all_elements()` already includes groups.
- `Edge._clearance` defaults to 15.0 (not None). `corner_radius` uses None to mean inherit. `Diagram.solve()` cascades only `corner_radius`.
- `CurveRouter.route` writes `edge.waypoints`. `run_layout` writes `edge.waypoints` and `diagram.routes` (keyed by `id(edge)`). The renderer prefers `e.waypoints` over `routes`.
- Routing runs after `_grow_canvas` (the cause of CR-2).
- Layers (`tests/test_module_boundaries.py`): geometry 0; elements 1; connections 2; router/constraints 3; renderer_svg/layout/bom 4; diagram 5.
- `renderer_svg._render_filleted_path` (lines 19–116) clamps fillets against obstacles. Under D-16 this moves to routing time.

## Working tree / state
- Branch `master`, local only. HEAD is `7522d42`, and the tree was clean before this file.
- This checkpoint file is **uncommitted** (the user interrupted the last commit attempt; ask before committing it).
- Baseline: `uv run pytest -q` → **520 passed** (re-verified during the pre-flight).
- No background processes.

## Authorizations
- Commits of planning/doc work: granted earlier this session. Re-confirm after the reset.
- **Push: not granted.**

## Next command
Read this file, run `git status` and `uv run pytest -q` (expect 520 passed), then invoke `superpowers:writing-plans` with 11-CONTEXT.md and the review doc as the spec.
