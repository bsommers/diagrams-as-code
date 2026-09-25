# Stack Research

**Domain:** Vector Geometry, Curve Routing & SVG Rendering Engine (Pure Python Standard Library)
**Researched:** 2026-09-24
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python Standard Library (`math`) | `^3.10` (3.10–3.14) | Euclidean distance (`hypot`), trigonometry (`atan2`, `sin`, `cos`), square root (`sqrt`), float comparison (`isclose`) | Native CPython implementation with zero dependencies, hardware-accelerated IEEE 754 arithmetic, overflow-safe distance calculations via `math.hypot`. |
| Python Standard Library (`dataclasses`) | `^3.10` (3.10–3.14) | Immutable geometric primitives (`Point`, `Rect`, `CubicBezier`, `ControlPoints`) | Zero runtime overhead, clean value-object semantics, structural equality, and full IDE typing support. |
| Python Standard Library (`enum`) | `^3.10` (3.10–3.14) | Typed routing strategies (`Routing.CURVE`, `Routing.ORTHOGONAL`, `Routing.DIRECT`) and port anchors (`Port`) | Safe string coercion via `_coerce_enum`, strict type checking, and clean public API design. |
| W3C SVG Path Specification (`d` attribute) | SVG 1.1 / 2.0 | Vector path output syntax using `M`, `L`, `C`, `S`, `Q`, `A` commands | Universal open standard rendered natively by modern browsers, vector graphics tools (Inkscape, Illustrator), and rasterizers (`resvg-py`) without external binary layout engines. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Python Standard Library (`itertools`) | `^3.10` (3.10–3.14) | Consecutive segment and corner triplet iteration via `itertools.pairwise` | Processing orthogonal waypoint paths $(P_{i-1}, P_i, P_{i+1})$ to compute rounded corner fillet tangents without index bookkeeping. Introduced in Python 3.10 stdlib. |
| Python Standard Library (`heapq`) | `^3.10` (3.10–3.14) | Priority queue for A* waypoint detour pathfinding around obstacles | When an edge intersects obstacle elements and requires corridor search for avoidance waypoints. |
| Python Standard Library (`typing`) | `^3.10` (3.10–3.14) | Static type hints (`NamedTuple`, `Sequence`, `Union`, `Optional`, `Literal`) | Ensuring strict boundary enforcement, API contracts, and linting correctness across `geometry`, `router`, and `renderer_svg`. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `uv` | `>=0.4.0` | Environment management, test execution, dependency isolation | Strictly enforces project requirement that `dependencies = []` in `pyproject.toml`. All runs must use `uv run`. |
| `pytest` | `>=8.0.0` | Test runner for unit, integration, boundary, and regression tests | Configured in `pyproject.toml` with strict markers and pythonpath pointing to `src`. |
| `resvg-py` | `>=0.5.0` | Headless SVG rendering for image rasterization and visual regression tests | Installed strictly as a dev dependency (`dependency-groups.dev`). Never imported or required at runtime. |
| `hatchling` | `>=1.21.0` | PEP 517 build backend for wheel and sdist generation | Enforces packaging metadata without external runtime dependencies. |

## Installation

```bash
# Verify runtime dependencies remain strictly empty
python -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); assert d['project']['dependencies'] == [], 'dependencies must be empty'"

# Sync dev environment using uv
uv sync --dev

# Run complete test suite across all modules
uv run pytest
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **Cubic Bezier (`C`) for `Routing.CURVE`** | Quadratic Bezier (`Q`) | Use `Q` when only a single intermediate control point is available (e.g. 3-point arcs or 90° corner fillets). For general edge routing between two oriented ports, `C` is superior because it provides independent control points $(P_1, P_2)$ for both the source exit angle and target entry angle. |
| **Cubic Bezier (`C`) for `Routing.CURVE`** | SVG Arc (`A`) | SVG `A` (elliptical arc) requires radius, rotation, large-arc, and sweep flags. It is rigid and cannot produce the S-curves or inflection curves common in architectural node connections. `C` smoothly connects arbitrary port orientations with natural easing. |
| **Quadratic Bezier (`Q`) or Circular Arc (`A`) for Fillets** | Collinear Chamfer / Bevel (`L`) | Chamfer (`L`) cuts the corner with a flat 45° angle. Fillets (`Q` or `A`) provide publication-quality rounded corners. `Q` with control point at the original corner $P_i$ provides exact $C^1$ tangent continuity with adjacent orthogonal line segments. |
| **Piecewise Spline via Detour Waypoints for Curve Obstacle Deflection** | Force-Directed Potential Fields | Force-directed curve deformation requires iterative physics simulation steps, non-deterministic settling, and high compute overhead. Detour waypoint routing utilizes existing deterministic A* corridor search and converts the path to a smooth spline using Catmull-Rom to Bezier transformation. |
| **Port Normal Tangent Scaling Heuristic** | Fixed Offset or Polar Projection | Fixed offsets produce awkward loops when nodes are close, and stiff lines when nodes are far. Normal scaling $d = \text{clamp}(k \cdot D, d_{\min}, d_{\max})$ scales proportionally to node distance while respecting port exit directions. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `numpy` | Heavy external library (30+ MB), compiled C extensions, breaks zero-dependency mandate (`dependencies = []`). | Pure Python floats and stdlib `math` (`math.hypot`, `math.sqrt`, `math.atan2`). 2D vector operations on diagram edges require only a few dozen operations per solve, making Python float overhead negligible (< 1 ms). |
| `scipy` (`scipy.interpolate`, `scipy.spatial`) | Heavy external C/Fortran dependency. Violates zero runtime dependency constraint. | Custom standard-library Catmull-Rom to Cubic Bezier conversion matrix: $C_1 = P_i + \frac{P_{i+1} - P_{i-1}}{6}$, $C_2 = P_{i+1} - \frac{P_{i+2} - P_i}{6}$. Under 25 lines of pure Python. |
| `shapely` / `GEOS` | Requires external C library bindings (`libgeos_c`). Incompatible with pure-Python redistribution. | Standard AABB (Axis-Aligned Bounding Box) overlap and segment-rect intersection using slab method already implemented in `geometry.Rect` and `router.segment_intersects_rect`. |
| `bezier` / `pybezier` | External PyPI packages with compiled C extensions or Fortran speedups. | Explicit cubic Bezier formula: $B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3$. Midpoint evaluation at $t=0.5$ simplifies to $\frac{P_0 + 3(P_1 + P_2) + P_3}{8}$. |
| `cairosvg` / `pycairo` | Runtime C library dependency. | Native string formatting of SVG XML (`renderer_svg.py`). Cairo is only an optional external rasterizer in `rasterize.py` fallback chain. |
| `networkx` | External graph data structure library. | Built-in Python dictionaries, sets, and `heapq` for graph traversal and A* pathfinding. |

## Stack Patterns by Variant

### 1. Direct Routing (`Routing.DIRECT`)
**If `edge.routing == Routing.DIRECT`:**
- Use simple 2-point linear path:
  $$\text{SVG: } M\ x_0\ y_0\ L\ x_1\ y_1$$
- Because direct connections represent unconstrained straight-line point-to-point links. Midpoint for badge placement is $(\frac{x_0+x_1}{2}, \frac{y_0+y_1}{2})$.

### 2. Sharp Orthogonal Routing (`Routing.ORTHOGONAL`, `arc_radius <= 0`)
**If `edge.routing == Routing.ORTHOGONAL` and corner fillet radius is 0:**
- Use Manhattan grid waypoints with collinear line simplification:
  $$\text{SVG: } M\ x_0\ y_0\ L\ x_1\ y_1\ L\ x_2\ y_2 \dots L\ x_n\ y_n$$
- Because sharp 90-degree corners are the standard industrial baseline for schematic diagrams.

### 3. Filleted Orthogonal Routing (`Routing.ORTHOGONAL`, `arc_radius > 0`)
**If `edge.routing == Routing.ORTHOGONAL` and `arc_radius > 0`:**
- For each 90° corner vertex $V_i$ between incoming segment $V_{i-1} \to V_i$ (length $L_1$, unit vector $\hat{u}_1$) and outgoing segment $V_i \to V_{i+1}$ (length $L_2$, unit vector $\hat{u}_2$):
  1. Clamp radius: $r = \min(\text{arc\_radius}, L_1 / 2.0, L_2 / 2.0)$.
  2. Compute tangent start: $T_{\text{in}} = V_i - r \cdot \hat{u}_1$.
  3. Compute tangent end: $T_{\text{out}} = V_i + r \cdot \hat{u}_2$.
  4. Emit line to $T_{\text{in}}$, then quadratic arc to $T_{\text{out}}$ with control point $V_i$:
     $$\text{SVG: } \dots L\ T_{\text{in}}.x\ T_{\text{in}}.y\ Q\ V_i.x\ V_i.y\ T_{\text{out}}.x\ T_{\text{out}}.y \dots$$
     *(Alternatively via circular arc: $A\ r\ r\ 0\ 0\ \text{sweep}\ T_{\text{out}}.x\ T_{\text{out}}.y$ where $\text{sweep} = 1 \text{ if } (\hat{u}_1 \times \hat{u}_2)_z > 0 \text{ else } 0$)*.
- Because quadratic Bezier fillets with control point at $V_i$ guarantee continuous $C^1$ tangents, prevent clipping on short segments via dynamic clamping, and render cleanly across all SVG viewers.

### 4. Unobstructed Cubic Bezier Curve Routing (`Routing.CURVE`, no obstacle collision)
**If `edge.routing == Routing.CURVE` and the direct Bezier path does not intersect any obstacles:**
- Compute 4 control points $(P_0, P_1, P_2, P_3)$:
  1. $P_0 = \text{source port anchor}$, $P_3 = \text{target port anchor}$.
  2. Normal vectors: $\vec{n}_{\text{src}}$ from source port, $\vec{n}_{\text{tgt}}$ into target port ($-\text{port\_normal}$).
  3. Distance $D = \text{math.hypot}(P_3.x - P_0.x, P_3.y - P_0.y)$.
  4. Offset distance:
     - For aligned cardinal ports (e.g. East to West): $dx = P_3.x - P_0.x$, $offset = \max(dx \cdot 0.5, 40.0)$.
     - For general/perpendicular/backward ports: $offset = \max(D \cdot 0.45, 40.0)$.
  5. Control points: $P_1 = P_0 + offset \cdot \vec{n}_{\text{src}}$, $P_2 = P_3 - offset \cdot \vec{n}_{\text{tgt\_out}}$.
  6. Emit cubic Bezier path:
     $$\text{SVG: } M\ P_0.x\ P_0.y\ C\ P_1.x\ P_1.y,\ P_2.x\ P_2.y,\ P_3.x\ P_3.y$$
  7. Compute label badge position via algebraic midpoint ($t=0.5$):
     $$B(0.5) = \frac{P_0 + 3(P_1 + P_2) + P_3}{8}$$
- Because a single cubic Bezier provides smooth S-curves with port-aligned entry and exit tangents, while $B(0.5)$ provides an analytical solution for badge centering without numerical approximation.

### 5. Obstacle-Aware Deflected Bezier Curve (`Routing.CURVE`, obstacle collision detected)
**If `edge.routing == Routing.CURVE` and control polygon / curve samples intersect element bounding boxes:**
- Use existing A* corridor search to obtain detour clearance waypoints $W_0, W_1, \dots, W_m$:
  1. Filter out collinear points along straight clearance channels.
  2. Convert waypoint sequence into a multi-segment cubic Bezier spline using Catmull-Rom tangent fitting:
     - For segment $i$ from $W_i$ to $W_{i+1}$:
       $C_{i, 1} = W_i + \frac{W_{i+1} - W_{i-1}}{6}$
       $C_{i, 2} = W_{i+1} - \frac{W_{i+2} - W_i}{6}$
     - At endpoints $W_0$ and $W_m$, replace outer difference with the scaled port tangent vector $offset \cdot \vec{n}$.
  3. Emit multi-segment SVG path:
     $$\text{SVG: } M\ W_0.x\ W_0.y\ C\ C_{0,1}.x\ C_{0,1}.y,\ C_{0,2}.x\ C_{0,2}.y,\ W_1.x\ W_1.y\ C \dots$$
- Because this guarantees collision-free routing around obstacles while replacing jagged Manhattan corners with a continuous, smooth spline.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Python 3.10 | Python 3.10–3.14 | Requires `itertools.pairwise` (added in 3.10) for elegant corner fillet iteration. Type annotations use PEP 604 (`X \| Y`) and PEP 585 (`list[Point]`). |
| SVG 1.1 / 2.0 Paths | All Modern Browsers, resvg 0.5+, Inkscape, Illustrator | Standard path commands `M`, `L`, `C`, `S`, `Q`, `A` are supported uniformly across all SVG renderers since SVG 1.0 (2001). |
| `resvg-py` (dev only) | SVG 1.1 / 2.0 | Accurately rasterizes cubic Bezier curves (`C`) and quadratic/arc fillets (`Q`/`A`) for visual golden regression tests. |

## Sources

- [W3C SVG 2.0 Paths Specification (W3C Candidate Recommendation)](https://www.w3.org/TR/SVG2/paths.html) — Verified `M`, `L`, `C`, `S`, `Q`, and `A` path command grammar and arc sweep flag definitions.
- [`src/diagrams_as_code/connections.py`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py) — Verified existing `Port` (NORTH, SOUTH, EAST, WEST), `Routing` (DIRECT, ORTHOGONAL, CURVE), and `Edge.waypoints` dataclass contracts.
- [`src/diagrams_as_code/geometry.py`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py) — Verified `Point`, `Rect`, `Anchor`, and `UnitBasis` data structures.
- [`src/diagrams_as_code/router.py`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py) — Verified existing `OrthogonalRouter`, `segment_intersects_rect`, A* detour pathfinding, and collinear simplification.
- [`src/diagrams_as_code/renderer_svg.py`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py) — Verified current SVG `<path d="...">` generation and badge positioning logic.
- [`pyproject.toml`](file:///home/bill/src/ai/diagrams-as-code/pyproject.toml) — Verified runtime `dependencies = []` requirement and Python `>=3.10` target.
- Foley, van Dam, Feiner, Hughes, *Computer Graphics: Principles and Practice* (Cubic Bezier curve formulations, tangent derivatives, Catmull-Rom to Bezier transformation).

---
*Stack research for: Curved & Bezier Edge Routing Engine (`v0.8.0`)*
*Researched: 2026-09-24*
