---
phase: "09"
status: passed
requirements_verified:
  - FILLET-01
  - FILLET-02
  - FILLET-03
---

# Phase 09 Verification Report: Rounded Corner Fillets for Orthogonal Routing

## Verdict: PASSED

All requirements (FILLET-01, FILLET-02, FILLET-03), locked architectural decisions (D-01 through D-16), threat mitigations (T-09-01 through T-09-09), and AST module boundaries have been verified against the codebase through direct code inspection and automated test execution. The full test suite passes with 491 tests green and zero regressions. Existing gallery diagrams maintain 100% bit-for-bit zero diff.

---

## 1. Requirements Verification

| Requirement ID | Description | Code Implementation | Verification Test | Status |
|---|---|---|---|---|
| **FILLET-01** | User can configure `corner_radius` (or `arc_radius`) on orthogonal edges to produce rounded 90-degree corner bends. | `connections.py` lines 78-79, 108-109, 116-153; `diagram.py` lines 50-70, 127-130, 292-293, 307-308, 331-348, 359-360, 374-377, 483-484, 498-499, 515-516, 520-522, 534, 583-586 | `tests/test_routing.py::test_edge_corner_radius_and_arc_radius_alias`, `test_edge_corner_radius_validation`, `tests/test_diagram_api.py::test_diagram_corner_radius_cascade_and_override`, `test_fluent_operator_multi_hop_cascade_and_selective_override` | **VERIFIED** |
| **FILLET-02** | Corner filleting dynamically clamps radius per corner to $\min(R, L_1/2, L_2/2)$ so short segments never invert, create "dog ears", or overlap. | `renderer_svg.py` lines 56-99 (`max_r_in = l_in / 2.0`, `max_r_out = l_out / 2.0`, port lead-in `min(10.0, l / 2.0)`, obstacle clearance guard $\ge 4.0\text{px}$, and threshold suppression $R < 2.0\text{px} \implies 0.0$) | `tests/test_renderer_svg.py::test_orthogonal_fillet_short_segment_budget_clamping`, `test_orthogonal_fillet_threshold_suppression`, `test_orthogonal_fillet_port_straight_lead_in`, `test_orthogonal_fillet_obstacle_clearance_guard` | **VERIFIED** |
| **FILLET-03** | SVG renderer emits quadratic Bezier (`Q`) commands connecting corner fillet tangent points for $C^1$-continuous smooth bends. | `geometry.py` lines 306-364 (`QuadraticBezier`); `renderer_svg.py` lines 19-116 (`_render_filleted_path`), lines 721-723 (`SVGRenderer._render_edges` dispatch) | `tests/test_geometry.py::test_quadratic_bezier_evaluation_and_tangents`, `test_quadratic_bezier_bbox_vs_numerical_samples`, `test_quadratic_bezier_arc_length_and_immutability`, `tests/test_renderer_svg.py::test_orthogonal_fillet_svg_path_and_q_commands`, `test_mixed_routing_styles_in_single_diagram`, `test_resvg_rasterization_of_filleted_paths`, `tests/test_e2e.py::test_e2e_obstacle_avoidance_with_corner_fillets` | **VERIFIED** |

---

## 2. Locked Decisions Verification (D-01 through D-16)

- **D-01 (API Attributes & Cascading):** `corner_radius` is primary, `arc_radius` is symmetric alias on `Edge`, `Diagram`, and `_EdgeBuilder`. Diagram default cascades to fluent operator chains, `connect()`, and `solve()`, while honoring explicit edge overrides. Verified in `tests/test_diagram_api.py`.
- **D-02 (Default Sharp Compatibility):** Default `corner_radius=None`/`0.0` preserves sharp corners. Verified bit-for-bit zero diff via `uv run python main.py && git diff --exit-code -- output/`.
- **D-03 (Orthogonal Routing Scope):** `corner_radius` strictly applies to `Routing.ORTHOGONAL` edges; gracefully ignored on `DIRECT` and `CURVE`. Verified in `tests/test_renderer_svg.py::test_mixed_routing_styles_in_single_diagram`.
- **D-04 (Input Validation):** `Edge._validate_corner_radius` strictly validates non-negative finite floats; rejects negative floats, strings, booleans, NaN, and Inf with `ValueError`. Verified in `tests/test_routing.py::test_edge_corner_radius_validation`.
- **D-05 (50% Segment Budget Clamping):** $R_{\text{effective}} \le \min(R, L_{\text{in}} / 2, L_{\text{out}} / 2)$ enforced in `renderer_svg._render_filleted_path` lines 56-58. Verified in `tests/test_renderer_svg.py::test_orthogonal_fillet_short_segment_budget_clamping`.
- **D-06 (Threshold Suppression):** $R_{\text{effective}} < 2.0\text{px}$ clamped to sharp right angle (`L P_c.x P_c.y`). Verified in `tests/test_renderer_svg.py::test_orthogonal_fillet_threshold_suppression`.
- **D-07 (Orthogonal Turn Detection):** Evaluates $|\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}}| \le 10^{-6}$; collinear segments and turnarounds remain sharp linear. Verified in `renderer_svg.py` lines 52-54.
- **D-08 (Endpoint Straight Lead-in):** First and last interior corners reserve $\min(10.0, L / 2)$ straight lead-in adjacent to ports. Verified in `tests/test_renderer_svg.py::test_orthogonal_fillet_port_straight_lead_in`.
- **D-09 (SVG Q Command Syntax):** Emits `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y` with tangent points $T_1 = P_c - \mathbf{u}_{\text{in}} R$, $T_2 = P_c + \mathbf{u}_{\text{out}} R$. Verified in `tests/test_renderer_svg.py::test_orthogonal_fillet_svg_path_and_q_commands`.
- **D-10 (Layer 0 Primitive):** `QuadraticBezier(p0, p1, p2)` implemented in `geometry.py` as immutable frozen dataclass; exported in `diagrams_as_code` and mirrored in `iiot_diagrams`. Verified in `tests/test_geometry.py` and `tests/test_public_api.py`.
- **D-11 (Waypoint Data Contract):** `Edge.waypoints` remains strictly the Manhattan vertex polyline `[P_0, ..., P_n]`; fillets are computed purely during SVG path emission. Verified in `tests/test_renderer_svg.py::test_orthogonal_fillet_badge_placement`.
- **D-12 (Protocol Badge Placement):** Badges on filleted orthogonal edges are centered at the midpoint of the longest straight segment. Default sharp edges preserve legacy midpoint positioning for regression invariance. Verified in `tests/test_renderer_svg.py::test_orthogonal_fillet_badge_placement`.
- **D-13 (Uniform Filleting on Detours):** Detours around obstacles receive uniform filleting across all 90-degree corners. Verified in `tests/test_e2e.py::test_e2e_obstacle_avoidance_with_corner_fillets`.
- **D-14 (Obstacle Clearance Guard):** Inside apex displacement evaluated against obstacle bounding boxes expanded by 4.0px; radius clamped to guarantee $\ge 4.0\text{px}$ clearance. Verified in `tests/test_renderer_svg.py::test_orthogonal_fillet_obstacle_clearance_guard` and `tests/test_e2e.py::test_e2e_obstacle_avoidance_with_corner_fillets`.
- **D-15 (Performance Optimization):** Pure standard library analytical vector math ($O(1)$ closed-form per corner, $O(n)$ per edge); sub-millisecond execution. Suite runs 491 tests in ~11s.
- **D-16 (Interactive SVG Compatibility):** Filleted paths emit standard `<path d="..." class="edge">` elements compatible with interactive pan/zoom, minimap, and search. Verified in `tests/test_renderer_svg.py::test_interactive_svg_collapsible_groups_and_edges`.

---

## 3. Threat Model Verification

- **T-09-01 (Denial of Service / Degenerate Roots):** `QuadraticBezier.bbox()` guards zero-division when $|P_0 - 2P_1 + P_2| \le 10^{-9}$. `tangent_at()` evaluates exact linear polynomials. Verified in `test_geometry.py`.
- **T-09-02 (Input Tampering / Non-numeric or Negative):** `_validate_corner_radius()` rejects strings, booleans, negative numbers, NaN, and Inf with `ValueError`. Verified in `test_routing.py`.
- **T-09-03 (State Mutation):** `QuadraticBezier` is decorated with `@dataclass(frozen=True)`. Mutations raise `FrozenInstanceError`. Verified in `test_geometry.py`.
- **T-09-04 (Division by Zero in Normalization):** Degenerate segments with $L \le 10^{-6}$ are assigned zero unit vectors and left sharp. Verified in `renderer_svg.py` lines 37, 45.
- **T-09-05 (Dog-Ear Loops / Short Segments):** Dynamic 50% segment budget clamping ensures tangent points never overlap. Verified in `test_renderer_svg.py`.
- **T-09-06 (Obstacle Penetration):** Inside apex clearance guard ensures corner fillets maintain $\ge 4.0\text{px}$ clearance margin from all obstacle bounding boxes. Verified in `test_renderer_svg.py` and `test_e2e.py`.
- **T-09-07 (Sub-pixel Raster Distortion):** Radii $< 2.0\text{px}$ suppress to sharp 90-degree corners. Verified in `test_renderer_svg.py`.
- **T-09-08 (Visual Regression Drift):** Preserved sharp defaults verified via `git diff --exit-code -- output/`.
- **T-09-09 (Architectural Erosion):** Layer hierarchy verified via `tests/test_module_boundaries.py`.

---

## 4. Architecture & Module Boundaries

- **Zero External Runtime Dependencies:** Pure Python standard library (`math`, `dataclasses`, `enum`, `xml.etree.ElementTree`).
- **AST Module Boundaries:** `tests/test_module_boundaries.py` passed with 100% compliance (27 passed). Layer 0 (`geometry.py`) has 0 internal imports.
- **Public API Mirroring:** `tests/test_public_api.py` passed with 100% parity between `diagrams_as_code` and `iiot_diagrams`. `QuadraticBezier` exported in both packages.
- **Headless Rasterization:** `test_resvg_rasterization_of_filleted_paths` verified valid PNG generation from filleted SVG paths.

---

## 5. Test Suite Execution

```
$ uv run pytest
============================= 491 passed in 11.62s =============================

$ uv run python main.py && git diff --exit-code -- output/
Generated: output/main_architecture.svg
Generated: output/main_architecture.png
Generated: output/main_README.md
[exit code: 0 - clean zero diff]
```

All 491 tests pass green with zero regressions and zero visual diff against existing baseline diagrams.
