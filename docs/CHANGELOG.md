# Consolidated Master Changelog: Diagrams as Code (IIoT Engine)

All notable changes, architectural milestones, and capability updates to the pure-Python Directed Diagrams as Code framework (`iiot_diagrams`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), adhering to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), Standard 44 (*Pre-Commit Changelog & Documentation Synchronization*), and Standard 45 (*Continuous Capability Manifest Synchronization*).

## [Unreleased]

### Added
- **Multi-Engine PNG Rasterization (`Diagram.render_png()`):** High-speed vector-to-raster rendering supporting `resvg-py` with fallbacks to `cairosvg`, Inkscape, and ImageMagick.
- **Rendered Output Assets Catalog (`output/`):** Tracked SVG, PNG, and Markdown BOM output artifacts (222 files) for all 70 domain example diagrams and core architectures in repository.
- **Dev Tooling Dependency:** Added `resvg-py` to optional dev dependencies for pure-wheel PNG compilation without external C-dependencies.
- **PNG Verification Test Suite:** Added assertions in `tests/test_domain_examples.py` and `tests/test_examples.py` validating PNG file existence, non-zero size, and `\x89PNG\r\n\x1a\n` magic bytes.
- **Container Font Packaging & Compose:** Integrated `fonts-dejavu-core` into `Dockerfile` for crisp rasterized typography and added standard `docker-compose.yml` for zero-configuration `docker compose run --rm diagram-gen`.

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
