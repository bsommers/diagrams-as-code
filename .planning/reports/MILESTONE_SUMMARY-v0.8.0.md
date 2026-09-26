# Milestone v0.8.0 — Project Summary

**Generated:** 2026-09-26  
**Purpose:** Team onboarding and project review  
**Target Release:** `v0.8.0`  
**Milestone Focus:** Curved & Bezier Edge Routing Engine  

---

## 1. Project Overview

`diagrams-as-code` is a pure-Python directed diagramming compiler engine designed to produce deterministic, publication-quality architecture diagrams from clean, declarative Python code. The engine requires **zero external binary or C-dependencies** (no Graphviz `dot`, Cairo, or ImageMagick).

In `v0.8.0`, the framework breaks beyond rigid right-angle Manhattan lines by introducing two major visual connection capabilities:
1. **Analytical Cubic Bezier Curves (`Routing.CURVE`):** Smooth, flowing S-curves with automatic outward cardinal port normal tangent handles, distance-proportional tension scaling, native SVG `C` path emission, and physical arc-length midpoint protocol badge placement.
2. **Rounded Corner Fillets for Orthogonal Paths (`corner_radius` / `arc_radius`):** Smooth $C^1$-continuous quadratic Bezier (`Q`) bends replacing sharp 90-degree corners, governed by dynamic 50% segment budget clamping, straight port lead-in preservation, sub-pixel threshold suppression, and obstacle clearance guards.

The milestone maintains **100% backward compatibility** and bit-for-bit identical zero visual drift across all 88 domain reference diagrams when default sharp orthogonal routing is used.

---

## 2. Architecture & Technical Decisions

The codebase strictly adheres to an 8-layer downward architectural hierarchy verified by automated AST import tests (`tests/test_module_boundaries.py`):
- **Layer 0 (Core Geometry):** Vector math and shape primitives (`Point`, `Rect`, `Size`, `Anchor`, `UnitBasis`, `CubicBezier`, `QuadraticBezier`). Strict constraint: 0 internal imports.
- **Layer 1 (Vector Shapes):** Standalone SVG vector primitives and icon libraries (`ShapeLibrary`, `ShapeRenderer`).
- **Layer 2 (Model & Connections):** Graph semantic entities (`Element`, `Shape`, `Edge`, `Port`, `Routing`, `Constraint`).
- **Layer 3 (Routing & Layout Engines):** Algorithmic routing and layout solvers (`OrthogonalRouter`, `CurveRouter`, `EdgeRouter`, `LayeredLayout`).
- **Layer 4 (Presentation & SVG Emission):** Pure-Python XML/SVG code generators (`SVGRenderer`, `_render_filleted_path`).
- **Layer 5 (High-Level Diagram API):** Public fluent builder interfaces (`Diagram`, `_EdgeBuilder`).
- **Layer 6 (Documentation & BOM):** Markdown and JSON catalog generators (`BOMGenerator`).
- **Layer 7 (Command-Line Interface):** CLI entry points and argument parsing (`diagrams-as-code`).
- **Layer 8 (Public Facade):** Top-level package exports (`diagrams_as_code` and backward-compatible `iiot_diagrams`).

### Key Architectural Choices:
- **Immutable Value Objects (Layer 0):** `CubicBezier` and `QuadraticBezier` are implemented as `@dataclass(frozen=True)` to prevent mutation across solver stages.
- **Strict Waypoint Invariance (Layer 2/3):** `Edge.waypoints` remains strictly the clean sequence of anchor points or Manhattan corner vertices. Fillets and SVG commands are calculated during Layer 4 presentation, preserving layout serialization and collision simplicity.
- **Dynamic Closed-Form Clamping (Layer 4):** Corner fillets clamp radius to $R_{\text{eff}} = \min(R, L_{\text{in}}/2, L_{\text{out}}/2)$ with $O(1)$ analytical math, preventing inverted loops on short segments without iterative solvers.
- **Dual Facade Parity (Layer 8):** Every newly exposed symbol (`CubicBezier`, `QuadraticBezier`, `CurveRouter`, `EdgeRouter`, `PORT_NORMALS`) is exported in `diagrams_as_code` and automatically mirrored in `iiot_diagrams`.

---

## 3. Phases Delivered

| Phase | Name | Status | One-Liner |
|:---:|---|:---:|---|
| **08** | Core Cubic Bezier Geometry & SVG Path Generation | **Complete** | Layer 0 `CubicBezier`, Layer 3 outward port normal tangents & distance scaling, Layer 4 native SVG `M...C` path rendering, and arc-length midpoint badge positioning. |
| **09** | Rounded Corner Fillets for Orthogonal Routing | **Complete** | Layer 0 `QuadraticBezier`, Layer 2/5 `corner_radius`/`arc_radius` cascading, Layer 4 dynamic 50% budget clamping, port lead-in, obstacle apex guards, and native SVG `Q` path emission. |
| **10** | Obstacle Detection & Deflection for Curved Edges | Planned | Broadphase bounding box and De Casteljau subdivision collision detection, obstacle-deflected multi-segment splines, and lateral clearance corridors. |
| **11** | Configuration Hierarchy, Layout & Extrema Integration | Planned | Diagram-level default cascade, fluent operator inheritance, unified layout routing pipeline, and canvas auto-expansion via analytical curve extrema roots. |

---

## 4. Requirements Coverage

| Requirement ID | Description | Status | Verification Evidence |
|---|---|:---:|---|
| **BEZ-01** | Connect elements with analytical cubic Bezier curves (`Routing.CURVE`) | ✅ Complete | Verified in `tests/test_routing.py` and `tools/eval_bezier.py` |
| **BEZ-02** | Tangent handles aligned with cardinal port normal vectors (`NORTH`, `SOUTH`, `EAST`, `WEST`) | ✅ Complete | Dot product alignment > 0.999 verified in `tests/test_routing.py` |
| **BEZ-03** | Distance-proportional handle scaling along flow axes (`LR` and `TB`) | ✅ Complete | Smooth S-curve tension heuristics verified across 10 benchmark scenarios |
| **BEZ-04** | Native SVG `<path d="M... C...">` emission with tangential arrowhead markers | ✅ Complete | W3C SVG 1.1 compliant; validated via `xml.etree.ElementTree` |
| **BEZ-05** | Protocol badges centered at physical arc-length midpoint | ✅ Complete | Piecewise chord arc-length parameterization verified on asymmetric curves |
| **FILLET-01** | Configurable `corner_radius` / `arc_radius` on orthogonal edges and diagrams | ✅ Complete | Non-negative validation & diagram cascading verified in `test_diagram_api.py` |
| **FILLET-02** | Dynamic radius clamping per corner to $\min(R, L_1/2, L_2/2)$ | ✅ Complete | Short segment clamping, 2.0px suppression, & port lead-ins verified |
| **FILLET-03** | SVG renderer emits quadratic Bezier (`Q`) commands for $C^1$ smooth bends | ✅ Complete | Native `M... L... Q... L...` emission verified with `resvg-py` rasterization |

*Audit Verdict:* Phase 08 and Phase 09 evaluation reviews achieved **100/100 (PRODUCTION READY)** with 0 critical gaps.

---

## 5. Key Decisions Log

### Phase 8 Decisions (Cubic Bezier Geometry & Routing):
- **D-01:** Handle length scales proportionally along primary flow axis: $d = \max(0.5 \cdot \Delta_{\text{axis}}, 25.0)$ for standard forward flow (`LR` or `TB`).
- **D-02:** Enforce minimum handle length of 20px, with no upper clamp to allow natural scaling for distant nodes.
- **D-03:** Blend lateral offset $0.25 \cdot |\Delta_{\text{lateral}}|$ when flow-axis distance is small to avoid sharp kinks.
- **D-04:** Fixed default heuristic ($k=0.5$) with internal math ready for dynamic curvature tuning in future releases.
- **D-05:** Perpendicular ports scale incoming and outgoing handles independently by coordinate delta.
- **D-06:** Same-side / parallel ports project handles outward with vertical clearance proportional to separation.
- **D-07:** Reverse-facing or backward connections enforce a minimum clearance offset of 30px to prevent control handles from crossing.
- **D-08:** Automatic port resolution reuses `router.resolve_ports(edge)` when ports are not explicitly specified.
- **D-09:** Evaluate curve midpoint via piecewise chord arc-length parameterization (16–32 samples) for physical centering on asymmetric curves.
- **D-10:** Keep protocol label badges horizontal ($0^\circ$ rotation) to preserve typography readability.
- **D-11:** Protocol badges render as solid background pill rectangles matching node fill or badge style, passing underlying SVG strokes under the pill.
- **D-12:** Reuse existing badge sizing logic (height 18px, padding 8px) centered on the physical midpoint.
- **D-13:** Store single-segment cubic Bezier curves in `Edge.waypoints` as exactly 4 points: `[P_start, C_1, C_2, P_end]`.
- **D-14:** JSON layout export/import serializes the 4 points as standard `{x, y}` dicts.
- **D-15:** Enforce minimum distance $\|P_3 - P_2\| \ge 1.0\text{px}$ along port normal ray to prevent degenerate zero-tangent marker orientation errors.
- **D-16:** Implement `geometry.CubicBezier(p0, c1, c2, p3)` in Layer 0 as an immutable dataclass with analytical `bbox()`, `sample(n)`, `tangent_at(t)`, and `arc_length()`.

### Phase 9 Decisions (Rounded Corner Fillets):
- **D-01:** Support `corner_radius` as primary on `Edge` and `Diagram` with `arc_radius` accepted as a fully-supported alias. `Diagram(corner_radius=...)` cascades as default for all orthogonal edges; `Edge(corner_radius=...)` overrides.
- **D-02:** Sharp corners by default (`corner_radius=0.0` or `None`), preserving 100% backward compatibility and zero visual diff across all 88 gallery diagrams.
- **D-03:** `corner_radius` applies strictly to `Routing.ORTHOGONAL` edges (gracefully ignored on `DIRECT` or `CURVE`).
- **D-04:** Input validation: Coerce int/float to `float`; raise `ValueError` on negative values or non-numeric types.
- **D-05:** Strict 50% segment budget: For each corner $P_i$, $R_{\text{effective}} = \min(R, L_{\text{in}} / 2.0, L_{\text{out}} / 2.0)$, preventing adjacent arcs on shared segments from overlapping.
- **D-06:** Minimum threshold suppression: If $R_{\text{effective}} < 2.0\text{px}$, suppress the fillet to a sharp 90-degree corner, eliminating sub-pixel rasterization artifacts.
- **D-07:** Strict 90-degree turn detection ($|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$): Fillet applies strictly to genuine right angles; collinear segments and turnarounds remain linear.
- **D-08:** Endpoint straight lead-in: Segments adjacent to ports reserve at least $\min(10.0, L / 2)$ to ensure arrowheads seat flush against node boundaries.
- **D-09:** Emit native SVG quadratic Bezier commands `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y` for $C^1$ tangent continuity.
- **D-10:** Implement immutable `geometry.QuadraticBezier(p0, p1, p2)` in Layer 0 with analytical linear root derivative bounding box (`bbox()`).
- **D-11:** Keep `Edge.waypoints` as sharp Manhattan vertices `[P_0, ..., P_n]`; compute fillets dynamically during SVG path generation in Layer 4.
- **D-12:** Keep protocol badges on filleted orthogonal edges centered on the longest straight segment.
- **D-13:** Uniform filleting across both default Manhattan paths and obstacle-avoidance detour paths.
- **D-14:** Dynamic obstacle clearance guard clamps $R_{\text{effective}}$ so the fillet apex maintains $\ge 4.0\text{px}$ clearance from obstacle bounding boxes.
- **D-15:** Analytical $O(1)$ vector math per corner in pure Python standard library.
- **D-16:** Filleted paths emit standard `<path d="..." class="edge">` elements compatible with interactive pan/zoom, search, and minimap navigation.

---

## 6. Tech Debt & Deferred Items

- **Phases 10 & 11 Remaining in Roadmap:**
  - **Phase 10:** Obstacle collision detection on curved edges (bounding box broadphase + De Casteljau subdivision) and multi-segment spline deflection around intervening obstacles.
  - **Phase 11:** Auto-growth of diagram canvas bounds (`_grow_canvas`) using analytical curve extrema ($B'(t) = 0$) to prevent clipping on high-arching curves.
- **Deferred v2 Features:**
  - `EDGE-01`: Continuous curvature parameter tuning (`curvature: float = 0.5`) to allow users to customize curve tension.
  - `EDGE-02`: Bridge jump arcs (semi-circular bridge hops) where orthogonal or curved edges cross each other.
  - `EDGE-03`: Edge bundling for high-density multi-edge meshes.

---

## 7. Getting Started

### Prerequisites & Tooling
The repository mandates Astral [`uv`](https://docs.astral.sh/uv/) for all Python package management, virtual environment provisioning, and testing:
```bash
# Clone and synchronize virtual environment
git clone https://github.com/bsommers/diagrams-as-code.git
cd diagrams-as-code
uv sync
```

### Running Tests
Execute the local test suite (zero external binary dependencies required):
```bash
# Run full test suite (491 tests)
uv run pytest

# Run cubic Bezier evaluation benchmark runner
uv run python tools/eval_bezier.py

# Verify AST module boundaries
uv run pytest tests/test_module_boundaries.py
```

### Creating Your First Diagram with Curves & Fillets
```python
from diagrams_as_code import Diagram, Shape, Edge, Routing, Port

# Initialize diagram with default corner filleting
with Diagram("Architecture Overview", corner_radius=12.0) as diag:
    # Define elements
    ingress = Shape("ingress", "API Gateway", kind="cloud")
    auth = Shape("auth", "Auth Service", kind="cybersecurity").right_of(ingress, margin=80)
    db = Shape("db", "Primary DB", kind="database").below(auth, margin=60)
    analytics = Shape("analytics", "Analytics Engine", kind="ai").right_of(auth, margin=80)

    # 1. Rounded orthogonal connection (inherits corner_radius=12.0)
    ingress >> diag.edge("HTTPS") >> auth

    # 2. Smooth cubic Bezier feedback loop with protocol label
    Edge(
        source=analytics,
        target=ingress,
        routing=Routing.CURVE,
        source_port=Port.NORTH,
        target_port=Port.NORTH,
        label="Async Event",
        color="#8B5CF6"
    )

    # 3. Orthogonal connection with sharp corner override
    auth >> diag.edge(corner_radius=0.0) >> db

# Render to standalone SVG and PNG
diag.render_svg("architecture.svg")
diag.render_png("architecture.png")
```

---

## Stats

- **Timeline:** 2026-09-24 → 2026-09-26 (2 days)
- **Phases:** 2 complete / 4 total in Milestone v0.8.0
- **Commits:** 48 commits
- **Files Changed:** 72 files (+9,518 lines / -51 lines)
- **Test Suite:** 491 tests passing (100% green in 12.8s)
- **Contributors:** Bill Sommers
