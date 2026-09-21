# Functional Capabilities Manifest: Pure-Python Directed Diagrams as Code

**Status:** LIVING OPERATIONAL MANIFEST  
**Specification:** Standard 43 / Tenet 45  
**Machine-Readable Twin:** [`docs/capabilities.json`](capabilities.json) (Root symlink: `capabilities.json`)  
**Last Updated:** 2026-09-21 (v0.3.0)  

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
| **Can living BOM docs be generated?** | **YES** | `diag.generate_readme()` | Extracts component inventories, group affiliations, connection topology, and technical notes into Markdown tables and JSON catalogs. |

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

### 2.9 Domain Architectural Reference Suite

#### `CAP-DIAG-DOMAINS`: Multi-Domain Reference Topologies & Automated Test Suite
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `examples/` (`examples/cloud`, `examples/ai`, `examples/computer`, `examples/datacenter`, `examples/business_process`, `examples/cybersecurity`, `examples/network_engineering`, `examples/iiot`)
- **Exports:** 70 self-contained executable diagram scripts and documentation artifacts
- **Features:** 10 topologies per domain demonstrating varying architectural complexity (Simple, Moderate, Advanced, Enterprise), multi-theme deployment across the 13 presets, automated SVG and Markdown BOM generation in `output/`, and gallery documentation in `examples/README.md`.
- **Verification:** `uv run pytest tests/test_domain_examples.py`

---

### 2.10 Planned Capabilities

#### `CAP-DIAG-INTERACTIVE`: Interactive SVG Pan-Zoom and Collapsible Groups
- **Status:** `PLANNED`
- **Target Release:** unscheduled
- **Details:** Client-side lightweight JavaScript injection into SVG output for interactive panning, zooming, and group fold/unfold toggles.
- **Verification:** Pending Milestone 2

