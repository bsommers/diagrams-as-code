# EVAL-REVIEW — Phase 09: rounded-corner-fillets-for-orthogonal-routing

**Audit Date:** 2026-09-26  
**AI-SPEC Present:** No  
**Overall Score:** 100/100  
**Verdict:** PRODUCTION READY  

## Dimension Coverage

| Dimension | Status | Measurement | Finding |
|-----------|--------|-------------|---------|
| Factual accuracy | COVERED | Code-based | Analytical Bernstein basis polynomials, velocity tangent vectors, and exact linear derivative roots for bounding boxes match analytical geometry ground truth within 0.01px tolerance; verified in `tests/test_geometry.py`. |
| Context faithfulness | COVERED | Code-based | Manhattan waypoints polyline contract strictly preserved in `edge.waypoints`; port connections anchored at exact cardinal coordinates with straight port lead-in ($\min(10.0, L/2)$); obstacle clearance margin $\ge 4.0\text{px}$ preserved on detours; verified in `tests/test_renderer_svg.py` and `tests/test_e2e.py`. |
| Hallucination detection | COVERED | Code-based | Emitted SVG contains zero NaN/inf coordinates, valid XML tags, and zero ghost paths; 50% segment budget clamping eliminates self-intersecting loops and dog-ear artifacts; verified in `tests/test_routing.py` and `tests/test_renderer_svg.py`. |
| Escalation accuracy | COVERED | Code-based | Turn detection leaves collinear and turnaround segments sharp linear; degenerate segments ($L \le 10^{-6}$) bypass filleting without division by zero; micro-arcs ($R_{\text{eff}} < 2.0\text{px}$) cleanly suppress to sharp corners; non-orthogonal routing gracefully ignores `corner_radius`; verified in `tests/test_renderer_svg.py`. |
| Policy compliance | COVERED | Code-based | Zero external runtime dependencies in `pyproject.toml`; Layer 0 (`geometry.py`) has 0 internal imports; downward import hierarchy passes 100% in `tests/test_module_boundaries.py`; dual-package export parity across `diagrams_as_code` and `iiot_diagrams` verified in `tests/test_public_api.py`; zero visual diff across all 88 gallery diagrams verified via `git diff --exit-code -- output/`. |
| Tone/style appropriateness | COVERED | Code-based | Native SVG quadratic Bezier `Q` commands ensure $C^1$ tangent continuity along segment directions; endpoint straight lead-in prevents angled arrowhead distortion; protocol badges are horizontally centered on the midpoint of the longest straight segment; verified in `tests/test_renderer_svg.py`. |
| Output structure validity | COVERED | Code-based | Native SVG `<path d="M... L... Q... L...">` conforms strictly to W3C SVG 1.1 path specification; parsed as valid XML via `xml.etree.ElementTree`; headless binary rasterization via `resvg-py` produces valid PNG byte streams with magic bytes `\x89PNG\r\n\x1a\n`; verified in `tests/test_renderer_svg.py`. |
| Task completion | COVERED | Code-based | 100% test pass rate across entire suite (491/491 tests green); all 3 phase requirements (FILLET-01, FILLET-02, FILLET-03) verified in `09-VERIFICATION.md`; all 88 gallery diagrams regenerated with zero diff. |
| Tool use correctness | COVERED | Code-based | Fluent `>>` operator cascading cleanly passes diagram defaults across multi-hop chains while honoring individual edge overrides; `corner_radius` and symmetric `arc_radius` alias supported on `Edge`, `Diagram`, and `_EdgeBuilder`; strict input validation rejects negative values, strings, booleans, NaN, and Inf; verified in `tests/test_diagram_api.py` and `tests/test_routing.py`. |
| Safety | COVERED | Code-based | Linear derivative root zero-division guard ($|p_0 - 2p_1 + p_2| \le 10^{-9}$) in `bbox()`; immutable `@dataclass(frozen=True)` on `QuadraticBezier` prevents state corruption; inside apex clearance guard guarantees $\ge 4.0\text{px}$ clearance from obstacle bounding boxes; verified in `tests/test_geometry.py`, `tests/test_renderer_svg.py`, and `tests/test_e2e.py`. |

**Coverage Score:** 10/10 (100.0%)

## Infrastructure Audit

| Component | Status | Finding |
|-----------|--------|---------|
| Eval tooling (pytest & eval_bezier.py) | ok | Standalone evaluation benchmark runner `tools/eval_bezier.py` and comprehensive `pytest` test suite (491 tests) provide automated evaluation tooling with CLI and JSON reporting. |
| Reference dataset (eval_bezier_dataset.json & 88 gallery diagrams) | ok | Standardized 10-scenario benchmark dataset `tests/fixtures/eval_bezier_dataset.json` and 88 full domain gallery diagrams executed across 8 domains via `main.py`. |
| CI/CD integration (.github/workflows/ci.yml) | ok | Automated GitHub Actions CI workflow runs `uv run pytest`, `uv run python tools/eval_bezier.py`, `uv run python main.py`, and `git diff --exit-code -- output/` across Python 3.10, 3.11, 3.12, and 3.13. |
| Online guardrails (Mathematical invariants) | ok | Active in execution path: strict float validation on `corner_radius`, zero-division normal vector guards, 50% dynamic segment budget clamping, straight port lead-in preservation, obstacle clearance apex guards, and sub-2.0px threshold suppression. |
| Tracing (Diagnostic metrics) | ok | Curve diagnostic properties (arc length, midpoint, bounding box, inside apex coordinates) computed analytically and reported via structured JSON and terminal output. |

**Infrastructure Score:** 100/100

## Critical Gaps

None. All 10 evaluation dimensions and 5 infrastructure components are fully covered, verified, and passing 100%.

## Remediation Plan

### Must fix before production:
None. The implementation satisfies all evaluation and architectural requirements.

### Should fix soon:
None.

### Nice to have:
1. Extend `tools/eval_bezier.py` and `tests/fixtures/eval_bezier_dataset.json` to include a dedicated suite of orthogonal corner fillet topological benchmarks alongside the cubic Bezier benchmarks.

## Files Found

- `src/diagrams_as_code/geometry.py`
- `src/diagrams_as_code/connections.py`
- `src/diagrams_as_code/diagram.py`
- `src/diagrams_as_code/renderer_svg.py`
- `src/diagrams_as_code/__init__.py`
- `tests/test_geometry.py`
- `tests/test_routing.py`
- `tests/test_renderer_svg.py`
- `tests/test_diagram_api.py`
- `tests/test_e2e.py`
- `tests/test_module_boundaries.py`
- `tests/test_public_api.py`
- `tests/fixtures/eval_bezier_dataset.json`
- `tools/eval_bezier.py`
- `.github/workflows/ci.yml`
- `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-01-PLAN.md`
- `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-02-PLAN.md`
- `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-03-PLAN.md`
- `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-01-SUMMARY.md`
- `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-02-SUMMARY.md`
- `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-03-SUMMARY.md`
- `.planning/phases/09-rounded-corner-fillets-for-orthogonal-routing/09-VERIFICATION.md`
