# AI & Evaluation Specification — Phase 08: Core Cubic Bezier Geometry & SVG Path Generation

## 1. Overview & Architecture

Diagrams as Code (`diagrams_as_code`) is a pure-Python deterministic architecture diagramming engine designed to compile directed graphs into publication-quality SVG diagrams with zero external binary or runtime dependencies.

Phase 08 introduces the mathematical primitives, routing heuristics, and SVG rendering commands for cubic Bezier edge curves (`Routing.CURVE`). While the core compiler operates deterministically rather than via probabilistic neural models, it adopts the GSD evaluation and benchmark framework to continuously assess geometric fidelity, topological edge cases, aesthetic styling, and error handling.

## 2. System Taxonomy & Design Philosophy

- **Engine Classification:** Directed graph layout compiler and geometric path synthesizer.
- **Evaluation Strategy:** Deterministic, code-based verification paired with benchmark datasets and diagnostic curve tracing.
- **Guardrails Strategy:** Hard mathematical invariants enforced at compile time (minimum handle separation, non-zero denominator protection, analytical derivative extrema, and quadratic root validation).

## 3. Critical Failure Modes

1. **Port Anchor Drift (Context Faithfulness):** Curve endpoints disconnect or deviate from the node bounding box cardinal anchors.
2. **Degenerate Markers & Coordinates (Hallucination / Artifact):** Zero-length tangents causing `NaN` or `inf` angle calculations in SVG markers.
3. **Rendering Crashes on Malformed Input (Escalation Accuracy):** Curves with non-standard waypoint counts crashing the renderer instead of gracefully falling back.
4. **Kinks and Unnatural Loops (Tone & Style Appropriateness):** Exit and entry tangents departing at angles non-collinear with port normals.
5. **Zero Division & Numerical Instability (Safety):** Discriminants $a \to 0$ or arc lengths $L \to 0$ causing unhandled runtime exceptions.

## 4. Evaluation Strategy & Methodology

The evaluation strategy relies on code-based deterministic verification across 10 defined dimensions, backed by a standardized 10-scenario reference dataset (`tests/fixtures/eval_bezier_dataset.json`), an automated CLI runner (`tools/eval_bezier.py`), and continuous test execution in CI/CD (`.github/workflows/ci.yml`).

## 5. Evaluation Dimensions & Rubrics

| Dimension | Rubric Criteria (Pass / Fail) | Measurement Approach | Implementation Target |
|-----------|--------------------------------|----------------------|-----------------------|
| **Factual Accuracy** | Bernstein polynomials $B(t)$, velocity tangents $B'(t)$, and derivative root bounding boxes match analytical closed-form mathematics within 0.01px tolerance. | Code-based / Unit Tests | `tests/test_geometry.py` |
| **Context Faithfulness** | Waypoints $P_0$ and $P_3$ match the exact cardinal port anchor coordinates of the source and target elements within $10^{-6}$ px (zero drift). | Code-based / Benchmark Dataset | `tools/eval_bezier.py`, `tests/test_eval_routing.py` |
| **Hallucination Detection** | Generated SVG contains zero `NaN` or `inf` coordinates, zero unreferenced marker IDs, and parses strictly as valid XML. | Code-based / XML Parsing | `tools/eval_bezier.py`, `tests/test_eval_routing.py` |
| **Escalation Accuracy** | Degenerate curves (e.g. coincident points, malformed waypoint lengths) gracefully fall back to direct lines or polylines without crashing. | Code-based / Boundary Tests | `tools/eval_bezier.py`, `tests/test_eval_routing.py` |
| **Policy Compliance** | Layer 0 has zero internal dependencies; core engine has zero runtime dependencies in `pyproject.toml`; AST import boundaries pass 100%. | Code-based / AST Audits | `tests/test_module_boundaries.py`, `tests/test_public_api.py` |
| **Tone & Style Appropriateness** | Tangents depart collinear with port normals ($dot > 0.999$); handle tension $d_1, d_2 \ge 20.0$px; protocol badges satisfy visual contrast across all 13 themes. | Code-based / Aesthetic Audits | `tools/eval_bezier.py`, `tests/test_eval_routing.py` |
| **Output Structure Validity** | Emits exact SVG `<path d="M... C...">` syntax conforming to the W3C SVG 1.1 path specification. | Code-based / Regex & XML | `tests/test_renderer_svg.py` |
| **Task Completion** | 100% of benchmark topological scenarios resolve to valid routed paths and render successfully without warnings. | Code-based / Full Suite | `tools/eval_bezier.py` (10/10 PASS) |
| **Tool Use Correctness** | `EdgeRouter` facade, `CurveRouter`, and standalone CLI correctly handle `Routing.CURVE` and edge parameters across all APIs. | Code-based / CLI Tests | `tests/test_routing.py`, `tests/test_public_api.py` |
| **Safety & Numerical Stability** | Zero-division guards on curve length $< 10^{-6}$, handle clamping $\ge 20.0$px, and linear quadratic fallback when $|a| < 10^{-9}$. | Code-based / Defensive Guards | `src/diagrams_as_code/geometry.py`, `src/diagrams_as_code/router.py` |

## 6. Evaluation Infrastructure

1. **Eval Tooling:**
   - Standalone CLI benchmark runner: `tools/eval_bezier.py`.
   - Supports human-readable terminal output and machine-parseable `--json` reports with exit code gating.
2. **Reference Dataset:**
   - Standardized JSON benchmark corpus: `tests/fixtures/eval_bezier_dataset.json`.
   - Covers 10 canonical scenarios: facing cardinal ports, perpendicular turns, parallel same-side loops, backward opposing flows, lateral S-curves, and coincident degenerate cases.
3. **CI/CD Integration:**
   - Integrated into GitHub Actions workflow `.github/workflows/ci.yml` as `Run evaluation and benchmark suite`.
   - Automated regression test suite in `tests/test_eval_routing.py` running on every `pytest` invocation.
4. **Online Guardrails:**
   - Active runtime validation:
     - `d1 = max(d1, 20.0)` and `d2 = max(d2, 20.0)` preventing zero-length handles in `CurveRouter`.
     - `total_len < 1e-6` and `segment_len > 1e-9` guards in `CubicBezier.arc_length` and `arc_length_midpoint`.
     - Analytical quadratic root fallback when $|a| < 10^{-9}$ in `CubicBezier.bbox`.
     - Polyline fallback in `SVGRenderer._render_edges` when edge waypoints do not form complete Bezier control tuples.
5. **Tracing & Observability:**
   - Structured curve diagnostics calculated for every routed segment: arc length, midpoint coordinates, and bounding box dimensions.
   - Traceable through `tools/eval_bezier.py --json`.

## 7. Monitoring & Continuous Verification

- All builds must achieve 100% pass rate on `uv run pytest` and `uv run python tools/eval_bezier.py`.
- No visual drift or clobbering of tracked documentation or output artifacts (`git diff --exit-code -- output/ icons/ README.md docs/`).
- Benchmark dataset serves as living regression guard for future routing enhancements (fillets, obstacle avoidance, multi-segment splines).
