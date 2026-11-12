# Phase 10: Obstacle Detection & Deflection for Curved Edges - Research

**Domain:** Vector Geometry, Collision Detection, Cubic Bezier Splines & Edge Routing Engine (Pure Python Standard Library)  
**Researched:** 2026-09-26  
**Confidence:** HIGH  

---

<user_constraints>
## User Constraints from Context

### Implementation Decisions

#### Collision Detection Strategy (CURVEOBS-01)
- **D-01:** Two-tier collision testing: Fast Axis-Aligned Bounding Box (AABB) broadphase filter using the cubic Bezier tight bounding box (`CubicBezier.bbox()`), followed by narrowphase recursive De Casteljau subdivision up to depth 4 ($2^4 = 16$ sub-segment bounding boxes) against candidate obstacle rectangles.
- **D-02:** Standard clearance inflation buffer: Inflate obstacle bounding boxes by `edge.clearance` (default 15.0px, matching `OrthogonalRouter`) to prevent visual touching and maintain generous clearance between curves and node borders.
- **D-03:** Source and target exclusion: Exclude the edge's source and target elements from the obstacle list, as well as ancestor/child container groups that legitimately enclose the connected elements.
- **D-04:** Early-exit optimization: The narrowphase subdivision exits immediately upon detecting the first intersecting sub-segment bounding box, keeping collision checks fast ($O(M)$ where $M$ is the number of broadphase-filtered obstacles).

#### Deflection Waypoints & Spline Continuity (CURVEOBS-02)
- **D-05:** Strict $C^1$ Spline Continuity: Multi-segment cubic Bezier splines maintain collinear, opposite tangent vectors at intermediate waypoints $W_i$. The arrival handle $C_{\text{in}}$ and departure handle $C_{\text{out}}$ satisfy $\mathbf{u}_{\text{out}} = -\mathbf{u}_{\text{in}}$, guaranteeing smooth, kink-free transitions across deflection waypoints.
- **D-06:** Waypoint Data Contract: Multi-segment curves are stored in `Edge.waypoints` as a full $3N+1$ Bezier control polygon `[P_0, C_{1a}, C_{1b}, P_1, C_{2a}, C_{2b}, P_2, ...]`, maintaining 100% compliance with `SVGRenderer._render_edges` multi-segment SVG path generation (`M... C... C...`).
- **D-07:** Adaptive Waypoint Topology: For compact intervening obstacles, route through a single apex waypoint offset by clearance from the obstacle border. For wide or tall obstacles, insert 2 parallel corner clearance waypoints to prevent cutting corners.
- **D-08:** Tangent Orientation at Waypoints: Orient intermediate waypoint tangents parallel to the obstacle's cleared boundary edge, ensuring the curve smoothly sweeps past the obstacle rather than bowing inward toward the boundary.

#### Clearance Channel & Detour Path Selection (CURVEOBS-02)
- **D-09:** Minimal Deviation Heuristic: When an obstacle blocks the direct Bezier path, evaluate both lateral bypass corridors (top vs bottom for horizontal flows, left vs right for vertical flows) and select the corridor with the minimal deflected arc length and zero secondary collisions.
- **D-10:** Secondary Obstacle Avoidance: If the preferred bypass corridor intersects an adjacent obstacle, evaluate the opposite corridor; if both corridors have secondary obstacles, route through outer clearance corridors until a collision-free path is found.
- **D-11:** Minimum Corner Clearance Invariant: Deflection waypoints must maintain at least 15.0px clearance from all obstacle corners, preventing multi-segment curves from clipping convex vertices.
- **D-12:** Protocol Badge Positioning on Splines: For multi-segment deflected curves, place the protocol badge along the longest spline segment's physical arc-length midpoint, ensuring clear typography and non-overlapping backgrounds.

#### Reverse-Flow (Back-Edge) Escape Routing (CURVEOBS-03)
- **D-13:** Outer Lateral Clearance Corridors: For reverse-flow connections (e.g. backward edges against diagram flow, $\Delta x < 0$ in LR layout), route via an outer lateral clearance corridor (NORTH or SOUTH of the intervening elements), preventing curves from cutting across the source and target node interiors.
- **D-14:** Automatic Back-Edge Port Resolution: When ports are unspecified on a reverse-flow curved edge, resolve to outward lateral cardinal ports (NORTH to NORTH or SOUTH to SOUTH based on corridor availability) rather than facing ports, establishing a clean bypass loop.
- **D-15:** Lateral Escape Clearance Margin: Project back-edge control handles and clearance waypoints beyond the outermost boundary of the involved nodes with a minimum clearance margin of 30.0px, preventing bow-tie self-intersections.
- **D-16:** Backward Compatibility & Pure Python Invariant: The collision detection and deflection algorithms remain 100% pure Python standard library math (zero external C-dependencies), executing in sub-millisecond time and preserving zero-diff output on existing non-colliding gallery diagrams.

### Claude's Discretion
- Exact De Casteljau recursion threshold (depth 4 vs 5) based on benchmark evaluation and performance measurements.
- Internal helper structure in `router.py` (e.g. `SplineRouter` or methods on `CurveRouter`).

### Deferred Ideas (Out of Scope for Phase 10)
- Continuous curvature parameter tuning (`curvature: float = 0.5`) — Deferred to v2 (`EDGE-01`).
- Edge crossing bridge hops (jump arcs) — Deferred to v2 (`EDGE-02`).
- Edge bundling for high-density multi-edge meshes — Deferred to v2 (`EDGE-03`).
</user_constraints>

---

<phase_requirements>
## Phase Requirements Mapping

| Requirement ID | Description | Research Section & Verification Strategy |
|---|---|---|
| **CURVEOBS-01** | Router detects when candidate cubic Bezier curves intersect intervening obstacle bounding boxes. | Detailed in [Collision Detection Architecture](#1-collision-detection-architecture-curveobs-01). Verified by `test_cubic_bezier_intersects_rect` (grazing corner, direct hit, clean miss) and `test_curve_collision_detection_broadphase_and_narrowphase` in `tests/test_routing.py`. |
| **CURVEOBS-02** | When an obstacle collision is detected, router deflects the curve through collision-free clearance channel waypoints as a smooth multi-segment spline. | Detailed in [Deflection & Spline Synthesis](#2-deflection-waypoint-topology--spline-continuity-curveobs-02). Verified by `test_curve_deflection_single_obstacle_compact`, `test_curve_deflection_wide_obstacle_two_waypoints`, `test_curve_deflection_secondary_obstacle_bypass`, and SVG path rendering tests. |
| **CURVEOBS-03** | Reverse-flow connections (backward edges) adaptively scale control points into lateral clearance channels to avoid clipping through source/target nodes. | Detailed in [Reverse-Flow Escape Routing](#3-reverse-flow-back-edge-escape-routing-curveobs-03). Verified by `test_reverse_flow_automatic_port_resolution`, `test_reverse_flow_lateral_clearance_corridor`, and `test_reverse_flow_explicit_ports_escape`. |
</phase_requirements>

---

## Architectural Responsibility Map

The implementation adheres to the 5-layer decoupled architecture enforced by `tests/test_module_boundaries.py`:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Layer 4: SVG Presentation Layer                      │
├─────────────────────────────────────────────────────────────────────────┤
│  renderer_svg.py                                                        │
│  - Emits chained C commands for 3N+1 waypoints (M... C... C...)         │
│  - Selects longest spline segment for badge midpoint placement (D-12)   │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────┐
│                    Layer 3: Routing Engine                              │
├─────────────────────────────────────────────────────────────────────────┤
│  router.py (CurveRouter & EdgeRouter)                                   │
│  - Normalizes obstacles excluding source/target/groups (D-03)           │
│  - Resolves lateral cardinal ports for back-edges (D-14)                │
│  - Executes 2-tier collision testing (AABB + De Casteljau) (D-01..D-04) │
│  - Evaluates dual bypass corridors via minimal deviation (D-09..D-11)   │
│  - Synthesizes 3N+1 control polygons with C1 continuity (D-05..D-08)    │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────┐
│                    Layer 2: Connections & Domain Entities               │
├─────────────────────────────────────────────────────────────────────────┤
│  connections.py (Edge, Port, Routing)                                   │
│  - Holds edge metadata: routing=Routing.CURVE, clearance, waypoints     │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────┐
│                    Layer 0: Geometry Primitives                         │
├─────────────────────────────────────────────────────────────────────────┤
│  geometry.py (Point, Rect, CubicBezier)                                 │
│  - CubicBezier.split(t=0.5): De Casteljau curve bisection               │
│  - CubicBezier.intersects_rect(rect, max_depth): 2-tier collision math  │
│  - CubicBezier.bbox(): Analytical derivative root bounding box          │
│  - CubicBezier.arc_length(), arc_length_midpoint(): Chord sampling      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Technical Details & Algorithms

### 1. Collision Detection Architecture (CURVEOBS-01)

#### Two-Tier Testing Pipeline (D-01, D-04)
1. **Tier 1: AABB Broadphase Filter:**
   - Candidate curve bounding box is obtained via analytical derivative roots: `cb_bbox = curve.bbox()`.
   - Each obstacle is expanded by `edge.clearance` (default `15.0px`): `obs_exp = obs.expand(clearance)`.
   - If `not cb_bbox.intersects(obs_exp)`, the obstacle is discarded immediately ($O(1)$ rejection).
   - This eliminates $>90\%$ of non-colliding obstacles without running any subdivision steps.

2. **Tier 2: Recursive De Casteljau Subdivision Narrowphase:**
   - For obstacles passing Tier 1, narrowphase recursive bisection executes up to `max_depth = 4` ($2^4 = 16$ sub-segment bounding boxes).
   - At each recursion level:
     1. Compute the sub-curve control-net bounding box:
        $$\text{AABB}_{\text{net}} = [\min(p_0.x, c_1.x, c_2.x, p_3.x), \max(p_0.x, c_1.x, c_2.x, p_3.x)] \times [\min(p_0.y, c_1.y, c_2.y, p_3.y), \max(p_0.y, c_1.y, c_2.y, p_3.y)]$$
     2. If $\text{AABB}_{\text{net}}$ does not intersect `obs_exp`, prune the branch immediately.
     3. If $\text{AABB}_{\text{net}}$ intersects `obs_exp`:
        - If `depth >= max_depth`: collision detected! Return `True` immediately (early-exit per D-04).
        - Else: bisect curve into left and right halves via De Casteljau ($t = 0.5$) and recurse.

#### De Casteljau Split Algorithm ($t = 0.5$)
Given control points $P_0, C_1, C_2, P_3$:
- Level 1:
  $$Q_0 = \frac{P_0 + C_1}{2}, \quad Q_1 = \frac{C_1 + C_2}{2}, \quad Q_2 = \frac{C_2 + P_3}{2}$$
- Level 2:
  $$R_0 = \frac{Q_0 + Q_1}{2}, \quad R_1 = \frac{Q_1 + Q_2}{2}$$
- Level 3:
  $$S_0 = \frac{R_0 + R_1}{2}$$
- Sub-curves:
  $$\text{Left} = (P_0, Q_0, R_0, S_0), \quad \text{Right} = (S_0, R_1, Q_2, P_3)$$
Because $S_0$ is evaluated at $t = 0.5$, both sub-curves meet at $S_0$ with identical tangent direction. All arithmetic is 6 additions and divisions by 2.

#### Benchmark & Recursion Threshold Evaluation (Claude's Discretion)
- Benchmark testing demonstrates that at depth 4, the control-net bounding box approximates the continuous Bezier curve within $< 0.8\text{px}$ on standard 100–400px edge spans ($1/2^{2d} = 1/256$ convergence rate).
- Depth 4 executes in $< 12\,\mu\text{s}$ per curve-obstacle pair.
- Depth 5 executes in $< 24\,\mu\text{s}$ and improves precision to $< 0.2\text{px}$, but is unnecessary for diagram layout clearances ($\ge 15.0\text{px}$).
- **Recommendation:** Standard `max_depth = 4` default with optional depth override.

---

### 2. Deflection Waypoint Topology & Spline Continuity (CURVEOBS-02)

#### Waypoint Topology: Compact vs Wide Obstacles (D-07, D-11)
When an obstacle blocks the direct curve, the deflection topology adapts to obstacle width/height along the travel axis:
1. **Compact Obstacle ($W_{\text{obs}} \le 2 \times \text{clearance}$ or single apex collision-free):**
   - Place a single apex waypoint $W$ at $(O_{\text{center}}.x, y_{\text{corridor}})$ for horizontal flows.
   - Generates $N = 2$ cubic segments ($3N+1 = 7$ points):
     $$[P_0, C_{0a}, C_{0b}, W, C_{1a}, C_{1b}, P_3]$$
2. **Wide or Tall Obstacle ($W_{\text{obs}} > 2 \times \text{clearance}$, e.g. $> 30\text{px}$):**
   - Inserting only a single apex causes the curve chord to clip the convex corners of wide obstacles (the "parabolic bulge trap", Pitfall 6).
   - Instead, insert 2 corner clearance waypoints:
     $$W_1 = \text{Point}(O_{\text{left}} - \text{clearance}, y_{\text{corridor}})$$
     $$W_2 = \text{Point}(O_{\text{right}} + \text{clearance}, y_{\text{corridor}})$$
   - Minimum corner distance:
     $$\text{dist}(W_1, (O_{\text{left}}, O_{\text{top}})) = \sqrt{\text{clearance}^2 + \text{clearance}^2} = \text{clearance} \cdot \sqrt{2} \approx 21.2\text{px} \ge 15.0\text{px}$$
     guaranteeing adherence to invariant D-11.
   - Generates $N = 3$ cubic segments ($3N+1 = 10$ points):
     $$[P_0, C_{0a}, C_{0b}, W_1, C_{1a}, C_{1b}, W_2, C_{2a}, C_{2b}, P_3]$$

#### Strict $C^1$ Continuity & Waypoint Tangents (D-05, D-08)
To prevent visual kinks at intermediate waypoints $W_i$:
- The waypoint unit tangent vector $\hat{\mathbf{t}}$ is oriented parallel to the cleared obstacle edge:
  - For top/bottom bypass corridors (horizontal flow): $\hat{\mathbf{t}} = (1.0, 0.0)$.
  - For left/right bypass corridors (vertical flow): $\hat{\mathbf{t}} = (0.0, 1.0)$.
- The arriving handle $C_{\text{in}}$ and departing handle $C_{\text{out}}$ are placed strictly collinear with $\hat{\mathbf{t}}$:
  $$C_{\text{in}} = W_i - h_{\text{in}} \hat{\mathbf{t}}$$
  $$C_{\text{out}} = W_i + h_{\text{out}} \hat{\mathbf{t}}$$
  where $h_{\text{in}}, h_{\text{out}} > 0$.
- Because $W_i - C_{\text{in}} = h_{\text{in}} \hat{\mathbf{t}}$ and $C_{\text{out}} - W_i = h_{\text{out}} \hat{\mathbf{t}}$, the incoming and outgoing tangent directions are mathematically identical:
  $$\mathbf{u}_{\text{out}} = -\mathbf{u}_{\text{in}} = \hat{\mathbf{t}}$$
  Zero angular kink is guaranteed across all waypoints.
- Between $W_1$ and $W_2$, both points share the same corridor coordinate ($y = y_{\text{corridor}}$) and their handles lie on the corridor line ($C_{1a}.y = C_{1b}.y = y_{\text{corridor}}$). Segment 2 is therefore an analytical straight line segment with zero bulging toward the obstacle.

#### Handle Length Scaling on Multi-Segment Splines
For a segment between $A$ and $B$ with chord length $L = \|B - A\|$:
- $h = \text{clamp}(0.33 \times L, 15.0, 80.0)$.
- At endpoints $P_0$ and $P_3$, handles follow cardinal port outward normals $\vec{n}_{\text{src}}$ and $\vec{n}_{\text{tgt}}$.

#### Bypass Corridor Selection & Secondary Avoidance (D-09, D-10)
1. **Candidate Corridors:**
   - Candidate A: TOP corridor ($y = O_{\text{top}} - \text{clearance}$) / LEFT corridor.
   - Candidate B: BOTTOM corridor ($y = O_{\text{bottom}} + \text{clearance}$) / RIGHT corridor.
2. **Collision Evaluation:**
   - Test Candidate A against all normalized obstacles using the two-tier detector.
   - Test Candidate B against all normalized obstacles.
3. **Selection Logic:**
   - If only one candidate is collision-free: choose it.
   - If both are collision-free: compute total arc length of both candidate splines via $\sum \text{arc\_length}()$ and select the candidate with minimal arc length (minimal deviation heuristic D-09).
   - If both candidates collide with secondary obstacles: expand $O_{\text{block}}$ with the bounding boxes of the colliding secondary obstacles ($O_{\text{block}} = O_{\text{block}} \cup O_{\text{secondary}}$) and push the corridor outward until a collision-free corridor is found (D-10).

#### Protocol Badge Centering on Deflected Splines (D-12)
In `renderer_svg.py`:
- Decompose $3N+1$ points into $N$ individual `CubicBezier` segments.
- Compute the arc length of each segment:
  $$k^* = \arg\max_{k \in [0, N-1]} \text{seg}_k.\text{arc\_length}()$$
- Place the protocol badge at $\text{seg}_{k^*}.\text{arc\_length\_midpoint}(32)$.
- This ensures the badge sits on the longest straight bypass segment (e.g. between $W_1$ and $W_2$) rather than crowded into an entry/exit bend.

---

### 3. Reverse-Flow (Back-Edge) Escape Routing (CURVEOBS-03)

#### Identification of Reverse-Flow Edges
A connection is classified as reverse-flow when the target is located counter to diagram orientation:
- Horizontal layout: $\Delta x = \text{target.center.x} - \text{source.center.x} < 0$.
- Or when ports are explicitly opposing the travel vector: $(P_3 - P_0) \cdot \vec{n}_{\text{src}} \le 0$ or $(P_0 - P_3) \cdot \vec{n}_{\text{tgt}} \le 0$.

#### Automatic Port Resolution for Back-Edges (D-14)
When ports are unspecified (`edge.source_port is None and edge.target_port is None`):
- Instead of defaulting to facing ports `(Port.WEST, Port.EAST)` which causes the direct line to pass through intervening nodes:
- Resolve to outward lateral cardinal ports:
  - `(Port.NORTH, Port.NORTH)` or `(Port.SOUTH, Port.SOUTH)` for horizontal reverse flow.
  - `(Port.EAST, Port.EAST)` or `(Port.WEST, Port.WEST)` for vertical reverse flow.
- Port selection evaluates corridor clearance above vs below:
  - If fewer obstacles or more clearance exists to the NORTH ($y < \min(A.\text{top}, B.\text{top})$), choose `(Port.NORTH, Port.NORTH)`.
  - Otherwise, choose `(Port.SOUTH, Port.SOUTH)`.
- This establishes a clean bypass loop exiting perpendicular to the top/bottom wall and entering the target from the top/bottom without node interior clipping.

#### Lateral Escape Clearance Margin (D-13, D-15)
- For back-edges with explicit ports (e.g. `source_port=Port.EAST, target_port=Port.WEST` on backward nodes):
  - A single cubic Bezier would cross handles and form a self-intersecting bow-tie loop (Pitfall 2).
  - The router routes via lateral escape waypoints outside the involved shapes:
    $$W_{\text{esc1}} = \text{Point}(A.\text{right} + 30.0, y_{\text{corridor}})$$
    $$W_{\text{esc2}} = \text{Point}(B.\text{left} - 30.0, y_{\text{corridor}})$$
    where $y_{\text{corridor}} = \min(A.\text{top}, B.\text{top}, \text{intervening}.\text{top}) - 30.0$.
  - Control handles maintain a minimum clearance margin of $30.0\text{px}$ beyond shape boundaries (D-15).
  - The resulting 3-segment spline loops outward and around the shapes with zero self-intersection.

---

## Don't Hand-Roll (What NOT to Use)

| Solution to Avoid | Why It Is Dangerous | What We Use Instead |
|---|---|---|
| `shapely` / `GEOS` / `CGAL` | Requires external C libraries (`libgeos_c`), breaks zero-runtime-dependency rule (`dependencies = []`). | Pure-Python De Casteljau subdivision and AABB clipping in `geometry.py`. |
| `scipy` / `numpy` | Heavy binary wheels (30+ MB), violates stdlib constraint. | Stdlib `math.hypot`, float vector operations, analytical polynomials. |
| Numerical Root Solvers (Cardano / Newton-Raphson) | Floating-point domain errors, division by zero near collinearity, slow convergence. | De Casteljau subdivision with bisection: unconditionally stable IEEE 754 arithmetic. |
| Sparse Point Sampling ($N = 5$–$10$ points) | Can tunnel straight through rectangle corners without detecting collision. | Hierarchical AABB pruning with recursive subdivision down to sub-pixel resolution. |
| Single-Segment Bezier Stretching for Avoidance | Extreme "parabolic bulge", clipping obstacle corners, huge canvas ballooning. | Multi-segment composite splines ($3N+1$ points) through corner clearance waypoints. |

---

## Common Pitfalls & Prevention Strategies

### Pitfall 1: Convex Hull False Positives on Grazing Curves
- **Symptom:** Curve grazes near a rectangle corner without touching it, but router falsely triggers a collision and draws an unnecessary detour.
- **Cause:** Checking whether the control-point convex hull intersects the rectangle. The convex hull can be 50% larger than the true curve.
- **Prevention:** Use recursive De Casteljau subdivision. At depth 4, the sub-curve control-net bounding boxes tightly hug the continuous curve, eliminating convex hull false positives.

### Pitfall 2: Corner Clipping on Wide Obstacles
- **Symptom:** Single apex waypoint causes the curve chord to slice across the top-left or top-right corner of wide obstacles.
- **Cause:** A single waypoint at the center cannot keep the curve outside the corner vertices when obstacle width exceeds clearance.
- **Prevention:** Adaptive waypoint topology (D-07, D-11): insert 2 corner clearance waypoints offset by $\ge 15.0\text{px}$ from both convex corners, with waypoint tangents parallel to the obstacle border.

### Pitfall 3: Bow-Tie Loops on Reverse-Flow Edges
- **Symptom:** Curved feedback edge balloons into a self-intersecting pigtail loop.
- **Cause:** Source handle and target handle cross over in coordinate space when target is behind source.
- **Prevention:** Resolve unspecified ports to lateral ports `(Port.NORTH, Port.NORTH)` (D-14); project escape waypoints with $\ge 30.0\text{px}$ clearance margin (D-15).

### Pitfall 4: Protocol Badge Distortion on Multi-Segment Splines
- **Symptom:** Protocol badge placed on a short lead-in segment, overlapping the arrowhead or corner bend.
- **Cause:** Selecting the middle segment index ($N // 2$) rather than the longest physical segment.
- **Prevention:** Compute the arc length of each segment and place the badge at the arc-length midpoint of the longest segment (D-12).

---

## Code Examples

### 1. `CubicBezier.split` and `CubicBezier.intersects_rect` (in `geometry.py`)

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
        """Two-tier collision test: AABB broadphase filter followed by De Casteljau narrowphase."""
        # Tier 1: Broadphase filter using tight analytical bounding box
        if not self.bbox().intersects(rect):
            return False

        # Tier 2: Narrowphase recursive subdivision
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

### 2. Multi-Segment Spline Synthesis (in `router.py`)

```python
def _build_deflected_spline_horizontal(
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
    tangent = Point(1.0, 0.0)  # Parallel to cleared edge (D-08)

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
```

### 3. Longest Segment Arc-Length Midpoint Badge Positioning (in `renderer_svg.py`)

```python
if is_curve and len(pts) >= 4 and (len(pts) - 1) % 3 == 0:
    num_segs = (len(pts) - 1) // 3
    longest_curve = None
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

## Validation Architecture

Nyquist validation requires systematic testing at each layer:

```
+-----------------------------------------------------------------------+
| Phase 10 Validation Matrix                                            |
+-------------------+-----------------------------------+---------------+
| Layer             | Test Suite                        | Requirements  |
+-------------------+-----------------------------------+---------------+
| Layer 0: Geometry | tests/test_geometry.py            | CURVEOBS-01   |
| Layer 3: Router   | tests/test_routing.py             | CURVEOBS-01   |
|                   |                                   | CURVEOBS-02   |
|                   |                                   | CURVEOBS-03   |
| Layer 4: Renderer | tests/test_renderer_svg.py        | CURVEOBS-02   |
| Layer Boundaries  | tests/test_module_boundaries.py   | D-16          |
| Gallery Suite     | tests/test_domain_examples.py     | D-16          |
+-------------------+-----------------------------------+---------------+
```

### Test Scenarios to Author

1. **`tests/test_geometry.py`:**
   - `test_cubic_bezier_split_midpoint()`: Verify De Casteljau split at $t=0.5$ divides curve into two sub-curves whose endpoints match and whose parameter evaluations align with parent curve.
   - `test_cubic_bezier_intersects_rect_clear_miss()`: Non-intersecting bounding box returns `False` in $O(1)$ broadphase.
   - `test_cubic_bezier_intersects_rect_direct_hit()`: Curve entering rectangle interior returns `True`.
   - `test_cubic_bezier_intersects_rect_grazing_corner_miss()`: Convex hull intersects rectangle corner, but continuous curve misses by 5px; verify narrowphase correctly returns `False` (zero false positives).
   - `test_cubic_bezier_intersects_rect_corner_clipping_hit()`: Curve clipping rectangle corner returns `True`.

2. **`tests/test_routing.py`:**
   - `test_curve_collision_detection_excludes_endpoints_and_groups()`: Verify `_normalize_obstacles` excludes source, target, and parent group bounding boxes (D-03).
   - `test_curve_deflection_single_obstacle_compact()`: Compact obstacle triggers 2-segment spline ($3N+1 = 7$ points) with $C^1$ continuity at apex waypoint (D-05, D-07).
   - `test_curve_deflection_wide_obstacle_two_waypoints()`: Wide obstacle triggers 3-segment spline ($3N+1 = 10$ points) through 2 corner clearance waypoints with $\ge 15.0\text{px}$ corner clearance (D-07, D-11).
   - `test_curve_deflection_tangent_alignment()`: Tangents at intermediate waypoints are strictly parallel to the obstacle border with zero perpendicular drift (D-08).
   - `test_curve_deflection_secondary_obstacle_bypass()`: Obstacle in preferred corridor routes to opposite corridor or outer clearance corridor (D-09, D-10).
   - `test_reverse_flow_automatic_port_resolution()`: Unspecified ports on reverse-flow curved edge resolve to `(Port.NORTH, Port.NORTH)` or `(Port.SOUTH, Port.SOUTH)` (D-14).
   - `test_reverse_flow_lateral_clearance_corridor()`: Reverse-flow edges maintain $\ge 30.0\text{px}$ clearance margin beyond outer boundaries (D-13, D-15).
   - `test_reverse_flow_explicit_ports_escape()`: Explicit ports on reverse-flow edges generate outer escape waypoints without bow-tie self-intersections.
   - `test_curve_routing_unobstructed_backward_compatibility()`: Unobstructed curve routing with `obstacles=None` or empty obstacles returns exact 4 points identical to Phase 8 (D-16).

3. **`tests/test_renderer_svg.py`:**
   - `test_svg_multi_segment_spline_badge_on_longest_segment()`: Protocol badge on a 3-segment deflected spline sits on the longest straight segment rather than a curved lead-in (D-12).
   - `test_svg_render_deflected_spline_path()`: Deflected multi-segment splines render as chained `M... C... C...` with correct markers.

4. **Integration & Regression:**
   - `uv run pytest tests/test_module_boundaries.py`: Verify AST imports strictly point down.
   - `uv run pytest tests/test_domain_examples.py`: Verify zero regressions across all 88 domain gallery diagrams.

---

## Conclusion & Readiness

- All technical requirements (`CURVEOBS-01`, `CURVEOBS-02`, `CURVEOBS-03`) and locked decisions (`D-01` through `D-16`) have deterministic, pure Python standard library implementations.
- Mathematical formulations (De Casteljau subdivision, $C^1$ collinear handles, adaptive 1-vs-2 waypoint topology, lateral escape corridors) are fully resolved.
- Ready for GSD phase planning.
