# Checkpoint — v0.17.1 fixes (uncommitted, unpushed) — 2026-11-21
**Status:** IN PROGRESS — needs resume (fixes verified, not committed; no push/PR/tag authorized)

## Goal (user's words)
> "ok to 1, 2; then do 3,4"
1 = sync master + commit .planning (not ROADMAP/NEXT_STEPS); 2 = delete merged branches feat/medical-engineering, refactor/colocate-examples-output, release/v0.17.0 (local+origin); 3 = Docker py3.10-3.13 matrix; 4 = fix `Draft.dimension` 8 px label offset and engineering/02 runout symbol (`\frac` was my own extra item, NOT approved, not done).
Standing: "use subagents in parallel with best model balancing". Always `uv`; no runtime deps; local-first gate; merge commits for PRs.

## Done (with evidence)
- v0.17.0 released earlier (PR #29 -> 7dd85c3, tag pushed); bare `render` writes beside script (092a179).
- 1: local master reset to origin/master 7dd85c3; planning commit `3f155b1` (CHECKPOINT+STATE) on branch `fix/v0.17.1`.
- 2: three merged branches deleted locally and on origin.
- 4: `draft.py` — dimension label gap = max(8, half label extent along normal); new `RUNOUT="↗"` cell in `gdt_frame` drawn as vector arrow (font glyph broke PDF export: test_pdf shaft). `examples/engineering/02_shaft_gdt.py` uses `RUNOUT`... (it passes literal "↗"). New test `test_vertical_dimension_label_clears_the_line`. 7 example SVGs re-rendered (cad/01,02,03,06; engineering/01,02,07). CHANGELOG [Unreleased] entry (root CHANGELOG.md; docs/CHANGELOG.md also shows modified — verify it is a synced copy).
- 3: Docker not used (no matrix script; pull failed earlier). uv matrix 3.10/3.11/3.12/3.13: 1574 passed each.
- Gate: pytest 1574 passed; main.py 0; generate_icons --check up to date; audit_gallery --check 0; lint examples 0.

## Dead ends
- `↗` as a plain text glyph: renders in SVG but PDF exporter has no glyph -> test_pdf fails. Use vector path.
- Sloppy test attempts: Diagram has no `_elements`; math text emits no `<text>` tags. Test intercepts `Draft._tag`.
- `git pull` / checkout blocked by dirty .planning; used `git checkout -B master origin/master` (carries dirty files).
- BSD `sed -i ''`.

## Working-tree state
- Branch `fix/v0.17.1` @ `3f155b1` (local only, not pushed).
- Uncommitted: .planning/ROADMAP.md (another session's; do not commit), docs/CHANGELOG.md, root CHANGELOG change, 7 examples/*.svg, examples/engineering/02_shaft_gdt.py, src/diagrams_as_code/draft.py, tests/test_draft.py, this checkpoint.
- Stashes: none · Background jobs: none · Ports: none of mine.

## Authorizations (RE-CONFIRM after reset)
- Done under approval: master sync, planning commit (CHECKPOINT/STATE), branch deletes.
- NOT authorized: committing the fix files, pushing `fix/v0.17.1`, opening a PR, merging, version bump to 0.17.1, tag. Never commit ROADMAP.md or NEXT_STEPS.md.

## Baseline check
- `uv run pytest -q` -> 1574 passed, 1 warning.

## Exact next command
Ask user: commit the fixes on `fix/v0.17.1`, then push + PR + (bump to v0.17.1 and tag?). Commit command: `git add CHANGELOG.md docs/CHANGELOG.md examples src tests && git commit` (check `git status` first; exclude .planning/ROADMAP.md). Also ask whether to do `\frac`.
