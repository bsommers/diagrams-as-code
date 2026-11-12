# Phase 11: Configuration Hierarchy, Layout & Extrema Integration - Research

**Domain:** Diagram Configuration Cascading, Layout Pipeline Dispatch & Analytical Extrema Canvas Growth  
**Researched:** 2026-09-28  
**Confidence:** HIGH  

> [!IMPORTANT]
> **Superseded in part (2026-09-28).** `11-CONTEXT.md` now revises D-05 to D-08 and adds D-13 to D-19 (routing data model and edge style resolution), following `docs/reviews/2026-09-28-edge-routing-architecture.md`. Where this research recommends `router_for_routing`, a `CURVED` alias, `translate_waypoints`, preserving non-empty `edge.waypoints`, or writing routes onto `edge.waypoints`, **CONTEXT.md wins.**

<user_constraints>
## Implementation Decisions

### Diagram Default Hierarchy & Cascade Precedence
- **D-01:** `Diagram(routing=...)` defaults to `None`. When unset (`None`), it falls back to `"orthogonal"`, preserving 100% backward compatibility for all existing diagrams, test suites, and gallery renders.
- **D-02:** Configuration precedence follows a strict 3-tier cascade: Explicit `Edge` / `_EdgeBuilder` parameter > `Diagram` default property > System default (`"orthogonal"`, `corner_radius=0.0`, `clearance=15.0`).
- **D-03:** For `corner_radius`, `None` signals "inherit diagram default", allowing `corner_radius=0.0` to explicitly force sharp corners on individual edges even when a diagram-wide `corner_radius` (e.g. 12.0) is configured.
- **D-04:** `Diagram.configure(routing=..., corner_radius=..., clearance=...)` supports dynamic runtime reconfiguration of diagram routing defaults and marks `self._is_solved = False` to invalidate cached layout and routing.

### Layout Pipeline Routing Execution & Lifecycle
- **D-05:** Layout pipeline uses a dynamic router factory / dispatcher: `router_for_routing(edge.routing)` dispatches to `CurveRouter` for `Routing.CURVED`, `OrthogonalRouter` for `Routing.ORTHOGONAL`, or direct/polyline calculations.
- **D-06:** In `run_layout()`, edge routing executes BEFORE canvas auto-growth (`_grow_canvas`), populating `edge.waypoints` and `diagram.routes` so canvas boundary calculations have full visibility into edge trajectories and extrema.
- **D-07:** If an `Edge` already has `edge.waypoints` explicitly populated and non-empty (e.g. manually placed or loaded from file), `run_layout()` preserves it and skips auto-routing for that edge.
- **D-08:** `run_layout()` passes all elements AND diagram groups (`elements + diagram.groups`) as obstacles to the edge routers for comprehensive collision deflection coverage.

### Canvas Auto-Growth & Extrema Clipping Margin
- **D-09:** Analytical curve bounding box: `_grow_canvas` evaluates analytical bounding boxes (`CubicBezier.bbox()` for curved/bezier edges, and corner/vertex envelopes for orthogonal/polyline) to compute the true geometric envelope of all edges.
- **D-10:** Coordinate framing (`_frame`): If Bezier curves or detours arch into negative coordinates (or above the top title banner area, `min_y < FRAME_Y` or `min_x < FRAME_X`), framing translates both elements and edge waypoints by `offset_x` / `offset_y` so curves are never clipped on the top or left.
- **D-11:** Canvas margins: Standard `FRAME_X` (60.0px) and `FRAME_Y` (80.0px) framing margins are applied between curve extrema and the diagram canvas boundary, matching element layout margins.
- **D-12:** Max-expansion only: Canvas dimensions are updated via `diagram.width = max(diagram.width, max_x + FRAME_X)` and `diagram.height = max(diagram.height, max_y + FRAME_Y)`, preserving user-specified dimensions unless content actually overflows.

### Claude's Discretion
- Router factory naming and location: implementation can place `get_router(routing: Routing)` or `router_for_routing` in `router.py` or `layout/pipeline.py`.
- Translation helper: translation of edge waypoints during `_frame` can be encapsulated in a clean utility function `translate_waypoints(waypoints, dx, dy)`.
- Internal structure of `_grow_canvas`: may split or combine element and edge extrema scanning cleanly.

## Deferred Ideas
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements Coverage

| Requirement | Description | Research Status | Implementation Location |
|-------------|-------------|-----------------|-------------------------|
| **CFG-01** | User can set diagram-wide default edge routing and corner radius via `Diagram(routing=..., corner_radius=...)`. | Validated: Add `routing: Optional[Union[Routing, str]] = None` to `Diagram.__init__`, implement `@property routing` getter/setter with enum coercion, update `Diagram.configure()`, and invalidate cache (`self._is_solved = False`). | `src/diagrams_as_code/diagram.py` |
| **CFG-02** | Connections created via fluent operators (`s1 >> s2`) inherit diagram defaults while individual `Edge` parameters take precedence. | Validated: Update `_EdgeBuilder.__init__` and `Edge.__init__` to default `routing` to `None`, storing explicit setting in `_routing` while keeping `Edge.routing` property returning `Routing.ORTHOGONAL` when unconfigured. Cascade in `_EdgeBuilder.__rshift__`, `Diagram.connect()`, and `Diagram.solve()`. | `src/diagrams_as_code/diagram.py`, `src/diagrams_as_code/connections.py` |
| **CFG-03** | Layout pipeline automatically runs unified edge routing for all diagram edges, populating `edge.waypoints` and `diagram.routes`. | Validated: In `layout/pipeline.py`, replace hardcoded `OrthogonalRouter()` with `router_for_routing(edge.routing)` (or `EdgeRouter`), run routing before framing and canvas growth, pass `elements + diagram.groups` as obstacles, and preserve manually supplied `edge.waypoints`. | `src/diagrams_as_code/layout/pipeline.py`, `src/diagrams_as_code/router.py` |
| **CFG-04** | Diagram canvas boundaries automatically expand (`_grow_canvas`) to encompass analytical curve extrema so high-arching Bezier curves are never clipped. | Validated: Use `CubicBezier.bbox()` for curved/bezier segments and polyline bounds for orthogonal/direct paths. In `_frame`, translate elements and edge waypoints via `translate_waypoints()` when content arches into negative coordinates or above `FRAME_Y` (in auto layout). In `_grow_canvas`, max-expand canvas dimensions with `FRAME_X` and `FRAME_Y` margins. | `src/diagrams_as_code/layout/pipeline.py` |
</phase_requirements>

---

## Executive Summary

Phase 11 unifies the configuration hierarchy, layout pipeline execution lifecycle, and canvas boundary auto-expansion across all routing strategies (`Routing.ORTHOGONAL`, `Routing.CURVE`, `Routing.DIRECT`). Milestone v0.8.0 previously completed Phase 8 (Cubic Bezier primitives & SVG rendering), Phase 9 (Rounded corner fillets), and Phase 10 (Obstacle detection and deflection for curves). Prior to Phase 11, curved routing was configured only per-edge (`Edge(routing=Routing.CURVE)`), and `layout/pipeline.py` ran only `OrthogonalRouter()` at the very end of `run_layout()`, after `_frame` and `_grow_canvas` had already completed.

This phase completes Milestone v0.8.0 by:
1. **Diagram Default Hierarchy (CFG-01, CFG-02):** Enabling users to specify `Diagram(routing=Routing.CURVE, corner_radius=12.0, clearance=25.0)` and `diag.configure(...)`. Fluent connections (`s1 >> s2` and `s1 >> diag.edge(...) >> s2`) cleanly inherit diagram defaults, while explicit edge arguments override diagram defaults with 100% backward compatibility for all existing diagrams and tests.
2. **Unified Routing Dispatch (CFG-03):** Dispatching routing dynamically via `router_for_routing(edge.routing)` (or `EdgeRouter`) in `run_layout()` before framing and canvas expansion, populating `edge.waypoints` and `diagram.routes`, preserving explicit non-empty waypoints, and feeding comprehensive obstacles (`elements + diagram.groups`) into both `CurveRouter` and `OrthogonalRouter`.
3. **Extrema-Aware Canvas Auto-Growth & Framing (CFG-04):** Computing analytical bounding boxes using `CubicBezier.bbox()` (derivative roots $B'(t) = 0$) for curved edges and vertex envelopes for orthogonal edges. `_frame` translates elements and edge waypoints synchronously when curves arch into negative coordinates (or above the top banner area in auto-layout), and `_grow_canvas` expands `diagram.width` and `diagram.height` to encompass all curve extrema with standard framing margins (`FRAME_X = 60.0`, `FRAME_Y = 80.0`).

All changes adhere strictly to the zero-dependency pure Python standard library rule and pass AST module boundary validation.

---

## Architectural Responsibility Map

Conforming to `tests/test_module_boundaries.py` layer constraints (`geometry` 0 < `connections` 2 < `router` 3 < `layout` 4 < `diagram` 5):

```
+---------------------------------------------------------------------------------+
| Layer 5: src/diagrams_as_code/diagram.py                                        |
| - Diagram.__init__(routing=None, corner_radius=None, clearance=None)            |
| - Diagram.routing property getter/setter with enum coercion                     |
| - Diagram.configure(routing=..., corner_radius=..., clearance=...)              |
| - _EdgeBuilder.__init__(routing=None) & __rshift__ default cascading            |
| - Diagram.connect(routing=None) inheritance resolution                          |
| - Diagram.solve() edge default cascading & layout execution                     |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
| Layer 4: src/diagrams_as_code/layout/pipeline.py                                |
| - run_layout(): lifecycle reordering (route -> frame -> grow canvas)            |
| - _route_edges(): routes diagram.edges via router_for_routing() with obstacles  |
| - _get_edge_bounds(): evaluates CubicBezier.bbox() and polyline bounds          |
| - _frame(): translates roots & edge waypoints when min_x < 0 or min_y < 0       |
| - _grow_canvas(): expands diagram.width/height based on element & edge extrema  |
| - translate_waypoints(): translates [Point] by (offset_x, offset_y)             |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
| Layer 3: src/diagrams_as_code/router.py                                         |
| - router_for_routing(routing): returns CurveRouter() or OrthogonalRouter()      |
| - EdgeRouter.route(): unified routing facade                                    |
| - CurveRouter & OrthogonalRouter: normalize obstacles, detect collisions        |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
| Layer 2: src/diagrams_as_code/connections.py                                    |
| - Routing enum: DIRECT = "direct", ORTHOGONAL = "orthogonal", CURVE = "curve"   |
|   (with CURVED = "curve" alias for robust typing)                               |
| - Edge.__init__(routing=None): records explicit vs inherited routing            |
| - Edge.routing property: returns self._routing or Routing.ORTHOGONAL            |
| - Edge.corner_radius & clearance validation helpers                             |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
| Layer 0: src/diagrams_as_code/geometry.py                                       |
| - CubicBezier.bbox(): analytical derivative roots quadratic solver              |
| - Point, Rect primitives                                                        |
+---------------------------------------------------------------------------------+
```

---

## Standard Stack

The core engine strictly requires zero external runtime dependencies (`dependencies = []` in `pyproject.toml`). All geometric calculations, polynomial evaluations, and data cascading execute in Python `>=3.10`:

| Module / Component | Purpose | Justification |
|--------------------|---------|---------------|
| `math` | Root finding, hypotenuse, trigonometric checks | Built-in standard library; IEEE 754 precision |
| `dataclasses` | `CubicBezier`, `_LayoutState`, `Point`, `Rect` | Zero-overhead immutable geometric value objects |
| `enum.Enum` | `Routing`, `Port` | Strongly typed domain enums with string coercion |
| `pathlib.Path` | Path handling in `Diagram.configure()` | Standard library filesystem paths |
| `typing` | `Union`, `Optional`, `Sequence`, `Literal` | Static typing and mypy compliance |

---

## Architecture Patterns & Implementation Details

### Pattern 1: 3-Tier Configuration Cascading with Sentinels (D-01, D-02, D-03)

To ensure explicit overrides take precedence over diagram defaults, which take precedence over global system defaults:
- **Tier 1 (Explicit Edge / Builder parameter):** The user explicitly provides `routing=Routing.ORTHOGONAL` or `corner_radius=0.0`.
- **Tier 2 (Diagram default property):** `Diagram(routing=Routing.CURVE, corner_radius=12.0)`.
- **Tier 3 (System default):** `Routing.ORTHOGONAL`, `corner_radius=0.0`, `clearance=15.0`.

#### The Sentinel Pattern for `Edge.routing`
In `connections.py`:
```python
class Edge:
    def __init__(
        self,
        source: Element,
        target: Element,
        ...,
        routing: Optional[Union[Routing, str]] = None,
        corner_radius: Optional[float] = None,
        arc_radius: Optional[float] = None,
        clearance: Optional[float] = None,
        ...,
    ) -> None:
        ...
        self._routing: Optional[Routing] = (
            _coerce_enum(routing, Routing, "routing", allow_none=False)
            if routing is not None
            else None
        )
        effective_r = corner_radius if corner_radius is not None else arc_radius
        self._corner_radius: Optional[float] = self._validate_corner_radius(effective_r)
        self._clearance_is_default: bool = clearance is None
        self._clearance: float = self._validate_clearance(clearance)

    @property
    def routing(self) -> Routing:
        """Routing strategy for this edge; defaults to ORTHOGONAL when unset."""
        if self._routing is not None:
            return self._routing
        return Routing.ORTHOGONAL

    @routing.setter
    def routing(self, val: Optional[Union[Routing, str]]) -> None:
        if val is None:
            self._routing = None
        else:
            self._routing = _coerce_enum(val, Routing, "routing", allow_none=False)
```

**Key Benefit:**
- Standalone edges outside a diagram still evaluate `edge.routing == Routing.ORTHOGONAL`, satisfying all existing unit tests.
- When an edge enters a diagram, the diagram solver checks `edge._routing is None`. If `None`, the edge inherits `diag.routing`. If the user passed `routing=Routing.ORTHOGONAL` explicitly, `edge._routing` is not `None`, so it is preserved!

#### `_EdgeBuilder` & `Diagram.connect` Cascading
In `_EdgeBuilder.__init__`:
`routing: Optional[Union[Routing, str]] = None`
In `_EdgeBuilder.__rshift__`:
```python
effective_routing = self.routing
if effective_routing is None and diag is not None and diag.routing is not None:
    effective_routing = diag.routing
if effective_routing is None:
    effective_routing = Routing.ORTHOGONAL
```
And similarly for `corner_radius` and `clearance`.

In `Diagram.connect()`:
```python
effective_routing = routing if routing is not None else (self.routing or Routing.ORTHOGONAL)
effective_r = corner_radius if corner_radius is not None else arc_radius
if effective_r is None and self.corner_radius is not None:
    effective_r = self.corner_radius
effective_c = clearance if clearance is not None else self.clearance
```

In `Diagram.solve()`:
```python
if self.routing is not None:
    for edge in self.edges:
        if edge._routing is None:
            edge.routing = self.routing
if self.corner_radius is not None:
    for edge in self.edges:
        if edge.corner_radius is None:
            edge.corner_radius = self.corner_radius
if self.clearance is not None:
    for edge in self.edges:
        if edge._clearance_is_default:
            edge.clearance = self.clearance
```

---

### Pattern 2: Router Dispatch & Router Factory (D-05, D-08, CFG-03)

In `router.py`:
```python
def router_for_routing(routing: Union[Routing, str]) -> Any:
    """Return the router instance for the specified routing strategy."""
    if isinstance(routing, str):
        routing_norm = routing.lower()
    elif isinstance(routing, Routing):
        routing_norm = routing.value
    else:
        raise TypeError(f"Expected Routing or str, got {type(routing).__name__}")

    if routing_norm in ("curve", "curved"):
        return CurveRouter()
    return OrthogonalRouter()
```
`OrthogonalRouter` already handles `Routing.DIRECT` (returning `[p_start, p_end]`) and `Routing.ORTHOGONAL`. `CurveRouter` handles `Routing.CURVE`.

In `run_layout()`:
```python
def _route_edges(diagram: Any, elements: list[Element], obstacles: list[Any]) -> None:
    routes: dict[int, list[Point]] = {}
    auto_routed = diagram._layout_state.auto_routed_edges
    for edge in diagram.edges:
        # D-07: Preserve explicit user-provided waypoints
        if edge.waypoints is not None and len(edge.waypoints) > 0 and id(edge) not in auto_routed:
            routes[id(edge)] = edge.waypoints
            continue

        router = router_for_routing(edge.routing)
        waypoints = router.route(edge, obstacles=obstacles, clearance=edge.clearance)
        edge.waypoints = waypoints
        routes[id(edge)] = waypoints
        auto_routed.add(id(edge))
    diagram.routes = routes
```

**Obstacle Coverage (D-08):**
Obstacles passed to `_route_edges` are:
```python
obstacles = list(elements) + [g for g in diagram.groups if g not in elements]
```
Both `CurveRouter` and `OrthogonalRouter` already implement `_normalize_obstacles()`, which safely extracts `bounds`, ignores endpoints/source/target, and ignores enclosing groups when endpoints reside inside them.

---

### Pattern 3: Lifecycle Reordering in `run_layout()` (D-06, D-07)

Currently, `run_layout()` routes edges *after* `_grow_canvas()`. Phase 11 reorders the pipeline:
1. `_reset(diagram, elements)` — restores base coordinates and clears `auto_routed_edges`.
2. `_apply_layout_file(diagram, elements)`
3. `_auto_place(diagram, elements)` (if `diagram.layout == "auto"`)
4. `diagram.solver.solve()`
5. `_refresh_group_bounds(groups)`
6. `_route_edges(diagram, elements, obstacles)` — **Edge routing executes here!** Populates `edge.waypoints` and `diagram.routes`.
7. `_frame(diagram, elements, groups)` — translates elements and edge waypoints if content has negative coordinates or breaches auto-layout margins.
8. `_grow_canvas(diagram, elements)` — evaluates analytical curve extrema and element bounds to expand canvas.
9. `diagram._layout_state.grown_size = (diagram.width, diagram.height)`
10. `_warn_pinned_overlaps(diagram, elements, auto_ids)` (if auto)

---

### Pattern 4: Analytical Extrema Calculation & Coordinate Framing (D-09, D-10, D-11, D-12, CFG-04)

#### Analytical Curve Bounding Box (`_get_edge_bounds`)
A cubic Bezier curve edge's waypoints format is:
- Single-segment curve: 4 points `[P0, C1, C2, P3]`
- Multi-segment spline: $3k + 1$ points `[P0, C1, C2, P3, C4, C5, P6, ...]`
- Orthogonal / direct polyline: sequence of vertices $[W_0, W_1, \dots, W_m]$

For cubic Beziers, `CubicBezier(p0, c1, c2, p3).bbox()` solves the quadratic derivative roots $B'(t) = 0$ in $[0, 1]$ via `math.sqrt()` to find exact extrema.

```python
def _get_edge_bounds(edge: Edge) -> Optional[Rect]:
    pts = edge.waypoints
    if not pts:
        return None
    is_curve = edge.routing in (Routing.CURVE, "curve", "curved")
    if is_curve and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
        min_x = float("inf")
        max_x = float("-inf")
        min_y = float("inf")
        max_y = float("-inf")
        for i in range(0, len(pts) - 1, 3):
            cb = CubicBezier(pts[i], pts[i + 1], pts[i + 2], pts[i + 3])
            b = cb.bbox()
            min_x = min(min_x, b.left)
            max_x = max(max_x, b.right)
            min_y = min(min_y, b.top)
            max_y = max(max_y, b.bottom)
        return Rect(min_x, min_y, max(0.0, max_x - min_x), max(0.0, max_y - min_y))
    else:
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)
        return Rect(min_x, min_y, max(0.0, max_x - min_x), max(0.0, max_y - min_y))
```

#### Waypoint Translation Helper (`translate_waypoints`)
Affine translation of cubic Beziers:
$$\text{CubicBezier}(P_0 + \vec{v}, C_1 + \vec{v}, C_2 + \vec{v}, P_3 + \vec{v}) = \text{CubicBezier}(P_0, C_1, C_2, P_3) + \vec{v}$$
Translating both element bounds and edge waypoints by $(dx, dy)$ maintains port tangency and collision avoidance invariants exactly.

```python
def translate_waypoints(waypoints: list[Point], dx: float, dy: float) -> list[Point]:
    """Translate a list of waypoints by offset (dx, dy)."""
    return [Point(p.x + dx, p.y + dy) for p in waypoints]
```

#### Coordinate Framing (`_frame`)
```python
def _frame(diagram: Any, elements: list[Element], groups: list[Group]) -> None:
    """Translate elements and edge waypoints when content has negative coordinates."""
    roots = [e for e in elements if getattr(e, "parent", None) is None]
    if not roots and not diagram.edges:
        return

    elem_min_x = min((e.bounds.x for e in roots), default=float("inf"))
    elem_min_y = min((e.bounds.y for e in roots), default=float("inf"))

    edge_min_x = float("inf")
    edge_min_y = float("inf")
    for edge in diagram.edges:
        eb = _get_edge_bounds(edge)
        if eb is not None:
            edge_min_x = min(edge_min_x, eb.left)
            edge_min_y = min(edge_min_y, eb.top)

    min_x = min(elem_min_x, edge_min_x)
    min_y = min(elem_min_y, edge_min_y)

    # In auto layout, threshold is frame margin (FRAME_X, FRAME_Y); in manual layout, threshold is 0.0
    thresh_x = FRAME_X if diagram.layout == "auto" else 0.0
    thresh_y = FRAME_Y if diagram.layout == "auto" else 0.0

    offset_x = max(0.0, FRAME_X - min_x) if min_x < thresh_x else 0.0
    offset_y = max(0.0, FRAME_Y - min_y) if min_y < thresh_y else 0.0

    if offset_x > 0.0 or offset_y > 0.0:
        for r in roots:
            r.translate(offset_x, offset_y)
        _refresh_group_bounds(groups)
        for edge in diagram.edges:
            if edge.waypoints is not None:
                edge.waypoints = translate_waypoints(edge.waypoints, offset_x, offset_y)
                diagram.routes[id(edge)] = edge.waypoints
```

#### Canvas Auto-Growth (`_grow_canvas`)
```python
def _grow_canvas(diagram: Any, elements: list[Element]) -> None:
    roots = [e for e in elements if e.parent is None]
    max_x = max((e.bounds.right for e in roots), default=0.0)
    max_y = max((e.bounds.bottom for e in roots), default=0.0)

    for edge in diagram.edges:
        eb = _get_edge_bounds(edge)
        if eb is not None:
            max_x = max(max_x, eb.right)
            max_y = max(max_y, eb.bottom)

    if roots or diagram.edges:
        diagram.width = max(diagram.width, max_x + FRAME_X)
        diagram.height = max(diagram.height, max_y + FRAME_Y)
```

---

## Don't Hand-Roll

| Problem | Established Tool / Method | Why Not Hand-Roll |
|---------|---------------------------|-------------------|
| Cubic Bezier Bounding Box | `CubicBezier.bbox()` in `geometry.py` | Already implemented and verified against analytical derivative roots ($B'(t) = 0$). Hand-rolling endpoint-only or control-point-only bounds will either underflow (clipping) or inflate excessively. |
| Enum Coercion | `_coerce_enum()` in `connections.py` | Handles case-insensitivity, enum instances, strings, and custom error messages uniformly. |
| Group Bounds Calculation | `_refresh_group_bounds()` & `calculate_bounds()` | Properly computes padding and header heights hierarchically. |
| Idempotent Solver Reset | `_reset()` with `_LayoutState` | Keeps user-specified canvas dimensions intact across multiple solves without state pollution. |

---

## Common Pitfalls & Mitigations

### Pitfall 8: Edge Default Precedence Masking Diagram-Level Routing Configuration
- **Failure:** Instantiating `Edge(s1, s2)` bakes in `routing = Routing.ORTHOGONAL` before `Diagram` can cascade defaults. As a result, `Diagram(routing=Routing.CURVE)` has no effect on edges.
- **Root Cause:** Default argument in `Edge.__init__` was `routing = Routing.ORTHOGONAL`.
- **Mitigation:** Change default to `routing: Optional[Union[Routing, str]] = None`. Store `self._routing: Optional[Routing]`. The `@property def routing` returns `self._routing or Routing.ORTHOGONAL`. Standalone edges evaluate to `Routing.ORTHOGONAL`, but `Diagram.solve()` and `_EdgeBuilder` can check `if edge._routing is None:` to cascade `diag.routing`.

### Pitfall 10: Canvas Clipping from Unchecked Curve Extrema
- **Failure:** High-arching Bezier curves or obstacle deflection detours extend beyond `diagram.width` or `diagram.height`, cutting off SVG paths and arrowheads.
- **Root Cause:** `_grow_canvas()` previously scanned only element bounding boxes (`e.bounds.right`, `e.bounds.bottom`), completely blind to edge trajectories.
- **Mitigation:** Scan all edge bounds using `_get_edge_bounds()` in `_grow_canvas()`, computing exact derivative root envelopes via `CubicBezier.bbox()`. Max-expand canvas dimensions to `max_x + FRAME_X` and `max_y + FRAME_Y`.

### Pitfall 11: Idempotency Breakage on Re-solve / `configure()`
- **Failure:** When `d.configure(routing="curve")` is called and `d.solve()` re-runs, the layout engine sees existing `edge.waypoints` and skips re-routing (thinking they were user-pinned waypoints).
- **Root Cause:** Inability to distinguish auto-routed waypoints from user-supplied manual waypoints.
- **Mitigation:** Track `auto_routed_edges: set[int]` in `_LayoutState`. In `_reset()`, clear `edge.waypoints = None` for any edge whose ID is in `auto_routed_edges`, while preserving true user-pinned waypoints.

### Pitfall 12: Desynchronized Framing Translations
- **Failure:** `_frame` shifts element bounding boxes to positive coordinates, but leaves edge waypoints behind, causing edges to detach from element ports.
- **Root Cause:** Translating `Element.bounds` without applying the identical `(offset_x, offset_y)` translation to `edge.waypoints`.
- **Mitigation:** Apply `translate_waypoints(edge.waypoints, offset_x, offset_y)` to all edges whenever `_frame` applies non-zero offsets, and update `diagram.routes[id(edge)]`.

---

## Code Examples

### Example 1: Diagram Default Cascading with Fluent Operator & Sharp Override
```python
with Diagram("Architecture", routing=Routing.CURVE, corner_radius=12.0) as diag:
    db = diag.shape("Database")
    api = diag.shape("API Service").right_of(db, margin=100)
    auth = diag.shape("Auth Service").below(api, margin=60)

    # 1. Inherits diagram default (CURVE)
    db >> api

    # 2. Explicit sharp override (ORTHOGONAL with sharp corners)
    api >> diag.edge(routing=Routing.ORTHOGONAL, corner_radius=0.0) >> auth

    # 3. Explicit fillet override (ORTHOGONAL with custom radius)
    auth >> diag.edge(routing=Routing.ORTHOGONAL, corner_radius=20.0) >> db
```

### Example 2: Dynamic Runtime Reconfiguration via `Diagram.configure()`
```python
diag = Diagram("Dynamic")
a = diag.shape("A")
b = diag.shape("B").right_of(a, margin=80)
a >> b

# Initially orthogonal
diag.solve()
assert diag.edges[0].routing == Routing.ORTHOGONAL

# Reconfigure diagram default to CURVE
diag.configure(routing=Routing.CURVE)
diag.solve()
assert diag.edges[0].routing == Routing.CURVE
assert len(diag.edges[0].waypoints) == 4  # Cubic Bezier
```

### Example 3: Canvas Auto-Expansion on High-Arching Curve Extrema
```python
with Diagram("Auto Growth", width=400, height=300) as diag:
    s = diag.shape("Source").at(50, 200)
    t = diag.shape("Target").at(350, 200)
    # Reverse flow with explicit ports forces top escape corridor above both shapes
    diag.connect(s, t, source_port=Port.EAST, target_port=Port.WEST, routing=Routing.CURVE)

# Canvas automatically expands height/width to encompass escape corridor and curve arch
assert diag.width >= 400
assert diag.height >= 300
```

---

## Validation Architecture

### Nyquist Test Plan & Quality Gates

The test architecture ensures 100% test coverage across all 4 requirements without degrading test performance:

1. **Unit Tests (`tests/test_diagram_api.py`):**
   - Diagram constructor initialization: `Diagram(routing=Routing.CURVE)`, `Diagram(routing="curve")`, `Diagram(routing="curved")`.
   - `Diagram.routing` property getter/setter with error validation on invalid strings or types.
   - `Diagram.configure(routing=...)` re-marking `self._is_solved = False`.
   - 3-tier precedence cascade: Explicit `Edge` / `_EdgeBuilder` parameter > `Diagram` default property > System default.
   - Fluent operator chain (`a >> b >> c`) inheriting diagram routing defaults.
   - Mixed routing in single diagram (`Routing.CURVE` alongside `Routing.ORTHOGONAL` with `corner_radius=0.0`).

2. **Layout Pipeline Tests (`tests/test_layout_pipeline.py`):**
   - Routing lifecycle: Edge waypoints and `diagram.routes` populated during `run_layout()`.
   - Explicit waypoints preservation: Non-empty `edge.waypoints` preserved across layout passes.
   - Idempotency across multiple solves with `auto_routed_edges` reset.
   - Obstacle coverage: Both elements and diagram groups passed to routing engines.

3. **Extrema & Framing Tests (`tests/test_layout_pipeline.py` / `tests/test_routing.py`):**
   - Analytical bounding box evaluation: `_get_edge_bounds()` matches `CubicBezier.bbox()`.
   - Canvas expansion (`_grow_canvas`): Canvas grows to encompass high-arching curve extrema and lateral deflection detours with `FRAME_X` and `FRAME_Y` margins.
   - Canvas non-shrinking: Explicit user canvas dimensions larger than content are preserved.
   - Framing translation (`_frame`): When curve extrema or detours have negative coordinates (`min_y < 0` or `min_x < 0`), elements and waypoints are translated together via `translate_waypoints()`.
   - Auto-layout margin framing: When a curve arches above `FRAME_Y` in auto-layout, framing shifts content down so the curve clears the top banner area.

4. **Regression & Safety Guards:**
   - Full suite execution: all 520 tests must pass (`uv run pytest`).
   - AST module boundary verification: `tests/test_module_boundaries.py` passes with zero circular or upward imports.
   - Benchmark evaluation: `uv run python tools/eval_bezier.py` passes 10/10 scenarios.
   - Icon hygiene: `uv run python tools/generate_icons.py --check` passes.
