# Architecture Research

**Domain:** Directed Diagramming Engine — Curved & Bezier Edge Routing Architecture  
**Researched:** 2026-09-24  
**Confidence:** HIGH  

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Layer 5: Diagram & Fluent API                        │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────┐         ┌─────────────────────────────────┐  │
│  │ Diagram               │         │ _EdgeBuilder / connect()        │  │
│  │ - default routing     │────────▶│ - per-edge routing override    │  │
│  │ - default arc_radius  │         │ - per-edge arc_radius override  │  │
│  └───────────┬───────────┘         └────────────────┬────────────────┘  │
│              │                                      │                   │
├──────────────┴──────────────────────────────────────┴───────────────────┤
│                    Layer 4: Layout & Rendering Layer                    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  ┌────────────────────────────┐  │
│  │ layout/pipeline.py (run_layout)   │  │ renderer_svg.py            │  │
│  │ - routes all edges                │  │ - path generation:         │  │
│  │ - populates edge.waypoints        │  │   * M...L (direct/sharp)   │  │
│  │ - builds diagram.routes dict      │  │   * M...L...Q/A (fillets)  │  │
│  └─────────────────┬─────────────────┘  │   * M...C (cubic Bezier)   │  │
│                    │                    │ - midpoint badge placing   │  │
│                    │                    └──────────────▲─────────────┘  │
│                    │                                   │                │
├────────────────────┴───────────────────────────────────┴────────────────┤
│                    Layer 3: Routing Engine                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ router.py (EdgeRouter / OrthogonalRouter / CurveRouter)           │  │
│  │ - resolve_ports(): cardinal port & normal vector resolution       │  │
│  │ - OrthogonalRouter: Manhattan waypoints, obstacle A* corridors    │  │
│  │ - CurveRouter: Port tangents, control points C1/C2, deflection    │  │
│  │ - Evaluates curve collision & avoidance waypoints                 │  │
│  └─────────────────┬─────────────────────────────────────────────────┘  │
│                    │                                                    │
├────────────────────┴────────────────────────────────────────────────────┤
│                    Layer 2: Connections & Domain Entities               │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   ┌─────────────────────────────┐  │
│  │ Edge (connections.py)           │   │ Routing (enum)              │  │
│  │ - routing: DIRECT|ORTHO|CURVE   │   │ - DIRECT = "direct"         │  │
│  │ - arc_radius: float             │   │ - ORTHOGONAL = "orthogonal" │  │
│  │ - waypoints: list[Point]        │   │ - CURVE = "curve"           │  │
│  └─────────────────┬───────────────┘   └─────────────────────────────┘  │
│                    │                                                    │
├────────────────────┴────────────────────────────────────────────────────┤
│                    Layer 0: Geometry & Primitives                       │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────────────┐  │
│  │ Point(x, y)  │   │ Rect(...)    │   │ CubicBezier(p0, c1, c2, p3) │  │
│  └──────────────┘   └──────────────┘   └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `geometry.CubicBezier` (Layer 0) | Pure math representation of a cubic Bezier segment. Evaluates point at $t \in [0, 1]$, tangent vector $B'(t)$, and bounding box. | `@dataclass(frozen=True)` with analytical Bernstein polynomial evaluation. |
| `connections.Edge` (Layer 2) | Connection metadata holder. Tracks source, target, ports, routing mode, corner fillet radius (`arc_radius`), and calculated waypoints. | Python class with type validation, enum coercion, and default fallback to diagram settings. |
| `connections.Routing` (Layer 2) | Supported routing strategies: `DIRECT`, `ORTHOGONAL`, `CURVE`. | `Enum` (already existing in `connections.py`). |
| `router.CurveRouter` (Layer 3) | Calculates Bezier control points from port normals, detects obstacle collision via curve sampling, and routes deflected Bezier splines. | Class in `router.py` taking `Edge` and obstacle `Rect`s; outputs ordered `list[Point]`. |
| `router.OrthogonalRouter` (Layer 3) | Calculates Manhattan waypoints and A* detour paths around obstacles. Delegator for orthogonal edges. | Existing class in `router.py`; backward-compatible API maintained. |
| `router.EdgeRouter` (Layer 3) | Unified routing facade dispatching to `DIRECT`, `OrthogonalRouter`, or `CurveRouter` based on `edge.routing`. | Routing coordinator class ensuring uniform route signature. |
| `layout/pipeline.run_layout` (Layer 4) | Orchestrates diagram layout and calls router for all edges before rendering. | Layout pipeline step 7 updating `edge.waypoints` and `diagram.routes`. |
| `renderer_svg.SVGRenderer` (Layer 4) | Pure presentation renderer converting geometric routes into SVG `<path d="...">` XML string and positioning protocol badges. | `render_edge_path()` helper formatting `M...L`, `M...C`, and `M...L...Q...L`. |
| `diagram.Diagram` (Layer 5) | Context manager and container. Holds diagram-level default `routing` and `arc_radius`. Cascades defaults down to edges. | Configurable properties on `Diagram`, `Diagram.configure()`, and `_EdgeBuilder`. |

---

## Recommended Project Structure

```
src/diagrams_as_code/
├── geometry.py             # Layer 0: Point, Rect, Anchor, Size, + CubicBezier primitive
├── connections.py          # Layer 2: Port, Routing enum, Edge (+ arc_radius attribute)
├── router.py               # Layer 3: OrthogonalRouter, + CurveRouter, + EdgeRouter dispatch
├── layout/
│   └── pipeline.py         # Layer 4: run_layout invokes EdgeRouter for all edges
├── renderer_svg.py         # Layer 4: SVG path generator for C curves & Q/A fillets
└── diagram.py              # Layer 5: Diagram(routing=..., arc_radius=...) & builder cascading
```

### Structure Rationale

- **`geometry.py` (Layer 0):** Adding `CubicBezier` to `geometry.py` keeps pure geometric calculations (Bernstein polynomials, curve bounding boxes, $t$-parameter evaluation) at the lowest layer without importing anything from higher layers. This complies 100% with `test_module_boundaries.py` AST import rules.
- **`connections.py` (Layer 2):** `Routing.CURVE` already exists here. Adding `arc_radius: float = 0.0` to `Edge.__init__` allows both orthogonal fillets and curve configurations to live directly on the edge specification.
- **`router.py` (Layer 3):** All waypoint and control point calculations belong strictly in the router, not the renderer. Keeping `CurveRouter` in `router.py` alongside `OrthogonalRouter` allows obstacle-avoidance logic (`_normalize_obstacles`, `segment_intersects_rect`, A* detour channels) to be reused cleanly without circular dependencies.
- **`renderer_svg.py` (Layer 4):** Strictly translates calculated waypoints and control points into SVG path syntax (`d="M... C..."` or `d="M... Q..."`) and places badge text at the evaluated curve midpoint.

---

## Architectural Patterns

### Pattern 1: Control Point Separation (Router Calculates, Renderer Draws)

**What:** Control points ($C_1, C_2$) and intermediate avoidance waypoints are calculated during the layout/routing phase (`router.py`), never inside `renderer_svg.py`. The renderer only maps geometric points into SVG path commands.  
**When to use:** All edge routing (`DIRECT`, `ORTHOGONAL`, `CURVE`).  
**Trade-offs:** Decouples geometric routing algorithms from XML generation. Allows unit tests to verify control point coordinates without parsing SVG strings. Ensures label/badge placement math has access to the exact mathematical curve.

**Example:**
```python
# In router.py (Layer 3)
class CurveRouter:
    def route(self, edge: Edge, obstacles: list[Rect] | None = None) -> list[Point]:
        p_start, p_end, n_src, n_tgt = self._resolve_ports_and_normals(edge)
        dist = math.hypot(p_end.x - p_start.x, p_end.y - p_start.y)
        handle_len = max(40.0, min(160.0, dist * 0.45))
        
        c1 = Point(p_start.x + n_src.x * handle_len, p_start.y + n_src.y * handle_len)
        c2 = Point(p_end.x + n_tgt.x * handle_len, p_end.y + n_tgt.y * handle_len)
        
        candidate = [p_start, c1, c2, p_end]
        if not obstacles or not self._has_collision(candidate, obstacles):
            return candidate
        return self._route_deflected(p_start, p_end, n_src, n_tgt, obstacles)

# In renderer_svg.py (Layer 4)
def _format_svg_path(edge: Edge, pts: list[Point]) -> str:
    if edge.routing == Routing.CURVE and len(pts) == 4:
        p0, c1, c2, p3 = pts
        return f"M {p0.x} {p0.y} C {c1.x} {c1.y}, {c2.x} {c2.y}, {p3.x} {p3.y}"
    # ...
```

### Pattern 2: Waypoint Representation Compatibility (`list[Point]`)

**What:** Store curve control points and waypoints within the existing `edge.waypoints: list[Point]` and `diagram.routes: dict[int, list[Point]]` structures.  
- For a single cubic Bezier: `[P_start, C_1, C_2, P_end]` (length 4).  
- For a multi-segment spline of $k$ segments: $1 + 3k$ points ($[P_0, C_1, C_2, P_1, C_3, C_4, P_2, \dots]$).  
- For orthogonal paths: `[P_0, P_1, \dots, P_n]` corner vertices (filleted on the fly during SVG generation according to `edge.arc_radius`).  
**When to use:** Universal edge waypoint storage across all routing modes.  
**Trade-offs:** 100% backward compatibility with existing tests and sidecar layout files. Callers expecting `list[Point]` never break. `CubicBezier` helper can be instantiated on demand: `CubicBezier(*pts[0:4])`.

**Example:**
```python
# Instantiating helper from points when needed
curve = CubicBezier(p0=pts[0], c1=pts[1], c2=pts[2], p3=pts[3])
midpoint = curve.point_at(0.5)  # Exact location for protocol badge
```

### Pattern 3: Rounded Corner Fillets via SVG Quadratic Beziers (`Q`)

**What:** On orthogonal paths with `arc_radius > 0`, replace each 90° bend at vertex $P_i$ with an arc starting at $P_i - r \hat{u}_{in}$ and ending at $P_i + r \hat{u}_{out}$, where $r = \min(R, L_{in}/2, L_{out}/2)$. Use SVG command `Q {P_i.x} {P_i.y} {end.x} {end.y}`.  
**When to use:** `Routing.ORTHOGONAL` when `edge.arc_radius > 0`.  
**Trade-offs:**  
- Quadratic Bezier `Q` with the control point placed at the original corner vertex $P_i$ is tangent to both incoming and outgoing line segments.  
- It creates a perfectly smooth $C^1$ fillet without circular arc flag bugs (`sweep-flag`, `large-arc-flag`).  
- It degrades cleanly to sharp corners when `arc_radius == 0` or segments are too short.

**Example:**
```python
def render_filleted_path(pts: list[Point], arc_radius: float) -> str:
    if len(pts) < 3 or arc_radius <= 0.0:
        return f"M {pts[0].x} {pts[0].y} " + " ".join(f"L {p.x} {p.y}" for p in pts[1:])
    
    parts = [f"M {pts[0].x} {pts[0].y}"]
    for i in range(1, len(pts) - 1):
        prev_p, curr_p, next_p = pts[i - 1], pts[i], pts[i + 1]
        v_in = Point(curr_p.x - prev_p.x, curr_p.y - prev_p.y)
        v_out = Point(next_p.x - curr_p.x, next_p.y - curr_p.y)
        l_in = math.hypot(v_in.x, v_in.y)
        l_out = math.hypot(v_out.x, v_out.y)
        if l_in == 0 or l_out == 0:
            continue
        u_in = Point(v_in.x / l_in, v_in.y / l_in)
        u_out = Point(v_out.x / l_out, v_out.y / l_out)
        
        r = min(arc_radius, l_in / 2.0, l_out / 2.0)
        p_start_arc = Point(curr_p.x - u_in.x * r, curr_p.y - u_in.y * r)
        p_end_arc = Point(curr_p.x + u_out.x * r, curr_p.y + u_out.y * r)
        
        parts.append(f"L {p_start_arc.x} {p_start_arc.y}")
        parts.append(f"Q {curr_p.x} {curr_p.y} {p_end_arc.x} {p_end_arc.y}")
        
    parts.append(f"L {pts[-1].x} {pts[-1].y}")
    return " ".join(parts)
```

### Pattern 4: Cascading Routing Configuration

**What:** Allow setting routing defaults at the `Diagram` level (`Diagram(routing="curve", arc_radius=8.0)`), inherited by fluent connections (`s1 >> s2`), while supporting granular per-edge overrides (`s1 >> diag.edge(routing="orthogonal", arc_radius=0) >> s2`).  
**When to use:** Diagram definition and connection building.  
**Trade-offs:** Provides global aesthetic control with zero repetition, while preserving surgical edge-level customization.

---

## Data Flow

### Edge Routing & Rendering Flow

```
[Diagram Specification]
    │  Diagram(routing="curve", arc_radius=8.0)
    │  s1 >> s2  (inherits diagram defaults)
    ▼
[Diagram.solve() -> layout/pipeline.run_layout]
    │  1. Solve node constraints & group boundaries
    │  2. Frame canvas & grow boundaries
    │  3. For each edge in diagram.edges:
    │         EdgeRouter.route(edge, obstacles=elements)
    ▼
[EdgeRouter]
    ├── If edge.routing == Routing.DIRECT:
    │       return [p_start, p_end]
    ├── If edge.routing == Routing.ORTHOGONAL:
    │       OrthogonalRouter.route(edge, obstacles)
    │       return [P0, P1, ..., Pn] (sharp corner vertices)
    └── If edge.routing == Routing.CURVE:
            CurveRouter.route(edge, obstacles)
            return [P_start, C1, C2, P_end] (or multi-segment spline)
    ▼
[diagram.routes & edge.waypoints populated]
    ▼
[renderer_svg.SVGRenderer.render]
    ├── Format SVG path `d` string:
    │     - If Routing.CURVE: `M p0 C c1, c2, p3`
    │     - If Routing.ORTHOGONAL & arc_radius > 0: `M...L...Q...L...`
    │     - Else: `M...L...`
    └── Position badge label:
          - If Routing.CURVE: evaluate CubicBezier.point_at(0.5)
          - Else: midpoint between pts[mid - 1] and pts[mid]
```

### Key Data Flows

1. **Routing Resolution Flow:** `Diagram.solve()` collects positioned element bounding boxes as obstacles. `EdgeRouter` resolves cardinal ports based on relative bounding box positions. For `Routing.CURVE`, port normal vectors calculate initial control points $C_1, C_2$.
2. **Obstacle Collision & Deflection Flow:** `CurveRouter` checks if the candidate Bezier curve intersects any obstacle rectangle. If collision occurs, `CurveRouter` finds an avoidance waypoint $W$ around the obstacle clearance corridor and generates a 2-segment cubic Bezier spline with $C^1$ continuity at $W$.
3. **SVG Rendering Flow:** `SVGRenderer` inspects `edge.routing` and `edge.arc_radius`. It formats the SVG `<path d="..." />` element using `C` or `Q` commands, places protocol badges at the exact geometric midpoint, and adds marker arrowheads.

---

## Detailed Integration Points

### 1. `diagrams_as_code/geometry.py` (Layer 0)

- **Status:** Modified
- **New Additions:**
  - `CubicBezier` frozen dataclass:
    - Attributes: `p0: Point`, `c1: Point`, `c2: Point`, `p3: Point`
    - Methods:
      - `point_at(t: float) -> Point`: Evaluates cubic Bernstein polynomial at $t$.
      - `tangent_at(t: float) -> Point`: First derivative vector $B'(t)$.
      - `bbox() -> Rect`: Tight axis-aligned bounding box around the curve.
      - `sample(num_samples: int = 12) -> list[Point]`: Generates polyline approximation for collision testing.

### 2. `diagrams_as_code/connections.py` (Layer 2)

- **Status:** Modified
- **Changes:**
  - `Routing` enum already contains `CURVE = "curve"`.
  - Update `Edge.__init__`:
    - Add `arc_radius: Optional[float] = None` parameter (defaults to `0.0` if `None`).
    - Change `routing: Optional[Union[Routing, str]] = None` (defaults to `Routing.ORTHOGONAL` when standalone).
    - Store `self.arc_radius: float = float(arc_radius or 0.0)`.
    - Ensure `self.waypoints: Optional[list[Point]] = None` stores calculated curve control points or orthogonal waypoints.

### 3. `diagrams_as_code/router.py` (Layer 3)

- **Status:** Modified
- **Changes:**
  - Define `PORT_NORMALS`:
    - `Port.EAST: Point(1.0, 0.0)`
    - `Port.WEST: Point(-1.0, 0.0)`
    - `Port.SOUTH: Point(0.0, 1.0)`
    - `Port.NORTH: Point(0.0, -1.0)`
  - Add `CurveRouter`:
    - `resolve_ports(edge: Edge) -> tuple[Port, Port]`
    - `route(edge: Edge, obstacles: Optional[Iterable[Any]] = None, clearance: float = 15.0) -> list[Point]`
    - Calculates control points $C_1, C_2$ along port outward normals.
    - Samples curve to test intersection with obstacle bounding boxes.
    - If obstructed, calculates detour waypoint $W$ outside obstacle clearance box and builds a 2-segment cubic spline $(P_0 \to W \to P_3)$ preserving tangent smoothness at $W$.
  - Update `OrthogonalRouter`:
    - Retain existing Manhattan routing and A* detour logic.
    - When `edge.routing == Routing.CURVE`, delegate to `CurveRouter.route(edge, obstacles, clearance)`.
  - Add `EdgeRouter`:
    - Dispatches cleanly to `DIRECT`, `OrthogonalRouter`, or `CurveRouter`.

### 4. `diagrams_as_code/layout/pipeline.py` (Layer 4)

- **Status:** Modified
- **Changes:**
  - In `run_layout(diagram)`:
    - Replace `router = OrthogonalRouter()` with `router = EdgeRouter()` (or keep `OrthogonalRouter` with curve delegation).
    - Routes all edges and stores waypoints into `edge.waypoints` and `diagram.routes[id(edge)]`.

### 5. `diagrams_as_code/renderer_svg.py` (Layer 4)

- **Status:** Modified
- **Changes:**
  - Path generation in edge rendering loop:
    - Check `edge.routing` and `edge.arc_radius`.
    - If `edge.routing == Routing.CURVE`:
      - For 4 points ($P_0, C_1, C_2, P_3$): `M {p0.x} {p0.y} C {c1.x} {c1.y}, {c2.x} {c2.y}, {p3.x} {p3.y}`.
      - For $1 + 3k$ points (multi-segment spline): chain consecutive `C` commands.
      - Badge positioning: evaluate `CubicBezier(pts[0], pts[1], pts[2], pts[3]).point_at(0.5)`.
    - If `edge.routing == Routing.ORTHOGONAL`:
      - If `edge.arc_radius > 0`: format rounded corner fillets using `Q` quadratic bezier arcs at each corner vertex.
      - If `edge.arc_radius <= 0`: format straight orthogonal segments `M...L...`.
      - Badge positioning: midpoint of the middle segment.
    - If `edge.routing == Routing.DIRECT`:
      - Format `M {p0.x} {p0.y} L {p1.x} {p1.y}`.

### 6. `diagrams_as_code/diagram.py` (Layer 5)

- **Status:** Modified
- **Changes:**
  - In `Diagram.__init__`:
    - Add `routing: Union[Routing, str] = Routing.ORTHOGONAL`.
    - Add `arc_radius: float = 0.0`.
  - In `Diagram.configure`:
    - Accept `routing: Optional[Union[Routing, str]] = None`.
    - Accept `arc_radius: Optional[float] = None`.
  - In `Diagram.connect` and `Diagram.edge` and `_EdgeBuilder`:
    - Default to `diagram.routing` and `diagram.arc_radius` when parameters are not explicitly passed.

---

## Anti-Patterns

### Anti-Pattern 1: Calculating Bezier Control Points in the SVG Renderer

**What people do:** Let the router output only start and end points (or straight waypoints), and make `SVGRenderer` invent control points when generating SVG strings.  
**Why it's wrong:**
1. Breaks separation of concerns: the renderer should only draw what the layout pipeline solved.
2. Obstacle avoidance cannot work: the renderer has no concept of collision detection, detour channels, or clearance margins.
3. Untestable geometry: testing curve shapes requires parsing raw SVG strings rather than checking coordinate math.
4. Breaks badge/label alignment: the label badge must sit precisely on the curve, which requires knowing the exact mathematical polynomial.  
**Do this instead:** The router computes all control points and avoidance waypoints during `solve()`, attaching them to `edge.waypoints`. The renderer strictly emits SVG commands.

### Anti-Pattern 2: Replacing `list[Point]` with Incompatible Path Objects in `edge.waypoints`

**What people do:** Change `edge.waypoints` to a list of heterogeneous SVG command strings or custom class instances that do not behave like `Point` objects.  
**Why it's wrong:** Breaks existing public and internal contracts (`assert edge.waypoints == OrthogonalRouter().route(edge)`, JSON layout export, route caching in `diagram.routes`).  
**Do this instead:** Keep `edge.waypoints` as a `list[Point]`. For a cubic Bezier, `waypoints` contains $[P_0, C_1, C_2, P_3]$. Provide a `CubicBezier` helper in `geometry.py` to wrap those points when mathematical evaluation is required.

### Anti-Pattern 3: Using Elliptical Arcs (`A`) with Hardcoded Sweep Flags for Fillets

**What people do:** Attempt to construct SVG `A` path commands without handling all 8 possible 90-degree corner orientations and direction reversals, leading to flipped arc bulbs.  
**Why it's wrong:** SVG `A` commands require 7 parameters (`rx, ry, x-axis-rotation, large-arc-flag, sweep-flag, x, y`). If direction vectors are flipped, the arc bows outward into an inverted loop instead of a rounded fillet.  
**Do this instead:** Use SVG quadratic Bezier commands `Q {curr.x} {curr.y} {end.x} {end.y}` where the control point is simply the corner vertex $P_i$. It is mathematically symmetric, tangent to both legs, and physically impossible to flip.

---

## Scaling Considerations

| Diagram Scale | Performance Impact | Architectural Adjustments |
|---------------|--------------------|---------------------------|
| 1–50 edges | < 5 ms total routing time | Direct cubic Bezier calculation and 12-point collision sampling run instantly. |
| 50–500 edges | 10–50 ms total routing time | Bounding box pre-check before curve sampling eliminates 95% of obstacle checks in $O(1)$. |
| 500+ edges | 50–200 ms total routing time | Detour channel caching and spatial grid pruning avoid redundant A* searches. Monolithic pure-Python remains fast. |

### Scaling Priorities

1. **First bottleneck:** Obstacle collision detection when every curve tests against every element bounding box ($O(E \times N)$). Fix with axis-aligned bounding box (AABB) broad-phase rejection before fine curve sampling.
2. **Second bottleneck:** Multi-segment spline detour search when multiple obstacles block direct line of sight. Fix by leveraging existing corridor grid from `OrthogonalRouter._find_detour_path`.

---

## Suggested Build Order

1. **Phase 1: Geometry & Connection Primitives**
   - Implement `CubicBezier` in `diagrams_as_code/geometry.py`.
   - Add `arc_radius` to `Edge` in `diagrams_as_code/connections.py`.
   - Add unit tests for `CubicBezier` (point evaluation, tangent, bounding box) in `tests/test_geometry.py`.
   - Verify boundary tests pass (`uv run pytest tests/test_module_boundaries.py`).

2. **Phase 2: Curved Routing Engine**
   - Implement `CurveRouter` in `diagrams_as_code/router.py`:
     - Port normal resolution and handle length calculations.
     - Candidate Bezier generation.
     - Collision detection against obstacle rects.
     - Obstacle deflection and intermediate avoidance waypoints.
   - Unify routing dispatch via `EdgeRouter` (and preserve `OrthogonalRouter` interface).
   - Add comprehensive routing tests in `tests/test_routing.py`.

3. **Phase 3: SVG Renderer Enhancements**
   - Update `SVGRenderer` in `diagrams_as_code/renderer_svg.py`:
     - Implement cubic Bezier SVG path generation (`M...C...`).
     - Implement rounded corner fillets (`M...L...Q...L...`) when `edge.arc_radius > 0`.
     - Implement curve midpoint badge label positioning via `CubicBezier.point_at(0.5)`.
   - Add rendering unit tests in `tests/test_renderer_svg.py`.

4. **Phase 4: Diagram & Fluent API Integration**
   - Update `Diagram` and `_EdgeBuilder` in `diagrams_as_code/diagram.py`:
     - Add `routing` and `arc_radius` parameters to `Diagram.__init__` and `Diagram.configure`.
     - Cascade diagram-level defaults down to `connect()`, `edge()`, and `>>` operator.
   - Update `diagrams_as_code/layout/pipeline.py` to route all edges using the unified router.
   - Add end-to-end and API integration tests in `tests/test_diagram_api.py` and `tests/test_layout_routes.py`.

5. **Phase 5: Domain Gallery & Documentation**
   - Verify all 88 domain example diagrams render cleanly with zero regressions.
   - Add curved and filleted examples to documentation and gallery.

---

## Sources

- SVG 1.1 Specification (W3C), Section 8.3: The "C" (cubic Bézier curve) and "Q" (quadratic Bézier curve) commands.
- Mortenson, M. E., *Geometric Modeling*, 3rd Edition (Bézier curves, Bernstein basis, and continuity).
- Graphviz `dot` Spline Routing Architecture (tangent matching and obstacle avoidance corridors).
- Existing `diagrams-as-code` codebase (`geometry.py`, `connections.py`, `router.py`, `renderer_svg.py`, `layout/pipeline.py`).
