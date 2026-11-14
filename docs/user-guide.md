# User Guide

[← Back to Documentation Hub](README.md) · [Project README](../README.md)

A task-oriented guide to writing diagrams as Python code and rendering them to SVG, PNG and Markdown/JSON Bill-of-Materials (BOM) files. For paper-style figures see [technical-figures.md](technical-figures.md) and the [math markup reference](math-markup.md); for deeper recipes see [how-to.md](how-to.md); for installation details see [running.md](running.md); for internals see [architecture.md](architecture.md).

## Table of Contents
- [Concepts](#concepts)
- [Install and first diagram](#install-and-first-diagram)
- [Building blocks](#building-blocks)
- [Positioning: manual, relative, auto](#positioning-manual-relative-auto)
- [Edges and routing](#edges-and-routing)
- [Text, markup and math](#text-markup-and-math)
- [Technical drawing primitives](#technical-drawing-primitives)
- [Themes](#themes)
- [Icons](#icons)
- [Outputs and the BOM](#outputs-and-the-bom)
- [Command-line interface](#command-line-interface)
- [Troubleshooting](#troubleshooting)

## Concepts

| Term | Meaning |
|---|---|
| **Diagram** | The canvas and container. Created with `with Diagram("Title", ...) as diag:`. |
| **Shape** | A node: box, cylinder, or standalone icon, with a label. |
| **Group** | A named container (for example a tier or a zone) that holds shapes and nests. |
| **Edge** | A labelled connection between two shapes, written `a >> diag.edge("label") >> b`. |
| **Constraint** | A placement rule such as `right_of`, `below`, `above`, `left_of`, `align_with`, or an absolute `at(x, y)`. |
| **Theme** | A named colour palette. |
| **BOM** | A generated Markdown table and JSON file describing the components in a diagram. |

The core engine uses only the Python standard library. It needs no Graphviz, Cairo or ImageMagick to produce SVG.

## Install and first diagram

This project uses [`uv`](https://docs.astral.sh/uv/) for everything.

```bash
git clone https://github.com/bsommers/diagrams-as-code
cd diagrams-as-code
uv sync
uv run python main.py        # renders the reference architecture into output/
```

Your own script:

```python
from diagrams_as_code import Diagram

with Diagram("Order Pipeline", theme="nord", layout="auto", direction="LR") as diag:
    with diag.group("Ingress"):
        client = diag.shape("Client", icon="mobile")
        gw = diag.shape("API Gateway", icon="api_gateway")
    with diag.group("Compute"):
        worker = diag.shape("Worker", icon="server")

    client >> diag.edge("HTTPS") >> gw
    gw >> diag.edge("invoke") >> worker

diag.render_svg("order_pipeline.svg")
```

Call the `render_*` methods **after** the `with` block so the layout has been solved.

To use the CLI, define a function named `diagram()` that returns the `Diagram`, then run `uv run diagrams-as-code render my_script.py`.

## Building blocks

**Diagram options** (constructor): `title`, `width`, `height`, `theme`, `theme_overrides`, `label_position` (`"inside"` or `"bottom"`), `layout` (`"manual"` or `"auto"`), `direction` (`"LR"` or `"TB"`), `layout_file`, `rank_gap`.

**Shapes**: `diag.shape(label, width=130, height=60, kind="box", icon=None, id=None, metadata=None)`. Use `kind="cylinder"` for databases and `kind="icon"` for a borderless icon with a label. `Shape(id, label, icon=..., kind=...)` can also be created directly and added with `diag.add(...)`.

**Groups**: `with diag.group("Name") as g:` collects everything created inside the block. Groups size themselves to their children and can nest.

**Edge options**: `label`, `color`, `style`, `source_port`, `target_port`, `arrow_head`, `arrow_tail`, `routing`, `corner_radius`, `arc_radius`, `clearance`, `metadata`.

## Positioning: manual, relative, auto

**Relative (manual mode)**: anchor things to each other.

```python
alb.below(client, margin=25)
g_app.right_of(g_public, margin=90)
g_db.at(60.0, 80.0)
```

**Auto layout**: set `layout="auto"`. The layered engine ranks shapes and groups from the edge structure, so the same script always produces the same layout. Anything you pin with `.at()` or anchor with `.right_of()` and friends stays where you put it; only unconstrained elements are auto-placed.

**Layout files**: export the resolved positions, hand-edit them, and feed them back:

```bash
uv run diagrams-as-code layout export my_script.py        # writes my_script.layout.json
uv run diagrams-as-code render my_script.py --layout-file my_script.layout.json
```

See [Recipe 7 in how-to.md](how-to.md#recipe-7-let-the-engine-lay-out-a-diagram).

## Edges and routing

By default edges are routed orthogonally (Manhattan style). Pass `routing="curve"` for cubic Bézier curves that deflect around obstacles (see `Routing.CURVE`). Set `corner_radius` on a diagram or an edge to round orthogonal corners. Declare shapes before edges so routing can avoid them; use `clearance=` to widen the buffer around obstacles.

Recipes: [curved routing](how-to.md#recipe-8-routing-curved-bezier-edges-with-obstacle-deflection), [corner fillets](how-to.md#recipe-9-smoothing-orthogonal-edges-with-rounded-corner-fillets).

## Text, markup and math

Every label (shape, group title, edge badge) accepts a small markup:

| Write | Get |
|---|---|
| `**bold**` | bold |
| `*italic*` | italic |
| `\n` or a real newline | line break |
| `$E_{t+1} \in \Omega_{\mathrm{safe}}$` | typeset math |
| `\$`, `\*` | a literal `$` or `*` |

Ordinary labels need no escaping: `"Under $50k"`, `"2 * 3"` and `snake_case_names` are left alone, because math needs a closing `$` and emphasis needs a closing marker.

```python
d.add(Shape(
    "policy",
    "**Policy Decision Function**\n"
    r"$\Pi(E_t, E_{t+1}) \to \{\mathrm{allow}, \mathrm{deny}\}$",
    width=260, height=70,
))
d.connect(a, b, label=r"$g_k(I, C, D, T) \leq 0$")
```

**Math** is a TeX-like subset: letters are set in math italic and digits upright; `_` and `^` take one character or a `{group}`; Greek letters (`\alpha` … `\Omega`); relations and operators (`\leq \geq \neq \approx \in \subseteq \to \leadsto \land \lor \cap \cup \times \cdot \forall \exists` and more); `\mathrm{}`, `\text{}`, `\mathbf{}`; named functions (`\min`, `\max`, `\log` …); big operators with limits underneath (`\sum_{i=1}^{n}`, `\bigcap_{k}`; add `\nolimits` to set them beside); and the spaces `\,` `\;` `\quad`. Fractions, radicals, accents and matrices are not supported and raise `MathError` rather than rendering wrongly. Every supported command is listed in the [math markup reference](math-markup.md).

Math is drawn as vector outlines, so it looks identical in every browser, in PNG and in print. Ordinary text stays real, selectable SVG text.

**Fitting.** Label width is measured from bundled font metrics, not guessed. A label that cannot fit its shape at the smallest size makes the shape grow, so text never spills out. To keep a size exactly as given, pass `fit_label=False` on the shape or `Diagram(fit_labels=False)`. To pin the text size, pass `font_size=14` on the shape.

**Canvas size.** Leave `width` and `height` off and the canvas is fitted to the content with an even margin. Pass either one to fix that axis; it still grows if content would otherwise be clipped.

**Shape artwork.** An inside label stays clear of the shape's own drawing: below the rim of a cylinder or database, between the lobes of a cloud, inside the diamond. Racks and databases draw a plain plate behind the label. A shape grows if that leaves too little room.

**Edge labels.** A badge is moved along its edge to a spot clear of nodes, group titles, other badges and other edges. A label too wide for the gap is wrapped; if nothing on the line is clear it sits just beside the line. Edges that carry the same label along a shared trunk draw one badge.

**Coordinates.** SVG coordinates are written to two decimals (`Diagram(precision=2)`). `Diagram(pixel_snap=True)` rounds every position to a whole pixel and draws 1 px strokes on pixel centres, so hairlines in the `paper` theme are exactly one pixel wide.

To measure or lay out text yourself:

```python
from diagrams_as_code.text import TextStyle, layout, measure

width, height = measure("Edge Gateway", TextStyle(size=13))
block = layout(r"State $E_{t+1}$", TextStyle(size=16), max_width=200)
svg_fragment = block.to_svg(x=100, y=50, anchor="middle", fill="#111")
```

## Technical drawing primitives

For figures in papers and specifications. Each has a focused example in [`examples/primitives/`](../examples/primitives/); the `paper` theme suits them.

**Text, captions, brackets.** `d.text("**Note:** $x_i \\le 1$", size=12, max_width=200)` is text with no box; it takes the same markup as labels and is placed like a shape. `font="serif"` and `italic=True` set remarks. `d.caption("**Figure 1:** ...", small_caps=True)` is centred under the drawing unless you position it. `d.bracket("three states", side="right").spanning(first, last)` draws a brace beside the elements it is given; `shape=` is `curly`, `square` or `round`.

**Outlines.** `d.polygon([(0, 0), (60, 0), (30, 50)], "A")`, `d.polyline(points)` and `d.path("M 0 40 A 60 60 0 0 1 100 40 Z")` draw free shapes. They are drawn where their coordinates say until you place them with `.at()` or `.right_of()`; style them with `Style(fill=, stroke_width=, dash=, fill_opacity=)`.

**Bands.** `with d.band("Runtime layer", notes=["Checked on every call."], min_width=640):` is a group drawn as a dashed frame with a bold title and a column of italic side notes. Give stacked bands the same `min_width`.

**Nesting and double borders.** `inner = d.shape("L1", 80, 34).inside(core, "bottom_center", 0, -14)` puts a shape inside another, pinned by the named anchor plus an offset; it moves with its container. Give the container `label_position="top"` so its label becomes a heading. `Style(double=4)` draws a second border 4 px inside the first.

**Line weights and arrowheads.** `d.edge(width=3)` sets the stroke; `head=` and `tail=` choose `triangle`, `stealth`, `open`, `diamond`, `circle`, `bar` or `none`; `arrow_size=2` doubles the head; `two_way=True` puts a head on both ends; `ellipsis=True` replaces the middle of the line with three dots.

**Where a line attaches.** `box.anchor("left", 0.25)` is the point a quarter of the way down the left side (fractions run top to bottom and left to right) and can be either end of an edge: `source >> mux.anchor("left", 0.25)`. A bare point is an end too: `d.connect((60, 300), box, routing="direct")`; `d.point(x, y, dot=True)` is a junction dot several edges can meet at. `d.fan_out(source, targets, trunk=40)` runs the edges along one trunk for 40 px and then splits them; `d.fan_in()` is the mirror. `d.connect(a, b, routing="spline", via=[(180, 20), (420, 30)])` draws a smooth curve through the given points; with any other routing `via` gives straight runs. `d.leader("note text", box.anchor("bottom", 0.75), at=(150, 330), head="circle")` is a note with a thin line to what it describes.

**Solids.** `d.cuboid("label", 120, 80, 90)` draws a box in oblique projection with the edges behind it dashed. `d.solid(Solid.hull(points), projection=isometric(), style=Style(fill="#DCE6F2", fill_opacity=0.55))` draws any convex solid; `Solid.box`, `.prism` and `.pyramid` build common ones. `cut=((0, 15, 0), (0, 1, 0)), cut_size=95` draws a cutting plane through a point with a normal, and outlines the section. Model axes: x right, y up, z away from the viewer.

**Paint order.** Shapes are painted in the order declared; `z=` overrides it. A shape with `z` below zero, or one that contains other shapes, goes under the edges, and an edge with `z` above zero goes over the nodes. `obstacle=False` lets edges cross a shape instead of going round it, as for a backdrop.

**Arranging and units.** `distribute([a, b, c], "right", gap=30, align="bottom")` chains elements with equal gaps and `align([a, b], "left")` lines edges up; position the first element yourself. `Diagram(grid=10)` snaps every corner to a 10 px grid. Sizes and positions accept units: `d.shape("A", "30mm", "12mm").at("15mm", "15mm")`, `size="9pt"`; `mm()`, `pt()` and `to_px()` convert numbers.

Annotations are not components, so none of these appear in the BOM.

For putting these together into a whole figure, and for checking it with `lint` and golden images, see [Technical figures](technical-figures.md) and the eleven figures in [`examples/technical/`](../examples/technical/).

## Themes

Fourteen built-in themes:

- Dark: `iiot_dark_gold` (default), `blueprint`, `cyber_slate`, `nord`, `emerald`, `crimson`, `dracula`, `synthwave`
- Light: `iiot_light`, `monochrome`, `solarized_light`, `pastel_light`, `paper`
- Accessibility: `high_contrast`

`paper` is for figures in papers: black on white, 1 px strokes, square corners, dashed group frames, no shadows.

A theme also sets line weights, corner radii, the group dash pattern and whether nodes cast a shadow (`node_stroke_width`, `node_radius`, `group_stroke_width`, `group_radius`, `group_dash`, `edge_width`, `shadow`). To restyle part of a diagram, pass a `Style`: `d.group("Layer", child_style=Style(fill="#EEEEEE"))` styles every node in the group, `d.group(..., style=Style(dash=""))` styles the group's own frame, and `d.shape("A", style=Style(stroke_width=2))` styles one node. Order of precedence: theme, enclosing groups (outermost first), the element's `style`, then legacy keyword overrides such as `fill=`.

Select with `Diagram(..., theme="nord")`, override single colours with `theme_overrides={...}`, or derive and register your own with `create_theme` / `register_theme`. List them with `uv run diagrams-as-code themes`. See [Recipe 2](how-to.md#recipe-2-switching-themes--creating-custom-brand-palettes).

## Icons

Sixty built-in 24×24 vector icons across eight domains: `ai`, `business_process`, `cloud`, `computer`, `cybersecurity`, `datacenter`, `iiot`, `network_engineering`.

```bash
uv run diagrams-as-code icons                    # all icons: name, domain, description
uv run diagrams-as-code icons --domain cloud     # one domain
```

Canonical names and aliases live in [`icons/icons.yaml`](../icons/icons.yaml). Provenance and licences are in [sources.md](sources.md). Custom SVG icons can be loaded with `ShapeLibrary.load_icon_file(...)`.

## Outputs and the BOM

| Call | Produces |
|---|---|
| `diag.render_svg(path)` | SVG (add `interactive` options for pan/zoom, search and minimap; see [Recipe 10](how-to.md#recipe-10-generating-interactive-svgs-with-pan-zoom-search-and-minimap)) |
| `diag.render_png(path)` | PNG raster |
| `diag.generate_readme(svg_path, readme_path)` | Markdown component tables |
| `diag.generate_bom_json(path)` | Machine-readable JSON BOM |

The BOM is built from shape and edge `metadata`, so documentation stays in step with the diagram. See [Recipe 5](how-to.md#recipe-5-living-documentation--bom-generation).

## Command-line interface

```text
diagrams-as-code render PATH... [--out DIR] [--format svg,png,bom] [--theme T]
                 [--interactive | --no-interactive] [--layout manual|auto]
                 [--direction LR|TB] [--layout-file FILE] [--debug]
diagrams-as-code lint PATH... [--ignore KIND[,KIND]] [--quiet] [--layout ...] [--direction ...] [--layout-file ...] [--debug]
diagrams-as-code layout export SCRIPT [-o FILE] [--layout ...] [--direction ...] [--layout-file ...] [--debug]
diagrams-as-code themes
diagrams-as-code icons [--domain DOMAIN]
```

- `--format` defaults to `svg,bom`; PNG is opt-in because its bytes vary by backend.
- `render` accepts scripts or directories; directories are scanned recursively for files defining `diagram()`.
- `lint` lays each diagram out and reports visual defects (a line through a node, overlapping labels, text that does not fit), one per line as `script: kind: detail`. It exits `1` if anything is found. See [Technical figures](technical-figures.md#7-check-the-figure) for the kinds.
- Also runnable as `uv run python -m diagrams_as_code ...`.
- Exit codes: `0` success, `1` one or more scripts failed (the rest still run), `2` usage error.

Full reference: [running.md](running.md#34-the-diagrams-as-code-command).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Shapes stacked at (0, 0) | Render after the `with Diagram(...)` block, not inside it. |
| Labels clip | Use `label_position="bottom"` or shorten the label; multi-line wrapping is automatic. |
| `RuntimeError: Cycle detected` | Two relative constraints depend on each other; remove the loop. |
| Unknown icon name | Check `uv run diagrams-as-code icons` or `icons/icons.yaml`. |
| Curved edge crosses a shape | Declare shapes before edges, or raise `clearance`. |
| Rounded corner looks sharp | The segment is too short to fillet; add spacing. |

The full matrix is in [how-to.md](how-to.md#troubleshooting-matrix).
