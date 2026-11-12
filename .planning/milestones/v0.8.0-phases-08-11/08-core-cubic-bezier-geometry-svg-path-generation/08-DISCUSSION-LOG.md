# Phase 8: Core Cubic Bezier Geometry & SVG Path Generation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-25  
**Phase:** 8-Core Cubic Bezier Geometry & SVG Path Generation  
**Areas discussed:** Handle Length & S-Curve Tension Heuristics, Non-Facing & Lateral Port Tangent Behavior, Protocol Badge Midpoint Computation, Waypoint Data Contract & Storage  

---

## Handle Length & S-Curve Tension Heuristics

| Option | Description | Selected |
|--------|-------------|----------|
| d = max(0.5 * delta_axis, 25.0) | Industry standard (React Flow/XYFlow) creating natural S-curves without bulging | ✓ |
| d = max(0.35 * delta_axis, 20.0) | Tighter, more direct curves with flatter midpoints | |
| Isotropic scaling d = 0.5 * hypot(dx, dy) | Total Euclidean distance scaling regardless of flow direction | |

**User's choice:** `d = max(0.5 * delta_axis, 25.0)`  
**Notes:** Minimum handle length enforced at 20px with no upper clamp. When nodes are close along the flow axis but have large lateral offsets, lateral offset is blended ($d = \max(0.5 \cdot \Delta_{\text{axis}}, 0.25 \cdot |\Delta_{\text{lateral}}|, 20.0)$). Fixed default heuristic ($k=0.5$) used for Phase 8.

---

## Non-Facing & Lateral Port Tangent Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Independent axis scaling | Scale each handle by its axis delta along its port normal: d1 = max(0.5 * abs(dx), 25.0), d2 = max(0.5 * abs(dy), 25.0) | ✓ |
| Equal Euclidean distance | Equal handle lengths based on Euclidean distance | |

**User's choice:** Independent axis scaling for perpendicular ports  
**Notes:** For same-side / parallel ports (e.g. NORTH to NORTH), project handles outward with vertical clearance proportional to horizontal separation: $d = \max(0.5 \cdot |\Delta x|, 30.0)$. For reverse-facing connections in Phase 8, outward normal projection enforces a minimum clearance offset of 30px to prevent handle crossover. Automatic port resolution reuses `router.resolve_ports(edge)`.

---

## Protocol Badge Midpoint Computation

| Option | Description | Selected |
|--------|-------------|----------|
| Piecewise chord arc-length parameterization | 16–32 point chord sampling; binary search for physical midpoint s = L/2 | ✓ |
| Analytical parametric evaluation at t=0.5 | Instant O(1) evaluation via B(0.5) = (P0 + 3P1 + 3P2 + P3)/8 | |
| Fast hybrid | t=0.5 for symmetric curves, chord sampling for asymmetric curves | |

**User's choice:** Piecewise chord arc-length parameterization (16–32 points)  
**Notes:** Protocol badges remain horizontal ($0^\circ$ rotation) for readability. Solid background pill rect obscures underlying curve stroke cleanly. Reuses existing `renderer_svg.py` badge sizing (height 18px, padding 8px per side).

---

## Waypoint Data Contract & Storage

| Option | Description | Selected |
|--------|-------------|----------|
| 4-point list in Edge.waypoints | Exactly 4 points: [P_start, C1, C2, P_end] stored in Edge.waypoints: list[Point] | ✓ |
| Dedicated curve_geometry attribute | Store CubicBezier instance directly on Edge alongside polyline waypoints | |

**User's choice:** Exactly 4 points: `[P_start, C_1, C_2, P_end]` in `Edge.waypoints`  
**Notes:** 100% backward compatible with existing serializers and AST boundaries. Minimum handle distance $\|P_3 - P_2\| \ge 1.0\text{px}$ along port normal ray enforced to prevent SVG arrowhead marker NaN rotation bugs. `geometry.CubicBezier` designed as a clean single-segment primitive ready for multi-segment splines in Phase 10.

---

## Claude's Discretion

- Chord sample resolution (16 vs 32 points) for arc-length parameterization tuned for optimal performance during testing.
- Internal helper structure in `router.py` adhering to Layer 3 contracts.

## Deferred Ideas

- User-configurable `curvature: float = 0.5` parameter on `Edge` / `Diagram` (deferred to v0.8.x).
- Rounded corner fillets on Manhattan orthogonal routing (Phase 9).
- Obstacle avoidance & multi-segment deflected splines for curved edges (Phase 10).
- Diagram-level default routing configuration cascade (Phase 11).
