# Checkpoint — code review remediation (2026-09-20)

Written before `/compact`. Everything below is verified on disk, not remembered.

## Goal (user's words)

1. `/code-review high. write a report in form of script. well written commands to write github issue. do not file issues, just make script for review`
2. `uncomment the three severity labels so gh label create works. then run script with --file option`
3. Triage of a 3-batch proposal: `1 - do this / 2 - skip for now. now. license and source tracing was more of a curiosity, not a requirement / 3 - do it`
4. `yeah. fix that README.md issue with ci.yml, root case as #9. tell me what you fixed`
5. `refresh all documentation, links, example outputs and rerun test suite`
6. `commit` (via `/commit`), then `close them` (the resolved issues)

**All six are complete.** There is no work in flight.

## Decisions and corrections (verbatim, do not re-litigate)

- **#1 (icon provenance table) is deliberately NOT fixed.** User: *"skip for now. now. license and
  source tracing was more of a curiosity, not a requirement"*. `docs/sources.md` still attributes
  icons to Lucide/Feather/Tabler/Cisco/CNCF/AWS and still names two licenses that do not exist
  ("Public Domain / Open Stencil Use", "Permissive Architectural Diagramming Use").
  **Do not edit that table unless the user reopens it.**
- **#6 (dependency catalog omits cairosvg, Inkscape, ImageMagick, DejaVu) was never chosen.**
  Not a decision against it — it simply was not in either approved batch.
- Both remain OPEN on GitHub by intent.

## State (verified at checkpoint time)

- Branch `master`, clean, in sync with `origin/master`. 0 stashes, 1 worktree (the repo itself).
- HEAD = `de33502` "fix: make icons and docs generated and verifiable, not hand-maintained"
  (59 files, +1906/−697). **Committed AND pushed** to `bsommers/diagrams-as-code` (private).
- Baseline: `uv run pytest -q` → **304 passed**; `uv run python tools/generate_icons.py --check`
  → "icons/ is up to date (63 files)"; link check → 188 resolved / 0 broken.
- No background processes, no open ports.

## What shipped in de33502

Single source of truth for icons:
- `ShapeLibrary._ICON_CATALOG` (`src/diagrams_as_code/shapes.py`) — 60 icons, each mapped to one
  domain and one description. `_CANONICAL_ICONS = frozenset(_ICON_CATALOG)` derived from it.
- `tools/generate_icons.py` emits the whole `icons/` tree + `icons.csv` + `icons.yaml` +
  `icons/README.md`. `--check` lists missing/stale/extra and exits 1.
- Tree 59 → 60 files: added `iiot/{dashboard,database,queue}.svg`; removed duplicate
  `computer/sensor.svg` and `iiot/plc.svg` (one domain home per icon).
- `tests/test_icon_catalog.py` — 76 tests. Negative-tested: hand-edit an icon → 2 fail;
  delete an icon file → 6 fail; revert a doc count → count guard fails.

Other fixes: `LICENSE` (MIT) added; 127 `file:///home/bill/...` links → relative; `requirements.txt`
removed; `resvg-py` row corrected to baseplate-admin/MIT and recategorized "Optional Runtime";
version synced to 0.3.0; false uniform-stroke claim replaced with a measured one; icon total
corrected to 60 in ten documents; all 83 example diagrams re-rendered (6 outputs were stale).

README/CI root cause (same shape as #9):
- `main.py`'s `generate_root_readme()` **deleted**. It rebuilt `README.md` from a hardcoded template
  91 lines behind the maintained file, silently reverting every edit — including in CI.
- `.github/workflows/ci.yml` gained a guard step: `tools/generate_icons.py --check` then
  `git diff --exit-code -- README.md docs/ icons/`. **`output/` is excluded on purpose** —
  PNG bytes are not guaranteed reproducible across runners and a flaky gate gets disabled.

## Issue tracker

- CLOSED with verification comments citing `de33502`: #2 #3 #4 #5 #7 #8 #9 #10 #11 #12
- OPEN by intent: **#1** (provenance, user-skipped), **#6** (dependency catalog rows)
- `.issues/draft-2026-09-20.sh` is committed — the script that filed #1–12. Re-runnable;
  `--file` creates, bare is a dry run.

## Dead ends / gotchas (do not repeat)

- **GitHub closing keywords bind only to the first reference.** `Resolves #2, #3, #4` closed only #2.
  Write `resolves #2, resolves #3, ...`. Also: `gh issue close -c` **silently drops the comment** if
  the issue is already closed — use `gh issue comment` separately.
- **perl `-0777 -pe` for multi-line block replacement is hazardous here.** `${VAR}` gets interpreted
  by perl, and `$ENV{X}` read in a `BEGIN` block once produced an EMPTY replacement that deleted a
  whole `CONCERNS.md` section. Use `head`/`tail` + heredoc splicing instead.
- `grep "import diagrams"` false-positives on `diagrams_as_code`; use `(?!_as_code)`.
- A **regex** guard for doc icon counts kept false-positiving on sentences like "13 themes … 60 icons".
  Replaced with `DOC_ICON_CLAIMS` — an exact advertised phrase pinned per document.
- The test-count claim in `README.md:100` went stale **twice in one session** (227 → 299 → 304).
  It is currently correct at 304 but is **unguarded** and will drift again.

## Authorizations (scope, and what needs re-confirming)

- User authorized filing issues (`--file`) and `/commit` (which stages all, commits, pushes to
  upstream `master`). Both were **used and are spent**.
- **Any further push, issue filing, or issue close needs fresh confirmation.** Do not treat the
  above as standing permission.
- Note: `/commit` pushes directly to `master`. Its skill template says to attribute
  `Claude Sonnet 4.6`; this session used `Claude Opus 5` because that is the model that did the work.

## Next command

No work is pending. If the user picks up the remaining items, start with:

```bash
cd /home/bill/src/ai/diagrams-as-code && git log --oneline -1 && uv run pytest -q | tail -2
```

Then one of, in the order recommended to the user:
1. **#6** — add cairosvg (LGPL-3.0), Inkscape (GPL-3.0), ImageMagick, the Docker base image and
   `fonts-dejavu-core` rows to the `docs/sources.md` dependency table.
2. **Guard the test-count number** in `README.md:100` and `docs/CHANGELOG.md` the way
   `DOC_ICON_CLAIMS` guards the icon total, or drop the number from the prose.
3. **`output/`** — 252 checked-in files nothing verifies. Either add to the CI guard (requires
   answering PNG determinism first) or stop committing rendered outputs.
4. **#1** — only if the user reopens the provenance question.

---

## UPDATE — issue #6 done, NOT COMMITTED (2026-09-20)

User picked option 1 (#6, dependency catalog). Uncommitted work now in the tree:
- `docs/sources.md`: §2 gained CairoSVG (LGPL-3.0), Inkscape (GPL-3.0), ImageMagick rows;
  intro reworded to "not uniformly permissive"; new §3 catalogs the container image
  (base image, Debian 12 layer, `fonts-dejavu-core`) + an SBOM pointer.
- `tests/test_dependency_catalog.py` (NEW, 4 tests): parses `render_png`'s real fallback chain
  via `inspect.getsource` and the real `Dockerfile`; fails if a backend, base image, or apt
  package is missing from the catalog. All 4 negative-tested.
- `docs/CHANGELOG.md`: v0.3.0 Changed + Verification entries; "permissive" claim softened.

Baseline now: **308 passed**; icons --check clean; 274 links resolved / 0 broken;
`main.py` leaves README/docs/icons untouched (md5-verified).

**DEVIATION from issue #6's acceptance criteria:** criterion 4 asked for a CI SBOM diff
(`syft`/`docker sbom`). Not done — it would flag every Debian base-layer package and needs a
network tool in CI. Replaced with the source-derived test above. Say so when closing #6.

NEXT: needs user approval to commit/push and to close #6. Nothing is authorized yet.

### UPDATE 2026-09-21 — #6 committed, pushed, closed
HEAD = `826c227` "docs: catalog every PNG backend and what the container ships", pushed
(`de33502..826c227`). #6 auto-closed via `Resolves #6.`; verification comment added separately
(`gh issue comment`, since `-c` on an already-closed issue is dropped). Tree clean except
untracked `.claude/`. **Only #1 remains open, by user decision.** Nothing pending.
