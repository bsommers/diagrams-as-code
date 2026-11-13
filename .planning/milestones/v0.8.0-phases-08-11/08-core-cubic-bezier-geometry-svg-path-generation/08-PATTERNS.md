# Phase 8: Core Cubic Bezier Geometry & SVG Path Generation - Pattern Map

**Domain:** Vector Geometry, Cubic Bezier Splines & Native SVG Path Rendering (Pure Python Standard Library)  
**Output Target:** `.planning/phases/08-core-cubic-bezier-geometry-svg-path-generation/08-PATTERNS.md`

---

## 1. Target File Map

| Target File | Action | Layer & Role | Data Flow | Closest Existing Codebase Analog |
|-------------|--------|--------------|-----------|----------------------------------|
| `src/diagrams_as_code/geometry.py` | Modify | Layer 0: Primitives & Math | Leaf mathematical module; imported downward by layers 1-5; 0 internal dependencies | `Point` ([geometry.py:6-9](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L6-L9)), `Rect` ([geometry.py:27-129](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L27-L129)) |
| `src/diagrams_as_code/router.py` | Modify | Layer 3: Routing Engine | Receives `Edge` (Layer 2) and obstacle elements; computes `list[Point]` waypoints along outward port normal rays | `OrthogonalRouter` ([router.py:51-137](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L51-L137)) |
| `src/diagrams_as_code/renderer_svg.py` | Modify | Layer 4: Presentation & SVG Emission | Formats SVG strings (`<path d="M... C...">`, `<rect>` badges) from computed `edge.waypoints` | `SVGRenderer._render_edges` ([renderer_svg.py:591-667](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py#L591-L667)) |
| `src/diagrams_as_code/__init__.py` | Modify | Layer 8: Public API Facade | Re-exports canonical classes (`CubicBezier`, `CurveRouter`, `EdgeRouter`) and registers in `__all__` | `__init__.py` exports ([__init__.py:1-114](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/__init__.py#L1-L114)) |
| `tests/test_geometry.py` | Modify | Test Suite: Layer 0 Math | Validates arithmetic operators, Bernstein evaluation, tangents, quadratic bbox, and chord arc lengths | `test_rect_anchor_points` & `test_immutability` ([test_geometry.py:13-37](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py#L13-L37)) |
| `tests/test_routing.py` | Modify | Test Suite: Layer 3 Routing | Validates port tangency collinearity, distance-proportional handle scaling, and backward clearances | `test_manhattan_routing_*` ([test_routing.py:206-270](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L206-L270)) |
| `tests/test_renderer_svg.py` | Modify | Test Suite: Layer 4 Rendering | Validates XML well-formedness, `M... C...` syntax, arrowhead orientation, and arc-length badge placement | `test_svg_xml_parse_validation` & badge tests ([test_renderer_svg.py:44-96](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py#L44-L96)) |
| `tests/test_public_api.py` | Modify | Test Suite: API Mirroring | Verifies newly added public classes are reachable and mirrored across both namespace facades | `test_every_advertised_name_is_reachable` ([test_public_api.py:19-32](file:///home/bill/src/ai/diagrams-as-code/tests/test_public_api.py#L19-L32)) |

---

## 2. Component Patterns & Analog Excerpts

### Pattern 1: Layer 0 Vector Arithmetic & Bezier Primitives (`geometry.py`)

#### Codebase Analog
Existing immutable `Point` and analytical `Rect` in [src/diagrams_as_code/geometry.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L6-L33):
```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float
```

#### New Implementation Pattern
```python
import bisect
import math
from dataclasses import dataclass

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
        return math.hypot(self.x - other.x, self.y - other.y)


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
        """Evaluate first derivative velocity vector B'(t)."""
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
        """Compute exact tight axis-aligned bounding box using quadratic derivative roots."""
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

#### Invariants & Anti-Patterns
- **Immutable Value Semantics:** `Point` and `CubicBezier` must remain `@dataclass(frozen=True)` (D-16).
- **Zero Inter-Module Imports:** `geometry.py` belongs to Layer 0. It must NEVER import from any module in `diagrams_as_code` (enforced by `tests/test_module_boundaries.py`).
- **No Third-Party Math Dependencies:** Pure Python standard library only (`math`, `bisect`, `dataclasses`). Do not import `numpy` or `scipy`.

---

### Pattern 2: Layer 3 Tangent Handles & S-Curve Tension Routing (`router.py`)

#### Codebase Analog
Existing `resolve_ports` and dispatch structure in [src/diagrams_as_code/router.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L51-L85):
```python
class OrthogonalRouter:
    """Computes orthogonal Manhattan waypoints and resolves port anchors."""

    def resolve_ports(self, edge: Edge) -> tuple[Port, Port]:
        if edge.source_port and edge.target_port:
            return (edge.source_port, edge.target_port)

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
```

#### New Implementation Pattern
```python
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
        if edge.source_port and edge.target_port:
            return (edge.source_port, edge.target_port)
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
            # Facing or opposing ports
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

#### Backward Compatibility Delegation in `OrthogonalRouter` and `EdgeRouter`
```python
# In OrthogonalRouter.route:
if edge.routing == Routing.CURVE:
    return CurveRouter().route(edge, obstacles=obstacles, clearance=clearance)

# EdgeRouter facade:
class EdgeRouter:
    """Unified routing facade dispatching across DIRECT, ORTHOGONAL, and CURVE strategies."""

    def __init__(self) -> None:
        self.orthogonal = OrthogonalRouter()
        self.curve = CurveRouter()

    def route(
        self,
        edge: Edge,
        obstacles: Optional[Iterable[Any]] = None,
        clearance: float = 15.0,
    ) -> list[Point]:
        if edge.routing == Routing.CURVE:
            return self.curve.route(edge, obstacles=obstacles, clearance=clearance)
        return self.orthogonal.route(edge, obstacles=obstacles, clearance=clearance)
```

#### Invariants & Anti-Patterns
- **Strict Cardinal Normal Collinearity (BEZ-02):** $C_1 - P_0$ and $P_3 - C_2$ MUST be parallel to port normal unit vectors with 0 perpendicular component.
- **Minimum Handle Length (D-15):** $\|C_1 - P_0\| \ge 20.0\text{px}$ and $\|P_3 - C_2\| \ge 20.0\text{px}$. Control points must NEVER coincide with endpoints ($d \ge 1.0\text{px}$).
- **Waypoint Structure (D-13):** `route()` MUST return `list[Point]` with exactly 4 elements `[P0, C1, C2, P3]`.

---

### Pattern 3: Layer 4 SVG `<path d="M... C...">` & Midpoint Badge Placement (`renderer_svg.py`)

#### Codebase Analog
Existing edge rendering and protocol badge generation in [src/diagrams_as_code/renderer_svg.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py#L591-L667):
```python
for e in edge_list:
    pts = (
        e.waypoints
        if getattr(e, "waypoints", None) is not None
        else (routes[id(e)] if routes is not None and id(e) in routes else self.router.route(e))
    )
    if len(pts) < 2:
        continue

    path_d = f"M {pts[0].x} {pts[0].y} " + " ".join(
        f"L {p.x} {p.y}" for p in pts[1:]
    )
    # ...
    # Centered protocol badge so edge lines don't cross text
    if e.label:
        mid_idx = len(pts) // 2
        lx = (pts[mid_idx - 1].x + pts[mid_idx].x) / 2.0
        ly = (pts[mid_idx - 1].y + pts[mid_idx].y) / 2.0
```

#### New Implementation Pattern
```python
from diagrams_as_code.connections import Routing
from diagrams_as_code.geometry import CubicBezier

# Inside SVGRenderer.render() edge rendering loop:
for e in edge_list:
    pts = (
        e.waypoints
        if getattr(e, "waypoints", None) is not None
        else (routes[id(e)] if routes is not None and id(e) in routes else self.router.route(e))
    )
    if len(pts) < 2:
        continue

    # Path generation branching (BEZ-04)
    if e.routing == Routing.CURVE and len(pts) == 4:
        p0, c1, c2, p3 = pts
        path_d = f"M {p0.x} {p0.y} C {c1.x} {c1.y}, {c2.x} {c2.y}, {p3.x} {p3.y}"
    elif e.routing == Routing.CURVE and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
        parts = [f"M {pts[0].x} {pts[0].y}"]
        for i in range(1, len(pts), 3):
            parts.append(f"C {pts[i].x} {pts[i].y}, {pts[i+1].x} {pts[i+1].y}, {pts[i+2].x} {pts[i+2].y}")
        path_d = " ".join(parts)
    else:
        path_d = f"M {pts[0].x} {pts[0].y} " + " ".join(
            f"L {p.x} {p.y}" for p in pts[1:]
        )

    # Edge stroke and marker attributes emission (unchanged)
    # ...

    # Protocol badge centering (BEZ-05, D-09..D-12)
    if e.label:
        if e.routing == Routing.CURVE and len(pts) == 4:
            curve = CubicBezier(pts[0], pts[1], pts[2], pts[3])
            mid = curve.arc_length_midpoint(num_samples=32)
            lx, ly = mid.x, mid.y
        else:
            mid_idx = len(pts) // 2
            lx = (pts[mid_idx - 1].x + pts[mid_idx].x) / 2.0
            ly = (pts[mid_idx - 1].y + pts[mid_idx].y) / 2.0

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
            bx,
            by,
            e.label,
            fill=badge_fill,
            text_color=badge_text_color,
            font_size=font_size,
            height=badge_h,
            font_family=self.theme.font_family,
        )
        indent = "    " if interactive else "  "
        lines.append(f"{indent}{badge_svg}")
```

#### Invariants & Anti-Patterns
- **Do Not Fall Back to `L` Commands on Curves (Pitfall 5):** When `e.routing == Routing.CURVE and len(pts) == 4`, NEVER emit `L` segments; emit single cubic Bezier `C` command.
- **Physical Arc-Length Midpoint over $t=0.5$ (Pitfall 4):** Do NOT use `curve.point_at(0.5)`. Always use `curve.arc_length_midpoint(num_samples=32)`.
- **Horizontal Badges Only (D-10):** Protocol badges remain horizontally aligned ($0^\circ$) without rotated text transforms.
- **Layer Separation:** Layer 4 formats SVG strings; it never mutates edge waypoints or executes heuristic path calculations.

---

### Pattern 4: Top-Level Exports & API Facades (`__init__.py`)

#### Codebase Analog
Existing exports in [src/diagrams_as_code/__init__.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/__init__.py#L14-L29):
```python
from diagrams_as_code.geometry import Anchor, Point, Rect, Size, UnitBasis
from diagrams_as_code.router import OrthogonalRouter
```

#### New Implementation Pattern
```python
# In src/diagrams_as_code/__init__.py:
from diagrams_as_code.geometry import Anchor, CubicBezier, Point, Rect, Size, UnitBasis
from diagrams_as_code.router import CurveRouter, EdgeRouter, OrthogonalRouter

__all__ = [
    # ...
    "CubicBezier",
    "CurveRouter",
    "EdgeRouter",
    # ... sorted alphabetically
]
```

#### Invariants & Anti-Patterns
- **Alphabetical Sorting:** Keep `__all__` sorted alphabetically.
- **Facade Mirroring:** `iiot_diagrams/__init__.py` mirrors `diagrams_as_code.__all__` via `__all__ = list(_dac.__all__)`. Both must expose identical sets of symbols (checked by `test_the_facade_mirrors_the_canonical_package`).

---

## 3. Test Patterns & Recipes

### Pattern 5: Mathematical Unit Tests (`tests/test_geometry.py`)

#### Codebase Analog
Existing immutability and anchor tests in [tests/test_geometry.py](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py#L13-L37):
```python
def test_rect_anchor_points():
    rect = Rect(10, 20, 100, 50)
    assert rect.center == Point(60, 45)
    assert rect.get_anchor(Anchor.TOP_LEFT) == Point(10, 20)

def test_immutability():
    pt = Point(1.0, 2.0)
    with pytest.raises(Exception):
        pt.x = 3.0
```

#### New Test Implementation Pattern
```python
import math
import pytest
from diagrams_as_code.geometry import CubicBezier, Point, Rect

def test_point_arithmetic_operators():
    p1 = Point(10.0, 20.0)
    p2 = Point(5.0, 10.0)
    assert p1 + p2 == Point(15.0, 30.0)
    assert p1 - p2 == Point(5.0, 10.0)
    assert p1 * 2.0 == Point(20.0, 40.0)
    assert 2.0 * p1 == Point(20.0, 40.0)
    assert p1 / 2.0 == Point(5.0, 10.0)
    assert math.isclose(p1.distance_to(p2), math.hypot(5.0, 10.0))

def test_cubic_bezier_evaluation_and_tangents():
    p0 = Point(0.0, 0.0)
    c1 = Point(0.0, 100.0)
    c2 = Point(100.0, 100.0)
    p3 = Point(100.0, 0.0)
    curve = CubicBezier(p0, c1, c2, p3)

    # Endpoints
    assert curve.point_at(0.0) == p0
    assert curve.point_at(1.0) == p3

    # Tangents at t=0 and t=1 match 3*(C1 - P0) and 3*(P3 - C2)
    v0 = curve.tangent_at(0.0)
    assert v0 == Point(0.0, 300.0)
    v1 = curve.tangent_at(1.0)
    assert v1 == Point(0.0, -300.0)

def test_cubic_bezier_bbox_vs_numerical_samples():
    curve = CubicBezier(Point(10, 20), Point(50, 180), Point(150, -50), Point(200, 100))
    bbox = curve.bbox()

    # Bbox must enclose fine-grained samples
    samples = curve.sample(1001)
    for p in samples:
        assert bbox.left - 1e-6 <= p.x <= bbox.right + 1e-6
        assert bbox.top - 1e-6 <= p.y <= bbox.bottom + 1e-6

def test_cubic_bezier_arc_length_and_midpoint():
    # Straight line cubic Bezier
    line_curve = CubicBezier(Point(0, 0), Point(25, 0), Point(75, 0), Point(100, 0))
    assert math.isclose(line_curve.arc_length(), 100.0, rel_tol=1e-3)
    mid = line_curve.arc_length_midpoint()
    assert math.isclose(mid.x, 50.0, abs_tol=1e-2)
    assert math.isclose(mid.y, 0.0, abs_tol=1e-2)
```

---

### Pattern 6: Routing & Port Normal Invariant Tests (`tests/test_routing.py`)

#### Codebase Analog
Existing Manhattan waypoint tests in [tests/test_routing.py](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L206-L245):
```python
def test_manhattan_routing_horizontal_pair_waypoints() -> None:
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 100)
    edge = Edge(s1, s2)
    router = OrthogonalRouter()
    waypoints = router.route(edge)
    assert len(waypoints) == 4
```

#### New Test Implementation Pattern
```python
from diagrams_as_code import Edge, Port, Routing, Shape
from diagrams_as_code.router import CurveRouter, EdgeRouter, OrthogonalRouter, PORT_NORMALS

def test_curve_routing_dispatch_and_4_points():
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 0)
    edge = Edge(s1, s2, routing=Routing.CURVE)

    router = CurveRouter()
    pts = router.route(edge)
    assert len(pts) == 4

    # OrthogonalRouter backward-compatible delegation
    ortho_pts = OrthogonalRouter().route(edge)
    assert ortho_pts == pts

    # EdgeRouter facade
    edge_router_pts = EdgeRouter().route(edge)
    assert edge_router_pts == pts

def test_port_normal_collinearity_all_directions():
    router = CurveRouter()
    ports = [Port.EAST, Port.WEST, Port.NORTH, Port.SOUTH]
    for sp in ports:
        for tp in ports:
            s1 = Shape("s1", "A", 100, 50).at(0, 0)
            s2 = Shape("s2", "B", 100, 50).at(300, 300)
            edge = Edge(s1, s2, source_port=sp, target_port=tp, routing=Routing.CURVE)
            p0, c1, c2, p3 = router.route(edge)

            n_src = PORT_NORMALS[sp]
            n_tgt = PORT_NORMALS[tp]

            # Vector (c1 - p0) must have 0 perpendicular component to n_src
            v_exit = c1 - p0
            assert math.isclose(v_exit.x * n_src.y - v_exit.y * n_src.x, 0.0, abs_tol=1e-5)
            # Dot product must be strictly positive (exits along outward normal)
            assert v_exit.x * n_src.x + v_exit.y * n_src.y > 0

            # Vector (p3 - c2) must point inward (opposite of n_tgt)
            v_entry = p3 - c2
            assert math.isclose(v_entry.x * n_tgt.y - v_entry.y * n_tgt.x, 0.0, abs_tol=1e-5)
            # Dot product with n_tgt must be negative (inward)
            assert v_entry.x * n_tgt.x + v_entry.y * n_tgt.y < 0

def test_handle_scaling_and_clearance_heuristics():
    router = CurveRouter()
    # Close nodes test minimum handle length >= 20px
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(105, 0)
    edge = Edge(s1, s2, source_port=Port.EAST, target_port=Port.WEST, routing=Routing.CURVE)
    p0, c1, c2, p3 = router.route(edge)
    assert p0.distance_to(c1) >= 20.0
    assert p3.distance_to(c2) >= 20.0
    assert p3.distance_to(c2) >= 1.0  # D-15 non-degenerate orientation
```

---

### Pattern 7: SVG Path & Protocol Badge Midpoint Tests (`tests/test_renderer_svg.py`)

#### Codebase Analog
Existing XML parsing and badge styling tests in [tests/test_renderer_svg.py](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py#L44-L60):
```python
def test_svg_xml_parse_validation() -> None:
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)
    # ...
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
```

#### New Test Implementation Pattern
```python
import xml.etree.ElementTree as ET
import pytest
from diagrams_as_code import Edge, Routing, Shape, SVGRenderer, get_theme
from diagrams_as_code.geometry import CubicBezier

def test_svg_render_cubic_bezier_path_and_arrowhead():
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("s1", "A", 100, 50).at(50, 50)
    s2 = Shape("s2", "B", 100, 50).at(350, 200)
    edge = Edge(s1, s2, routing=Routing.CURVE)

    svg = renderer.render(elements=[s1, s2], edges=[edge], width=600, height=400)
    root = ET.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Find path element for the edge
    paths = root.findall(".//svg:path", ns)
    edge_paths = [p for p in paths if "marker-end" in p.attrib]
    assert len(edge_paths) == 1
    d = edge_paths[0].attrib["d"]
    assert d.startswith("M ") and " C " in d
    assert " L " not in d

def test_svg_badge_arc_length_centering_on_asymmetric_curve():
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("s1", "A", 100, 50).at(50, 50)
    s2 = Shape("s2", "B", 100, 50).at(400, 300)
    edge = Edge(s1, s2, label="HTTPS/REST", routing=Routing.CURVE)

    svg = renderer.render(elements=[s1, s2], edges=[edge], width=600, height=500)
    root = ET.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Compute expected arc length midpoint
    pts = edge.waypoints
    assert pts is not None and len(pts) == 4
    curve = CubicBezier(*pts)
    expected_mid = curve.arc_length_midpoint(num_samples=32)

    # Check badge text or background rect position
    badge_rects = [r for r in root.findall(".//svg:rect", ns) if r.attrib.get("rx") == "9.0"]
    assert len(badge_rects) == 1
    rect = badge_rects[0]
    bx = float(rect.attrib["x"])
    by = float(rect.attrib["y"])
    bw = float(rect.attrib["width"])
    bh = float(rect.attrib["height"])

    badge_center_x = bx + bw / 2.0
    badge_center_y = by + bh / 2.0

    assert math.isclose(badge_center_x, expected_mid.x, abs_tol=1.0)
    assert math.isclose(badge_center_y, expected_mid.y, abs_tol=1.0)
```

---

## 4. Architectural Rules & Anti-Patterns Checklist

| Item | Architectural Rule | Failure Mode / Prohibited Anti-Pattern |
|------|--------------------|----------------------------------------|
| **1** | Layer 0 purity in `geometry.py` | Adding imports from other project modules into `geometry.py`. (Fails `test_module_boundaries.py`) |
| **2** | Storage in `Edge.waypoints` | Changing `Edge.waypoints` type from `list[Point]` to a custom object. (Breaks layout serialization) |
| **3** | Calculation vs Presentation | Computing Bezier control handles in Layer 4 (`renderer_svg.py`). Must be in Layer 3 (`router.py`). |
| **4** | Degenerate Tangent Orientation | Handle length $< 1.0\text{px}$ causing `NaN` or 0-vector arrowhead rotation in SVG engines. |
| **5** | Parameter $t=0.5$ Midpoint | Positioning label badges at $B(0.5)$ instead of arc-length parameterization $s = L / 2$. |
| **6** | Polyline Fallback | Emitting `L` commands when `e.routing == Routing.CURVE` and `len(pts) == 4`. Must emit `C`. |
| **7** | Badge Stroke Masking | Allowing edge stroke to show through or cut across protocol label text. Badge pill must be solid. |
| **8** | Public API Mirroring | Exporting classes in `diagrams_as_code` but forgetting `iiot_diagrams` or `__all__`. |
