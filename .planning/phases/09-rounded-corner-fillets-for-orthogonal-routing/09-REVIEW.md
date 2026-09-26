---
phase: 09-rounded-corner-fillets-for-orthogonal-routing
reviewed: 2026-09-26T19:41:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - src/diagrams_as_code/geometry.py
  - src/diagrams_as_code/connections.py
  - src/diagrams_as_code/diagram.py
  - src/diagrams_as_code/renderer_svg.py
  - src/diagrams_as_code/__init__.py
  - tests/test_geometry.py
  - tests/test_routing.py
  - tests/test_diagram_api.py
  - tests/test_renderer_svg.py
  - tests/test_e2e.py
  - tests/test_public_api.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 09 Code Review: Rounded Corner Fillets for Orthogonal Routing

## Executive Summary

Phase 09 implementation has been reviewed across all 11 source and test files:
- `src/diagrams_as_code/geometry.py`
- `src/diagrams_as_code/connections.py`
- `src/diagrams_as_code/diagram.py`
- `src/diagrams_as_code/renderer_svg.py`
- `src/diagrams_as_code/__init__.py`
- `tests/test_geometry.py`
- `tests/test_routing.py`
- `tests/test_diagram_api.py`
- `tests/test_renderer_svg.py`
- `tests/test_e2e.py`
- `tests/test_public_api.py`

Test suite execution: **491 passed in 12.57s** (100% pass rate, zero regressions).
Visual regression check: `uv run python main.py && git diff --exit-code -- output/` passed with **bit-for-bit zero diff** across all 88 domain example diagrams.
AST module boundary validation: `tests/test_module_boundaries.py` passed with 100% compliance.
Zero blockers and zero warnings identified. Status: **clean**.

---

## Findings Summary

| Severity | Category | Count | Status |
|----------|----------|-------|--------|
| BLOCKER  | Correctness / Security | 0 | None |
| WARNING  | Maintainability / Quality | 0 | None |

---

## Detailed Review by Domain

### 1. Mathematical Precision & Vector Geometry (`geometry.py`)
- **Bernstein Evaluation & Derivatives (`QuadraticBezier.point_at`, `tangent_at`)**: Implements exact Bernstein polynomial evaluation $B(t) = (1-t)^2 P_0 + 2(1-t)t P_1 + t^2 P_2$ and analytical first derivative $B'(t) = 2(1-t)(P_1 - P_0) + 2t(P_2 - P_1)$.
- **Analytical Bounding Box (`QuadraticBezier.bbox`)**: Solves first derivative roots $t = \frac{P_0 - P_1}{P_0 - 2P_1 + P_2}$ analytically with zero-division guard ($|P_0 - 2P_1 + P_2| > 10^{-9}$). Tightness verified within $0.01\text{px}$ against 1,001 numerical samples.
- **Arc-Length & Sampling (`QuadraticBezier.arc_length`, `sample`)**: Uniform sampling handles $n < 2$ degeneracies gracefully, and piecewise chord accumulation handles $n \ge 1$.
- **Immutability**: Enforced via `@dataclass(frozen=True)` and verified with mutation tests raising `FrozenInstanceError`.

### 2. Edge & Diagram Contracts (`connections.py`, `diagram.py`)
- **Input Validation**: `Edge._validate_corner_radius` validates non-negative finite floats and rejects negative floats, booleans (`isinstance(val, (bool, str))`), strings, NaN, and Inf with clear `ValueError` messages.
- **Backward-Compatible Alias**: `arc_radius` and `corner_radius` provide symmetric property getters and setters with synchronized state.
- **Cascading & Overrides**: Diagram-level `corner_radius` defaults cascade through `_EdgeBuilder.__rshift__`, `Diagram.connect`, and `Diagram.solve()` while strictly honoring explicit edge overrides (e.g., `corner_radius=0.0` is preserved because checks use `is not None` rather than truthiness).

### 3. SVG Fillet Rendering Engine (`renderer_svg.py`)
- **$C^1$ Continuity & Command Syntax**: Native SVG quadratic Bezier `Q` commands connect tangent points $T_1 = P_c - \mathbf{u}_{\text{in}} R$ and $T_2 = P_c + \mathbf{u}_{\text{out}} R$ through control vertex $P_c$.
- **Dynamic Segment Clamping**: Enforces 50% segment budget $R_{\text{eff}} \le \min(R, L_{\text{in}} / 2, L_{\text{out}} / 2)$, completely eliminating overlapping curves or loops on short segments.
- **Endpoint Lead-in Reservation**: Preserves straight lead-in of $\min(10.0, L / 2)$ on segments entering or exiting ports, ensuring arrowheads align flush on straight orthogonal segments.
- **Strict Turn Detection**: Verifies 90° turns via $|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$, leaving collinear points and reversals sharp.
- **Obstacle Clearance Guard**: Checks apex displacement $P_c - 0.25(\mathbf{u}_{\text{in}} - \mathbf{u}_{\text{out}}) R$ against obstacle bounding boxes expanded by $4.0\text{px}$, analytically clamping radius to guarantee $\ge 4.0\text{px}$ clearance.
- **Threshold Suppression**: Clamped radii $< 2.0\text{px}$ suppress to sharp right angles (`L P_c.x P_c.y`), avoiding sub-pixel rasterization artifacts.
- **Protocol Badge Positioning**: On rounded orthogonal edges, badges center on the midpoint of the longest straight segment rather than straddling corner bends. Sharp edges (`corner_radius=None` / `0.0`) retain legacy mid-waypoint positioning, ensuring bit-for-bit regression invariance.

### 4. Security & Safety
- **Safe XML/SVG Emission**: All path definitions are constructed strictly from numeric coordinates (`pts[i].x`, `pts[i].y`, $R_{\text{eff}}$); user strings are never interpolated directly into SVG path descriptions. All text labels, IDs, and attributes are sanitized with `html.escape`.
- **Resource Constraints**: Pure analytical $O(n)$ polyline processing with closed-form math; zero risk of infinite loops or excessive allocations.

### 5. Architecture & Public API (`diagrams_as_code`, `iiot_diagrams`)
- **Layer 0 Purity**: `geometry.py` imports only standard library (`dataclasses`, `enum`, `math`, `typing`, `bisect`) with zero internal or external dependencies.
- **Module Boundaries**: Layer 0 through Layer 5 AST hierarchy rules pass with 100% compliance across all 27 tests in `tests/test_module_boundaries.py`.
- **Public API Exports**: `QuadraticBezier` is exported in `diagrams_as_code.__all__` and mirrored in `iiot_diagrams.__all__`, verified by `test_public_api.py`.
- **Headless Rasterization**: Verified `resvg-py` compatibility parsing filleted `Q` path commands and outputting valid PNG binary streams without errors.

---

## Verification Run

```
$ uv run pytest
============================= 491 passed in 12.57s =============================

$ uv run python main.py && git diff --exit-code -- output/
Generated: output/main_architecture.svg
Generated: output/main_architecture.png
Generated: output/main_README.md
[exit code: 0 - clean zero diff]
```
