# Phase 9: Rounded Corner Fillets for Orthogonal Routing - Research

**Domain:** Vector Geometry, Orthogonal Fillets & Native SVG Quadratic Bezier Path Generation (Pure Python Standard Library)  
**Researched:** 2026-09-26  
**Confidence:** HIGH  

---

<user_constraints>
## User Constraints (from 09-CONTEXT.md)

### Implementation Decisions

#### API Parameter & Default Behavior
- **D-01:** Support `corner_radius` as the primary attribute on `Edge` and `Diagram`, with `arc_radius` accepted as a fully-supported alias. `Diagram(corner_radius=...)` cascades as default for all orthogonal edges in the diagram; individual `Edge(corner_radius=...)` overrides the diagram default.
- **D-02:** Sharp corners by default (`corner_radius=0.0` or `None`), preserving 100% backward compatibility and zero visual diff across all 88 gallery diagrams and existing tests unless explicitly configured.
- **D-03:** `corner_radius` applies strictly to `Routing.ORTHOGONAL` edges. If configured on `Routing.DIRECT` or `Routing.CURVE`, it is gracefully ignored without raising an error.
- **D-04:** Input validation: Coerce int/float inputs to `float`. Raise `ValueError` if `corner_radius < 0.0` or non-numeric (strict defensive validation).

#### Fillet Radius Clamping & Short Segments
- **D-05:** Strict 50% segment budget: For each corner $P_i$, $R_{\text{effective}} = \min(R, L_{\text{in}} / 2.0, L_{\text{out}} / 2.0)$ where $L_{\text{in}} = \|P_i - P_{i-1}\|$ and $L_{\text{out}} = \|P_{i+1} - P_i\|$. Adjacent corners on a shared segment each receive up to 50% of the segment length, preventing inverted arcs or overlaps.
- **D-06:** Minimum threshold suppression: If $R_{\text{effective}} < 2.0\text{px}$, suppress the fillet for that specific corner and render a sharp 90-degree corner, preventing sub-pixel rasterization artifacts and micro-arcs.
- **D-07:** Orthogonal turn detection: Fillet is applied strictly to 90-degree orthogonal turns where $\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}} = 0$ (within numerical tolerance $10^{-6}$). Collinear segments continue straight, and turnarounds remain linear.
- **D-08:** Endpoint straight lead-in: Segments adjacent to source and target ports enforce a minimum straight lead-in of at least $10.0\text{px}$ (or $L / 2$ if shorter), ensuring edges depart and arrive strictly perpendicular to node bounds and arrowheads rest on clean linear segments without curvature distortion.

#### SVG Path Generation & Mathematical Contract
- **D-09:** SVG path syntax: Emit quadratic Bezier commands `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y` where $P_c$ is the corner control point, and $T_1, T_2$ are tangent points on the incoming and outgoing segments, directly fulfilling requirement FILLET-03 with $C^1$ continuity.
- **D-10:** Layer 0 primitive: Implement `geometry.QuadraticBezier(p0, p1, p2)` in `src/diagrams_as_code/geometry.py` as an immutable frozen dataclass with `point_at(t)`, `tangent_at(t)`, `bbox()`, and `arc_length()`, exported in `diagrams_as_code` and facade `iiot_diagrams`.
- **D-11:** Waypoint data contract: `Edge.waypoints` remains the clean sequence of sharp Manhattan corner vertices `[P_0, P_1, ..., P_n]`. Fillet tangent point calculation and `Q` command generation is performed in Layer 4 during SVG path generation, preserving layout JSON serialization, collision tests, and backward compatibility.
- **D-12:** Protocol badge placement: Keep existing orthogonal badge positioning on the midpoint of the longest straight segment, ensuring badges remain horizontal, highly readable, and on flat straight line segments rather than straddling corner bends.

#### Obstacle Avoidance & Clearance Integration
- **D-13:** Uniform filleting: Apply corner filleting uniformly across both default Manhattan paths and obstacle-avoidance detour paths for consistent visual style across all orthogonal edges.
- **D-14:** Obstacle clearance guard: When rounding corners near obstacles, clamp $R_{\text{effective}}$ such that the fillet apex preserves a minimum clearance margin of at least $4.0\text{px}$ from any obstacle bounding box, preventing curved paths from clipping obstacle corners.
- **D-15:** Performance optimization: Analytical vector calculations $O(1)$ per corner in pure Python standard library (`math.hypot`, closed-form quadratic tangent placement), executing in sub-millisecond time per edge with zero iterative root finders.
- **D-16:** Interactive SVG compatibility: Filleted paths emit standard `<path d="M... Q..." class="edge">` elements, providing transparent, zero-code compatibility with existing interactive pan/zoom, search/highlighting, and viewport minimap navigation.

### Claude's Discretion
- Internal helper structure in `renderer_svg.py` (e.g. `_render_filleted_path` helper function) vs `router.py`.
- Exact numerical tolerance for orthogonality detection (`1e-6`).

### Deferred Ideas
- None — discussion stayed within phase scope.

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| Requirement ID | Summary | Architectural Mapping | Research Finding & Solution |
|----------------|---------|------------------------|-----------------------------|
| **FILLET-01** | User can configure `corner_radius` (or `arc_radius`) on orthogonal edges to produce rounded 90-degree corner bends. | `connections.py` (Layer 2), `diagram.py` (Layer 5), `renderer_svg.py` (Layer 4) | Support `corner_radius` as primary attribute on `Edge` and `Diagram`, with `arc_radius` accepted as a fully-supported alias. `Diagram(corner_radius=...)` cascades default radius to all orthogonal edges, while individual `Edge(corner_radius=...)` takes precedence (D-01). Default is sharp corners (`corner_radius=0.0` or `None`), preserving 100% backward compatibility (D-02). Ignored gracefully on `Routing.DIRECT` and `Routing.CURVE` (D-03). Validates non-negative float inputs (D-04). |
| **FILLET-02** | Corner filleting dynamically clamps radius per corner to $\min(R, L_1/2, L_2/2)$ so short segments never invert, create "dog ears", or overlap. | `renderer_svg.py` (Layer 4) `_render_filleted_path` | Implements closed-form 50% segment budgeting: $R_{\text{effective}} = \min(R, L_{\text{in}}/2, L_{\text{out}}/2)$ (D-05). Enforces port straight lead-in of at least $\min(10.0, L/2)$ on segments entering/exiting ports (D-08). Suppresses micro-arcs $< 2.0\text{px}$ to sharp corners (D-06). Only 90° orthogonal turns are filleted ($|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$), keeping collinear lines and turnarounds linear (D-07). Clamps apex to maintain $\ge 4.0\text{px}$ clearance from obstacle bounding boxes (D-14). |
| **FILLET-03** | SVG renderer emits quadratic Bezier (`Q`) commands connecting corner fillet tangent points for $C^1$-continuous smooth bends. | `geometry.py` (Layer 0) `QuadraticBezier`, `renderer_svg.py` (Layer 4) | Emits SVG syntax `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y` where $P_c$ is original corner vertex, $T_1 = P_c - \mathbf{u}_{\text{in}} R_{\text{eff}}$, $T_2 = P_c + \mathbf{u}_{\text{out}} R_{\text{eff}}$ (D-09). Using $P_c$ as the control point guarantees $C^1$ tangent continuity: $B'(0) = 2(P_c - T_1) = 2 R \mathbf{u}_{\text{in}}$ and $B'(1) = 2(T_2 - P_c) = 2 R \mathbf{u}_{\text{out}}$. Evaluates Layer 0 `QuadraticBezier` primitive with analytical bounding box and arc length (D-10). Keeps `Edge.waypoints` clean as sharp Manhattan vertices (D-11). |

</phase_requirements>

---

## Architectural Responsibility Map

The architecture strictly adheres to the 5-layer decoupled pipeline enforced by `tests/test_module_boundaries.py`. Imports point strictly downward.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 5: Diagram & Fluent API (diagram.py)                                   │
│ - Accepts corner_radius & arc_radius in Diagram.__init__() and configure()   │
│ - Cascades diagram corner_radius default down to _EdgeBuilder and connect()   │
│ - Allows individual edge override: s1 >> diag.edge(corner_radius=12.0) >> s2 │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 4: Presentation & Layout (renderer_svg.py, layout/pipeline.py)         │
│ - pipeline.py: routes edges via router; populates edge.waypoints             │
│ - Cascades diagram.corner_radius to unconfigured edges in solve()            │
│ - renderer_svg.py:                                                           │
│   * _render_filleted_path(): transforms sharp Manhattan waypoints into       │
│     M...L...Q...L... SVG path syntax with dynamic radius clamping            │
│   * Enforces 50% segment budget, port straight lead-in, and micro-arc clamp  │
│   * Obstacle clearance guard: clamps apex to >= 4.0px obstacle margin        │
│   * Retains horizontal protocol badges on straight segment midpoint (D-12)   │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 3: Routing Engine (router.py)                                          │
│ - OrthogonalRouter: Manhattan waypoints, obstacle A* corridors (unchanged)   │
│ - Waypoint contract: outputs clean sharp corner polyline [P0, ..., Pn] (D-11)│
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 2: Connections & Entities (connections.py)                             │
│ - Edge.__init__(): accepts corner_radius and alias arc_radius                │
│ - Coerces int/float, strictly rejects negative or non-numeric values         │
│ - Property arc_radius proxies corner_radius getter/setter                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 0: Primitives & Math (geometry.py)                                     │
│ - QuadraticBezier: frozen dataclass (p0, p1, p2)                             │
│   * point_at(t) -> Point: Bernstein polynomial evaluation                    │
│   * tangent_at(t) -> Point: first derivative velocity vector B'(t)           │
│   * bbox() -> Rect: exact tight bounding box from derivative linear root     │
│   * arc_length(n) -> float: cumulative chord distance                        │
│   * sample(n) -> list[Point]: equidistant parameter sampling                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Standard Stack

The core engine is 100% Python standard library with zero runtime dependencies (`dependencies = []` in `pyproject.toml`).

| Technology | Standard Library Module | Purpose | Rationale / Performance |
|------------|-------------------------|---------|-------------------------|
| **Arithmetic & Geometry** | `math` | `math.hypot`, `math.isclose`, `math.isnan`, `math.isinf` | Hardware-accelerated IEEE 754 arithmetic with zero external C dependencies. Safe Euclidean distances and float comparisons. |
| **Immutable Value Objects** | `dataclasses` | `@dataclass(frozen=True)` for `QuadraticBezier` | Zero-overhead value semantics, structural equality, hashability, and full IDE auto-complete. |
| **Sequence Processing** | `itertools` / indexing | Triplet corner iteration $(P_{i-1}, P_i, P_{i+1})$ | Processing adjacent incoming and outgoing segments along Manhattan waypoints. |
| **Type Contracts** | `typing` | `Optional`, `Union`, `Sequence`, `Mapping` | Strict static typing compliant with PEP 585 and PEP 604. |
| **Vector Output Syntax** | W3C SVG 1.1 / 2.0 | `<path d="M... L... Q... L...">` | Universal vector format natively supported by all browsers and headless rasterizers (`resvg-py`). |
| **Dev Rasterizer** | `resvg-py` | Development dependency only (`dependency-groups.dev`) | Headless Rust-based SVG rasterizer for visual regression tests and PNG output validation. Never imported at runtime. |

---

## Architecture Patterns

### Pattern 1: Waypoint Preservation Contract (`Edge.waypoints`)
**Rule:** `Edge.waypoints` remains strictly the clean sequence of sharp Manhattan corner vertices `[P_0, P_1, ..., P_n]` produced by `OrthogonalRouter`.
- Fillet tangent point calculation and `Q` command generation is performed strictly in Layer 4 (`renderer_svg.py`) during SVG path formatting.
- **Why:** Preserves 100% backward compatibility with layout file JSON serialization (`export_layout`), collision detection, downstream consumers, and existing tests asserting `edge.waypoints`.

### Pattern 2: Quadratic Bezier Tangent Geometry ($P_c$ Control Point)
**Rule:** For a 90-degree corner at vertex $P_c$ with effective radius $R_{\text{eff}}$:
- Tangent point on incoming segment: $T_1 = P_c - \mathbf{u}_{\text{in}} \cdot R_{\text{eff}}$
- Tangent point on outgoing segment: $T_2 = P_c + \mathbf{u}_{\text{out}} \cdot R_{\text{eff}}$
- Control point: $P_1 = P_c$
- Path command: `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y`
- **Why:**
  1. The quadratic Bezier $B(t) = (1-t)^2 T_1 + 2(1-t)t P_c + t^2 T_2$ has derivative $B'(0) = 2(P_c - T_1) = 2 R_{\text{eff}} \mathbf{u}_{\text{in}}$ and $B'(1) = 2(T_2 - P_c) = 2 R_{\text{eff}} \mathbf{u}_{\text{out}}$.
  2. Because the derivatives match the incoming and outgoing line directions exactly, the curve possesses guaranteed $C^1$ tangent continuity.
  3. Unlike circular arcs (`A` command), quadratic Bezier fillets require zero sweep flags or large-arc flags, eliminating arc-flipping bugs entirely.

### Pattern 3: Dynamic 50% Budget Clamping + Port Lead-In
**Rule:** For each corner $P_i$ ($i \in [1, n-1]$):
1. **50% Segment Budget:** $R_{\text{eff}} \le \min(R, L_{\text{in}} / 2.0, L_{\text{out}} / 2.0)$. Adjacent corners sharing a segment never compete or overlap.
2. **Port Straight Lead-In:**
   - For $i = 1$ (incoming segment originates at source port $P_0$): straight lead-in $\ge \min(10.0, L_{\text{in}} / 2.0)$ leaves available radius $\min(L_{\text{in}} / 2.0, L_{\text{in}} - \min(10.0, L_{\text{in}} / 2.0))$.
   - For $i = n - 1$ (outgoing segment terminates at target port $P_n$): straight lead-in $\ge \min(10.0, L_{\text{out}} / 2.0)$ leaves available radius $\min(L_{\text{out}} / 2.0, L_{\text{out}} - \min(10.0, L_{\text{out}} / 2.0))$.
   - **Why:** Arrowheads at target ports and edge origins at source ports rest on clean, perpendicular linear segments. Arrowheads never appear tilted or distorted.

### Pattern 4: Sub-pixel Threshold Suppression
**Rule:** If the clamped radius for a corner satisfies $R_{\text{eff}} < 2.0\text{px}$, suppress the fillet for that specific corner and emit a sharp 90-degree corner (`L P_i.x P_i.y`).
- **Why:** Prevents sub-pixel rasterization fuzziness, degenerate micro-curves, and numerical noise on tiny routing jogs.

### Pattern 5: Strict 90° Orthogonal Turn Detection
**Rule:** Apply filleting only if $|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$.
- If dot product is close to $1.0$ (collinear points) or $-1.0$ (180° turnaround), do not emit a fillet curve; continue straight or linear.
- **Why:** Protects against division by zero and malformed geometry when waypoints contain redundant collinear vertices or turnarounds.

### Pattern 6: Obstacle Clearance Apex Clamping
**Rule:** The apex of the quadratic Bezier fillet occurs at $t = 0.5$:
$$P_{\text{apex}}(R) = \frac{T_1 + 2P_c + T_2}{4} = P_c - 0.25 R (\mathbf{u}_{\text{in}} - \mathbf{u}_{\text{out}})$$
Because $\mathbf{u}_{\text{in}} and \mathbf{u}_{\text{out}}$ are orthogonal unit vectors, the apex vector $\mathbf{d} = -0.25 (\mathbf{u}_{\text{in}} - \mathbf{u}_{\text{out}})$ has coordinates $(\pm 0.25, \pm 0.25)$ directed toward the inside corner.
- When an obstacle is on the inside of the turn, clamp $R_{\text{eff}}$ so that $P_{\text{apex}}$ does not enter any obstacle `Rect` expanded by $4.0\text{px}$.
- **Why:** Prevents rounded corner cuts from clipping into obstacle cards when navigating tight clearance corridors.

### Pattern 7: Parameter Cascading and Dual Alias API
**Rule:** Support `corner_radius` as primary and `arc_radius` as alias:
- In `Edge.__init__`: accepts `corner_radius` or `arc_radius`. Provides `.corner_radius` attribute and `.arc_radius` property.
- In `Diagram.__init__` and `Diagram.configure`: accepts `corner_radius` or `arc_radius`.
- In `Diagram.edge` and `_EdgeBuilder`: defaults to `diagram.corner_radius` if unset.
- In `Diagram.solve()` / `run_layout()`: edges with `corner_radius is None` inherit `diagram.corner_radius`.

---

## Don't Hand-Roll

| Problem | Anti-Pattern to Avoid | Standard Library / Deterministic Approach |
|---------|-----------------------|-------------------------------------------|
| **Corner Fillet Geometry** | SVG Circular Arc (`A rx ry 0 large-arc sweep x y`) | SVG Quadratic Bezier (`Q P_c.x P_c.y T2.x T2.y`). The corner vertex $P_c$ serves directly as the control point, eliminating sweep flag inversion bugs and trigonometric center-radius conversions. |
| **Quadratic Curve Math** | Adding external geometry libraries (Shapely, SciPy) | Direct Bernstein polynomial evaluation in Layer 0 (`geometry.QuadraticBezier`): $B(t) = (1-t)^2 P_0 + 2(1-t)t P_1 + t^2 P_2$. Under 20 lines of pure Python standard library. |
| **Short Segment Budgeting** | Fixed fillet radius $R$ without clamping | Dynamic per-corner clamping: $R_{\text{eff}} = \min(R, L_{\text{in}} / 2.0, L_{\text{out}} / 2.0)$. Prevents inverted arc "dog ears" and crossing loops. |
| **Sub-pixel Artifacts** | Rounding every corner regardless of size | Threshold suppression: if $R_{\text{eff}} < 2.0\text{px}$, drop radius to 0 and emit sharp `L` command. |
| **Arrowhead Straightness** | Filleting right up to port anchor ($P_0$ or $P_n$) | Enforce straight lead-in $\ge \min(10.0, L/2)$. Arrowhead sits on flat orthogonal segment, keeping rotation perpendicular to shape walls. |
| **Data Contract Integrity** | Modifying `Edge.waypoints` to store fillet arcs or Q commands | Keep `Edge.waypoints` as clean `list[Point]` Manhattan corners. Decompose fillets during SVG path string formatting in `renderer_svg.py`. |

---

## Common Pitfalls & Mitigations

### Pitfall 1: Fillet Arc Inversion & "Dog Ears" on Short Segments
- **Failure:** Fixed radius $R=15\text{px}$ on an 18px segment between two 90° bends causes adjacent fillets to request $15 + 15 = 30\text{px} > 18\text{px}$. The tangent points cross over, producing inverted triangular loops ("dog ears") in the SVG path.
- **Mitigation:** Strict 50% segment budget: each corner is clamped to $\min(R, L_{\text{in}}/2, L_{\text{out}}/2)$. For $L=18\text{px}$, each corner gets at most $9\text{px}$, leaving 0px overlap and exact tangency meeting at the segment midpoint.

### Pitfall 2: Sub-pixel Micro-Arcs Causing Rendering Artifacts
- **Failure:** On very short routing jogs (e.g. $L=3\text{px}$), clamping yields $R=1.5\text{px}$. SVG rasterizers produce blurred or distorted anti-aliasing artifacts on sub-pixel curves.
- **Mitigation:** If $R_{\text{eff}} < 2.0\text{px}$, suppress the fillet and emit a clean sharp corner `L P_i.x P_i.y`.

### Pitfall 3: Arrowhead Diagonal Slant from Port Anchor Curvature
- **Failure:** Filleting the corner immediately adjacent to a target port curves the path right up to the port anchor, rotating the arrowhead marker away from normal ($90^\circ$).
- **Mitigation:** Segments adjacent to ports enforce a straight lead-in of at least $\min(10.0, L/2)$. The final $10\text{px}$ entering the port is strictly linear, ensuring the arrowhead marker with `orient="auto-start-reverse"` seats squarely against the flat card wall.

### Pitfall 4: Collinear Points and 180° Turnarounds
- **Failure:** Redundant collinear points or 180° hairpin turns cause division by zero in unit vector normalization or produce degenerate quadratic curves.
- **Mitigation:** Test orthogonality with $|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$ and check $L_{\text{in}} > 10^{-6}, L_{\text{out}} > 10^{-6}$. Only genuine 90° turns receive fillets; collinear points continue straight.

### Pitfall 5: Obstacle Corner Clipping from Inside-Turn Fillet Apex
- **Failure:** When an edge turns tightly around an obstacle card, the sharp corner cleared the card by 15px, but the rounded fillet apex cuts inside the corner and clips the obstacle's bounding box.
- **Mitigation:** Calculate the apex coordinate $P_{\text{apex}}(R) = P_c - 0.25 R (\mathbf{u}_{\text{in}} - \mathbf{u}_{\text{out}})$. Clamp $R$ such that $P_{\text{apex}}$ maintains a clearance margin of at least $4.0\text{px}$ from all obstacle bounding boxes.

### Pitfall 6: Public API Desynchronization (`corner_radius` vs `arc_radius`)
- **Failure:** User passes `corner_radius=10.0` or `arc_radius=10.0`, but one is ignored or raises an attribute error; or diagram default fails to cascade to edges created via `s1 >> s2`.
- **Mitigation:** Support both names symmetrically. `corner_radius` is primary; `arc_radius` is a property alias. Diagram defaults cascade to `_EdgeBuilder` and unconfigured edges in `Diagram.solve()`.

### Pitfall 7: Waypoints Polyline Data Model Breakdown
- **Failure:** Generating fillet points into `Edge.waypoints` changes waypoint count, breaks JSON sidecar export, and triggers unexpected test failures in existing tests asserting `len(edge.waypoints) == 4`.
- **Mitigation:** `Edge.waypoints` strictly stores sharp Manhattan vertices. Fillet path generation is isolated to `renderer_svg.py`.

---

## Code Examples

### 1. Layer 0: `QuadraticBezier` Primitive (`geometry.py`)

```python
# In src/diagrams_as_code/geometry.py
@dataclass(frozen=True)
class QuadraticBezier:
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
        """Evaluate first derivative velocity vector B'(t)."""
        it = 1.0 - t
        vx = 2.0 * it * (self.p1.x - self.p0.x) + 2.0 * t * (self.p2.x - self.p1.x)
        vy = 2.0 * it * (self.p1.y - self.p0.y) + 2.0 * t * (self.p2.y - self.p1.y)
        return Point(vx, vy)

    def bbox(self) -> Rect:
        """Compute exact tight axis-aligned bounding box using derivative roots."""
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

    def sample(self, n: int = 16) -> list[Point]:
        """Uniform parameter sampling at t = i / (n - 1) for i in [0, n-1]."""
        if n < 2:
            return [self.p0, self.p2]
        return [self.point_at(i / (n - 1)) for i in range(n)]

    def arc_length(self, num_samples: int = 16) -> float:
        """Compute approximate curve arc length via piecewise chord lengths."""
        num_samples = max(1, num_samples)
        pts = self.sample(num_samples + 1)
        return sum(pts[i].distance_to(pts[i + 1]) for i in range(len(pts) - 1))
```

### 2. Layer 2: `Edge` Configuration & Validation (`connections.py`)

```python
# In src/diagrams_as_code/connections.py
class Edge:
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
        # ... existing initialization ...
        
        # Primary parameter and alias resolution (D-01)
        effective_r = corner_radius if corner_radius is not None else arc_radius
        self._corner_radius: Optional[float] = self._validate_corner_radius(effective_r)

    @staticmethod
    def _validate_corner_radius(val: Optional[Union[int, float]]) -> Optional[float]:
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
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, val: Optional[Union[int, float]]) -> None:
        self._corner_radius = self._validate_corner_radius(val)

    @property
    def arc_radius(self) -> Optional[float]:
        """Backward-compatible alias for corner_radius."""
        return self.corner_radius

    @arc_radius.setter
    def arc_radius(self, val: Optional[Union[int, float]]) -> None:
        self.corner_radius = val
```

### 3. Layer 4: Filleted Path Generation Engine (`renderer_svg.py`)

```python
# In src/diagrams_as_code/renderer_svg.py
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
    seg_vecs: list[Point] = []
    seg_lens: list[float] = []
    seg_units: list[Point] = []
    for j in range(n - 1):
        v = Point(pts[j + 1].x - pts[j].x, pts[j + 1].y - pts[j].y)
        l = math.hypot(v.x, v.y)
        seg_vecs.append(v)
        seg_lens.append(l)
        seg_units.append(Point(v.x / l, v.y / l) if l > 1e-6 else Point(0.0, 0.0))

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
            continue  # Collinear or non-orthogonal, leave sharp

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
                apex = Point(p_c.x + r_corner * dx_apex, p_c.y + r_corner * dy_apex)
                if exp.left < apex.x < exp.right and exp.top < apex.y < exp.bottom:
                    # Apex violates 4.0px obstacle margin; clamp radius
                    # Closed-form safe radius along axis entry
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

---

## Validation Architecture

Nyquist test validation ensures every requirement is programmatically verified under automated test suites.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Validation Harness                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. AST Architectural Boundary Check (tests/test_module_boundaries.py)       │
│    - geometry.py has 0 internal imports (Layer 0)                           │
│    - connections.py imports only geometry, elements (Layer 2)               │
│    - renderer_svg.py imports geometry, router, connections, theme (Layer 4) │
│                                                                             │
│ 2. Public API Mirroring Check (tests/test_public_api.py)                    │
│    - QuadraticBezier exported in diagrams_as_code.__all__                   │
│    - iiot_diagrams.__all__ strictly equals diagrams_as_code.__all__         │
│                                                                             │
│ 3. Geometric Unit Tests (tests/test_geometry.py)                            │
│    - Quadratic Bernstein polynomial point_at(t) evaluation                  │
│    - Velocity tangent derivative vectors B'(0) and B'(1)                    │
│    - Analytical linear root bbox vs numerical samples (< 1e-4)              │
│    - Immutability and frozen dataclass guarantees                           │
│                                                                             │
│ 4. Route Calculation & Contract Tests (tests/test_routing.py)               │
│    - FILLET-01: edge.waypoints preserved as sharp Manhattan vertices       │
│    - FILLET-01: corner_radius & arc_radius parameter validation             │
│    - FILLET-01: Diagram default cascading and per-edge override            │
│    - Non-negative validation: rejects negative and non-numeric inputs       │
│                                                                             │
│ 5. SVG Fillet Path Rendering Tests (tests/test_renderer_svg.py)             │
│    - FILLET-02: 50% segment budget clamping on short segments (L < 2R)      │
│    - FILLET-02: Minimum 10px straight lead-in at port anchors               │
│    - FILLET-02: Minimum threshold suppression (< 2.0px -> sharp corner)     │
│    - FILLET-02: Obstacle clearance guard (apex >= 4.0px clearance)          │
│    - FILLET-03: Emits valid SVG <path d="M... L... Q... L..."> commands    │
│    - FILLET-03: Tangent points guarantee C1 continuous transitions         │
│    - Protocol badge placement on straight segment midpoint                  │
│    - resvg-py headless rasterization test verifies zero SVG parsing errors  │
│                                                                             │
│ 6. Full Regression Suite                                                    │
│    - All 473 existing tests remain 100% green: `uv run pytest`              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Requirement-to-Test Matrix

| Requirement | Test File | Test Name | Invariants Verified |
|-------------|-----------|-----------|---------------------|
| **FILLET-01** | `tests/test_routing.py` | `test_edge_corner_radius_attributes_and_aliases` | Accepts `corner_radius` and `arc_radius`; rejects negative/non-numeric values; preserves sharp corners by default (`corner_radius=None` / `0.0`). |
| **FILLET-01** | `tests/test_diagram_api.py` | `test_diagram_corner_radius_cascade_and_override` | `Diagram(corner_radius=15.0)` cascades to unconfigured edges; individual `Edge(corner_radius=0.0)` overrides diagram default. |
| **FILLET-02** | `tests/test_renderer_svg.py` | `test_orthogonal_fillet_short_segment_budget_clamping` | For $L=18\text{px}$ and $R=15\text{px}$, each corner clamps to $9.0\text{px} \le L/2$, preventing inverted arcs or overlaps. |
| **FILLET-02** | `tests/test_renderer_svg.py` | `test_orthogonal_fillet_threshold_suppression` | Corners with $R_{\text{eff}} < 2.0\text{px}$ are suppressed to sharp 90° corners without emitting `Q` commands. |
| **FILLET-02** | `tests/test_renderer_svg.py` | `test_orthogonal_fillet_port_straight_lead_in` | Segments adjacent to ports preserve at least $\min(10.0, L/2)$ straight lead-in; arrowheads seat strictly perpendicular. |
| **FILLET-02** | `tests/test_renderer_svg.py` | `test_orthogonal_fillet_obstacle_clearance_guard` | When rounding corners near obstacles, fillet apex maintains $\ge 4.0\text{px}$ clearance from obstacle bounding boxes. |
| **FILLET-03** | `tests/test_geometry.py` | `test_quadratic_bezier_evaluation_and_bbox` | `point_at(t)`, `tangent_at(t)`, `bbox()`, and `arc_length()` execute with analytical precision in Layer 0. |
| **FILLET-03** | `tests/test_renderer_svg.py` | `test_orthogonal_fillet_svg_path_and_q_commands` | Generates `M...L...Q...L...` path with $C^1$ continuity at tangent points; parses cleanly with `xml.etree.ElementTree`. |
| **FILLET-03** | `tests/test_public_api.py` | `test_quadratic_bezier_is_exported` | `QuadraticBezier` is exported in both `diagrams_as_code` and `iiot_diagrams` facade. |

---

## Phase Execution Plan Guidance

Downstream planning agents should structure Phase 9 execution into three focused plans:

1. **Plan 09-01: Layer 0 Primitives & Layer 2/5 API Contracts**
   - Implement `QuadraticBezier` in `src/diagrams_as_code/geometry.py` (point_at, tangent_at, bbox, arc_length, sample).
   - Re-export `QuadraticBezier` in `src/diagrams_as_code/__init__.py` and `src/iiot_diagrams/__init__.py`.
   - Update `Edge` in `src/diagrams_as_code/connections.py` with `corner_radius`, `arc_radius` alias, and input validation.
   - Update `Diagram` and `_EdgeBuilder` in `src/diagrams_as_code/diagram.py` with cascading defaults.
   - Add unit tests in `tests/test_geometry.py`, `tests/test_public_api.py`, and `tests/test_routing.py`.

2. **Plan 09-02: Layer 4 SVG Fillet Path Engine**
   - Implement `_render_filleted_path` helper in `src/diagrams_as_code/renderer_svg.py`.
   - Integrate 50% segment budget clamping ($\min(R, L_{\text{in}}/2, L_{\text{out}}/2)$).
   - Enforce port straight lead-in of at least $\min(10.0, L/2)$.
   - Enforce minimum threshold suppression ($< 2.0\text{px} \implies$ sharp).
   - Enforce strict 90° orthogonal turn detection ($|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$).
   - Enforce obstacle clearance guard (apex clearance $\ge 4.0\text{px}$).
   - Integrate with `SVGRenderer._render_edges` when `edge.routing == Routing.ORTHOGONAL` and `corner_radius > 0`.
   - Maintain horizontal protocol badge placement on the longest/middle straight segment.
   - Add comprehensive rendering tests in `tests/test_renderer_svg.py`.

3. **Plan 09-03: End-to-End Integration, Diagram Cascading & Visual Regression**
   - Verify diagram-wide cascade `Diagram(corner_radius=...)` to all orthogonal edges in `layout/pipeline.py` and `diagram.py`.
   - Verify fluent connections (`s1 >> s2`) inherit diagram corner radius.
   - Test obstacle avoidance detours with uniform filleting.
   - Run complete test suite (`uv run pytest`) across all 473+ tests to guarantee 100% backward compatibility.
   - Verify headless SVG rasterization with `resvg-py`.
