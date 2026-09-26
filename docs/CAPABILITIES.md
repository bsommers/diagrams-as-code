# Functional Capabilities Manifest: Pure-Python Directed Diagrams as Code

**Status:** LIVING OPERATIONAL MANIFEST  
**Specification:** Standard 43 / Tenet 45  
**Machine-Readable Twin:** [`docs/capabilities.json`](capabilities.json) (Root symlink: `capabilities.json`)  
**Last Updated:** 2026-09-26 (v0.8.2)  

---

## 1. Executive Capability Inquiries (Quick Answers)

| Inquiry | Supported? | Operational Entrypoint | Details & Artifacts |
| :--- | :---: | :--- | :--- |
| **Can this render without Graphviz / binaries?** | **YES** | `Diagram.render_svg()` | Pure-Python vector SVG generation with zero external dependencies (no Graphviz `dot`, Cairo, or ImageMagick required). |
| **Can shapes be positioned relatively?** | **YES** | `shape2.right_of(shape1, margin=40)` | Directional placement (`right_of`, `left_of`, `below`, `above`) with custom margins and alignments evaluated by a DAG constraint solver. |
| **Can shapes use unit-basis coordinates?** | **YES** | `diag.unit_basis.to_absolute(0.5, 0.25)` | Normalized coordinate placement (0.0 to 1.0 or `"50%"`, `"25%"`) mapped to canvas dimensions. |
| **Can shapes be decoupled from location?** | **YES** | `Shape(id, label)` / `s.move_to(x, y)` | Shapes can be defined unplaced, placed late, relocated dynamically, or stamped from prototypes via `.clone()`. |
| **Can groups auto-bound and flow?** | **YES** | `group2.below(group1, margin=40)` | Hierarchical containers with bottom-up auto-bounding encapsulating children, headers, and padding. |
| **Can connections route orthogonally?** | **YES** | `s1 >> diag.edge("MQTT") >> s2` | Automatic port deduction (`NORTH`, `SOUTH`, `EAST`, `WEST`) and Manhattan waypoint routing with collinear line simplification. |
| **Can connections route as cubic Bezier curves?** | **YES** | `Edge(routing=Routing.CURVE)` | Analytical cubic Bezier curves with outward cardinal port normals, distance-proportional tension scaling, native SVG `M...C` path rendering, and arc-length centered protocol badges. |
| **Can orthogonal corners be rounded with fillets?** | **YES** | `Edge(corner_radius=12)` / `Diagram(corner_radius=12)` | Smooth quadratic Bezier corner fillets with dynamic 50% segment budget clamping, 2.0px suppression threshold, obstacle apex clearance guard, and native SVG `Q` commands. |
| **Can living BOM docs be generated?** | **YES** | `diag.generate_readme()` | Extracts component inventories, group affiliations, connection topology, and technical notes into Markdown tables and JSON catalogs. |
| **Is there auto-layout?** | **YES** | `Diagram(layout="auto")` | A deterministic layered engine places unpinned shapes and groups from the edge structure (`direction="LR"`/`"TB"`); pinned shapes coexist via `.at()`/`.right_of()`, and a `LayoutWarning` flags any pin that overlaps an auto-placed sibling. |
| **Can diagrams be zoomed and panned interactively?** | **YES** | `Diagram(interactive=True)` | Pure-Python client-side interactive SVG generation with zero external runtime dependencies. Features click-drag panning, scroll wheel zooming, viewport reset HUD controls, and interactive collapsible groups with header toggles. |

---

## 2. Capability Catalog by Domain

### 2.1 Geometry & Coordinate Systems

#### `CAP-DIAG-GEOM`: Core Geometry and Unit-Basis Coordinate Engine
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.geometry`
- **Exports:** `Point`, `Size`, `Rect`, `Anchor`, `UnitBasis`
- **Features:** Immutable 2D primitives, 9-point cardinal/intercardinal rect anchors (`TOP_LEFT`, `CENTER`, `BOTTOM_RIGHT`), rect expansion/union, and normalized canvas unit-basis coordinate conversion (`0.0`-`1.0` and percentage strings).
- **Verification:** `uv run pytest tests/test_geometry.py`

---

### 2.2 Constraint Resolution & Relative Positioning

#### `CAP-DIAG-CONSTR`: Decoupled Elements and Iterative DAG Constraint Solver
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.constraints.ConstraintSolver`
- **Exports:** `Element`, `Shape`, `ConstraintSolver`
- **Features:** Directional shape-to-shape placement (`right_of`, `left_of`, `below`, `above`) with alignment (`center`, `top`, `bottom`, `left`, `right`) and margin padding. Evaluates dependency DAGs with cycle detection and unconstrained element retention.
- **Verification:** `uv run pytest tests/test_constraints.py`

---

### 2.3 Containers & Hierarchical Grouping

#### `CAP-DIAG-GROUP`: Hierarchical Grouping, Auto-Bounding, and Group Flow
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.groups.Group`
- **Exports:** `Group`
- **Features:** Hierarchical container elements with bottom-up recursive auto-bounding, child coordinate delta propagation, cycle prevention in ancestry, and group-to-group flow placement.
- **Verification:** `uv run pytest tests/test_groups.py`

---

### 2.4 Connection Routing

#### `CAP-DIAG-ROUTER`: Orthogonal Manhattan Routing and Port Deduction
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.router.OrthogonalRouter`
- **Exports:** `Edge`, `Port`, `Routing`, `OrthogonalRouter`
- **Features:** Intelligent edge connection model with automatic port deduction (`NORTH`, `SOUTH`, `EAST`, `WEST`), orthogonal Manhattan waypoints calculation, and collinear straight-line simplification.
- **Verification:** `uv run pytest tests/test_routing.py`

#### `CAP-DIAG-ROUTER-AVOIDANCE`: Obstacle-Aware Orthogonal Routing and Multi-Rank Layout
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.7.0`
- **Python API:** `diagrams_as_code.router.OrthogonalRouter`, `diagrams_as_code.router.segment_intersects_rect`
- **Exports:** `OrthogonalRouter`, `segment_intersects_rect`
- **Features:** Segment-box collision detection with clearance corridors, shortest Manhattan detour channel routing around intermediate obstacles, and multi-rank crossing minimization via virtual dummy vertices.
- **Verification:** `uv run pytest tests/test_routing.py tests/test_layout_layered.py`

#### `CAP-DIAG-ROUTER-CURVE`: Cubic Bezier Edge Routing & SVG Path Generation
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.8.0`
- **Python API:** `diagrams_as_code.router.CurveRouter`
- **Exports:** `CubicBezier`, `CurveRouter`, `EdgeRouter`
- **Features:** Pure-Python analytical cubic Bezier edge routing (`Routing.CURVE`). Computes outward cardinal normal port tangents, distance-proportional handle heuristics along flow axes, native SVG `<path d="M... C...">` emission with tangentially aligned destination arrowheads, and physical arc-length midpoint protocol badge positioning.
- **Verification:** `uv run pytest tests/test_geometry.py tests/test_routing.py tests/test_renderer_svg.py -k "curve or bezier"`

#### `CAP-DIAG-ROUTER-FILLET`: Rounded Corner Fillets for Orthogonal Routing
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.8.0`
- **Python API:** `diagrams_as_code.renderer_svg._render_filleted_path`
- **Exports:** `QuadraticBezier`, `Edge`, `Diagram`
- **Features:** Quadratic Bezier corner filleting for orthogonal Manhattan edges (`corner_radius` and `arc_radius` alias on `Edge` and `Diagram`). Emits native SVG `Q` commands with dynamic 50% segment budget clamping, straight port lead-in preservation, 2.0px threshold suppression, and obstacle clearance apex guards.
- **Verification:** `uv run pytest tests/test_geometry.py tests/test_routing.py tests/test_renderer_svg.py -k "fillet or corner_radius"`


---

### 2.5 Vector Theming & Shapes

#### `CAP-DIAG-THEME`: Vector Theming Engine and Vector Shape Library
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.theme`, `diagrams_as_code.shapes`
- **Exports:** `Theme`, `ShapeLibrary`, `ShapeRenderer`, `get_theme`, `register_theme`
- **Features:** 13 theme presets (8 dark, 4 light, 1 high-contrast) (list them with `list_themes()`), 60 built-in vector icons across 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`), dynamic icon registration and loading from SVG files or directory trees, and standalone SVG vector primitives (`box`, `cylinder`, `database`, `server_rack`, `cloud`, `diamond`, `badge`).
- **Verification:** `uv run pytest tests/test_theme.py`


---

### 2.6 SVG Vector Rendering

#### `CAP-DIAG-SVG`: Pure-Python Zero-Binary SVG Vector Renderer
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.renderer_svg.SVGRenderer`
- **Exports:** `SVGRenderer`
- **Features:** Produces valid, standalone W3C SVG XML documents featuring responsive `viewBox` scaling, arrowhead markers, drop shadow filters, ordered group rendering, and automated luminance contrast text coloring.
- **Verification:** `uv run pytest tests/test_renderer_svg.py`

---

### 2.7 Diagram-as-Code API

#### `CAP-DIAG-API`: Fluent Diagram Context Manager and Operator Syntax
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.diagram.Diagram`
- **Exports:** `Diagram`
- **Features:** Pythonic context manager with bitshift connection operator overloading (`s1 >> s2`, `s1 >> diag.edge(...) >> s2`, fan-in/fan-out lists), automatic group scoping, decoupled shape lifecycles, and prototype cloning.
- **Verification:** `uv run pytest tests/test_diagram_api.py`

---

### 2.8 Living Documentation & BOM

#### `CAP-DIAG-BOM`: Living Documentation & Bill of Materials (BOM) Engine
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.bom.BOMGenerator`
- **Exports:** `BOMGenerator`
- **Features:** Extracts diagram inventory, parent groups, connection routes, and technical metadata into Markdown tables and JSON catalogs, with automated `README.md` synchronization.
- **Verification:** `uv run pytest tests/test_bom.py`

---

### 2.9 Layout (`diagrams_as_code.layout`)

#### `CAP-DIAG-LAYOUT`: Auto-Layout Engine and Editable Layout File
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.4.0`
- **Python API:** `diagrams_as_code.layout`
- **Classes:** `LayeredLayout`, `LayoutWarning`
- **Features:** Deterministic Sugiyama-style ranked placement (`layout="auto"`, `direction="LR"`/`"TB"`) for unpinned shapes and groups scope by scope; an editable JSON layout file keyed by explicit `id=` or label path (`diagrams-as-code layout export`); pinned shapes and relative placement (`.at()`, `.right_of()`) coexist with auto-placed siblings, with a `LayoutWarning` raised on overlap.
- **Verification:** `uv run pytest tests/test_layout_layered.py tests/test_layout_graph.py tests/test_layout_pipeline.py tests/test_layout_sidecar.py`

---

### 2.10 Command-Line Interface

#### `CAP-DIAG-CLI`: The `diagrams-as-code` Command
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.4.0`
- **Entrypoint:** `diagrams-as-code` (also `python -m diagrams_as_code`)
- **Subcommands:** `render`, `layout export`, `themes`, `icons`
- **Features:** Batch-renders scripts or whole directories to SVG/PNG/BOM without a Python entry point, exports layout files, and lists built-in themes and icons for discovery; exit codes `0` success, `1` a script failed, `2` usage error.
- **Verification:** `uv run pytest tests/test_cli.py`

---

### 2.11 Domain Architectural Reference Suite

#### `CAP-DIAG-DOMAINS`: Multi-Domain Reference Topologies & Automated Test Suite
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `examples/` (`examples/cloud`, `examples/ai`, `examples/computer`, `examples/datacenter`, `examples/business_process`, `examples/cybersecurity`, `examples/network_engineering`, `examples/iiot`)
- **Exports:** 88 self-contained executable diagram scripts and documentation artifacts
- **Features:** 11 topologies per domain (10 manually placed + 1 auto-layout) demonstrating varying architectural complexity (Simple, Moderate, Advanced, Enterprise), multi-theme deployment across the 13 presets, automated SVG and Markdown BOM generation in `output/`, and gallery documentation in `examples/README.md`.
- **Verification:** `uv run pytest tests/test_domain_examples.py`

---

### 2.12 Interactive SVG Vector Rendering

#### `CAP-DIAG-INTERACTIVE`: Interactive SVG Pan-Zoom and Collapsible Groups
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.5.0`
- **Python API:** `diagrams_as_code.renderer_svg.SVGRenderer`, `diagrams_as_code.diagram.Diagram`
- **Exports:** `Diagram(interactive=True)`, `SVGRenderer.render(interactive=True)`
- **Features:** Pure-Python client-side interactive SVG generation with zero external runtime dependencies. Features responsive click-drag viewport panning, cursor-anchored mouse wheel zoom, viewport reset HUD controls (`#svg-pan-zoom-controls`), and interactive collapsible groups with header toggles (`▼` / `▶`) with recursive visibility management for child shapes, nested sub-groups, and incident edges. Standard non-interactive rendering (`interactive=False`) retains 100% byte-invariance and zero script overhead.
- **Verification:** `uv run pytest tests/test_renderer_svg.py`

---

### 2.13 Command-Line Interface Extensions

#### `CAP-DIAG-CLI-INTERACTIVE`: CLI Interactive Export Option
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.6.0`
- **Command:** `diagrams-as-code render <path> --interactive` / `--no-interactive`
- **Features:** Command-line flags (`--interactive`, `--no-interactive`) for `diagrams-as-code render` supporting both single diagram scripts and batch directory exports. Injects client-side pan/zoom controls and collapsible groups into SVG assets directly from the CLI without code modifications. Preserves tri-state configuration defaulting to script-authored settings when omitted.
- **Verification:** `uv run pytest tests/test_cli.py`

---

### 2.14 Interactive Search & Node Highlight

#### `CAP-DIAG-SEARCH`: Client-Side Search and Node Highlighting
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.6.0`
- **Python API:** `diagrams_as_code.renderer_svg.SVGRenderer`
- **Exports:** `SVGRenderer.render(interactive=True)`
- **Features:** Client-side search input field integrated directly into the HUD controls via responsive XHTML `<foreignObject>`. Real-time dynamic substring matching against node IDs and labels dims non-matching nodes to 20% opacity, dims non-incident edges to 15% opacity, and highlights matching nodes and connected edges. Pressing Escape or clearing input resets all element opacities. Non-interactive rendering remains completely untouched.
- **Verification:** `uv run pytest tests/test_renderer_svg.py`

---

### 2.15 Viewport Minimap Navigator

#### `CAP-DIAG-NAVIGATOR`: Viewport Minimap Overview and Drag Navigation
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.6.0`
- **Python API:** `diagrams_as_code.renderer_svg.SVGRenderer`
- **Exports:** `SVGRenderer.render(interactive=True)`
- **Features:** Pinned overview minimap thumbnail widget rendered in the bottom-right corner of interactive SVG canvases. Features scaled live diagram rendering (`<use href="#diagram-content">`) under a clipped viewport, a responsive viewport rectangle (`#minimap-viewport`) tracking current view bounds during zoom and pan, and smooth click-and-drag navigation to pan across extensive architectural topologies.
- **Verification:** `uv run pytest tests/test_renderer_svg.py`




