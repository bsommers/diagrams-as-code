---
phase: 08-core-cubic-bezier-geometry-svg-path-generation
reviewed: 2026-09-25T21:28:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - src/diagrams_as_code/geometry.py
  - src/diagrams_as_code/router.py
  - src/diagrams_as_code/renderer_svg.py
  - src/diagrams_as_code/__init__.py
  - tests/test_geometry.py
  - tests/test_routing.py
  - tests/test_renderer_svg.py
  - tests/test_public_api.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 08 Code Review: Core Cubic Bezier Geometry & SVG Path Generation

## Executive Summary

Phase 08 implementation has been reviewed across all modified source and test files:
- `src/diagrams_as_code/geometry.py`
- `src/diagrams_as_code/router.py`
- `src/diagrams_as_code/renderer_svg.py`
- `src/diagrams_as_code/__init__.py`
- `tests/test_geometry.py`
- `tests/test_routing.py`
- `tests/test_renderer_svg.py`
- `tests/test_public_api.py`

Test suite execution: **469 passed in 11.53s** (100% pass rate, zero regressions).
Zero blockers and zero warnings identified. Architectural boundary tests pass with 100% compliance.

---

## Findings Summary

| Severity | Category | Count | Status |
|----------|----------|-------|--------|
| BLOCKER  | Correctness / Security | 0 | None |
| WARNING  | Maintainability / Quality | 0 | None |

---

## Detailed Review by Domain

### 1. Mathematical Precision & Degenerate Cases
- **Vector Operators (`Point`)**: `+`, `-`, `*`, `/`, and `distance_to` properly implement standard type coercion, handle non-numeric operands with `NotImplemented`, and raise standard `ZeroDivisionError` on zero division.
- **Cubic Bezier Evaluation (`CubicBezier.point_at`, `tangent_at`)**: Implements exact Bernstein polynomial evaluation and exact analytical first derivative calculations.
- **Analytical Bounding Box (`CubicBezier.bbox`)**: Derivative roots of quadratic equation $a t^2 + b t + c = 0$ are solved analytically. Extrema within $(0, 1)$ combined with endpoints $t \in \{0.0, 1.0\}$ guarantee exact tight bounding boxes, verified against 1,001 numerical samples within 0.01px tolerance.
- **Arc-Length & Midpoint Parameterization (`CubicBezier.arc_length`, `arc_length_midpoint`)**:
  - Chord piecewise sampling handles degenerate zero-length curves (`total_len < 1e-6`) by returning `p0`.
  - Zero-length segment delta division is guarded (`segment_len > 1e-9`).
  - Bisection index clamping (`max(0, min(idx, num_samples - 1))`) prevents out-of-bounds indexing.
  - Asymmetric curves verified to differentiate physical arc-length midpoint from parametric $B(0.5)$.

### 2. Router Engine & Handle Heuristics (`router.py`)
- **Port Tangent Collinearity**: `PORT_NORMALS` defines strict unit normal vectors. Exit control point $C_1$ extends outward along $N_{src}$, and entry control point $C_2$ extends outward along $N_{tgt}$ (approaching from inward normal direction). All 16 cardinal port pairings verified for zero perpendicular tangent drift ($< 10^{-6}$).
- **Handle Scaling Heuristics**:
  - Perpendicular ports scale along respective projection axes ($\ge 25.0\text{px}$).
  - Parallel same-side ports scale with lateral separation ($\ge 30.0\text{px}$).
  - Facing ports apply forward flow scaling with lateral offset blending ($\ge 20.0\text{px}$).
  - Opposing ports apply backward flow loops ($\ge 30.0\text{px}$).
  - Clamping invariant enforces $d_1 \ge 20.0\text{px}, d_2 \ge 20.0\text{px}$ against degenerate zero-length handles.
- **Facade & Delegation**:
  - `OrthogonalRouter.route` transparently delegates `Routing.CURVE` / `"curve"` to `CurveRouter`.
  - `EdgeRouter` provides unified routing facade across `DIRECT`, `ORTHOGONAL`, and `CURVE`.

### 3. SVG Path Generation & Protocol Badge Placement (`renderer_svg.py`)
- **Path Generation**: Generates standard SVG cubic Bezier path syntax `M p0.x p0.y C c1.x c1.y, c2.x c2.y, p3.x p3.y`. Chained cubic Bezier splines (`len(pts) >= 4 and (len(pts)-1) % 3 == 0`) correctly emit multi-segment `C` commands without fallback `L` commands.
- **Marker Orientation**: With non-degenerate handles ($d_2 \ge 20\text{px}$), incoming tangents at endpoints are numerically stable, producing valid marker angles without `NaN` or rendering artifacts.
- **Protocol Badge Positioning**: Curved edges compute badge center using `CubicBezier.arc_length_midpoint(num_samples=32)`, ensuring badges rest at the visual midpoint rather than clustering near accelerating endpoints.
- **Fallback Safety**: Fallback to polyline `L` commands occurs gracefully if waypoint counts do not match cubic Bezier requirements.

### 4. Security & Robustness
- **Injection Safety**: SVG path coordinates are formatted strictly from numeric attributes of `Point` objects. Badge text escaping via `html.escape` and element ID escaping are maintained.
- **Resource Bounds**: Bezier sample counts are bounded and guard against negative or zero sample numbers (`max(1, num_samples)`).

### 5. Architectural Layering & AST Boundaries
- **Layer 0 (`geometry.py`)**: Zero imports from internal project modules. Depends only on Python standard library (`bisect`, `dataclasses`, `enum`, `math`, `typing`).
- **Layer 3 (`router.py`)**: Imports only Layer 0–2 modules (`geometry`, `connections`, `elements`, `shapes`).
- **Layer 4 (`renderer_svg.py`)**: Imports only downward layers (`geometry`, `router`, `connections`, `theme`, `elements`, `groups`, `metrics`).
- **Facade Parity**: `diagrams_as_code` and backward-compatible `iiot_diagrams` export identical public symbols (`CubicBezier`, `CurveRouter`, `EdgeRouter`, `PORT_NORMALS`).
- All 27 module boundary AST tests pass.

---

## Verification Run

```
$ uv run pytest
============================= 469 passed in 11.53s =============================
```
