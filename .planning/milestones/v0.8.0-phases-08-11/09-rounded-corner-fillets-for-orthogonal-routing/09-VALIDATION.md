---
phase: 09
slug: rounded-corner-fillets-for-orthogonal-routing
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-09-26
---

# Phase 09 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_geometry.py tests/test_routing.py tests/test_renderer_svg.py -x` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~2.0 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_geometry.py tests/test_routing.py tests/test_renderer_svg.py -x`
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd:verify-work`:** Full suite must be green (100% pass across all 473+ tests)
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | FILLET-03 | T-09-01 | `QuadraticBezier` Bernstein evaluation and velocity tangents | unit | `uv run pytest tests/test_geometry.py -k test_quadratic_bezier` | ✅ | ⬜ pending |
| 09-01-02 | 01 | 1 | FILLET-03 | T-09-01 | `QuadraticBezier` analytical linear root bounding box and arc length | unit | `uv run pytest tests/test_geometry.py -k "test_quadratic_bbox or test_quadratic_arc_length"` | ✅ | ⬜ pending |
| 09-01-03 | 01 | 1 | FILLET-01 | T-09-02 | `Edge` and `Diagram` `corner_radius` attribute, `arc_radius` alias, and non-negative float validation | unit | `uv run pytest tests/test_routing.py -k test_corner_radius_attributes` | ✅ | ⬜ pending |
| 09-01-04 | 01 | 1 | FILLET-01..03 | — | Public API exports and AST boundary compliance | contract | `uv run pytest tests/test_public_api.py tests/test_module_boundaries.py` | ✅ | ⬜ pending |
| 09-02-01 | 02 | 2 | FILLET-02 | T-09-03 | Dynamic 50% segment budget clamping and 2.0px threshold suppression | unit | `uv run pytest tests/test_renderer_svg.py -k test_fillet_radius_clamping` | ✅ | ⬜ pending |
| 09-02-02 | 02 | 2 | FILLET-02 | T-09-04 | Port lead-in straight margin enforcement and obstacle apex clearance guard | unit | `uv run pytest tests/test_renderer_svg.py -k test_fillet_lead_in_and_obstacle_clearance` | ✅ | ⬜ pending |
| 09-02-03 | 02 | 2 | FILLET-03 | T-09-01 | Native SVG `<path d="M... Q...">` emission and $C^1$ tangent continuity | integration | `uv run pytest tests/test_renderer_svg.py -k test_svg_filleted_orthogonal_paths` | ✅ | ⬜ pending |
| 09-03-01 | 03 | 3 | FILLET-01 | — | Diagram-level default radius cascading and edge-level override verification | integration | `uv run pytest tests/test_renderer_svg.py -k test_diagram_corner_radius_cascade` | ✅ | ⬜ pending |
| 09-03-02 | 03 | 3 | FILLET-01..03 | — | Full suite regression and gallery diagram zero-diff byte verification | regression | `uv run pytest && uv run python main.py && git diff --exit-code -- output/` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing test infrastructure covers all phase requirements (`tests/test_geometry.py`, `tests/test_routing.py`, and `tests/test_renderer_svg.py` exist and are ready for test expansion).

---

## Manual Verification Procedures

### 1. Gallery Diagram Zero-Diff Baseline Check
- Run `uv run python main.py`
- Run `git diff --exit-code -- output/ README.md docs/ icons/`
- Verify zero diff when `corner_radius` is not configured (D-02 sharp default preservation).

### 2. Visual Quality of Rounded Fillets
- Render an example diagram with `corner_radius=12.0`
- Inspect SVG output in browser to verify corners are smoothly rounded with 90° fillet arcs without "dog ear" loops or overlaps.
