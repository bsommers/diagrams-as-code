# Phase 9: Rounded Corner Fillets for Orthogonal Routing - Pattern Map

**Domain:** Vector Geometry, Orthogonal Fillets & Native SVG Quadratic Bezier Path Generation (Pure Python Standard Library)  
**Output Target:** `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-PATTERNS.md`

---

## 1. Target File Map

| Target File | Action | Layer & Role | Data Flow | Closest Existing Codebase Analog |
|-------------|--------|--------------|-----------|----------------------------------|
| `src/diagrams_as_code/geometry.py` | Modify | Layer 0: Primitives & Math | Leaf mathematical module; imported downward by layers 1–5; 0 internal dependencies. Implements [`QuadraticBezier`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L191-L285). | [`CubicBezier`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L191-L285), [`Point`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L8-L40), [`Rect`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L57-L159) |
| `src/diagrams_as_code/connections.py` | Modify | Layer 2: Connections & Entities | Defines [`Edge`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L62-L109). Accepts `corner_radius` and alias `arc_radius`; validates non-negative finite float; exposes property accessors. | [`Edge.__init__`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L65-L109), [`_coerce_enum`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L12-L33) |
| `src/diagrams_as_code/diagram.py` | Modify | Layer 5: Diagram & Fluent API | Container and fluent syntax builder. Cascades `corner_radius` / `arc_radius` down to [`_EdgeBuilder`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L21-L140) and [`Diagram.connect()`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L445-L474). Populates unset edge radius during `solve()`. | [`_EdgeBuilder`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L21-L140), [`Diagram.__init__`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L253-L300), [`Diagram.configure`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L301-L335) |
| `src/diagrams_as_code/renderer_svg.py` | Modify | Layer 4: Presentation & SVG Emission | Converts sharp Manhattan `edge.waypoints` into SVG paths (`M...L...Q...L...`) via `_render_filleted_path()`; enforces 50% budget, port lead-in, micro-arc suppression, obstacle clearance. | [`SVGRenderer._render_edges`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py#L591-L656), [`CubicBezier` path branching](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py#L607-L620) |
| `src/diagrams_as_code/__init__.py` | Modify | Layer 8: Public API Facade | Re-exports [`QuadraticBezier`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L191-L285) in top-level package and registers in `__all__`. | [`CubicBezier` export](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/__init__.py#L14), [`__all__` list](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/__init__.py#L61-L121) |
| `tests/test_geometry.py` | Modify | Test Suite: Layer 0 Math | Unit tests for [`QuadraticBezier`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L191-L285): Bernstein point evaluation, velocity tangents, analytical bbox vs numerical samples, arc length, immutability. | [`test_cubic_bezier_evaluation_and_tangents`](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py#L147-L189), [`test_cubic_bezier_bbox_vs_numerical_samples`](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py#L190-L221) |
| `tests/test_routing.py` | Modify | Test Suite: Layer 2 Routing & Connections | Verifies [`Edge`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L62-L109) attribute validation, alias mirroring, non-negative enforcement, and waypoint preservation contract. | [`test_edge_initialization_defaults_and_attributes`](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L62-L78), [`test_edge_type_validation`](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L107-L123) |
| `tests/test_diagram_api.py` | Modify | Test Suite: Layer 5 Diagram API | Verifies `Diagram(corner_radius=...)` cascades to orthogonal edges, individual `Edge(corner_radius=...)` overrides, and fluent `>>` operator integration. | [`test_edge_operator_combinations`](file:///home/bill/src/ai/diagrams-as-code/tests/test_diagram_api.py#L34-L86), [`test_fluent_diagram_api`](file:///home/bill/src/ai/diagrams-as-code/tests/test_diagram_api.py#L10-L33) |
| `tests/test_renderer_svg.py` | Modify | Test Suite: Layer 4 Rendering | Tests `_render_filleted_path()` SVG output: valid `Q` commands, tangent continuity, 50% segment budget clamping, port straight lead-in, threshold suppression, obstacle clearance guard, badge placement. | [`test_svg_render_cubic_bezier_path_and_arrowhead`](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py#L634-L660), [`test_svg_xml_parse_validation`](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py#L44-L60) |
| `tests/test_public_api.py` | Modify | Test Suite: API Parity | Asserts [`QuadraticBezier`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L191-L285) is exported in both `diagrams_as_code.__all__` and facade `iiot_diagrams.__all__`. | [`test_cubic_bezier_is_exported`](file:///home/bill/src/ai/diagrams-as-code/tests/test_public_api.py#L34-L38), [`test_the_facade_mirrors_the_canonical_package`](file:///home/bill/src/ai/diagrams-as-code/tests/test_public_api.py#L30-L32) |

---

## 2. Component Patterns & Analog Excerpts

### Pattern 1: Layer 0 `QuadraticBezier` Primitive (`geometry.py`)

#### Codebase Analog
Existing immutable [`CubicBezier`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L190-L283) in [src/diagrams_as_code/geometry.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L190-L283):
```python
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
        x = (
            it2 * it * self.p0.x
            + 3.0 * it2 * t * self.c1.x
            + 3.0 * it * t2 * self.c2.x
            + t2 * t * self.p3.x
        )
        y = (
            it2 * it * self.p0.y
            + 3.0 * it2 * t * self.c1.y
            + 3.0 * it * t2 * self.c2.y
            + t2 * t * self.p3.y
        )
        return Point(x, y)

    def tangent_at(self, t: float) -> Point:
        """Evaluate first derivative velocity vector B'(t)."""
        it = 1.0 - t
        c_p0 = 3.0 * it * it
        c_c1 = 6.0 * it * t
        c_c2 = 3.0 * t * t
        vx = (
            c_p0 * (self.c1.x - self.p0.x)
            + c_c1 * (self.c2.x - self.c1.x)
            + c_c2 * (self.p3.x - self.c2.x)
        )
        vy = (
            c_p0 * (self.c1.y - self.p0.y)
            + c_c1 * (self.c2.y - self.c1.y)
            + c_c2 * (self.p3.y - self.c2.y)
        )
        return Point(vx, vy)
```

#### New Implementation Pattern
```python
@dataclass(frozen=True)
class QuadraticBezier:
    """Immutable quadratic Bezier curve defined by endpoints p0, p2 and control point p1."""

    p0: Point
    p1: Point
    p2: Point

    def point_at(self, t: float) -> Point:
        """Evaluate point on quadratic Bezier curve at parameter t in [0.0, 1.0]."""
        it = 1.0 - t
        it2 = it * it
        t2 = t * t
        two_it_t = 2.0 * it * t
        x = it2 * self.p0.x + two_it_t * self.p1.x + t2 * self.p2.x
        y = it2 * self.p0.y + two_it_t * self.p1.y + t2 * self.p2.y
        return Point(x, y)

    def tangent_at(self, t: float) -> Point:
        """Evaluate first derivative velocity vector B'(t) = 2(1-t)(p1-p0) + 2t(p2-p1)."""
        it = 1.0 - t
        vx = 2.0 * it * (self.p1.x - self.p0.x) + 2.0 * t * (self.p2.x - self.p1.x)
        vy = 2.0 * it * (self.p1.y - self.p0.y) + 2.0 * t * (self.p2.y - self.p1.y)
        return Point(vx, vy)

    def sample(self, n: int = 16) -> list[Point]:
        """Uniform parameter sampling at t = i / (n - 1) for i in [0, n - 1]."""
        if n < 2:
            return [self.p0, self.p2]
        return [self.point_at(i / (n - 1)) for i in range(n)]

    def bbox(self) -> Rect:
        """Compute exact tight axis-aligned bounding box using derivative linear roots."""
        candidates = [0.0, 1.0]

        # Derivative B'_x(t) = 2(1-t)(p1.x - p0.x) + 2t(p2.x - p1.x) = 0
        # t * (p0.x - 2*p1.x + p2.x) = p0.x - p1.x
        denom_x = self.p0.x - 2.0 * self.p1.x + self.p2.x
        if abs(denom_x) > 1e-9:
            tx = (self.p0.x - self.p1.x) / denom_x
            if 0.0 < tx < 1.0:
                candidates.append(tx)

        denom_y = self.p0.y - 2.0 * self.p1.y + self.p2.y
        if abs(denom_y) > 1e-9:
            ty = (self.p0.y - self.p1.y) / denom_y
            if 0.0 < ty < 1.0:
                candidates.append(ty)

        pts = [self.point_at(t) for t in candidates]
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def arc_length(self, num_samples: int = 16) -> float:
        """Compute approximate curve arc length via piecewise chord lengths."""
        num_samples = max(1, num_samples)
        pts = self.sample(num_samples + 1)
        return sum(pts[i].distance_to(pts[i + 1]) for i in range(len(pts) - 1))
```

#### Invariants & Anti-Patterns
- **Immutable Value Object:** Must be decorated with `@dataclass(frozen=True)` (D-10). Mutations raise `FrozenInstanceError`.
- **Zero Inter-Module Imports:** `geometry.py` belongs to Layer 0. It must never import any other module from `diagrams_as_code` (verified by [`tests/test_module_boundaries.py`](file:///home/bill/src/ai/diagrams-as-code/tests/test_module_boundaries.py)).
- **Zero External Dependencies:** Use pure Python standard library (`math`, `dataclasses`). Do not import `numpy`, `scipy`, or `shapely`.
- **Exact Linear Roots for Bounding Box:** Derivative of quadratic Bezier is degree 1 (linear), so solving $B'(t) = 0$ requires simple division `(p0 - p1) / (p0 - 2*p1 + p2)` with zero iterative root finding.

---

### Pattern 2: Layer 2 `Edge` Corner Radius & Property Alias (`connections.py`)

#### Codebase Analog
Existing initialization and validation in [`Edge.__init__`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L65-L108):
```python
class Edge:
    """Connection between source and target elements with port anchors and routing style."""

    def __init__(
        self,
        source: Element,
        target: Element,
        label: str = "",
        color: Optional[str] = None,
        style: str = "solid",
        source_port: Optional[Union[Port, str]] = None,
        target_port: Optional[Union[Port, str]] = None,
        arrow_head: bool = True,
        arrow_tail: bool = False,
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        # ... validation ...
        self.metadata: dict[str, Any] = dict(metadata) if metadata else {}
        self.waypoints: Optional[list[Point]] = None
```

#### New Implementation Pattern
```python
import math

class Edge:
    """Connection between source and target elements with port anchors and routing style."""

    def __init__(
        self,
        source: Element,
        target: Element,
        label: str = "",
        color: Optional[str] = None,
        style: str = "solid",
        source_port: Optional[Union[Port, str]] = None,
        target_port: Optional[Union[Port, str]] = None,
        arrow_head: bool = True,
        arrow_tail: bool = False,
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        # ... existing source, target, port, routing coercion ...

        effective_r = corner_radius if corner_radius is not None else arc_radius
        self._corner_radius: Optional[float] = self._validate_corner_radius(effective_r)
        self.metadata: dict[str, Any] = dict(metadata) if metadata else {}
        self.waypoints: Optional[list[Point]] = None

    @staticmethod
    def _validate_corner_radius(val: Optional[Union[int, float]]) -> Optional[float]:
        """Validate that corner_radius is None or a non-negative finite float."""
        if val is None:
            return None
        try:
            r = float(val)
        except (TypeError, ValueError):
            raise ValueError(f"corner_radius must be a non-negative float, got {val!r}")
        if r < 0.0 or math.isnan(r) or math.isinf(r):
            raise ValueError(f"corner_radius must be a non-negative finite float, got {r}")
        return r

    @property
    def corner_radius(self) -> Optional[float]:
        """Fillet radius for 90-degree orthogonal corner bends, or None for diagram default/sharp."""
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, val: Optional[Union[int, float]]) -> None:
        self._corner_radius = self._validate_corner_radius(val)

    @property
    def arc_radius(self) -> Optional[float]:
        """Fully-supported backward-compatible alias for corner_radius."""
        return self.corner_radius

    @arc_radius.setter
    def arc_radius(self, val: Optional[Union[int, float]]) -> None:
        self.corner_radius = val
```

#### Invariants & Anti-Patterns
- **Strict Validation (D-04):** Non-numeric strings, negative numbers, `math.nan`, and `math.inf` must immediately raise `ValueError`. Integer inputs (e.g. `12`) are coerced cleanly to `float(12.0)`.
- **Default Sharp Semantics (D-02):** Unspecified `corner_radius=None` defaults to sharp corners unless diagram provides a cascade default. Default parameter `0.0` or `None` keeps existing 88 gallery diagrams identical.
- **Symmetric Alias Support (D-01):** `arc_radius` getter and setter must delegate directly to `corner_radius` with zero divergence.
- **Polyline Waypoint Contract (D-11):** `self.waypoints: Optional[list[Point]] = None` stores ONLY sharp Manhattan vertices. Filleting calculations never overwrite `waypoints`.

---

### Pattern 3: Layer 5 `Diagram` Cascading & Fluent Builder (`diagram.py`)

#### Codebase Analog
Existing cascading in [`Diagram.__init__`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L253-L300), [`_EdgeBuilder`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L21-L140), and [`Diagram.connect`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L445-L474):
```python
class _EdgeBuilder:
    def __init__(
        self,
        diagram: Optional[Diagram] = None,
        label: str = "",
        color: Optional[str] = None,
        style: str = "solid",
        source_port: Optional[Union[Port, str]] = None,
        target_port: Optional[Union[Port, str]] = None,
        arrow_head: bool = True,
        arrow_tail: bool = False,
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        # ...
```

#### New Implementation Pattern
```python
class _EdgeBuilder:
    def __init__(
        self,
        diagram: Optional[Diagram] = None,
        label: str = "",
        color: Optional[str] = None,
        style: str = "solid",
        source_port: Optional[Union[Port, str]] = None,
        target_port: Optional[Union[Port, str]] = None,
        arrow_head: bool = True,
        arrow_tail: bool = False,
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.diagram = diagram
        self.label = label
        self.color = color
        self.style = style
        self.source_port = source_port
        self.target_port = target_port
        self.arrow_head = arrow_head
        self.arrow_tail = arrow_tail
        self.routing = routing
        effective_r = corner_radius if corner_radius is not None else arc_radius
        self.corner_radius = Edge._validate_corner_radius(effective_r)
        self.metadata = dict(metadata) if metadata else {}
        self.source: Any = None

    def __rshift__(self, target: Any) -> Any:
        # ... resolve sources, targets, diag ...
        for s in sources:
            for t in targets:
                edge_r = self.corner_radius
                if edge_r is None and diag is not None:
                    edge_r = diag.corner_radius

                if diag is not None:
                    diag.connect(
                        source=s,
                        target=t,
                        label=self.label,
                        color=self.color,
                        style=self.style,
                        source_port=self.source_port,
                        target_port=self.target_port,
                        arrow_head=self.arrow_head,
                        arrow_tail=self.arrow_tail,
                        routing=self.routing,
                        corner_radius=edge_r,
                        metadata=self.metadata,
                    )
                else:
                    Edge(
                        source=s,
                        target=t,
                        label=self.label,
                        color=self.color,
                        style=self.style,
                        source_port=self.source_port,
                        target_port=self.target_port,
                        arrow_head=self.arrow_head,
                        arrow_tail=self.arrow_tail,
                        routing=self.routing,
                        corner_radius=edge_r,
                        metadata=self.metadata,
                    )


class Diagram:
    def __init__(
        self,
        title: str = "IIoT Architecture",
        width: float = 1200.0,
        height: float = 800.0,
        theme: Union[Theme, str] = "iiot_dark_gold",
        theme_overrides: Optional[dict[str, str]] = None,
        label_position: str = "inside",
        layout: str = "manual",
        direction: str = "LR",
        layout_file: Optional[Union[str, Path]] = None,
        rank_gap: float = 80.0,
        node_gap: float = 40.0,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        interactive: bool = False,
    ) -> None:
        # ...
        effective_r = corner_radius if corner_radius is not None else arc_radius
        self.corner_radius: Optional[float] = Edge._validate_corner_radius(effective_r)
        # ...

    @property
    def arc_radius(self) -> Optional[float]:
        return self.corner_radius

    @arc_radius.setter
    def arc_radius(self, val: Optional[Union[int, float]]) -> None:
        self.corner_radius = Edge._validate_corner_radius(val)

    def configure(
        self,
        *,
        layout: Optional[str] = None,
        direction: Optional[str] = None,
        theme: Optional[Union[Theme, str]] = None,
        layout_file: Optional[Union[str, Path]] = None,
        rank_gap: Optional[float] = None,
        node_gap: Optional[float] = None,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        interactive: Optional[bool] = None,
    ) -> Diagram:
        effective_r = corner_radius if corner_radius is not None else arc_radius
        if effective_r is not None:
            self.corner_radius = Edge._validate_corner_radius(effective_r)
        # ...
        return self

    def edge(
        self,
        label: str = "",
        color: Optional[str] = None,
        style: str = "solid",
        source_port: Optional[Union[Port, str]] = None,
        target_port: Optional[Union[Port, str]] = None,
        arrow_head: bool = True,
        arrow_tail: bool = False,
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> _EdgeBuilder:
        return _EdgeBuilder(
            diagram=self,
            label=label,
            color=color,
            style=style,
            source_port=source_port,
            target_port=target_port,
            arrow_head=arrow_head,
            arrow_tail=arrow_tail,
            routing=routing,
            corner_radius=corner_radius if corner_radius is not None else arc_radius,
            metadata=metadata,
        )

    def connect(
        self,
        source: Element,
        target: Element,
        label: str = "",
        color: Optional[str] = None,
        style: str = "solid",
        source_port: Optional[Union[Port, str]] = None,
        target_port: Optional[Union[Port, str]] = None,
        arrow_head: bool = True,
        arrow_tail: bool = False,
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Edge:
        effective_r = corner_radius if corner_radius is not None else arc_radius
        if effective_r is None:
            effective_r = self.corner_radius
        e = Edge(
            source=source,
            target=target,
            label=label,
            color=color,
            style=style,
            source_port=source_port,
            target_port=target_port,
            arrow_head=arrow_head,
            arrow_tail=arrow_tail,
            routing=routing,
            corner_radius=effective_r,
            metadata=metadata,
        )
        self.edges.append(e)
        return e

    def solve(self) -> None:
        """Place every element and propagate diagram defaults to edges."""
        if self.corner_radius is not None:
            for edge in self.edges:
                if edge.corner_radius is None:
                    edge.corner_radius = self.corner_radius
        run_layout(self)
        self._is_solved = True
```

#### Invariants & Anti-Patterns
- **Cascading Order (D-01):** Explicit `Edge.corner_radius` takes priority over `Diagram.corner_radius`. If an edge is created with `corner_radius=0.0`, it must NOT be overwritten by `diagram.corner_radius=15.0`.
- **Inheritance on `solve()`:** Edges added via `diag.add(Edge(s1, s2))` without specifying `corner_radius` receive `diag.corner_radius` during `diag.solve()`.
- **Graceful Ignore on Curve/Direct (D-03):** If `corner_radius` is set on `Routing.DIRECT` or `Routing.CURVE`, no error is raised and the value is ignored during SVG path rendering.

---

### Pattern 4: Layer 4 SVG Fillet Path Engine (`renderer_svg.py`)

#### Codebase Analog
Existing edge path generation and badge centering in [`SVGRenderer._render_edges`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py#L591-L685):
```python
        for e in edge_list:
            pts = (
                e.waypoints
                if getattr(e, "waypoints", None) is not None
                else (routes[id(e)] if routes is not None and id(e) in routes else self.router.route(e))
            )
            if len(pts) < 2:
                continue

            # Path generation branching
            if e.routing in (Routing.CURVE, "curve") and len(pts) == 4:
                p0, c1, c2, p3 = pts
                path_d = f"M {p0.x} {p0.y} C {c1.x} {c1.y}, {c2.x} {c2.y}, {p3.x} {p3.y}"
            elif e.routing in (Routing.CURVE, "curve") and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
                parts = [f"M {pts[0].x} {pts[0].y}"]
                for i in range(1, len(pts), 3):
                    parts.append(
                        f"C {pts[i].x} {pts[i].y}, {pts[i+1].x} {pts[i+1].y}, {pts[i+2].x} {pts[i+2].y}"
                    )
                path_d = " ".join(parts)
            else:
                path_d = f"M {pts[0].x} {pts[0].y} " + " ".join(
                    f"L {p.x} {p.y}" for p in pts[1:]
                )
```

#### New Implementation Pattern
```python
def _render_filleted_path(
    pts: list[Point],
    corner_radius: float,
    obstacles: Optional[Sequence[Rect]] = None,
) -> str:
    """Format orthogonal Manhattan polyline into SVG path with rounded quadratic Bezier fillets."""
    n = len(pts)
    if n < 3 or corner_radius <= 0.0:
        return f"M {pts[0].x} {pts[0].y} " + " ".join(f"L {p.x} {p.y}" for p in pts[1:])

    # 1. Precalculate segment vectors, lengths, and unit vectors
    seg_lens: list[float] = []
    seg_units: list[Point] = []
    for j in range(n - 1):
        vx = pts[j + 1].x - pts[j].x
        vy = pts[j + 1].y - pts[j].y
        l = math.hypot(vx, vy)
        seg_lens.append(l)
        seg_units.append(Point(vx / l, vy / l) if l > 1e-6 else Point(0.0, 0.0))

    # 2. Compute effective radius per corner with dynamic clamping
    effective_radii: list[float] = [0.0] * n
    for i in range(1, n - 1):
        l_in = seg_lens[i - 1]
        l_out = seg_lens[i]
        u_in = seg_units[i - 1]
        u_out = seg_units[i]

        if l_in < 1e-6 or l_out < 1e-6:
            continue

        # Strict 90-degree orthogonal turn detection (D-07)
        dot = u_in.x * u_out.x + u_in.y * u_out.y
        if abs(dot) > 1e-6:
            continue  # Collinear or turnaround: keep sharp linear

        # 50% segment budget (D-05)
        max_r_in = l_in / 2.0
        max_r_out = l_out / 2.0

        # Endpoint straight lead-in enforcement (D-08)
        if i == 1:
            lead_in = min(10.0, l_in / 2.0)
            max_r_in = min(max_r_in, max(0.0, l_in - lead_in))
        if i == n - 2:
            lead_in = min(10.0, l_out / 2.0)
            max_r_out = min(max_r_out, max(0.0, l_out - lead_in))

        r_corner = min(corner_radius, max_r_in, max_r_out)

        # Obstacle clearance guard (D-14)
        if obstacles and r_corner >= 2.0:
            p_c = pts[i]
            # Apex displacement vector: d = -0.25 * (u_in - u_out)
            dx_apex = -0.25 * (u_in.x - u_out.x)
            dy_apex = -0.25 * (u_in.y - u_out.y)
            for obs in obstacles:
                # Obstacle expanded by 4.0px minimum clearance margin
                exp = obs.expand(4.0)
                apex_x = p_c.x + r_corner * dx_apex
                apex_y = p_c.y + r_corner * dy_apex
                if exp.left < apex_x < exp.right and exp.top < apex_y < exp.bottom:
                    safe_r = r_corner
                    if abs(dx_apex) > 1e-6:
                        target_x = exp.right if dx_apex < 0 else exp.left
                        safe_r = min(safe_r, max(0.0, (target_x - p_c.x) / dx_apex))
                    if abs(dy_apex) > 1e-6:
                        target_y = exp.bottom if dy_apex < 0 else exp.top
                        safe_r = min(safe_r, max(0.0, (target_y - p_c.y) / dy_apex))
                    r_corner = min(r_corner, safe_r)

        # Minimum threshold suppression (D-06)
        if r_corner < 2.0:
            r_corner = 0.0

        effective_radii[i] = r_corner

    # 3. Assemble SVG path commands (D-09)
    parts = [f"M {pts[0].x} {pts[0].y}"]
    for i in range(1, n - 1):
        p_c = pts[i]
        r = effective_radii[i]
        if r >= 2.0:
            u_in = seg_units[i - 1]
            u_out = seg_units[i]
            t1 = Point(p_c.x - u_in.x * r, p_c.y - u_in.y * r)
            t2 = Point(p_c.x + u_out.x * r, p_c.y + u_out.y * r)
            parts.append(f"L {t1.x} {t1.y} Q {p_c.x} {p_c.y}, {t2.x} {t2.y}")
        else:
            parts.append(f"L {p_c.x} {p_c.y}")

    parts.append(f"L {pts[-1].x} {pts[-1].y}")
    return " ".join(parts)
```

And in `SVGRenderer._render_edges`:
```python
            # Path generation branching
            is_orthogonal = e.routing in (Routing.ORTHOGONAL, "orthogonal")
            corner_r = getattr(e, "corner_radius", None) or 0.0

            if e.routing in (Routing.CURVE, "curve") and len(pts) == 4:
                p0, c1, c2, p3 = pts
                path_d = f"M {p0.x} {p0.y} C {c1.x} {c1.y}, {c2.x} {c2.y}, {p3.x} {p3.y}"
            elif e.routing in (Routing.CURVE, "curve") and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
                parts = [f"M {pts[0].x} {pts[0].y}"]
                for i in range(1, len(pts), 3):
                    parts.append(
                        f"C {pts[i].x} {pts[i].y}, {pts[i+1].x} {pts[i+1].y}, {pts[i+2].x} {pts[i+2].y}"
                    )
                path_d = " ".join(parts)
            elif is_orthogonal and corner_r > 0.0:
                # Obstacle bounds collected from elements for clearance guard
                obs_bounds = [el.bounds for el in elements if el not in (e.source, e.target)]
                path_d = _render_filleted_path(pts, corner_r, obstacles=obs_bounds)
            else:
                path_d = f"M {pts[0].x} {pts[0].y} " + " ".join(
                    f"L {p.x} {p.y}" for p in pts[1:]
                )
```

And for protocol badge placement (D-12):
```python
                else:
                    # Place badge on the midpoint of the longest straight segment
                    longest_idx = 0
                    longest_len = -1.0
                    for j in range(len(pts) - 1):
                        seg_l = math.hypot(pts[j + 1].x - pts[j].x, pts[j + 1].y - pts[j].y)
                        if seg_l > longest_len:
                            longest_len = seg_l
                            longest_idx = j
                    lx = (pts[longest_idx].x + pts[longest_idx + 1].x) / 2.0
                    ly = (pts[longest_idx].y + pts[longest_idx + 1].y) / 2.0
```

#### Invariants & Anti-Patterns
- **$C^1$ Continuity (FILLET-03, D-09):** The control point $P_1$ for corner $P_c$ is always $P_c$ itself. The first derivative at $t=0$ points along $\mathbf{u}_{\text{in}}$, and at $t=1$ points along $\mathbf{u}_{\text{out}}$, giving exact tangent continuity without solving equations.
- **Budget Clamping (FILLET-02, D-05):** At most $50\%$ of segment length $L / 2$ is available to each adjacent corner. Two corners on an 18px segment clamp to $\le 9.0\text{px}$, preventing crossover loops ("dog ears").
- **Port Lead-In (D-08):** At least $\min(10.0, L/2)$ straight length is reserved at port departure and arrival, ensuring arrowhead markers seat normal to shape bounding boxes without tilt.
- **Micro-Arc Suppression (D-06):** Any corner where $R_{\text{eff}} < 2.0\text{px}$ is rendered as a clean sharp `L` command, preventing sub-pixel rasterization blur.
- **No Polyline Corruption (D-11):** `Edge.waypoints` remains unchanged. All tangent decompositions exist only within SVG path formatting.

---

### Pattern 5: Layer 8 Public API Re-exports & Facade Parity (`__init__.py`)

#### Codebase Analog
Existing export pattern in [`src/diagrams_as_code/__init__.py`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/__init__.py#L14-L71) and [`src/iiot_diagrams/__init__.py`](file:///home/bill/src/ai/diagrams-as-code/src/iiot_diagrams/__init__.py#L1-L7):
```python
# src/diagrams_as_code/__init__.py
from diagrams_as_code.geometry import Anchor, CubicBezier, Point, Rect, Size, UnitBasis

__all__ = [
    # ...
    "CubicBezier",
    # ...
]
```

#### New Implementation Pattern
```python
# src/diagrams_as_code/__init__.py
from diagrams_as_code.geometry import Anchor, CubicBezier, Point, QuadraticBezier, Rect, Size, UnitBasis

__all__ = [
    # ...
    "Point",
    "Port",
    "QuadraticBezier",
    "Rect",
    # ...
]
```
`src/iiot_diagrams/__init__.py` automatically inherits all exports via `from diagrams_as_code import *` and `__all__ = list(_dac.__all__)`.

#### Invariants & Anti-Patterns
- **Export Parity:** `diagrams_as_code.__all__` must contain `"QuadraticBezier"`. Tested by `tests/test_public_api.py`.
- **Alphabetical Sorting:** Keep `__all__` list strictly sorted alphabetically to satisfy repository hygiene.

---

## 3. Testing Patterns & Verification Harness

### Pattern 7: Layer 0 Geometric Unit Tests (`tests/test_geometry.py`)

#### Codebase Analog
Existing tests in [`tests/test_geometry.py`](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py#L147-L298):
```python
def test_cubic_bezier_evaluation_and_tangents():
    # ...
def test_cubic_bezier_bbox_vs_numerical_samples():
    # ...
def test_cubic_bezier_immutability():
    # ...
```

#### New Implementation Pattern
```python
from dataclasses import FrozenInstanceError
import math
import pytest
from diagrams_as_code.geometry import Point, QuadraticBezier, Rect

def test_quadratic_bezier_evaluation_and_tangents():
    qb = QuadraticBezier(
        p0=Point(0.0, 0.0),
        p1=Point(10.0, 0.0),
        p2=Point(10.0, 10.0),
    )
    # Endpoints
    assert qb.point_at(0.0) == Point(0.0, 0.0)
    assert qb.point_at(1.0) == Point(10.0, 10.0)

    # Parametric midpoint t = 0.5:
    # B(0.5) = 0.25 * (0,0) + 0.5 * (10,0) + 0.25 * (10,10) = (7.5, 2.5)
    mid = qb.point_at(0.5)
    assert mid.x == pytest.approx(7.5)
    assert mid.y == pytest.approx(2.5)

    # Tangents: B'(0) = 2*(p1 - p0) = 2*(10, 0) = (20, 0)
    t0 = qb.tangent_at(0.0)
    assert t0.x == pytest.approx(20.0)
    assert t0.y == pytest.approx(0.0)

    # Tangents: B'(1) = 2*(p2 - p1) = 2*(0, 10) = (0, 20)
    t1 = qb.tangent_at(1.0)
    assert t1.x == pytest.approx(0.0)
    assert t1.y == pytest.approx(20.0)

def test_quadratic_bezier_bbox_vs_numerical_samples():
    qb = QuadraticBezier(
        p0=Point(10.0, 50.0),
        p1=Point(80.0, -20.0),
        p2=Point(100.0, 50.0),
    )
    fine_samples = qb.sample(1001)
    num_min_x = min(p.x for p in fine_samples)
    num_max_x = max(p.x for p in fine_samples)
    num_min_y = min(p.y for p in fine_samples)
    num_max_y = max(p.y for p in fine_samples)

    bb = qb.bbox()
    assert bb.left <= num_min_x + 1e-4
    assert bb.right >= num_max_x - 1e-4
    assert bb.top <= num_min_y + 1e-4
    assert bb.bottom >= num_max_y - 1e-4

    assert bb.left == pytest.approx(num_min_x, abs=0.01)
    assert bb.right == pytest.approx(num_max_x, abs=0.01)
    assert bb.top == pytest.approx(num_min_y, abs=0.01)
    assert bb.bottom == pytest.approx(num_max_y, abs=0.01)

def test_quadratic_bezier_arc_length_and_immutability():
    # Straight segment: arc length equals Euclidean distance
    line = QuadraticBezier(Point(0.0, 0.0), Point(10.0, 0.0), Point(20.0, 0.0))
    assert line.arc_length() == pytest.approx(20.0, rel=1e-4)

    # Immutability
    with pytest.raises(FrozenInstanceError):
        line.p0 = Point(5.0, 5.0)  # type: ignore[misc]
```

---

### Pattern 8: Layer 2 & 5 API Validation & Cascading Tests (`tests/test_routing.py` & `tests/test_diagram_api.py`)

#### Codebase Analog
Existing edge attribute tests in [`tests/test_routing.py`](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L62-L123) and [`tests/test_diagram_api.py`](file:///home/bill/src/ai/diagrams-as-code/tests/test_diagram_api.py#L34-L86):
```python
def test_edge_initialization_defaults_and_attributes() -> None:
    # ...
def test_edge_type_validation() -> None:
    # ...
```

#### New Implementation Pattern
```python
# In tests/test_routing.py
def test_edge_corner_radius_and_arc_radius_alias():
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 0)

    # Default is None (sharp)
    e_default = Edge(s1, s2)
    assert e_default.corner_radius is None
    assert e_default.arc_radius is None

    # Explicit corner_radius
    e_cr = Edge(s1, s2, corner_radius=12.0)
    assert e_cr.corner_radius == 12.0
    assert e_cr.arc_radius == 12.0

    # arc_radius alias parameter
    e_alias = Edge(s1, s2, arc_radius=8.5)
    assert e_alias.corner_radius == 8.5
    assert e_alias.arc_radius == 8.5

    # Setter synchronization
    e_cr.arc_radius = 16.0
    assert e_cr.corner_radius == 16.0
    e_cr.corner_radius = 20.0
    assert e_cr.arc_radius == 20.0

def test_edge_corner_radius_validation():
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 0)

    with pytest.raises(ValueError, match="corner_radius must be a non-negative"):
        Edge(s1, s2, corner_radius=-5.0)

    with pytest.raises(ValueError, match="corner_radius must be a non-negative"):
        Edge(s1, s2, corner_radius="invalid")

    with pytest.raises(ValueError, match="corner_radius must be a non-negative finite"):
        Edge(s1, s2, corner_radius=float("nan"))

    # Integer coercion
    e = Edge(s1, s2, corner_radius=15)
    assert e.corner_radius == 15.0
    assert isinstance(e.corner_radius, float)

# In tests/test_diagram_api.py
def test_diagram_corner_radius_cascade_and_override():
    with Diagram("Cascade Test", corner_radius=15.0) as diag:
        s1 = diag.shape("S1").at(0, 0)
        s2 = diag.shape("S2").at(200, 100)
        s3 = diag.shape("S3").at(400, 200)

        # Inherits diagram cascade default
        s1 >> s2
        # Explicit override
        s2 >> diag.edge("Sharp", corner_radius=0.0) >> s3

    diag.solve()
    assert diag.edges[0].corner_radius == 15.0
    assert diag.edges[1].corner_radius == 0.0
```

---

### Pattern 9: Layer 4 SVG Fillet Rendering Tests (`tests/test_renderer_svg.py`)

#### Codebase Analog
Existing curve rendering tests in [`tests/test_renderer_svg.py`](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py#L634-L755):
```python
def test_svg_render_cubic_bezier_path_and_arrowhead() -> None:
    # ...
def test_svg_multi_segment_bezier_path_rendering() -> None:
    # ...
```

#### New Implementation Pattern
```python
import xml.etree.ElementTree as ET
import pytest
from diagrams_as_code.connections import Edge, Routing
from diagrams_as_code.elements import Shape
from diagrams_as_code.geometry import Point, Rect
from diagrams_as_code.renderer_svg import SVGRenderer, _render_filleted_path
from diagrams_as_code.theme import get_theme

def test_orthogonal_fillet_svg_path_and_q_commands():
    pts = [
        Point(0.0, 50.0),
        Point(100.0, 50.0),
        Point(100.0, 150.0),
        Point(200.0, 150.0),
    ]
    path_d = _render_filleted_path(pts, corner_radius=20.0)

    assert path_d.startswith("M 0.0 50.0")
    # Corner 1 at (100, 50): T1=(80, 50), Q (100, 50), T2=(100, 70)
    assert "L 80.0 50.0 Q 100.0 50.0, 100.0 70.0" in path_d
    # Corner 2 at (100, 150): T1=(100, 130), Q (100, 150), T2=(120, 150)
    assert "L 100.0 130.0 Q 100.0 150.0, 120.0 150.0" in path_d
    assert path_d.endswith("L 200.0 150.0")

def test_orthogonal_fillet_short_segment_budget_clamping():
    # Segment between (100, 50) and (100, 68) is 18px long.
    # corners each request 15px radius; 50% budget clamps each to 9px (18 / 2 = 9).
    pts = [
        Point(0.0, 50.0),
        Point(100.0, 50.0),
        Point(100.0, 68.0),
        Point(200.0, 68.0),
    ]
    path_d = _render_filleted_path(pts, corner_radius=15.0)

    # First corner outgoing clamped to 9.0: T2 = (100.0, 50.0 + 9.0) = (100.0, 59.0)
    assert "Q 100.0 50.0, 100.0 59.0" in path_d
    # Second corner incoming clamped to 9.0: T1 = (100.0, 68.0 - 9.0) = (100.0, 59.0)
    assert "L 100.0 59.0 Q 100.0 68.0" in path_d

def test_orthogonal_fillet_threshold_suppression():
    # 3px segment gives max radius 1.5px < 2.0px threshold; suppresses to sharp corner
    pts = [
        Point(0.0, 50.0),
        Point(100.0, 50.0),
        Point(100.0, 53.0),
        Point(200.0, 53.0),
    ]
    path_d = _render_filleted_path(pts, corner_radius=10.0)

    # No Q commands should be emitted; stays sharp L commands
    assert "Q" not in path_d
    assert "L 100.0 50.0 L 100.0 53.0" in path_d

def test_orthogonal_fillet_port_straight_lead_in():
    # First segment is 16px long. Port lead-in enforces min(10.0, 16/2) = 8px.
    # Available radius is min(8, 16 - 8) = 8.0px.
    pts = [
        Point(0.0, 50.0),
        Point(16.0, 50.0),
        Point(16.0, 100.0),
    ]
    path_d = _render_filleted_path(pts, corner_radius=20.0)
    # Incoming tangent must not exceed (16.0 - 8.0) = 8.0
    assert "L 8.0 50.0 Q 16.0 50.0" in path_d

def test_orthogonal_fillet_obstacle_clearance_guard():
    # Corner at (100, 100) turning from EAST to SOUTH (inside corner is bottom-right or top-left)
    # Obstacle located close to inside apex:
    pts = [
        Point(50.0, 100.0),
        Point(100.0, 100.0),
        Point(100.0, 150.0),
    ]
    # Inside corner apex is toward (100 - 0.25*R, 100 + 0.25*R)
    # Place obstacle at (90, 102, 20, 20)
    obs = Rect(90.0, 102.0, 20.0, 20.0)
    path_d = _render_filleted_path(pts, corner_radius=20.0, obstacles=[obs])
    # Effective radius is clamped so apex does not penetrate obs.expand(4.0)
    assert "Q 100.0 100.0" in path_d
```

---

## 4. Phase Execution Plan Guidance

Downstream planning agents should structure Phase 9 execution into three focused plans:

### Plan 09-01: Layer 0 Primitives & Layer 2/5 API Contracts
1. Implement [`QuadraticBezier`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L191-L285) in `src/diagrams_as_code/geometry.py`:
   - `@dataclass(frozen=True)` with `p0: Point`, `p1: Point`, `p2: Point`.
   - Methods: `point_at(t)`, `tangent_at(t)`, `bbox()`, `sample(n)`, `arc_length(num_samples)`.
2. Re-export `QuadraticBezier` in `src/diagrams_as_code/__init__.py` and include in `__all__`.
3. Add `corner_radius` and alias `arc_radius` to `Edge` in `src/diagrams_as_code/connections.py` with static validation `_validate_corner_radius`.
4. Update `Diagram` and `_EdgeBuilder` in `src/diagrams_as_code/diagram.py`:
   - Accept `corner_radius` and `arc_radius` in `__init__`, `configure()`, `edge()`, and `connect()`.
   - Propagate cascade defaults in `solve()`.
5. Add test coverage:
   - `tests/test_geometry.py`: unit tests for `QuadraticBezier`.
   - `tests/test_public_api.py`: export reachable in both namespaces.
   - `tests/test_routing.py` & `tests/test_diagram_api.py`: parameter validation, alias property, and diagram cascading.

### Plan 09-02: Layer 4 SVG Fillet Path Engine
1. Implement `_render_filleted_path(pts, corner_radius, obstacles=None)` in `src/diagrams_as_code/renderer_svg.py`:
   - Dynamic 50% segment budget clamping: $R_{\text{eff}} \le \min(R, L_{\text{in}}/2, L_{\text{out}}/2)$.
   - Port straight lead-in: $\ge \min(10.0, L/2)$.
   - Micro-arc suppression: $< 2.0\text{px} \implies 0.0$ (sharp `L` command).
   - Strict 90° orthogonal turn detection: $|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$.
   - Obstacle clearance guard: inside apex clearance $\ge 4.0\text{px}$.
   - SVG quadratic Bezier path assembly: `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y`.
2. Connect `_render_filleted_path` into `SVGRenderer._render_edges` when `is_orthogonal and corner_radius > 0.0`.
3. Center protocol badges on the midpoint of the longest straight segment for filleted edges.
4. Add comprehensive rendering tests in `tests/test_renderer_svg.py`:
   - Path command syntax validation (`M...L...Q...L...`).
   - Clamping verification on short segments.
   - Threshold suppression verification.
   - Port straight lead-in verification.
   - Obstacle clearance guard verification.
   - Badge placement verification.

### Plan 09-03: End-to-End Integration, Diagram Cascading & Visual Regression
1. Verify end-to-end diagram rendering with `Diagram(corner_radius=15.0)` across multiple shapes and groups.
2. Verify obstacle avoidance detour paths receive uniform corner filleting.
3. Verify backward compatibility: run full pytest suite (`uv run pytest`) across all 473+ tests to ensure zero regressions on existing diagrams.
4. Verify headless SVG rasterization with `resvg-py` to ensure valid W3C quadratic Bezier rendering.
