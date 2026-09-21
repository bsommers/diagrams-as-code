# Auto-Layout, CLI, and Modularity — Design

**Date:** 2026-09-21 · **Status:** approved in brainstorming, pending spec review · **Target:** v0.4.0

## 1. Goal

1. **Auto-layout.** A diagram may omit positions and have the engine place shapes and groups from the edge structure. Manual placement keeps working, and the two mix: auto-layout first, then manual adjustment in code or in an editable layout file.
2. **CLI.** A real `diagrams-as-code` command replaces `main.py` and the batch one-liner in `docs/running.md`.
3. **Modularity.** Build is separate from render, placement is separate from the diagram model, and PNG backends and icon glyphs live in their own modules, with import direction enforced by a test.

**Non-goals (v1):** obstacle-avoiding edge routing; auto-placing *around* pinned shapes; a declarative JSON/YAML diagram format; an interactive editor; any new runtime dependency (`dependencies = []` stays empty).

## 2. Compatibility contract

- `Diagram(layout=...)` defaults to `"manual"`. **Every existing diagram renders byte-identically.** The CI guard (`git diff --exit-code -- output/`) is the proof, and it applies to every refactor in this spec.
- Default element ids (`shape_N`, `group_N`) do not change.
- `build_diagram(output_dir)` keeps its signature and return value in all examples; `tests/test_domain_examples.py` passes unmodified.
- `iiot_diagrams` facade re-exports every new public symbol.

## 3. Architecture

New and changed modules under `src/diagrams_as_code/`:

```
layout/
  __init__.py      public: LayoutEngine, LayeredLayout, LayoutWarning, load_layout_file, export_layout
  base.py          LayoutEngine protocol, LayoutGraph/LayoutNode/LayoutEdge dataclasses
  graph.py         build_layout_graph(diagram) -> LayoutGraph
  layered.py       LayeredLayout engine
  sidecar.py       layout-file keys, load, apply, export
  pipeline.py      run_layout(diagram): the ordered solve pipeline (§4.3)
rasterize.py       PNG backends as an ordered list of functions (moved from Diagram.render_png)
output.py          render_all(diagram, out_dir, stem, formats) — shared file writing
icon_glyphs.py     name -> glyph function table (moved from ShapeLibrary._render_icon_content)
cli.py             argparse CLI; __main__.py calls cli.main()
```

**Dependency direction** (enforced by `tests/test_module_boundaries.py`, which parses imports with `ast`):
`geometry` → `elements`, `connections`, `groups` → `constraints`, `layout` → `diagram` → `output`, `rasterize` → `cli`.
Lower layers never import higher ones. `layout/` never imports `diagram` (it receives the diagram duck-typed through `graph.py`'s input protocol) and never mutates elements except in `pipeline.py`.

## 4. Auto-layout

### 4.1 API

```python
Diagram(title, ..., layout="manual" | "auto", direction="LR" | "TB",
        layout_file: str | Path | None = None,
        rank_gap: float = 80.0, node_gap: float = 40.0)
```

- `layout="auto"` enables §4.3 step 1. `direction` is the rank axis (LR: ranks are columns, flow left→right).
- With `layout="auto"`, the canvas `width`/`height` grow to fit content plus the framing margin; they never shrink below the values passed.
- Invalid `layout`/`direction` values raise `ValueError` at construction.

### 4.2 Layout graph

`build_layout_graph` produces, for each *scope* (the diagram root and each group), the direct children of that scope as nodes (a child group is one node with its laid-out size) and the edges between them. An edge whose endpoints sit in different subtrees is **lifted**: at each scope it becomes an edge between the two ancestors that are direct children of that scope; lifted edges inside the same node are dropped. Parallel lifted edges collapse into one with a weight.

A node is **pinned** if its element has any constraint (`.at`, `.move_to`, `.right_of`, etc.) or a layout-file entry. Pinned nodes are excluded from auto-placement and edges touching them are ignored by the engine.

### 4.3 Solve pipeline (`layout/pipeline.py`)

`Diagram.solve()` delegates to `run_layout(diagram)`, which runs:

1. **Auto-place** (only if `layout="auto"`): scopes are processed bottom-up (deepest groups first). For each scope, `engine.arrange(graph)` returns `{node_id: Point}` for unpinned nodes relative to the scope origin; the pipeline stores each as an absolute constraint tagged `"source": "auto"`, translated by the group's padding and header height. Group sizes feed the parent scope. Auto-tagged constraints are cleared at the start of every run, so `solve()` is idempotent and auto-placed nodes never count as pinned.
2. **Layout-file overrides**: each matching entry replaces the element's constraints with an absolute one (§4.5).
3. **Constraint solve**: existing `ConstraintSolver.solve()`, unchanged. Relative constraints may target auto-placed elements.
4. **Group bounds**: bottom-up `calculate_bounds()`, as today.
5. **Framing**: the negative-bounds translation currently in `Diagram.solve()` moves here, unchanged in behavior. With `layout="auto"`, canvas growth (§4.1) is applied after framing.
6. **Overlap check**: any overlap between a pinned element and an auto-placed sibling emits `LayoutWarning` (a `UserWarning` subclass) naming both labels. Overlaps between two auto-placed nodes cannot occur (§4.4 invariant) and are asserted in tests, not checked at runtime.

With `layout="manual"` and no layout file, steps 1, 2 and 6 are no-ops, and the pipeline produces exactly today's coordinates.

### 4.4 `LayeredLayout` engine

Input: one scope's `LayoutGraph` (nodes with width/height in declaration order, directed weighted edges). Output: top-left `Point` per unpinned node. Pure, stdlib only, deterministic: no sets iterated without sorting, no randomness, ties broken by declaration index.

1. **Cycle breaking** — DFS in declaration order; back edges are reversed for ranking only (arrow direction in the rendered diagram is unchanged).
2. **Ranking** — longest-path from sources; isolated nodes get rank 0.
3. **Ordering** — initial order within each rank by declaration index, then 4 alternating down/up barycenter sweeps; a sweep's result is kept only if it lowers the weighted crossing count.
4. **Coordinates** — rank *r* is placed at `sum(max extent of ranks < r) + r * rank_gap` along the rank axis; within a rank, nodes are stacked with `node_gap` and the rank is centered on the widest rank. Nodes are centered on the rank's axis line.

**Invariants (tested):** no two unpinned nodes' rects overlap; for every non-reversed edge `u→v`, `rank(u) < rank(v)`; identical input yields identical output.

### 4.5 Layout file (sidecar)

JSON, UTF-8, sorted keys, 2-space indent, trailing newline (stable diffs):

```json
{
  "version": 1,
  "positions": {
    "Cloud Platform (UNS Tier)": {"x": 420.0, "y": 80.0},
    "Cloud Platform (UNS Tier)/Enterprise MQTT Broker": {"x": 450.0, "y": 150.0}
  }
}
```

- **Key** = the element's explicit `id=` if one was passed, else its label path: ancestor group labels and its own label joined by `/`. (`Element` records whether its id was explicit.)
- Coordinates are absolute top-left, after framing — what you see in the SVG.
- **Load** (`layout_file=` or `--layout-file`): missing file → no-op; malformed JSON or unknown `version` → `ValueError` naming the file; a key matching no element → `LayoutWarning` ("stale layout entry: …").
- **Export** (`export_layout(diagram, path)` / `diagrams-as-code layout export`): writes positions for every shape and group after a full solve. If two elements share a key → `ValueError` listing them, advising `id=`.
- Round-trip property: export, then render with that file, gives identical coordinates.

## 5. Script contract and output

- Each diagram script defines **`def diagram() -> Diagram`**: build and return, no file I/O.
- A script may define **`OUTPUT_STEM = "<name>"`**; otherwise the stem is the file stem.
- `output.render_all(diag, out_dir, stem, formats=("svg", "png", "bom"), readme_name=None)` writes `<stem>.svg`, `<stem>.png`, and the BOM as `readme_name` or `<stem>_README.md` (linking `<stem>.svg`), and returns the written paths.
- All 80 domain examples, the 3 top-level examples and `main.py` are converted: existing body → `diagram()`; `build_diagram(output_dir)` becomes `render_all(diagram(), output_dir, "<stem>")` and returns the SVG path as before. The conversion is done by a one-off script, and each converted file is verified by the byte-identical `output/` guard. Current names are preserved: the 80 domain examples already use their file stem; the 3 top-level examples get `OUTPUT_STEM` without the number prefix (`mockup_slide`, `high_availability`, `sparkplug_pipeline`); `main.py` gets `OUTPUT_STEM = "main_architecture"` and passes `readme_name="main_README.md"`.

## 6. CLI (`cli.py`)

Installed as `[project.scripts] diagrams-as-code = "diagrams_as_code.cli:main"`; also `python -m diagrams_as_code`.

```
diagrams-as-code render PATH... [--out DIR] [--format svg,png,bom]
                                [--layout manual|auto] [--direction LR|TB]
                                [--theme NAME] [--layout-file FILE] [--debug]
diagrams-as-code layout export SCRIPT [-o FILE]
diagrams-as-code themes
diagrams-as-code icons [--domain NAME]
```

- `PATH` is a script or a directory (recursed for `*.py` defining `diagram()`, sorted). Scripts are loaded with `importlib` under a unique module name; one failing script does not stop the others.
- Flags override the returned diagram's settings before solving (`Diagram` gains a `configure(layout=, direction=, theme=, layout_file=)` method that raises if already solved).
- `--out` defaults to `output/`; for a directory input, outputs mirror the input's subdirectories (so `render examples/` reproduces today's `output/<domain>/`).
- **Exit codes:** 0 all succeeded; 1 any script failed to load or render; 2 usage error (argparse). Failures print `error: <script>: <message>` to stderr; `--debug` adds the traceback.
- `layout export` defaults `-o` to `<script stem>.layout.json` beside the script and uses the script's own `layout` setting unless `--layout` is given.
- `main.py` keeps `generate_main_architecture(output_dir)` and `python main.py [OUT_DIR]`; its body becomes `diagram()` plus one `render_all` call, with the same output paths and printed lines.

## 7. Modularity cleanups (byte-identical output)

| Change | From | To |
|---|---|---|
| PNG backends | 4 inline `try` blocks in `Diagram.render_png` | `rasterize.BACKENDS`: ordered list of `(name, fn)`; `render_png` loops. Same order, same error text. `tests/test_dependency_catalog.py` is updated to read the list. |
| File writing | `render_svg(path)` etc. plus per-script boilerplate | `output.render_all`; `render_svg(path)` keeps working. |
| Icon glyphs | 486-line `if/elif` in `ShapeLibrary._render_icon_content` | `icon_glyphs.GLYPHS: dict[str, Callable]`; `_ICON_CATALOG` stays in `shapes.py` for `tools/generate_icons.py`. |
| Theme overrides | field-by-field copy in `Diagram.__init__` | `dataclasses.replace(base, name=f"{base.name}_custom", **overrides)` |
| Framing | inside `Diagram.solve()` | `layout/pipeline.py` step 5 |

## 8. Testing (TDD, red → green per unit)

- `tests/test_layout_layered.py` — pure graphs: chain, diamond, fan-out, cycle, disconnected, weighted parallel edges; rank order, crossing count on known graphs, no-overlap and determinism invariants, LR vs TB.
- `tests/test_layout_graph.py` — edge lifting across nested groups; pinned detection.
- `tests/test_layout_pipeline.py` — auto + pinned mix, relative constraint targeting an auto-placed node, `LayoutWarning` on pinned overlap, canvas growth, manual mode unchanged.
- `tests/test_layout_sidecar.py` — key derivation, round-trip, stale key warning, duplicate key error, malformed file error.
- `tests/test_cli.py` — in-process `main(argv)` and one subprocess smoke run against `tmp_path`: each subcommand, exit codes 0/1/2, directory mirroring, flag overrides.
- `tests/test_module_boundaries.py` — import direction (§3).
- **Visual gate:** one new example per domain with `layout="auto"` (8 files, `examples/<domain>/11_auto_*.py`), rendered into `output/` and covered by the existing CI guard. Each must also pass the existing per-example checks (valid SVG, BOM, ≥3 themes per domain). `tests/test_domain_examples.py`'s expected count changes from 80 to 88 (8 domains × 11); the docs that say "80 examples" are updated in step 6.

## 9. Documentation

`docs/how-to.md` (auto-layout and layout-file walkthrough), `docs/running.md` (CLI replaces the batch one-liner), `docs/architecture.md` (layout pipeline stage, module list), `README.md` quick start, `CHANGELOG.md` `[Unreleased]`, `CAPABILITIES.md`/`capabilities.json` (new `CAP-DIAG-LAYOUT` and `CAP-DIAG-CLI`).

## 10. Build order

Each step lands green with `output/` unchanged, except step 6, which adds only new files.

1. Modularity refactors (§7) — no behavior change.
2. `diagram()` contract + `output.render_all` + example conversion (§5).
3. Layout graph + `LayeredLayout` engine (§4.2, §4.4) — pure, unwired.
4. Pipeline + `Diagram(layout=...)` (§4.1, §4.3).
5. Layout file (§4.5).
6. CLI (§6), `main.py`, auto-layout examples, docs.
