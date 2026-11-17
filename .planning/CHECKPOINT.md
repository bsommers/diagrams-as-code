# Checkpoint — v0.13.1 released; working tree taken over by another session — 2026-11-15 (late)
**Status:** COMPLETE for this session's work. v0.13.1 is merged, tagged and pushed. Open question: who owns the new-domain-galleries work now in the tree (see Working-tree state).

## Goal (user's words)
> "fix the PNG shadow bug in output/cloud/09_iot_cloud_fleet_management.png"

> "i want it"  (also fix the interactive-overlay id clash)

> "2, then 1"  (tidy planning files, then release the fix)

> "yes. go"  (merge PR #24 and tag)

## Decisions and corrections (verbatim)
- "2, then 1" — planning cleanup first (STATE.md, ignore `graphify-out/`), then the v0.13.1 release.
- "yes. go" — approved merging PR #24 and pushing the tag. No GitHub Release page was requested.
- "Should we compact and checkpoint now?" — asked for this checkpoint; I must not run /compact or /clear.
- Standing rules: always `uv`; no runtime deps; local-first verification, GitHub CI is disabled (billing); never push WIP; merge PRs with merge commits.

## Done (with evidence)
- Root cause of the PNG "shadow" bug: node id `shadow` clashed with the `<filter id="shadow">`. Fixed in PR #23 (`76ebc37`, code `0ffcd26`), plus overlay ids in `renderer_interactive.py`.
- Planning cleanup — commit `8ad9612` (STATE.md records PR #23 merged; `.gitignore` gains `graphify-out/`).
- Release commit `f468819`: 0.13.1 in `pyproject.toml`, `uv.lock`, `src/diagrams_as_code/__init__.py`, `docs/capabilities.json`, `docs/CAPABILITIES.md`; `[Unreleased]` changelog entries dated under `[v0.13.1] - 2026-11-15`.
- Gate before PR: `uv run pytest -q` → 1126 passed; `main.py` ok; `generate_icons.py --check` up to date; `audit_gallery.py --check` exit 0; `git diff --exit-code -- output/ icons/ README.md` clean. Docker py3.10–3.13 matrix NOT re-run for 0.13.1 (it was run at `0ffcd26`).
- PR #24 merged → `b7772db` on master. Annotated tag `v0.13.1` created on it and pushed to origin.

## Dead ends (don't retry)
- BSD `sed -i 's/…/'` with `\n` in the replacement fails on macOS and `&&` stops the chain; use Python for multi-line edits.
- `git checkout master` fails while `.planning/CHECKPOINT.md` / `STATE.md` are modified by a hook or another session; stash first.

## Working-tree state
- Branch: `feat/new-domain-galleries` @ `b7772db` (== master head). I left the tree on `master`; I did NOT switch it. Another session did.
- `git status --short`: ` M .planning/CHECKPOINT.md`, ` M .planning/STATE.md`, ` M tests/test_domain_examples.py`, untracked `examples/{computer_science,database,enterprise_architecture,manufacturing,mind_map}/` and `output/{same five}/`. None of this was written by this session; treat it as the other session's work in progress. Do not stage, stash, discard or commit it without asking.
- `.planning/STATE.md` still says "v0.13.1 release prepared as PR #24, waiting for the user to merge and tag" (stale; PR #24 is merged and the tag pushed). I did not run `state.record-session`, to avoid overwriting the other session's state.
- Stashes: none · Background jobs/agents of mine: none · Ports: only unrelated local processes.

## Authorizations and scope (RE-CONFIRM after reset)
- Merge of PR #24 and push of tag `v0.13.1` were authorized and are done. Nothing further is authorized.
- Any push, PR, merge, tag or GitHub Release needs fresh confirmation.

## Baseline check
- `uv run pytest -q` → 1126 passed, 1 warning (expected `LayoutWarning`) at `f468819`, before the other session's changes.

## Exact next command
`cd /Users/bill/src/diagrams-as-code && git status -sb && git log --oneline -3` — then ask the user whether the `feat/new-domain-galleries` work is theirs to continue, and refresh `.planning/STATE.md` ("v0.13.1 released") once that is settled.
