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
|  - Standalone Vector Icons (59)       | |  - Metadata Attribute Extraction        |
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
- Built-in library of 59 handcrafted 24x24 open-source vector icons spanning 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`).
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
