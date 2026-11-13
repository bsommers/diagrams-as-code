# Phase 11: Configuration Hierarchy, Layout & Extrema Integration - Context

**Gathered:** 2026-09-27
**Status:** Ready for planning (revised 2026-09-28 after the edge-routing architecture review)

<domain>
## Phase Boundary

Phase 11 integrates diagram-wide configuration cascading, layout pipeline execution, and canvas auto-growth for curved and filleted edges. It ensures:
1. Diagram defaults (`routing`, `corner_radius`, `clearance`) cascade through fluent operators (`s1 >> s2`), explicit edge builders, and individual `Edge` instances with clean precedence.
2. The layout pipeline (`run_layout()`) automatically executes unified edge routing for all edges according to their configured routing strategy, caching waypoints and populating `diagram.routes`.
3. Diagram canvas boundaries automatically expand (`_grow_canvas` and `_frame`) to encompass analytical curve extrema (`CubicBezier.bbox()`), preventing clipping of high-arching Bezier curves and obstacle deflection detours.
4. 100% backward compatibility is preserved for existing diagrams, test suites, and gallery outputs.
5. **(Added 2026-09-28)** The routing data model is rebuilt first, because items 2–3 build on it: a typed `RoutedPath` output, a `RoutingScene` obstacle model, pure routers behind one dispatcher, and separate user-input and computed-route fields. This is Batches 1–2 of `docs/reviews/2026-09-28-edge-routing-architecture.md`, and it closes code-review findings CR-1, 3, 4, 9–13 and 15.

</domain>

<decisions>
## Implementation Decisions

### Diagram Default Hierarchy & Cascade Precedence
- **D-01:** `Diagram(routing=...)` defaults to `None`. When unset (`None`), it falls back to `"orthogonal"`, preserving 100% backward compatibility for all existing diagrams, test suites, and gallery renders.
- **D-02:** Configuration precedence follows a strict 3-tier cascade: Explicit `Edge` / `_EdgeBuilder` parameter > `Diagram` default property > System default (`"orthogonal"`, `corner_radius=0.0`, `clearance=15.0`).
- **D-03:** For `corner_radius`, `None` signals "inherit diagram default", allowing `corner_radius=0.0` to explicitly force sharp corners on individual edges even when a diagram-wide `corner_radius` (e.g. 12.0) is configured.
- **D-04:** `Diagram.configure(routing=..., corner_radius=..., clearance=...)` supports dynamic runtime reconfiguration of diagram routing defaults and marks `self._is_solved = False` to invalidate cached layout and routing.

### Layout Pipeline Routing Execution & Lifecycle
- **D-05 (revised 2026-09-28):** The existing `EdgeRouter` facade is the single dispatcher: `EdgeRouter.route(edge, style, scene) -> RoutedPath` dispatches on `Routing.DIRECT` / `ORTHOGONAL` / `CURVE` (the enum member is `CURVE`; no `CURVED` alias is needed). No new `router_for_routing` factory. `OrthogonalRouter.route` loses its CURVE branch, and `run_layout()` is the only caller of the routers.
- **D-06:** In `run_layout()`, edge routing executes BEFORE canvas auto-growth (`_grow_canvas`), populating `diagram.routes` so canvas boundary calculations have full visibility into edge trajectories and extrema. Order: solve elements → build scene → route → frame (elements + routes) → grow canvas.
- **D-07 (revised 2026-09-28):** User-supplied routes live in a new input field, `Edge.manual_waypoints`, which the engine never writes. When it is set, `run_layout()` builds a `RoutedPath` from it and skips auto-routing. Computed routes are never treated as input: every solve re-routes every other edge. *(The original wording, "preserve non-empty `edge.waypoints`", would have frozen every route at its first-solve geometry, because all edges have waypoints after one solve.)*
- **D-08 (revised 2026-09-28):** Obstacles come from a `RoutingScene` built once per solve from `solver.all_elements()` (which already includes groups). The scene holds each element's rect, its ancestor groups and the canvas rect. `scene.obstacles_for(edge, clearance)` returns padded rects, excluding the endpoints and the groups that contain them. Routers take the scene, never an `Iterable[Any]`.

### Routing Data Model (added 2026-09-28)
- **D-13:** A new `RoutedPath` frozen dataclass in `geometry.py` (layer 0) has `kind: PathKind` (`POLYLINE` | `BEZIER_CHAIN`), `points: tuple[Point, ...]` and `corner_radius: float`. Its methods are `segments()`, `bbox()`, `translate(dx, dy)`, `label_anchor()` and `svg_d()`. The fillet geometry moves here from `renderer_svg._render_filleted_path`. D-09 and D-10 are implemented with `bbox()` and `translate()`.
- **D-14:** Routers are pure. They return a `RoutedPath` and never assign to the `Edge`. `run_layout()` is the only writer of `diagram.routes: dict[Edge, RoutedPath]`. `Edge.waypoints` stays as a read-only compatibility property returning the last solved route's points (or `None`).
- **D-15:** The renderer only draws. `SVGRenderer.render` takes `routes` and emits `path.svg_d()` / `path.label_anchor()`, with no routing fallback, no obstacle logic and no model mutation. Direct callers use a new `router.route_all(edges, elements, width, height) -> dict[Edge, RoutedPath]` helper. `tests/test_module_boundaries.py` forbids `renderer_svg → router`.
- **D-16:** Fillet obstacle clamping (Phase 9, D-14) moves into routing time: the orthogonal router clamps each corner radius against `scene.obstacles_for(...)` when it builds the `RoutedPath`.

### Edge Style Resolution (added 2026-09-28; implements D-02 and D-03)
- **D-17:** `Edge` and `_EdgeBuilder` store `None` for every unset style field: `routing`, `corner_radius`, `clearance`. `Edge.clearance` and `Edge.routing` getters return the resolved value after a solve, or the system default before one.
- **D-18:** A single function, `resolve_edge_style(edge, diagram) -> EdgeStyle(routing, corner_radius, clearance)` in `layout/pipeline.py`, is called for every edge on every solve, whether the edge came from `connect()`, `>>`, `add()` or `Edge(...)`. The per-site resolution in `connect()`, `_EdgeBuilder.__rshift__` and `solve()` is removed. Both routers honour `style.clearance`, so `OrthogonalRouter` stops ignoring clearance. The routers' `clearance=15.0` parameter is removed.
- **D-19:** `_EdgeBuilder.__call__` raises `TypeError` on unknown keyword arguments. Per-call `clearance` applies to the edges created by that call only; it is not stored on the builder.

### Canvas Auto-Growth & Extrema Clipping Margin
- **D-09:** Analytical curve bounding box: `_grow_canvas` evaluates analytical bounding boxes (`CubicBezier.bbox()` for curved/bezier edges, and corner/vertex envelopes for orthogonal/polyline) to compute the true geometric envelope of all edges.
- **D-10:** Coordinate framing (`_frame`): If Bezier curves or detours arch into negative coordinates (or above the top title banner area, `min_y < FRAME_Y` or `min_x < FRAME_X`), framing translates both elements and edge waypoints by `offset_x` / `offset_y` so curves are never clipped on the top or left.
- **D-11:** Canvas margins: Standard `FRAME_X` (60.0px) and `FRAME_Y` (80.0px) framing margins are applied between curve extrema and the diagram canvas boundary, matching element layout margins.
- **D-12:** Max-expansion only: Canvas dimensions are updated via `diagram.width = max(diagram.width, max_x + FRAME_X)` and `diagram.height = max(diagram.height, max_y + FRAME_Y)`, preserving user-specified dimensions unless content actually overflows.

### Claude's Discretion
- Exact names of `RoutingScene`, `EdgeStyle`, `PathKind` and `route_all`, and whether `RoutingScene` lives in `router.py` or a new layer-3 `routing_scene.py`. A new module must be classified in `tests/test_module_boundaries.py`.
- Translation during `_frame` uses `RoutedPath.translate()`; no separate `translate_waypoints` helper.
- Whether `diagram.routes` is keyed by `Edge` (requires identity hashing, the default) or kept as `id(edge)`.
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

### Reviews (added 2026-09-28)
- `docs/reviews/2026-09-28-edge-routing-architecture.md` — target architecture, Batches 1–2 (this phase), CR-n → roadmap mapping.
- `docs/reviews/2026-09-22-architecture-boundaries.md` — the earlier decision that routing belongs in layout and the renderer receives paths.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `CubicBezier.bbox()` in `geometry.py`: Solves analytical derivative roots $B'(t) = 0$ in $[0, 1]$ to calculate exact tight bounding box without sampling approximation.
- `_EdgeBuilder.__rshift__` in `diagram.py`: Currently cascades `corner_radius` and `clearance` from `diag` onto `diag.connect(...)`. Under D-18 this per-site cascade is removed in favour of `resolve_edge_style` at solve time.
- `EdgeRouter` in `router.py`: exported, currently unused internally; becomes the single dispatcher (D-05).
- `_frame()` in `layout/pipeline.py`: Already computes `min_x`, `min_y` and translates root elements. Can be augmented to handle edge waypoints and curve extrema.
- `_grow_canvas()` in `layout/pipeline.py`: Already expands `diagram.width` and `diagram.height` based on element bounds. Needs to incorporate edge extrema.

### Established Patterns
- Zero external runtime dependencies: all mathematical operations use standard library `math` and typed dataclasses.
- Explicit priority: explicit edge attributes override diagram defaults, which override global system defaults.
- Cache invalidation: setting layout or routing properties invalidates `_is_solved = False` to trigger re-routing on next render.

### Integration Points
- `src/diagrams_as_code/diagram.py`: Add `routing` parameter and property to `Diagram.__init__`, `Diagram.configure()`, and cascade in `_EdgeBuilder.__rshift__` and `Diagram.solve()`.
- `src/diagrams_as_code/layout/pipeline.py`: Update `run_layout()` to resolve styles, build the scene, route through `EdgeRouter` before `_frame()` / `_grow_canvas()`, and include `RoutedPath.bbox()` in both.
- `src/diagrams_as_code/geometry.py`: Add `RoutedPath` / `PathKind` (D-13).
- `src/diagrams_as_code/renderer_svg.py`: Remove routing fallback, `_render_filleted_path` obstacle logic, and length-based path decoding (D-15, D-16).

</code_context>

<specifics>
## Specific Ideas
- Prevent clipping on top-arching or deflected curves: `_frame` and `_grow_canvas` work in tandem to ensure high-arching Bezier curves never clip past the top/left/bottom/right canvas edges.
- Fluent operator consistency: `s1 >> s2` must automatically produce curved edges when `Diagram(routing="curved")` is active, without requiring per-edge overrides.

</specifics>

<deferred>
## Deferred Ideas
- **To a follow-up phase (review Batches 4–5):** CurveRouter internals (axis-transposed corridor code, iterative widening, clamped handle lengths, `CubicBezier.intersects_rect` leaf precision: CR-5, 6, 8), the explicit-port escape corridor scope (CR-7), and a gallery-wide routing invariant test. The invariant test depends on the CurveRouter fixes to pass, so it ships with them.
- The `min_top <= 30` "no room above" port heuristic (CR-2) becomes obsolete once D-10 framing can translate. Removing it is in scope only if it falls out naturally; otherwise it goes to the follow-up phase.

</deferred>

---

*Phase: 11-configuration-hierarchy-layout-extrema-integration*
*Context gathered: 2026-09-27; revised 2026-09-28 (D-05–D-08 revised, D-13–D-19 added)*
