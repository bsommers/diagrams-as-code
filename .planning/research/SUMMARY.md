# Project Research Summary

**Project:** Diagrams as Code (Directed IIoT & Architecture Engine) — Milestone v0.8.0 Curved & Bezier Edge Routing Engine  
**Domain:** Vector Geometry, Curve Routing & SVG Rendering Engine (Pure Python Standard Library)  
**Researched:** 2026-09-24  
**Confidence:** HIGH  

## Executive Summary

Diagrams as Code is a pure-Python, zero-dependency directed architecture diagramming engine designed to produce deterministic, publication-quality SVG diagrams. Milestone v0.8.0 expands the engine beyond Manhattan orthogonal lines to introduce smooth cubic Bezier edge routing (`Routing.CURVE`) and rounded corner fillets (`arc_radius` on `Routing.ORTHOGONAL`). In modern architecture diagramming (e.g., Graphviz `dot`, XYFlow/React Flow, Draw.io/mxGraph), smooth curves and rounded corners convey distinct architectural semantics—such as asynchronous event streams or feedback loops—while softening high-density connection grids.

The recommended approach implements pure vector geometry primitives in Layer 0 (`geometry.CubicBezier`) using Python's standard library (`math`, `dataclasses`). Architectural boundaries are strictly maintained: `CurveRouter` and `EdgeRouter` in Layer 3 calculate outward cardinal port normal tangents, handle scaling, obstacle collision detection, and multi-segment avoidance waypoints, populating `edge.waypoints`; while `SVGRenderer` in Layer 4 strictly formats SVG path commands (`C` for cubic Beziers, `Q` for rounded orthogonal fillets) and centers protocol label badges. Filleting replaces sharp 90° corners with quadratic Beziers controlled by corner vertices and guarded by dynamic radius clamping.

The primary technical risks involve degenerate control handles causing undefined or `NaN` arrowhead rotations in SVG renderers, ballooning "bow-tie" loops on backward edges, fillet arc inversion ("dog ears") on short Manhattan segments, label badge distortion on asymmetric curves, and single-segment curve distortion around wide obstacles. All risks have proven analytical mitigations rooted in standard library vector arithmetic, De Casteljau subdivision, and A* detour corridor smoothing.

## Key Findings

### Recommended Stack

The implementation requires zero external runtime dependencies (`dependencies = []` in `pyproject.toml` remains strictly empty). All geometric calculations, polynomial evaluations, and SVG string generation execute within the Python standard library across Python 3.10–3.14.

Detailed stack documentation is available in [STACK.md](file:///home/bill/src/ai/diagrams-as-code/.planning/research/STACK.md).

**Core technologies:**
- **Python Standard Library (`math`)**: Euclidean distance (`hypot`), trigonometry (`atan2`, `sin`, `cos`), square root (`sqrt`), float comparison (`isclose`) — hardware-accelerated IEEE 754 arithmetic with zero dependencies.
- **Python Standard Library (`dataclasses`)**: Immutable geometric primitives (`CubicBezier`, `Point`, `Rect`) — clean value-object semantics and structural equality without runtime overhead.
- **Python Standard Library (`itertools.pairwise`)**: Adjacent segment and corner triplet iteration — enables robust orthogonal fillet tangent generation without index bookkeeping.
- **Python Standard Library (`heapq`)**: Priority queue for A* waypoint detour pathfinding — obstacle clearance channel navigation for deflected splines.
- **W3C SVG Path Specification (`d` attribute)**: Path commands (`M`, `L`, `C`, `Q`, `A`) — universal vector format rendered natively by browsers, vector illustration tools, and headless rasterizers (`resvg-py`).

### Expected Features

Detailed feature documentation and competitor analysis are available in [FEATURES.md](file:///home/bill/src/ai/diagrams-as-code/.planning/research/FEATURES.md).

**Must have (table stakes):**
- **Cubic Bezier Routing (`Routing.CURVE`)** — analytical cubic Bezier curves connecting source and target port anchors.
- **Port Tangent Orientation & Directional Normals** — curves exit and enter node boundaries strictly perpendicular to shape walls.
- **Smooth S-Curve Handle Distance Heuristics** — proportional handle scaling along primary flow axes to prevent kinks or bulging.
- **Rounded Corner Fillets for `Routing.ORTHOGONAL`** — smooth corner transitions on Manhattan polylines with configurable `corner_radius` / `arc_radius`.
- **Diagram Default + Per-Edge Routing Override** — global diagram styling with granular connection-level overrides.
- **Protocol Label Badge Placement on Curves** — centered badge rectangles and text positioned along physical curve arc lengths.

**Should have (competitive differentiators):**
- **Obstacle-Deflected Bezier Splines** — detection of obstacles intersecting candidate curves, routing multi-segment splines through collision-free clearance channels.
- **Adaptive Tangent Scaling for Back-Edges & Loops** — projection of control points into lateral clearance channels for reverse-flow edges.
- **Mixed Semantic Routing in Single Diagrams** — co-existence of orthogonal, filleted, curved, and direct edges within the same diagram.

**Defer (v2+):**
- **Curvature Parameter Tuning (`curvature: float = 0.5`)** — normalized parameter for dialling curve tension.
- **Edge Crossing Bridge Hops (Jump Arcs)** — semi-circular jump bridges over intersecting edges.
- **Edge Bundling for High-Density Meshes** — shared spline bundles for parallel connections.

### Architecture Approach

The architecture follows a strict 5-layer decoupled design conforming to project AST module boundary enforcement (`tests/test_module_boundaries.py`). Control points and detour paths are computed entirely during the layout and routing phase (`router.py`), leaving `renderer_svg.py` strictly responsible for emitting SVG XML elements.

Detailed architecture diagrams and contracts are available in [ARCHITECTURE.md](file:///home/bill/src/ai/diagrams-as-code/.planning/research/ARCHITECTURE.md).

**Major components:**
1. **`geometry.CubicBezier` (Layer 0)** — frozen dataclass representing a cubic Bezier segment; provides Bernstein polynomial evaluation, tangent derivatives, chord length sampling, and derivative root bounding boxes.
2. **`connections.Edge` & `Routing` (Layer 2)** — holds edge routing metadata (`Routing.CURVE`, `Routing.ORTHOGONAL`, `Routing.DIRECT`), `arc_radius`, and calculated waypoints.
3. **`router.CurveRouter` & `router.EdgeRouter` (Layer 3)** — resolves port normal vectors, computes control handles, executes obstacle collision testing via AABB broadphase and De Casteljau subdivision, synthesizes detour splines, and dispatches routing requests.
4. **`renderer_svg.SVGRenderer` (Layer 4)** — formats SVG `<path d="...">` using `C` (cubic) and `Q` (quadratic fillet) commands; positions protocol badges at evaluated arc-length midpoints.
5. **`diagram.Diagram` & `_EdgeBuilder` (Layer 5)** — provides diagram-level defaults (`routing`, `arc_radius`) that cascade down to connection builders and the fluent `>>` operator.

### Critical Pitfalls

Detailed failure modes, root causes, and recovery strategies are available in [PITFALLS.md](file:///home/bill/src/ai/diagrams-as-code/.planning/research/PITFALLS.md).

1. **Degenerate Control Points Causing NaN / Undefined SVG Marker Orientations** — when endpoints are close or control handles collapse, endpoint tangents evaluate to $(0, 0)$, causing SVG markers with `orient="auto"` to disappear or rotate erratically.  
   *Mitigation:* Enforce a minimum separation invariant ($\|P_1 - P_0\| \ge 1.0\text{px}$, $\|P_3 - P_2\| \ge 1.0\text{px}$) along outward port normal rays.
2. **Control Point Overshoot and Bow-Tie Loops on Backward Edges** — naive handle lengths based on total Euclidean distance cause handles on reverse-flow edges to cross over, creating ballooning loops.  
   *Mitigation:* Scale control handles by the projected forward distance along the port normal axis; detect opposing port alignments and route through intermediate clearance waypoints.
3. **Orthogonal Fillet Radius Clamping Failure ("Dog Ears")** — fixed fillet radii on short Manhattan segments cause overlapping arcs that invert into protruding triangular loops.  
   *Mitigation:* Apply dynamic per-corner radius clamping $r = \min(R, L_{\text{in}} / 2, L_{\text{out}} / 2)$; suppress fillets and emit sharp corners if $r < 2.0\text{px}$.
4. **Parameter-Space ($t = 0.5$) Label Placement Distortion on Asymmetric Curves** — parameter $t$ does not progress at constant physical speed along curved paths, causing labels on asymmetric curves to clump near one endpoint.  
   *Mitigation:* Use 32-chord piecewise arc-length parameterization and binary search to locate physical curve midpoint $s = L / 2$.
5. **Single-Segment Bezier Distortion on Wide Obstacles ("Parabolic Bulge")** — attempting to stretch a single cubic curve around an obstacle causes extreme distortion and corner clipping.  
   *Mitigation:* Leverage existing A* clearance corridor waypoints to generate multi-segment composite splines or filleted detour paths.

---

## Implications for Roadmap

Based on research findings, the implementation should be structured into 5 sequential phases:

### Phase 1: Core Cubic Bezier Geometry & SVG Path Generation
**Rationale:** Establishes fundamental Layer 0 math, connection primitives, port normal tangents, and SVG path generation. Completing unobstructed curve routing first provides the baseline for badges and rendering before tackling fillets or obstacle collisions.  
**Delivers:** `geometry.CubicBezier` primitive, `connections.Edge` parameter updates, outward cardinal port normal calculations, unobstructed `Routing.CURVE` routing in `router.py`, SVG `M...C` rendering, and arc-length badge centering in `renderer_svg.py`.  
**Addresses:** Cubic Bezier Routing (`Routing.CURVE`), Port Tangent Orientation, S-Curve Handle Distance Heuristics, Protocol Label Badge Placement.  
**Avoids:** Pitfall 1 (degenerate NaN markers), Pitfall 4 ($t=0.5$ label distortion), Pitfall 7 (waypoints polyline renderer breakage), Pitfall 9 (crooked arrowheads).

### Phase 2: Rounded Corner Fillets for Orthogonal Routing
**Rationale:** Orthogonal filleting operates purely on Manhattan polyline vertices generated by `OrthogonalRouter`. Developing this as an independent phase isolates corner clamping logic and SVG `Q` path formatting without entanglement with Bezier spline math.  
**Delivers:** Corner fillet generation algorithm with dynamic per-segment radius clamping, SVG quadratic Bezier (`Q`) formatting, and `arc_radius` support on `Edge`.  
**Addresses:** Rounded Corner Fillets for `Routing.ORTHOGONAL`.  
**Avoids:** Pitfall 3 (fillet radius clamping failure & "dog ears"), collinear zero-division errors.

### Phase 3: Obstacle Detection & Deflection for Curved Edges
**Rationale:** Obstacle deflection builds on both Phase 1 (Bezier math) and existing Layer 3 A* detour pathfinding. Isolating collision detection and deflection into its own phase allows rigorous testing of numerical stability and avoidance geometry.  
**Delivers:** Hierarchical collision detection (AABB broadphase + De Casteljau subdivision / chord sampling), backward-edge lateral clearance routing, and multi-segment spline synthesis using detour corridor waypoints.  
**Addresses:** Obstacle-Deflected Bezier Splines, Adaptive Tangent Scaling for Back-Edges & Loops.  
**Avoids:** Pitfall 2 (bow-tie loops on reverse flow), Pitfall 5 (convex hull false positives and raycast misses), Pitfall 6 (single-segment parabolic bulge trap).

### Phase 4: Configuration Hierarchy, Canvas Auto-Growth & Layout Integration
**Rationale:** With all routing engines and rendering paths stabilized, diagram-level configuration and layout pipeline integration unify the public API and ensure canvas viewports encompass curved boundaries.  
**Delivers:** `Diagram(routing=..., arc_radius=...)` constructor and `configure()` updates, builder default cascading, unified `EdgeRouter` dispatch in `layout/pipeline.py`, and analytical Bezier extrema roots ($B'(t) = 0$) in `_grow_canvas`.  
**Addresses:** Diagram Default + Per-Edge Routing Override, Mixed Semantic Routing.  
**Avoids:** Pitfall 8 (edge default masking diagram routing), Pitfall 10 (canvas clipping from unchecked curve extrema).

### Phase 5: Domain Gallery Validation & Visual Regression
**Rationale:** End-to-end verification across the entire suite of 88 domain gallery diagrams guarantees backward compatibility and verifies visual quality under production scenarios.  
**Delivers:** Golden master test suite verification via `resvg-py`, gallery examples featuring curved and filleted edges, and documentation updates.  
**Addresses:** Systemic visual verification across cloud, AI, datacenter, and IIoT diagrams.  
**Avoids:** Visual regressions on existing orthogonal diagrams and undetected edge-case clipping.

---

### Phase Ordering Rationale

- **Mathematical primitives before routing logic:** `CubicBezier` in Layer 0 must exist before Layer 3 (`CurveRouter`) can sample points or Layer 4 (`renderer_svg`) can place badges.
- **Unobstructed curves before obstacle deflection:** Verifying clean S-curves between unobstructed ports proves handle scaling heuristics before adding obstacle avoidance complexity.
- **Fillets decoupled from splines:** Filleting Manhattan lines is a polyline-to-arc transformation that does not depend on Bezier mathematics, allowing clean parallel or sequential implementation without coupling.
- **Engine stabilization before API wiring:** Establishing deterministic route output ensures diagram-level defaults and canvas growth logic operate on verified waypoint structures.
- **Gallery validation as final gate:** Running all 88 gallery diagrams verifies zero regressions across existing models while demonstrating new features.

---

### Research Flags

Phases likely needing deeper research/prototyping during phase planning:
- **Phase 3 (Obstacle Detection & Deflection):** Needs careful tuning of De Casteljau recursion depth limit (`max_depth = 6`) and Catmull-Rom tangent matching to ensure smooth $C^1$ transitions at corridor waypoints without introducing numerical jitter.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Core Cubic Bezier):** Standard analytical Bernstein polynomials and W3C SVG `C` path grammar.
- **Phase 2 (Rounded Fillets):** Standard quadratic Bezier fillets with established radius clamping formula.
- **Phase 4 (Configuration & Layout):** Standard Python class inheritance/cascading patterns and quadratic root formula for extrema.
- **Phase 5 (Gallery Validation):** Standard test harness execution with existing `uv run pytest`.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Pure Python standard library (`math`, `dataclasses`, `enum`, `itertools`, `heapq`) and W3C SVG 1.1/2.0 specifications thoroughly verified against zero-dependency constraint. |
| Features | HIGH | Feature scope benchmarked against Graphviz `dot`, XYFlow/React Flow, and Draw.io; aligned with existing codebase abstractions. |
| Architecture | HIGH | 5-layer architecture conforms to AST import boundary constraints (`test_module_boundaries.py`) and maintains `edge.waypoints` compatibility. |
| Pitfalls | HIGH | Mathematical edge cases (NaN marker angles, bow-tie loops, dog-ear fillets, lopsided badges, canvas clipping) analyzed with closed-form algorithmic solutions. |

**Overall confidence:** HIGH

---

### Gaps to Address

- **Detour Spline Tangent Continuity:** When converting A* corridor waypoints to multi-segment cubic Beziers, Catmull-Rom conversion ($C_1 = W_i + \frac{W_{i+1}-W_{i-1}}{6}$) must be verified against acute angle turns to ensure curves remain inside clearance channels.
- **Backward Edge Port Selection:** Determine whether unpinned reverse-flow edges should dynamically swap to North/South ports or use lateral clearance channels while respecting user-specified port constraints.

---

## Sources

### Primary (HIGH confidence)
- W3C SVG 1.1 / 2.0 Paths Specification ([W3C Candidate Recommendation](https://www.w3.org/TR/SVG2/paths.html)) — path commands `M`, `L`, `C`, `Q`, `A`, and marker orientation specifications.
- Existing codebase (`diagrams_as_code`):
  - `src/diagrams_as_code/connections.py` — `Port`, `Routing`, and `Edge` contracts.
  - `src/diagrams_as_code/geometry.py` — `Point`, `Rect`, `Anchor`, and `UnitBasis` primitives.
  - `src/diagrams_as_code/router.py` — `OrthogonalRouter`, `segment_intersects_rect`, and A* detour pathfinding.
  - `src/diagrams_as_code/renderer_svg.py` — SVG path rendering and protocol badge styling.
  - `src/diagrams_as_code/layout/pipeline.py` — layout solving and canvas growth pipeline.
  - `pyproject.toml` — runtime `dependencies = []` mandate and Python `>=3.10` requirement.

### Secondary (MEDIUM confidence)
- Pomax, *A Primer on Bezier Curves* ([online edition](https://pomax.github.io/bezierinfo/)) — arc-length chord sampling, De Casteljau recursive subdivision, and derivative root extrema.
- XYFlow / React Flow `bezier-edge.ts` — directional port normal tangents and handle distance scaling heuristics.
- Draw.io / mxGraph `OrthConnector` and `mxConnector.paintLine` — dynamic orthogonal corner fillet clamping routines.
- Graphviz `dot` / `neato` Spline Routing Documentation ([graphviz.org](https://graphviz.org/docs/attrs/splines/)) — obstacle avoidance via piecewise cubic splines within constraint polygons.

### Tertiary (LOW confidence)
- Foley, van Dam, Feiner, Hughes, *Computer Graphics: Principles and Practice* — Catmull-Rom to cubic Bezier conversion matrices (requires validation during Phase 3 implementation).

---
*Research completed: 2026-09-24*  
*Ready for roadmap: yes*
