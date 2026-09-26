# Plan 09-01 Summary: Layer 0 Geometry and API Contracts

**Phase:** 09-rounded-corner-fillets-for-orthogonal-routing  
**Plan:** 09-01  
**Status:** Completed  
**Outcome:** All 3 tasks executed and verified; 481/481 tests passing.

## Accomplishments

1. **Layer 0 Vector Primitive (`geometry.QuadraticBezier`)**:
   - Implemented `@dataclass(frozen=True) class QuadraticBezier(p0, p1, p2)` in `src/diagrams_as_code/geometry.py`.
   - Analytical Bernstein polynomial evaluation via `point_at(t)`.
   - First-derivative velocity tangent vectors via `tangent_at(t)`.
   - Exact tight axis-aligned bounding box calculation via `bbox()` using analytical linear derivative roots.
   - Uniform parameter sampling via `sample(n)` and cumulative chord length via `arc_length(num_samples)`.
   - Unit tests covering evaluation, tangents, bounding box vs 1,001 numerical samples, and frozen immutability in `tests/test_geometry.py`.

2. **Layer 2/5 Edge and Diagram API Contracts (`corner_radius` / `arc_radius`)**:
   - Added `corner_radius` and symmetric alias `arc_radius` to `Edge` in `src/diagrams_as_code/connections.py`.
   - Implemented static validator `Edge._validate_corner_radius` enforcing non-negative finite floats and rejecting negative values, booleans, strings, NaN, and Inf with `ValueError`.
   - Preserved default sharp corner semantics (`corner_radius=None`).
   - Added `corner_radius` and `arc_radius` to `_EdgeBuilder` and `Diagram` in `src/diagrams_as_code/diagram.py`.
   - Implemented diagram-level default cascading down to fluent connections (`s1 >> s2`), `diag.connect(...)`, and `diag.solve()`, while honoring explicit edge overrides.
   - Comprehensive test suites added to `tests/test_routing.py` and `tests/test_diagram_api.py`.

3. **Public API Parity & AST Boundary Compliance**:
   - Exported `QuadraticBezier` in `diagrams_as_code.__all__` and verified automatic mirroring in `iiot_diagrams.__all__`.
   - Verified AST module boundary rules (`tests/test_module_boundaries.py`) ensuring `geometry.py` has 0 internal imports (Layer 0) and connections/diagram strictly import downward.

## Verification

- `uv run pytest tests/test_geometry.py -k test_quadratic_bezier` (3 passed)
- `uv run pytest tests/test_routing.py tests/test_diagram_api.py -k "corner_radius or arc_radius"` (3 passed)
- `uv run pytest tests/test_public_api.py tests/test_module_boundaries.py` (38 passed)
- `uv run pytest` (481 passed in 12.06s)

## Commits

- `feat(geometry): implement QuadraticBezier primitive and unit tests` (`425b635`)
- `feat(connections): add corner_radius and arc_radius validation and diagram cascading` (`2f04272`)
- `feat(api): export QuadraticBezier in public API and facade` (`54480f2`)
