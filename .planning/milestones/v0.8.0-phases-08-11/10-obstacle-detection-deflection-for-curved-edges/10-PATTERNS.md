# Phase 10: Obstacle Detection & Deflection for Curved Edges - Pattern Map

**Domain:** Vector Geometry, Collision Detection, Cubic Bezier Splines & Edge Routing Engine (Pure Python Standard Library)  
**Output Target:** `.planning/phases/10-obstacle-detection-deflection-for-curved-edges/10-PATTERNS.md`

---

## 1. Target File Map

| Target File | Action | Layer & Role | Data Flow | Closest Existing Codebase Analog |
|-------------|--------|--------------|-----------|----------------------------------|
| `src/diagrams_as_code/geometry.py` | Modify | Layer 0: Primitives & Math | Leaf mathematical module; imported downward by layers 1–5; 0 internal dependencies. Implements [`CubicBezier.split()`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L191-L304) and [`CubicBezier.intersects_rect()`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L191-L304). | [`CubicBezier.bbox()`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L240-L276), [`Rect.intersects()`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L128-L135), [`Point`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L8-L40) |
| `src/diagrams_as_code/connections.py` | Modify | Layer 2: Connections & Entities | Defines [`Edge`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L63-L154). Holds routing metadata: `clearance` (default 15.0px per D-02), property accessors, and non-negative finite float validation. | [`Edge.corner_radius`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L116-L145), [`Edge._validate_corner_radius`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L116-L136) |
| `src/diagrams_as_code/router.py` | Modify | Layer 3: Routing Engine | Contains [`CurveRouter`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L59-L137), [`OrthogonalRouter`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L139-L402), and [`EdgeRouter`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L404-L427). Implements obstacle normalization, 2-tier collision testing (AABB + De Casteljau), dual bypass corridor evaluation, $C^1$ multi-segment spline synthesis (7 or 10 waypoints), and reverse-flow escape routing. | [`OrthogonalRouter._normalize_obstacles`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L229-L251), [`OrthogonalRouter._find_detour_path`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L253-L380), [`CurveRouter.route`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L80-L136) |
| `src/diagrams_as_code/renderer_svg.py` | Modify | Layer 4: Presentation & SVG Emission | Emits chained `M... C... C...` path commands for $3N+1$ curve waypoints. Updates protocol badge placement to locate physical arc-length midpoint of the longest spline segment (D-12). | [`SVGRenderer._render_edges`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py#L692-L824), [`_render_filleted_path` badge midpoint](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py#L784-L797) |
| `src/diagrams_as_code/diagram.py` | Modify | Layer 5: Diagram & Fluent API | Context manager and container. Forwards optional `clearance` parameter through `_EdgeBuilder` and `Diagram.connect` to `Edge`. | [`Diagram.connect`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L503-L538), [`_EdgeBuilder.__init__`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py#L21-L45) |
| `tests/test_geometry.py` | Modify | Test Suite: Layer 0 Math | Unit tests for De Casteljau curve bisection `CubicBezier.split()` and two-tier collision detector `CubicBezier.intersects_rect()`. | [`test_cubic_bezier_evaluation_and_tangents`](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py#L147-L189), [`test_cubic_bezier_bbox_vs_numerical_samples`](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py#L190-L221) |
| `tests/test_routing.py` | Modify | Test Suite: Layer 3 Routing Engine | Unit and integration tests for `CurveRouter`: obstacle exclusion, compact vs wide obstacle deflection, tangent alignment, secondary obstacle bypass, reverse-flow port resolution and escape corridor. | [`test_curve_routing_edge_dispatch`](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L443-L474), [`test_curve_router_port_tangent_alignment`](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L475-L518), [`test_obstacle_avoidance_horizontal`](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L362-L389) |
| `tests/test_renderer_svg.py` | Modify | Test Suite: Layer 4 Rendering | Tests protocol badge centering on the longest spline segment for multi-segment deflected curves (D-12). | [`test_svg_multi_segment_bezier_path_rendering`](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py#L717-L753), [`test_orthogonal_fillet_badge_placement`](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py#L882-L947) |

---

## 2. Component Patterns & Analog Excerpts

### Pattern 1: Layer 0 `CubicBezier.split` and `CubicBezier.intersects_rect` (`geometry.py`)

#### Codebase Analog
Existing analytical bounding box and sampling methods in [`CubicBezier`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py#L190-L304):
```python
@dataclass(frozen=True)
class CubicBezier:
    p0: Point
    c1: Point
    c2: Point
    p3: Point

    def bbox(self) -> Rect:
        """Compute exact tight axis-aligned bounding box using derivative roots."""
        # Solves quadratic derivative roots in [0, 1]...
        pts = [self.point_at(t) for t in candidates]
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)
```

#### New Implementation Pattern
```python
@dataclass(frozen=True)
class CubicBezier:
    p0: Point
    c1: Point
    c2: Point
    p3: Point

    def split(self, t: float = 0.5) -> tuple[CubicBezier, CubicBezier]:
        """Bisect cubic Bezier curve into two sub-curves using De Casteljau algorithm."""
        it = 1.0 - t
        # Level 1
        q0 = Point(it * self.p0.x + t * self.c1.x, it * self.p0.y + t * self.c1.y)
        q1 = Point(it * self.c1.x + t * self.c2.x, it * self.c1.y + t * self.c2.y)
        q2 = Point(it * self.c2.x + t * self.p3.x, it * self.c2.y + t * self.p3.y)
        # Level 2
        r0 = Point(it * q0.x + t * q1.x, it * q0.y + t * q1.y)
        r1 = Point(it * q1.x + t * q2.x, it * q1.y + t * q2.y)
        # Level 3
        s0 = Point(it * r0.x + t * r1.x, it * r0.y + t * r1.y)
        return (
            CubicBezier(self.p0, q0, r0, s0),
            CubicBezier(s0, r1, q2, self.p3),
        )

    def intersects_rect(self, rect: Rect, max_depth: int = 4) -> bool:
        """Two-tier collision test: AABB broadphase filter followed by De Casteljau narrowphase.
        
        Tier 1: Fast O(1) broadphase filter using analytical tight bounding box.
        Tier 2: Narrowphase recursive bisection down to max_depth (depth 4 = 16 sub-curves,
        approximating the continuous curve within < 0.8px). Early exits on first hit.
        """
        # Tier 1: Broadphase filter (D-01)
        if not self.bbox().intersects(rect):
            return False

        # Tier 2: Recursive De Casteljau narrowphase (D-01, D-04)
        def _check_subcurve(curve: CubicBezier, depth: int) -> bool:
            min_x = min(curve.p0.x, curve.c1.x, curve.c2.x, curve.p3.x)
            max_x = max(curve.p0.x, curve.c1.x, curve.c2.x, curve.p3.x)
            min_y = min(curve.p0.y, curve.c1.y, curve.c2.y, curve.p3.y)
            max_y = max(curve.p0.y, curve.c1.y, curve.c2.y, curve.p3.y)
            # AABB intersection check
            if not (min_x < rect.right and max_x > rect.left and min_y < rect.bottom and max_y > rect.top):
                return False
            if depth >= max_depth:
                return True
            left, right = curve.split(0.5)
            return _check_subcurve(left, depth + 1) or _check_subcurve(right, depth + 1)

        return _check_subcurve(self, 0)
```

#### Invariants & Anti-Patterns
- **Pure Python IEEE 754 Math:** Do not use `numpy`, `scipy`, or `shapely`. All math consists of additions, multiplications, and min/max tests.
- **Early-Exit Optimization (D-04):** The recursion immediately returns `True` upon discovering the first sub-segment intersection, avoiding unnecessary branch exploration.
- **Layer 0 Isolation:** `geometry.py` must never import from higher layers (verified by `tests/test_module_boundaries.py`).

---

### Pattern 2: Layer 2 `Edge.clearance` Attribute & Validation (`connections.py`)

#### Codebase Analog
Existing validation and property setters in [`Edge`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py#L116-L154):
```python
    @staticmethod
    def _validate_corner_radius(val: Optional[Union[int, float]]) -> Optional[float]:
        """Validate and coerce corner radius to non-negative finite float."""
        if val is None:
            return None
        if isinstance(val, (bool, str)):
            raise ValueError(
                f"corner_radius must be a non-negative finite float, got {val!r}"
            )
        try:
            r = float(val)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"corner_radius must be a non-negative finite float, got {val!r}"
            ) from exc
        if r < 0.0 or math.isnan(r) or math.isinf(r):
            raise ValueError(
                f"corner_radius must be a non-negative finite float, got {r}"
            )
        return r
```

#### New Implementation Pattern
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
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        clearance: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        # ... existing initializers ...
        self._clearance: float = self._validate_clearance(clearance if clearance is not None else 15.0)

    @staticmethod
    def _validate_clearance(val: Optional[Union[int, float]]) -> float:
        """Validate and coerce clearance buffer to positive finite float."""
        if val is None:
            return 15.0
        if isinstance(val, (bool, str)):
            raise ValueError(f"clearance must be a non-negative finite float, got {val!r}")
        try:
            c = float(val)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"clearance must be a non-negative finite float, got {val!r}") from exc
        if c < 0.0 or math.isnan(c) or math.isinf(c):
            raise ValueError(f"clearance must be a non-negative finite float, got {c}")
        return c

    @property
    def clearance(self) -> float:
        """Obstacle clearance inflation margin in pixels (default 15.0px)."""
        return self._clearance

    @clearance.setter
    def clearance(self, val: Union[int, float]) -> None:
        self._clearance = self._validate_clearance(val)
```

---

### Pattern 3: Layer 3 `CurveRouter` Obstacle Normalization & Collision Detection (`router.py`)

#### Codebase Analog
Existing obstacle normalization in [`OrthogonalRouter._normalize_obstacles`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L229-L251):
```python
    def _normalize_obstacles(
        self, edge: Edge, obstacles: Iterable[Any], p_start: Point, p_end: Point
    ) -> list[Rect]:
        norm: list[Rect] = []
        for item in obstacles:
            if item is edge.source or item is edge.target:
                continue
            if hasattr(item, "id") and item.id in (edge.source.id, edge.target.id):
                continue
            if hasattr(item, "bounds") and isinstance(item.bounds, Rect):
                r = item.bounds
            elif isinstance(item, Rect):
                r = item
            else:
                continue

            # Skip if start or end point is inside the obstacle (e.g. enclosing group)
            if (r.left <= p_start.x <= r.right and r.top <= p_start.y <= r.bottom) or (
                r.left <= p_end.x <= r.right and r.top <= p_end.y <= r.bottom
            ):
                continue
            norm.append(r)
        return norm
```

#### New Implementation Pattern
```python
class CurveRouter:
    """Computes cubic Bezier control handles from port normal vectors with obstacle avoidance."""

    def _normalize_obstacles(
        self, edge: Edge, obstacles: Iterable[Any], p_start: Point, p_end: Point
    ) -> list[Rect]:
        """Normalize obstacle bounding boxes excluding source, target, and enclosing groups (D-03)."""
        norm: list[Rect] = []
        for item in obstacles:
            if item is edge.source or item is edge.target:
                continue
            if hasattr(item, "id") and item.id in (edge.source.id, edge.target.id):
                continue
            if hasattr(item, "bounds") and isinstance(item.bounds, Rect):
                r = item.bounds
            elif isinstance(item, Rect):
                r = item
            else:
                continue

            # Skip if start or end point is inside the obstacle (e.g. enclosing container group)
            if (r.left <= p_start.x <= r.right and r.top <= p_start.y <= r.bottom) or (
                r.left <= p_end.x <= r.right and r.top <= p_end.y <= r.bottom
            ):
                continue
            norm.append(r)
        return norm

    def _detect_collisions(
        self, curve: CubicBezier, obstacles: list[Rect], clearance: float
    ) -> list[Rect]:
        """Return list of obstacles whose clearance-inflated box collides with the candidate curve (D-01, D-02)."""
        hits: list[Rect] = []
        for obs in obstacles:
            exp_obs = obs.expand(clearance)
            if curve.intersects_rect(exp_obs):
                hits.append(obs)
        return hits
```

---

### Pattern 4: Layer 3 `CurveRouter` Multi-Segment Spline Deflection (`router.py`)

#### Codebase Analog
Existing handle calculation in [`CurveRouter.route`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L80-L136):
```python
        c1 = Point(p_start.x + n_src.x * d1, p_start.y + n_src.y * d1)
        c2 = Point(p_end.x + n_tgt.x * d2, p_end.y + n_tgt.y * d2)
        return [p_start, c1, c2, p_end]
```

#### New Implementation Pattern
```python
    def _build_deflected_spline_horizontal(
        self,
        p0: Point,
        p3: Point,
        n_src: Point,
        n_tgt: Point,
        obs_block: Rect,
        y_corridor: float,
        clearance: float = 15.0,
    ) -> list[Point]:
        """Construct 3N+1 control polygon with strict C1 continuity around horizontal obstacle block."""
        w_obs = obs_block.width
        tangent = Point(1.0, 0.0)  # Parallel to cleared boundary edge (D-08)

        if w_obs <= 2.0 * clearance:
            # Compact obstacle: single apex waypoint (D-07)
            w = Point(obs_block.center.x, y_corridor)
            l1 = p0.distance_to(w)
            l2 = w.distance_to(p3)
            h0 = max(20.0, min(0.35 * l1, 0.5 * abs(w.x - p0.x)))
            h1a = max(20.0, min(0.35 * l1, 0.5 * abs(w.x - p0.x)))
            h1b = max(20.0, min(0.35 * l2, 0.5 * abs(p3.x - w.x)))
            h2 = max(20.0, min(0.35 * l2, 0.5 * abs(p3.x - w.x)))

            c0a = Point(p0.x + n_src.x * h0, p0.y + n_src.y * h0)
            c0b = Point(w.x - tangent.x * h1a, w.y - tangent.y * h1a)
            c1a = Point(w.x + tangent.x * h1b, w.y + tangent.y * h1b)
            c1b = Point(p3.x + n_tgt.x * h2, p3.y + n_tgt.y * h2)
            return [p0, c0a, c0b, w, c1a, c1b, p3]

        # Wide obstacle: 2 corner clearance waypoints (D-07, D-11)
        w1_x = max(p0.x + 10.0, obs_block.left - clearance)
        w2_x = min(p3.x - 10.0, obs_block.right + clearance)
        w1 = Point(w1_x, y_corridor)
        w2 = Point(w2_x, y_corridor)

        l1 = p0.distance_to(w1)
        l_mid = w2.x - w1.x
        l3 = w2.distance_to(p3)

        h0 = max(20.0, min(0.35 * l1, 0.5 * abs(w1.x - p0.x)))
        h1_in = max(20.0, min(0.35 * l1, 0.5 * abs(w1.x - p0.x)))
        h_mid = l_mid / 3.0
        h2_out = max(20.0, min(0.35 * l3, 0.5 * abs(p3.x - w2.x)))
        h3 = max(20.0, min(0.35 * l3, 0.5 * abs(p3.x - w2.x)))

        c0a = Point(p0.x + n_src.x * h0, p0.y + n_src.y * h0)
        c0b = Point(w1.x - tangent.x * h1_in, w1.y - tangent.y * h1_in)

        c1a = Point(w1.x + tangent.x * h_mid, w1.y)
        c1b = Point(w2.x - tangent.x * h_mid, w2.y)

        c2a = Point(w2.x + tangent.x * h2_out, w2.y + tangent.y * h2_out)
        c2b = Point(p3.x + n_tgt.x * h3, p3.y + n_tgt.y * h3)

        return [p0, c0a, c0b, w1, c1a, c1b, w2, c2a, c2b, p3]

    def _select_deflected_corridor(
        self,
        p0: Point,
        p3: Point,
        n_src: Point,
        n_tgt: Point,
        colliding: list[Rect],
        all_obstacles: list[Rect],
        clearance: float,
    ) -> list[Point]:
        """Evaluate dual bypass corridors and select minimal deviation collision-free spline (D-09, D-10)."""
        # Block bounding box
        block = colliding[0]
        for obs in colliding[1:]:
            block = block.union(obs)

        # Candidate corridors: TOP and BOTTOM
        y_top = block.top - clearance
        y_bot = block.bottom + clearance

        cand_top = self._build_deflected_spline_horizontal(p0, p3, n_src, n_tgt, block, y_top, clearance)
        cand_bot = self._build_deflected_spline_horizontal(p0, p3, n_src, n_tgt, block, y_bot, clearance)

        def _spline_has_collision(pts: list[Point]) -> bool:
            num_segs = (len(pts) - 1) // 3
            for s in range(num_segs):
                idx = s * 3
                seg = CubicBezier(pts[idx], pts[idx + 1], pts[idx + 2], pts[idx + 3])
                for obs in all_obstacles:
                    if seg.intersects_rect(obs.expand(clearance)):
                        return True
            return False

        def _spline_len(pts: list[Point]) -> float:
            num_segs = (len(pts) - 1) // 3
            total = 0.0
            for s in range(num_segs):
                idx = s * 3
                seg = CubicBezier(pts[idx], pts[idx + 1], pts[idx + 2], pts[idx + 3])
                total += seg.arc_length(num_samples=16)
            return total

        top_collides = _spline_has_collision(cand_top)
        bot_collides = _spline_has_collision(cand_bot)

        if not top_collides and bot_collides:
            return cand_top
        if not bot_collides and top_collides:
            return cand_bot
        if not top_collides and not bot_collides:
            # Minimal deviation heuristic (D-09)
            return cand_top if _spline_len(cand_top) <= _spline_len(cand_bot) else cand_bot

        # Both collide with secondary obstacles: outer clearance expansion (D-10)
        # Push top corridor higher past secondary obstacles
        min_y = min(obs.top for obs in all_obstacles) - clearance
        return self._build_deflected_spline_horizontal(p0, p3, n_src, n_tgt, block, min_y, clearance)
```

---

### Pattern 5: Layer 3 `CurveRouter` Reverse-Flow Escape Routing (`router.py`)

#### Codebase Analog
Existing backward flow handle scaling in [`CurveRouter.route`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L124-L128):
```python
            if axis_delta > 0:
                # Forward flow (D-01, D-02, D-03)
                d = max(0.5 * axis_delta, 0.25 * lat_delta, 20.0)
                d1 = d2 = d
            else:
                # Backward flow (D-07)
                d = max(0.25 * lat_delta, 30.0)
                d1 = d2 = d
```

#### New Implementation Pattern
```python
    def resolve_ports(self, edge: Edge) -> tuple[Port, Port]:
        """Determine connection ports for source and target elements, resolving lateral ports for back-edges (D-14)."""
        if edge.source_port and edge.target_port:
            return (edge.source_port, edge.target_port)

        sb, tb = edge.source.bounds, edge.target.bounds
        dx = tb.center.x - sb.center.x
        dy = tb.center.y - sb.center.y

        if abs(dx) >= abs(dy):
            if dx < 0 and edge.source_port is None and edge.target_port is None:
                # Reverse-flow horizontal: resolve to outward lateral cardinal ports (NORTH/NORTH) (D-14)
                return (Port.NORTH, Port.NORTH)
            src_p = Port.EAST if dx > 0 else Port.WEST
            tgt_p = Port.WEST if dx > 0 else Port.EAST
        else:
            if dy < 0 and edge.source_port is None and edge.target_port is None:
                # Reverse-flow vertical: resolve to outward lateral cardinal ports (EAST/EAST) (D-14)
                return (Port.EAST, Port.EAST)
            src_p = Port.SOUTH if dy > 0 else Port.NORTH
            tgt_p = Port.NORTH if dy > 0 else Port.SOUTH

        return (edge.source_port or src_p, edge.target_port or tgt_p)

    def _route_reverse_flow_explicit_ports(
        self,
        p_start: Point,
        p_end: Point,
        src_port: Port,
        tgt_port: Port,
        sb: Rect,
        tb: Rect,
        obstacles: list[Rect],
        clearance: float,
    ) -> list[Point]:
        """Route reverse-flow connection with explicit facing ports via lateral escape corridor (D-13, D-15)."""
        margin = max(clearance, 30.0)
        # Determine escape corridor above or below both nodes
        min_top = min(sb.top, tb.top, *(obs.top for obs in obstacles)) if obstacles else min(sb.top, tb.top)
        y_corridor = min_top - margin

        # Escape waypoints projected laterally beyond shape boundaries
        w_esc1 = Point(sb.right + margin if src_port == Port.EAST else sb.left - margin, y_corridor)
        w_esc2 = Point(tb.right + margin if tgt_port == Port.EAST else tb.left - margin, y_corridor)

        # Build 3-segment spline
        return self._build_deflected_spline_horizontal(
            p_start, p_end, PORT_NORMALS[src_port], PORT_NORMALS[tgt_port],
            Rect(w_esc2.x, y_corridor, abs(w_esc1.x - w_esc2.x), 1.0),
            y_corridor,
            clearance=clearance,
        )
```

---

### Pattern 6: Layer 4 `SVGRenderer` Longest Segment Arc-Length Midpoint Badge Placement (`renderer_svg.py`)

#### Codebase Analog
Existing badge positioning in [`SVGRenderer._render_edges`](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py#L765-L784):
```python
            if e.label:
                is_curve = e.routing in (Routing.CURVE, "curve")
                if is_curve and len(pts) == 4:
                    curve = CubicBezier(pts[0], pts[1], pts[2], pts[3])
                    mid = curve.arc_length_midpoint(num_samples=32)
                    lx, ly = mid.x, mid.y
                elif is_curve and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
                    # Multi-segment fallback: take arc-length midpoint of middle segment or first segment
                    num_segs = (len(pts) - 1) // 3
                    seg_idx = num_segs // 2
                    seg_start = seg_idx * 3
                    curve = CubicBezier(
                        pts[seg_start],
                        pts[seg_start + 1],
                        pts[seg_start + 2],
                        pts[seg_start + 3],
                    )
                    mid = curve.arc_length_midpoint(num_samples=32)
                    lx, ly = mid.x, mid.y
```

#### New Implementation Pattern (D-12)
```python
                elif is_curve and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
                    # Multi-segment spline: position badge on the longest physical segment (D-12)
                    num_segs = (len(pts) - 1) // 3
                    longest_curve: Optional[CubicBezier] = None
                    max_seg_len = -1.0
                    for k in range(num_segs):
                        seg_start = k * 3
                        curve = CubicBezier(
                            pts[seg_start],
                            pts[seg_start + 1],
                            pts[seg_start + 2],
                            pts[seg_start + 3],
                        )
                        l = curve.arc_length(num_samples=16)
                        if l > max_seg_len:
                            max_seg_len = l
                            longest_curve = curve

                    assert longest_curve is not None
                    mid = longest_curve.arc_length_midpoint(num_samples=32)
                    lx, ly = mid.x, mid.y
```

---

## 3. Testing Patterns & Verification Harness

### Pattern 7: Layer 0 Geometric Collision Tests (`tests/test_geometry.py`)

#### Codebase Analog
Existing tests in [`tests/test_geometry.py`](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py#L147-L298):
```python
def test_cubic_bezier_bbox_vs_numerical_samples():
    cb = CubicBezier(
        p0=Point(10.0, 50.0),
        c1=Point(100.0, 200.0),
        c2=Point(50.0, -100.0),
        p3=Point(200.0, 50.0),
    )
    # ...
```

#### New Implementation Pattern
```python
def test_cubic_bezier_split_midpoint():
    """Verify De Casteljau split at t=0.5 yields continuous matching halves."""
    cb = CubicBezier(Point(0.0, 0.0), Point(10.0, 30.0), Point(40.0, 30.0), Point(50.0, 0.0))
    left, right = cb.split(0.5)

    # Split midpoint must equal parent curve at t=0.5
    mid = cb.point_at(0.5)
    assert left.p3 == mid
    assert right.p0 == mid

    # Parameter matching: left sub-curve at t=1.0 is mid, left at t=0.5 is cb.point_at(0.25)
    assert left.point_at(0.5).x == pytest.approx(cb.point_at(0.25).x, abs=1e-5)
    assert left.point_at(0.5).y == pytest.approx(cb.point_at(0.25).y, abs=1e-5)
    assert right.point_at(0.5).x == pytest.approx(cb.point_at(0.75).x, abs=1e-5)
    assert right.point_at(0.5).y == pytest.approx(cb.point_at(0.75).y, abs=1e-5)

def test_cubic_bezier_intersects_rect_clear_miss():
    """Verify O(1) broadphase rejection on non-overlapping rectangles."""
    cb = CubicBezier(Point(0.0, 0.0), Point(50.0, 0.0), Point(100.0, 0.0), Point(150.0, 0.0))
    rect = Rect(50.0, 50.0, 50.0, 50.0)  # y in [50, 100], curve is at y=0
    assert not cb.intersects_rect(rect)

def test_cubic_bezier_intersects_rect_direct_hit():
    """Verify narrowphase collision detection when curve passes through rectangle."""
    cb = CubicBezier(Point(0.0, 50.0), Point(100.0, 50.0), Point(100.0, 50.0), Point(200.0, 50.0))
    rect = Rect(80.0, 30.0, 40.0, 40.0)
    assert cb.intersects_rect(rect)

def test_cubic_bezier_intersects_rect_grazing_corner_miss():
    """Verify narrowphase avoids convex hull false positive when curve grazes corner by 5px."""
    # Control polygon bow creates large convex hull that overlaps rect, but curve itself misses
    cb = CubicBezier(Point(0.0, 0.0), Point(100.0, 100.0), Point(100.0, 100.0), Point(200.0, 0.0))
    # True apex at t=0.5: y = 0.375 * 100 + 0.375 * 100 = 75.0
    # Place rectangle at y in [80, 120] (overlaps control points at (100, 100), but curve max y is 75)
    rect = Rect(80.0, 80.0, 40.0, 40.0)
    assert not cb.intersects_rect(rect)

def test_cubic_bezier_intersects_rect_corner_clipping_hit():
    """Verify narrowphase detects when curve clips rectangle corner."""
    cb = CubicBezier(Point(0.0, 0.0), Point(100.0, 100.0), Point(100.0, 100.0), Point(200.0, 0.0))
    # Place rectangle intersecting the apex y=75.0
    rect = Rect(90.0, 70.0, 20.0, 20.0)
    assert cb.intersects_rect(rect)
```

---

### Pattern 8: Layer 3 Curve Routing Deflection & Reverse-Flow Tests (`tests/test_routing.py`)

#### Codebase Analog
Existing routing tests in [`tests/test_routing.py`](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py#L362-L442):
```python
def test_obstacle_avoidance_horizontal() -> None:
    # ...
def test_obstacle_avoidance_backward_compatibility() -> None:
    # ...
```

#### New Implementation Pattern
```python
def test_curve_deflection_single_obstacle_compact():
    """Compact obstacle triggers 2-segment spline (7 points) with C1 continuity at apex waypoint."""
    s1 = Shape("s1", "A", 100, 50).at(0, 100)
    s2 = Shape("s2", "B", 100, 50).at(400, 100)
    obs = Shape("obs", "Obstacle", 20, 20).at(200, 115)  # Compact obstacle
    edge = Edge(s1, s2, routing=Routing.CURVE)

    router = CurveRouter()
    pts = router.route(edge, obstacles=[obs], clearance=15.0)

    # Must generate 7 points (2 cubic segments) (D-06, D-07)
    assert len(pts) == 7
    p0, c0a, c0b, w, c1a, c1b, p3 = pts

    # Waypoint w must maintain clearance from obstacle
    assert w.y <= obs.bounds.top - 15.0 or w.y >= obs.bounds.bottom + 15.0

    # C1 continuity: incoming handle (c0b -> w) and outgoing handle (w -> c1a) collinear (D-05)
    v_in = w - c0b
    v_out = c1a - w
    # Unit tangents must match (parallel)
    assert math.isclose(v_in.x / v_in.distance_to(Point(0, 0)), v_out.x / v_out.distance_to(Point(0, 0)), abs_tol=1e-5)
    assert math.isclose(v_in.y / v_in.distance_to(Point(0, 0)), v_out.y / v_out.distance_to(Point(0, 0)), abs_tol=1e-5)

def test_curve_deflection_wide_obstacle_two_waypoints():
    """Wide obstacle triggers 3-segment spline (10 points) through 2 corner clearance waypoints."""
    s1 = Shape("s1", "A", 100, 50).at(0, 100)
    s2 = Shape("s2", "B", 100, 50).at(500, 100)
    obs = Shape("obs", "Wide Obstacle", 120, 60).at(200, 95)  # Wide obstacle: 120px > 2 * 15px
    edge = Edge(s1, s2, routing=Routing.CURVE)

    router = CurveRouter()
    pts = router.route(edge, obstacles=[obs], clearance=15.0)

    # Must generate 10 points (3 cubic segments) (D-06, D-07)
    assert len(pts) == 10
    p0, c0a, c0b, w1, c1a, c1b, w2, c2a, c2b, p3 = pts

    # Corner clearance invariant >= 15.0px (D-11)
    obs_corners = [obs.bounds.top_left, obs.bounds.top_right, obs.bounds.bottom_left, obs.bounds.bottom_right]
    for c in obs_corners:
        assert w1.distance_to(c) >= 15.0 - 1e-4
        assert w2.distance_to(c) >= 15.0 - 1e-4

    # Segment between w1 and w2 is straight horizontal bypass line (D-08)
    assert math.isclose(w1.y, w2.y, abs_tol=1e-5)
    assert math.isclose(c1a.y, w1.y, abs_tol=1e-5)
    assert math.isclose(c1b.y, w2.y, abs_tol=1e-5)

def test_reverse_flow_automatic_port_resolution():
    """Reverse-flow curved edge resolves unspecified ports to outward lateral ports (D-14)."""
    s1 = Shape("s1", "Src", 100, 50).at(300, 100)
    s2 = Shape("s2", "Tgt", 100, 50).at(50, 100)  # Target is to the left (reverse flow)
    edge = Edge(s1, s2, routing=Routing.CURVE)

    router = CurveRouter()
    ports = router.resolve_ports(edge)
    assert ports in ((Port.NORTH, Port.NORTH), (Port.SOUTH, Port.SOUTH))

def test_curve_routing_unobstructed_backward_compatibility():
    """Unobstructed curved edge with obstacles=None or empty obstacles returns exact 4 points (D-16)."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 0)
    edge = Edge(s1, s2, routing=Routing.CURVE)

    router = CurveRouter()
    pts_default = router.route(edge)
    pts_none = router.route(edge, obstacles=None)
    pts_empty = router.route(edge, obstacles=[])

    assert len(pts_default) == 4
    assert pts_default == pts_none == pts_empty
```

---

### Pattern 9: Layer 4 SVG Badge Centering Tests (`tests/test_renderer_svg.py`)

#### Codebase Analog
Existing curve badge tests in [`tests/test_renderer_svg.py`](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py#L662-L715):
```python
def test_svg_badge_arc_length_centering_on_asymmetric_curve() -> None:
    # ...
```

#### New Implementation Pattern
```python
def test_svg_multi_segment_spline_badge_on_longest_segment():
    """Protocol badge on a 3-segment deflected spline sits on the longest straight segment (D-12)."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("node_a", label="Source", width=100, height=50).at(0, 100)
    s2 = Shape("node_b", label="Target", width=100, height=50).at(600, 100)
    edge = Edge(s1, s2, label="HTTPS", routing=Routing.CURVE)

    # 10 waypoints: segment 0 (short 50px), segment 1 (long bypass 300px), segment 2 (short 50px)
    edge.waypoints = [
        Point(100.0, 125.0), Point(125.0, 125.0), Point(140.0, 50.0), Point(150.0, 50.0),  # Seg 0 (~60px)
        Point(150.0, 50.0), Point(250.0, 50.0), Point(350.0, 50.0), Point(450.0, 50.0),   # Seg 1 (300px LONGEST)
        Point(450.0, 50.0), Point(460.0, 50.0), Point(475.0, 125.0), Point(600.0, 125.0),  # Seg 2 (~130px)
    ]

    svg = renderer.render(elements=[s1, s2], edges=[edge], width=800, height=400)
    root = ET.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Find badge rect
    rects = root.findall(".//svg:g[@class='badge']/svg:rect", ns)
    if not rects:
        rects = [r for r in root.findall(".//svg:rect", ns) if r.attrib.get("rx") == "9.0"]
    assert len(rects) == 1
    badge_rect = rects[0]
    bx = float(badge_rect.attrib["x"])
    bw = float(badge_rect.attrib["width"])
    badge_center_x = bx + bw / 2.0

    # Badge must be centered on Segment 1 midpoint: (150 + 450) / 2 = 300.0
    assert abs(badge_center_x - 300.0) <= 2.0
```

---

## 4. Phase Execution Plan Guidance

Downstream planning agents should structure Phase 10 execution into three focused plans:

### Plan 10-01: Layer 0 Geometric Subdivision & Two-Tier Collision Math
1. In `src/diagrams_as_code/geometry.py`:
   - Add `CubicBezier.split(t: float = 0.5) -> tuple[CubicBezier, CubicBezier]`.
   - Add `CubicBezier.intersects_rect(rect: Rect, max_depth: int = 4) -> bool` with Tier 1 AABB broadphase filter and Tier 2 De Casteljau recursive narrowphase.
2. In `src/diagrams_as_code/connections.py`:
   - Add `clearance: Optional[float] = None` attribute and property on `Edge` with `_validate_clearance` (defaults to 15.0px).
3. In `tests/test_geometry.py`:
   - Add unit tests: `test_cubic_bezier_split_midpoint`, `test_cubic_bezier_intersects_rect_clear_miss`, `test_cubic_bezier_intersects_rect_direct_hit`, `test_cubic_bezier_intersects_rect_grazing_corner_miss`, `test_cubic_bezier_intersects_rect_corner_clipping_hit`.
4. Run `uv run pytest tests/test_geometry.py`.

### Plan 10-02: Layer 3 Obstacle Normalization, Collision Detection & Reverse-Flow Escape
1. In `src/diagrams_as_code/router.py`:
   - Add `_normalize_obstacles()` to `CurveRouter` (excluding source, target, matching IDs, and enclosing container groups per D-03).
   - Implement reverse-flow detection and automatic lateral port resolution `(Port.NORTH, Port.NORTH)` or `(Port.SOUTH, Port.SOUTH)` (D-14).
   - Implement lateral clearance corridor and $\ge 30.0\text{px}$ escape margin for reverse flows (D-13, D-15).
2. In `tests/test_routing.py`:
   - Add tests: `test_curve_collision_detection_excludes_endpoints_and_groups`, `test_reverse_flow_automatic_port_resolution`, `test_reverse_flow_lateral_clearance_corridor`, `test_reverse_flow_explicit_ports_escape`.
3. Run `uv run pytest tests/test_routing.py`.

### Plan 10-03: Layer 3 Deflection Waypoint Topology, Corridor Selection & Layer 4 Badge Placement
1. In `src/diagrams_as_code/router.py`:
   - Implement `_build_deflected_spline_horizontal` and `_select_deflected_corridor`:
     - Compact obstacle: 1 apex waypoint (7 points) (D-07).
     - Wide obstacle: 2 corner clearance waypoints (10 points) (D-07, D-11).
     - Strict $C^1$ collinear handles parallel to cleared obstacle edge (D-05, D-08).
     - Minimal deviation corridor evaluation and secondary obstacle avoidance (D-09, D-10).
     - Backward compatibility for unobstructed edges (D-16).
2. In `src/diagrams_as_code/renderer_svg.py`:
   - Update protocol badge positioning for multi-segment curves to find the longest segment by `arc_length()` and place badge at its `arc_length_midpoint(32)` (D-12).
3. In `tests/test_routing.py` and `tests/test_renderer_svg.py`:
   - Add deflection tests: `test_curve_deflection_single_obstacle_compact`, `test_curve_deflection_wide_obstacle_two_waypoints`, `test_curve_deflection_tangent_alignment`, `test_curve_deflection_secondary_obstacle_bypass`.
   - Add badge placement test: `test_svg_multi_segment_spline_badge_on_longest_segment`.
4. Run full test suite: `uv run pytest` (all 492+ tests and gallery examples passing with zero regressions).
