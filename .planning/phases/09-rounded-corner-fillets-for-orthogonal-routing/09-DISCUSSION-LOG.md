# Phase 09: Rounded Corner Fillets for Orthogonal Routing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-26  
**Phase:** 09-rounded-corner-fillets-for-orthogonal-routing  
**Areas discussed:** API Parameter & Default Behavior, Fillet Radius Clamping & Short Segments, SVG Path Generation & Mathematical Contract, Obstacle Avoidance & Clearance Integration  

---

## API Parameter & Default Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| `corner_radius` primary with `arc_radius` alias | Support `corner_radius` as primary on Edge and Diagram, with `arc_radius` alias | ✓ |
| `arc_radius` primary | Use `arc_radius` as primary attribute on Edge and Diagram | |
| Strict `corner_radius` only | No aliases to keep API surface minimal | |

**User's choice:** Support `corner_radius` as primary on Edge and Diagram, with `arc_radius` as an accepted alias (Diagram(corner_radius=...) sets default; Edge overrides).

| Option | Description | Selected |
|--------|-------------|----------|
| Sharp corners by default | `corner_radius=0.0 / None` — 100% backward compatibility | ✓ |
| Opt-in via theme | Theme presets define default corner radius | |
| Always-on default | `corner_radius=10.0` default for all orthogonal edges | |

**User's choice:** Sharp corners by default (corner_radius=0.0 / None) — guarantees 100% backward compatibility and zero visual diff across all 88 gallery diagrams and existing tests unless explicitly enabled.

| Option | Description | Selected |
|--------|-------------|----------|
| Graceful ignore on non-orthogonal | Apply corner_radius strictly to ORTHOGONAL; gracefully ignore on DIRECT and CURVE | ✓ |
| Strict validation | Raise ValueError if corner_radius > 0 on non-orthogonal edge | |
| Claude's discretion | Graceful ignore with debug logging | |

**User's choice:** Apply corner_radius strictly to Routing.ORTHOGONAL edges. If set on Routing.CURVE or Routing.DIRECT edges, gracefully ignore it without raising an exception.

| Option | Description | Selected |
|--------|-------------|----------|
| Defensive coercion & error | Coerce numeric int/float to float; raise ValueError if corner_radius < 0.0 or non-numeric | ✓ |
| Automatic clamp | Clamp negative values automatically to 0.0 without error | |
| Claude's discretion | Discretion on numeric validation | |

**User's choice:** Coerce numeric int/float inputs to float; raise ValueError if corner_radius < 0.0 or non-numeric (strict defensive validation).

---

## Fillet Radius Clamping & Short Segments

| Option | Description | Selected |
|--------|-------------|----------|
| Strict 50% budget | R_clamped = min(R, L_in/2.0, L_out/2.0) | ✓ |
| Dynamic greedy | First corner takes min(R, L_in/2, L_segment) | |
| Proportional scaling | Scale radii proportionally | |

**User's choice:** Strict 50% segment budget per corner: R_clamped = min(R, L_in / 2.0, L_out / 2.0) — guarantees adjacent corners never collide or overlap even on short segments.

| Option | Description | Selected |
|--------|-------------|----------|
| Suppress R < 2.0px | Falls back to clean sharp corner for that bend | ✓ |
| Suppress R < 4.0px | Higher threshold for cleaner rendering | |
| No threshold cutoff | Always render fillet if R > 0 | |

**User's choice:** Suppress fillet if R_effective < 2.0px — falls back to a clean sharp corner for that specific bend, preventing sub-pixel rasterization artifacts.

| Option | Description | Selected |
|--------|-------------|----------|
| Strict 90-degree check | Apply fillet only when dot(u_in, u_out) == 0 | ✓ |
| Any non-collinear angle | Allow filleting on any bend | |
| Claude's discretion | Discretion on orthogonality check | |

**User's choice:** Filter strictly for 90-degree orthogonal turns: apply fillet only when dot(u_in, u_out) == 0 (perpendicular). Collinear segments continue straight; turnarounds remain linear.

| Option | Description | Selected |
|--------|-------------|----------|
| Minimum straight lead-in | Require minimum lead-in (10px or L/2) at port anchors and arrowheads | ✓ |
| Uniform 50% rule | Treat endpoints with standard 50% rule | |
| Claude's discretion | Discretion on port clearance | |

**User's choice:** Require minimum straight lead-in (e.g. 5px or 10px) at port anchors and arrowhead destinations so fillets never curve directly inside the node boundary or underneath arrowheads.

---

## SVG Path Generation & Mathematical Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Quadratic Bezier `Q` | `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y` — exact tangent continuity | ✓ |
| Elliptical arc `A` | SVG `A R R 0 0 [sweep] T2.x T2.y` circular arc | |
| Cubic Bezier `C` | Cubic Bezier circular arc approximation | |

**User's choice:** Emit quadratic Bezier `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y` — exact tangent continuity at corner vertices, compact syntax, and directly satisfies FILLET-03.

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated `QuadraticBezier` in Layer 0 | Implement `geometry.QuadraticBezier(p0, p1, p2)` in Layer 0 | ✓ |
| Inline in renderer | Compute tangent points and Q string directly in renderer_svg.py | |
| Claude's discretion | Discretion on Layer 0 primitives | |

**User's choice:** Implement `geometry.QuadraticBezier(p0, p1, p2)` in Layer 0 (`geometry.py`) — complete standard mathematical primitive with point_at, tangent_at, bbox, and arc_length, mirroring CubicBezier.

| Option | Description | Selected |
|--------|-------------|----------|
| Clean Manhattan in `Edge.waypoints` | Keep waypoints as sharp Manhattan vertices; fillet in Layer 4 | ✓ |
| Store filleted in waypoints | Pre-calculate fillet waypoints in router.py | |
| Claude's discretion | Discretion on layer boundary | |

**User's choice:** Keep `Edge.waypoints` as sharp Manhattan vertices; perform fillet tangent point generation in Layer 4 (`renderer_svg.py` or router helper) during SVG path emission — preserves JSON layout compatibility, collision checking, and waypoint contracts.

| Option | Description | Selected |
|--------|-------------|----------|
| Centered on longest straight segment | Keep existing orthogonal badge placement on longest straight segment | ✓ |
| 50% total path length | Place badge at exact 50% path distance | |
| Claude's discretion | Discretion on badge placement | |

**User's choice:** Keep existing orthogonal badge placement on the midpoint of the longest straight segment — fillets only soften corners; straight segment centering remains visually optimal and readable.

---

## Obstacle Avoidance & Clearance Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Uniform filleting | Apply corner fillets across default Manhattan and obstacle detour paths | ✓ |
| Default paths only | Keep detour corners around obstacles sharp | |
| Claude's discretion | Discretion on detour filleting | |

**User's choice:** Apply corner fillets uniformly across both default Manhattan paths and obstacle detour paths — consistent aesthetic styling across the entire diagram.

| Option | Description | Selected |
|--------|-------------|----------|
| Dynamic clearance guard | Clamp R_effective so fillet apex maintains minimum clearance (4.0px) from obstacles | ✓ |
| Rely on 15px corridor | Rely on segment length budget and 15px clearance corridor | |
| Claude's discretion | Discretion on clearance margin | |

**User's choice:** Dynamic clearance guard: clamp R_effective so the fillet apex maintains a guaranteed minimum clearance (e.g. at least 4.0px) from any obstacle boundary, in addition to the segment length budget.

| Option | Description | Selected |
|--------|-------------|----------|
| Analytical vector math | O(1) per corner in pure Python standard library | ✓ |
| Claude's discretion | Discretion on performance optimization | |

**User's choice:** Analytical vector math O(1) per corner in pure Python standard library — compute corner geometry in sub-millisecond time without complex iterative solvers.

| Option | Description | Selected |
|--------|-------------|----------|
| Native SVG path compatibility | Emit standard `<path d="M... Q..." class="edge">` elements | ✓ |
| Claude's discretion | Discretion on interactive path formatting | |

**User's choice:** Native SVG path compatibility — emit standard `<path d="M... Q..." class="edge">` elements, ensuring transparent compatibility with interactive pan/zoom, search/highlight, and viewport minimap with zero JS modifications.

---

## Claude's Discretion

- Internal helper structure in `renderer_svg.py` vs `router.py`.
- Exact numerical tolerance for orthogonality detection (`1e-6`).

## Deferred Ideas

None — discussion stayed within phase scope.
