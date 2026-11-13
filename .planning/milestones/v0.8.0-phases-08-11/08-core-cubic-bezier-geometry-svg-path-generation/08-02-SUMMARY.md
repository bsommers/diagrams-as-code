# Phase 08-02 Summary: Layer 3 Curve Routing Engine

**Phase:** 08 - Core Cubic Bezier Geometry & SVG Path Generation  
**Plan:** 08-02 - Layer 3 Curve Routing Engine  
**Status:** Completed  
**Executed:** 2026-09-25  

---

## Executive Summary

Plan 08-02 implemented Layer 3 curve routing in `src/diagrams_as_code/router.py`. Cardinal port outward unit normal vectors (`PORT_NORMALS`) were defined to strictly align cubic Bezier control handles with port orientations. `CurveRouter` was built to compute exactly 4 waypoints `[P_start, C_1, C_2, P_end]` adhering to distance-proportional handle scaling (D-01..D-07), port normal collinearity (BEZ-02), and non-degenerate handle separation (D-02, D-15). `OrthogonalRouter` seamlessly delegates to `CurveRouter` when `edge.routing == Routing.CURVE`, and `EdgeRouter` provides a unified multi-strategy facade. Top-level exports and comprehensive tests verify invariants across all 16 cardinal port pair combinations.

---

## Tasks Completed

| Task ID | Description | Commits | Status |
|---------|-------------|---------|--------|
| **08-02-01** | Define `PORT_NORMALS` and implement `CurveRouter` skeleton with `resolve_ports` and 4-point waypoint routing contract. | `1834a38` | Complete |
| **08-02-02** | Implement handle length heuristics in `CurveRouter.route` adhering strictly to D-01 through D-07 (perpendicular, parallel, facing, backward flow) with minimum 20px clamp (D-02, D-15). | `6aec3de` | Complete |
| **08-02-03** | Implement `EdgeRouter` facade, `OrthogonalRouter` delegation, top-level exports in `src/diagrams_as_code/__init__.py`, and comprehensive tests in `tests/test_routing.py` and `tests/test_public_api.py`. | `6a1e645` | Complete |

---

## Threat Mitigation & Invariants Verified

- **T-08-01 (Denial of Service / Degenerate Markers):**
  - Minimum handle separation $\|P_3 - C_2\| \ge 20.0\text{px} \gg 1.0\text{px}$ is strictly preserved under all node spacings (D-02, D-15), preventing zero-length arrival vectors and `NaN` arrowhead rotations in SVG renderers.
- **T-08-02 (Tampering / Bow-tie Overlaps):**
  - Backward flow connections enforce a minimum outward clearance of 30.0px (D-07) and blend lateral separation ($d = \max(0.25 \cdot |\Delta_{\text{lateral}}|, 30.0)$), eliminating self-intersecting loops and sharp kinking.
- **Tangency Alignment (BEZ-02):**
  - Exit vector $C_1 - P_0$ and arrival tangent vector $P_3 - C_2$ have 0 perpendicular component (cross product $= 0$) against port normals across all 16 cardinal port combinations.
- **AST Architecture Boundaries:**
  - `router.py` strictly imports Layer 0 (`geometry`) and Layer 2 (`connections`), verified by `tests/test_module_boundaries.py`.
- **API Mirroring:**
  - `CurveRouter`, `EdgeRouter`, and `PORT_NORMALS` are exported in `diagrams_as_code.__all__` and mirrored in `iiot_diagrams.__all__`, verified by `tests/test_public_api.py`.

---

## Verification Results

- `uv run pytest tests/test_routing.py tests/test_public_api.py tests/test_module_boundaries.py` -> 62 passed in 0.16s
- `uv run pytest` -> 466 passed in 11.58s (100% green, 0 regressions)

---

## Next Steps

Proceed to Plan **08-03**: Layer 4 SVG Cubic Bezier Path Rendering (`<path d="M... C...">`, tangential arrowhead marker orientation, and arc-length midpoint protocol badge placement).
