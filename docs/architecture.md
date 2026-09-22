# System Architecture & Technical Specifications

## 1. Architectural Overview

`diagrams-as-code` is a declarative vector diagramming engine written in 100% pure standard-library Python. It compiles high-level Python code models into production-quality W3C SVG vector documents, rasterized PNG graphics, and structured Bill of Materials (BOM) documentation without relying on external system libraries like Graphviz, Cairo, or ImageMagick.

```
+-----------------------------------------------------------------------------------+
|                              User Architecture Script                             |
|        with Diagram("Title", theme="nord") as diag: diag.add(...) >> ...          |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                         Declarative Object Model (DOM)                            |
|      - Diagram (Context & Registry)                                              |
|      - Elements & Shapes (Nodes with Kind, Icon, Label Position, Dimensions)       |
|      - Groups (Hierarchical Containers with Padding, Headers, Auto-Bounds)        |
|      - Edges (Source, Target, Ports, Style, Arrowheads, Protocol Badges)          |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                       Topological Constraint Solver DAG                           |
|      - Cycle Detection & Topological Sort                                         |
|      - Relative Alignment & Margin Calculation (right_of, below, above, left_of)  |
|      - Hierarchical Group Bounds Recalculation                                    |
|      - Canvas Negative Coordinate Auto-Framing                                    |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                Layout Pipeline (manual / auto / layout file)                      |
|      - manual: constraint solver output passes through unchanged                  |
|      - auto: LayeredLayout places unpinned shapes/groups per scope                |
|      - layout file: JSON overrides applied last, keyed by id or label path        |
|      - Pinned-vs-auto overlap detection emits LayoutWarning                       |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                       Orthogonal Manhattan Router (A*)                            |
|      - Dynamic Automatic Port Selection (North, South, East, West)                |
|      - Obstacle Avoidance & Bounding Box Routing                                  |
|      - Collinear Segment Simplification & Waypoint Generation                     |
+-----------------------------------------------------------------------------------+
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
+---------------------------------------+ +-----------------------------------------+
|            SVGRenderer                | |             BOMGenerator                |
|  - Theme Palette Injection            | |  - Component Inventory Assembly         |
|  - Standalone Vector Icons (60)       | |  - Metadata Attribute Extraction        |
|  - Dynamic SVG Defs & Shadow Filters  | |  - Protocol & Connection Mapping        |
|  - Multi-line <tspan> Anti-Spill Wrap | |  - Markdown Table & JSON Serialization  |
|  - Text-Below-Graphic Support         | +-----------------------------------------+
+---------------------------------------+
                    │
                    ▼
+---------------------------------------+
|        resvg-py Rasterizer            |
|  - Pure Wheel PNG Rasterization       |
|  - Crisp 2x / 4x Vector Scaled Output |
+---------------------------------------+
```

---

## 2. Subsystem Breakdown

### 2.1 Geometry Engine (`diagrams_as_code.geometry`)
- **`Point(x, y)`**: Immutable 2D Cartesian coordinate with vector arithmetic (`+`, `-`, scalar `*`).
- **`Size(width, height)`**: Non-negative 2D dimension descriptor.
- **`Rect(x, y, width, height)`**: Bounding box primitive supporting intersection tests, bounding box union (`union()`), inflation/padding expansion (`expand()`), and 9-point cardinal anchors (`TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`, `CENTER_LEFT`, `CENTER`, `CENTER_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_CENTER`, `BOTTOM_RIGHT`).
- **`UnitBasis`**: Coordinate normalization converting canvas-relative floating ratios (`0.0` to `1.0`) into absolute pixel coordinates.

### 2.2 Domain Object Model (`diagrams_as_code.elements`)
- **`Element`**: Abstract root for all nodes and containers. Tracks geometric bounds, parent-child hierarchies, custom metadata dictionaries, and positioning constraints. Supports fluent edge creation via the `>>` right-shift operator.
- **`Shape`**: Concrete visual node. Configurable with shape kinds (`box`, `cylinder`, `database`, `server_rack`, `cloud`, `diamond`, `icon`), embedded vector icons, dynamic width adaptation, and `label_position` (`"inside"`, `"bottom"`, `"below"`, `"auto"`).

### 2.3 Vector Shape & Icon Library (`diagrams_as_code.shapes`)
- Pure SVG path emitters for boxes (with customizable corner radii), database cylinders (multi-tiered storage drums), server racks (individual blade unit partitions), decision diamonds, and clouds.
- Built-in library of 60 handcrafted 24x24 open-source vector icons spanning 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`).
- Extensible custom icon loading via SVG files or entire directories.

### 2.4 Hierarchical Grouping (`diagrams_as_code.groups`)
- Nested zone management (`Group`).
- Automatically computes bounding boxes enclosing all child elements with customizable padding and header heights.
- Supports internal grid, column, and row layouts (`layout_row`, `layout_column`, `layout_grid`).
- Translates nested child coordinates automatically when parent groups are repositioned.

### 2.5 Topological Constraint Solver (`diagrams_as_code.constraints`)
- Resolves complex relative spatial alignments without manual coordinate tracking.
- Constructs a Directed Acyclic Graph (DAG) of relative constraints (`right_of`, `left_of`, `below`, `above`).
- Detects circular dependencies and raises explicit `RuntimeError` on cycles.
- Applies auto-framing on negative coordinates: translates all canvas elements so the minimum bounding box begins at visible canvas coordinates `(60.0, 80.0)`.

### 2.6 Orthogonal Manhattan Router (`diagrams_as_code.router`)
- Computes clean orthogonal Manhattan routes with 90-degree waypoints.
- Automatically selects the optimal cardinal ports (`North`, `South`, `East`, `West`) between source and target based on relative positioning.
- Simplifies redundant collinear segments.
- Centers protocol badges over the midpoint segment with white or theme-colored backgrounds to prevent lines from crossing text.

### 2.7 Theme Engine (`diagrams_as_code.theme`)
- 13 built-in themes:
  - **Dark Themes:** `iiot_dark_gold`, `blueprint`, `cyber_slate`, `nord`, `emerald`, `crimson`, `dracula`, `synthwave`.
  - **Light Themes:** `iiot_light`, `monochrome`, `solarized_light`, `pastel_light`.
  - **Accessibility Themes:** `high_contrast` (WCAG AAA compliant).
- Auto-calculates W3C relative luminance to determine optimal foreground text contrast against custom container fill colors.
- Dynamic theme derivation via `create_theme(name, base="...", **overrides)`.

### 2.8 Living Documentation & BOM Generator (`diagrams_as_code.bom`)
- Automatically inventories all components, types, categories, and custom metadata attributes.
- Produces clean Markdown tables suitable for GitHub READMEs or architecture portals.
- Serializes complete Bill of Materials to machine-readable JSON schemas for integration with asset tracking, procurement, or configuration management databases (CMDB).

### 2.9 Layout (`diagrams_as_code.layout`)
- **`base.py`**: Shared data model — `LayoutNode`, `LayoutEdge`, `LayoutGraph` (one scope's nodes and edges), the `LayoutEngine` protocol, and the `LayoutWarning` (`UserWarning`) class used whenever a layout result is probably not what the author intended.
- **`graph.py`**: Turns one scope of a diagram (the canvas, or a single group) into a `LayoutGraph` — collecting that scope's unpinned children and the edges between them, duck-typed against `solver.elements`/`edges` so it never imports `diagram`.
- **`layered.py`**: `LayeredLayout` — deterministic Sugiyama-style placement. Ranks nodes by edge direction (`LR` or `TB`), orders each rank to reduce crossings, and spaces ranks evenly; ties always break by declaration index, so a re-run of the same script reproduces the same layout.
- **`sidecar.py`**: The editable layout file. `element_key()` derives a stable key (explicit `id=`, else the ancestor-label path joined by `/`); `load_layout_file()` / `export_layout()` round-trip a JSON file of `{key: {x, y}}` entries; `apply_entries()` inserts each entry as the winning constraint, warning on any stale key that matches no element.
- **`pipeline.py`**: `run_layout()` — the ordered steps `Diagram.solve()` runs: drop the previous run's generated constraints, apply layout-file entries first, place unpinned elements scope-by-scope with `layout="auto"`, solve, recompute group bounds and frame negative coordinates, grow the canvas and warn about pins overlapping auto-placed siblings, then route every edge. With `layout="manual"` and no layout file this reproduces the original solve exactly.

---

## 3. Execution Lifecycle

1. **Context Initialization**: `with Diagram("Title", theme="nord") as diag:` establishes active context on thread-local stack.
2. **Declaration Phase**: Shapes, groups, and edges are declared using fluent syntax.
3. **Context Exit / Pre-Render Hook**: `Diagram.__exit__()` or `render_svg()` verifies `_is_solved`.
4. **Constraint Solving**:
   - Computes topological ordering of relative constraints.
   - Computes group bounds from leaf elements upwards.
   - Detects any negative bounds and translates canvas into visible viewport coordinates `(60.0, 80.0)`.
5. **Path Routing**: Orthogonal router determines port waypoints and protocol badge locations.
6. **SVG Assembly**: SVGRenderer generates XML document with markers, filters, groups, paths, icons, and multi-line wrapped labels.
7. **PNG Rasterization & BOM Emission**: `resvg-py` renders high-resolution PNG; `BOMGenerator` emits structured living documentation.

---

## 4. Source Code Hierarchy (`src/`)

The engine lives in `src/diagrams_as_code/`; `src/iiot_diagrams/` is a backward-compatibility facade that re-exports it.

```
src/
├── diagrams_as_code/               # Canonical Root Module
│   ├── __init__.py                 # Public API exports & package version
│   ├── geometry.py                 # Geometric primitives (Point, Size, Rect, Anchor, UnitBasis)
│   ├── elements.py                 # Core Element base model and Shape node
│   ├── shapes.py                   # Vector ShapeLibrary & embedded SVG icon renderers
│   ├── icon_glyphs.py              # SVG bodies for the built-in icons (24x24 grid)
│   ├── groups.py                   # Group container with dynamic auto-bounding and flow layouts
│   ├── constraints.py              # Topological DAG ConstraintSolver with cycle detection
│   ├── context.py                  # Stack of Diagrams whose `with` block is currently open
│   ├── metrics.py                  # Text metrics shared by layout and rendering
│   ├── layout/                     # Manual / auto / layout-file placement (see §2.9)
│   │   ├── base.py                 # LayoutNode, LayoutEdge, LayoutGraph, LayoutEngine, LayoutWarning
│   │   ├── graph.py                # Diagram scope -> LayoutGraph
│   │   ├── layered.py              # LayeredLayout: deterministic Sugiyama-style placement
│   │   ├── sidecar.py              # Editable layout file: keys, load/export, apply_entries
│   │   └── pipeline.py             # run_layout(): the ordered steps Diagram.solve() runs
│   ├── router.py                   # Orthogonal Manhattan routing with obstacle avoidance
│   ├── connections.py              # Edge connection models & fluent >> operator overloading
│   ├── renderer_svg.py             # SVGRenderer with theme integration and defs generation
│   ├── rasterize.py                # PNG rasterization backends, tried in order until one works
│   ├── theme.py                    # 13 built-in palette themes (nord, emerald, crimson, …)
│   ├── bom.py                      # Bill of Materials (BOM) living markdown documentation
│   ├── output.py                   # Writes a diagram's SVG, PNG and BOM to a directory
│   ├── cli.py                      # `diagrams-as-code render|layout export|themes|icons`
│   └── diagram.py                  # Diagram canvas context manager, render_svg, render_png
│
└── iiot_diagrams/                  # Backward Compatibility Facade
    ├── __init__.py                 # Re-exports diagrams_as_code symbols and __all__
    ├── bom.py                      # Forwards to diagrams_as_code.bom
    ├── connections.py              # Forwards to diagrams_as_code.connections
    ├── constraints.py              # Forwards to diagrams_as_code.constraints
    ├── diagram.py                  # Forwards to diagrams_as_code.diagram
    ├── elements.py                 # Forwards to diagrams_as_code.elements
    ├── geometry.py                 # Forwards to diagrams_as_code.geometry
    ├── groups.py                   # Forwards to diagrams_as_code.groups
    ├── renderer_svg.py             # Forwards to diagrams_as_code.renderer_svg
    ├── router.py                   # Forwards to diagrams_as_code.router
    ├── shapes.py                   # Forwards to diagrams_as_code.shapes
    └── theme.py                    # Forwards to diagrams_as_code.theme
```

---

## 5. Domain Hierarchy

IIoT is treated as one of eight first-class architectural domains:

```
examples/
├── cloud/                          # 11 Cloud architecture diagrams (incl. 1 auto-layout)
├── ai/                             # 11 AI / ML pipeline diagrams (incl. 1 auto-layout)
├── computer/                       # 11 Computer & endpoint diagrams (incl. 1 auto-layout)
├── datacenter/                     # 11 Datacenter & infrastructure diagrams (incl. 1 auto-layout)
├── business_process/               # 11 Business workflow & BPMN diagrams (incl. 1 auto-layout)
├── cybersecurity/                  # 11 Cybersecurity & Zero-Trust diagrams (incl. 1 auto-layout)
├── network_engineering/            # 11 Campus & WAN network diagrams (incl. 1 auto-layout)
└── iiot/                           # 11 Industrial IoT & automation diagrams (incl. 1 auto-layout)
```

---

## 6. Key Architectural Invariants

1. **Deterministic Core:** Zero external runtime dependencies required for SVG generation.
2. **Always Use `uv`:** All environment setup, script runs, and testing must use `uv run`.
3. **Decoupled Lifecycle:** Elements exist independently of positioning constraints; positions can be declared late or updated dynamically.
4. **Guaranteed Solve:** Rendering functions (`render_svg`, `render_png`, `generate_readme`) automatically resolve layout constraints and normalize bounds before emitting output.
5. **Layered imports:** enforced by `tests/test_module_boundaries.py`.
