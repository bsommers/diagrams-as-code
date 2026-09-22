# Checkpoint — auto-layout / CLI / modularity (2026-09-22)

**Safe to `/clear`. Read this file + the SDD ledger before acting.**

## ⚠️ First thing to know

PR #13 was **merged** at `bc55bc8` (merge commit `fda6f69` on `origin/master`).
**Three later commits sit on `origin/feat/auto-layout-cli` and are NOT in master:**

| Commit | What |
|---|---|
| `28714da` | fix(layout): canvas grows whenever content lands outside it — **unclips 15 previously clipped diagrams** (only SVG header lines change; no artwork moves) |
| `9ef90dd` | docs: canvas growth described as unconditional (spec §4.1/§4.3/§11 + how-to.md) |
| `10328a2` | docs: full refresh — architecture.md pipeline/lifecycle, all 4 files in docs/diagrams/, README + running.md counts 227→431, AGENTS.md core-package fix, CHANGELOG [Unreleased] |

**Open question for the user:** second PR for these three, or push straight to
master? Not asked, not authorized. CI never ran on them (PR already merged, so
the pushes triggered no workflow). Locally: 431 tests pass, `generate_icons.py
--check` clean, `git status --porcelain -- output/ icons/` empty, tree clean.

## State

- Worktree: `/home/bill/src/ai/diagrams-as-code-auto-layout`, branch `feat/auto-layout-cli` @ `10328a2`, pushed.
- Main checkout `/home/bill/src/ai/diagrams-as-code` on `master`; fetched, local master may lag `origin/master` (`fda6f69`).
- SDD ledger (every ruling, deferred minor, parked finding):
  `/home/bill/src/ai/diagrams-as-code-auto-layout/.superpowers/sdd/2026-09-22-auto-layout-cli/progress.md`
  Same dir: per-task briefs/reports/reviews, `final-review.md`, `final-fix-report.md`, `docs-refresh-report.md`. Git-ignored; delete only once the three commits land.
- No background processes. No subagents running.

## What shipped (12 plan tasks + final-review fixes)

Auto-layout (`Diagram(layout="auto", direction=...)`, layered engine, mixes with manual pins),
editable JSON layout file (export/apply/round-trip; a group entry moves the whole group),
`diagrams-as-code` CLI (render / layout export / themes / icons, also `python -m`),
modularity split (context, rasterize, icon_glyphs, metrics, output, layout package; routing moved
into layout; import-direction test), 8 auto-layout examples (gallery 80→88), 315→431 tests.

## User decisions (verbatim where it matters)

- Order: "#1, then #4, then #3 — auto-layout … also allow manual placement or auto first, then manual adjustment; real CLI entry point; ensure modularity all throughout". #1 (dedupe) and #4 (v0.3.0, tagged + pushed) DONE.
- "In code + layout file (Recommended)" · "Layered, groups-aware" · "Python diagram scripts".
- "continue to use superpowers for now. we'll onboard gsd later" → memory `superpowers-now-gsd-later`; don't create `.planning/` files unprompted.
- Execution: subagent-driven ("1."). Then "3" = open a PR (#13). Then "fix the 15 clipped diagrams" (`28714da`). Then "refresh all documentation … need everything fresh" (`9ef90dd`, `10328a2`).
- Last message: "should we clear context? let's checkpoint when you're done. I'll start with a new agent - agy".

## Rulings made during execution (all in the ledger, with costs)

A/B preflight wording · **C: commit trailers name the model that did the work**, not the plan's
"Claude Opus 5" · D: CairoSVG now returns bytes (plan-intended) · E: canvas bottom margin uses
FRAME_Y (80) · F: test noise pulled into a fix round · G: the CLI must report unparsable scripts
instead of skipping them silently (exit 1) · **H: clipping fix deferred to the user — since
superseded: the user said fix it, and `28714da` does.**

## Gotchas

- The suite re-renders `output/` in place; CI runs `git diff --exit-code -- README.md docs/ icons/ output/`.
- Root `CHANGELOG.md` / `CAPABILITIES.md` / `capabilities.json` / `RUNNING.md` are symlinks into `docs/`.
- Never run a doc's example snippet from the repo root with a relative output path — a subagent did and overwrote `README.md` (restored; verified by diffing against master).
- `groups.py` tags flow constraints `_auto_layout`; the layout pipeline uses a distinct `_layout_source`.
- Deferred minors (none block merge) are listed in the ledger, already triaged by the final reviewer.

## Authorizations

All spent. Any further push, PR, merge or issue action needs fresh confirmation.
