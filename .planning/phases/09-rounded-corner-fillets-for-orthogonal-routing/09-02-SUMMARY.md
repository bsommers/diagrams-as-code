# Plan 09-02 Summary: Layer 4 SVG Fillet Rendering Engine

**Phase:** 09-rounded-corner-fillets-for-orthogonal-routing  
**Plan:** 09-02  
**Status:** Completed  
**Outcome:** All 3 tasks executed and verified; 487/487 tests passing.

## Accomplishments

1. **Layer 4 Vector Fillet Generator (`_render_filleted_path`)**:
   - Implemented `_render_filleted_path(pts, corner_radius, obstacles)` in `src/diagrams_as_code/renderer_svg.py`.
   - $C^1$ tangent continuity using native SVG quadratic Bezier `Q` commands connecting tangent points $T_1 = P_c - \mathbf{u}_{\text{in}} R$ and $T_2 = P_c + \mathbf{u}_{\text{out}} R$.
   - Analytical 50% segment budget clamping: $R_{\text{eff}} \le \min(R, L_{\text{in}} / 2, L_{\text{out}} / 2)$ to eliminate overlapping curves and "dog ear" loops on short segments.
   - Preserved straight port lead-ins: reserved $\min(10.0, L / 2)$ on segments entering or exiting ports so arrowheads rest flush on perpendicular segments.
   - Strict 90° orthogonal turn detection ($|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$), leaving collinear points and turnarounds sharp.
   - Obstacle clearance guard: inside corner apex displacement checked against obstacle bounding boxes expanded by 4.0px margin, clamping radius to ensure $\ge 4.0\text{px}$ clearance.
   - Threshold suppression: suppressed micro-arcs with $R_{\text{eff}} < 2.0\text{px}$ to sharp right angles (`L P_c.x P_c.y`) to avoid sub-pixel rasterization artifacts.

2. **SVGRenderer Integration & Protocol Badge Centering**:
   - Integrated filleted path dispatch in `SVGRenderer._render_edges`: edges with `Routing.ORTHOGONAL` and `corner_radius > 0` are emitted via `_render_filleted_path`.
   - Obstacle extraction: passed diagram non-terminal element bounding boxes into `_render_filleted_path`.
   - Waypoints integrity preserved: `edge.waypoints` remains strictly the clean sequence of sharp Manhattan corner vertices `[P_0, ..., P_n]`.
   - Longest-segment protocol badge centering: positioned protocol badge labels at the midpoint of the longest straight segment, keeping labels on flat segments rather than straddling corner bends.

3. **Comprehensive Unit & Integration Test Suite**:
   - Added 6 thorough tests to `tests/test_renderer_svg.py` covering:
     * Native `Q` command syntax and $C^1$ continuity verification.
     * 50% segment budget dynamic clamping on short segments (18px segment with 15px requested radius clamped to 9px).
     * Micro-arc threshold suppression (< 2.0px clamped radius suppresses to sharp corner).
     * Port lead-in preservation (16px departure segment preserves 8px lead-in).
     * Obstacle clearance guard (apex maintains $\ge 4.0\text{px}$ clearance from obstacle bounds).
     * Protocol badge placement centered on the longest straight segment midpoint.
   - Full test suite passing cleanly (487 passed in ~11s).
   - AST module boundaries (`tests/test_module_boundaries.py`) and public API (`tests/test_public_api.py`) cleanly verified.

## Verification

- `uv run pytest tests/test_renderer_svg.py -k orthogonal_fillet` (6 passed)
- `uv run pytest tests/test_renderer_svg.py` (34 passed)
- `uv run pytest tests/test_module_boundaries.py tests/test_public_api.py` (38 passed)
- `uv run pytest` (487 passed in 11.83s)

## Commits

- `feat(renderer): implement _render_filleted_path with dynamic clamping and obstacle guards` (`523fc51`)
- `feat(renderer): integrate filleted path emission and longest-segment badge centering` (`a38738a`)
- `test(renderer): add unit and integration tests for svg fillet rendering engine` (`490636d`)
