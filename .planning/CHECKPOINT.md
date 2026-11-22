# Checkpoint — v0.17.0 release, PR #29 open, awaiting merge + tag OK — 2026-11-19
**Status:** COMPLETE (re-verified 2026-11-21 15:03: origin/master=7dd85c3 incl. 092a179; tag v0.17.0 -> 7dd85c3) — PR #29 merged as 7dd85c3; tag v0.17.0 and GitHub Release published. Matrix run via uv on 3.10-3.13 (Docker could not pull: locked keychain).

## Goal (user's words)
> "run the gate on master ; take care of loose-ends; tidy planning; decide on release - v0.17.0 and update refresh full documenation, examples, replace main README.md diagram with something more snazzy from our examples ; 4 - yes redraw"

> "Ok. But first check with any other agents and the GitHub remote state before.  Do a branch and pr if unsure or if safer"

Earlier scope: "do 50-diagram release plus public module. then let it run to a green gate" (that became v0.15.0, merged) and "yes, run the gate on medical-engineering" (v0.16.0, merged).

## Decisions and corrections (verbatim)
- "Do a branch and pr if unsure or if safer" — I pushed the branch and opened PR #29 and stopped; I did NOT merge or tag.
- "4 - yes redraw" — heart figure redrawn (done). The "review MCP security" half of my item 4 was done too and hardening was applied.
- Standing rules (CLAUDE.md): always `uv`; no runtime deps; local-first verification (GitHub CI disabled); never push WIP; merge PRs with merge commits. Gate step 4 now diffs `examples/ icons/ README.md docs/` (the `output/` dir is gone).

## Done (with evidence)
- Gate on master `5d27b28` in a worktree: pytest 1567 passed; main.py 0; icons up to date; audit exit 0; diff clean.
- Branch `release/v0.17.0` @ `5ba208b` (1 commit on `5d27b28`): MCP hardening (`src/diagrams_as_code/mcp.py`, 6 new tests in `tests/test_mcp.py`); redrawn `examples/medical/01_heart_chambers.*`; README hero (mind map) + 2x2 strip + gallery table + MCP quickstart; docs refresh; version 0.17.0 (pyproject, uv.lock, `__init__`, capabilities.json/CAPABILITIES.md with `CAP-MCP-SERVER`); CHANGELOG `[v0.17.0]`; planning refresh.
- Gate on the branch: `uv run pytest` → 1572 passed, 1 expected LayoutWarning; main.py 0; `generate_icons.py --check` up to date; `audit_gallery.py --check` exit 0; `diagrams-as-code lint examples` exit 0; examples diff only the intended heart files and examples/README.md.
- Remote check before push: all peer sessions idle (incl. diagrams-as-code-e7); `origin/master` = `5d27b28`; no open PRs; other remote branches old/merged; tag v0.17.0 absent.
- Pushed `release/v0.17.0`; opened https://github.com/bsommers/diagrams-as-code/pull/29 (OPEN, MERGEABLE, head `5ba208b`, re-checked just now).

## Dead ends (don't retry)
- `json.dump` on `docs/capabilities.json` reformats compact arrays (148-line diff); edit it as text.
- `sed -i` on macOS needs `sed -i ''`; BSD sed with `\n` in replacement fails. Use Python for multi-line edits.
- A pytest/grep-style test of "arguments": [] passes because `[] or {}` is falsy; use a non-empty non-dict to test validation.

## Working-tree state
- Branch: `release/v0.17.0` @ `5ba208b`, tracking `origin/release/v0.17.0`.
- `git status --short`: clean before this checkpoint; this checkpoint and `state.record-session` modify `.planning/CHECKPOINT.md` and `.planning/STATE.md` (uncommitted on purpose; no CI trigger).
- Stashes: none · Background jobs/agents of mine: none running (heart, docs and security subagents all finished) · Ports: only unrelated local Claude/agy processes.

## Authorizations and scope (RE-CONFIRM after reset)
- Authorized and done: push of `release/v0.17.0` and opening PR #29.
- NOT authorized yet: merging PR #29, pushing tag `v0.17.0`, any GitHub Release. Ask the user; plan is merge with a merge commit, then tag `v0.17.0` on the merge commit and push the tag.
- Docker py3.10-3.13 matrix was not run; offer it before merging.
- Known MCP limits (documented, not fixed): no script timeout; a script can write to fd 1 or read stdin; path confinement is not a sandbox. Roadmap item: resource-limited subprocess.

## Baseline check
- `uv run pytest -q` → 1572 passed, 1 warning at `5ba208b`.

## Exact next command
`cd /Users/bill/src/diagrams-as-code && git fetch -q origin && gh pr view 29 --json state,mergeable,headRefOid && git ls-remote --tags origin 'v0.17*'` — then ask the user to confirm "merge PR #29 and tag v0.17.0" (and whether to run the Docker matrix first). After merge: `git checkout master && git pull`, tag `v0.17.0` on the merge, `git push origin v0.17.0`, update STATE.md/ROADMAP (v0.17.0 released).

## Addendum (2026-11-21, this session)
- User chose "2": bare `render` writes beside each script; it is `092a179` (in v0.17.0). The earlier side-agent claim that bare render overwrote committed examples was false (tested).
- Still on local branch `release/v0.17.0` @ `092a179`; local master is behind `origin/master` (7dd85c3). Next: `git fetch && git checkout master && git merge --ff-only origin/master` (blocked while .planning is dirty).
- `.planning/ROADMAP.md` is modified by another session; not mine; do not commit without asking.
- Leftover merged local/remote branches: feat/medical-engineering, refactor/colocate-examples-output, release/v0.17.0. Deleting needs user OK.
