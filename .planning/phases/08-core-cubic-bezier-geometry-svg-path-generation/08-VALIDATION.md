---
phase: 08
slug: core-cubic-bezier-geometry-svg-path-generation
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-09-25
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_geometry.py tests/test_routing.py tests/test_renderer_svg.py -x` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~1.5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_geometry.py tests/test_routing.py tests/test_renderer_svg.py -x`
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd:verify-work`:** Full suite must be green (100% pass across all 453+ tests)
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | BEZ-01 | T-08-01 | Point vector operators and CubicBezier evaluation | unit | `uv run pytest tests/test_geometry.py -k test_cubic_bezier` | ✅ | ⬜ pending |
| 08-01-02 | 01 | 1 | BEZ-01 | T-08-01 | Derivative root bounding box and arc-length midpoint | unit | `uv run pytest tests/test_geometry.py -k "test_bbox or test_arc_length"` | ✅ | ⬜ pending |
| 08-01-03 | 01 | 1 | BEZ-01 | — | Public API exports and AST boundary compliance | contract | `uv run pytest tests/test_public_api.py tests/test_module_boundaries.py` | ✅ | ⬜ pending |
| 08-02-01 | 02 | 2 | BEZ-01 | T-08-02 | Edge.waypoints stores exactly 4 points for Routing.CURVE | unit | `uv run pytest tests/test_routing.py -k test_curve_routing_edge_dispatch` | ✅ | ⬜ pending |
| 08-02-02 | 02 | 2 | BEZ-02 | T-08-02 | Cardinal port normal tangency alignment | unit | `uv run pytest tests/test_routing.py -k test_curve_router_port_tangent_alignment` | ✅ | ⬜ pending |
| 08-02-03 | 02 | 2 | BEZ-03 | T-08-02 | Distance-proportional handle scaling and clearance | unit | `uv run pytest tests/test_routing.py -k test_curve_router_handle_scaling_heuristics` | ✅ | ⬜ pending |
| 08-03-01 | 03 | 3 | BEZ-04 | T-08-03 | SVG <path d="M... C..."> emission and marker orientation | integration | `uv run pytest tests/test_renderer_svg.py -k test_svg_render_cubic_bezier_path` | ✅ | ⬜ pending |
| 08-03-02 | 03 | 3 | BEZ-05 | T-08-04 | Protocol badge placement at arc-length midpoint | integration | `uv run pytest tests/test_renderer_svg.py -k test_curved_edge_protocol_badge` | ✅ | ⬜ pending |
| 08-03-03 | 03 | 3 | BEZ-01..05 | — | Full suite regression gate | regression | `uv run pytest` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing test infrastructure covers all phase requirements (`tests/test_geometry.py`, `tests/test_routing.py`, and `tests/test_renderer_svg.py` exist and are ready for test expansion).

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
