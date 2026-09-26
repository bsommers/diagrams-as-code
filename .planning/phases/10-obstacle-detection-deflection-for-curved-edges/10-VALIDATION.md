---
phase: 10
slug: obstacle-detection-deflection-for-curved-edges
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-09-26
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x / 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_geometry.py tests/test_routing.py tests/test_renderer_svg.py -x` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~3.0 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_geometry.py tests/test_routing.py tests/test_renderer_svg.py -x`
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd:verify-work`:** Full suite must be green (100% pass across all 492+ tests)
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | CURVEOBS-01 | T-10-01 | `CubicBezier.subdivide()` De Casteljau subdivision at arbitrary $t$ | unit | `uv run pytest tests/test_geometry.py -k test_cubic_bezier_subdivision` | ✅ | ⬜ pending |
| 10-01-02 | 01 | 1 | CURVEOBS-01 | T-10-01 | `CubicBezier.intersects_rect()` two-tier AABB broadphase + De Casteljau narrowphase | unit | `uv run pytest tests/test_geometry.py -k test_cubic_bezier_intersects_rect` | ✅ | ⬜ pending |
| 10-01-03 | 01 | 1 | CURVEOBS-01..03 | — | Public API exports and AST boundary compliance | contract | `uv run pytest tests/test_public_api.py tests/test_module_boundaries.py` | ✅ | ⬜ pending |
| 10-02-01 | 02 | 2 | CURVEOBS-01 | T-10-02 | `CurveRouter` obstacle normalization, exclusion filters, and clearance inflation | unit | `uv run pytest tests/test_routing.py -k test_curve_router_obstacle_filtering` | ✅ | ⬜ pending |
| 10-02-02 | 02 | 2 | CURVEOBS-03 | T-10-03 | Reverse-flow automatic outward port resolution (NORTH/SOUTH) and lateral escape corridors | unit | `uv run pytest tests/test_routing.py -k test_curve_router_reverse_flow` | ✅ | ⬜ pending |
| 10-03-01 | 03 | 3 | CURVEOBS-02 | T-10-04 | Clearance channel bypass selection (minimal deviation) and adaptive 1–2 waypoint topology | unit | `uv run pytest tests/test_routing.py -k test_curve_router_deflection_waypoints` | ✅ | ⬜ pending |
| 10-03-02 | 03 | 3 | CURVEOBS-02 | T-10-04 | $C^1$ continuous multi-segment cubic spline synthesis ($3N+1$ points) | unit | `uv run pytest tests/test_routing.py -k test_curve_router_c1_spline_continuity` | ✅ | ⬜ pending |
| 10-03-03 | 03 | 3 | CURVEOBS-02 | — | Layer 4 protocol badge placement along longest spline segment midpoint | unit | `uv run pytest tests/test_renderer_svg.py -k test_svg_spline_badge_placement` | ✅ | ⬜ pending |
| 10-04-01 | 04 | 4 | CURVEOBS-01..03 | — | End-to-end integration: multi-obstacle detours and mixed routing coexistence | integration | `uv run pytest tests/test_e2e.py -k test_curved_obstacle_avoidance` | ✅ | ⬜ pending |
| 10-04-02 | 04 | 4 | CURVEOBS-01..03 | — | Full suite regression, Bezier benchmark eval, and gallery zero-diff byte verification | regression | `uv run pytest && uv run python tools/eval_bezier.py && uv run python main.py && git diff --exit-code -- output/` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing test infrastructure covers all phase requirements (`tests/test_geometry.py`, `tests/test_routing.py`, and `tests/test_renderer_svg.py` exist and are ready for test expansion).

---

## Manual Verification Procedures

1. **Visual Spline Quality:** Run deflected curve examples and inspect SVG paths for smooth curvature without sharp kinks at waypoint transitions.
2. **Obstacle Clearance Inspection:** Verify in SVG output that all deflected curve paths maintain $\ge 15.0\text{px}$ clearance from obstacle bounding box boundaries.
3. **Back-Edge Lateral Escape:** Inspect backward connections to verify they bypass source and target shapes cleanly without clipping node interiors or creating self-intersecting loops.
