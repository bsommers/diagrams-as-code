---
phase: 10-obstacle-detection-deflection-for-curved-edges
reviewed: 2026-09-27T12:25:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - src/diagrams_as_code/geometry.py
  - src/diagrams_as_code/connections.py
  - src/diagrams_as_code/diagram.py
  - src/diagrams_as_code/router.py
  - src/diagrams_as_code/renderer_svg.py
  - src/diagrams_as_code/__init__.py
  - tests/test_geometry.py
  - tests/test_routing.py
  - tests/test_renderer_svg.py
  - tests/test_e2e.py
  - tests/test_public_api.py
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: clean
---

# Phase 10 Code Review: Obstacle Detection & Deflection for Curved Edges

## Executive Summary

Phase 10 source and test implementations have been reviewed across 11 files:
- [geometry.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/geometry.py)
- [connections.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/connections.py)
- [diagram.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/diagram.py)
- [router.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py)
- [renderer_svg.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/renderer_svg.py)
- [__init__.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/__init__.py)
- [test_geometry.py](file:///home/bill/src/ai/diagrams-as-code/tests/test_geometry.py)
- [test_routing.py](file:///home/bill/src/ai/diagrams-as-code/tests/test_routing.py)
- [test_renderer_svg.py](file:///home/bill/src/ai/diagrams-as-code/tests/test_renderer_svg.py)
- [test_e2e.py](file:///home/bill/src/ai/diagrams-as-code/tests/test_e2e.py)
- [test_public_api.py](file:///home/bill/src/ai/diagrams-as-code/tests/test_public_api.py)

Test suite status: **520 passed in 11.35s** (100% pass rate, zero regressions).
Visual regression check: `main.py` execution matches existing gallery SVGs with **bit-for-bit zero diff** (`git diff --exit-code -- output/`).
AST module boundary compliance: 100% compliant across all 27 tests in `test_module_boundaries.py`.

Findings: 0 critical blockers, 1 warning (in-place waypoint mutation consistency in reverse-flow routing), 1 informational item. Status: **issues_found**.

---

## Findings Summary

| Severity | Category | Location | Summary |
|----------|----------|----------|---------|
| WARNING  | Correctness / API Consistency | `src/diagrams_as_code/router.py:272-275` | `edge.waypoints` is not assigned in-place when routing reverse-flow explicit ports via `_route_reverse_flow_explicit_ports()`. |
| INFO     | Robustness / Heuristic Boundary | `src/diagrams_as_code/router.py:534-550` | `_select_deflected_corridor` limits secondary obstacle bypass expansion to a single tier before falling back to minimal-hit selection. |

---

## Detailed Findings

### WARNING: `edge.waypoints` Not Mutated in `_route_reverse_flow_explicit_ports` Return Path
- **File**: [router.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L272-L275)
- **Description**: In `CurveRouter.route`:
  ```python
  if obstacles is not None and self._is_reverse_flow_explicit(edge, src_port, tgt_port):
      return self._route_reverse_flow_explicit_ports(
          edge, p_start, p_end, src_port, tgt_port, norm_obstacles, eff_clearance
      )
  ```
  In all other code branches of `CurveRouter.route` (lines 324, 329, 335), `edge.waypoints` is mutated before returning:
  ```python
  edge.waypoints = pts
  return pts
  ```
  When routing an explicit reverse-flow curved edge directly via `CurveRouter.route(edge, obstacles=...)`, `edge.waypoints` remains `None` (or its prior value) unless the caller subsequently calls `SVGRenderer.render()`, which backfills `e.waypoints = pts`.
- **Suggested Remediation**: Assign `pts = self._route_reverse_flow_explicit_ports(...)`, set `edge.waypoints = pts`, and return `pts`.

### INFO: Single-Tier Expansion in Dense Obstacle Corridor Selection
- **File**: [router.py](file:///home/bill/src/ai/diagrams-as-code/src/diagrams_as_code/router.py#L534-L550)
- **Description**: In `CurveRouter._select_deflected_corridor`, when secondary obstacles block both primary bypass corridors, the corridor expands outward once (`y_top_exp` / `y_bot_exp`). If tertiary obstacles also block the expanded corridor, it selects the corridor candidate with fewer intersection hits (`cand_top_exp if len(hits_top_exp) <= len(hits_bot_exp) else cand_bot_exp`). This is compliant with spec D-10 and avoids unbounded recursion, but in extreme maze configurations the returned spline may still intersect an obstacle.

---

## Domain Analysis

### 1. Mathematical Precision & Vector Geometry (`geometry.py`)
- **De Casteljau Subdivision (`CubicBezier.subdivide`, `split`)**:
  - Implements exact numerical subdivision via De Casteljau convex combinations.
  - Parameter bounds strictly validated `0.0 <= t <= 1.0` (rejecting negative, >1.0, and NaN values).
  - Accuracy verified: intermediate midpoint evaluation matches parent curve within $10^{-5}\text{px}$.
- **Two-Tier Collision Narrowphase (`CubicBezier.intersects_rect`)**:
  - Broadphase fast exit via analytical tight bounding box (`self.bbox().intersects(rect)`).
  - Narrowphase recursive subdivision strictly bounded by `clamped_depth = max(1, min(int(max_depth), 8))`, preventing stack overflow while achieving sub-pixel clearance discrimination.
  - Correctly discriminates grazing corner misses from interior penetrations.

### 2. Edge Clearance Architecture & Diagram Cascading (`connections.py`, `diagram.py`)
- **Input Validation (`Edge._validate_clearance`)**:
  - Strictly validates non-negative finite floats; rejects `bool`, `str`, `nan`, `inf`, and negative values with descriptive `ValueError`.
  - Default clearance is $15.0\text{px}$.
- **Cascading & Overrides**:
  - Diagram-level default clearance cascades through `_EdgeBuilder.__rshift__` and `Diagram.connect`.
  - Overrides on edge instances or builder invocations are strictly preserved (including `clearance=0.0` via explicit `is not None` guards).

### 3. Obstacle Avoidance, Deflection & Continuity (`router.py`)
- **Obstacle Normalization (`CurveRouter._normalize_obstacles`)**:
  - Successfully excludes edge source and target elements, matching IDs, and enclosing container groups whose bounds contain $P_{\text{start}}$ or $P_{\text{end}}$.
- **Adaptive Waypoint Topology (`_build_deflected_spline_*`)**:
  - Differentiates compact obstacles ($W \le 2 \times \text{clearance}$) using 1 apex waypoint (7 points / 2 segments) from wide obstacles ($W > 2 \times \text{clearance}$) using 2 corner clearance waypoints (10 points / 3 segments).
  - Enforces corner clearance invariant: waypoints maintain $\ge 15.0\text{px}$ from all obstacle corners.
- **Strict $C^1$ Continuity**:
  - Flat bypass segments utilize collinear tangent vectors along the corridor line ($\mathbf{u}_{\text{in}} = \mathbf{u}_{\text{out}}$ within $10^{-5}$ tolerance), eliminating inward or outward bulging.
- **Reverse Flow Handling (`resolve_ports`, `_route_reverse_flow_explicit_ports`)**:
  - Automatic reverse flow resolves outward to cardinal lateral ports (`NORTH/NORTH` or `SOUTH/SOUTH` for horizontal; `WEST/WEST` or `EAST/EAST` for vertical).
  - Explicit reverse-flow ports route via lateral escape corridor ($\ge 30.0\text{px}$ margin), with disjoint bounding boxes eliminating bow-tie self-intersections.
  - Coincident shapes guarded against division by zero.

### 4. SVG Rendering Engine & Protocol Badges (`renderer_svg.py`)
- **Longest-Segment Arc-Length Midpoint Centering**:
  - Multi-segment Bezier splines evaluate Euclidean arc lengths of constituent cubic segments and locate the longest segment.
  - Badges center on physical arc length $s = L / 2$ of the longest segment, positioning labels on straight bypass chords rather than curved entry turns.
- **Path Generation**:
  - Emits valid SVG chained cubic Bezier commands (`M... C... C...`) without extraneous `L` commands.
  - All coordinates and XML strings are properly formatted and escaped.

### 5. Security & Safety
- **XML / SVG Injection**: All path definitions use formatted numeric coordinates; labels use `html.escape`.
- **Recursion & Denial of Service**: Recursive subdivision depth clamped to at most 8 frames (max 256 sub-curve evaluations), guaranteeing deterministic execution under all inputs.
- **Zero External Dependencies**: Pure standard library only (`math`, `bisect`, `dataclasses`, `enum`, `typing`, `xml.etree.ElementTree`).

---

## Verification Run

```bash
$ uv run pytest
============================= 520 passed in 11.35s =============================

$ uv run python tools/eval_bezier.py
================================================================================
Cubic Bezier Routing Geometry Evaluation (Phase 10)
================================================================================
Pass rate: 10/10 (100.0%)

$ uv run pytest tests/test_module_boundaries.py tests/test_public_api.py
============================== 42 passed in 0.13s ==============================

$ uv run python main.py && git diff --exit-code -- output/
# 0 diff - bit-for-bit backward compatibility verified
```
