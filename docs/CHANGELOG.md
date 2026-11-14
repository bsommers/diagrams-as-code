# Consolidated Master Changelog: Diagrams as Code (IIoT Engine)

All notable changes, architectural milestones, and capability updates to the pure-Python Directed Diagrams as Code framework (`diagrams_as_code`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), adhering to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), Standard 44 (*Pre-Commit Changelog & Documentation Synchronization*), and Standard 45 (*Continuous Capability Manifest Synchronization*).

## [Unreleased]

## [v0.12.0] - 2026-11-13

Technical figures, a linter and golden-image regression tests. `uv run diagrams-as-code lint examples` reports no findings across every example.

### Added
- **Eleven technical figures** in `examples/technical/`, rendered to `output/technical/`. `01_composition_enforcement.py` reproduces a reference figure element for element (four layer bands, shaded panels, a cuboid, a clipped polyhedron with trajectories through it, typeset formulas, leaders, a heavy spine, a two-way arrow, a bracket, a serif caption) and corrects its slips: a label used twice, "Taint Tracking Tracker", an unbalanced bracket and an unexplained frame. The other ten: control loop, transformer block, state machine, protocol stack, memory layout, timing diagram, training pipeline with equations, tensor shapes, geometric construction, constraint region.
- **`diagrams-as-code lint PATH...`**: lays each diagram out and prints every visual defect as `script: kind: detail`, naming the elements involved (`edge_through_node: 'Idle' -> 'Closed' crosses 'Connecting'`). Layout warnings are reported too. Exit code 1 if anything is found; `--ignore KIND[,KIND]` drops kinds; `--quiet` prints findings only.
- **`audit_findings(diagram)`** returns the defects as `Finding(kind, detail)`; `audit_diagram()` is now their tally.
- **Golden images** (`tools/golden_images.py`, `tests/test_golden_images.py`, `tests/golden/technical/`). Every technical figure is rendered at 800 px wide and compared with a stored picture; a pixel counts as changed when a channel differs by more than 48, and a picture fails when more than 0.05% of its pixels changed. Rendering uses only the fonts in `tests/fixtures/fonts` (a Latin subset of Arimo, SIL OFL 1.1), so pictures match across machines. The PNG decoder is standard library.
- `docs/technical-figures.md` (how to build, lint and pin a figure) and `docs/math-markup.md` (every supported math command, and what to write for the unsupported ones).

### Fixed
- **`\n` inside math is no longer a line break.** `$\nabla L$`, `$a \neq b$`, `$\nu$` and `\nolimits` were split into two lines at the `\n`. A typed backslash-n still breaks the line outside math.
- **A caption wider than the drawing was clipped on the left.** The canvas is now framed again after the caption is placed.

### Changed
- The audit no longer counts these as defects: a line that ends at a bare point set inside a shape (a leader to a spot on it), a bracket beside shapes nested in a panel overlapping that panel, and free outlines (`path`, `polygon`, `polyline`) overlapping each other or being written on. Free outlines are drawing, and only their bounding boxes are known to the audit.

## [v0.11.0] - 2026-11-13

Technical drawing primitives. Everything here is additive: the 92 existing gallery diagrams render byte-identically except the four whose spacing was changed to clear the last audit defects. `uv run python tools/audit_gallery.py` across 101 diagrams: every count is 0 (v0.10.0 left 4 lines through badges and 1 edge through a group title).

### Added
- **`Text`, `Caption`, `Bracket`** (`Diagram.text()`, `.caption()`, `.bracket()`). Text with no box, sized to its content, taking the label markup and math; `font="serif"` uses the theme's new `serif_family`. A caption is centred under the whole drawing unless positioned. A bracket (curly, square or round) runs along one side of the elements it is given with `.spanning(a, b)` and may carry a label.
- **`Polygon`, `Polyline`, `Path`** (`Diagram.polygon()`, `.polyline()`, `.path()`). Outlines from points or from SVG path data (every path command, arcs included). Drawn where their coordinates say until placed with `at()` or a relative placement.
- **`Band`** (`Diagram.band()`): a layer container with a dashed square frame, a bold title and a column of side notes (`notes=`, `note_side=`, `note_width=`); `min_width`/`min_height` let stacked bands share a size.
- **Nesting and double borders.** `shape.inside(container, anchor, dx, dy)` nests a shape in another; it moves with its container and edges to it may cross the container's outline. `label_position="top"` turns a container's label into a heading. `Style(double=4)` draws a second border inset by that many pixels; `Style(fill_opacity=)` makes a fill translucent.
- **Edge weights and arrowheads.** `Edge(width=, head=, tail=, arrow_size=, two_way=, ellipsis=)`: head styles `triangle`, `stealth`, `open`, `diamond`, `circle`, `bar`, `none`. These are also accepted by `Diagram.edge()` and `Diagram.connect()`. An edge that uses them has its heads drawn as shapes with the tip exactly on the target; edges that do not are drawn as before.
- **Anchors, points, trunks, leaders, splines.** `box.anchor("right", 0.25)` is a point a quarter of the way down a side and can be either end of an edge. A bare `(x, y)` or `Diagram.point(x, y, dot=True)` is an endpoint too. `Diagram.fan_out()` / `.fan_in()` (`Edge(trunk=)`) run several edges along one trunk that then splits. `Diagram.leader(text, target, at=)` is a note with a thin line to what it describes. `Edge(via=[...])` passes through given points, smoothly with `routing="spline"`.
- **Projected solids** (`diagrams_as_code.solids`, `Diagram.solid()`, `.cuboid()`): `Solid.box`, `.prism`, `.pyramid`, `.hull` (convex hull of points), `.section` and `.clipped` for cutting planes; `oblique()` and `isometric()` projections. Hidden edges are dashed, faces may be translucent, and a cutting plane with its section can be drawn through the solid.
- **Z-order.** `z=` on any shape or edge. A shape with `z` below zero, or one that contains other shapes, is painted under the edges; an edge with `z` above zero is painted over the nodes. `obstacle=False` lets edges pass over a shape (a backdrop).
- **Arranging and units.** `align(elements, "top")`, `distribute(elements, "right", gap=40)`, `Diagram(grid=10)` to snap corners to a grid, and lengths as strings with units (`"30mm"`, `"12pt"`, `"1in"`) wherever a size or position is given; `mm()`, `pt()`, `to_px()`.
- `diagrams_as_code.drawing`: backend-neutral `PathItem` / `TextItem`. Every primitive describes itself with these, in absolute `M`/`L`/`C`/`Z` commands, so the PDF writer planned for v0.13.0 needs only lines and cubic curves.
- Nine focused examples in `examples/primitives/`, rendered to `output/primitives/`.

### Changed
- Annotations (text, captions, brackets, outlines, solids, points) are left out of the bill of materials.
- The audit understands the new elements: a shape nested in another is not an overlap, a caption or point is not a node, and a point has no side for a line to arrive along.
- Canvas sizing counts what a self-drawing element really covers (a solid's label underneath it, for example).
- `tests/test_domain_examples.py` now checks only the eight domain galleries; `examples/primitives/` has `tests/test_primitive_examples.py`.

### Fixed
- The last five gallery audit defects. `computer/01`, `datacenter/01` and `network_engineering/09` had groups 80 px apart, narrower than the edge labels between them; the gaps are now wide enough. In `cloud/06` the standby route dropped through the title of the group it entered; it now turns in the gap before the group (`clearance=45` on that edge).

## [v0.10.0] - 2026-11-12

Style model and layout correctness. `uv run python tools/audit_gallery.py` across 92 diagrams, v0.9.0 -> v0.10.0: mostly-empty canvases 90 -> 0, overlapping edges 22 -> 0, badges over nodes 21 -> 0, badges over badges 16 -> 0, lines through badges 183 -> 4, group titles wider than their group 29 -> 0. Still open: 4 lines through badges in 3 diagrams and 1 edge through a group title, all in hand-placed examples whose gaps are narrower than their labels.

### Added
- **`Style`** (`diagrams_as_code.Style`): fill, stroke, stroke width, corner radius, dash, shadow, text colour, font size and opacity for a node or group. Resolved theme -> enclosing groups' `child_style` -> element `style` -> legacy keyword overrides (`fill=`, `stroke=`, ...), which keep working. `Diagram.group(style=, child_style=)`, `Diagram.shape(style=)`.
- **`paper` theme:** black on white, 1 px strokes, square corners, dashed group frames, no shadows. Themes gained `node_stroke_width`, `node_radius`, `group_stroke_width`, `group_radius`, `group_dash`, `edge_width` and `shadow`; the defaults are the previous look. Arrowheads keep a readable size on hairline edges.
- **Group titles fit.** An auto-sized group widens evenly when its title is wider than its contents (`group.fit_title = False` to opt out); edge badges avoid group titles.
- Audit checks `badge_over_title`, `title_overflow` (29 in the gallery before the fix, now 0) and `group_overlap`.

### Changed
- **Fit-to-content canvas (default).** `Diagram(width=None, height=None)`: an axis left unset is sized to the content after layout, with a trailing margin that mirrors the leading one (at most 60 x 80, at least 24). Previously every diagram defaulted to 1200 x 800 and the canvas could only grow, so 89 of 92 gallery diagrams filled a median 23% of their canvas. A size you pass is still honoured as a minimum and still grows if content would be clipped; setting `diagram.width` / `.height` later pins that axis. Edge badges now count as content when sizing.
- **Edge badge placement.** New `layout/badges.py` pass: a badge that would cover a node, another badge or another edge's line slides along its own route to a clear spot; a label too wide for the gap is wrapped onto two or three lines; edges carrying the same label along a shared trunk draw one badge between them. The renderer, the audit and canvas sizing all read the badge box from `labels.edge_badge_rect`. Gallery audit: badge over node 21 -> 0.
- **Lane separation.** New `layout/lanes.py` pass: detours that were routed along the same corridor are shifted onto parallel lanes 14 px apart. An end segment is moved only when no interior one can be, by sliding its port along the node side; arrival directions are untouched.
- **Consistent port spreading.** When a node side carries both incoming and outgoing edges, the order now takes account of the shift already given to each edge's other end, so a request/reply pair is drawn as two straight parallel lines instead of two overlapping Z shapes.
- A badge with no clear spot on its line may sit just beside the line.
- The audit no longer counts a bus as overlapping edges when every source on it feeds every target on it (`connections.may_share_a_line`); a partial bus is still counted. 
- **Labels clear of shape artwork.** `labels.label_area(shape)` gives the part of a shape an inside label and icon may use: below the rim of a cylinder or database, between the lobes of a cloud, the inscribed rectangle of a diamond. Fitting, grow-to-fit, drawing and the audit all use it. Server racks and databases, whose artwork fills the body, draw a plain plate behind the label. Cylinders, clouds and diamonds with long labels or icons may now grow slightly (opt out with `fit_label=False`).
- **Renderer split.** `SVGRenderer.render` now runs four passes (`_defs`, `_groups_pass`, `_edges_pass`, `_nodes_pass`); the pan/zoom/minimap overlay moved to `renderer_interactive.py`. The route fallback for edges drawn without a layout is one helper, and its unreachable branch is gone. Output is byte-identical.
- **Fixed-precision coordinates.** Every coordinate and length in the SVG is written to two decimals (`Diagram(precision=)`), with trailing zeros dropped; text content and names are never touched, and scale factors keep four more places so math glyphs keep their size. `Diagram(pixel_snap=True)` rounds positions to whole pixels and draws odd-width strokes on pixel centres.
- Lane separation now takes any move that shortens the overlap, over three passes, so two crossing Z routes are separated by sliding a port.
- The audit no longer counts a line under a badge that carries that line's own label.
- `flatten` and `segment_enters` moved from `audit` to `geometry` (still importable from `audit`).
- Gallery SVG output regenerated at the fitted sizes; `main.py` and the three root examples no longer hard-code a canvas size.

### Fixed
- `docs/licenses/OFL-STIX.txt` was a byte-identical copy of the packaged licence and failed the repository hygiene test; it is now a symlink.

## [v0.9.0] - 2026-11-12

Text engine: measured text, label markup and typeset math.

### Added
- **`diagrams_as_code.text`:** font-metric text measurement, rich text layout with balanced word wrap, and a TeX-like math typesetter. `layout()`, `measure()`, `TextStyle`, `typeset()`.
- **Label markup** in shape labels, group titles and edge badges: `**bold**`, `*italic*`, explicit line breaks, and `$math$`. Ordinary labels containing `$`, `*` or `_` are unaffected.
- **Math** drawn as vector outlines: sub/superscripts, grouping, Greek, operators and relations, `\mathrm` / `\text` / `\mathbf`, named functions, limits under big operators. Unsupported constructs raise `MathError`.
- **Grow-to-fit:** a shape whose label cannot fit at the smallest size grows so the text never spills. Opt out with `Shape(fit_label=False)` or `Diagram(fit_labels=False)`; pin the text size with `font_size=`.
- `tools/generate_text_data.py` (development-time; uses fontTools via `uv run --with`), `docs/licenses/OFL-STIX.txt`, and a provenance section in `docs/sources.md`.

### Changed
- Node labels, group titles and edge badges are sized and wrapped from real advance widths. The three separate `0.62 x font size` guesses are gone; layout, drawing and the audit share `diagrams_as_code.labels`.
- Wrapped labels are balanced ("Hardware" / "Security Key", not "Hardware Security" / "Key").
- Edge badges are drawn above all edge lines, so no line strikes through a label.
- Gallery SVG output regenerated.

### Licensing
- Math glyph outlines are derived from STIX Two Math 2.13 (SIL Open Font License 1.1) and are redistributed under that license; the license text ships in the package. Advance widths come from Arimo (Apache-2.0). No runtime dependency is added.

### Verification Evidence
- `uv run pytest` -> 654 passed.
- `tools/audit_gallery.py`, v0.8.4 -> v0.9.0: label overflow 29 -> 0, badges over nodes 80 -> 21, badges over badges 28 -> 16, edges through a badge 188 -> 183. Unchanged: overlapping edges 22, mostly-empty canvas 90 (both scheduled for v0.10.0).
- Every formula in the reference figure renders in SVG and PNG (checked by eye).

## [v0.8.4] - 2026-11-12

First release of the Technical Figures program (`docs/plans/2026-11-12-technical-figures-and-quality.md`): a bug-fix baseline and a visual defect gate.

### Fixed
- **Orthogonal routing:** routes leave and arrive perpendicular to their ports and treat the boxes they connect as obstacles, so no edge ends along a node's border or passes back through its own source or target. Automatic port choice uses the free axis when two boxes overlap on the other.
- **Self-loops:** `connect(a, a)` draws a loop outside the node instead of a line across it.
- **Shared sides:** when a node side carries both incoming and outgoing edges, the two sets are moved apart, so `A → B` and `B → A` no longer coincide and their labels no longer stack. Fan-out and fan-in trunks are unchanged.
- **Curved routing:** a spline that still collides after deflection falls back to a rounded orthogonal route. Any edge that cannot be routed clear now raises a `LayoutWarning` instead of failing silently.
- **Stale solves:** shapes, edges and constraints added after the first solve are laid out on the next render; resizing a shape between solves is kept.
- **Style cascade:** edges with manual waypoints inherit diagram-level `corner_radius`; the BOM reports the resolved routing (`Diagram(routing="direct")` was listed as orthogonal).
- **Auto-layout:** spacing accounts for the width of labels drawn below shapes and for edge badges between ranks.
- **Layout files:** non-finite coordinates are rejected.
- **CLI:** a missing `--layout-file` is an error; two scripts that would write the same output no longer overwrite each other silently; scripts can import modules beside them; `sys.exit()` inside one script no longer aborts the batch; `layout export -o <dir>` blames `-o`; an input directory with no diagram scripts is reported.
- **Rasterizer:** an external converter that exits 0 without writing can no longer return a stale PNG.

### Added
- `diagrams_as_code.audit`: counts visual defects in a solved diagram (edges through nodes, tangent arrivals, overlapping edges, badges over nodes or each other, label overflow, clipped or mostly empty canvas).
- `tools/audit_gallery.py` with `--check` / `--update`, and `tools/audit_baseline.json`. The test suite fails if any gallery defect count rises above the baseline.

### Changed
- Gallery SVG output regenerated for the routing fixes.
- Shared text-width estimates moved to `diagrams_as_code.metrics`.

### Verification Evidence
- `uv run pytest` -> 602 passed.
- `uv run python tools/audit_gallery.py` across 92 diagrams, before -> after: tangent arrivals 47 -> 0, edges through own endpoint 1 -> 0, overlapping edges 48 -> 22, edges through a badge 196 -> 188, badges over nodes 95 -> 80, badges over badges 37 -> 28. Label overflow (29) and mostly-empty canvas (90) are unchanged and are scheduled for v0.9.0 and v0.10.0.

## [v0.8.3] - 2026-09-28

### Added
- **Obstacle Detection & Deflection for Curved Edges (`CAP-DIAG-ROUTER-CURVE-OBS`, `CURVEOBS-01` to `CURVEOBS-03`):**
  - Added `CubicBezier.subdivide(t)` (and `split()` alias) using de Casteljau recursion to split cubic curves into two self-contained sub-segments.
  - Implemented analytical two-tier collision detection via `CubicBezier.intersects_rect()` combining bounding box broadphase filtering with recursive De Casteljau curve subdivision (capped at depth $\le 4$).
  - Implemented `Edge.clearance` attribute and property on `Edge` and `Diagram` with strict positive float validation ($\ge 0.0$), defaulting to $15.0\text{px}$.
  - Implemented obstacle normalization and filtering in `CurveRouter._normalize_obstacles`, automatically excluding source and target elements and their nested child nodes.
  - Implemented automatic lateral port resolution (`NORTH`/`SOUTH`) for reverse-flow back-edges in `CurveRouter.resolve_ports()`.
  - Implemented outer lateral clearance escape corridors in `CurveRouter.route()` for reverse-flow edges with explicit ports, ensuring curves navigate safely around node bodies without bow-tie loops.
  - Implemented minimal deviation clearance channel selection (top/bottom and left/right detour corridors) with adaptive 1-2 waypoint synthesis and $C^1$-continuous handle generation ($u_{\text{out}} = -u_{\text{in}}$).
  - Added protocol badge centering on the longest spline segment midpoint in `SVGRenderer._render_edges`.
  - Added end-to-end integration tests in `tests/test_e2e.py` verifying multi-obstacle deflections, mixed curved/orthogonal routing, and nested group avoidance.

### Changed
- **Apache-2.0 License Migration:**
  - Relicensed the repository under the standard Apache License Version 2.0 (Copyright 2026 Bill Sommers).
  - Updated `LICENSE`, `pyproject.toml` (`license = { text = "Apache-2.0" }`), `README.md`, `docs/sources.md`, `icons/README.md`, and `tools/generate_icons.py`.

### Verification Evidence
- `uv run pytest` -> 520 passed in 12.68s across all unit, integration, boundary, and hygiene test suites.
- `uv run python tools/eval_bezier.py` -> 10/10 scenarios passed (100.0% score).
- `uv run python tools/generate_icons.py --check` -> 63/63 vector icons clean and up to date.
- `git diff --exit-code -- output/` -> Zero byte drift across all gallery diagrams.

## [v0.8.2] - 2026-09-26

### Fixed
- **Curves & Fillets Reference Example Headroom (`examples/04_curves_and_fillets.py`):**
  - Shifted node positions down ($y = 220\text{px}$) and expanded canvas height to $680\text{px}$ to prevent top clipping on wide North-to-North cubic Bezier curves ($560\text{px}$ span).
  - Provided $78\text{px}+$ of top margin clearance for the curve apex ($y = 67.4\text{px}$) and `Async Event` protocol badge ($y = 87.8\text{px}$).
  - Re-routed `SQL Sync` connection from `auth` South port to `db` East port to demonstrate explicit $90^\circ$ sharp corner overrides (`corner_radius=0.0`).
  - Added companion vector output `output/curves_and_fillets.svg` and living BOM documentation `output/curves_and_fillets_README.md`.

### Verification Evidence
- `uv run pytest` -> 492 passed in 11.66s across all unit, integration, boundary, and hygiene test suites.
- Automated SVG margin audit -> 93/93 SVGs verified 100% free of clipping with positive margin bounds.
- `uv run python tools/eval_bezier.py` -> 10/10 scenarios passed (100.0% score).

## [v0.8.1] - 2026-09-26

### Added
- **Curves & Fillets Reference Architecture Example (`examples/04_curves_and_fillets.py`):**
  - Added standalone executable example demonstrating rounded corner fillets (`corner_radius=16.0`), cubic Bezier feedback loop with protocol badge (`Routing.CURVE`), and explicit sharp corner overrides (`corner_radius=0.0`).
  - Added automated execution verification test `test_04_curves_and_fillets_execution` in `tests/test_examples.py`.
- **Milestone Onboarding Summary (`.planning/reports/MILESTONE_SUMMARY-v0.8.0.md`):**
  - Generated comprehensive project and architecture overview for Milestone v0.8.0 covering decisions D-01 through D-16 across Phases 8 and 9, requirements coverage, and quickstart guide.

### Verification Evidence
- `uv run pytest` -> 492 passed in 11.95s across all unit, integration, boundary, and hygiene test suites.
- `uv run python tools/eval_bezier.py` -> 10/10 scenarios passed (100.0% score).
- `git diff --exit-code -- output/ icons/` -> Zero byte drift across all gallery diagrams.

## [v0.8.0] - 2026-09-26

### Added
- **Cubic Bezier Edge Routing & SVG Path Generation (`CAP-DIAG-ROUTER-CURVE`, `BEZ-01` to `BEZ-05`):**
  - Added immutable Layer 0 `CubicBezier(p0, p1, p2, p3)` primitive with Bernstein polynomial evaluation, analytical velocity tangents, linear root derivative bounding box (`bbox()`), and physical arc-length integration (`arc_length()`, `arc_length_midpoint()`).
  - Implemented Layer 3 `CurveRouter` computing outward cardinal port normal tangent handles (`PORT_NORMALS`) and distance-proportional handle scaling along flow axes (`LR` and `TB`) to produce smooth S-curves without kinks or excessive handle bulging.
  - Implemented `EdgeRouter` facade dispatching `Routing.CURVE` edges to `CurveRouter` while delegating `Routing.ORTHOGONAL` to `OrthogonalRouter`.
  - Added native SVG `<path d="M... C...">` path command formatting in `SVGRenderer._render_edges` with endpoint arrowhead markers tangentially aligned to curve departure vectors.
  - Added physical arc-length midpoint protocol label badge placement (`edge.label`) with high-contrast background pill stroke masks for asymmetric curves.
  - Added standalone CLI and CI evaluation test runner `tools/eval_bezier.py` validating 10 quality dimensions across a 10-scenario canonical benchmark dataset (`tests/fixtures/eval_bezier_dataset.json`).
- **Rounded Corner Fillets for Orthogonal Routing (`CAP-DIAG-ROUTER-FILLET`, `FILLET-01` to `FILLET-03`):**
  - Added immutable Layer 0 `QuadraticBezier(p0, p1, p2)` primitive with Bernstein evaluation, velocity tangents, exact linear-root bounding box, and chord arc length.
  - Extended `Edge` and `Diagram` with `corner_radius` (primary) and `arc_radius` (alias), strict non-negative float input validation, and diagram-level cascading to `_EdgeBuilder` with per-edge overrides.
  - Implemented Layer 4 `_render_filleted_path` vector engine emitting native SVG `<path d="M... L... Q... L...">` elements connecting corner fillet tangent points for $C^1$-continuous smooth 90-degree corner bends.
  - Implemented dynamic 50% segment budget clamping ($R_{\text{eff}} \le \min(R, L_{\text{in}}/2, L_{\text{out}}/2)$), preventing inverted arcs, overlapping loops, or "dog ear" artifacts on short segments.
  - Implemented straight port lead-in preservation ($\ge \min(10.0, L/2)$) at source and destination ports, ensuring arrowheads and departures seat flush against shape bounds.
  - Implemented 2.0px threshold suppression clamping micro-arcs to clean sharp 90-degree corners to eliminate sub-pixel rasterization artifacts.
  - Implemented analytical obstacle apex clearance guards maintaining $\ge 4.0\text{px}$ clearance from obstacle bounding boxes.
  - Preserved Manhattan waypoint sequences in `Edge.waypoints` for downstream layout and collision simplicity.
  - Maintained longest-segment protocol badge centering on filleted edges.
  - Verified headless W3C SVG rasterization using `resvg-py`.

### Verification Evidence
- `uv run pytest` -> 491 passed in 11.29s across all unit, integration, boundary, and hygiene test suites.
- `uv run python tools/eval_bezier.py` -> 10/10 scenarios passed (100.0% score, PRODUCTION READY).
- `uv run python main.py && git diff --exit-code -- output/ icons/ README.md docs/` -> Zero byte drift across all 88 domain gallery diagrams (100% backward compatibility for sharp default `corner_radius=0.0`).
- `tests/test_module_boundaries.py` -> 27/27 tests passed; 100% compliant with strict downward architectural layering (Layer 0 geometry has 0 internal imports).
- `tests/test_public_api.py` -> 100% export parity between canonical package `diagrams_as_code` and backward-compatible facade `iiot_diagrams`.

## [v0.7.0] - 2026-09-24

### Added
- **Obstacle-Aware Orthogonal Routing (`CAP-DIAG-ROUTER-AVOIDANCE`, `ROUTE-01` to `ROUTE-03`, `ROUTE-05`):**
  - Added `segment_intersects_rect(p1, p2, rect)` detecting orthogonal segment penetrations into obstacle interior bounds with strict boundary clearance.
  - Extended `OrthogonalRouter.route(edge, obstacles=None, clearance=15.0)` to automatically calculate clean Manhattan detour channels around intermediate node obstacles.
  - Implemented minimum-bend orthogonal channel Dijkstra grid search with collinear simplification.
  - Preserved fast-path collision check ensuring 100% byte invariance for obstacle-free routes.
  - Wired diagram elements as obstacles in `layout/pipeline.py`.
- **Multi-Rank Crossing Minimization (`ROUTE-04`):**
  - Extended `LayeredLayout._order()` with Sugiyama virtual dummy vertices across ranks spanning $\ge 2$ layers.
  - Included intermediate edge segments in barycenter sweeps and crossing count evaluations to eliminate avoidable cross-layer line crossings.

### Verification Evidence
- `uv run pytest` -> 453 passed in 11.5s across all unit, integration, boundary, and hygiene test suites.
- `git diff --exit-code -- output/ icons/ README.md` -> Zero byte drift across all domain diagrams.
- `tests/test_module_boundaries.py` -> 100% compliant with strict downward architectural layering.

## [v0.6.0] - 2026-09-23

### Added
- **CLI Interactive Export Flags (`CAP-DIAG-CLI-INTERACTIVE`, `CLI-INTER-01` to `CLI-INTER-04`):**
  - Added `--interactive` and `--no-interactive` flags to `diagrams-as-code render` subcommand in `src/diagrams_as_code/cli.py`.
  - Added tri-state override forwarding to `Diagram.configure(interactive=...)`, preserving script-authored configuration by default.
  - Enabled batch directory rendering with `--interactive` across all discovered diagram scripts.
  - Added unit and subprocess integration tests in `tests/test_cli.py`.
- **Client-Side Search & Node Highlighting (`CAP-DIAG-SEARCH`, `SEARCH-01` to `SEARCH-03`):**
  - Integrated a lightweight search input field into the interactive HUD controls via responsive XHTML `<foreignObject>`.
  - Implemented real-time dynamic substring matching against node IDs and labels, dimming non-matching nodes to 20% opacity and non-incident edges to 15% opacity.
  - Added Escape key and clearing handler to restore original element opacities.
  - Retained strict XML parseability and 100% byte invariance for non-interactive rendering.
- **Viewport Minimap Navigator (`CAP-DIAG-NAVIGATOR`, `MINIMAP-01` to `MINIMAP-03`):**
  - Added a pinned overview minimap thumbnail widget in the bottom-right corner of interactive SVG canvases.
  - Implemented scaled diagram rendering (`<use href="#diagram-content">`) within a clipped viewport.
  - Added a responsive viewport rectangle (`#minimap-viewport`) tracking visible diagram bounds on zoom and pan.
  - Implemented click-and-drag navigation on the minimap to smoothly pan the diagram view across large topologies.

### Verification Evidence
- `uv run pytest` -> 447 passed in 11.5s across all unit, integration, boundary, and hygiene test suites.
- `git diff --exit-code -- output/ icons/ README.md` -> Zero byte drift across all domain diagrams.
- `tests/test_module_boundaries.py` -> 100% compliant with strict downward architectural layering.
## [v0.5.0] - 2026-09-23

### Added
- **Interactive SVG Pan-Zoom and Collapsible Groups (`CAP-DIAG-INTERACTIVE`, `INTER-01` to `INTER-03`):**
  - Added `interactive: bool = False` flag to `Diagram.__init__`, `Diagram.configure()`, and `Diagram.render_svg()`.
  - Added pure client-side SVG interaction with zero external binary or JavaScript dependencies.
  - Implemented responsive mouse-drag canvas panning, cursor-centered scroll wheel zooming, and fixed-viewport HUD controls (`#svg-pan-zoom-controls`) featuring Zoom In, Zoom Out, and Reset buttons.
  - Implemented collapsible hierarchical container groups with interactive click toggles (`▼` / `▶`) on group headers and recursive visibility management across child shapes, nested sub-groups (preserving nested collapse states), and incident edges.
  - Enclosed inline JavaScript within `<![CDATA[ ... ]]>` inside `<script type="text/javascript">` to guarantee strict XML parser and ElementTree compatibility. Default rendering (`interactive=False`) remains 100% byte-identical and zero-script.
- **Typed Constraint Dataclasses (`ARCH-01`):**
  - Introduced typed dataclasses `AbsoluteConstraint`, `RelativeConstraint`, and `AlignConstraint` inheriting from base `Constraint` and `collections.abc.MutableMapping` for seamless dictionary duck-typing.
  - Added `align_with()` multi-axis alignment supporting horizontal/vertical center, left, right, top, and bottom alignment constraints.
- **Group Flow Layout Engine Decoupling (`ARCH-02`):**
  - Created `diagrams_as_code.layout.flow` housing `GroupFlowLayout` protocol and engine classes `VerticalFlowLayout`, `HorizontalFlowLayout`, and `GridLayout`.
  - Decoupled `Group` (Layer 2) from `layout` (Layer 4) via a dynamic layout registry (`register_group_layout`, `get_group_layout_engine`), ensuring strict acyclic module boundaries.
  - Added `Group.flow(engine, **kwargs)` accepting either instantiated layout engines or registered mode names.
- **CI Quota Conservation & Local-First Directives:**
  - Added local-first testing and artifact verification directives to `AGENTS.md` and `.cursor/rules/uv.md`.
  - Added concurrency cancellation (`cancel-in-progress: true`) and path filtering to `.github/workflows/ci.yml`.
  - Symlinked `CLAUDE.md` and `GEMINI.md` to `AGENTS.md` for consistent cross-tool constraint enforcement.

### Fixed
- **CLI Output Collision Validation (`POLISH-01`):** Validated `--out` path collisions against existing regular files before executing diagram scripts, reporting a clear error attributing the collision to `--out`.
- **Graph Builder Descendant Traversal Memoization (`POLISH-02`):** Memoized descendant pin state traversal in `layout/graph.py` to eliminate redundant $O(n \cdot \text{depth})$ subtree walks.
- **Stable Edge Waypoint Keying (`POLISH-03`):** Replaced transient `id(edge)` dictionary keys in `layout/pipeline.py` with direct `Edge.waypoints` attribute storage.
- **Import Ordering & Cleanup (`POLISH-04`):** Cleaned up unused imports in `tests/test_dependency_catalog.py` and alphabetized imports in `diagram.py`.

### Verification Evidence
- `uv run pytest` -> 439 passed in 11.3s across all unit, integration, boundary, and hygiene test suites.
- `git diff --exit-code -- output/ icons/ README.md docs/` -> Zero byte drift across all 88 domain diagrams.
- `tests/test_module_boundaries.py` -> 100% compliant with strict downward architectural layering.

## [v0.4.0] - 2026-09-22

### Added
- **Auto-layout (`Diagram(layout="auto")`):** a deterministic layered engine places unpinned shapes and groups from the edge structure, left-to-right or top-to-bottom. Shapes placed with `.at()` or `.right_of()` stay pinned, relative placement can target auto-placed shapes, and a `LayoutWarning` names any pin that overlaps an auto-placed sibling.
- **Layout file:** `diagrams-as-code layout export` writes every position to a JSON file keyed by label path or explicit `id=`; hand edits are applied as overrides on the next render, and a group entry moves the whole group.
- **`diagrams-as-code` command:** `render`, `layout export`, `themes`, `icons`; also `python -m diagrams_as_code`.
- **8 auto-layout gallery examples** (`examples/<domain>/11_auto_*.py`), bringing the gallery to 88.

### Changed
- Scripts define `diagram() -> Diagram`; files are written by `output.render_all`. Existing `build_diagram()` functions keep working.
- Internals split for modularity: PNG backends in `rasterize.py`, icon glyphs in `icon_glyphs.py`, the active-diagram stack in `context.py`, label metrics in `metrics.py`, and the solve pipeline in `layout/pipeline.py`, which now also routes edges so the renderer only draws. `tests/test_module_boundaries.py` enforces import direction. Rendered output of all existing diagrams was byte-identical through the modularity and layout work; the canvas-growth fix below changed 15 of them (see Fixed).
- `Diagram.render_png()` returns the PNG bytes for every backend (CairoSVG previously returned `None`).

### Fixed
- **Canvas growth is unconditional:** the canvas now grows to fit any content that lands outside it — hand-placed coordinates in `manual` mode included, not just auto-layout or a layout file. 15 of the 92 committed diagrams were clipped this way; their SVG `width`/`height` grew (`1200`→`1290`, `1540`, or `1790`) and no artwork moved.

## [v0.3.0] - 2026-09-21

### Added
- **Canonical Package `diagrams_as_code` (`src/diagrams_as_code/`):** The engine moved from `iiot_diagrams` to `diagrams_as_code`. `src/iiot_diagrams/` remains as a facade that re-exports every public symbol, so existing `import iiot_diagrams` code keeps working.
- **IIoT Domain Gallery (`examples/iiot/`):** IIoT became the eighth example domain, bringing the gallery to 80 diagrams.
- **PNG and BOM Output for Every Example:** Each example script writes an SVG, a PNG, and a Markdown Bill of Materials to `output/<domain>/`.
- **Container Fonts and Compose File:** The Docker image installs `fonts-dejavu-core` so rasterized labels render with a real font, and `docker-compose.yml` defines the `diagram-gen` service with `output/` mounted.
- **Expanded Theme Engine (`src/diagrams_as_code/theme.py`):** Added 5 new built-in themes (`solarized_light`, `pastel_light`, `dracula`, `synthwave`, `high_contrast`), expanding the palette to 13 themes (8 dark, 4 light, 1 accessibility WCAG AAA). Added `list_themes()`, `get_light_themes()`, `get_dark_themes()`, `create_theme()`, and direct `Theme` instance or `theme_overrides` injection in `Diagram.__init__`.
- **Anti-Spill Label Wrapping & Text-Below-Graphic (`src/diagrams_as_code/renderer_svg.py`, `elements.py`):**
  - Implemented multi-line text wrapping via SVG `<tspan>` tags and dynamic font scaling (10px–12px) to permanently prevent labels from spilling outside shape boundaries.
  - Implemented `label_position="bottom"` (or `"below"`) to place labels cleanly underneath compact graphic tiles.
  - Implemented `kind="icon"` for borderless standalone vector icon nodes (like Cisco / AWS architecture schematics).
- **5 Theme Varieties per Domain (80 Diagrams):** Updated all 80 reference architecture scripts across all 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`) to showcase 5 distinct theme varieties per domain, with widened group margins (`margin=90`) to prevent protocol badge line overlap.
- **Complete Documentation Suite (`docs/` & `docs/diagrams/`):**
  - Authoring of `docs/README.md`, `docs/purpose.md`, `docs/architecture.md`, `docs/running.md`, and `docs/how-to.md`.
  - Authoring of `docs/sources.md` and `icons/README.md` cataloging upstream provenance, design systems, and the license of each of the 60 vector icons and every build dependency.
  - Authored multi-format visual architecture diagrams in `docs/diagrams/`: terminal ASCII schematic (`ascii_architecture.txt`), Mermaid flowchart (`architecture.mmd`), Mermaid sequence lifecycle (`execution_lifecycle.mmd`), and native Draw.io XML (`architecture.drawio`).
  - Updated root `README.md` with badges, 8-domain showcase, and documentation hub links.
- **Automated Verification:** Added `test_domain_theme_variety`, `test_text_wrapping_multiline_tspan`, `test_label_position_bottom`, `test_kind_icon_pure_rendering`, and `test_theme_expansion_and_helpers`.

### Changed
- **Generated Icon Catalog (`tools/generate_icons.py`, `src/diagrams_as_code/shapes.py`):** `ShapeLibrary._ICON_CATALOG` is now the single source of truth for icons, mapping each of the 60 canonical names to one domain directory and one description; `_CANONICAL_ICONS` is derived from it. The entire `icons/` tree, `icons/icons.csv`, `icons/icons.yaml`, and `icons/README.md` are emitted from that catalog by `tools/generate_icons.py`, which also provides `--check` for CI. Standalone icon files and the glyphs the renderer draws are now the same artwork by construction.
- **Icon Tree Reconciled (59 → 60 files):** Added the missing `dashboard`, `database`, and `queue` icon files, which the engine rendered but the catalog never shipped. Removed the duplicate `computer/sensor.svg` and `iiot/plc.svg`, so each icon has exactly one domain home.
- **Relative Documentation Links:** Replaced 127 `file:///home/bill/...` absolute links across `README.md`, `docs/`, `examples/README.md`, and `icons/README.md` with repository-relative paths that resolve for every reader and on GitHub.
- **Icon Provenance Corrected (`docs/sources.md`, `icons/README.md`):** The provenance section credited the bundled icons to Lucide, Feather, Tabler, Cisco, CNCF, and AWS with per-glyph derivation claims, and labeled the Cisco and AWS icon programs with two invented license names, neither of which exists (both are conditional brand-asset terms, not open-source licenses). The glyphs are original geometry emitted by `ShapeLibrary._render_icon_content` as SVG primitives on the 24x24 grid — `icons/datacenter/kubernetes.svg` is a circle with eight spokes, not the seven-sided CNCF helm. The table was replaced with an authorship statement (original work, MIT), a "visual conventions, not sources" note, and a vendor-names note pointing at Cisco's and AWS's actual terms pages rather than inventing license names. The retraction is recorded in the document itself.
- **Dependency Catalog Completed (`docs/sources.md`):** The catalog listed only the first of the four PNG backends `Diagram.render_png()` tries. CairoSVG (LGPL-3.0-or-later), Inkscape (GPL-3.0-or-later), and ImageMagick are now listed with their real licenses and with how each is used — imported into the process, or located on `PATH` and run as a subprocess. A new section catalogs what the container image redistributes: the `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` base image, the Debian 12 layer, and `fonts-dejavu-core`. The blanket claim of "permissive" licensing was removed, since two of the backends are copyleft.
- **Dependency Provenance Corrected (`docs/sources.md`):** `resvg-py` is credited to `baseplate-admin/resvg-py` under MIT (verified against the installed distribution metadata) and recategorized from "Dev Dependency" to "Optional Runtime", since `Diagram.render_png()` imports it at runtime.

### Fixed
- **Diagrams Collapsing to the Origin:** Rendering inside the `with Diagram(...)` block ran before layout was solved, and unanchored groups with negative coordinates were clipped, so shapes stacked at `(0, 0)`. `render_svg()`, `render_png()`, and `generate_readme()` now solve any unsolved layout first, the canvas is translated to frame negative bounds, and the examples render after the context manager exits. See `docs/LAYOUT_ROOT_CAUSE.md`.
- **Rendered Output Verified in CI:** The 84 rendered PNGs are no longer tracked (their bytes depend on the rasterizer backend) and are gitignored. The SVGs and BOM Markdown in `output/` stay tracked, and CI fails if the suite's re-render of them differs from the commit.
- **Duplicated Files Removed:** `docker_compose.yml` (a copy of `docker-compose.yml`) was deleted; `RUNNING.md` became a symlink to `docs/running.md`; `docs/ARCHITECTURE.md`, which collided with `docs/architecture.md` on case-insensitive filesystems, was merged into it. `tests/test_repo_hygiene.py` rejects case collisions and byte-identical copies.
- **`main.py` No Longer Overwrites `README.md`:** `generate_root_readme()` rebuilt the repository README from a hardcoded template that had fallen 91 lines behind the maintained file, so every `uv run python main.py` — including the CI "Verify diagram generation" step — silently reverted edits to it. The function and its call were removed; the Bill of Materials continues to be emitted to `output/main_README.md`.
- **CI Guards Generated Artifacts (`.github/workflows/ci.yml`):** A new step runs `tools/generate_icons.py --check` and `git diff --exit-code -- README.md docs/ icons/` after diagram generation, failing the build if a generator rewrites a tracked file or if the committed icon tree drifts from the catalog.
- **Project License Published:** Added the `LICENSE` file (MIT) that `pyproject.toml` declared and `README.md` linked to but which was never committed.
- **Stale Dependency Manifest Removed:** Deleted `requirements.txt`, which listed `diagrams`, `pyyaml`, `gitpython`, and `boto3` — none imported anywhere in the tree — and contradicted `dependencies = []` in `pyproject.toml`. `pyproject.toml` with `uv.lock` is the single source of truth.
- **Documentation Counts and Stroke Claims:** Corrected the icon total from 59 to 60 in `README.md`, `docs/sources.md`, and this changelog. `docs/sources.md` no longer claims uniform round line-caps and line-joins across the set; `icons/README.md` now measures and reports stroke weights from the emitted files.
- **Package Version Synchronized:** `pyproject.toml` and `src/diagrams_as_code/__init__.py` report `0.3.0`, matching this changelog section.

### Verification
- `tests/test_icon_provenance.py` adds 6 tests: no fabricated license name may be asserted outside a quoted retraction, a derivation claim naming an upstream set and a license must ship that license text under `icons/licenses/`, and `docs/sources.md` and the generated `icons/README.md` must agree on authorship.
- `tests/test_dependency_catalog.py` adds 4 tests that read the real `render_png()` fallback chain and the real `Dockerfile`, failing if a rasterizer, a base image, or an `apt`-installed package is absent from `docs/sources.md`.
- `tests/test_icon_catalog.py` adds 76 tests binding the catalog, the generated tree, the manifests, the alias table, and the documented totals together. Drift in any of them fails the suite.

## [v0.2.0] - 2026-09-19

### Added
- Standardized project packaging via `pyproject.toml` with `hatchling` backend and `uv` dependency management.
- Pinned dependency lockfile `uv.lock` for deterministic, reproducible builds.
- Official Astral `uv:python3.12-bookworm-slim` multi-stage `Dockerfile` and container runner `docker-build-n-run.sh`.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) testing matrix across Python 3.10-3.13 with `astral-sh/setup-uv`.
- Universal repository agent guidelines (`AGENTS.md`, `.cursor/rules/uv.md`) enforcing `uv` across all workflows.
- **Domain Vector Icon Catalog (`icons/`):** 51 handcrafted 24x24 open-source W3C SVG icons spanning 7 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`), cataloged in `icons/icons.yaml` and `icons/icons.csv`.
- **Native Shape Library Icon Integration (`src/iiot_diagrams/shapes.py`):** Subsumed all 51 icons natively into `ShapeLibrary` and implemented `register_svg_icon()`, `load_icon_file()`, and `load_icons_from_directory()`.
- **Expanded Color Theme Presets (`src/iiot_diagrams/theme.py`):** Added 4 new presets (`nord`, `emerald`, `crimson`, `monochrome`), expanding the palette to 8 distinct themes.
- **70 Executable Domain Reference Diagrams (`examples/`):** 10 architectural diagrams per domain across 7 domains of varying complexity, generating SVG vector diagrams and Markdown BOM tables in `output/`, cataloged in `examples/README.md`.
- **Domain Examples Test Suite (`tests/test_domain_examples.py`):** Automated parametrized test suite verifying execution, XML structure, and BOM generation across all 70 domain examples.

### Changed
- Migrated all execution, testing, and documentation commands across plans and manifests to `uv run pytest` and `uv sync`.
- **Root Directory Cleanup:** Relocated orphaned exploratory/scratch scripts and chat notes to `legacy/`.

## [v0.1.0] - 2026-09-19

### Added
- **Core Geometry & Coordinate Engine (`src/iiot_diagrams/geometry.py`):**
  - Geometric primitives: `Point`, `Size`, `Rect` with 9 `Anchor` positions (`TOP_LEFT`, `CENTER`, `BOTTOM_RIGHT`, etc.).
  - Bounding box math: `union()` and `expand()` with directional padding.
  - `UnitBasis`: Normalized coordinates (0.0 to 1.0 or percentage strings `'50%'`) mapped to diagram dimensions.
- **Decoupled Elements & Constraint Solver (`src/iiot_diagrams/elements.py`, `src/iiot_diagrams/constraints.py`):**
  - `Element` base class and `Shape` entity model with decoupled lifecycle: can exist unplaced, be placed late, relocated via `.move_to()` or `.translate()`, and cloned via `.clone()`.
  - Directional placement methods: `.right_of()`, `.left_of()`, `.below()`, `.above()` with custom margins and alignments.
  - Topological DAG `ConstraintSolver` resolving dependencies with cycle detection and unconstrained element retention.
- **Hierarchical Grouping & Flow Placement (`src/iiot_diagrams/groups.py`):**
  - Container element `Group` with dynamic bottom-up auto-bounding encapsulating children, headers, and padding.
  - Group-to-group flow placement (`group2.below(group1)`, `group2.right_of(group1)`) propagating child coordinate translations.
  - Internal layout helpers (`vertical_flow`, `horizontal_flow`, `grid`) and cycle prevention in ancestry.
- **Connection Model & Smart Orthogonal Router (`src/iiot_diagrams/connections.py`, `src/iiot_diagrams/router.py`):**
  - `Edge` connection model with `Port` anchors (`NORTH`, `SOUTH`, `EAST`, `WEST`) and `Routing` styles (`ORTHOGONAL`, `DIRECT`, `CURVE`).
  - `OrthogonalRouter` implementing Manhattan waypoint routing, automated port deduction based on relative geometry, and collinear segment simplification.
- **Theming & Vector Shapes (`src/iiot_diagrams/theme.py`, `src/iiot_diagrams/shapes.py`):**
  - Theme presets: `iiot_dark_gold`, `iiot_light`, `blueprint`, `cyber_slate` with registration and reset helpers.
  - Vector shape generators: `render_box`, `render_cylinder`, `render_server_rack`, `render_database`, `render_cloud`, `render_diamond`, `render_badge`.
  - Built-in IIoT vector icons: `sensor`, `gateway`/`edge`, `broker`, `database`/`influx`, `queue`/`kafka`, `cloud`, `dashboard`/`grafana`.
- **Pure-Python Standalone SVG Renderer (`src/iiot_diagrams/renderer_svg.py`):**
  - Zero-binary vector SVG generator with `viewBox`, drop shadows, arrowhead markers, nested group clipping, and contrast-aware protocol badges.
- **Fluent Diagram API & Context Manager (`src/iiot_diagrams/diagram.py`):**
  - Context manager `with Diagram(...) as diag:` supporting operator overloading: `s1 >> s2`, `s1 >> diag.edge(...) >> s2`, fan-in and fan-out lists.
  - Automated group scoping (`with diag.group(...) as g:`) and bottom-up bounds resolution.
- **Bill of Materials (BOM) & Living Documentation (`src/iiot_diagrams/bom.py`):**
  - `BOMGenerator` extracting component inventory, parent groups, and connection metadata into Markdown tables and JSON catalogs.
  - `diag.generate_readme()` synchronizing diagram graphics and BOM tables into root documentation.
- **Runnable Architectural Examples (`examples/`):**
  - `01_mockup_slide.py`: Plant-to-cloud remote monitoring slide with 3 columns, group flow, and MQTT bridge.
  - `02_high_availability.py`: High-availability cluster with load balancer and peer discovery edges.
  - `03_sparkplug_pipeline.py`: Sparkplug B edge pipeline with brokers, message queues, and time-series database.
  - `main.py`: Production entrypoint generating `output/main_architecture.svg` and `README.md`.
- **Comprehensive 10-Suite Test Harness (`tests/`):**
  - 139 tests covering unit, integration, CLI subprocess execution with `tmp_path` isolation, and end-to-end workflows.
  - Strict type checking via `mypy` across 26 source files with 0 errors.

### Changed
- Replaced legacy `mingrammer/diagrams` (Graphviz `dot`) reliance with pure Python geometry and SVG vector rendering.
- Scrubbed all proprietary/vendor branding in favor of generic, customizable Industrial IoT (IIoT) terminology.

### Verification Evidence
- `uv run pytest`: 139 passed in 0.35s.
- `mypy src/ tests/ examples/ main.py`: Success: no issues found in 26 source files.
