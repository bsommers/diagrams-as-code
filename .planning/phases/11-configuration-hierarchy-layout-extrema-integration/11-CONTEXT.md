# Phase 11: Configuration Hierarchy, Layout & Extrema Integration - Context

**Gathered:** 2026-09-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 11 integrates diagram-wide configuration cascading, layout pipeline execution, and canvas auto-growth for curved and filleted edges. It ensures:
1. Diagram defaults (`routing`, `corner_radius`, `clearance`) cascade through fluent operators (`s1 >> s2`), explicit edge builders, and individual `Edge` instances with clean precedence.
2. The layout pipeline (`run_layout()`) automatically executes unified edge routing for all edges according to their configured routing strategy, caching waypoints and populating `diagram.routes`.
3. Diagram canvas boundaries automatically expand (`_grow_canvas` and `_frame`) to encompass analytical curve extrema (`CubicBezier.bbox()`), preventing clipping of high-arching Bezier curves and obstacle deflection detours.
4. 100% backward compatibility is preserved for existing diagrams, test suites, and gallery outputs.

</domain>

<decisions>
## Implementation Decisions

### Diagram Default Hierarchy & Cascade Precedence
- **D-01:** `Diagram(routing=...)` defaults to `None`. When unset (`None`), it falls back to `"orthogonal"`, preserving 100% backward compatibility for all existing diagrams, test suites, and gallery renders.
- **D-02:** Configuration precedence follows a strict 3-tier cascade: Explicit `Edge` / `_EdgeBuilder` parameter > `Diagram` default property > System default (`"orthogonal"`, `corner_radius=0.0`, `clearance=15.0`).
- **D-03:** For `corner_radius`, `None` signals "inherit diagram default", allowing `corner_radius=0.0` to explicitly force sharp corners on individual edges even when a diagram-wide `corner_radius` (e.g. 12.0) is configured.
- **D-04:** `Diagram.configure(routing=..., corner_radius=..., clearance=...)` supports dynamic runtime reconfiguration of diagram routing defaults and marks `self._is_solved = False` to invalidate cached layout and routing.

### Layout Pipeline Routing Execution & Lifecycle
- **D-05:** Layout pipeline uses a dynamic router factory / dispatcher: `router_for_routing(edge.routing)` dispatches to `CurveRouter` for `Routing.CURVED`, `OrthogonalRouter` for `Routing.ORTHOGONAL`, or direct/polyline calculations.
- **D-06:** In `run_layout()`, edge routing executes BEFORE canvas auto-growth (`_grow_canvas`), populating `edge.waypoints` and `diagram.routes` so canvas boundary calculations have full visibility into edge trajectories and extrema.
- **D-07:** If an `Edge` already has `edge.waypoints` explicitly populated and non-empty (e.g. manually placed or loaded from file), `run_layout()` preserves it and skips auto-routing for that edge.
- **D-08:** `run_layout()` passes all elements AND diagram groups (`elements + diagram.groups`) as obstacles to the edge routers for comprehensive collision deflection coverage.

### Canvas Auto-Growth & Extrema Clipping Margin
- **D-09:** Analytical curve bounding box: `_grow_canvas` evaluates analytical bounding boxes (`CubicBezier.bbox()` for curved/bezier edges, and corner/vertex envelopes for orthogonal/polyline) to compute the true geometric envelope of all edges.
- **D-10:** Coordinate framing (`_frame`): If Bezier curves or detours arch into negative coordinates (or above the top title banner area, `min_y < FRAME_Y` or `min_x < FRAME_X`), framing translates both elements and edge waypoints by `offset_x` / `offset_y` so curves are never clipped on the top or left.
- **D-11:** Canvas margins: Standard `FRAME_X` (60.0px) and `FRAME_Y` (80.0px) framing margins are applied between curve extrema and the diagram canvas boundary, matching element layout margins.
- **D-12:** Max-expansion only: Canvas dimensions are updated via `diagram.width = max(diagram.width, max_x + FRAME_X)` and `diagram.height = max(diagram.height, max_y + FRAME_Y)`, preserving user-specified dimensions unless content actually overflows.

### Claude's Discretion
- Router factory naming and location: implementation can place `get_router(routing: Routing)` or `router_for_routing` in `router.py` or `layout/pipeline.py`.
- Translation helper: translation of edge waypoints during `_frame` can be encapsulated in a clean utility function `translate_waypoints(waypoints, dx, dy)`.
- Internal structure of `_grow_canvas`: may split or combine element and edge extrema scanning cleanly.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core Engine & Routing
- `src/diagrams_as_code/diagram.py` — `Diagram` container, context management, `_EdgeBuilder` fluent operator (`>>`), `solve()`, and `render_svg()`.
- `src/diagrams_as_code/connections.py` — `Edge` class, `Routing` enum, `corner_radius`, `clearance`, and validation helpers.
- `src/diagrams_as_code/router.py` — `OrthogonalRouter`, `CurveRouter`, and routing interfaces.
- `src/diagrams_as_code/layout/pipeline.py` — Layout pipeline: `run_layout()`, `_reset()`, `_frame()`, and `_grow_canvas()`.
- `src/diagrams_as_code/geometry.py` — `Point`, `Rect`, `QuadraticBezier`, and `CubicBezier` with analytical `.bbox()`.
- `src/diagrams_as_code/renderer_svg.py` — SVG renderer: path generation and marker rendering.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `CubicBezier.bbox()` in `geometry.py`: Solves analytical derivative roots $B'(t) = 0$ in $[0, 1]$ to calculate exact tight bounding box without sampling approximation.
- `_EdgeBuilder.__rshift__` in `diagram.py`: Already cascades `corner_radius` and `clearance` from `diag` onto `diag.connect(...)`. Needs to cascade `routing` as well.
- `_frame()` in `layout/pipeline.py`: Already computes `min_x`, `min_y` and translates root elements. Can be augmented to handle edge waypoints and curve extrema.
- `_grow_canvas()` in `layout/pipeline.py`: Already expands `diagram.width` and `diagram.height` based on element bounds. Needs to incorporate edge extrema.

### Established Patterns
- Zero external runtime dependencies: all mathematical operations use standard library `math` and typed dataclasses.
- Explicit priority: explicit edge attributes override diagram defaults, which override global system defaults.
- Cache invalidation: setting layout or routing properties invalidates `_is_solved = False` to trigger re-routing on next render.

### Integration Points
- `src/diagrams_as_code/diagram.py`: Add `routing` parameter and property to `Diagram.__init__`, `Diagram.configure()`, and cascade in `_EdgeBuilder.__rshift__` and `Diagram.solve()`.
- `src/diagrams_as_code/layout/pipeline.py`: Update `run_layout()` to route edges before `_grow_canvas()`, support dynamic routing via `router_for_routing()`, and update `_grow_canvas()` and `_frame()` to incorporate curve extrema.

</code_context>

<specifics>
## Specific Ideas
- Prevent clipping on top-arching or deflected curves: `_frame` and `_grow_canvas` work in tandem to ensure high-arching Bezier curves never clip past the top/left/bottom/right canvas edges.
- Fluent operator consistency: `s1 >> s2` must automatically produce curved edges when `Diagram(routing="curved")` is active, without requiring per-edge overrides.

</specifics>

<deferred>
## Deferred Ideas
None — discussion stayed within phase scope.

</deferred>

---

*Phase: 11-configuration-hierarchy-layout-extrema-integration*
*Context gathered: 2026-09-27*
