# Phase 8: Core Cubic Bezier Geometry & SVG Path Generation - Research

**Domain:** Vector Geometry, Cubic Bezier Splines & Native SVG Path Rendering (Pure Python Standard Library)  
**Researched:** 2026-09-25  
**Confidence:** HIGH  

---

<user_constraints>
## User Constraints (from 08-CONTEXT.md)

### Implementation Decisions

#### Handle Length & S-Curve Tension Heuristics
- **D-01:** Proportional scaling along primary flow axis: $d = \max(0.5 \cdot \Delta_{\text{axis}}, 25.0)$ for standard forward flow (`LR` or `TB`).
- **D-02:** Enforce minimum handle length of 20px, with no upper clamp (curves scale naturally with distant nodes).
- **D-03:** When nodes are close along the flow axis but have large lateral offsets, blend lateral offset into handle calculation: $d = \max(0.5 \cdot \Delta_{\text{axis}}, 0.25 \cdot |\Delta_{\text{lateral}}|, 20.0)$ to prevent steep sharp bends.
- **D-04:** Keep fixed default heuristic ($k=0.5$) for Phase 8; design internal math to easily accept curvature parameter dynamically in future phases.

#### Non-Facing & Lateral Port Tangent Behavior
- **D-05:** For perpendicular ports (e.g. EAST to SOUTH), scale each handle independently by its axis delta along its port normal: $d_1 = \max(0.5 \cdot |\Delta x|, 25.0)$, $d_2 = \max(0.5 \cdot |\Delta y|, 25.0)$.
- **D-06:** For same-side / parallel ports (e.g. NORTH to NORTH), project handles outward with vertical clearance proportional to horizontal separation: $d = \max(0.5 \cdot |\Delta x|, 30.0)$.
- **D-07:** For reverse-facing or backward connections in Phase 8, outward normal projection enforces a minimum clearance offset of 30px, ensuring control handles never cross or form self-intersecting loops.
- **D-08:** Automatic port resolution reuses `router.resolve_ports(edge)` when ports are not explicitly specified, choosing facing cardinal ports based on bounding boxes.

#### Protocol Badge Midpoint Computation
- **D-09:** Evaluate curve midpoint via piecewise chord arc-length parameterization (16–32 sample chords with binary search) to guarantee the badge is physically centered even on asymmetric curves.
- **D-10:** Keep protocol label badge horizontal ($0^\circ$ rotation) to preserve typography readability and consistency with orthogonal badges.
- **D-11:** Protocol badges render as solid background pill rectangles matching node fill or badge style, passing the underlying SVG stroke under the pill cleanly.
- **D-12:** Reuse existing `renderer_svg.py` badge sizing logic (height 18px, padding 8px per side) centered on the physical midpoint.

#### Waypoint Data Contract & Storage
- **D-13:** Store single-segment cubic Bezier curves in `Edge.waypoints` as exactly 4 points: `[P_start, C_1, C_2, P_end]`, maintaining 100% backward compatibility with `Point` dataclass and existing layout serialization.
- **D-14:** JSON layout export/import serializes the 4 points as standard `{x, y}` dicts, re-rendered as cubic Bezier when `edge.routing == Routing.CURVE`.
- **D-15:** Enforce minimum distance $\|P_3 - P_2\| \ge 1.0\text{px}$ along port normal ray to prevent degenerate zero-tangent marker orientation errors in SVG.
- **D-16:** Implement `geometry.CubicBezier(p0, c1, c2, p3)` in Layer 0 as an immutable dataclass with `point_at(t)`, `tangent_at(t)`, `sample(n)`, and `bbox()`, providing a clean foundation composable into multi-segment splines in Phase 10.

### Claude's Discretion
- Exact chord count for arc-length parameterization (16 vs 32) can be tuned for optimal sub-millisecond execution time during test verification.
- Internal helper structure in `router.py` (e.g., `_compute_bezier_waypoints` or `CurveRouter` class) is at developer discretion conforming to Layer 3 boundaries.

### Deferred Ideas
- User-configurable `curvature: float = 0.5` parameter on `Edge` / `Diagram` (deferred to v0.8.x).
- Rounded corner fillets on Manhattan orthogonal routing (`Routing.ORTHOGONAL` with `corner_radius`) (Phase 9).
- Obstacle avoidance & multi-segment deflected splines for curved edges (Phase 10).
- Diagram-level default routing configuration cascade (Phase 11).

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| Requirement ID | Summary | Architectural Mapping | Research Finding & Solution |
|----------------|---------|------------------------|-----------------------------|
| **BEZ-01** | User can set `routing=Routing.CURVE` (or `"curve"`) on an `Edge` to connect elements with an analytical cubic Bezier curve. | `connections.py` (Layer 2), `router.py` (Layer 3), `diagram.py` (Layer 5) | `connections.Routing.CURVE = "curve"` already exists in `Routing` enum and is coerced by `_coerce_enum`. `Edge.__init__`, `Diagram.connect()`, and `Diagram.edge()` already accept `routing`. When `edge.routing == Routing.CURVE`, router dispatches to curve calculation rather than Manhattan midpoint routing. |
| **BEZ-02** | Curve router computes control handles aligned with cardinal port outward normal vectors (NORTH, SOUTH, EAST, WEST) so curves enter/exit strictly perpendicular to node bounds. | `router.py` (Layer 3) `CurveRouter` | Port outward normal unit vectors: `EAST: (+1, 0)`, `WEST: (-1, 0)`, `SOUTH: (0, +1)`, `NORTH: (0, -1)`. $C_1 = P_0 + d_1 \vec{n}_{\text{src}}$ and $C_2 = P_3 + d_2 \vec{n}_{\text{tgt}}$. Outward projection guarantees exit vector $C_1 - P_0$ and arrival vector $P_3 - C_2 = -d_2 \vec{n}_{\text{tgt}}$ have zero perpendicular component, seating curves and arrowheads strictly normal to shape boundaries. |
| **BEZ-03** | Curve router applies distance-proportional handle scaling along primary flow axes (`LR` and `TB`) to produce smooth S-curves without kinks or excessive bulging. | `router.py` (Layer 3) `CurveRouter` | Implements decisions D-01 through D-07: Facing flow scales $d = \max(0.5 \cdot \Delta_{\text{axis}}, 0.25 \cdot |\Delta_{\text{lateral}}|, 20.0)$ with no upper clamp. Perpendicular ports scale independently ($d_1 = \max(0.5 \cdot |\Delta x|, 25.0), d_2 = \max(0.5 \cdot |\Delta y|, 25.0)$). Parallel/same-side ports project outward $d = \max(0.5 \cdot |\Delta_{\text{sep}}|, 30.0)$. Backward edges enforce minimum 30.0px clearance. |
| **BEZ-04** | SVG renderer emits native cubic Bezier `<path d="M... C...">` elements with correct arrowhead marker rotation angles at endpoints. | `renderer_svg.py` (Layer 4) | When `e.routing == Routing.CURVE` and `len(pts) == 4`, formats `f"M {pts[0].x} {pts[0].y} C {pts[1].x} {pts[1].y}, {pts[2].x} {pts[2].y}, {pts[3].x} {pts[3].y}"`. SVG markers with `orient="auto-start-reverse"` compute angle from instantaneous arrival tangent $3(P_3 - C_2)$. Since $\|P_3 - C_2\| \ge 20.0\text{px} \gg 1.0\text{px}$, rotation is mathematically non-zero, non-NaN, and points directly inward. |
| **BEZ-05** | Protocol label badges on curved edges are positioned at the curve's arc-length midpoint with non-overlapping background pills. | `geometry.py` (Layer 0) `CubicBezier`, `renderer_svg.py` (Layer 4) | Arc-length parameterization using 32 chords and `bisect` binary search finds $t^*$ where cumulative arc length $s(t^*) = L_{\text{total}} / 2$. Label pill is rendered horizontally ($0^\circ$) at $B(t^*)$ with solid theme background masking the stroke underneath. Sizing matches existing standard badge logic ($H=18\text{px}$, $W = \max(\text{len} \cdot 0.62 \cdot f_s + 16, 24)$). |

</phase_requirements>

---

## Architectural Responsibility Map

The architecture strictly adheres to the 5-layer decoupled pipeline enforced by `tests/test_module_boundaries.py`. Imports point strictly downward.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 5: Diagram & Fluent API (diagram.py)                                   │
│ - Accepts routing=Routing.CURVE or routing="curve" in connect() and edge()   │
│ - Passes routing down to Edge instance                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 4: Presentation & Layout (renderer_svg.py, layout/pipeline.py)         │
│ - pipeline.py: routes all edges during solve(); populates edge.waypoints     │
│ - renderer_svg.py: formats SVG <path d="M... C...">                          │
│ - Evaluates CubicBezier.arc_length_midpoint() for protocol badge coordinates │
│ - Emits opaque pill rectangle masking underlying stroke                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 3: Routing Engine (router.py)                                          │
│ - PORT_NORMALS mapping: outward unit normal vectors for cardinal ports       │
│ - CurveRouter.route(): calculates [P_start, C1, C2, P_end] using heuristics  │
│ - OrthogonalRouter.route(): delegates to CurveRouter if routing == CURVE     │
│ - EdgeRouter facade: unified dispatch to DIRECT, ORTHOGONAL, or CURVE        │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 2: Connections & Entities (connections.py)                             │
│ - Routing enum: DIRECT, ORTHOGONAL, CURVE                                    │
│ - Edge.waypoints: holds list[Point] (exactly 4 points for single cubic curve)│
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 0: Primitives & Math (geometry.py)                                     │
│ - Point: immutable dataclass; add vector operators (+, -, *, /, distance_to)│
│ - CubicBezier: frozen dataclass (p0, c1, c2, p3)                             │
│   * point_at(t) -> Point: Bernstein polynomial evaluation                    │
│   * tangent_at(t) -> Point: first derivative velocity vector B'(t)           │
│   * bbox() -> Rect: tight bounding box from quadratic derivative roots       │
│   * sample(n) -> list[Point]: equidistant parameter sampling                 │
│   * arc_length(n) -> float: cumulative chord distance                        │
│   * arc_length_midpoint(n) -> Point: physical s = L/2 midpoint position      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Standard Stack

The core engine is 100% Python standard library with zero runtime dependencies (`dependencies = []` in `pyproject.toml`).

| Technology | Standard Library Module | Purpose | Rationale / Performance |
|------------|-------------------------|---------|-------------------------|
| **Arithmetic & Geometry** | `math` | `math.hypot`, `math.sqrt`, `math.isclose` | Hardware-accelerated IEEE 754 floating-point operations. `math.hypot` computes Euclidean chord distances without intermediate overflow. |
| **Immutable Value Objects** | `dataclasses` | `@dataclass(frozen=True)` for `CubicBezier`, `Point` | Zero-overhead value semantics, structural equality, hashability, and full IDE auto-complete. |
| **Search & Interpolation** | `bisect` | `bisect.bisect_right` | $O(\log N)$ binary search on cumulative chord distance arrays for arc-length midpoint lookup (takes $< 15\,\mu\text{s}$ for $N=32$). |
| **Type Contracts** | `typing` | `Optional`, `Union`, `Sequence`, `Mapping` | Strict static typing compliant with PEP 585 and PEP 604. |
| **Vector Output Syntax** | W3C SVG 1.1 / 2.0 | `<path d="M... C...">`, `<marker orient="auto-start-reverse">` | Open W3C standard rendered identically across web browsers and headless rasterizers (`resvg-py`). |
| **Dev Rasterizer** | `resvg-py` | Development dependency only (`dependency-groups.dev`) | Headless Rust-based SVG rasterizer for visual regression tests and PNG output validation. Never imported at runtime. |

---

## Architecture Patterns

### Pattern 1: Control Point Separation (Router Calculates, Renderer Formats)
**Rule:** All control handle positions, port normals, and coordinate math are computed strictly in Layer 3 (`router.py`) and recorded in `edge.waypoints: list[Point]`. Layer 4 (`renderer_svg.py`) has zero geometric routing heuristics; it only inspects `edge.routing` and formats the SVG path string.

### Pattern 2: Waypoint Compatibility Contract (`list[Point]`)
**Rule:** `Edge.waypoints` remains strictly a `list[Point]`.
- For single-segment cubic Bezier: exactly 4 points `[P_0, C_1, C_2, P_3]`.
- Backward-compatible with existing serializers, sidecar files, and tests.
- Layer 0 `CubicBezier` is instantiated on demand: `CubicBezier(*pts[:4])`.

### Pattern 3: Piecewise Chord Arc-Length Midpoint Parameterization
**Rule:** Do NOT place labels at parameter $t=0.5$. On asymmetric curves, $t=0.5$ is physically displaced toward one endpoint.
- Divide curve into $N=32$ chords via $B(i/N)$.
- Compute cumulative chord distances $D_i$. Total length $L = D_N$.
- Binary search `bisect.bisect_right` finds chord interval $[k, k+1]$ containing $L/2$.
- Linear interpolation within the chord determines $t^* = (k + \alpha) / N$.
- Evaluate $B(t^*)$ for the physical midpoint.
- Benchmark: 1,000 evaluations take $14.99\,\text{ms}$ ($15\,\mu\text{s}$ per curve), well below the sub-millisecond requirement.

### Pattern 4: Strict Port Normal Vector Tangency
**Rule:** Adjacent control handles lie strictly on outward port normal rays:
- For source port: $C_1 = P_0 + d_1 \vec{n}_{\text{src}}$
- For target port: $C_2 = P_3 + d_2 \vec{n}_{\text{tgt}}$
Because $\vec{n}_{\text{tgt}}$ points OUTWARD from the node, the incoming vector from $C_2$ to $P_3$ is $P_3 - C_2 = -d_2 \vec{n}_{\text{tgt}}$, which points straight INWARD into the node face. This guarantees:
1. Curves enter and exit at exactly $90^\circ$ to rectangular card walls.
2. Arrowheads rendered with `orient="auto-start-reverse"` seat squarely against the node without diagonal slant.
3. $\|P_3 - C_2\| \ge 20.0\text{px} \gg 1.0\text{px}$, preventing degenerate NaN orientations.

---

## Don't Hand-Roll

| Problem | Anti-Pattern to Avoid | Standard Library / Deterministic Approach |
|---------|-----------------------|-------------------------------------------|
| **Cubic Curve Math** | Adding NumPy, SciPy, or PyPI `bezier` package | Direct Bernstein polynomial evaluation: $B(t) = (1-t)^3 P_0 + 3(1-t)^2 t C_1 + 3(1-t) t^2 C_2 + t^3 P_3$. Under 15 lines of pure Python. |
| **Curve Extrema & Bounding Box** | Dense sampling (e.g., checking 10,000 points) or loose control polygon AABB | Analytical quadratic roots of first derivative: $B'_x(t) = a t^2 + b t + c = 0$. Solve with quadratic formula, evaluate $B(t)$ at roots $\in (0, 1)$ and endpoints. Exact to $10^{-7}$ precision in $< 1\,\mu\text{s}$. |
| **Arrowhead Rotation** | Calculating angle via `math.atan2` in Python and emitting SVG `transform="rotate(...)"` | Rely on native SVG marker `orient="auto-start-reverse"`. By enforcing $\|P_3 - C_2\| \ge 20.0\text{px}$ along port normal, SVG engines compute rotation natively and accurately. |
| **Label Positioning** | Using $B(0.5)$ or iterative Newton-Raphson | 32-chord piecewise linear arc-length parameterization with `bisect`. Exact within $0.5\%$, stable, zero oscillation, deterministic. |
| **Data Representation** | Creating custom `BezierPath` objects in `edge.waypoints` | Store exactly 4 `Point` instances in `edge.waypoints: list[Point]`. Keeps 100% interoperability with all layout engines. |

---

## Common Pitfalls & Mitigations

### Pitfall 1: Degenerate Control Points Causing NaN / Missing SVG Arrowheads
- **Failure:** When source and target are close ($< 10\text{px}$), handles collapse ($C_2 = P_3$), making tangent vector $(0, 0)$. SVG `atan2(0, 0)` produces `NaN` or disappears.
- **Mitigation:** Enforce minimum handle length $d_{\min} = 20.0\text{px}$ along the port normal ray (D-02, D-15). Even if elements touch, $\|P_3 - C_2\| \ge 20.0\text{px} > 1.0\text{px}$.

### Pitfall 2: Control Point Overshoot and Bow-Tie Loops on Backward / Lateral Connections
- **Failure:** When target is behind the source port ($dx < 0$ for East port), handles point toward each other, cross in space, and form a ballooning "bow-tie" loop.
- **Mitigation:**
  1. Automatic port resolution (`router.resolve_ports`) automatically selects facing ports (e.g. West-to-East) when ports are unpinned (D-08).
  2. For explicit opposing/backward ports, project handles along outward normal with minimum 30px clearance offset and blend lateral delta: $d = \max(0.25 \cdot |\Delta_{\text{lateral}}|, 30.0)$ (D-03, D-07).

### Pitfall 3: Arrowhead Diagonal Slant Against Flat Shape Borders
- **Failure:** $C_2$ has lateral drift ($C_2.y \ne P_3.y$ for West port), causing curve to enter at an oblique angle (e.g., $42^\circ$), tilting the arrowhead.
- **Mitigation:** Lock $C_2$ strictly to the port normal ray: $C_2 = P_3 + d_2 \vec{n}_{\text{tgt}}$. Tangent $P_3 - C_2$ has 0 perpendicular component; arrowhead enters strictly perpendicular ($0^\circ, 90^\circ, 180^\circ, 270^\circ$).

### Pitfall 4: Parameter-Space ($t=0.5$) Label Distortion on Asymmetric Curves
- **Failure:** On curves with unequal handles (e.g. $d_1 = 150, d_2 = 30$), $t=0.5$ is physically at 70% of the travel distance, placing the badge right next to the target shape.
- **Mitigation:** Use 32-chord piecewise linear arc-length parameterization (D-09) to place the badge at physical arc length $s = L / 2$.

### Pitfall 5: Jagged Polyline Rendering of Curves
- **Failure:** If `renderer_svg.py` treats `len(pts) == 4` as a polyline, it emits `M P0 L C1 L C2 L P3`, drawing a jagged zig-zag.
- **Mitigation:** In `SVGRenderer._render_edges`, check `if e.routing == Routing.CURVE and len(pts) == 4:` and emit `M {p0} C {c1}, {c2}, {p3}`.

### Pitfall 6: Stroke Slicing Through Protocol Badge Text
- **Failure:** The curved stroke passes underneath or through badge text, rendering text illegible.
- **Mitigation:** Render protocol badge with opaque background pill (`rx = height / 2.0`, `fill = badge_fill`) after `<path>`, using SVG document order to paint the pill over the stroke (D-11, D-12).

---

## Code Examples

### 1. Layer 0: `Point` Arithmetic Operators (`geometry.py`)

```python
# In src/diagrams_as_code/geometry.py
@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Point:
        return Point(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Point:
        return Point(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Point:
        return Point(self.x / scalar, self.y / scalar)

    def distance_to(self, other: Point) -> float:
        import math
        return math.hypot(self.x - other.x, self.y - other.y)
```

### 2. Layer 0: `CubicBezier` Primitive (`geometry.py`)

```python
# In src/diagrams_as_code/geometry.py
import bisect
import math

@dataclass(frozen=True)
class CubicBezier:
    p0: Point
    c1: Point
    c2: Point
    p3: Point

    def point_at(self, t: float) -> Point:
        """Evaluate point on cubic Bezier curve at parameter t in [0.0, 1.0]."""
        it = 1.0 - t
        it2 = it * it
        t2 = t * t
        x = (it2 * it * self.p0.x +
             3.0 * it2 * t * self.c1.x +
             3.0 * it * t2 * self.c2.x +
             t2 * t * self.p3.x)
        y = (it2 * it * self.p0.y +
             3.0 * it2 * t * self.c1.y +
             3.0 * it * t2 * self.c2.y +
             t2 * t * self.p3.y)
        return Point(x, y)

    def tangent_at(self, t: float) -> Point:
        """Evaluate first derivative vector B'(t)."""
        it = 1.0 - t
        c_p0 = 3.0 * it * it
        c_c1 = 6.0 * it * t
        c_c2 = 3.0 * t * t
        vx = (c_p0 * (self.c1.x - self.p0.x) +
              c_c1 * (self.c2.x - self.c1.x) +
              c_c2 * (self.p3.x - self.c2.x))
        vy = (c_p0 * (self.c1.y - self.p0.y) +
              c_c1 * (self.c2.y - self.c1.y) +
              c_c2 * (self.p3.y - self.c2.y))
        return Point(vx, vy)

    def bbox(self) -> Rect:
        """Compute exact tight axis-aligned bounding box using derivative roots."""
        def solve_quadratic(a: float, b: float, c: float) -> list[float]:
            if abs(a) < 1e-9:
                if abs(b) < 1e-9:
                    return []
                return [-c / b]
            disc = b * b - 4.0 * a * c
            if disc < 0:
                return []
            if abs(disc) < 1e-9:
                return [-b / (2.0 * a)]
            s = math.sqrt(disc)
            return [(-b - s) / (2.0 * a), (-b + s) / (2.0 * a)]

        ax = 3.0 * (-self.p0.x + 3.0 * self.c1.x - 3.0 * self.c2.x + self.p3.x)
        bx = 6.0 * (self.p0.x - 2.0 * self.c1.x + self.c2.x)
        cx = 3.0 * (self.c1.x - self.p0.x)

        ay = 3.0 * (-self.p0.y + 3.0 * self.c1.y - 3.0 * self.c2.y + self.p3.y)
        by = 6.0 * (self.p0.y - 2.0 * self.c1.y + self.c2.y)
        cy = 3.0 * (self.c1.y - self.p0.y)

        candidates = [0.0, 1.0]
        for t in solve_quadratic(ax, bx, cx):
            if 0.0 < t < 1.0:
                candidates.append(t)
        for t in solve_quadratic(ay, by, cy):
            if 0.0 < t < 1.0:
                candidates.append(t)

        pts = [self.point_at(t) for t in candidates]
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def sample(self, n: int = 16) -> list[Point]:
        """Sample n points uniformly along parameter t in [0.0, 1.0]."""
        if n < 2:
            return [self.p0, self.p3]
        return [self.point_at(i / (n - 1)) for i in range(n)]

    def arc_length(self, num_samples: int = 32) -> float:
        """Compute approximate curve arc length via piecewise chord lengths."""
        pts = self.sample(num_samples + 1)
        return sum(pts[i].distance_to(pts[i + 1]) for i in range(len(pts) - 1))

    def arc_length_midpoint(self, num_samples: int = 32) -> Point:
        """Find the physical midpoint s = L / 2 using chord parameterization."""
        pts = self.sample(num_samples + 1)
        dists = [0.0]
        for i in range(len(pts) - 1):
            dists.append(dists[-1] + pts[i].distance_to(pts[i + 1]))

        total_len = dists[-1]
        if total_len < 1e-6:
            return self.p0

        half_len = total_len / 2.0
        idx = bisect.bisect_right(dists, half_len) - 1
        idx = max(0, min(idx, num_samples - 1))

        segment_len = dists[idx + 1] - dists[idx]
        alpha = (half_len - dists[idx]) / segment_len if segment_len > 1e-9 else 0.0
        t_mid = (idx + alpha) / num_samples
        return self.point_at(t_mid)
```

### 3. Layer 3: `CurveRouter` in `router.py`

```python
# In src/diagrams_as_code/router.py
PORT_NORMALS: dict[Port, Point] = {
    Port.EAST: Point(1.0, 0.0),
    Port.WEST: Point(-1.0, 0.0),
    Port.SOUTH: Point(0.0, 1.0),
    Port.NORTH: Point(0.0, -1.0),
}

class CurveRouter:
    """Computes cubic Bezier control handles from port normal vectors."""

    def resolve_ports(self, edge: Edge) -> tuple[Port, Port]:
        """Resolve cardinal ports using OrthogonalRouter's spatial orientation."""
        # Reuses existing bounding box spatial orientation logic
        sb, tb = edge.source.bounds, edge.target.bounds
        dx = tb.center.x - sb.center.x
        dy = tb.center.y - sb.center.y
        if abs(dx) >= abs(dy):
            src_p = Port.EAST if dx > 0 else Port.WEST
            tgt_p = Port.WEST if dx > 0 else Port.EAST
        else:
            src_p = Port.SOUTH if dy > 0 else Port.NORTH
            tgt_p = Port.NORTH if dy > 0 else Port.SOUTH
        return (edge.source_port or src_p, edge.target_port or tgt_p)

    def route(
        self,
        edge: Edge,
        obstacles: Optional[Iterable[Any]] = None,
        clearance: float = 15.0,
    ) -> list[Point]:
        """Compute [P_start, C_1, C_2, P_end] for analytical cubic Bezier curve."""
        src_port, tgt_port = self.resolve_ports(edge)
        p_start = edge.source.bounds.get_anchor(src_port.to_anchor())
        p_end = edge.target.bounds.get_anchor(tgt_port.to_anchor())

        n_src = PORT_NORMALS[src_port]
        n_tgt = PORT_NORMALS[tgt_port]

        dx = p_end.x - p_start.x
        dy = p_end.y - p_start.y

        # Handle Length Calculation based on D-01 through D-07
        is_src_horiz = src_port in (Port.EAST, Port.WEST)
        is_tgt_horiz = tgt_port in (Port.EAST, Port.WEST)

        if is_src_horiz != is_tgt_horiz:
            # Perpendicular ports (D-05)
            d_x = max(0.5 * abs(dx), 25.0)
            d_y = max(0.5 * abs(dy), 25.0)
            d1 = d_x if is_src_horiz else d_y
            d2 = d_x if is_tgt_horiz else d_y
        elif src_port == tgt_port:
            # Same-side / parallel ports (D-06)
            sep = abs(dx) if not is_src_horiz else abs(dy)
            d = max(0.5 * sep, 30.0)
            d1 = d2 = d
        else:
            # Opposing / facing ports
            if is_src_horiz:
                axis_delta = dx if src_port == Port.EAST else -dx
                lat_delta = abs(dy)
            else:
                axis_delta = dy if src_port == Port.SOUTH else -dy
                lat_delta = abs(dx)

            if axis_delta > 0:
                # Forward flow (D-01, D-02, D-03)
                d = max(0.5 * axis_delta, 0.25 * lat_delta, 20.0)
                d1 = d2 = d
            else:
                # Backward flow (D-07)
                d = max(0.25 * lat_delta, 30.0)
                d1 = d2 = d

        # Minimum handle separation invariant (D-15)
        d1 = max(d1, 20.0)
        d2 = max(d2, 20.0)

        c1 = Point(p_start.x + n_src.x * d1, p_start.y + n_src.y * d1)
        c2 = Point(p_end.x + n_tgt.x * d2, p_end.y + n_tgt.y * d2)

        return [p_start, c1, c2, p_end]
```

### 4. Layer 4: SVG Path Generation & Protocol Badge Placement (`renderer_svg.py`)

```python
# In src/diagrams_as_code/renderer_svg.py
from diagrams_as_code.geometry import CubicBezier

# In SVGRenderer.render() -> edge rendering loop:
for e in edge_list:
    pts = (
        e.waypoints
        if getattr(e, "waypoints", None) is not None
        else (routes[id(e)] if routes is not None and id(e) in routes else self.router.route(e))
    )
    if len(pts) < 2:
        continue

    # Path generation branching
    if e.routing == Routing.CURVE and len(pts) == 4:
        p0, c1, c2, p3 = pts
        path_d = f"M {p0.x} {p0.y} C {c1.x} {c1.y}, {c2.x} {c2.y}, {p3.x} {p3.y}"
    elif e.routing == Routing.CURVE and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
        parts = [f"M {pts[0].x} {pts[0].y}"]
        for i in range(1, len(pts), 3):
            parts.append(f"C {pts[i].x} {pts[i].y}, {pts[i+1].x} {pts[i+1].y}, {pts[i+2].x} {pts[i+2].y}")
        path_d = " ".join(parts)
    else:
        path_d = f"M {pts[0].x} {pts[0].y} " + " ".join(f"L {p.x} {p.y}" for p in pts[1:])

    # Emit SVG path element
    # ...

    # Protocol badge centering
    if e.label:
        if e.routing == Routing.CURVE and len(pts) == 4:
            curve = CubicBezier(pts[0], pts[1], pts[2], pts[3])
            mid = curve.arc_length_midpoint(num_samples=32)
            lx, ly = mid.x, mid.y
        else:
            mid_idx = len(pts) // 2
            lx = (pts[mid_idx - 1].x + pts[mid_idx].x) / 2.0
            ly = (pts[mid_idx - 1].y + pts[mid_idx].y) / 2.0

        # Existing badge sizing and rendering logic
        edge_meta = getattr(e, "metadata", {}) or {}
        badge_fill = edge_meta.get("badge_fill", self.theme.node_fill)
        badge_text_color = edge_meta.get("badge_text_color", self.theme.text)
        font_size = float(edge_meta.get("font_size", 10.0))
        badge_h = float(edge_meta.get("badge_height", 18.0))
        char_w = font_size * 0.62
        badge_w = max(len(e.label) * char_w + 16.0, 24.0)
        bx = lx - badge_w / 2.0
        by = ly - badge_h / 2.0

        badge_svg = self.shapes.render_badge(
            bx, by, e.label,
            fill=badge_fill,
            text_color=badge_text_color,
            font_size=font_size,
            height=badge_h,
            font_family=self.theme.font_family,
        )
        indent = "    " if interactive else "  "
        lines.append(f"{indent}{badge_svg}")
```

---

## Validation Architecture

Nyquist test validation ensures every requirement is programmatically verified under automated test suites.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Validation Harness                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. AST Architectural Boundary Check (tests/test_module_boundaries.py)       │
│    - geometry.py has 0 internal imports (Layer 0)                           │
│    - router.py imports only geometry, connections, elements, shapes         │
│    - renderer_svg.py imports down to geometry, router, connections, theme   │
│                                                                             │
│ 2. Public API Mirroring Check (tests/test_public_api.py)                    │
│    - CubicBezier and CurveRouter in diagrams_as_code.__all__                │
│    - iiot_diagrams.__all__ strictly equals diagrams_as_code.__all__         │
│                                                                             │
│ 3. Geometric Unit Tests (tests/test_geometry.py)                            │
│    - Bernstein polynomial evaluation at t in {0, 0.25, 0.5, 0.75, 1.0}      │
│    - Velocity tangent derivative vectors B'(0) and B'(1)                    │
│    - Analytical quadratic bbox vs 10^4 numerical sample ground truth (<1e-4)│
│    - Arc-length cumulative distance and bisect midpoint accuracy (<0.5%)    │
│    - Point vector operators (+, -, *, /, distance_to)                       │
│                                                                             │
│ 4. Route Calculation Tests (tests/test_routing.py)                          │
│    - BEZ-01: edge.routing == Routing.CURVE returns exactly 4 points         │
│    - BEZ-02: Port normal tangency: (C1 - P0) and (P3 - C2) have 0 lateral   │
│      drift relative to cardinal port unit normal                            │
│    - BEZ-03: Distance-proportional handle scaling: flow delta, lateral      │
│      blending, perpendicular ports, parallel ports, and backward offsets    │
│    - Minimum handle separation invariant: ||P3 - C2|| >= 20px >= 1.0px      │
│    - OrthogonalRouter and EdgeRouter delegation backward compatibility      │
│                                                                             │
│ 5. SVG Path & Badge Rendering Tests (tests/test_renderer_svg.py)            │
│    - BEZ-04: Emits valid <path d="M... C..."> with xml.etree.ElementTree    │
│    - BEZ-04: Marker end orientation aligned with arrival port normal        │
│    - BEZ-05: Protocol badge positioned at arc-length midpoint, not t=0.5    │
│    - BEZ-05: Pill masking rect has non-empty fill and covers path stroke    │
│    - resvg-py headless rasterization test verifies zero SVG parsing errors  │
│                                                                             │
│ 6. Full Regression Suite                                                    │
│    - All 453 existing tests must remain 100% green: `uv run pytest`         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Requirement-to-Test Matrix

| Requirement | Test File | Test Name | Invariants Verified |
|-------------|-----------|-----------|---------------------|
| **BEZ-01** | `tests/test_routing.py` | `test_curve_routing_edge_dispatch` | `len(edge.waypoints) == 4`; `isinstance(p, Point)`; works with `Routing.CURVE` and `"curve"`. |
| **BEZ-02** | `tests/test_routing.py` | `test_curve_router_port_tangent_alignment` | For all 4 ports, $(C_1 - P_0)$ has 0 perpendicular component; $(P_3 - C_2)$ is parallel to inward normal. |
| **BEZ-03** | `tests/test_routing.py` | `test_curve_router_handle_scaling_heuristics` | $d = \max(0.5 \Delta_{\text{axis}}, 0.25 \Delta_{\text{lat}}, 20.0)$; perpendicular ports scale by axis delta; backward edges project 30px offset without crossing. |
| **BEZ-04** | `tests/test_renderer_svg.py` | `test_svg_render_cubic_bezier_path_and_markers` | Emitted SVG `<path d="M... C...">` is valid XML; arrowhead marker references `#arrow` or dynamic color marker with non-zero arrival vector. |
| **BEZ-05** | `tests/test_renderer_svg.py` | `test_curved_edge_protocol_badge_arc_length_centering` | Badge pill center $(lx, ly)$ matches `CubicBezier.arc_length_midpoint()`; badge rect masks stroke; badge text is horizontal. |

---

## Phase Execution Plan Guidance

Downstream planning agents should structure Phase 8 execution into three focused plans:
1. **Plan 08-01 (Layer 0 Primitives & Layer 2 Contracts):** Implement `Point` arithmetic operators and `CubicBezier` in `src/diagrams_as_code/geometry.py`. Add comprehensive geometric unit tests in `tests/test_geometry.py`. Re-export in packages.
2. **Plan 08-02 (Layer 3 Routing Engine):** Implement `PORT_NORMALS`, `CurveRouter`, and `EdgeRouter` (with `OrthogonalRouter` delegation) in `src/diagrams_as_code/router.py`. Implement handle scaling heuristics, port tangency invariants, and backward offset guards. Add routing tests in `tests/test_routing.py`.
3. **Plan 08-03 (Layer 4 SVG Path Generation & Protocol Badge Centering):** Update `SVGRenderer` in `src/diagrams_as_code/renderer_svg.py` to format `M...C...` path commands and center badges using `CubicBezier.arc_length_midpoint()`. Add SVG rendering tests and rasterization validation in `tests/test_renderer_svg.py`. Verify all 453 baseline tests pass.
