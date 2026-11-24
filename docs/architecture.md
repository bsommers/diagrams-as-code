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
|                               Layout Pipeline                                     |
|      - manual: constraint solver output passes through unchanged, except canvas   |
|        growth, which is unconditional (see below)                                 |
|      - auto: LayeredLayout places unpinned shapes/groups per scope                |
|      - layout file: overrides applied first (before auto-place); id or path keys  |
|      - Pinned-vs-auto overlap detection emits LayoutWarning                       |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                  Edge Routing Engine (Orthogonal / Curve)                         |
|      - OrthogonalRouter: A* Manhattan, Cardinal Ports, Collinear Simplification   |
|        and Quadratic Rounded Corner Fillets (Q) with Dynamic Budget Clamping      |
|      - CurveRouter: Cubic Bezier (C), Cardinal Port Normals, De Casteljau         |
|        Collision Detection, C1 Deflection Splines, and Reverse-Flow Escape        |
+-----------------------------------------------------------------------------------+
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
+---------------------------------------+ +-----------------------------------------+
|            SVGRenderer                | |             BOMGenerator                |
|  - Theme Palette Injection (14)       | |  - Component Inventory Assembly         |
|  - Standalone Vector Icons (60)       | |  - Metadata Attribute Extraction        |
|  - Dynamic SVG Defs & Shadow Filters  | |  - Protocol & Connection Mapping        |
|  - Multi-line <tspan> Anti-Spill Wrap | |  - Markdown Table & JSON Serialization  |
|  - Interactive Pan/Zoom & Minimap HUD | +-----------------------------------------+
|  - Client-Side Search Highlighting    |
+---------------------------------------+
                    │
                    ▼
+---------------------------------------+
|  rasterize.py / pdf.py                |
|  - PNG via resvg-py (or fallbacks)    |
|  - Vector PDF, standard library only  |
+---------------------------------------+
```

`Plot` (data-space plotting), `Draft` (drafting and anatomy primitives) and `SequenceDiagram` (UML sequence diagrams) sit beside the Declarative Object Model: they add ordinary paths, polygons and text to a `Diagram`, so their output flows through the same layout, audit and renderer stages. `diagrams-as-code mcp` wraps the CLI operations (render, lint, list) in a stdio MCP server.

---

## 2. Subsystem Breakdown

### 2.1 Geometry Engine (`diagrams_as_code.geometry`)
- **`Point(x, y)`**: Immutable 2D Cartesian coordinate with vector arithmetic (`+`, `-`, scalar `*`, length, normalization, dot product, distance).
- **`Size(width, height)`**: Non-negative 2D dimension descriptor.
- **`Rect(x, y, width, height)`**: Bounding box primitive supporting intersection tests, bounding box union (`union()`), inflation/padding expansion (`expand()`), point containment (`contains()`, `contains_point()`), and 9-point cardinal anchors (`TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`, `CENTER_LEFT`, `CENTER`, `CENTER_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_CENTER`, `BOTTOM_RIGHT`).
- **`CubicBezier(p0, p1, p2, p3)`**: Cubic Bezier parametric curve primitive. Evaluates coordinates (`point_at(t)`) and derivatives (`tangent_at(t)`), computes exact arc length via 5-point Legendre-Gauss numerical quadrature, determines tight axis-aligned bounding boxes via quadratic polynomial derivative root solving, performs recursive De Casteljau subdivision (`subdivide(t)`), and tests line/spline collisions against rectangular bounding boxes (`intersects_rect()`).
- **`QuadraticBezier(p0, p1, p2)`**: Quadratic Bezier parametric curve primitive used for corner filleting. Provides `point_at(t)`, `tangent_at(t)`, `bbox()`, analytical arc length calculation, and equidistant midpoint evaluation.
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

### 2.6 Edge Routing Engine (`diagrams_as_code.router`)

The routing subsystem computes collision-free trajectories between node ports, supporting both orthogonal Manhattan paths and organic cubic Bezier splines.

#### 2.6.1 Orthogonal Manhattan Router (`OrthogonalRouter`)
- **Cardinal Port Selection**: Dynamically evaluates geometric relative positions to select optimal exit and entry ports (`North`, `South`, `East`, `West`).
- **A* Obstacle Avoidance**: Computes orthogonal waypoints that navigate around intervening shapes and containers.
- **Collinear Simplification**: Prunes redundant collinear vertices to generate minimal-bend orthogonal paths.
- **Protocol Badge Placement**: Computes bounding boxes over the longest straight segment, masking the underlying stroke with high-contrast badge backgrounds.

#### 2.6.2 Rounded Corner Fillets (`corner_radius` / `arc_radius`)
- **Dynamic 50% Budget Clamping**: Constrains effective fillet radius to `R_eff = min(corner_radius, L_in / 2.0, L_out / 2.0)` to eliminate self-intersecting loops and "dog-ear" visual artifacts on short intermediate segments.
- **Port & Arrowhead Lead-In Protection**: Enforces straight collinear lead-ins at source and destination ports, ensuring arrowheads render flush without curvature distortion.
- **Threshold Suppression**: Suppresses fillets when `R_eff < 2.0px`, seamlessly falling back to sharp 90-degree corners.
- **Obstacle Apex Clearance**: Analytically checks corner rounded arc apices against obstacle boundaries, clamping radius to maintain >= 4.0px safety clearance.
- **Native SVG Q Emission**: Converts filleted corner bends into standard SVG Quadratic Bezier (`Q`) commands (`L T1 Q P_c T2`).

#### 2.6.3 Cubic Bezier Routing Engine (`CurveRouter`)
- **Smooth Spline Trajectories (`Routing.CURVE`)**: Calculates cubic Bezier curves using cardinal port normal vectors with handle distances scaled proportionally to Euclidean port separation (`handle_dist = clamp(dist * 0.4, 20.0, 300.0)`).
- **Two-Tier Obstacle Collision Detection**:
  - *Tier 1 (AABB Broadphase)*: Rapid bounding box intersection filtering excluding source and destination endpoints.
  - *Tier 2 (Narrowphase Subdivision)*: De Casteljau subdivision up to depth 4, testing child curve convex hulls against inflated obstacle rectangles (`clearance=15px`).
- **Minimal Deviation Deflection**: Evaluates perpendicular detour corridors (above/below or left/right), selects the minimal geometric deviation path, and inserts deflection waypoints.
- **Strict $C^1$ Spline Continuity**: Enforces collinear incoming and outgoing control handles (`u_out = -u_in`) across all intermediate deflection waypoints, guaranteeing zero slope discontinuity or inflection kinks.
- **Reverse-Flow Escape Routing**: Detects backward flow (e.g. source to the right of target in LR diagrams), automatically routes out of North/South ports, and offsets control handles into dedicated lateral escape corridors (>= 30px clearance).

### 2.7 Theme Engine (`diagrams_as_code.theme`)
- 14 built-in themes:
  - **Dark Themes:** `iiot_dark_gold`, `blueprint`, `cyber_slate`, `nord`, `emerald`, `crimson`, `dracula`, `synthwave`.
  - **Light Themes:** `iiot_light`, `monochrome`, `solarized_light`, `pastel_light`, `paper`.
  - **Accessibility Themes:** `high_contrast` (WCAG AAA compliant).
- A theme also carries line weights, corner radii, the group dash pattern, edge width and the shadow switch. `diagrams_as_code.style.Style` holds per-node or per-group overrides, merged theme -> enclosing groups' `child_style` -> element `style` -> legacy `metadata` keys by `resolve_node_style` / `resolve_group_style`.
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
- **`pipeline.py`**: `run_layout()` — the ordered steps `Diagram.solve()` runs: drop the previous run's generated constraints, apply layout-file entries first, place unpinned elements scope-by-scope with `layout="auto"`, solve, recompute group bounds and frame negative coordinates, size the canvas (an axis the user left unset is fitted to the content; a declared `width`/`height` is a minimum that grows if content would be clipped), and (with `layout="auto"`) warn about pins overlapping auto-placed siblings, then route every edge. Canvas sizing is unconditional — it runs in `layout="manual"` with no layout file too. With `layout="manual"` and no layout file this otherwise reproduces the original solve exactly.

### 2.10 Interactive SVG Engine (`diagrams_as_code.renderer_interactive`)
- **Zero-Dependency Vector Interactivity**: Embeds pure vanilla JavaScript directly into emitted SVG documents without requiring external scripts or web frameworks.
- **Client-Side Pan & Zoom**: Handles mouse drag and wheel events via SVG root matrix transforms (`transform="matrix(...)"`), supporting infinite canvas panning and smooth zoom scaling from 0.1x to 10.0x.
- **Node Search & Focus Highlighting**: Real-time client-side search bar HUD. Matches node labels, dims non-matching nodes, pulses active matches with focus outlines, and navigates match results with Enter/Tab keyboard navigation.
- **Minimap Navigator**: Real-time interactive minimap HUD in the bottom-right corner displaying an overview thumbnail with an interactive viewport bounding box synchronized to current pan/zoom coordinates.
- **Heuristics & Toggle**: Activated via `Diagram(interactive=True)` or automatically enabled when canvas dimensions exceed 1600x1200 pixels.

### 2.11 Primitives and Solids (`diagrams_as_code.primitives`, `solids`, `drawing`, `labels`, `arrange`)
- **`primitives.py`**: free `Text`, `Caption`, `Bracket`, `Polygon`, `Polyline`, `Path`, `SolidShape` and `Band` elements, created through `Diagram` helpers such as `diag.text()`, `diag.polygon()` and `diag.band()`. They are drawing, not components, so they never appear in the BOM.
- **`solids.py`**: convex `Solid` meshes (`Solid.box`, `.prism`, `.pyramid`, `.hull`), oblique and isometric `Projection`s, back-to-front face ordering and visible/hidden edge classification, with optional cutting planes.
- **`drawing.py` / `labels.py` / `arrange.py`**: the backend-neutral `PathItem`/`TextItem` model and SVG path parsing shared by the SVG and PDF writers; shared label, badge and title geometry; and the `align()` / `distribute()` helpers.

### 2.12 Data Plots (`diagrams_as_code.plot`)
- **`Plot(diagram, x=(lo, hi), y=(lo, hi), origin=(px, py), size=(w, h))`** owns the mapping from data coordinates to canvas pixels (`px()`), linear or log axes, and draws with the diagram's own primitives.
- Marks: `grid`, `axes`, `function`, `parametric`, `area`, `band`, `bars`, `bar_chart`, `stacked_bars`, `candles`, `slope_field`, `vector_field`, `trajectory`, `orbit`, `dot`, `label`, `legend`, `tangent`, `hline`/`vline`. `solve_ode` integrates systems with RK4.
- Used by the textbook, medical and engineering galleries; see [technical-figures.md](technical-figures.md#9-plots-and-drafting-views).

### 2.13 Drafting and Anatomy (`diagrams_as_code.draft`)
- **`Draft(diagram)`** works in canvas pixels. Engineering: `dimension`, `radius_dim` (`diameter=True` for a diameter), `hatch` (even-odd, so holes work), `centerline`, `hidden_line`, `section_arrows`, `gdt_frame`. Anatomy: `smooth_closed`, `smooth_open` (Catmull-Rom outlines), `leader`, `wave` (periodic traces such as an ECG).

### 2.13a Sequence Diagrams (`diagrams_as_code.sequence`)
- **`SequenceDiagram(title, theme=...)`** records participants and events (messages, replies, self-calls, activations, notes, `loop`/`alt`/`opt`/`par`/`critical`/`break` frames) and lays them out deterministically: one column per participant, one row per event, column gaps grown until every measured label fits. `build()` returns a `Diagram`; `draw(diag, origin)` adds to an existing one; `layout()` returns the geometry. See [sequence-diagrams.md](sequence-diagrams.md).

### 2.14 Audit, PDF Export and Rasterization (`audit`, `pdf`, `rasterize`)
- **`audit.py`**: `audit_diagram` / `audit_findings` check a solved diagram for visual defects (a line through a node, overlapping labels, text that does not fit). They back `diagrams-as-code lint`, `tools/audit_gallery.py` and the MCP `lint` tool.
- **`pdf.py`**: `svg_to_pdf` draws the renderer's own SVG with PDF operators, so the two cannot drift. Only the SVG vocabulary the engine writes is understood; anything else raises `PDFExportError`.
- **`rasterize.py`**: PNG backends tried in order (`resvg-py`, CairoSVG, Inkscape, ImageMagick) until one is available.

### 2.15 MCP Server (`diagrams_as_code.mcp`)
- A stdlib-only JSON-RPC 2.0 server over stdio (newline-delimited, MCP revision 2025-06-18), started with `diagrams-as-code mcp [--root DIR]`.
- Tools: `list_examples`, `render`, `lint`, `list_themes`, `list_icons`, mapping onto `cli.discover`/`load_script`, `output.render_all`, `audit.audit_findings`, `theme.list_themes` and `ShapeLibrary`.
- Rendering runs a diagram script, which is arbitrary Python, so every script and output path is confined to `--root` (default: the current directory). See [purpose.md](purpose.md#4-the-mcp-server-runs-scripts).

---

## 3. Execution Lifecycle

1. **Context Initialization**: `with Diagram("Title", theme="nord") as diag:` pushes the diagram onto the module-level active-diagram stack in `context.py` (a plain list, not thread-local — elements look up the innermost open `Diagram` there instead of importing `diagram`).
2. **Declaration Phase**: Shapes, groups, and edges are declared using fluent syntax, either directly or via the CLI's `load_script()`, which imports the script and calls its `diagram()` function.
3. **Context Exit / Pre-Render Hook**: `Diagram.__exit__()` or `render_svg()` verifies `_is_solved` and calls `solve()`, which delegates to `run_layout()` (`layout/pipeline.py`).
4. **Layout & Constraint Solving** (`run_layout()`):
   - Drops the previous run's auto-generated constraints and restores pre-layout bounds.
   - Applies layout-file overrides, if any, as each element's leading absolute constraint.
   - With `layout="auto"`, places unpinned shapes/groups scope-by-scope (deepest groups first) via `LayeredLayout`.
   - Runs the constraint solver: topological ordering of relative constraints (`right_of`, `below`, `above`, `left_of`).
   - Computes group bounds from leaf elements upwards.
   - Detects any negative bounds and translates canvas into visible viewport coordinates `(60.0, 80.0)`.
   - Sizes the canvas: fits an unset axis to the content, and grows a declared `width`/`height` when content would be clipped — in every layout mode.
   - With `layout="auto"`, warns (`LayoutWarning`) about any pinned element overlapping an auto-placed sibling.
5. **Path Routing**: `run_layout()` dispatches edge routing to `OrthogonalRouter` (for Manhattan routing and corner filleting) or `CurveRouter` (for cubic Bezier curves, obstacle collision deflection, and reverse-flow escape corridors). Port waypoints and badge rects are computed and cached on the diagram.
6. **SVG Assembly**: SVGRenderer generates the XML document with markers, filters, groups, paths, icons, multi-line wrapped labels (`<tspan>`), and interactive HUD controllers (pan/zoom, search, minimap) when interactive mode is active.
7. **Output Writing**: `render_svg()`/`render_png()`/`render_pdf()`/`generate_readme()`/`generate_bom_json()` write individually, or `output.render_all()` writes every requested format (`svg,bom` by default; `png` and `pdf` are opt-in) in one call — the CLI always uses `render_all()`. PNG rasterization tries `rasterize.py`'s four backends in order (`resvg-py` → CairoSVG → Inkscape → ImageMagick) until one is available; `BOMGenerator` emits the living Markdown and JSON documentation.

---

## 4. Source Code Hierarchy (`src/`)

The engine lives in `src/diagrams_as_code/`; `src/iiot_diagrams/` is a backward-compatibility facade that re-exports it.

```
src/
├── diagrams_as_code/               # Canonical Root Module
│   ├── __init__.py                 # Public API exports & package version
│   ├── geometry.py                 # Geometric primitives (Point, Size, Rect, Anchor, UnitBasis, CubicBezier, QuadraticBezier)
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
│   │   ├── flow.py                 # Group flow layouts (row, column, GridLayout) behind a GroupFlowLayout protocol
│   │   ├── lanes.py                # Moves edges routed along one corridor onto separate lanes
│   │   ├── badges.py               # Places edge badges clear of nodes, titles, badges and lines
│   │   └── pipeline.py             # run_layout(): the ordered steps Diagram.solve() runs
│   ├── router.py                   # Orthogonal Manhattan & Cubic Bezier routing with obstacle deflection
│   ├── connections.py              # Edge connection models & fluent >> operator overloading
│   ├── renderer_svg.py             # SVGRenderer: defs, group, edge and node passes
│   ├── renderer_interactive.py     # Pan/zoom/search/minimap overlay for interactive SVG
│   ├── style.py                    # Style value object and theme -> group -> element cascade
│   ├── labels.py                   # Label, badge and group-title geometry shared by layout, drawing and audit
│   ├── drawing.py                  # Backend-neutral PathItem/TextItem, SVG path parsing, arrowheads
│   ├── solids.py                   # Convex solids, oblique/isometric projection, hidden-edge classification
│   ├── plot.py                     # Plot: data-space axes, curves, areas, fields and bars on a Diagram
│   ├── draft.py                    # Draft: dimensions, hatching, centerlines, GD&T frames, anatomy outlines
│   ├── sequence.py                 # SequenceDiagram: UML lifelines, messages, activations, notes, frames
│   ├── primitives.py               # Text, Caption, Bracket, Polygon, Polyline, Path, SolidShape, Band
│   ├── arrange.py                  # align() and distribute() helpers
│   ├── rasterize.py                # PNG rasterization backends, tried in order until one works
│   ├── pdf.py                      # Vector PDF writer: draws the renderer's SVG with PDF operators
│   ├── theme.py                    # 14 built-in themes (nord, emerald, crimson, paper, …)
│   ├── text/                       # Font metrics (metrics.py), rich text (rich.py), math typesetting (math.py) and bundled glyph data
│   ├── audit.py                    # Visual defect checks on a solved diagram; named findings for `lint`
│   ├── bom.py                      # Bill of Materials (BOM) living markdown documentation
│   ├── output.py                   # Writes a diagram's SVG, PNG, PDF and BOM to a directory
│   ├── cli.py                      # `diagrams-as-code render|lint|layout export|themes|icons|mcp`
│   ├── mcp.py                      # Stdio MCP server: list_examples, render, lint, list_themes, list_icons (confined to --root)
│   ├── __main__.py                 # `python -m diagrams_as_code`
│   └── diagram.py                  # Diagram canvas context manager, render_svg, render_png, render_pdf
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

IIoT is one of thirteen first-class architectural domains, alongside the technical-figure, textbook, medical, engineering and CAD galleries. Rendered SVG, PNG and BOM files live next to each script (there is no top-level `output/` directory):

```
examples/
├── cloud/                          # 11 Cloud architecture diagrams (incl. 1 auto-layout)
├── ai/                             # 11 AI / ML pipeline diagrams (incl. 1 auto-layout)
├── computer/                       # 11 Computer & endpoint diagrams (incl. 1 auto-layout)
├── datacenter/                     # 11 Datacenter & infrastructure diagrams (incl. 1 auto-layout)
├── business_process/               # 11 Business workflow & BPMN diagrams (incl. 1 auto-layout)
├── cybersecurity/                  # 11 Cybersecurity & Zero-Trust diagrams (incl. 1 auto-layout)
├── network_engineering/            # 11 Campus & WAN network diagrams (incl. 1 auto-layout)
├── iiot/                           # 11 Industrial IoT & automation diagrams (incl. 1 auto-layout)
├── database/                       # 11 Database design & internals diagrams (incl. 1 auto-layout)
├── enterprise_architecture/        # 11 Enterprise architecture views (incl. 1 auto-layout)
├── manufacturing/                  # 11 Manufacturing & semiconductor diagrams (incl. 1 auto-layout)
├── mind_map/                       # 11 Mind maps (incl. 1 auto-layout)
├── computer_science/               # 11 Computer-science technical figures (incl. 1 auto-layout)
├── primitives/                     # 9 one-per-primitive figures (paper theme)
├── technical/                      # 11 complete paper-style figures
├── calculus_math/ differential_equations/ physics/ finance/ logic/   # 50 textbook figures (10 each, Plot-based)
├── medical/ engineering/ cad/      # 30 Draft/Plot figures (10 each)
├── sequence/                       # 3 SequenceDiagram figures
└── 01_*.py ... 04_*.py             # 4 top-level reference scripts
```

In total 250 example scripts: 143 domain diagrams, 4 top-level scripts, 9 primitives, 11 technical figures, 50 textbook figures, 30 medical, engineering and CAD figures and 3 sequence diagrams.

---

## 6. Key Architectural Invariants

1. **Deterministic Core:** Zero external runtime dependencies required for SVG generation.
2. **Always Use `uv`:** All environment setup, script runs, and testing must use `uv run`.
3. **Decoupled Lifecycle:** Elements exist independently of positioning constraints; positions can be declared late or updated dynamically.
4. **Guaranteed Solve:** Rendering functions (`render_svg`, `render_png`, `render_pdf`, `generate_readme`) automatically resolve layout constraints and normalize bounds before emitting output.
5. **Layered imports:** enforced by `tests/test_module_boundaries.py`. `plot`, `draft` and `sequence` sit above `diagram`, and `mcp` above `cli`.
6. **Confined execution:** the MCP server only runs scripts under its `--root`.
