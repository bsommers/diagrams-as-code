# Plan 10-02 Summary: Obstacle Normalization, Collision Detection & Reverse-Flow Escape

**Phase:** 10-obstacle-detection-deflection-for-curved-edges  
**Plan:** 10-02  
**Status:** Completed  
**Outcome:** All 3 tasks executed and verified; 509/509 tests passing.

## Accomplishments

1. **Layer 3 Obstacle Normalization & Two-Tier Collision Detection (`CurveRouter._normalize_obstacles`, `_detect_collisions`)**:
   - Implemented `CurveRouter._normalize_obstacles` in `src/diagrams_as_code/router.py`:
     - Excludes edge source and target nodes and matching IDs (D-03).
     - Excludes enclosing container groups containing `p_start` or `p_end` (D-03).
     - Standardizes heterogeneous input elements (Shapes, Groups, Rects) into clean `Rect` bounding boxes.
   - Implemented `CurveRouter._detect_collisions`:
     - Expands candidate obstacle bounding boxes by `edge.clearance` (15.0px default) (D-01, D-02).
     - Tests clearance-inflated obstacles against candidate curves via `CubicBezier.intersects_rect`.
   - Added unit tests `test_curve_router_obstacle_filtering` and `test_curve_router_collision_detection` in `tests/test_routing.py`.

2. **Automatic Lateral Port Selection for Reverse-Flow Curves (`CurveRouter.resolve_ports`)**:
   - Enhanced `CurveRouter.resolve_ports` to detect reverse-flow edges ($\Delta x < 0$ in horizontal diagrams or $\Delta y < 0$ in vertical diagrams) when ports are unspecified (D-14, CURVEOBS-03).
   - Evaluates obstacle bounding boxes to automatically choose outward lateral cardinal ports (`NORTH -> NORTH` or `SOUTH -> SOUTH` for horizontal flows; `WEST -> WEST` or `EAST -> EAST` for vertical flows), routing around node perimeters instead of penetrating node interiors.
   - Added unit test `test_curve_router_reverse_flow_automatic_port_resolution` in `tests/test_routing.py`.

3. **Lateral Clearance Escape Corridors for Reverse-Flow Explicit Ports (`CurveRouter._route_reverse_flow_explicit_ports`)**:
   - Implemented outer lateral clearance escape corridors for reverse-flow connections with explicit facing ports (D-13, D-15, CURVEOBS-03).
   - Projects escape waypoints laterally beyond shape boundaries with a minimum clearance margin of $30.0\text{px}$ (D-13).
   - Generates a 3-segment $C^1$ continuous spline (10 control points adhering to the $3N+1$ contract D-06) that routes cleanly above/around shapes and intervening obstacles without self-intersecting bow-tie loops (T-10-04).
   - Safely guards tangent normalization against zero-division or NaN on coincident nodes (T-10-02).
   - Added unit test `test_curve_router_reverse_flow_explicit_ports_escape` in `tests/test_routing.py`.

## Verification

- `uv run pytest tests/test_routing.py -k "test_curve_router_obstacle_filtering or test_curve_router_collision_detection"` (2 passed)
- `uv run pytest tests/test_routing.py -k "test_curve_router_reverse_flow"` (2 passed)
- `uv run pytest tests/test_routing.py` (35 passed)
- `uv run pytest` (509 passed in 13.69s)

## Commits

- `feat(router): implement obstacle normalization and clearance collision detection` (`9ac0ba4`)
- `feat(router): implement automatic lateral port resolution for reverse-flow edges` (`d4a0564`)
- `feat(router): implement lateral escape corridors for reverse-flow explicit ports` (`32b4142`)
