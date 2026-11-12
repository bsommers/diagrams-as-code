# Phase 9: Rounded Corner Fillets for Orthogonal Routing - Context

**Gathered:** 2026-09-26  
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 9 delivers rounded corner filleting on Manhattan orthogonal routing paths (`Routing.ORTHOGONAL`). It introduces a foundational quadratic Bezier primitive in Layer 0 (`geometry.QuadraticBezier`), dynamic per-corner radius clamping ($\min(R, L_{\text{in}}/2, L_{\text{out}}/2)$) and threshold suppression ($< 2.0\text{px}$) to prevent "dog ears" and overlapping arcs in Layer 3 (`router.py`), and native SVG path generation emitting quadratic Bezier (`Q`) commands with $C^1$ tangent continuity in Layer 4 (`renderer_svg.py`).

</domain>

<decisions>
## Implementation Decisions

### API Parameter & Default Behavior
- **D-01:** Support `corner_radius` as the primary attribute on `Edge` and `Diagram`, with `arc_radius` accepted as a fully-supported alias. `Diagram(corner_radius=...)` cascades as default for all orthogonal edges in the diagram; individual `Edge(corner_radius=...)` overrides the diagram default.
- **D-02:** Sharp corners by default (`corner_radius=0.0` or `None`), preserving 100% backward compatibility and zero visual diff across all 88 gallery diagrams and existing tests unless explicitly configured.
- **D-03:** `corner_radius` applies strictly to `Routing.ORTHOGONAL` edges. If configured on `Routing.DIRECT` or `Routing.CURVE`, it is gracefully ignored without raising an error.
- **D-04:** Input validation: Coerce int/float inputs to `float`. Raise `ValueError` if `corner_radius < 0.0` or non-numeric (strict defensive validation).

### Fillet Radius Clamping & Short Segments
- **D-05:** Strict 50% segment budget: For each corner $P_i$, $R_{\text{effective}} = \min(R, L_{\text{in}} / 2.0, L_{\text{out}} / 2.0)$ where $L_{\text{in}} = \|P_i - P_{i-1}\|$ and $L_{\text{out}} = \|P_{i+1} - P_i\|$. Adjacent corners on a shared segment each receive up to 50% of the segment length, preventing inverted arcs or overlaps.
- **D-06:** Minimum threshold suppression: If $R_{\text{effective}} < 2.0\text{px}$, suppress the fillet for that specific corner and render a sharp 90-degree corner, preventing sub-pixel rasterization artifacts and micro-arcs.
- **D-07:** Orthogonal turn detection: Fillet is applied strictly to 90-degree orthogonal turns where $\mathbf{u}_{\text{in}} \cdot \mathbf{u}_{\text{out}} = 0$ (within numerical tolerance $10^{-6}$). Collinear segments continue straight, and turnarounds remain linear.
- **D-08:** Endpoint straight lead-in: Segments adjacent to source and target ports enforce a minimum straight lead-in of at least $10.0\text{px}$ (or $L / 2$ if shorter), ensuring edges depart and arrive strictly perpendicular to node bounds and arrowheads rest on clean linear segments without curvature distortion.

### SVG Path Generation & Mathematical Contract
- **D-09:** SVG path syntax: Emit quadratic Bezier commands `L T1.x T1.y Q P_c.x P_c.y, T2.x T2.y` where $P_c$ is the corner control point, and $T_1, T_2$ are tangent points on the incoming and outgoing segments, directly fulfilling requirement FILLET-03 with $C^1$ continuity.
- **D-10:** Layer 0 primitive: Implement `geometry.QuadraticBezier(p0, p1, p2)` in `src/diagrams_as_code/geometry.py` as an immutable frozen dataclass with `point_at(t)`, `tangent_at(t)`, `bbox()`, and `arc_length()`, exported in `diagrams_as_code` and facade `iiot_diagrams`.
- **D-11:** Waypoint data contract: `Edge.waypoints` remains the clean sequence of sharp Manhattan corner vertices `[P_0, P_1, ..., P_n]`. Fillet tangent point calculation and `Q` command generation is performed in Layer 4 during SVG path generation, preserving layout JSON serialization, collision tests, and backward compatibility.
- **D-12:** Protocol badge placement: Keep existing orthogonal badge positioning on the midpoint of the longest straight segment, ensuring badges remain horizontal, highly readable, and on flat straight line segments rather than straddling corner bends.

### Obstacle Avoidance & Clearance Integration
- **D-13:** Uniform filleting: Apply corner filleting uniformly across both default Manhattan paths and obstacle-avoidance detour paths for consistent visual style across all orthogonal edges.
- **D-14:** Obstacle clearance guard: When rounding corners near obstacles, clamp $R_{\text{effective}}$ such that the fillet apex preserves a minimum clearance margin of at least $4.0\text{px}$ from any obstacle bounding box, preventing curved paths from clipping obstacle corners.
- **D-15:** Performance optimization: Analytical vector calculations $O(1)$ per corner in pure Python standard library (`math.hypot`, closed-form quadratic tangent placement), executing in sub-millisecond time per edge with zero iterative root finders.
- **D-16:** Interactive SVG compatibility: Filleted paths emit standard `<path d="M... Q..." class="edge">` elements, providing transparent, zero-code compatibility with existing interactive pan/zoom, search/highlighting, and viewport minimap navigation.

### Claude's Discretion
- Internal helper structure in `renderer_svg.py` (e.g. `_render_filleted_path` helper function) vs `router.py`.
- Exact numerical tolerance for orthogonality detection (`1e-6`).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Roadmap & Requirements
- `.planning/ROADMAP.md` — Phase 9 goals, requirements `FILLET-01` through `FILLET-03`, and success criteria.
- `.planning/REQUIREMENTS.md` — Full requirement statements for `FILLET-01`, `FILLET-02`, and `FILLET-03`.

### Milestone Research
- `.planning/research/SUMMARY.md` — Synthesized mathematical formulation, stack choices, and phase sequencing.
- `.planning/research/ARCHITECTURE.md` — Decoupled 5-layer system structure, waypoint contract, and component map.
- `.planning/research/PITFALLS.md` — Mitigations for "dog ear" corner loops, sub-pixel micro-arcs, and obstacle clipping.
- `.planning/research/STACK.md` — Pure Python standard library math primitives (`math.hypot`, vector operators).

### Layer 0 & Routing References
- `src/diagrams_as_code/geometry.py` — `Point`, `Rect`, `CubicBezier` patterns to mirror in `QuadraticBezier`.
- `src/diagrams_as_code/router.py` — `OrthogonalRouter`, `_simplify_collinear`, `_find_detour_path`.
- `src/diagrams_as_code/renderer_svg.py` — `SVGRenderer._render_edges`, marker orientation, and badge centering.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Point` vector arithmetic (`+`, `-`, `*`, `/`, `distance_to`) in `geometry.py`: directly calculates tangent points $T_1 = P_c - \mathbf{u}_1 \cdot R$ and $T_2 = P_c + \mathbf{u}_2 \cdot R$.
- `OrthogonalRouter` in `router.py`: generates clean Manhattan waypoints `[P_0, ..., P_n]` which feed directly into fillet tangent evaluation.
- `ShapeLibrary` & `SVGRenderer` in `renderer_svg.py`: handles marker placement, drop shadows, and SVG path assembly.

### Established Patterns
- Pure Python standard library with zero runtime dependencies.
- Strict layered architecture: Layer 0 (`geometry.py`) has 0 internal imports.
- Dual-package export parity: `diagrams_as_code` and `iiot_diagrams` facade re-export identical public symbols.

### Integration Points
- `src/diagrams_as_code/geometry.py`: Add `QuadraticBezier` dataclass.
- `src/diagrams_as_code/connections.py`: Add `corner_radius: Optional[float] = None` and `arc_radius` property to `Edge`.
- `src/diagrams_as_code/diagram.py`: Add `corner_radius: Optional[float] = None` to `Diagram` and propagate to edges.
- `src/diagrams_as_code/renderer_svg.py`: Implement fillet tangent point decomposition and `Q` command generation in `_render_edges`.

</code_context>

<specifics>
## Specific Ideas

- Quadratic Bezier control point is the sharp corner vertex $P_c$ itself: this guarantees exact tangency at both $T_1$ and $T_2$ without solving systems of equations.
- Minimum lead-in at port anchors prevents arrowheads from rotating or curving as they touch node bounding boxes.

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.

</deferred>

---

*Phase: 09-rounded-corner-fillets-for-orthogonal-routing*  
*Context gathered: 2026-09-26*  
