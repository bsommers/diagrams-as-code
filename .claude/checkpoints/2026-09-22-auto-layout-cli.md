# Checkpoint — auto-layout / CLI / modularity (2026-09-22)

## State (verified before writing)
- Branch `master`. Unpushed commits: `5d92a5c` (spec), `4d740cf` (spec group-move rule). Plan `docs/superpowers/plans/2026-09-22-auto-layout-cli.md` (12 tasks) and review `docs/reviews/2026-09-22-architecture-boundaries.md` committed together with this checkpoint.
- v0.3.0 released: commit `64cf2e9`, annotated tag `v0.3.0` pushed, CI green.
- Baseline: `uv run pytest -q` → 315 passed (before any plan task). No background processes.

## User decisions (verbatim where it matters)
- Order: "#1, then #4, then #3 - auto-layout -- add auto-layout option, also allow manual placement or auto first, then manual adjustment; real CLI entry point; ensure modularity all throughout". #1 and #4 are DONE.
- Adjust flow: "In code + layout file (Recommended)". Algorithm: "Layered, groups-aware". CLI input: "Python diagram scripts".
- Design part 1 "yes", part 2 "looks right"; spec "looks good. proceed".
- Planning: "continue to use superpowers for now. we'll onboard gsd later" (memory `superpowers-now-gsd-later`).
- Latest request (answered in chat 2026-09-22): small architecture review table of parser/layout/renderer boundaries with recommendations.

## Next steps
1. User said (2026-09-22): "save the above summary somewhere sensible. then do #1 and #2. then commit" — done: review saved; route-in-layout (Task 9) and shared `metrics.py` (Task 7) added; CLI export-test `or` fixed; typed constraints deferred.
2. Offer execution choice for the plan (subagent-driven vs inline). No execution started. Baseline 315 passing.
3. Pushing needs fresh confirmation (2 spec commits + this one are unpushed).

## Gotchas
- Suite re-renders `output/` in place; CI `git diff --exit-code -- README.md docs/ icons/ output/`.
- Root CHANGELOG/CAPABILITIES/capabilities.json/RUNNING.md are symlinks into docs/.
- groups.py already tags flow constraints `_auto_layout`; layout pipeline uses a distinct key `_layout_source`.
