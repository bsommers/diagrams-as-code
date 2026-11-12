# Phase 11: Configuration Hierarchy, Layout & Extrema Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-27
**Phase:** 11-configuration-hierarchy-layout-extrema-integration
**Areas discussed:** Diagram Default Hierarchy & Cascade Precedence, Layout Pipeline Routing Execution & Lifecycle, Canvas Auto-Growth & Extrema Clipping Margin

---

## Diagram Default Hierarchy & Cascade Precedence

| Option | Description | Selected |
|--------|-------------|----------|
| Optional with None default | Diagram(routing=None) falls back to "orthogonal" (preserving 100% backward compatibility for all existing diagrams and gallery tests). | ✓ |
| Explicit "orthogonal" default | Diagram(routing="orthogonal") explicitly sets the default property on the diagram instance. | |
| You decide | Choose the cleanest architecture for backward compatibility. | |

**User's choice:** Optional with None default: Diagram(routing=None) falls back to "orthogonal" (preserving 100% backward compatibility for all existing diagrams and gallery tests).

| Option | Description | Selected |
|--------|-------------|----------|
| 3-tier cascade | Explicit Edge/Builder parameter > Diagram default > System default ("orthogonal" / corner_radius=0.0). | ✓ |
| Diagram strict override | Diagram default always overrides unset edge parameters, but explicit Edge(routing=...) takes precedence. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** 3-tier cascade: Explicit Edge/Builder parameter > Diagram default > System default ("orthogonal" / corner_radius=0.0).

| Option | Description | Selected |
|--------|-------------|----------|
| Treat None as inherit | Treat None as 'inherit diagram default', allowing 0.0 to explicitly force sharp corners on individual edges. | ✓ |
| Treat 0.0 as inherit | Treat 0.0 as inherit diagram default as well. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Treat None as 'inherit diagram default', allowing 0.0 to explicitly force sharp corners on individual edges.

| Option | Description | Selected |
|--------|-------------|----------|
| Dynamic configure with invalidation | Support routing in Diagram.configure(routing=...) and invalidate solved layout/routing state (_is_solved = False). | ✓ |
| Init-only configuration | Routing can only be configured during Diagram.__init__. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Yes, support routing in Diagram.configure(routing=...) and invalidate solved layout/routing state (_is_solved = False).

---

## Layout Pipeline Routing Execution & Lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| Router Dispatcher / Factory | Route each edge with router_for_routing(edge.routing) (e.g. CurveRouter for curved/bezier, OrthogonalRouter for orthogonal, direct line for direct/polyline). | ✓ |
| Single unified router class | Wrap all routing algorithms inside a single UnifiedRouter class that delegates internally. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Router Dispatcher / Factory: Route each edge with router_for_routing(edge.routing) (e.g. CurveRouter for curved/bezier, OrthogonalRouter for orthogonal, direct line for direct/polyline).

| Option | Description | Selected |
|--------|-------------|----------|
| Route edges first, then expand canvas | Run unified edge routing before _grow_canvas so canvas boundaries can inspect all edge waypoints and curve extrema. | ✓ |
| Two-pass growth | Grow canvas for elements first, route edges, then expand canvas further if any edge extrema exceed current bounds. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Route edges first, then expand canvas: Run unified edge routing before _grow_canvas so canvas boundaries can inspect all edge waypoints and curve extrema.

| Option | Description | Selected |
|--------|-------------|----------|
| Respect manually provided waypoints | If edge.waypoints is already populated and not empty, preserve it and skip auto-routing for that edge. | ✓ |
| Always re-route | Overwrite edge.waypoints unconditionally during run_layout(). | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Respect manually provided waypoints: If edge.waypoints is already populated and not empty, preserve it and skip auto-routing for that edge.

| Option | Description | Selected |
|--------|-------------|----------|
| Pass all elements and groups | Provide elements + diagram.groups as obstacles to routers for complete deflection coverage. | ✓ |
| Pass elements only | Continue passing elements (nodes) as obstacles, ignoring group bounding boxes. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Pass all elements and groups: Provide elements + diagram.groups as obstacles to routers for complete deflection coverage.

---

## Canvas Auto-Growth & Extrema Clipping Margin

| Option | Description | Selected |
|--------|-------------|----------|
| Analytical bbox per segment | Use CubicBezier.bbox() for curved edges and vertex bounding box for orthogonal/polyline edges. | ✓ |
| Control polygon AABB | Use the bounding box of all control points and waypoints as a conservative upper bound. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Analytical bbox per segment: Use CubicBezier.bbox() for curved edges and vertex bounding box for orthogonal/polyline edges.

| Option | Description | Selected |
|--------|-------------|----------|
| Framing translation | Translate both elements and edge waypoints by offset_x / offset_y when curve extrema reach negative coordinates (or min_y < FRAME_Y). | ✓ |
| Expand width/height only | Only expand canvas width and height (bottom and right), assuming elements are placed with enough top/left clearance. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Yes, translate both elements and edge waypoints by offset_x / offset_y when curve extrema reach negative coordinates (or min_y < FRAME_Y).

| Option | Description | Selected |
|--------|-------------|----------|
| Standard FRAME margins | Standard FRAME_X (60px) and FRAME_Y (80px) margins, consistent with element layout framing. | ✓ |
| Dedicated edge buffer | Dedicated edge clearance buffer (e.g. 30px) beyond curve extrema. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Standard FRAME_X (60px) and FRAME_Y (80px) margins, consistent with element layout framing.

| Option | Description | Selected |
|--------|-------------|----------|
| Max-expansion only | diagram.width = max(diagram.width, max_x + margin), preserving fixed/explicit user canvas dimensions unless content overflows. | ✓ |
| Shrink-to-fit | Recalculate canvas dimensions tightly around content. | |
| You decide | Choose the cleanest architecture. | |

**User's choice:** Max-expansion only: diagram.width = max(diagram.width, max_x + margin), preserving fixed/explicit user canvas dimensions unless content overflows.

---

## Claude's Discretion
- Router factory naming and location (`router_for_routing` / `get_router`).
- Waypoint coordinate translation utility helper (`translate_waypoints`).
- Refactoring decomposition within `_grow_canvas()` and `_frame()`.

## Deferred Ideas
None — discussion stayed within phase scope.

---

## Revision — 2026-09-28 (post-review)

**Trigger:** the `/code-review` of v0.8.2..HEAD (15 findings) and the architecture review `docs/reviews/2026-09-28-edge-routing-architecture.md`.

**User's choice:** fold review Batches 1–2 (routing data model + edge style resolution) into Phase 11; defer Batches 4–5 (CurveRouter internals, invariant test) to a follow-up phase.

| Decision | Change | Reason |
|---|---|---|
| D-05 | `router_for_routing` → existing `EdgeRouter` as sole dispatcher | Three routing entry points already exist (CR-1, CR-15); a fourth would add to the problem. |
| D-07 | preserve non-empty `edge.waypoints` → new `Edge.manual_waypoints` input field | Every edge has waypoints after one solve, so the original rule would freeze routes on re-solve. |
| D-08 | `elements + groups` → `RoutingScene` | `all_elements()` already includes groups; the real bug is three drifting obstacle filters (CR-3, CR-4, CR-14). |
| D-13–D-16 | added: `RoutedPath`, pure routers, draw-only renderer, fillet clamping at route time | D-09 and D-10 need `bbox()` / `translate()` on a typed path; the renderer was decoding routes from list lengths. |
| D-17–D-19 | added: `None` for unset, `resolve_edge_style`, strict `_EdgeBuilder.__call__` | CR-9, CR-10, CR-11 and CR-13; this is how D-02 and D-03 get implemented. |

