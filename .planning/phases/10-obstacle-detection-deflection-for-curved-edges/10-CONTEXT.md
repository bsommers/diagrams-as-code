# Phase 10: Obstacle Detection & Deflection for Curved Edges - Context

**Gathered:** 2026-09-26  
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 10 delivers obstacle collision detection for candidate cubic Bezier curves (`CURVEOBS-01`), collision-free multi-segment $C^1$ spline deflection through clearance channel waypoints (`CURVEOBS-02`), and outer lateral clearance corridor routing for reverse-flow back-edges (`CURVEOBS-03`). The engine detects when a cubic curve intersects intervening nodes or groups using bounding box broadphase and recursive De Casteljau subdivision, deflects the trajectory through clean channel waypoints emitted as smooth multi-segment cubic Bezier splines (`M... C... C...`), and adaptively routes backward connections around source and target nodes without clipping.

</domain>

<decisions>
## Implementation Decisions

### Collision Detection Strategy (CURVEOBS-01)
- **D-01:** Two-tier collision testing: Fast Axis-Aligned Bounding Box (AABB) broadphase filter using the cubic Bezier tight bounding box (`CubicBezier.bbox()`), followed by narrowphase recursive De Casteljau subdivision up to depth 4 ($2^4 = 16$ sub-segment bounding boxes) against candidate obstacle rectangles.
- **D-02:** Standard clearance inflation buffer: Inflate obstacle bounding boxes by `edge.clearance` (default 15.0px, matching `OrthogonalRouter`) to prevent visual touching and maintain generous clearance between curves and node borders.
- **D-03:** Source and target exclusion: Exclude the edge's source and target elements from the obstacle list, as well as ancestor/child container groups that legitimately enclose the connected elements.
- **D-04:** Early-exit optimization: The narrowphase subdivision exits immediately upon detecting the first intersecting sub-segment bounding box, keeping collision checks fast ($O(M)$ where $M$ is the number of broadphase-filtered obstacles).

### Deflection Waypoints & Spline Continuity (CURVEOBS-02)
- **D-05:** Strict $C^1$ Spline Continuity: Multi-segment cubic Bezier splines maintain collinear, opposite tangent vectors at intermediate waypoints $W_i$. The arrival handle $C_{\text{in}}$ and departure handle $C_{\text{out}}$ satisfy $\mathbf{u}_{\text{out}} = -\mathbf{u}_{\text{in}}$, guaranteeing smooth, kink-free transitions across deflection waypoints.
- **D-06:** Waypoint Data Contract: Multi-segment curves are stored in `Edge.waypoints` as a full $3N+1$ Bezier control polygon `[P_0, C_{1a}, C_{1b}, P_1, C_{2a}, C_{2b}, P_2, ...]`, maintaining 100% compliance with `SVGRenderer._render_edges` multi-segment SVG path generation (`M... C... C...`).
- **D-07:** Adaptive Waypoint Topology: For compact intervening obstacles, route through a single apex waypoint offset by clearance from the obstacle border. For wide or tall obstacles, insert 2 parallel corner clearance waypoints to prevent cutting corners.
- **D-08:** Tangent Orientation at Waypoints: Orient intermediate waypoint tangents parallel to the obstacle's cleared boundary edge, ensuring the curve smoothly sweeps past the obstacle rather than bowing inward toward the boundary.

### Clearance Channel & Detour Path Selection (CURVEOBS-02)
- **D-09:** Minimal Deviation Heuristic: When an obstacle blocks the direct Bezier path, evaluate both lateral bypass corridors (top vs bottom for horizontal flows, left vs right for vertical flows) and select the corridor with the minimal deflected arc length and zero secondary collisions.
- **D-10:** Secondary Obstacle Avoidance: If the preferred bypass corridor intersects an adjacent obstacle, evaluate the opposite corridor; if both corridors have secondary obstacles, route through outer clearance corridors until a collision-free path is found.
- **D-11:** Minimum Corner Clearance Invariant: Deflection waypoints must maintain at least 15.0px clearance from all obstacle corners, preventing multi-segment curves from clipping convex vertices.
- **D-12:** Protocol Badge Positioning on Splines: For multi-segment deflected curves, place the protocol badge along the longest spline segment's physical arc-length midpoint, ensuring clear typography and non-overlapping backgrounds.

### Reverse-Flow (Back-Edge) Escape Routing (CURVEOBS-03)
- **D-13:** Outer Lateral Clearance Corridors: For reverse-flow connections (e.g. backward edges against diagram flow, $\Delta x < 0$ in LR layout), route via an outer lateral clearance corridor (NORTH or SOUTH of the intervening elements), preventing curves from cutting across the source and target node interiors.
- **D-14:** Automatic Back-Edge Port Resolution: When ports are unspecified on a reverse-flow curved edge, resolve to outward lateral cardinal ports (NORTH to NORTH or SOUTH to SOUTH based on corridor availability) rather than facing ports, establishing a clean bypass loop.
- **D-15:** Lateral Escape Clearance Margin: Project back-edge control handles and clearance waypoints beyond the outermost boundary of the involved nodes with a minimum clearance margin of 30.0px, preventing bow-tie self-intersections.
- **D-16:** Backward Compatibility & Pure Python Invariant: The collision detection and deflection algorithms remain 100% pure Python standard library math (zero external C-dependencies), executing in sub-millisecond time and preserving zero-diff output on existing non-colliding gallery diagrams.

### Claude's Discretion
- Exact De Casteljau recursion threshold (depth 4 vs 5) based on benchmark evaluation and performance measurements.
- Internal helper structure in `router.py` (e.g. `SplineRouter` or methods on `CurveRouter`).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Roadmap & Requirements
- `.planning/ROADMAP.md` — Phase 10 goals, requirements `CURVEOBS-01`, `CURVEOBS-02`, `CURVEOBS-03`, and success criteria.
- `.planning/REQUIREMENTS.md` — Full requirement statements for `CURVEOBS-01` through `CURVEOBS-03`.

### Milestone Research
- `.planning/research/SUMMARY.md` — Synthesized mathematical formulation, stack choices, and phase sequencing.
- `.planning/research/ARCHITECTURE.md` — Decoupled 5-layer system structure, waypoint contract, and component map.
- `.planning/research/PITFALLS.md` — Mitigations for obstacle corner clipping, spline kink artifacts, and bow-ties.
- `.planning/research/STACK.md` — Pure Python standard library math primitives (`math.hypot`, vector operators).

### Phase Predecessors
- `.planning/phases/08-core-cubic-bezier-geometry-svg-path-generation/08-CONTEXT.md` — Single-segment cubic Bezier primitives and handle scaling.
- `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-CONTEXT.md` — Obstacle clearance guards and quadratic Bezier math.

</canonical_refs>
