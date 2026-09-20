# Repository Architecture & Module Hierarchy

## 1. Project Overview

The repository is organized around a clean separation of concerns:
- **Canonical Engine (`src/diagrams_as_code/`):** Pure-Python standard library directed diagrams engine. Zero C-dependencies (no Graphviz, Cairo, or ImageMagick required for vector SVG generation).
- **Backward-Compatibility Layer (`src/iiot_diagrams/`):** Re-exports canonical symbols from `diagrams_as_code` for non-breaking API evolution.
- **Domain Galleries & Test Cases (`examples/`):** 80 production reference architectures across 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, and `iiot`).
- **Vector Icon Catalog (`icons/`):** 60 handcrafted 24x24 open-source W3C SVG vector assets.
- **Automated Verification (`tests/`):** 223 parametrized unit, integration, and E2E tests validating layout solving, vector generation, and Living Documentation BOM tables.

---

## 2. Source Code Hierarchy (`src/`)

```
src/
├── diagrams_as_code/               # Canonical Root Module
│   ├── __init__.py                 # Public API exports & package version
│   ├── geometry.py                 # Geometric primitives (Point, Size, Rect, Anchor, UnitBasis)
│   ├── elements.py                 # Core Element base model and Shape node
│   ├── shapes.py                   # Vector ShapeLibrary & embedded SVG icon renderers
│   ├── groups.py                   # Group container with dynamic auto-bounding and flow layouts
│   ├── constraints.py              # Topological DAG ConstraintSolver with cycle detection
│   ├── router.py                   # Orthogonal Manhattan routing with obstacle avoidance
│   ├── connections.py              # Edge connection models & fluent >> operator overloading
│   ├── renderer_svg.py             # SVGRenderer with theme integration and defs generation
│   ├── theme.py                    # 8 Palette themes (nord, emerald, crimson, monochrome, etc.)
│   ├── bom.py                      # Bill of Materials (BOM) living markdown documentation
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

## 3. Domain Hierarchy

IIoT is treated as one of eight first-class architectural domains:

```
examples/
├── cloud/                          # 10 Cloud architecture diagrams
├── ai/                             # 10 AI / ML pipeline diagrams
├── computer/                       # 10 Computer & endpoint diagrams
├── datacenter/                     # 10 Datacenter & infrastructure diagrams
├── business_process/               # 10 Business workflow & BPMN diagrams
├── cybersecurity/                  # 10 Cybersecurity & Zero-Trust diagrams
├── network_engineering/            # 10 Campus & WAN network diagrams
└── iiot/                           # 10 Industrial IoT & automation diagrams
```

---

## 4. Key Architectural Invariants

1. **Deterministic Core:** Zero external runtime dependencies required for SVG generation.
2. **Always Use `uv`:** All environment setup, script runs, and testing must use `uv run`.
3. **Decoupled Lifecycle:** Elements exist independently of positioning constraints; positions can be declared late or updated dynamically.
4. **Guaranteed Solve:** Rendering functions (`render_svg`, `render_png`, `generate_readme`) automatically resolve layout constraints and normalize bounds before emitting output.
