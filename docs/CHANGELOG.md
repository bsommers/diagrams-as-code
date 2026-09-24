# Consolidated Master Changelog: Diagrams as Code (IIoT Engine)

All notable changes, architectural milestones, and capability updates to the pure-Python Directed Diagrams as Code framework (`diagrams_as_code`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), adhering to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), Standard 44 (*Pre-Commit Changelog & Documentation Synchronization*), and Standard 45 (*Continuous Capability Manifest Synchronization*).

## [Unreleased]

## [v0.6.0] - 2026-09-23

### Added
- **CLI Interactive Export Flags (`CAP-DIAG-CLI-INTERACTIVE`, `CLI-INTER-01` to `CLI-INTER-04`):**
  - Added `--interactive` and `--no-interactive` flags to `diagrams-as-code render` subcommand in `src/diagrams_as_code/cli.py`.
  - Added tri-state override forwarding to `Diagram.configure(interactive=...)`, preserving script-authored configuration by default.
  - Enabled batch directory rendering with `--interactive` across all discovered diagram scripts.
  - Added unit and subprocess integration tests in `tests/test_cli.py`.
- **Client-Side Search & Node Highlighting (`CAP-DIAG-SEARCH`, `SEARCH-01` to `SEARCH-03`):**
  - Integrated a lightweight search input field into the interactive HUD controls via responsive XHTML `<foreignObject>`.
  - Implemented real-time dynamic substring matching against node IDs and labels, dimming non-matching nodes to 20% opacity and non-incident edges to 15% opacity.
  - Added Escape key and clearing handler to restore original element opacities.
  - Retained strict XML parseability and 100% byte invariance for non-interactive rendering.
- **Viewport Minimap Navigator (`CAP-DIAG-NAVIGATOR`, `MINIMAP-01` to `MINIMAP-03`):**
  - Added a pinned overview minimap thumbnail widget in the bottom-right corner of interactive SVG canvases.
  - Implemented scaled diagram rendering (`<use href="#diagram-content">`) within a clipped viewport.
  - Added a responsive viewport rectangle (`#minimap-viewport`) tracking visible diagram bounds on zoom and pan.
  - Implemented click-and-drag navigation on the minimap to smoothly pan the diagram view across large topologies.

### Verification Evidence
- `uv run pytest` -> 447 passed in 11.5s across all unit, integration, boundary, and hygiene test suites.
- `git diff --exit-code -- output/ icons/ README.md` -> Zero byte drift across all domain diagrams.
- `tests/test_module_boundaries.py` -> 100% compliant with strict downward architectural layering.
## [v0.5.0] - 2026-09-23

### Added
- **Interactive SVG Pan-Zoom and Collapsible Groups (`CAP-DIAG-INTERACTIVE`, `INTER-01` to `INTER-03`):**
  - Added `interactive: bool = False` flag to `Diagram.__init__`, `Diagram.configure()`, and `Diagram.render_svg()`.
  - Added pure client-side SVG interaction with zero external binary or JavaScript dependencies.
  - Implemented responsive mouse-drag canvas panning, cursor-centered scroll wheel zooming, and fixed-viewport HUD controls (`#svg-pan-zoom-controls`) featuring Zoom In, Zoom Out, and Reset buttons.
  - Implemented collapsible hierarchical container groups with interactive click toggles (`▼` / `▶`) on group headers and recursive visibility management across child shapes, nested sub-groups (preserving nested collapse states), and incident edges.
  - Enclosed inline JavaScript within `<![CDATA[ ... ]]>` inside `<script type="text/javascript">` to guarantee strict XML parser and ElementTree compatibility. Default rendering (`interactive=False`) remains 100% byte-identical and zero-script.
- **Typed Constraint Dataclasses (`ARCH-01`):**
  - Introduced typed dataclasses `AbsoluteConstraint`, `RelativeConstraint`, and `AlignConstraint` inheriting from base `Constraint` and `collections.abc.MutableMapping` for seamless dictionary duck-typing.
  - Added `align_with()` multi-axis alignment supporting horizontal/vertical center, left, right, top, and bottom alignment constraints.
- **Group Flow Layout Engine Decoupling (`ARCH-02`):**
  - Created `diagrams_as_code.layout.flow` housing `GroupFlowLayout` protocol and engine classes `VerticalFlowLayout`, `HorizontalFlowLayout`, and `GridLayout`.
  - Decoupled `Group` (Layer 2) from `layout` (Layer 4) via a dynamic layout registry (`register_group_layout`, `get_group_layout_engine`), ensuring strict acyclic module boundaries.
  - Added `Group.flow(engine, **kwargs)` accepting either instantiated layout engines or registered mode names.
- **CI Quota Conservation & Local-First Directives:**
  - Added local-first testing and artifact verification directives to `AGENTS.md` and `.cursor/rules/uv.md`.
  - Added concurrency cancellation (`cancel-in-progress: true`) and path filtering to `.github/workflows/ci.yml`.
  - Symlinked `CLAUDE.md` and `GEMINI.md` to `AGENTS.md` for consistent cross-tool constraint enforcement.

### Fixed
- **CLI Output Collision Validation (`POLISH-01`):** Validated `--out` path collisions against existing regular files before executing diagram scripts, reporting a clear error attributing the collision to `--out`.
- **Graph Builder Descendant Traversal Memoization (`POLISH-02`):** Memoized descendant pin state traversal in `layout/graph.py` to eliminate redundant $O(n \cdot \text{depth})$ subtree walks.
- **Stable Edge Waypoint Keying (`POLISH-03`):** Replaced transient `id(edge)` dictionary keys in `layout/pipeline.py` with direct `Edge.waypoints` attribute storage.
- **Import Ordering & Cleanup (`POLISH-04`):** Cleaned up unused imports in `tests/test_dependency_catalog.py` and alphabetized imports in `diagram.py`.

### Verification Evidence
- `uv run pytest` -> 439 passed in 11.3s across all unit, integration, boundary, and hygiene test suites.
- `git diff --exit-code -- output/ icons/ README.md docs/` -> Zero byte drift across all 88 domain diagrams.
- `tests/test_module_boundaries.py` -> 100% compliant with strict downward architectural layering.

## [v0.4.0] - 2026-09-22

### Added
- **Auto-layout (`Diagram(layout="auto")`):** a deterministic layered engine places unpinned shapes and groups from the edge structure, left-to-right or top-to-bottom. Shapes placed with `.at()` or `.right_of()` stay pinned, relative placement can target auto-placed shapes, and a `LayoutWarning` names any pin that overlaps an auto-placed sibling.
- **Layout file:** `diagrams-as-code layout export` writes every position to a JSON file keyed by label path or explicit `id=`; hand edits are applied as overrides on the next render, and a group entry moves the whole group.
- **`diagrams-as-code` command:** `render`, `layout export`, `themes`, `icons`; also `python -m diagrams_as_code`.
- **8 auto-layout gallery examples** (`examples/<domain>/11_auto_*.py`), bringing the gallery to 88.

### Changed
- Scripts define `diagram() -> Diagram`; files are written by `output.render_all`. Existing `build_diagram()` functions keep working.
- Internals split for modularity: PNG backends in `rasterize.py`, icon glyphs in `icon_glyphs.py`, the active-diagram stack in `context.py`, label metrics in `metrics.py`, and the solve pipeline in `layout/pipeline.py`, which now also routes edges so the renderer only draws. `tests/test_module_boundaries.py` enforces import direction. Rendered output of all existing diagrams was byte-identical through the modularity and layout work; the canvas-growth fix below changed 15 of them (see Fixed).
- `Diagram.render_png()` returns the PNG bytes for every backend (CairoSVG previously returned `None`).

### Fixed
- **Canvas growth is unconditional:** the canvas now grows to fit any content that lands outside it — hand-placed coordinates in `manual` mode included, not just auto-layout or a layout file. 15 of the 92 committed diagrams were clipped this way; their SVG `width`/`height` grew (`1200`→`1290`, `1540`, or `1790`) and no artwork moved.

## [v0.3.0] - 2026-09-21

### Added
- **Canonical Package `diagrams_as_code` (`src/diagrams_as_code/`):** The engine moved from `iiot_diagrams` to `diagrams_as_code`. `src/iiot_diagrams/` remains as a facade that re-exports every public symbol, so existing `import iiot_diagrams` code keeps working.
- **IIoT Domain Gallery (`examples/iiot/`):** IIoT became the eighth example domain, bringing the gallery to 80 diagrams.
- **PNG and BOM Output for Every Example:** Each example script writes an SVG, a PNG, and a Markdown Bill of Materials to `output/<domain>/`.
- **Container Fonts and Compose File:** The Docker image installs `fonts-dejavu-core` so rasterized labels render with a real font, and `docker-compose.yml` defines the `diagram-gen` service with `output/` mounted.
- **Expanded Theme Engine (`src/diagrams_as_code/theme.py`):** Added 5 new built-in themes (`solarized_light`, `pastel_light`, `dracula`, `synthwave`, `high_contrast`), expanding the palette to 13 themes (8 dark, 4 light, 1 accessibility WCAG AAA). Added `list_themes()`, `get_light_themes()`, `get_dark_themes()`, `create_theme()`, and direct `Theme` instance or `theme_overrides` injection in `Diagram.__init__`.
- **Anti-Spill Label Wrapping & Text-Below-Graphic (`src/diagrams_as_code/renderer_svg.py`, `elements.py`):**
  - Implemented multi-line text wrapping via SVG `<tspan>` tags and dynamic font scaling (10px–12px) to permanently prevent labels from spilling outside shape boundaries.
  - Implemented `label_position="bottom"` (or `"below"`) to place labels cleanly underneath compact graphic tiles.
  - Implemented `kind="icon"` for borderless standalone vector icon nodes (like Cisco / AWS architecture schematics).
- **5 Theme Varieties per Domain (80 Diagrams):** Updated all 80 reference architecture scripts across all 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`) to showcase 5 distinct theme varieties per domain, with widened group margins (`margin=90`) to prevent protocol badge line overlap.
- **Complete Documentation Suite (`docs/` & `docs/diagrams/`):**
  - Authoring of `docs/README.md`, `docs/purpose.md`, `docs/architecture.md`, `docs/running.md`, and `docs/how-to.md`.
  - Authoring of `docs/sources.md` and `icons/README.md` cataloging upstream provenance, design systems, and the license of each of the 60 vector icons and every build dependency.
  - Authored multi-format visual architecture diagrams in `docs/diagrams/`: terminal ASCII schematic (`ascii_architecture.txt`), Mermaid flowchart (`architecture.mmd`), Mermaid sequence lifecycle (`execution_lifecycle.mmd`), and native Draw.io XML (`architecture.drawio`).
  - Updated root `README.md` with badges, 8-domain showcase, and documentation hub links.
- **Automated Verification:** Added `test_domain_theme_variety`, `test_text_wrapping_multiline_tspan`, `test_label_position_bottom`, `test_kind_icon_pure_rendering`, and `test_theme_expansion_and_helpers`.

### Changed
- **Generated Icon Catalog (`tools/generate_icons.py`, `src/diagrams_as_code/shapes.py`):** `ShapeLibrary._ICON_CATALOG` is now the single source of truth for icons, mapping each of the 60 canonical names to one domain directory and one description; `_CANONICAL_ICONS` is derived from it. The entire `icons/` tree, `icons/icons.csv`, `icons/icons.yaml`, and `icons/README.md` are emitted from that catalog by `tools/generate_icons.py`, which also provides `--check` for CI. Standalone icon files and the glyphs the renderer draws are now the same artwork by construction.
- **Icon Tree Reconciled (59 → 60 files):** Added the missing `dashboard`, `database`, and `queue` icon files, which the engine rendered but the catalog never shipped. Removed the duplicate `computer/sensor.svg` and `iiot/plc.svg`, so each icon has exactly one domain home.
- **Relative Documentation Links:** Replaced 127 `file:///home/bill/...` absolute links across `README.md`, `docs/`, `examples/README.md`, and `icons/README.md` with repository-relative paths that resolve for every reader and on GitHub.
- **Icon Provenance Corrected (`docs/sources.md`, `icons/README.md`):** The provenance section credited the bundled icons to Lucide, Feather, Tabler, Cisco, CNCF, and AWS with per-glyph derivation claims, and labeled the Cisco and AWS icon programs with two invented license names, neither of which exists (both are conditional brand-asset terms, not open-source licenses). The glyphs are original geometry emitted by `ShapeLibrary._render_icon_content` as SVG primitives on the 24x24 grid — `icons/datacenter/kubernetes.svg` is a circle with eight spokes, not the seven-sided CNCF helm. The table was replaced with an authorship statement (original work, MIT), a "visual conventions, not sources" note, and a vendor-names note pointing at Cisco's and AWS's actual terms pages rather than inventing license names. The retraction is recorded in the document itself.
- **Dependency Catalog Completed (`docs/sources.md`):** The catalog listed only the first of the four PNG backends `Diagram.render_png()` tries. CairoSVG (LGPL-3.0-or-later), Inkscape (GPL-3.0-or-later), and ImageMagick are now listed with their real licenses and with how each is used — imported into the process, or located on `PATH` and run as a subprocess. A new section catalogs what the container image redistributes: the `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` base image, the Debian 12 layer, and `fonts-dejavu-core`. The blanket claim of "permissive" licensing was removed, since two of the backends are copyleft.
- **Dependency Provenance Corrected (`docs/sources.md`):** `resvg-py` is credited to `baseplate-admin/resvg-py` under MIT (verified against the installed distribution metadata) and recategorized from "Dev Dependency" to "Optional Runtime", since `Diagram.render_png()` imports it at runtime.

### Fixed
- **Diagrams Collapsing to the Origin:** Rendering inside the `with Diagram(...)` block ran before layout was solved, and unanchored groups with negative coordinates were clipped, so shapes stacked at `(0, 0)`. `render_svg()`, `render_png()`, and `generate_readme()` now solve any unsolved layout first, the canvas is translated to frame negative bounds, and the examples render after the context manager exits. See `docs/LAYOUT_ROOT_CAUSE.md`.
- **Rendered Output Verified in CI:** The 84 rendered PNGs are no longer tracked (their bytes depend on the rasterizer backend) and are gitignored. The SVGs and BOM Markdown in `output/` stay tracked, and CI fails if the suite's re-render of them differs from the commit.
- **Duplicated Files Removed:** `docker_compose.yml` (a copy of `docker-compose.yml`) was deleted; `RUNNING.md` became a symlink to `docs/running.md`; `docs/ARCHITECTURE.md`, which collided with `docs/architecture.md` on case-insensitive filesystems, was merged into it. `tests/test_repo_hygiene.py` rejects case collisions and byte-identical copies.
- **`main.py` No Longer Overwrites `README.md`:** `generate_root_readme()` rebuilt the repository README from a hardcoded template that had fallen 91 lines behind the maintained file, so every `uv run python main.py` — including the CI "Verify diagram generation" step — silently reverted edits to it. The function and its call were removed; the Bill of Materials continues to be emitted to `output/main_README.md`.
- **CI Guards Generated Artifacts (`.github/workflows/ci.yml`):** A new step runs `tools/generate_icons.py --check` and `git diff --exit-code -- README.md docs/ icons/` after diagram generation, failing the build if a generator rewrites a tracked file or if the committed icon tree drifts from the catalog.
- **Project License Published:** Added the `LICENSE` file (MIT) that `pyproject.toml` declared and `README.md` linked to but which was never committed.
- **Stale Dependency Manifest Removed:** Deleted `requirements.txt`, which listed `diagrams`, `pyyaml`, `gitpython`, and `boto3` — none imported anywhere in the tree — and contradicted `dependencies = []` in `pyproject.toml`. `pyproject.toml` with `uv.lock` is the single source of truth.
- **Documentation Counts and Stroke Claims:** Corrected the icon total from 59 to 60 in `README.md`, `docs/sources.md`, and this changelog. `docs/sources.md` no longer claims uniform round line-caps and line-joins across the set; `icons/README.md` now measures and reports stroke weights from the emitted files.
- **Package Version Synchronized:** `pyproject.toml` and `src/diagrams_as_code/__init__.py` report `0.3.0`, matching this changelog section.

### Verification
- `tests/test_icon_provenance.py` adds 6 tests: no fabricated license name may be asserted outside a quoted retraction, a derivation claim naming an upstream set and a license must ship that license text under `icons/licenses/`, and `docs/sources.md` and the generated `icons/README.md` must agree on authorship.
- `tests/test_dependency_catalog.py` adds 4 tests that read the real `render_png()` fallback chain and the real `Dockerfile`, failing if a rasterizer, a base image, or an `apt`-installed package is absent from `docs/sources.md`.
- `tests/test_icon_catalog.py` adds 76 tests binding the catalog, the generated tree, the manifests, the alias table, and the documented totals together. Drift in any of them fails the suite.

## [v0.2.0] - 2026-09-19

### Added
- Standardized project packaging via `pyproject.toml` with `hatchling` backend and `uv` dependency management.
- Pinned dependency lockfile `uv.lock` for deterministic, reproducible builds.
- Official Astral `uv:python3.12-bookworm-slim` multi-stage `Dockerfile` and container runner `docker-build-n-run.sh`.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) testing matrix across Python 3.10-3.13 with `astral-sh/setup-uv`.
- Universal repository agent guidelines (`AGENTS.md`, `.cursor/rules/uv.md`) enforcing `uv` across all workflows.
- **Domain Vector Icon Catalog (`icons/`):** 51 handcrafted 24x24 open-source W3C SVG icons spanning 7 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`), cataloged in `icons/icons.yaml` and `icons/icons.csv`.
- **Native Shape Library Icon Integration (`src/iiot_diagrams/shapes.py`):** Subsumed all 51 icons natively into `ShapeLibrary` and implemented `register_svg_icon()`, `load_icon_file()`, and `load_icons_from_directory()`.
- **Expanded Color Theme Presets (`src/iiot_diagrams/theme.py`):** Added 4 new presets (`nord`, `emerald`, `crimson`, `monochrome`), expanding the palette to 8 distinct themes.
- **70 Executable Domain Reference Diagrams (`examples/`):** 10 architectural diagrams per domain across 7 domains of varying complexity, generating SVG vector diagrams and Markdown BOM tables in `output/`, cataloged in `examples/README.md`.
- **Domain Examples Test Suite (`tests/test_domain_examples.py`):** Automated parametrized test suite verifying execution, XML structure, and BOM generation across all 70 domain examples.

### Changed
- Migrated all execution, testing, and documentation commands across plans and manifests to `uv run pytest` and `uv sync`.
- **Root Directory Cleanup:** Relocated orphaned exploratory/scratch scripts and chat notes to `legacy/`.

## [v0.1.0] - 2026-09-19

### Added
- **Core Geometry & Coordinate Engine (`src/iiot_diagrams/geometry.py`):**
  - Geometric primitives: `Point`, `Size`, `Rect` with 9 `Anchor` positions (`TOP_LEFT`, `CENTER`, `BOTTOM_RIGHT`, etc.).
  - Bounding box math: `union()` and `expand()` with directional padding.
  - `UnitBasis`: Normalized coordinates (0.0 to 1.0 or percentage strings `'50%'`) mapped to diagram dimensions.
- **Decoupled Elements & Constraint Solver (`src/iiot_diagrams/elements.py`, `src/iiot_diagrams/constraints.py`):**
  - `Element` base class and `Shape` entity model with decoupled lifecycle: can exist unplaced, be placed late, relocated via `.move_to()` or `.translate()`, and cloned via `.clone()`.
  - Directional placement methods: `.right_of()`, `.left_of()`, `.below()`, `.above()` with custom margins and alignments.
  - Topological DAG `ConstraintSolver` resolving dependencies with cycle detection and unconstrained element retention.
- **Hierarchical Grouping & Flow Placement (`src/iiot_diagrams/groups.py`):**
  - Container element `Group` with dynamic bottom-up auto-bounding encapsulating children, headers, and padding.
  - Group-to-group flow placement (`group2.below(group1)`, `group2.right_of(group1)`) propagating child coordinate translations.
  - Internal layout helpers (`vertical_flow`, `horizontal_flow`, `grid`) and cycle prevention in ancestry.
- **Connection Model & Smart Orthogonal Router (`src/iiot_diagrams/connections.py`, `src/iiot_diagrams/router.py`):**
  - `Edge` connection model with `Port` anchors (`NORTH`, `SOUTH`, `EAST`, `WEST`) and `Routing` styles (`ORTHOGONAL`, `DIRECT`, `CURVE`).
  - `OrthogonalRouter` implementing Manhattan waypoint routing, automated port deduction based on relative geometry, and collinear segment simplification.
- **Theming & Vector Shapes (`src/iiot_diagrams/theme.py`, `src/iiot_diagrams/shapes.py`):**
  - Theme presets: `iiot_dark_gold`, `iiot_light`, `blueprint`, `cyber_slate` with registration and reset helpers.
  - Vector shape generators: `render_box`, `render_cylinder`, `render_server_rack`, `render_database`, `render_cloud`, `render_diamond`, `render_badge`.
  - Built-in IIoT vector icons: `sensor`, `gateway`/`edge`, `broker`, `database`/`influx`, `queue`/`kafka`, `cloud`, `dashboard`/`grafana`.
- **Pure-Python Standalone SVG Renderer (`src/iiot_diagrams/renderer_svg.py`):**
  - Zero-binary vector SVG generator with `viewBox`, drop shadows, arrowhead markers, nested group clipping, and contrast-aware protocol badges.
- **Fluent Diagram API & Context Manager (`src/iiot_diagrams/diagram.py`):**
  - Context manager `with Diagram(...) as diag:` supporting operator overloading: `s1 >> s2`, `s1 >> diag.edge(...) >> s2`, fan-in and fan-out lists.
  - Automated group scoping (`with diag.group(...) as g:`) and bottom-up bounds resolution.
- **Bill of Materials (BOM) & Living Documentation (`src/iiot_diagrams/bom.py`):**
  - `BOMGenerator` extracting component inventory, parent groups, and connection metadata into Markdown tables and JSON catalogs.
  - `diag.generate_readme()` synchronizing diagram graphics and BOM tables into root documentation.
- **Runnable Architectural Examples (`examples/`):**
  - `01_mockup_slide.py`: Plant-to-cloud remote monitoring slide with 3 columns, group flow, and MQTT bridge.
  - `02_high_availability.py`: High-availability cluster with load balancer and peer discovery edges.
  - `03_sparkplug_pipeline.py`: Sparkplug B edge pipeline with brokers, message queues, and time-series database.
  - `main.py`: Production entrypoint generating `output/main_architecture.svg` and `README.md`.
- **Comprehensive 10-Suite Test Harness (`tests/`):**
  - 139 tests covering unit, integration, CLI subprocess execution with `tmp_path` isolation, and end-to-end workflows.
  - Strict type checking via `mypy` across 26 source files with 0 errors.

### Changed
- Replaced legacy `mingrammer/diagrams` (Graphviz `dot`) reliance with pure Python geometry and SVG vector rendering.
- Scrubbed all proprietary/vendor branding in favor of generic, customizable Industrial IoT (IIoT) terminology.

### Verification Evidence
- `uv run pytest`: 139 passed in 0.35s.
- `mypy src/ tests/ examples/ main.py`: Success: no issues found in 26 source files.
