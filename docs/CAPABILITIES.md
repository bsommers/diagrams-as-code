# Functional Capabilities Manifest: Pure-Python Directed Diagrams as Code

**Status:** LIVING OPERATIONAL MANIFEST  
**Specification:** Standard 43 / Tenet 45  
**Machine-Readable Twin:** [`docs/capabilities.json`](capabilities.json) (Root symlink: `capabilities.json`)  
**Last Updated:** 2026-11-24 (v0.20.0)  

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
| **Can curved edges deflect around obstacles?** | **YES** | `Edge(routing=Routing.CURVE, clearance=15)` | Two-tier collision detection (AABB broadphase + De Casteljau subdivision), reverse-flow lateral port resolution and escape corridors, and C1-continuous spline deflection waypoints. |
| **Can orthogonal corners be rounded with fillets?** | **YES** | `Edge(corner_radius=12)` / `Diagram(corner_radius=12)` | Smooth quadratic Bezier corner fillets with dynamic 50% segment budget clamping, 2.0px suppression threshold, obstacle apex clearance guard, and native SVG `Q` commands. |
| **Can living BOM docs be generated?** | **YES** | `diag.generate_readme()` | Extracts component inventories, group affiliations, connection topology, and technical notes into Markdown tables and JSON catalogs. |
| **Can it draw UML sequence diagrams?** | **YES** | `SequenceDiagram(title)` | Participants, messages, replies, self-calls, activations, notes and `loop`/`alt`/`opt`/`par`/`critical`/`break` frames, laid out from the events (`diagrams_as_code.sequence`). |
| **Can it draw Gantt charts and timelines?** | **YES** | `GanttChart(diag)` / `Timeline(diag)` | Tasks with dependencies and lag, phases, milestones, progress and a computed critical path; dated events with non-overlapping labels (`diagrams_as_code.gantt`). |
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

#### `CAP-DIAG-ROUTER-CURVE-OBS`: Obstacle Detection & Deflection for Curved Edges
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.8.3`
- **Python API:** `diagrams_as_code.router.CurveRouter`
- **Exports:** `CurveRouter`, `CubicBezier`, `Edge`
- **Features:** Two-tier collision detection combining bounding box broadphase filtering with recursive De Casteljau subdivision, automatic reverse-flow lateral port resolution and escape routing, adaptive $C^1$-continuous spline deflection waypoints around intervening obstacles, and longest-segment protocol badge centering.
- **Verification:** `uv run pytest tests/test_routing.py tests/test_e2e.py -k "deflection or collision or reverse_flow"`


---

### 2.5 Vector Theming & Shapes

#### `CAP-DIAG-THEME`: Vector Theming Engine and Vector Shape Library
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `diagrams_as_code.theme`, `diagrams_as_code.shapes`
- **Exports:** `Theme`, `ShapeLibrary`, `ShapeRenderer`, `get_theme`, `register_theme`
- **Features:** 13 theme presets (8 dark, 4 light, 1 high-contrast) (list them with `list_themes()`), 73 built-in vector icons across 9 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`, `project_management`), dynamic icon registration and loading from SVG files or directory trees, and standalone SVG vector primitives (`box`, `cylinder`, `database`, `server_rack`, `cloud`, `diamond`, `badge`).
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
- **Subcommands:** `render`, `lint`, `layout export`, `mcp`, `themes`, `icons`, `api`, `examples`, `source`
- **Features:** Batch-renders scripts or whole directories to SVG/PNG/BOM without a Python entry point, exports layout files, and lists built-in themes and icons for discovery; exit codes `0` success, `1` findings or failures, `2` usage error. Machine interface: `--json` on `render`, `lint`, `themes` and `icons` prints exactly one JSON document on stdout (diagnostics and any script `print` go to stderr); `api [NAME]` lists the public Python API with signatures and summaries (the same data as the MCP `describe_api`), `examples [--domain D]` lists the gallery, `source EXAMPLE` prints an example script. Lint JSON carries file, kind, detail and the ids of the elements involved.
- **Verification:** `uv run pytest tests/test_cli.py`

---

### 2.11 Domain Architectural Reference Suite

#### `CAP-DIAG-DOMAINS`: Multi-Domain Reference Topologies & Automated Test Suite
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.1.0`
- **Python API:** `examples/` (`examples/cloud`, `examples/ai`, `examples/computer`, `examples/datacenter`, `examples/business_process`, `examples/cybersecurity`, `examples/network_engineering`, `examples/iiot`, `examples/database`, `examples/enterprise_architecture`, `examples/manufacturing`, `examples/mind_map`, `examples/computer_science`)
- **Exports:** 143 self-contained executable diagram scripts and documentation artifacts for the 13 domains above, plus 115 in twelve newer galleries (`agentic_dev`, `semiconductor`, `chemistry`, `data_engineering`, `ml_models`, `devops`, `biology`, `chemical_engineering`, `org`, `electronics`, `sequence`, `project_management`): 362 example scripts in all, with the textbook, medical, engineering, CAD, technical and primitive figures and four top-level scripts
- **Features:** 11 diagrams per domain across 13 domains (10 manually placed + 1 auto-layout) demonstrating varying architectural complexity (Simple, Moderate, Advanced, Enterprise), multi-theme deployment across the 14 presets, automated SVG and Markdown BOM generation in `examples/`, and gallery documentation in `examples/README.md`. The newer galleries have 10 figures each (`sequence` 3, `project_management` 12), mostly in the `paper` theme with computed values.
- **Verification:** `uv run pytest tests/test_domain_examples.py tests/test_textbook_examples.py` (the committed SVG beside each newer-gallery script must equal what the script renders)

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

---

### 2.16 Technical Drawing Primitives

#### `CAP-DIAG-PRIMITIVES`: Technical Drawing Primitives
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.11.0`
- **Python API:** `diagrams_as_code.primitives`, `diagrams_as_code.solids`, `diagrams_as_code.drawing`, `diagrams_as_code.arrange`
- **Exports:** `Text`, `Caption`, `Bracket`, `Polygon`, `Polyline`, `Path`, `Band`, `SolidShape`, `Solid`, `Projection`, `oblique`, `isometric`, `Junction`, `AnchorRef`, `PathItem`, `TextItem`, `align`, `distribute`, `mm`, `pt`, `to_px`; `Diagram.text()`, `.caption()`, `.bracket()`, `.polygon()`, `.polyline()`, `.path()`, `.band()`, `.point()`, `.solid()`, `.cuboid()`, `.leader()`, `.fan_out()`, `.fan_in()`
- **Features:** Free text, captions and brackets; polygons, polylines and SVG paths; dashed layer bands with side notes; shapes nested in shapes (`shape.inside()`) and double borders (`Style(double=)`); edge stroke weight, seven arrowhead styles, two-way arrows and ellipsis connectors; edge ends at fractional side anchors (`box.anchor("right", 0.25)`) or bare points, shared-trunk fan-out, leaders and splines through given points; convex solids in oblique and isometric projection with hidden-edge dashing, translucent faces and cutting planes; z-order (`z=`, `obstacle=`); `align()`, `distribute()`, `Diagram(grid=)` and lengths in px, pt, mm, cm and in. Nine focused figures in `examples/primitives/`.
- **Verification:** `uv run pytest tests/test_primitives.py tests/test_edge_options.py tests/test_solids.py tests/test_drawing.py tests/test_primitive_examples.py`

---

### 2.17 Technical Figures & Visual Regression

#### `CAP-DIAG-TECHNICAL-FIGURES`: Technical Figures, Lint and Golden Images
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.12.0`
- **Python API:** `diagrams_as_code.audit` (`audit_findings`, `audit_diagram`, `Finding`)
- **CLI:** `diagrams-as-code lint PATH... [--ignore KIND[,KIND]] [--quiet]`
- **Features:** Eleven paper-style figures in `examples/technical/`, the first a reproduction of a reference figure with its slips corrected. `lint` lays each diagram out and reports every visual defect as `script: kind: detail`, naming the elements involved; exit code 1 if any are found. Golden-image regression: every technical figure is rendered at a fixed width with pinned fonts (`tests/fixtures/fonts`) and compared with `tests/golden/technical/*.png` within an anti-aliasing tolerance; `tools/golden_images.py --update` stores new pictures. Guides: `docs/technical-figures.md`, `docs/math-markup.md`.
- **Verification:** `uv run pytest tests/test_technical_examples.py tests/test_golden_images.py tests/test_lint.py && uv run diagrams-as-code lint examples`

### 2.17a Plot Kit & Textbook Galleries

#### `CAP-DIAG-PLOT`: Plot Kit and Textbook Galleries
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.15.0`
- **Python API:** `diagrams_as_code.plot.Plot`
- **Features:** Data-space plotting on a `Diagram`, standard library only: axes with ticks, grid, linear and log mapping; function and parametric curves clipped to the window and broken at asymptotes; tangents, shaded areas and bands, Riemann rectangles; slope and vector fields; RK4 trajectories and ODE solutions; candlesticks, stacked and plain bar charts, legends, orbits with direction arrows, custom tick labels and decade log ticks. Math markup gains `\bar`, `\overline`, `\sqrt` and more function names. Fifty textbook figures in `examples/calculus_math/`, `differential_equations/`, `physics/`, `finance/` and `logic/`.
- **Verification:** `uv run pytest tests/test_plot.py tests/test_textbook_examples.py && uv run diagrams-as-code lint examples`

### 2.17b Drafting Kit & Medical, Engineering, CAD Galleries

#### `CAP-DIAG-DRAFT`: Drafting Kit and Medical, Engineering, CAD Galleries
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.16.0`
- **Python API:** `diagrams_as_code.draft.Draft`
- **Features:** Drafting and anatomy primitives, standard library only: dimension lines, radius and diameter leaders, even-odd section hatching with holes, centerlines, hidden lines, section arrows, GD&T frames, smooth organic outlines, leaders and ECG-style traces. Thirty figures in `examples/medical/`, `engineering/` and `cad/`.
- **Verification:** `uv run pytest tests/test_draft.py tests/test_clinical_engineering_examples.py && uv run diagrams-as-code lint examples`

### 2.18 Vector PDF Export

#### `CAP-DIAG-PDF`: Vector PDF Export
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.13.0`
- **Python API:** `Diagram.render_pdf(path=None)`, `diagrams_as_code.svg_to_pdf(svg)`, `PDFExportError`
- **CLI:** `diagrams-as-code render PATH... --format pdf`
- **Features:** One-page vector PDF written with the standard library alone, at 0.75 pt per px. It is drawn from the SVG the renderer writes, so paths, fills, dashes, arrowheads, opacity, text and math match the SVG. Text uses the standard PDF fonts (nothing embedded); math is outlines. SVG the writer does not understand raises `PDFExportError`. Drop shadows are approximated with translucent rings.
- **Verification:** `uv run pytest tests/test_pdf.py`

### 2.19 Model Context Protocol Server

#### `CAP-MCP-SERVER`: MCP Server
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.17.0`
- **Python API:** `diagrams_as_code.mcp.serve(root)`, `Server`
- **CLI:** `diagrams-as-code mcp [--root DIR]`
- **Features:** A stdlib-only JSON-RPC 2.0 server over stdio (MCP revision 2025-06-18) exposing `list_examples`, `render`, `lint`, `render_source`, `lint_source`, `get_example`, `list_domains`, `describe_api`, `capabilities`, `list_themes` and `list_icons`. Beyond file-based `render` and `lint`, `render_source` and `lint_source` take script text, so a client with no file-write tool can create a diagram (the SVG comes back inline, bounded at 100,000 characters with a `truncated` flag, and/or is written under `out` inside the root); `get_example`, `list_domains`, `describe_api` and `capabilities` let an agent discover what exists. Source text runs as arbitrary Python in the same sandbox. Every tool declares an `inputSchema` (descriptions, enums) and, for object results, an `outputSchema`; failures are structured as `{error: {code, message, line?}}` with a stable code (`invalid_argument`, `path_outside_root`, `not_found`, `no_scripts`, `script_error`, `timeout`, `resource_limit`, `sandbox_failure`, `output_error`, `internal_error`). Script and output paths are confined to `--root` (symlinks are re-resolved, a script-chosen output name must be a plain stem, existing symlinked outputs are refused); messages over 1 MiB and results over 200k characters are cut off; a malformed message never ends the session; error text does not carry the absolute root path. Each script runs in a resource-limited child process (`sandbox.py`): wall-clock timeout (`--timeout`, default 60 s, process group killed), CPU and memory caps on POSIX (`--memory-mb`, default 2048; address space is only enforced on Linux), stdin closed, stdout discarded, stderr capped, scrubbed environment. This limits resources and protects the protocol stream; it is not file or network isolation, so for untrusted scripts also run the server in a container.
- **Verification:** `uv run pytest tests/test_mcp.py tests/test_agent_interfaces.py`

### 2.20 Math Markup

#### `CAP-DIAG-MATH`: TeX-like Math Markup in Labels and Captions
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.19.0`
- **Python API:** Labels, captions and `Diagram.text()` containing `$...$`
- **Features:** Beyond Greek letters, operators, scripts, big operators and named functions: `\frac`, `\binom{n}{k}`, `\sqrt[n]{x}` with an index, the accents `\hat \widehat \tilde \widetilde \dot \ddot \vec \grave`, the equilibrium signs `\rightleftharpoons` and `\rightleftarrows` (two stacked arrows, not harpoons), and `\ce{H2O}` for chemical formulas (upright, with computed subscripts and charges). `\acute`, `\check` and `\breve` are unsupported (no outlines) and raise `MathError`. Reference: `docs/math-markup.md`.
- **Verification:** `uv run pytest tests/test_text_engine.py tests/test_textbook_examples.py`

### 2.21 Sequence Diagrams

#### `CAP-DIAG-SEQUENCE`: UML Sequence Diagram Kit
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.19.0`
- **Python API:** `diagrams_as_code.sequence.SequenceDiagram`, `Participant`, `Frame`, `SequenceLayout`
- **Features:** Participants (lifelines), synchronous, asynchronous and reply messages, self-calls, activation bars, notes and `loop`/`alt`/`opt`/`par`/`critical`/`break` frames, all placed by a computed layout, standard library only. Draws onto an ordinary `Diagram`, so themes, lint, SVG, PNG and PDF apply. Limits: horizontal messages only; no lost/found messages, create/destroy or `ref` frames. Three examples in `examples/sequence/`; guide: `docs/sequence-diagrams.md`.
- **Verification:** `uv run pytest tests/test_sequence.py tests/test_domain_examples.py && uv run diagrams-as-code lint examples/sequence`

### 2.22 Gantt Charts and Timelines

#### `CAP-DIAG-GANTT`: Gantt Chart and Timeline Kit
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.19.0`
- **Python API:** `diagrams_as_code.gantt.GanttChart`, `Timeline`, `schedule`, `Task`
- **Features:** `GanttChart` schedules tasks from durations and finish-to-start dependencies (with lag), groups them in phases, draws milestones, percent done and a status line, and computes and highlights the critical path, with orthogonal dependency arrows. `Timeline` places dated events on a ruler with labels stacked so none overlap. Calendar days only; about 0.5% of arrows on dense random charts can be unroutable (a warning is raised). Eleven examples in `examples/project_management/` (01-03 use the kit; 04-11 are further delivery figures); guide: `docs/gantt-timelines.md`.
- **Verification:** `uv run pytest tests/test_gantt.py tests/test_domain_examples.py && uv run diagrams-as-code lint examples/project_management`

### 2.23 Agent-Readable Documentation and Typing

#### `CAP-AGENT-DOCS`: Agent Guide, llms.txt, API Reference and Examples Index
- **Status:** `OPERATIONAL`
- **Target Release:** `v0.20.0`
- **Python API:** `diagrams_as_code` ships a `py.typed` marker (PEP 561); every public class, function and method has a docstring
- **CLI:** `uv run python tools/build_agent_docs.py [--check]`
- **Features:** `docs/for-agents.md` (choose an interface, verified quickstart, 15-call cheat sheet, render and lint loop, pitfalls, determinism and MCP limits) in which every Python and `diagrams-as-code` snippet is executed by a test. `tools/build_agent_docs.py` generates `docs/api-reference.md` (signature, docstring and location of every name in `__all__` and of the plot, draft, sequence, gantt and math kits), `docs/llms.txt` and `docs/llms-full.txt` (served at the Pages root; the CLI and MCP sections are read from the live parser and tool table) and `examples/index.json` (one record per example script). Docstring coverage of the public API has a ratchet test.
- **Verification:** `uv run pytest tests/test_agent_docs.py tests/test_for_agents_doc.py tests/test_typing_docs.py && uv run python tools/build_agent_docs.py --check`
