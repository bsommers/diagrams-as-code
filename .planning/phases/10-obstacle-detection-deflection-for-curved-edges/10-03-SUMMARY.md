# Plan 10-03 Summary: Deflection Waypoint Topology, Corridor Selection & Badge Centering

**Phase:** 10-obstacle-detection-deflection-for-curved-edges  
**Plan:** 10-03  
**Status:** Completed  
**Outcome:** All 3 tasks executed and verified; 517/517 tests passing.

## Accomplishments

1. **Layer 3 Adaptive Deflection Waypoint Topology (`CurveRouter._build_deflected_spline_horizontal`, `_build_deflected_spline_vertical`)**:
   - Implemented adaptive waypoint synthesis distinguishing compact ($W \le 2 \times \text{clearance}$) vs wide ($W > 2 \times \text{clearance}$) obstacles (D-07):
     - Compact obstacles: routes through a single apex waypoint ($N=2$ segments, $3N+1 = 7$ points).
     - Wide obstacles: routes through 2 corner clearance waypoints ($N=3$ segments, $3N+1 = 10$ points) avoiding convex corner clipping.
   - Enforced corner clearance invariant: all intermediate waypoints maintain $\ge 15.0\text{px}$ distance from all obstacle corners (D-11, T-10-03).
   - Generated collinear handles along the bypass corridor, producing flat bypass segments with zero inward bulging (D-08).

2. **Minimal Deviation Corridor Selection & Secondary Obstacle Avoidance (`CurveRouter._select_deflected_corridor`)**:
   - Evaluates TOP and BOTTOM corridors (or LEFT and RIGHT for vertical flows) (D-09).
   - Chooses the collision-free corridor with minimal total arc length (minimal deviation heuristic D-09).
   - Automatically routes via alternative corridor or expands outward past secondary obstacles when preferred corridors are blocked (D-10).
   - Preserves 100% backward compatibility on unobstructed curves, returning exact 4 points (D-16).

3. **Strict $C^1$ Continuity & Full $3N+1$ Waypoint Data Contract**:
   - Enforces collinear arrival handle $C_{\text{in}}$ and departure handle $C_{\text{out}}$ with $\mathbf{u}_{\text{out}} = \mathbf{u}_{\text{in}}$ along direction of travel (zero angular deviation) across all deflection waypoints (D-05).
   - Populates `Edge.waypoints` with full $3N+1$ Bezier control polygon for seamless SVG path generation (`M... C... C...`) (D-06).

4. **Layer 4 Longest-Segment Arc-Length Midpoint Badge Centering (`SVGRenderer._render_edges`)**:
   - Decomposes multi-segment splines into individual `CubicBezier` segments, evaluates their Euclidean arc lengths, and locates the longest segment (D-12).
   - Places protocol badges precisely at the physical arc-length midpoint $s = L / 2$ of the longest segment, ensuring labels rest on straight clearance chords rather than sharp entry curves (D-12, T-10-07).
   - Added `self.curve_router` in `SVGRenderer` to automatically route curved edges with missing waypoints.

## Verification

- `uv run pytest tests/test_routing.py -k test_curve_deflection` (5 passed)
- `uv run pytest tests/test_routing.py -k "c1_continuity or backward_compatibility"` (2 passed)
- `uv run pytest tests/test_renderer_svg.py -k "test_svg_multi_segment_spline_badge or test_svg_render_deflected_spline"` (2 passed)
- `uv run pytest tests/test_routing.py tests/test_renderer_svg.py` (79 passed)
- `uv run pytest tests/test_module_boundaries.py tests/test_public_api.py` (42 passed)
- `uv run pytest` (517 passed in 11.48s)

## Commits

- `feat(router): implement adaptive deflection waypoint topology, corridor selection, and C1 continuity` (`c576059`)
- `feat(renderer): center protocol badges on longest spline segment midpoint` (`e719910`)
