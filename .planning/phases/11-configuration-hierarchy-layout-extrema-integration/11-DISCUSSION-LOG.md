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
