# Phase 8: Core Cubic Bezier Geometry & SVG Path Generation - Context

**Gathered:** 2026-09-25  
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 8 delivers foundational cubic Bezier mathematical primitives in Layer 0 (`geometry.CubicBezier` in `src/diagrams_as_code/geometry.py`), edge routing parameter support and validation in Layer 2 (`connections.py`), outward cardinal port normal tangent handles & distance-proportional handle scaling in Layer 3 (`router.py`), and native SVG cubic Bezier path rendering (`<path d="M... C...">`), arrowhead tangential alignment at destination endpoints, and arc-length midpoint protocol badge placement in Layer 4 (`renderer_svg.py`).

</domain>

<decisions>
## Implementation Decisions

### Handle Length & S-Curve Tension Heuristics
- **D-01:** Proportional scaling along primary flow axis: $d = \max(0.5 \cdot \Delta_{\text{axis}}, 25.0)$ for standard forward flow (`LR` or `TB`).
- **D-02:** Enforce minimum handle length of 20px, with no upper clamp (curves scale naturally with distant nodes).
- **D-03:** When nodes are close along the flow axis but have large lateral offsets, blend lateral offset into handle calculation: $d = \max(0.5 \cdot \Delta_{\text{axis}}, 0.25 \cdot |\Delta_{\text{lateral}}|, 20.0)$ to prevent steep sharp bends.
- **D-04:** Keep fixed default heuristic ($k=0.5$) for Phase 8; design internal math to easily accept curvature parameter dynamically in future phases.

### Non-Facing & Lateral Port Tangent Behavior
- **D-05:** For perpendicular ports (e.g. EAST to SOUTH), scale each handle independently by its axis delta along its port normal: $d_1 = \max(0.5 \cdot |\Delta x|, 25.0)$, $d_2 = \max(0.5 \cdot |\Delta y|, 25.0)$.
- **D-06:** For same-side / parallel ports (e.g. NORTH to NORTH), project handles outward with vertical clearance proportional to horizontal separation: $d = \max(0.5 \cdot |\Delta x|, 30.0)$.
- **D-07:** For reverse-facing or backward connections in Phase 8, outward normal projection enforces a minimum clearance offset of 30px, ensuring control handles never cross or form self-intersecting loops.
- **D-08:** Automatic port resolution reuses `router.resolve_ports(edge)` when ports are not explicitly specified, choosing facing cardinal ports based on bounding boxes.

### Protocol Badge Midpoint Computation
- **D-09:** Evaluate curve midpoint via piecewise chord arc-length parameterization (16–32 sample chords with binary search) to guarantee the badge is physically centered even on asymmetric curves.
- **D-10:** Keep protocol label badge horizontal ($0^\circ$ rotation) to preserve typography readability and consistency with orthogonal badges.
- **D-11:** Protocol badges render as solid background pill rectangles matching node fill or badge style, passing the underlying SVG stroke under the pill cleanly.
- **D-12:** Reuse existing `renderer_svg.py` badge sizing logic (height 18px, padding 8px per side) centered on the physical midpoint.

### Waypoint Data Contract & Storage
- **D-13:** Store single-segment cubic Bezier curves in `Edge.waypoints` as exactly 4 points: `[P_start, C_1, C_2, P_end]`, maintaining 100% backward compatibility with `Point` dataclass and existing layout serialization.
- **D-14:** JSON layout export/import serializes the 4 points as standard `{x, y}` dicts, re-rendered as cubic Bezier when `edge.routing == Routing.CURVE`.
- **D-15:** Enforce minimum distance $\|P_3 - P_2\| \ge 1.0\text{px}$ along port normal ray to prevent degenerate zero-tangent marker orientation errors in SVG.
- **D-16:** Implement `geometry.CubicBezier(p0, c1, c2, p3)` in Layer 0 as an immutable dataclass with `point_at(t)`, `tangent_at(t)`, `sample(n)`, and `bbox()`, providing a clean foundation composable into multi-segment splines in Phase 10.

### Claude's Discretion
- Exact chord count for arc-length parameterization (16 vs 32) can be tuned for optimal sub-millisecond execution time during test verification.
- Internal helper structure in `router.py` (e.g., `_compute_bezier_waypoints` or `CurveRouter` class) is at developer discretion conforming to Layer 3 boundaries.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Roadmap & Requirements
- `.planning/ROADMAP.md` — Phase 8 goals, requirements `BEZ-01` through `BEZ-05`, and success criteria.
- `.planning/REQUIREMENTS.md` — Full requirement statements for `BEZ-01` through `BEZ-05`.

### Milestone Research
- `.planning/research/SUMMARY.md` — Synthesized mathematical formulation, stack choices, and phase sequencing.
- `.planning/research/ARCHITECTURE.md` — Decoupled 5-layer system structure, waypoint contract, and component map.
- `.planning/research/PITFALLS.md` — Mitigations for degenerate control handles, NaN rotations, and bow-ties.
- `.planning/research/STACK.md` — Pure Python standard library math primitives (`math.hypot`, `itertools.pairwise`).

### Codebase Architecture & Boundaries
- `src/diagrams_as_code/geometry.py` — Layer 0: `Point`, `Rect`, `Anchor`. Target for `CubicBezier`.
- `src/diagrams_as_code/connections.py` — Layer 2: `Port`, `Routing`, `Edge`.
- `src/diagrams_as_code/router.py` — Layer 3: `Router` and port resolution logic.
- `src/diagrams_as_code/renderer_svg.py` — Layer 4: SVG `<path>` emission and marker definitions.
- `tests/test_module_boundaries.py` — Architectural layering enforcement (imports must point down).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `router.resolve_ports(edge)` in `router.py`: Robust cardinal anchor selection based on bounding box spatial orientation.
- `Point` in `geometry.py`: Immutable dataclass with arithmetic operations (`+`, `-`, `*`, `/`) and distance methods.
- `_marker_id_for_color` in `renderer_svg.py`: Dynamic arrowhead marker definition with `orient="auto"`.

### Established Patterns
- Layer 0 (`geometry.py`) has zero imports from other project modules; immutable frozen dataclasses.
- Layer 3 (`router.py`) calculates all coordinates and waypoints; Layer 4 (`renderer_svg.py`) only formats SVG strings.
- Arrowhead markers rely on `orient="auto"` which evaluates the tangent angle between the final two path points ($P_3 - P_2$).

### Integration Points
- `connections.Edge.routing`: Already contains `Routing.CURVE = "curve"`, ready for router activation.
- `router.Router.route()`: Dispatches to curve routing when `edge.routing == Routing.CURVE`.
- `renderer_svg.SVGRenderer._render_edges()`: When `len(pts) == 4` and `e.routing == Routing.CURVE`, emit `M {pts[0]} C {pts[1]}, {pts[2]}, {pts[3]}` instead of polyline `L` commands.

</code_context>

<specifics>
## Specific Ideas

- Natural S-curve cable look similar to React Flow and modern node-based UI wire routing.
- Protocol badge pills should look visually identical to orthogonal badges, hovering cleanly over the curved stroke without distortion.

</specifics>

<deferred>
## Deferred Ideas

- User-configurable `curvature: float = 0.5` parameter on `Edge` / `Diagram` (deferred to v0.8.x).
- Rounded corner fillets on Manhattan orthogonal routing (`Routing.ORTHOGONAL` with `corner_radius`) (Phase 9).
- Obstacle avoidance & multi-segment deflected splines for curved edges (Phase 10).
- Diagram-level default routing configuration cascade (Phase 11).

</deferred>

---

*Phase: 8-Core Cubic Bezier Geometry & SVG Path Generation*  
*Context gathered: 2026-09-25*
