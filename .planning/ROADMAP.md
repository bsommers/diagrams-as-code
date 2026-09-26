# Roadmap: Milestone v0.8.0 (Curved & Bezier Edge Routing Engine)

## Milestone History

- **[v0.7.0 Milestone](milestones/v0.7.0-ROADMAP.md)** — Shipped 2026-09-24: Phase 7 (Obstacle-aware orthogonal Manhattan routing, collision detection, and multi-rank crossing minimization).
- **[v0.6.0 Milestone](milestones/v0.6.0-ROADMAP.md)** — Shipped 2026-09-23: Phase 4 (CLI `--interactive` flag), Phase 5 (Client-side Search & Highlight), Phase 6 (Viewport Minimap Navigator).
- **[v0.5.0 Milestone](milestones/v0.5.0-ROADMAP.md)** — Shipped 2026-09-23: Phase 1 (Polish & Edge Robustness), Phase 2 (Typed Constraints & Group Flow Decoupling), Phase 3 (Interactive SVG Pan-Zoom & Collapsible Groups).
- **[v0.4.0 Milestone](milestones/v0.5.0-ROADMAP.md)** — Shipped 2026-09-22: Auto-layout, JSON layout files, CLI, modularity refactoring, unconditional canvas growth.

## Overview

Milestone `v0.8.0` expands the Diagrams as Code engine beyond sharp Manhattan orthogonal lines to deliver publication-quality cubic Bezier edge routing (`Routing.CURVE`) and rounded corner fillets (`arc_radius` on `Routing.ORTHOGONAL`). The implementation adheres strictly to pure Python standard library math and vector primitives (zero external dependencies), full backward compatibility across all 88 domain gallery diagrams, and clean architectural separation between Layer 0 geometry, Layer 3 curve routing, and Layer 4 SVG path rendering.

## Phases

- [x] **Phase 8: Core Cubic Bezier Geometry & SVG Path Generation** - Layer 0 `CubicBezier` vector primitive, outward port normal tangents, distance-proportional handle heuristics, SVG `M...C` path rendering, and arc-length midpoint badge positioning. (completed 2026-09-26)
- [ ] **Phase 9: Rounded Corner Fillets for Orthogonal Routing** - Orthogonal corner filleting, dynamic radius clamping ($\min(R, L_1/2, L_2/2)$) against "dog ear" artifacts, and SVG `Q` quadratic path generation.
- [ ] **Phase 10: Obstacle Detection & Deflection for Curved Edges** - Bounding box broadphase and De Casteljau collision detection, obstacle-deflected multi-segment splines, and lateral clearance routing for reverse-flow back-edges.
- [ ] **Phase 11: Configuration Hierarchy, Layout & Extrema Integration** - Diagram-level default cascade, fluent operator inheritance, unified layout routing pipeline, and canvas auto-expansion via analytical curve extrema roots.

---

## Phase Details

### Phase 8: Core Cubic Bezier Geometry & SVG Path Generation

**Goal:** Establish foundational cubic Bezier mathematical primitives in Layer 0, calculate port normal tangent handles in Layer 3, and render native SVG cubic curves with tangentially aligned arrowheads and arc-length centered protocol badges in Layer 4.

**Requirements Covered:**

- `BEZ-01`: User can set `routing=Routing.CURVE` (or `"curve"`) on an `Edge` to connect elements with an analytical cubic Bezier curve.
- `BEZ-02`: Curve router computes control handles aligned with cardinal port outward normal vectors (NORTH, SOUTH, EAST, WEST) so curves enter/exit strictly perpendicular to node bounds.
- `BEZ-03`: Curve router applies distance-proportional handle scaling along primary flow axes (`LR` and `TB`) to produce smooth S-curves without kinks or excessive bulging.
- `BEZ-04`: SVG renderer emits native cubic Bezier `<path d="M... C...">` elements with correct arrowhead marker rotation angles at endpoints.
- `BEZ-05`: Protocol label badges on curved edges are positioned at the curve's arc-length midpoint with non-overlapping background pills.

**Success Criteria:**

1. User can define an `Edge` with `routing=Routing.CURVE` (or `"curve"`) between two elements, producing a smooth cubic Bezier curve that exits and enters strictly normal to the node boundaries without manual control point manipulation.
2. Rendered SVG output contains native `<path d="M x0 y0 C x1 y1, x2 y2, x3 y3">` elements with arrowhead markers aligned tangentially at destination endpoints (without `NaN` or erratic orientation angles).
3. Curves across primary flow directions (`LR` and `TB`) scale control handles proportionally with node distance, eliminating kinks, cusps, or excessive handle bulge.
4. Protocol label badges (`label="HTTPS"`) are positioned along the physical arc-length midpoint of the cubic curve with high-contrast background pills that do not clip or distort on asymmetric curves.

---

### Phase 9: Rounded Corner Fillets for Orthogonal Routing

**Goal:** Implement quadratic Bezier corner filleting on Manhattan orthogonal paths with dynamic per-segment radius clamping and native SVG `Q` path command generation.

**Requirements Covered:**

- `FILLET-01`: User can configure `corner_radius` (or `arc_radius`) on orthogonal edges to produce rounded 90-degree corner bends.
- `FILLET-02`: Corner filleting dynamically clamps radius per corner to $\min(R, L_1/2, L_2/2)$ so short segments never invert, create "dog ears", or overlap.
- `FILLET-03`: SVG renderer emits quadratic Bezier (`Q`) commands connecting corner fillet tangent points for $C^1$-continuous smooth bends.

**Success Criteria:**

1. User can set `corner_radius=12` (or `arc_radius=12`) on orthogonal edges or diagrams to render smooth, rounded 90-degree corner bends instead of sharp right angles.
2. Short Manhattan segments automatically clamp corner radii to $\min(R, L_1/2, L_2/2)$ (and suppress fillets below $2\text{px}$), preventing inverted arcs, overlapping loops, or "dog ear" visual artifacts.
3. Rendered SVG paths for filleted orthogonal edges emit quadratic Bezier (`Q`) commands connecting fillet tangent points, maintaining tangent continuity with adjacent linear segments.

---

### Phase 10: Obstacle Detection & Deflection for Curved Edges

**Goal:** Detect bounding box intersections on candidate Bezier curves and route collision-free deflected multi-segment splines and backward edges around intervening nodes and groups.

**Requirements Covered:**

- `CURVEOBS-01`: Router detects when candidate cubic Bezier curves intersect intervening obstacle bounding boxes.
- `CURVEOBS-02`: When an obstacle collision is detected, router deflects the curve through collision-free clearance channel waypoints as a smooth multi-segment spline.
- `CURVEOBS-03`: Reverse-flow connections (backward edges) adaptively scale control points into lateral clearance channels to avoid clipping through source/target nodes.

**Success Criteria:**

1. When a direct cubic Bezier trajectory intersects an intervening node or group bounding box, the routing engine detects the collision via bounding box broadphase and De Casteljau subdivision.
2. Deflected curved edges automatically navigate through clearance channel waypoints as smooth multi-segment splines without penetrating obstacle boundaries.
3. Reverse-flow connections (e.g. backward edges against diagram flow) route around source and target nodes via lateral clearance corridors rather than creating bow-tie loops or piercing node interiors.

---

### Phase 11: Configuration Hierarchy, Layout & Extrema Integration

**Goal:** Unify diagram-wide routing defaults, fluent operator inheritance, automated pipeline routing dispatch, and analytical Bezier extrema canvas expansion.

**Requirements Covered:**

- `CFG-01`: User can set diagram-wide default edge routing and corner radius via `Diagram(routing=..., corner_radius=...)`.
- `CFG-02`: Connections created via fluent operators (`s1 >> s2`) inherit diagram defaults while individual `Edge` parameters take precedence.
- `CFG-03`: Layout pipeline automatically runs unified edge routing for all diagram edges, populating `edge.waypoints` and `diagram.routes`.
- `CFG-04`: Diagram canvas boundaries automatically expand (`_grow_canvas`) to encompass analytical curve extrema so high-arching Bezier curves are never clipped.

**Success Criteria:**

1. User can specify default edge routing and corner radius at the diagram level (`Diagram(routing=Routing.CURVE, corner_radius=10)`), with fluent connections (`node1 >> node2`) automatically inheriting these defaults.
2. Individual `Edge(routing=..., corner_radius=...)` instances seamlessly override diagram-level defaults, supporting mixed routing styles (e.g., curved feedback loops alongside orthogonal main pipelines) in a single diagram.
3. The layout pipeline runs unified edge routing across all edges, populating `edge.waypoints` and `diagram.routes` consistently across `manual`, `auto`, and layout-file modes.
4. Canvas auto-growth computes analytical polynomial extrema ($B'(t) = 0$) for all cubic Bezier curves, ensuring canvas boundaries expand to enclose high-arching curves without clipping.
