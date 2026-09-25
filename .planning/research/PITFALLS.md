# Pitfalls Research

**Domain:** Curved & Bezier Edge Routing, Rounded Corner Fillets, and Obstacle-Aware Deflection in Pure Python SVG Diagrams
**Researched:** 2026-09-24
**Confidence:** HIGH

---

## Critical Pitfalls

### Pitfall 1: Degenerate Control Points Causing NaN / Undefined SVG Marker Orientations

**What goes wrong:**
Arrowheads at curve start or end points disappear completely, point in the wrong direction (e.g., pointing 90° or 180° away from the target shape), or throw rendering warnings in SVG renderers and browsers.

**Why it happens:**
SVG markers configured with `orient="auto"` or `orient="auto-start-reverse"` compute the marker rotation angle from the path's instantaneous tangent vector at the endpoint. For a cubic Bezier curve defined by control points $(P_0, P_1, P_2, P_3)$, the tangent at $t = 1$ (the target arrowhead) is:
$$\vec{T}(1) = 3(P_3 - P_2)$$
Similarly, the tangent at $t = 0$ (the source tail) is:
$$\vec{T}(0) = 3(P_1 - P_0)$$
If $P_2 = P_3$ or $P_1 = P_0$ (which happens when source and target elements are very close, when zero-length offsets are calculated, or when deflection collapses control points), the tangent vector is $(0, 0)$. In standard SVG engines (Blink, Gecko, WebKit, resvg, librsvg), `atan2(0, 0)` is either undefined, returns `NaN`, or defaults to $0^\circ$. This causes the arrowhead marker to either vanish, orient horizontally regardless of actual edge direction, or point backward into the element.

**How to avoid:**
1. **Enforce Minimum Tangent Separation:** In the Bezier control point generator, enforce an invariant:
   $$\|P_1 - P_0\| \ge \epsilon \quad \text{and} \quad \|P_3 - P_2\| \ge \epsilon \quad (\text{where } \epsilon \ge 1.0\text{px})$$
2. **Project along Port Normal:** Control points adjacent to ports must be offset along the port's outward normal unit vector $\vec{n}_{port}$. Even if Euclidean distance between elements is tiny, keep a minimum stub distance $d_{\min} = \max(12.0, \text{arrowhead\_length})$ along the normal.
3. **Degenerate Fallback:** If $P_0 == P_3$ (self-loop or zero-distance edge), branch explicitly to a dedicated loop routing strategy rather than calculating zero-length control vectors.

**Warning signs:**
- Arrowhead missing entirely on short curved edges in SVG output.
- Arrowhead points right ($0^\circ$) on an edge that arrives vertically from above into a North port.
- Automated tests comparing marker angle against port normal report zero or `NaN` angle.

**Phase to address:**
Phase 1: Cubic Bezier Routing Engine & SVG Path Generation.

---

### Pitfall 2: Control Point Overshoot and Self-Intersecting "Bow-Tie" Loops on Close or Backward Nodes

**What goes wrong:**
When connecting elements that are placed close to each other, slightly offset along an orthogonal axis, or where the target is "behind" the source port (e.g., target $x < \text{source } x$ with East-to-West ports), the cubic Bezier curve balloons outward, forms a self-intersecting "bow-tie" or pigtail loop, and cuts across unrelated diagram shapes or leaves the canvas bounds.

**Why it happens:**
A naive control point heuristic calculates control handle distance as a fixed fraction of total Euclidean distance:
$$\Delta = k \cdot \|P_3 - P_0\| \quad (\text{often } k = 0.5)$$
or as a fixed absolute length (e.g., $\Delta = 50\text{px}$) directed outward along the port normal.
When the target element is behind the source port normal (i.e., $(P_3 - P_0) \cdot \vec{n}_{src} < 0$), the source handle $P_1 = P_0 + \Delta \cdot \vec{n}_{src}$ and the target handle $P_2 = P_3 + \Delta \cdot \vec{n}_{tgt}$ point towards each other and cross over in space ($P_1.x > P_2.x$). Because a cubic Bezier must interpolate $P_0 \to P_1 \to P_2 \to P_3$, the parametric curve is forced to loop backward on itself to satisfy the boundary tangents.

**How to avoid:**
1. **Axis-Projected Distance Clamping:**
   Instead of total Euclidean distance, scale the control handle displacement based on the *projected* forward distance along the port axis:
   $$\Delta_{src} = \text{clamp}\left(k \cdot \max(0.0, (P_3 - P_0) \cdot \vec{n}_{src}), \ d_{\min}, \ d_{\max}\right)$$
2. **Backward Edge Detection:**
   If $(P_3 - P_0) \cdot \vec{n}_{src} \le 0$ or $(P_0 - P_3) \cdot \vec{n}_{tgt} \le 0$, a single cubic Bezier cannot cleanly represent the path without looping. The router must either:
   - Automatically select alternative, non-opposing cardinal ports (e.g., switch East $\to$ West to South $\to$ South or North $\to$ North if unpinned).
   - Route a composite multi-segment spline through intermediate clearance waypoints around the nodes rather than forcing a single cubic segment.

**Warning signs:**
- Curves looping outward like lasso ropes on feedback/backward edges.
- Curve bounding box height or width is 3× to 5× greater than the bounding box of the two connected nodes.
- Intermediate inflection points where the second derivative changes sign twice within a short distance.

**Phase to address:**
Phase 1 (Bezier Routing Engine) & Phase 3 (Obstacle & Backward Deflection).

---

### Pitfall 3: Orthogonal Fillet Radius Clamping Failure (Arc Inversion & "Dog Ears" on Short Segments)

**What goes wrong:**
When rendering rounded corners on orthogonal Manhattan paths (`Routing.ORTHOGONAL` with `arc_radius`), corners with short intermediate segments produce inverted circular arcs, overlapping loops ("dog ears"), or SVG path parse glitches.

**Why it happens:**
Manhattan routing frequently generates short segments (e.g., 10–20px jogs to enter an anchor or clear an obstacle clearance corridor). If the fillet radius $R$ is fixed (e.g., default $R = 15\text{px}$), and a segment between two consecutive 90° bends is shorter than $2R$ (say, length $L = 18\text{px}$), the arc starting from the first bend tries to consume $15\text{px}$ while the arc entering the second bend also tries to consume $15\text{px}$. Because $15 + 15 = 30 > 18$, the arc start and end points overlap and cross over.
In SVG, rendering an arc (`A rx ry ...`) or quadratic curve (`Q cx cy ...`) whose start and end points are inverted causes SVG engines to flip the arc sweep, creating an outward-pointing spike or loop.

**How to avoid:**
1. **Per-Vertex Radius Clamping:**
   For every internal bend vertex $V_i$ with incoming segment length $L_{i-1, i} = \|V_i - V_{i-1}\|$ and outgoing segment length $L_{i, i+1} = \|V_{i+1} - V_i\|$, compute the maximum allowable radius for that corner:
   $$R_{\text{max}, i} = \min\left(R, \ \frac{L_{i-1, i}}{2}, \ \frac{L_{i, i+1}}{2}\right)$$
   For consecutive corners sharing a segment of length $L$, the sum of their radii must not exceed $L$:
   $$\text{If } R_i + R_{i+1} > L, \quad \text{scale both proportionally: } R_i' = R_i \cdot \frac{L}{R_i + R_{i+1}}$$
2. **Degradation to Sharp Corner:**
   If $R_{\text{eff}} < \text{threshold}$ (e.g., $< 2.0\text{px}$), suppress the fillet and emit a standard sharp line vertex (`L x y`).

**Warning signs:**
- Visible triangular "ears" or loops protruding from corners on tight S-bends or detour corridors.
- Path rendering errors or negative arc arguments in generated SVG XML.
- Regressions on benchmark diagrams with dense node clusters.

**Phase to address:**
Phase 2: Orthogonal Rounded Corner Fillets.

---

### Pitfall 4: Parameter-Space ($t = 0.5$) Label Placement Distortion on Asymmetric Curves

**What goes wrong:**
Edge label protocol badges on curved edges appear lopsided, clumped near one endpoint, or collided into a source/target node instead of sitting at the visual midpoint of the edge.

**Why it happens:**
On orthogonal edges, the midpoint is trivially calculated by finding the midpoint of the central polyline segment:
$$(x, y) = \frac{P_{k} + P_{k+1}}{2}$$
On a cubic Bezier curve $B(t)$, naive implementations evaluate the curve at parameter $t = 0.5$:
$$B(0.5) = \frac{1}{8}P_0 + \frac{3}{8}P_1 + \frac{3}{8}P_2 + \frac{1}{8}P_3$$
However, parameter $t$ does *not* progress at a constant speed along physical arc length $s$. If control points are asymmetric (e.g., $P_1$ is displaced 120px to clear an obstacle while $P_2$ is displaced only 30px near the target), $t = 0.5$ might be physically located at 25% or 75% of the curve's actual travel distance. The label badge ends up hovering right next to one node.

**How to avoid:**
1. **Piecewise Linear Arc-Length Parameterization:**
   In pure Python (stdlib only):
   - Sample the cubic Bezier into $N = 32$ chords by evaluating $B(t_i)$ for $t_i = i / N$.
   - Compute cumulative chord lengths: $d_i = \sum_{j=1}^i \|B(t_j) - B(t_{j-1})\|$.
   - The total curve length is $L_{\text{total}} = d_N$. The target midpoint distance is $s_{\text{mid}} = L_{\text{total}} / 2$.
   - Find the interval $[d_k, d_{k+1}]$ containing $s_{\text{mid}}$ and interpolate parameter $t^*$:
     $$\alpha = \frac{s_{\text{mid}} - d_k}{d_{k+1} - d_k}, \quad t^* = \frac{k + \alpha}{N}$$
   - Place the label badge at coordinates $B(t^*)$.
2. **Badge Clearance Padding:**
   Because a curve changes direction underneath the label badge, ensure the badge rectangle has minimum horizontal and vertical clearance ($16\text{px}$ width padding, $18\text{px}$ height) to prevent the curved stroke from peeking through behind label text.

**Warning signs:**
- Edge labels visibly clinging to source or target node walls.
- Label badge overlapping the arrowhead on curved connections.
- Asymmetry in label position when source and target elements are flipped.

**Phase to address:**
Phase 1: Cubic Bezier Routing Engine & Edge Labels.

---

### Pitfall 5: Flawed Curve-Obstacle Collision Detection (Convex Hull False Positives & Raycast Misses)

**What goes wrong:**
Either the router falsely reports a collision when a curve cleanly misses an obstacle (causing unnecessary, ugly detour loops), or worse, a curve cuts directly through a node's bounding box because point sampling jumped over the rectangle's corners.

**Why it happens:**
Without external geometry libraries (no Shapely, SciPy, or CGAL), developers typically resort to one of three flawed shortcuts:
1. *Convex Hull Shortcut:* Checking whether the convex hull of $(P_0, P_1, P_2, P_3)$ intersects the obstacle `Rect`. While the curve is guaranteed to lie within the convex hull, the hull can be up to 50% larger than the curve on high-curvature bends, generating massive false-positive collisions.
2. *Sparse Point Sampling:* Evaluating $B(t)$ at a fixed number of steps (e.g., 5 or 10 points) and checking `rect.contains(pt)`. If an obstacle is narrow or the curve clips a corner, all sample points can land outside the box while the continuous curve cuts straight through it (tunneling).
3. *Direct Analytic Root Solving:* Solving the 3rd-degree polynomial equation $B_y(t) = y_{\text{rect}}$ for $t \in [0, 1]$ using Cardano's formula. In floating-point arithmetic, handling edge cases (tangencies, multiple roots, division by small leading coefficients when $P$ coordinates are nearly collinear) is notoriously fragile and bug-prone.

**How to avoid:**
1. **Hierarchical AABB & De Casteljau Recursive Subdivision:**
   - **Broadphase:** Compute the axis-aligned bounding box (AABB) of the Bezier control points:
     $$\text{AABB} = [\min(P_x), \max(P_x)] \times [\min(P_y), \max(P_y)]$$
     If $\text{AABB}$ does not intersect obstacle `Rect`, return `False` immediately ($O(1)$ rejection).
   - **Narrowphase:** If $\text{AABB}$ intersects `Rect`:
     - Subdivide the cubic Bezier into two halves ($t \in [0, 0.5]$ and $t \in [0.5, 1.0]$) using De Casteljau's algorithm (only 6 midpoint additions and divisions by 2).
     - Test the sub-curve AABBs against `Rect`.
     - Recursively subdivide only branches that intersect `Rect`.
     - Terminate when a sub-curve AABB is smaller than tolerance $\epsilon \le 2.0\text{px}$ and intersects the rect (collision = `True`), or when recursion depth limit (e.g., depth 6) is reached with all branches disjoint (collision = `False`).
   This pure-Python algorithm is 100% numerically stable, requires zero dependencies, and executes in microseconds.

**Warning signs:**
- Curved edges visibly slicing through node cards or group boundaries.
- Curves executing bizarre, erratic detours through empty white space.
- Floating-point `ZeroDivisionError` or domain errors in polynomial solver routines.

**Phase to address:**
Phase 3: Obstacle-Aware Curve Deflection.

---

### Pitfall 6: Single-Segment Bezier Degeneracy on Obstacle Deflection ("The Parabolic Bulge Trap")

**What goes wrong:**
When an obstacle lies directly between source and target, attempting to deflect around it by pulling the two control points $P_1$ and $P_2$ of a single cubic Bezier outward causes extreme distortion: the curve flattens across the top, bulges into a wide bulbous loop, and still clips the obstacle's sharp corners.

**Why it happens:**
A single cubic Bezier curve has only 4 control points (2 endpoints and 2 intermediate control handles), giving it at most one inflection point. It cannot form an "S-turn" or navigate a "corridor" around an obstacle. When an obstacle is wide (e.g., a 200px database node), pushing $P_1$ and $P_2$ perpendicular to the collision point causes the curve to stretch into an eccentric, distorted shape that either balloons off the diagram canvas or fails to maintain minimum clearance around the obstacle corners.

**How to avoid:**
1. **Piecewise Composite Splines (Multi-Segment Beziers):**
   Do not force a single cubic Bezier around wide obstacles.
2. **Channel-Waypoint Smoothing:**
   Use the existing grid/channel obstacle router (`OrthogonalRouter` / A* grid) to find orthogonal clearance waypoints $[W_0, W_1, \dots, W_m]$ around the obstacle.
3. **Convert Waypoints to Smooth Curves:**
   Convert the waypoint path into a $C^1$-continuous composite spline:
   - Either place rounded fillets at each internal waypoint $W_k$ (yielding an orthogonal-with-fillets path).
   - Or generate cubic Bezier segments between waypoints with matched tangent vectors at joints ($P_{3,\text{seg }k} = P_{0,\text{seg }k+1}$, and $\vec{T}_{\text{exit}} = \vec{T}_{\text{entry}}$).

**Warning signs:**
- Curve looks like an oversized lightbulb or inflated balloon.
- Edges exceeding canvas width/height by hundreds of pixels.
- Inability to route cleanly between three or more aligned obstacles.

**Phase to address:**
Phase 3: Obstacle-Aware Curve Deflection.

---

### Pitfall 7: Waypoints Data Model Collision & Polyline Renderer Breakage

**What goes wrong:**
Adding curve support by stuffing Bezier control points into `Edge.waypoints: list[Point]` breaks downstream components: `renderer_svg.py` draws sharp triangular spikes connecting the control points with `L` commands, layout file export corrupts edge state, and collinear simplification obliterates control points.

**Why it happens:**
In the existing codebase (`v0.7.0`), `Edge.waypoints` is strictly a `list[Point]` representing polyline vertices.
In `renderer_svg.py` (lines 600–602):
```python
path_d = f"M {pts[0].x} {pts[0].y} " + " ".join(
    f"L {p.x} {p.y}" for p in pts[1:]
)
```
If a curve router outputs $[P_0, P_1, P_2, P_3]$ into `e.waypoints`, the renderer executes `M P0.x P0.y L P1.x P1.y L P2.x P2.y L P3.x P3.y`. Instead of a smooth curve, the diagram renders a jagged triangle. Furthermore, `OrthogonalRouter._simplify_collinear` tests `prev_p.x == curr_p.x == next_p.x`, which would erroneously discard collinear Bezier control handles.

**How to avoid:**
1. **Structured Path Representation:**
   Introduce a typed path representation or explicit path segment model:
   - For example, `PathCommand` dataclasses (`MoveTo(pt)`, `LineTo(pt)`, `CubicBezier(p1, p2, p3)`, `Arc(...)`) or an explicit `edge.path_d: Optional[str]`.
2. **Keep `waypoints` Backward-Compatible:**
   Retain `edge.waypoints` as the sequence of anchor/via waypoints the edge visits, while attaching the compiled SVG path instructions or segment objects to `edge.route_path` or generating `path_d` via dedicated path builder functions.
3. **Renderer Branching:**
   Update `renderer_svg.py` to check `edge.routing` (or inspect path segment types) before emitting SVG path commands, rendering `C p1x p1y, p2x p2y, p3x p3y` for cubic curves and `A rx ry ...` for rounded fillets.

**Warning signs:**
- Visible "control point handles" rendered as solid stroke lines in diagrams.
- Existing tests expecting `len(edge.waypoints) == 4` failing because collinear simplification stripped intermediate control points.
- Sidecar layout files failing to serialize non-standard point structures.

**Phase to address:**
Phase 1: Data Model & SVG Path Generation.

---

### Pitfall 8: Edge Default Precedence Masking Diagram-Level Routing Configuration

**What goes wrong:**
Setting `Diagram(routing=Routing.CURVE)` or `diag.configure(routing="curve")` has zero effect; all edges continue to render as orthogonal Manhattan lines.

**Why it happens:**
In `diagrams_as_code/connections.py`:
```python
class Edge:
    def __init__(
        self,
        source: Element,
        target: Element,
        ...,
        routing: Union[Routing, str] = Routing.ORTHOGONAL,
        ...,
    ):
```
Because `Edge.__init__` defaults `routing` to `Routing.ORTHOGONAL` upon instantiation, every edge object created via `Edge(s1, s2)` or fluent syntax `s1 >> diag.edge(...) >> s2` has `edge.routing = Routing.ORTHOGONAL` baked in before it ever enters `Diagram`.
When `run_layout` or the router processes edges, it cannot distinguish between:
1. An edge where the user *explicitly* requested `Edge(..., routing=Routing.ORTHOGONAL)` as an override.
2. An edge that simply accepted the default parameter in `__init__`.
As a result, the diagram-level default `Diagram(routing=Routing.CURVE)` is completely ignored.

**How to avoid:**
1. **Sentinel / Optional Default:**
   Change `Edge.__init__` parameter to `routing: Optional[Union[Routing, str]] = None`.
2. **Cascading Resolution:**
   Resolve effective routing at route time:
   ```python
   def resolve_routing(edge: Edge, diagram: Optional[Diagram]) -> Routing:
       if edge.routing is not None:
           return edge.routing
       if diagram is not None and diagram.routing is not None:
           return diagram.routing
       return Routing.ORTHOGONAL
   ```
3. **Preserve Property Access:**
   Maintain backward compatibility so that querying `edge.routing` on a standalone edge outside a diagram still yields `Routing.ORTHOGONAL` (e.g., via a property getter or default assignment on unbound edges).

**Warning signs:**
- `Diagram(routing="curve")` passes in constructor but renders orthogonal lines in all outputs.
- Test suites require passing `routing="curve"` to every individual edge builder call.

**Phase to address:**
Phase 4: Diagram & Edge Level Routing Configuration.

---

### Pitfall 9: Arrowhead Normal Tilt Against Flat Shape Borders

**What goes wrong:**
The arrowhead entering a rectangular shape sits at a slanted diagonal angle (e.g., 35° or 60°), causing the arrowhead wings to pierce the shape boundary or poke outside the node corner.

**Why it happens:**
In architecture diagrams with rectangular cards, an edge arriving at a port (e.g., `Port.WEST` on a box) looks natural only if it enters perpendicular to that wall (arriving horizontally from the left at $0^\circ$).
If the Bezier control point $P_2$ has a vertical offset ($P_2.y \ne P_3.y$ for a West port), the tangent vector $P_3 - P_2$ enters at an oblique angle. While mathematically smooth, visually the arrowhead appears crooked and misaligned against the flat vertical stroke of the box.

**How to avoid:**
1. **Strict Port-Normal Tangency:**
   Constrain control points adjacent to cardinal ports to lie strictly on the port's outward normal ray:
   - For `Port.EAST` ($+x$ normal): $P_1 = (P_0.x + \Delta, P_0.y)$
   - For `Port.WEST` ($-x$ normal): $P_2 = (P_3.x - \Delta, P_3.y)$
   - For `Port.NORTH` ($-y$ normal): $P_2 = (P_3.x, P_3.y - \Delta)$
   - For `Port.SOUTH` ($+y$ normal): $P_2 = (P_3.x, P_3.y + \Delta)$
2. By locking the perpendicular coordinate, the final arrival derivative is guaranteed to be parallel to the normal vector, seating the arrowhead perfectly square against the node boundary.

**Warning signs:**
- Arrowhead wings visibly crossing outside the corner of a shape.
- Arrowhead appears slanted when connecting nodes at different vertical elevations.

**Phase to address:**
Phase 1: Cubic Bezier Routing Engine.

---

### Pitfall 10: Canvas Clipping from Unchecked Curve Extrema (Auto-Growth Failure)

**What goes wrong:**
Curved edges that arch upward or downward to avoid nodes get clipped at the top or sides of the SVG canvas, cutting off the stroke and arrowheads when viewed in browsers or exported to PNG.

**Why it happens:**
In `layout/pipeline.py`, `_grow_canvas` expands `diagram.width` and `diagram.height` based on element bounding boxes and orthogonal waypoints:
```python
max_x = max(p.x for p in edge.waypoints)
```
For a cubic Bezier curve, the maximum $x$ or $y$ coordinate reached by the curve does *not* occur at the endpoints $P_0$ or $P_3$, nor does it reach the full extent of the control points $P_1$ or $P_2$. If `_grow_canvas` only checks endpoints, a curve that arches above $y = 0$ will be cut off. If it checks control points, it may grow the canvas excessively because the curve never reaches the control points.

**How to avoid:**
1. **Analytic Bezier Extrema Calculation:**
   Find the true mathematical bounding box of the cubic Bezier $B(t)$ for $t \in [0, 1]$.
   The extrema occur where the first derivative equals zero:
   $$B'(t) = 3(1-t)^2(P_1 - P_0) + 6(1-t)t(P_2 - P_1) + 3t^2(P_3 - P_2) = 0$$
   This is a standard quadratic equation $a t^2 + b t + c = 0$ in pure Python stdlib:
   $$a = 3(-P_0 + 3P_1 - 3P_2 + P_3)$$
   $$b = 6(P_0 - 2P_1 + P_2)$$
   $$c = 3(P_1 - P_0)$$
   Solve for real roots $t \in (0, 1)$ using the quadratic formula. Evaluate $B(t)$ at the valid roots, $t = 0$, and $t = 1$. The true tight bounding box is the min/max of these evaluated points.
2. Feed these exact bounds into `_grow_canvas` in `layout/pipeline.py`.

**Warning signs:**
- Curved edge tops sliced off at the top border of the SVG image.
- Scrollbars appearing inside embedded SVG images.

**Phase to address:**
Phase 4: Canvas Auto-Growth & Layout Integration.

---

## Technical Debt Patterns

Shortcuts that seem reasonable during initial implementation but create severe long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| **Flat Control Points in `Edge.waypoints`** | No new classes needed; reuses `list[Point]` everywhere. | Renderer draws jagged polylines; collinear simplification corrupts curves; downstream consumers cannot distinguish lines from curves. | **NEVER.** Maintain typed path commands or separate curve metadata. |
| **Evaluating Curve Midpoint at $t = 0.5$** | 2 lines of arithmetic; avoids numerical integration or chord sampling. | Labels on asymmetric or deflected curves are severely off-center, often colliding with node shapes. | Acceptable only in initial spike/prototype; must fix before release. |
| **Fixed Fillet Radius without Clamping** | Quick string replacement in SVG path generation; avoids neighboring segment checks. | Inverted arc "ears" and self-intersecting loops appear whenever two 90° bends are within $2R$ of each other. | **NEVER.** Dynamic radius clamping is mandatory for fillets. |
| **Single Cubic Bezier for Obstacle Avoidance** | Avoids multi-segment waypoint routing; single math formula. | Huge ballooning loops, extreme canvas growth, and clipping across wide obstacle nodes. | **NEVER.** Obstacle avoidance requires multi-segment composite splines or filleted orthogonal detours. |
| **Hardcoded `Routing.ORTHOGONAL` in `Edge.__init__`** | Avoids handling `None` in existing edge tests. | Breaks diagram-level default routing configuration; `Diagram(routing=Routing.CURVE)` is permanently ignored. | **NEVER.** Use `None` as default and cascade to diagram routing. |
| **Sparse Point Sampling for Collision (5–10 points)** | Fast and simple; avoids implementing subdivision math. | Curves tunnel straight through corners or thin obstacles, causing undetected visual collisions. | **NEVER.** Use recursive De Casteljau subdivision with AABB pruning. |

---

## Integration Gotchas

Common mistakes when connecting curved routing to existing diagram subsystems.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| **SVG Markers (`<marker>`)** | Using `orient="auto"` with zero-length tangent vectors ($P_2 = P_3$), causing marker deletion or `NaN` rotation. | Enforce minimum tangent separation ($\ge 1.0\text{px}$) along port normal vectors so tangent angle is always well-defined. |
| **SVG Fillet Arcs (`A` command)** | Passing non-orthogonal or 180° reversal vectors to SVG elliptical arc commands, causing invalid SVG syntax. | Filter collinear points first. Compute arc sweep flag ($0$ vs $1$) using 2D cross product of incoming and outgoing segment vectors: $(v_1 \times v_2 > 0)$. |
| **Interactive Pan/Zoom & Search** | Query selector `.diagram-edge` assuming edge paths only contain `L` commands, or minimap failing to scale curve extents. | SVG `<use href="#diagram-content"/>` handles `<path d="...">` natively, but canvas bounds must encompass true Bezier extrema so minimap viewport stays aligned. |
| **BOM Table & Markdown Generation** | `BOMGenerator` assuming `edge.routing` is a string or crashing if new routing enums are added. | Ensure `Routing` enum has clean `.value` string serialization (`"curve"`, `"orthogonal"`, `"direct"`) and is handled in BOM export. |
| **Backward-Compatibility Facade (`iiot_diagrams`)** | Adding `Routing.CURVE` and new router classes to `diagrams_as_code` without re-exporting in `iiot_diagrams`. | Re-export all new enums, routers, and helper functions in `src/iiot_diagrams/__init__.py` and `src/iiot_diagrams/router.py`. |
| **Layout Sidecar JSON Export** | Attempting to serialize Bezier control points into layout files. | Layout files (`layout.json`) only store element positions $(x, y)$, leaving edge routing deterministic and derived. Keep edge routing out of sidecar files. |

---

## Performance Traps

Patterns that work at small scale but degrade rapidly as diagram complexity increases.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| **Dense Brute-Force Curve Sampling (1000+ steps per edge)** | Diagram generation slows down from 50ms to 5+ seconds on diagrams with 50+ edges. | Use hierarchical AABB broadphase rejection before testing curves; sample chord lengths at $N = 32$ for arc-length. | $> 30$ edges and $> 20$ nodes. |
| **Unbounded De Casteljau Subdivision** | Infinite recursion or `RecursionError` on degenerate or near-coincident inputs. | Set strict maximum recursion depth (`max_depth = 6` or `8`) and minimum bounding box diagonal threshold ($\epsilon = 1.5\text{px}$). | Malformed user diagrams with overlapping shapes. |
| **High-Iteration Newton-Raphson for Label Arc Length** | CPU spikes during layout solving; noticeable lag in interactive or CLI batch mode. | Use piecewise linear chord approximation with binary search ($O(\log N)$ with $N = 32$) instead of iterative root solvers. | $> 50$ labeled curved edges. |
| **Repeated SVG Marker Registration** | Redundant `<marker>` defs emitted for every curved edge, inflating SVG file size. | Cache and register markers uniquely by color and arrow type in `<defs>` (existing `_marker_id_for_color` pattern). | $> 100$ edges in a single diagram. |

---

## Security Mistakes

Domain-specific security considerations for pure-Python static SVG diagram compilation.

| Mistake | Risk | Prevention |
|---------|------|------------|
| **Unsanitized Metadata in SVG `d` Attribute** | SVG path injection / XML malformation if custom routing metadata is injected directly into `<path d="...">`. | Strictly format all path coordinates with typed `float` format specifiers (`f"{val:.2f}"`), never raw string concatenation from metadata. |
| **Unbounded Recursive Subdivision on Malformed Geometry** | Denial of Service (DoS) via `RecursionError` / CPU lockup if coordinates contain `NaN`, `Infinity`, or denormal floats. | Validate that all coordinate floats are finite (`math.isfinite(x)`) and enforce a hard recursion ceiling (`max_depth <= 8`). |
| **ReDoS in Color and Marker Slugification** | Catastrophic backtracking in regex when sanitizing custom color strings for marker IDs. | Use linear-time character filtering or bounded regex (`re.sub(r"[^a-zA-Z0-9_-]", "", color)[:32]`). |

---

## UX Pitfalls

Common visual and user-experience mistakes when rendering curved diagrams.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| **"Spaghetti" Curve Crossing** | Diagram looks like tangled yarn; technical relationships and flow directions become unreadable. | Default to orthogonal routing; restrict curves to high-level conceptual flows; enforce port-normal tangents to keep entry/exit crisp. |
| **Crooked Arrowhead Orientation** | Arrowheads hit node borders at steep angles, piercing node text or sticking out past corners. | Enforce port-normal tangency for control points adjacent to shape ports ($P_2$ parallel to port normal). |
| **Curve Slicing Through Label Text** | Edge stroke passes straight through or behind edge label text, making it illegible. | Render opaque badge rectangles (`shapes.render_badge`) with background contrast behind all edge labels on curves. |
| **Ballooning Curves Leaving Canvas** | Curves arch outside visible diagram canvas; edges appear severed or truncated when embedded in READMEs. | Calculate true Bezier derivative extrema in `_grow_canvas` to ensure the SVG viewport accommodates full curve arcs. |
| **Inconsistent Corner Radii** | Some corners in an orthogonal diagram are rounded with $R = 15$ while others are sharp, looking like a glitch. | Apply consistent fillet radius diagram-wide; only clamp radius down when segment length strictly requires it. |

---

## "Looks Done But Isn't" Checklist

Things that appear complete in simple 2-node demos but fail in real-world architecture diagrams:

- [ ] **Arrowhead Tangent Alignment:** Verify arrowheads enter target shape borders strictly perpendicular (0°, 90°, 180°, 270°) without diagonal slant.
- [ ] **Zero/Near-Zero Distance Safety:** Verify edges between nodes that touch or are separated by $< 10\text{px}$ do not crash with `NaN` or emit invisible arrowheads.
- [ ] **Backward / Feedback Edges:** Verify an edge connecting an East port to a target located West does not produce a self-intersecting "bow-tie" loop.
- [ ] **Short-Segment Fillet Clamping:** Verify consecutive 90° bends separated by $< 2R$ (e.g., tight obstacle clearance jogs) do not invert into triangular "dog ears".
- [ ] **Curve Label Visual Centering:** Verify labels on asymmetric S-curves sit at the true visual midpoint ($s = L/2$) rather than bunched up near one node.
- [ ] **Canvas Auto-Growth for Curves:** Verify curves that bulge upward or outward expand `diagram.width` and `diagram.height` so edges are not cut off.
- [ ] **Diagram-Level Default Inheritance:** Verify `Diagram(routing=Routing.CURVE)` applies curve routing to all edges unless an individual `Edge(routing=...)` explicitly overrides it.
- [ ] **Multi-Segment Obstacle Avoidance:** Verify wide obstacle nodes are circumnavigated using composite splines/fillets rather than a single distorted, clipping cubic curve.
- [ ] **Collinear Vertex Safety in Fillet Router:** Verify collinear straight-line points (0° bends) or 180° reversals do not cause division by zero or NaN arc parameters.

---

## Recovery Strategies

When curved routing pitfalls occur in production, how to recover:

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| **Self-intersecting loop on backward edge** | LOW | Detect $(P_3 - P_0) \cdot \vec{n}_{src} \le 0$; fall back to multi-waypoint channel routing or alternate cardinal ports. |
| **Fillet "dog ears" in dense diagrams** | LOW | Wrap corner radius calculation in `min(R, L_prev / 2, L_next / 2)`; drop radius to 0 if segment $< 2\text{px}$. |
| **Off-center label badge on curve** | LOW | Replace $B(0.5)$ evaluation with 32-chord cumulative length lookup table and binary search. |
| **Curve clipping outside SVG canvas** | LOW | Add derivative extrema quadratic solver ($B'(t) = 0$) to `_grow_canvas` in `layout/pipeline.py`. |
| **Data model breakdown (`Edge.waypoints`)** | MEDIUM | Decouple polyline waypoints from compiled SVG path commands; introduce typed `route_path` or `path_commands` on `Edge`. |
| **Single-curve obstacle collision** | MEDIUM | Fall back to orthogonal channel router for collision waypoints, then apply fillet smoothing to waypoints. |

---

## Pitfall-to-Phase Mapping

How roadmap phases for Milestone v0.8.0 should systematically prevent and verify these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| **Degenerate Control Points / NaN Markers** | Phase 1 (Bezier Routing Engine) | Unit test with overlapping and adjacent elements; verify marker angle is non-NaN and parallel to port normal. |
| **Control Point Overshoot & Bow-Tie Loops** | Phase 1 (Bezier Routing Engine) | Unit test with backward source/target pairs; verify bounding box aspect ratio and absence of self-intersection. |
| **Arrowhead Normal Slant** | Phase 1 (Bezier Routing Engine) | Assert incoming tangent vector $(P_3 - P_2)$ has 0 component along the perpendicular port axis. |
| **Parameter-Space ($t = 0.5$) Label Distortion** | Phase 1 (Bezier Routing Engine) | Test label position on asymmetric curve; verify Euclidean distance along curve to source equals distance to target within 5%. |
| **Data Model Breakage (`Edge.waypoints`)** | Phase 1 (Bezier Routing Engine) | Regression test all existing polyline tests; verify SVG renderer generates `C` commands for curves and `L` for orthogonal. |
| **Fillet Arc Inversion & "Dog Ears"** | Phase 2 (Rounded Corner Fillets) | Test orthogonal paths with short segments ($L < 2R$); verify dynamic clamping prevents inverted arcs. |
| **Collinear Point Zero-Division in Fillets** | Phase 2 (Rounded Corner Fillets) | Test paths with redundant collinear points and 180° turns; verify graceful degradation to straight lines. |
| **Convex Hull / Sampling Collision Flaws** | Phase 3 (Obstacle-Aware Deflection) | Benchmark collision detector against known ground truth (curve grazing rectangle corner); verify 0 false positives and 0 misses. |
| **Single-Curve Distortion on Wide Obstacles** | Phase 3 (Obstacle-Aware Deflection) | Test curve routing across wide obstacle cards; verify multi-segment waypoint spline is generated without bulging. |
| **Diagram vs Edge Configuration Masking** | Phase 4 (Configuration & Polish) | Test `Diagram(routing=Routing.CURVE)` with unconfigured edges; verify all edges inherit curve routing; test explicit edge override. |
| **Canvas Boundary Clipping** | Phase 4 (Configuration & Polish) | Test diagram with high-arcing curves; assert `diagram.width` and `diagram.height` expand to encompass curve extrema. |

---

## Sources

- [SVG 2 Specification — Markers and Path Directionality (W3C)](https://www.w3.org/TR/SVG2/painting.html#MarkerOrientAttribute)
- [A Primer on Bezier Curves (Pomax)](https://pomax.github.io/bezierinfo/) — Numerical arc-length approximation, De Casteljau subdivision, and bounding box derivative extrema
- [De Casteljau's Algorithm & Adaptive Subdivision](https://en.wikipedia.org/wiki/De_Casteljau%27s_algorithm) — Numerically stable Bezier-rectangle intersection without external solvers
- [Graphviz `neato` & `dot` Spline Routing Documentation](https://graphviz.org/docs/attrs/splines/) — Obstacle avoidance via piecewise cubic splines
- Existing repository test suite: `tests/test_routing.py`, `tests/test_renderer_svg.py`, `tests/test_layout_routes.py`

---
*Pitfalls research for: Curved & Bezier Edge Routing (Milestone v0.8.0)*
*Researched: 2026-09-24*
