# Plan 10-01 Summary: Geometric Subdivision and Collision Math

**Phase:** 10-obstacle-detection-deflection-for-curved-edges  
**Plan:** 10-01  
**Status:** Completed  
**Outcome:** All 3 tasks executed and verified; 505/505 tests passing.

## Accomplishments

1. **Layer 0 Vector Subdivision and Collision Detection (`geometry.CubicBezier`)**:
   - Implemented `CubicBezier.subdivide(t=0.5)` and `CubicBezier.split(t=0.5)` alias using De Casteljau bisection algorithm in `src/diagrams_as_code/geometry.py`.
   - Implemented `CubicBezier.intersects_rect(rect, max_depth=4)` with two-tier collision testing:
     - Tier 1: Fast $O(1)$ analytical AABB broadphase filter using derivative roots (`self.bbox().intersects(rect)`).
     - Tier 2: Recursive De Casteljau narrowphase capped at `max_depth = 4` with control-net bounding box pruning and early-exit on the first intersecting leaf.
   - Guarded recursion depth to prevent stack exhaustion (clamped between 1 and 8).
   - Added comprehensive tests in `tests/test_geometry.py` covering subdivision at midpoint and asymmetric $t=0.3$, endpoint matching, parameter boundary handling, broadphase clear miss, direct hit, grazing corner miss with zero false positives, corner clipping hit, and depth capping.

2. **Layer 2/5 Edge and Diagram Clearance API Contracts (`Edge.clearance`)**:
   - Added `clearance: Optional[float] = None` attribute to `Edge.__init__` in `src/diagrams_as_code/connections.py` with default `15.0px` matching `OrthogonalRouter`.
   - Implemented static validator `Edge._validate_clearance` enforcing non-negative finite floats and rejecting negative values, booleans, strings, NaN, and Inf with `ValueError`.
   - Added `clearance` property getter and setter to `Edge`.
   - Forwarded `clearance` through `_EdgeBuilder` and `Diagram.connect()` in `src/diagrams_as_code/diagram.py`, supporting diagram-level default inheritance and explicit fluent overrides.
   - Added unit tests in `tests/test_routing.py` verifying default value, setter updates, invalid type rejections, and diagram cascading.

3. **Public API Parity & AST Boundary Compliance**:
   - Verified `CubicBezier` methods (`subdivide`, `split`, `intersects_rect`) and `Edge.clearance` property accessibility across both `diagrams_as_code` and facade `iiot_diagrams` in `tests/test_public_api.py`.
   - Verified AST module boundary rules (`tests/test_module_boundaries.py`) ensuring `geometry.py` remains pure Layer 0 with 0 internal imports and all layers strictly import downward.

## Verification

- `uv run pytest tests/test_geometry.py -k "subdivision or intersects_rect"` (6 passed)
- `uv run pytest tests/test_routing.py -k test_edge_clearance` (3 passed)
- `uv run pytest tests/test_public_api.py tests/test_module_boundaries.py` (42 passed)
- `uv run pytest` (505 passed in 12.47s)

## Commits

- `feat(geometry): implement cubic Bezier subdivision and two-tier collision detection` (`3d00de6`)
- `feat(connections): add Edge clearance attribute with strict validation and diagram cascading` (`47441d9`)
- `test(api): verify CubicBezier methods and Edge clearance accessibility in public API` (`3304c0a`)
