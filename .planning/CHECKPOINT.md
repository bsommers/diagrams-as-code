# Checkpoint — id-collision fixes after Phase 17 (PNG "shadow" bug) — 2026-11-15
**Status:** COMPLETE, in review. Both fixes are committed as `0ffcd26` on `fix/svg-id-collisions`, pushed, and open as PR #23 (https://github.com/bsommers/diagrams-as-code/pull/23) against `master`. Not merged, not tagged, not released. Phases 12–17 are merged and tagged `v0.8.4` … `v0.13.0`, all pushed.

## Goal (user's words)
> "fix the PNG shadow bug in output/cloud/09_iot_cloud_fleet_management.png"

Then, after I reported that interactive-overlay ids could clash the same way and offered to fix it:
> "i want it"

- GSD position: no active phase. Phases 12–17 are done (`.planning/ROADMAP.md`, `STATE.md`); this was follow-up work outside a phase, no PLAN.md.
- Earlier goal of the milestone, for context: "Review this code repository Make it better fix bugs Increase the quality add more examples make it capable of Highly precise technical drawings in the style of the referenced diagram. …" (plan: `docs/plans/2026-11-12-technical-figures-and-quality.md`; reference image `~/Downloads/Gemini_Generated_Image_ujvhivujvhivujvh.jpeg`).

## Decisions and corrections (verbatim)
This session:
- "fix the PNG shadow bug in output/cloud/09_iot_cloud_fleet_management.png" — scope of fix 1.
- "i want it" — approved fix 2 (interactive overlay ids).
- "commit" — commit on `fix/svg-id-collisions`; done (`0ffcd26`).
- "push" — push the branch and open the PR; done (PR #23).
- "then compact" — the user compacts after the push. No merge, tag or release was asked for.

Earlier sessions (still valid):
- "that's right Open GSD refers to GSD. \n* fonts - yes open-license ; \n* existing gallery output: accept recommendations fit-to-content\n* reference slips: do as you suggest\n* PDF export: add it\n* Version: stay on 0x.\ndo GSD if it helps - do the suggestions you have on Keep, Drop, add missing items to GSD"
  - Open-licence font data may be bundled. Fit-to-content canvas is the default. The reproduction corrects the reference's slips. PDF export is in scope (Phase 17, pure stdlib). Versions stay 0.x.
  - GSD: keep ROADMAP/REQUIREMENTS/STATE + atomic commits; research, plan_check and nyquist_validation are off in `.planning/config.json`; visual gates (audit, golden images, looking at rendered PNGs) are part of the phase gate.
- "push and PR, keep defaults grow-to-fix; keep exemptions" — grow-to-fit labels stay on by default; audit exemptions (exact bus, line under its own badge) stay.
- "do as you suggest above. then start Phase 16" — merge with merge commits; retarget stacked PRs by hand.
- "1 - yes I want local. no need to spend github CI\n2 - yes\n3 - yes" (2026-11-13) — (1) verify in local Linux Docker on Python 3.10–3.13 instead of GitHub CI, and do not spend GitHub CI minutes; (2) push Phase 16 and open its PR; (3) merge PR #20. All three done.
- "checkpoint then we'll clear" — the user then quoted the open items (merge #21, tags, Phase 17) without approving any of them.
- Standing repo rules (AGENTS.md / CLAUDE.md): always `uv`; no runtime dependencies (`dependencies = []`); core engine pure stdlib; `src/iiot_diagrams` is a compat facade; local-first verification; never push WIP.
- "1 - go; 2 - create missing tags ; 3 start phase 17" — merged PR #21, created and pushed the tags, built Phase 17 (since merged as PR #22, `41a6af7`, tagged `v0.13.0`).

## Done (with evidence)
This session (committed as `0ffcd26`, pushed, PR #23):
- Root cause: not a resvg bug. `examples/cloud/09_iot_cloud_fleet_management.py` has a node with id `shadow`, the same id as the drop-shadow `<filter id="shadow">`. With two elements sharing the id, resvg resolved `url(#shadow)` to the node and dropped every shadowed shape. (The PDF writer was unaffected because it reads filters from `<defs>` only.)
- Fix 1, `src/diagrams_as_code/renderer_svg.py`: `SVGRenderer._taken_ids` (set at the top of `render()` from element and group ids) and `SVGRenderer._def_id(name, suffixes=("",))`, which returns `name`, or `name-def`, `name-def2`, … when a node or group has it. Used for the shadow filter, the arrow markers (`_marker_id_for_color`, with `-tail` checked too) and `minimap-clip`. `renderer_interactive.py` references the filter and clip through `_def_id`.
- Fix 2, `src/diagrams_as_code/renderer_interactive.py`: `OVERLAY_IDS` (`diagram-content`, `svg-pan-zoom-controls`, `diagram-search-input`, `btn-zoom-in`, `btn-zoom-out`, `btn-zoom-reset`, `svg-minimap`, `minimap-viewport`) and `InteractiveOverlay._overlay_ids(text)`, a regex pass that renames those ids via `_def_id` in the overlay markup, stylesheet and script together. `renderer_svg.py` wraps the `<g id="diagram-content">` line with it.
- Tests added at the end of `tests/test_renderer_svg.py`: `test_node_ids_do_not_collide_with_definition_ids` (static and interactive), `test_definition_ids_are_unchanged_without_a_collision`, `test_node_ids_do_not_collide_with_interactive_overlay_ids`, `test_interactive_overlay_ids_are_unchanged_without_a_collision`.
- Output: only `output/cloud/09_iot_cloud_fleet_management.svg` changed (`shadow` → `shadow-def` for the filter and its 7 references). Every example was rerun (`for f in examples/*/*.py; do uv run python "$f"; done`) with no other diff. A scan of all `output/**/*.svg` found 0 files with duplicate ids.
- The regenerated PNG (untracked, gitignored) was looked at: all seven nodes are drawn.
- Docs: `docs/CHANGELOG.md` has two "Fixed" bullets under `[Unreleased]`; `.planning/STATE.md` "Phase 17 result" no longer blames resvg (hand-edited before this checkpoint).
- Gate, macOS py3.14: `uv run pytest -q` → 1126 passed, 1 warning (the expected `LayoutWarning` in `test_unroutable_edge_warns`); `uv run python main.py` ok; `tools/generate_icons.py --check` up to date (63 files); `tools/audit_gallery.py --check` exit 0; `tools/golden_images.py --check` exit 0; `diagrams-as-code lint examples --quiet` exit 0.
- Linux arm64 Docker matrix at `0ffcd26`, py3.10–3.13: 1112 passed + 14 skipped on each; every other gate step exit 0; output, icons, docs and README identical.
- Headless Chrome (`--headless=new --dump-dom`, synthetic events) on an interactive diagram whose nodes use all eight overlay ids plus `shadow`, `arrow`, `minimap-clip`: zoom in/out, reset, wheel zoom, drag-pan, minimap and search all work; nodes keep their ids; screenshot looked at.
- Not verified: real mouse input in a browser (the Chrome extension was not connected); x86-64 never run.

Earlier sessions:
- Phases 12–14: PR #19 merged to master, merge commit `19528dd`. Master then: 727 tests pass.
- Phase 15: PR #20 merged to master, merge commit `3f0f88f` (`gh pr merge 20 --merge`).
- Phase 16: branch `feat/phase16-technical-examples` @ `9aa2d7c`, pushed; PR #21 https://github.com/bsommers/diagrams-as-code/pull/21 against master. Commits: `d292993` lint + named findings + two engine fixes, `31b7be7` eleven technical figures, `4a86680` golden images, `e9ddce8` docs and v0.12.0, `9aa2d7c` planning. PR body holds the reference-figure checklist.
- Local gate on macOS at `9aa2d7c`: 935 tests pass; `main.py`, icons check, audit (all 0, 112 diagrams), `lint examples` (0 findings), golden images (identical), output diff all clean.
- Linux arm64 Docker matrix (`ghcr.io/astral-sh/uv:python3.X-bookworm-slim`, X = 10..13): Phase 15 `99e8509` 879 pass + 2 skip; Phase 16 `9aa2d7c` 933 pass + 2 skip; every other gate step ok on all four versions. The 2 skips are `tests/test_repo_hygiene.py` (no `git` in the image).
- Not verified: the full suite on x86-64 (only golden rendering was checked there, py3.12).
- CI finding: workflow `.github/workflows/ci.yml` is `disabled_manually`; before that every run since 2026-09-26 failed in seconds with "The job was not started because recent account payments have failed or your spending limit needs to be increased". No GitHub checks ran on PRs #19, #20 or #21.

How the Docker matrix was run (the script lived in the session scratchpad and is gone): `git worktree add --detach <dir> <sha>`; mount it read-only at `/src`; in the container `cp -r /src /work && cd /work && rm -f .git && export UV_LINK_MODE=copy && uv sync -q`; then `uv run pytest -q`, `uv run python main.py`, `uv run python tools/generate_icons.py --check`, `uv run python tools/audit_gallery.py --check`, `uv run python tools/golden_images.py --check`, `uv run diagrams-as-code lint examples --quiet`; then `diff -rq -x '*.png' /src/output output`, `diff -rq /src/icons icons`, `diff -rq /src/docs docs`, `diff -q /src/README.md README.md`. Remove the worktree afterwards.

Judgment calls already reported to the user (none objected to):
- Phase 16: bundled Arimo Latin subset fonts in `tests/fixtures/fonts/` (OFL 1.1, ~165 KB, tests only); new audit exemptions (line ending at a point inside a shape, bracket beside shapes nested in a panel, free outlines); figure 1 band frames sized by two empty text struts; caption in plain capitals, not small caps.
- Earlier phases: audit treats an exact bus and a line under its own badge as intended; same-label edges on a shared trunk draw one badge; default edges still use SVG markers; annotations are left out of the BOM.
- Phase 17 (2026-11-14):
  - User: "1 - go; 2 - create missing tags ; 3 start phase 17" — merged PR #21, created and pushed the five tags, built Phase 17.
  - Tag placement: v0.8.4 `9a72b64`, v0.9.0 `c5d4be2` (the commits whose content matches each changelog entry), v0.10.0 `19528dd`, v0.11.0 `3f0f88f`, v0.12.0 `ce7d267` (merge commits).
  - Commits: `932085d` feat(pdf), `0f0e46b` docs, `8eae6b0` planning.
  - Gate at `0f0e46b`: macOS 1121 pass; Linux arm64 Docker py3.10–3.13 1107 pass + 14 skip, every other step ok. x86-64 not run.
  - Design call made without asking: the PDF is drawn from the renderer's SVG (`pdf.svg_to_pdf`) instead of a second display list. Reported to the user.
  - Merged as PR #22 (`41a6af7`) and tagged `v0.13.0`.

## Dead ends (don't retry)
- Treating the fleet-management PNG as a resvg bug — it was a duplicate SVG id in our output.
- A stub `_def_id` on the `InteractiveOverlay` mixin — unneeded; the mixin already calls `SVGRenderer` methods (`_contrast_color`) without declaring them.
- In a test, telling CSS id selectors from hex colours by stripping `: #RRGGBB` — misses colours inside values; match selectors at line start instead.
- Running `main.py` to regenerate a gallery example — it only writes `output/main_*`; run the example script itself.
- Removing `routes[id(edge)]` from the layout result — tests depend on both the edge key and `id(edge)`.
- `metrics.py` importing `text` — violates the same-layer rule in `tests/test_module_boundaries.py`; badge sizing lives in `labels.py`.
- Escaping font-family with `&#x27;` — breaks a theme test; escape without quoting single quotes.
- Greedy line wrapping — leaves orphans; `_wrap_balanced` is the fix.
- Treating shapes that overlap an endpoint box as obstacles in `path_collides` — breaks `test_e2e_fluent_chain_inherits_diagram_curved_routing`.
- STIX font from `master` — 404; use tag `v2.13b171`.
- Editing root `CHANGELOG.md`, `CAPABILITIES.md`, `capabilities.json` separately — they are symlinks into `docs/`; edit once.
- `json.dumps` on `docs/capabilities.json` reformats the whole file; edit it as text.
- Regenerating glyph data needs `uv run --with fonttools python -I tools/generate_text_data.py --math-font … --sans-regular … --sans-bold …`.
- Rounding every number in `transform` shrank math glyphs; scale factors keep places+4.
- Counting crossing lines per segment in badge cost outweighed a node overlap; count per edge.
- Excluding an edge's own endpoints from lane node-collision checks; keep all nodes.
- The repo hygiene test reads the git index, so a symlink fix only passes once staged.
- A container shape painted in the nodes pass hides edges to shapes nested in it; containers are painted before the edges.
- Captions placed from element bounds alone sit on labels drawn outside a shape; `_drawn_extents` is used.
- Global `source.replace("\\n", "\n")` in `text/rich.py` broke `\nabla`, `\neq`, `\nu`; a typed backslash-n is a line break only outside math.
- `Rect` has no `contains`; `Edge` has no `two_way` attribute (use `arrow_head and arrow_tail`).
- Bands have no explicit size; `header_height=0` plus corner struts is the workaround.

Known limits and gaps (also in `.planning/STATE.md` under "Phase 16 result"): no circle/ellipse kind (an unknown `kind` silently draws a box); no self-loop helper; no edge label beside the line; no math accents, `\mathcal`, `\frac`, `\sqrt`; no monospace text; serif text measured with sans metrics; cutting plane drawn over the whole solid. Older review items still open: `min_top <= 30` guess, north-only escape corridor, mirrored corridor code, handle clamping, conservative `intersects_rect`.

Optional follow-ups (none requested): circle/ellipse kind, self-loop helper, edge labels beside the line, `\frac`/`\sqrt`/accents, monospace text, PDF font embedding, x86-64 run, browser check of a clashing interactive diagram.

## Working-tree state
- Branch: `fix/svg-id-collisions` @ `0ffcd26`, tracking `origin/fix/svg-id-collisions`, in sync. `master` @ `41a6af7`.
- `git status --short`:
  ```
   M .planning/STATE.md
  ?? .planning/CHECKPOINT.md
  ?? graphify-out/
  ```
  `.planning/STATE.md` holds only the session record written by `gsd-tools state.record-session` after the push (not in PR #23; commit it with the next planning change). The two untracked entries stay out of commits.
- Stashes: none · Background jobs/agents: none · Async GSD jobs: none · Ports: none · Worktrees: only the main one.

## Authorizations and scope (RE-CONFIRM after reset)
- Done with approval: commit, push, PR #23. NOT authorized: merging PR #23, tagging or releasing.
- Do not re-enable or trigger GitHub Actions; verification is local (the workflow is `disabled_manually`).
- The auto-mode classifier denies `gh pr merge` and `git push` of tags; the user runs those with `!`.
- Merges use `gh pr merge N --merge`; the repo does not delete branches on merge.
- Outward-facing actions (push, PR, merge, tags) need fresh confirmation each time.

## Baseline check
- `uv run pytest -q` → 1126 passed, 1 warning (macOS py3.14, 2026-11-14).
- `git status --short` → the three entries above.

## Exact next command
Ask the user whether to merge PR #23. On yes, the user runs `! gh pr merge 23 --merge`; then `git switch master && git pull`. If the user wants a release, it would be a patch (`v0.13.1`): bump the version, move the `[Unreleased]` bullets under it, rerun the gate, and the user pushes the tag with `!`.
