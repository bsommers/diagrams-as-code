# Checkpoint — code review remediation (2026-09-20 → 2026-09-21)

**STATUS: COMPLETE. No work is pending.** Everything below was verified on disk before `/clear`.
Do not start work from this file; wait for a new request.

## State (verified 2026-09-21)

- Branch `master`, clean, in sync with `origin/master`. 0 stashes, no background processes.
- HEAD = the commit that added this checkpoint update; the last code commit is `e12027d`.
- `uv run pytest -q` → **314 passed**. `uv run python tools/generate_icons.py --check` → up to date (63 files).
- CI green on all jobs (Python 3.10–3.13 + Docker) for `e12027d`.
- **GitHub issues: 0 open.** All 12 from the review (#1–#12) are closed, each with a verification comment.

## What shipped (oldest → newest)

| Commit | What |
|---|---|
| `de33502` | Icons generated from `ShapeLibrary._ICON_CATALOG` by `tools/generate_icons.py`; `main.py` no longer clobbers `README.md`; CI guard; LICENSE; relative links; version 0.3.0 (#2–5, #7–12) |
| `826c227` | `docs/sources.md` catalogs all four PNG backends + container image; `tests/test_dependency_catalog.py` (#6) |
| `81dad9e` | `.claude/` tracked in git (user's choice) |
| `7075434` | Test count dropped from `README.md` — it drifted 3 times; removed rather than guarded |
| `da2dbd4` | 84 rendered PNGs untracked + gitignored; CI now `git diff --exit-code -- output/` |
| `e12027d` | Fabricated icon attribution retracted; icons stated as original MIT work; `tests/test_icon_provenance.py` (#1) |

## Gates now in place (a future change must satisfy these)

- `tools/generate_icons.py --check` + `tests/test_icon_catalog.py` — icon tree, manifests, doc icon totals.
- `tests/test_dependency_catalog.py` — every `render_png` backend, base image and apt package is in `docs/sources.md`.
- `tests/test_icon_provenance.py` — no fabricated license names; an upstream attribution claim needs license text under `icons/licenses/`.
- CI: `git diff --exit-code -- README.md docs/ icons/ output/` after the suite runs.
- **Workflow consequence:** the test suite re-renders all 84 diagrams in place (`tests/test_domain_examples.py` runs with `cwd=<repo root>`). An engine change that alters SVG output fails CI until you run `uv run pytest` and commit `output/`.

## Decisions (verbatim where it matters)

- Provenance: first deferred (*"skip for now … a curiosity, not a requirement"*), then reversed a day later: *"fix issue #1"*. Done. See memory `provenance-tracing-is-optional`.
- `.claude/`: user chose to commit it (*"add .claude"*).
- `output/`: user approved untracking PNGs and gating SVG + BOM (*"do both"*).
- #6 deviation: the SBOM-diff CI criterion was replaced by a source-derived test (base-layer noise). Documented on the issue.

## Gotchas worth keeping

- GitHub closing keywords bind only to the first reference: write `Resolves #2, resolves #3`, not `Resolves #2, #3`.
- `gh issue close -c` silently drops the comment on an already-closed issue; use `gh issue comment`.
- Avoid `perl -0777 -pe` for multi-line replacement here (it once blanked a section). Use Python or head/tail.
- `/commit` skill template says `Claude Sonnet 4.6`; commits in this repo use the attribution of the model that actually did the work.

## Authorizations

All spent. Any future push, issue filing or issue close needs fresh confirmation.
