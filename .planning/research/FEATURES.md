# Feature Research: Curved & Bezier Edge Routing Engine

**Domain:** Directed Architecture Diagramming / Vector Edge Routing & Spline Geometry  
**Researched:** 2026-09-24  
**Confidence:** HIGH (empirically grounded in Graphviz `dot`, XYFlow/React Flow `getBezierPath`, Draw.io/mxGraph `OrthConnector`, W3C SVG 1.1/2.0 specifications, and existing codebase architecture)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete or visually unpolished.

| Feature | Why Expected | Complexity | Implementation Notes |
|---------|--------------|------------|----------------------|
| **Cubic Bezier Routing (`Routing.CURVE`)** | Standard in modern diagramming (Mermaid, React Flow, Graphviz) for organic, readable flow connections. | MEDIUM | Compute 4 control points $(P_0, P_1, P_2, P_3)$ per curve. Emit SVG path syntax `d="M x0 y0 C cp1_x cp1_y, cp2_x cp2_y, x3 y3"`. |
| **Port Tangent Orientation & Directional Normals** | Curves exiting or entering nodes at arbitrary angles look broken; connections must exit perpendicular to the node boundary. | LOW | Outward unit normals for cardinal ports: `NORTH (0, -1)`, `SOUTH (0, 1)`, `EAST (1, 0)`, `WEST (-1, 0)`. Source handle extends along $+\hat{n}_{src}$; target handle extends along $+\hat{n}_{tgt}$ (opposing entry vector). |
| **Smooth S-Curve Handle Distance Heuristics** | Direct curves between adjacent ranks must form smooth sigmoidal transitions without kinks or excessive bulging. | MEDIUM | Handle length $d$: For primary flow axis ($\Delta x$ in LR, $\Delta y$ in TB), calculate $d = \max(0.5 \cdot \|\Delta\|, d_{min})$ with $d_{min} \approx 20\text{px}$. For lateral/backward offsets, scale with $k \cdot \sqrt{\|\Delta\|}$ to avoid exaggerated loops. |
| **Rounded Corner Fillets for `Routing.ORTHOGONAL`** | Sharp 90° corners look dated and harsh; modern tools (Draw.io, Lucidchart) use circular or quadratic fillets. | MEDIUM | At corner $P_i$ between orthogonal segments $P_{i-1} \to P_i$ and $P_i \to P_{i+1}$, clamp effective radius $r_{eff} = \min(r, \frac{1}{2}\|P_i - P_{i-1}\|, \frac{1}{2}\|P_{i+1} - P_i\|)$. Emit SVG elliptical arc `A r_eff r_eff 0 0 sweep E.x E.y` (or quadratic Bezier `Q P_i.x P_i.y E.x E.y`). |
| **Diagram Default + Per-Edge Routing Override** | Users need to set a global diagram style (e.g. all curves or all rounded orthogonal) while overriding specific links. | LOW | Add `routing: Union[Routing, str] = Routing.ORTHOGONAL` and `corner_radius: float = 0.0` to `Diagram.__init__`. Allow `Edge.routing` and `Edge.corner_radius` to default to `None` and inherit from active `Diagram`. |
| **Protocol Label Badge Placement on Curves** | Protocol labels and metadata badges must stay centered on curved edges without being bisected by the stroke. | LOW | Evaluate cubic Bezier polynomial at $t = 0.5$: $B(0.5) = \frac{1}{8} P_0 + \frac{3}{8} P_1 + \frac{3}{8} P_2 + \frac{1}{8} P_3$. Center the badge background rectangle and text at $(B_x, B_y)$. |

---

### Differentiators (Competitive Advantage)

Features that set the product apart. Not strictly required for basic curves, but provide major visual and architectural advantages.

| Feature | Value Proposition | Complexity | Implementation Notes |
|---------|-------------------|------------|----------------------|
| **Obstacle-Deflected Bezier Splines** | Naive diagrammers (Mermaid, React Flow) draw curved lines that slice directly through intermediate nodes. Obstacle deflection preserves curved aesthetics without visual collision. | HIGH | 1. Fast rejection: test if obstacle bounds intersect Bezier control polygon bounding box.<br>2. Precision check: discretize curve into $N$ segments and test `segment_intersects_rect`.<br>3. Deflection: if collision detected, retrieve detour waypoints from existing A* channel search (`_find_detour_path`) and fit a smooth piecewise cubic Bezier spline or filleted path around obstacles. |
| **Adaptive Tangent Scaling for Back-Edges & Loops** | Backward edges (e.g. feedback loops, retry cycles where target rank $\le$ source rank) often generate self-intersecting loops or pierce source shapes in standard cubic formulations. | MEDIUM | Detect when target port normal opposes the natural vector toward the target; adaptively project control points laterally into inter-rank corridors or clearance channels. |
| **Mixed Semantic Routing in Single Diagrams** | Allows visual differentiation of connection semantics (e.g. orthogonal lines for synchronous data pipelines, curved Bezier lines for asynchronous event triggers, direct lines for peer pairings). | LOW | Edge routing is evaluated per-edge during the layout pipeline (`layout/pipeline.py`) and rendered according to each edge's individual strategy (`renderer_svg.py`). |

---

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem appealing in GUI tools but cause fundamental problems in code-based diagramming engines.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Manual Control Point Dragging / Canvas Sculpting** | Users from Illustrator/Draw.io want pixel-by-pixel control over curve handles. | Destroys the "Diagrams as Code" philosophy of reproducible, script-driven generation. Hardcoded coordinates break responsiveness when nodes move or labels change. | Expose declarative parameters (`curvature`, `corner_radius`, explicit `source_port`/`target_port`, or intermediate avoidance hints). |
| **Dynamic Physics / Force-Directed Spline Simulation** | Organic spring-embedder layout feels dynamic and interactive. | Highly non-deterministic, causes jitter, slow execution, breaks reproducible SVG snapshots, and introduces massive algorithmic complexity or runtime dependencies. | Deterministic analytical Bezier equations and deterministic A* clearance channel pathfinding. |
| **Arbitrary High-Order Bezier Curves ($N \ge 4$)** | Desired to route a single curve through many arbitrary waypoints. | High-order polynomials suffer from Runge's phenomenon (wild oscillations) and are not supported in SVG (SVG only supports quadratic `Q` and cubic `C`). | Piecewise cubic Bezier splines (composite $C^1$-continuous cubic segments) or rounded orthogonal polylines. |
| **Global NURBS (Non-Uniform Rational B-Splines)** | Industrial CAD standard for smooth curves. | Requires external geometric math libraries (violates zero-dependency stdlib rule) and cannot be natively rendered in SVG without dense line discretization. | Standard cubic Bezier `<path>` elements natively rendered by SVG engines and browsers. |

---

## Feature Dependencies

```
[Diagram / Edge Routing Configuration]
    │
    ├──enables──> [Cubic Bezier Routing (Routing.CURVE)]
    │                 │
    │                 ├──requires──> [Port Tangent & Normal Calculations]
    │                 │
    │                 ├──requires──> [S-Curve Handle Distance Heuristics]
    │                 │
    │                 ├──requires──> [Bezier Protocol Badge Midpoint Evaluator]
    │                 │
    │                 └──enhances──> [Obstacle-Deflected Bezier Splines]
    │                                     └──requires──> [A* Detour Pathfinding (Existing)]
    │
    └──enables──> [Rounded Corner Fillets (Routing.ORTHOGONAL)]
                      │
                      ├──requires──> [Orthogonal Waypoint Path (Existing)]
                      │
                      └──requires──> [Corner Radius Clamping & SVG Arc/Quadratic Generator]
```

### Dependency Notes

- **`Routing.CURVE` requires Port Tangent & Normal Calculations:** A Bezier curve without outward-pointing control handles clips through the boundary of the source and target elements. Port normals provide the necessary geometric vectors.
- **`Routing.CURVE` requires S-Curve Handle Distance Heuristics:** Tangent direction alone is insufficient; handle length dictates whether the curve forms a natural S-curve or an unnatural overshoot.
- **`Routing.CURVE` requires Bezier Protocol Badge Midpoint Evaluator:** Existing protocol badges rely on the midpoint of polyline segments. Curved edges require cubic polynomial evaluation at $t=0.5$ ($B(0.5)$) to center badges properly.
- **Obstacle-Deflected Bezier Splines enhance `Routing.CURVE` and require A\* Detour Pathfinding:** When a direct cubic Bezier intersects an obstacle, it delegates to the obstacle clearance grid to obtain avoidance waypoints, transforming the polyline detour into a smooth spline.
- **Rounded Corner Fillets require Orthogonal Waypoint Path & Radius Clamping:** Filleting operates directly on the output of `OrthogonalRouter.route()`. Radius clamping ensures corners do not invert or overlap on short segments.

---

## MVP Definition

### Launch With (Milestone v0.8.0 Scope)

Minimum viable product for the curved and Bezier routing milestone.

- [x] **`Routing.CURVE` Strategy Enum & Pipeline Wiring** — Support `Routing.CURVE` in `connections.py`, `router.py`, `layout/pipeline.py`, and `renderer_svg.py`.
- [x] **Cardinal Port Tangent & Control Point Calculation** — Analytical computation of $(P_1, P_2)$ for all 16 cardinal port pairings (EAST $\to$ WEST, SOUTH $\to$ NORTH, etc.).
- [x] **Smooth S-Curve Handle Scaling** — Proportional handle lengths based on delta distance and layout flow direction (`LR` vs `TB`).
- [x] **Rounded Corner Fillets for `Routing.ORTHOGONAL`** — Configurable corner radius (`corner_radius: float`) with automatic segment length clamping.
- [x] **SVG `<path>` Generation for Curves & Fillets** — SVG `C` commands for cubic Beziers and `A` (elliptical arc) or `Q` (quadratic) commands for corner fillets.
- [x] **Diagram & Edge Configuration Hierarchy** — Diagram-level defaults (`Diagram(routing=..., corner_radius=...)`) with per-edge overrides (`Edge(..., routing=..., corner_radius=...)`).
- [x] **Cubic Bezier Protocol Badge Centering** — Mathematical midpoint calculation via $B(0.5)$ for edge protocol labels.
- [x] **Obstacle Detection & Deflection for Curved Edges** — Bounding box collision check with fallback to smooth detour corridor routing when direct curves collide with nodes.

### Add After Validation (v0.8.x)

Features to add once core Bezier and fillet routing are validated across the gallery.

- [ ] **Curvature Parameter Tuning (`curvature: float = 0.5`)** — Expose a normalized curvature factor on `Diagram` and `Edge` to allow users to dial curves between flatter and more dramatic arcs.
- [ ] **Continuous Multi-Segment Bezier Smoothing ($C^1$ Spline)** — Fit smooth Catmull-Rom or Bezier control points across arbitrary 3+ waypoint detour sequences.
- [ ] **Edge Crossing Bridge Hops (Jump Arcs)** — Draw small semi-circular bridge arcs where orthogonal or curved edges cross each other to eliminate visual ambiguity.

### Future Consideration (v0.9+)

- [ ] **Edge Bundling for High-Density Meshes** — Group parallel curved edges into shared spline bundles to reduce visual clutter in complex microservice architectures.
- [ ] **Interactive Control Handle Inspection in HUD** — Display debug control handles and tangent vectors when `--interactive` inspector mode is active.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| **Cubic Bezier Routing (`Routing.CURVE`)** | HIGH | MEDIUM | P1 |
| **Port Tangent & Normal Calculations** | HIGH | LOW | P1 |
| **Rounded Corner Fillets for Orthogonal Paths** | HIGH | MEDIUM | P1 |
| **Diagram-Level Default & Edge Override Hierarchy** | HIGH | LOW | P1 |
| **Bezier Protocol Badge Centering ($B(0.5)$)** | HIGH | LOW | P1 |
| **Obstacle Collision Detection for Curves** | HIGH | MEDIUM | P1 |
| **Obstacle Deflection via Smooth Detour Splines** | HIGH | HIGH | P1 |
| **Curvature Tuning Parameter (`curvature`)** | MEDIUM | LOW | P2 |
| **Edge Crossing Jump Arcs (Bridge Hops)** | MEDIUM | MEDIUM | P2 |
| **Edge Bundling for Dense Meshes** | LOW | HIGH | P3 |

**Priority Key:**
- **P1:** Must have for milestone v0.8.0 release.
- **P2:** Fast follow after core stabilization.
- **P3:** Deferred to future architectural milestones.

---

## Competitor Feature Analysis

| Dimension / Feature | Graphviz (`dot`) | Mermaid.js | Draw.io / mxGraph | React Flow / XYFlow | Diagrams-as-Code (Our Approach) |
|---|---|---|---|---|---|
| **Curve Routing Method** | Piecewise cubic Bezier splines (`splines=spline` or `splines=curved`). | D3-shape curves (`curve: basis`, `linear`, `cardinal`, `stepAfter`). | Custom curved connector (`edgeStyle=curved`). | Analytical cubic Bezier (`getBezierPath`). | Analytical cubic Bezier (`Routing.CURVE`) with cardinal port tangent vectors. |
| **Port Tangent Orientation** | Handled by internal layout engine; enters/exits at node boundary. | Enters/exits node edge, but tangents can warp oddly with Dagre layout. | Manual or fixed port directions; user can drag handles. | Strict directional tangents based on `sourcePosition` and `targetPosition`. | Strict directional normals from 9-point cardinal anchors (`Port.to_anchor()`). |
| **Orthogonal Corner Fillets** | `splines=ortho` polylines; limited and buggy corner radius support. | Not supported for orthogonal lines (sharp steps only). | First-class support via `rounded=1` and `arcSize` property. | Supported via `SmoothStepEdge` with `borderRadius`. | First-class `corner_radius` parameter with automatic clamping against segment length. |
| **Obstacle Avoidance on Curves** | Full visibility graph spline router avoids all node boundaries. | **None**; curves cut straight through intervening nodes across ranks. | Simple waypoint heuristic or manual user waypoint adjustment. | **None**; curves pass through intervening nodes. | **Obstacle-aware deflection**: direct curve collision test triggers detour channel spline routing. |
| **Configuration Hierarchy** | Graph-level attributes with per-edge overrides (`[splines=...]`). | Diagram directives (`%%{init: ...}%%`) with limited per-edge classes. | Global diagram defaults with per-shape/edge XML style overrides. | Component props on `<ReactFlow defaultEdgeOptions={...}>` + edge object. | Pythonic hierarchy: `Diagram(routing=..., corner_radius=...)` with per-`Edge` overrides. |
| **External Runtime Dependencies** | Heavy C binary (`libgvc`, `libcgraph`, Graphviz installation). | Node.js / Browser JavaScript runtime. | Electron / Browser JavaScript runtime. | React / JavaScript browser environment. | **Zero dependencies**: Pure Python standard library producing standalone SVG. |

---

## Technical Deep-Dive: Mathematical Formulations

### 1. Cubic Bezier Formulations & Tangents

A cubic Bezier curve is defined by four points: start $P_0$, source control point $P_1$, target control point $P_2$, and end $P_3$:
$$B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3, \quad t \in [0, 1]$$

#### Port Outward Normal Vectors $\hat{n}$:
$$\hat{n}(\text{EAST}) = (+1, 0), \quad \hat{n}(\text{WEST}) = (-1, 0), \quad \hat{n}(\text{SOUTH}) = (0, +1), \quad \hat{n}(\text{NORTH}) = (0, -1)$$

#### Control Point Positioning:
$$P_1 = P_0 + d_{src} \cdot \hat{n}_{src}$$
$$P_2 = P_3 + d_{tgt} \cdot \hat{n}_{tgt}$$

*Note:* $P_2$ is placed in the direction of the target's outward normal $\hat{n}_{tgt}$, which means the tangent entering the target ($P_2 \to P_3$) is directed inward ($-\hat{n}_{tgt}$), creating a clean perpendicular entry into the target port.

#### Handle Distance Heuristic:
For primary flow axis (e.g. horizontal layout with source EAST and target WEST where $\Delta x = x_3 - x_0$):
- If $\Delta x > 0$ (forward flow):
  $$d_{src} = d_{tgt} = \max\left(\frac{\Delta x}{2}, 20.0\right)$$
- If $\Delta x \le 0$ (reverse flow / back-edge) or non-aligned ports:
  $$d_{src} = \max\left(25.0 \cdot \sqrt{|\Delta x|}, 30.0\right)$$
  $$d_{tgt} = \max\left(25.0 \cdot \sqrt{|\Delta y|}, 30.0\right)$$

#### Midpoint Evaluation for Protocol Badges:
At $t = 0.5$:
$$B(0.5) = \frac{1}{8} P_0 + \frac{3}{8} P_1 + \frac{3}{8} P_2 + \frac{1}{8} P_3$$
This provides the exact coordinate $(B_x, B_y)$ where the label badge background and `<text>` element are anchored.

---

### 2. Rounded Corner Fillet Geometry for Orthogonal Paths

Given an orthogonal polyline sequence $P_0, P_1, \dots, P_n$:
For each internal corner $P_i$ ($0 < i < n$):
1. Compute incoming segment vector $\vec{v}_{in} = P_i - P_{i-1}$ and length $L_{in} = \|\vec{v}_{in}\|$.
2. Compute outgoing segment vector $\vec{v}_{out} = P_{i+1} - P_i$ and length $L_{out} = \|\vec{v}_{out}\|$.
3. Clamp fillet radius to avoid inverted corners on short segments:
   $$r_{eff} = \min\left(r, \frac{L_{in}}{2}, \frac{L_{out}}{2}\right)$$
4. Compute fillet start point $S$ and end point $E$:
   $$S = P_i - r_{eff} \cdot \frac{\vec{v}_{in}}{L_{in}}$$
   $$E = P_i + r_{eff} \cdot \frac{\vec{v}_{out}}{L_{out}}$$
5. Determine SVG arc sweep flag via 2D cross product:
   $$z = v_{in.x} \cdot v_{out.y} - v_{in.y} \cdot v_{out.x}$$
   $$\text{sweep} = \begin{cases} 1 & \text{if } z > 0 \text{ (clockwise / right turn in SVG coords)} \\ 0 & \text{if } z < 0 \text{ (counter-clockwise / left turn in SVG coords)} \end{cases}$$
6. Emit SVG path segment:
   $$\text{Line to } S: \quad \texttt{L } S_x \ S_y$$
   $$\text{Arc to } E: \quad \texttt{A } r_{eff} \ r_{eff} \ 0 \ 0 \ \text{sweep} \ E_x \ E_y$$
   *(Alternative using quadratic Bezier: $\texttt{Q } P_{i.x} \ P_{i.y} \ E_x \ E_y$)*

---

### 3. Obstacle Collision Detection & Deflection

1. **Convex Hull Bounding Box Check:**  
   The cubic Bezier curve lies entirely within the bounding box of its 4 control points $\text{AABB}(P_0, P_1, P_2, P_3)$. If an obstacle bounding box does not intersect this AABB, no collision is possible.
2. **Discretized Segment Intersection:**  
   Evaluate $N = 10$ points along the curve at $t_k = \frac{k}{N}$. For each sub-segment $[B(t_k), B(t_{k+1})]$, test intersection against normalized obstacle bounds using `segment_intersects_rect()`.
3. **Detour Spline Synthesis:**  
   If a collision is detected, invoke the existing A* grid channel search (`_find_detour_path()`) to obtain collision-free channel waypoints $[W_0, W_1, \dots, W_m]$. Convert the detour polyline into a smooth obstacle-clearing path using rounded fillets or piecewise cubic Bezier segments.

---

## Sources

- **W3C SVG 1.1 / 2.0 Paths Specification:** Section 8.3.4 (The cubic Bézier curve commands) & Section 8.3.8 (The elliptical arc curve commands).
- **XYFlow / React Flow `bezier-edge.ts`:** Implementation of `getBezierPath`, `getControlWithCurvature`, and `calculateControlOffset` for directional port tangents.
- **Graphviz `dot` Source Architecture:** Gansner, E. R., Koutsofios, E., North, S. C., & Vo, K. P. (1993). *A technique for drawing directed graphs*. IEEE TSE, 19(3), 214-230. Spline routing within obstacle-free constraint polygons.
- **Draw.io (diagrams.net) / mxGraph:** `mxEdgeStyle.OrthConnector` and `mxConnector.paintLine` rounding routines (`arcSize` and rounded orthogonal paths).
- **Existing `diagrams-as-code` Codebase:**
  - `src/diagrams_as_code/connections.py` (`Port`, `Routing`, `Edge`)
  - `src/diagrams_as_code/router.py` (`OrthogonalRouter`, `segment_intersects_rect`, `_find_detour_path`)
  - `src/diagrams_as_code/renderer_svg.py` (`render_edge`, marker defs, protocol badges)
  - `src/diagrams_as_code/diagram.py` (`Diagram`, `_EdgeBuilder`, `connect`)

---
*Feature research for: Directed Architecture Diagramming / Curved & Bezier Edge Routing Engine*  
*Researched: 2026-09-24*
