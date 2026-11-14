# Technical figures

How to draw a precise, paper-style figure: black on white, typeset formulas, layer bands, nested panels, solids, leader lines and a caption. Eleven worked examples are in [`examples/technical/`](../examples/technical/), rendered to [`output/technical/`](../output/technical/).

| Figure | Script | Shows |
|---|---|---|
| 1 | `01_composition_enforcement.py` | A four-layer architecture with panels, a cuboid, a clipped polyhedron and formulas. A reproduction of a reference figure. |
| 2 | `02_control_loop.py` | A feedback control loop with summing junctions and transfer functions. |
| 3 | `03_transformer_block.py` | A transformer encoder block with residual connections and tensor shapes. |
| 4 | `04_state_machine.py` | A state machine with guards, a self-loop and a double-bordered final state. |
| 5 | `05_protocol_stack.py` | Two protocol stacks and a router, with peer-to-peer and hop-by-hop paths. |
| 6 | `06_memory_layout.py` | A process address space and a zoomed stack frame. |
| 7 | `07_timing_diagram.py` | A digital timing diagram with a bus and setup and hold times. |
| 8 | `08_pipeline_equations.py` | A training pipeline with the equation of each stage. |
| 9 | `09_tensor_shapes.py` | Tensor shapes through a convolutional network, as solids. |
| 10 | `10_geometric_construction.py` | A geometric construction from computed coordinates. |
| 11 | `11_constraint_region.py` | A feasible region with constraints and an objective, beside a block diagram. |

The primitives these use are described one at a time in the [user guide](user-guide.md#technical-drawing-primitives) and shown in [`examples/primitives/`](../examples/primitives/). Formulas are covered in the [math markup reference](math-markup.md).

## 1. Start from the paper theme

```python
from diagrams_as_code import Diagram, Style

with Diagram("Control loop", theme="paper") as diag:
    ...
    diag.caption("**Figure 2:** Closed-loop control", small_caps=True)
```

`paper` gives black hairlines on white, square corners and no shadows. Leave the canvas size off: it is fitted to the drawing, caption included. Add `pixel_snap=True` if 1 px lines must fall exactly on pixels in a PNG.

## 2. Decide how the figure is laid out

A block diagram can be left to the layout engine. A figure with a fixed composition is placed by hand, and that is normal: positions are part of what the figure says.

- **Relative placement** keeps a script short when things form rows and columns: `b.right_of(a, margin=60)`, `c.below(a, margin=40)`, `align([...], "top")`, `distribute([...], "right", gap=40)`.
- **Absolute placement** suits everything else: `shape.at(x, y)`, with `anchor="top_center"` and the like to say which point of the element goes there. Lengths may carry units (`"30mm"`, `"12pt"`).
- **Computed placement** suits geometry and plots. Work out the coordinates in the script (intersections, centres, a mapping from data to pixels) and pass them in. Figures 7, 10 and 11 do this.

When copying an existing figure, measure it once in its own pixels and scale: figure 1 keeps the reference's coordinates and multiplies them by one factor.

## 3. Layers, panels and nesting

- `with diag.band("1. Governance layer", notes=[...]):` draws a dashed frame with a bold title around what is created inside it. `min_width` lets stacked bands share a width.
- A box that holds other things is a shape with children: `inner.inside(panel, "top_left", 20, 40)`. The children move with the panel, the panel is painted under the lines, and lines to a child may cross the panel's border.
- A label that sits on another shape is nested in it the same way, as figure 1 does with the text on its cuboid.
- `Style(fill="#E9E9EC")` shades a panel; `Style(double=4)` gives a double border; `Style(fill_opacity=0.5)` makes a fill translucent.

## 4. Text and formulas

- `diag.text("...", size=14, align="center")` is text with no box. It takes `**bold**`, `*italic*`, line breaks and `$math$`.
- Every label takes the same markup, so a box can hold a title and a formula: `"**Loss**\n$L = \\sum_i (y_i - p_i)^2$"`.
- `font="serif"` with `italic=True` sets a remark apart. `padding=4` keeps lines that end at a text a little clear of the letters.
- The supported math is listed in the [math markup reference](math-markup.md). Fractions, radicals and accents are not supported; the reference gives the usual substitutes.

## 5. Lines

| Need | Write |
|---|---|
| A heavier or lighter line | `diag.edge(width=3.0)`, `width=0.75` |
| Another arrowhead | `head="open"`, `"stealth"`, `"circle"`, `"bar"`, `"diamond"`, `"none"`; `arrow_size=0.8` |
| An arrow at both ends | `two_way=True` |
| "And so on" | `ellipsis=True` |
| A line attached at an exact spot on a side | `box.anchor("right", 0.25) >> other.anchor("left", 0.5)` |
| A line between two points | `diag.connect((x1, y1), (x2, y2), routing="direct")` |
| A line through given points | `via=[(x, y), ...]`; with `routing="spline"` it is a smooth curve |
| A note with a thin line to what it describes | `diag.leader("text", target, at=(x, y))` |
| Several lines sharing a trunk | `diag.fan_out(source, targets, trunk=40)` |
| A line drawn over the shapes | `z=5` |
| A brace beside some elements | `diag.bracket("label", side="right").spanning(first, last)` |

A leader or a curve may end at a point inside the shape it refers to: `diag.leader("the cut", (420, 310), at=(250, 260))`.

## 6. Solids and free outlines

- `diag.cuboid("label", width, height, depth)` and `diag.solid(Solid.hull(points), projection=oblique(35, 0.55))` draw convex solids with hidden edges dashed. `cut=(point, normal)` draws a cutting plane and its section.
- `diag.polygon(points)`, `diag.polyline(points)` and `diag.path("M ... A ... Z")` draw free outlines: waveforms, regions, circles and arcs. They are drawing, not nodes, so they may overlap each other and be written on.

## 7. Check the figure

Three checks, in this order.

**Lint it.** The linter lays the figure out and reports what a reader would see as a defect, naming the elements involved. A run that finds problems looks like this:

```text
$ uv run diagrams-as-code lint examples/technical
examples/technical/04_state_machine.py: edge_through_node: 'Idle' -> 'Closed' crosses 'Connecting'
examples/technical/04_state_machine.py: node_overlap: 'timeout' overlaps 'Backoff'
11 diagrams checked, 2 findings
```

It exits 1 if anything is found, so it can gate a commit. `--ignore KIND[,KIND]` drops kinds you have decided to accept. Findings are fixed in the script: move the element, attach the line somewhere else with `anchor()`, nest a label in the shape it sits on, or create a note inside the band it belongs to.

| Kind | Meaning |
|---|---|
| `edge_through_node` | a line crosses a shape it is not attached to |
| `edge_through_own_endpoint` | a line cuts through the shape it starts or ends at |
| `tangent_arrival` | a line runs along the side it arrives at |
| `edge_on_edge` | two unrelated lines run on top of each other |
| `edge_through_badge`, `edge_through_title` | a line crosses an edge label or a group title |
| `badge_over_node`, `badge_over_badge`, `badge_over_title` | an edge label covers something |
| `label_overflow`, `title_overflow` | text does not fit its shape or frame |
| `node_overlap`, `group_overlap` | two shapes, or a shape and a group it is not in, cover each other |
| `content_clipped`, `canvas_mostly_empty` | the canvas is too small, or far too large |
| `layout_warning` | the layout engine warned about the script |

What the linter does not count: shapes nested with `inside()`, captions and points, a line ending at a point set inside a shape, a bracket beside shapes nested in a panel, and free outlines.

**Look at it.** A clean lint means nothing collides. It does not mean the figure is well composed. Render a PNG and look at the spacing, the alignment and where the arrows end:

```bash
uv run python examples/technical/02_control_loop.py     # writes svg, png and a README
```

**Pin it.** Each figure in `examples/technical/` has a golden image in `tests/golden/technical/`. The test suite renders the figure and compares the two, so an engine change that moves a line fails a test and shows up as a changed picture in review.

```bash
uv run python tools/golden_images.py            # compare and print a table
uv run python tools/golden_images.py --update   # after a deliberate change: store the new pictures
```

Golden images are rendered at a fixed width with the fonts in `tests/fixtures/fonts`, so they come out the same on every machine. A pixel counts as changed when a colour channel differs by more than 48 of 255; a picture fails when more than 0.05% of its pixels changed.

## 8. Export a PDF

```python
diag.render_pdf("figure.pdf")
```

or, from the command line:

```bash
uv run diagrams-as-code render examples/technical --out build --format svg,pdf
```

The PDF is one page the size of the figure (0.75 pt per px) and is all vector: it can be placed in a LaTeX or Word document and scaled freely. Nothing has to be installed; the writer is part of the package.

It is drawn from the same SVG `render_svg` writes, so what you checked in section 7 is what the PDF holds. Three things to know:

- **Fonts.** Text is set in the standard PDF fonts (Helvetica for sans, Times for serif), which every viewer supplies, so no font is embedded. Formulas are outlines and look the same everywhere. If a publisher requires every font to be embedded, convert the file with their tool of choice or use the SVG.
- **Characters.** Latin text, Greek letters, arrows and common math signs are covered. A character outside those (CJK, emoji) is drawn as `?`, and a warning names it. Inside `$...$` every supported symbol is an outline and always works.
- **Shadows.** Themes other than `paper` draw drop shadows; in the PDF they are approximated with translucent rings rather than a true blur.

## Limits to know about

- Shape kinds are boxes, cylinders, clouds, diamonds and the like; there is no circle or ellipse kind. A circle is a box with `Style(radius=...)` set to half its side, or an arc path.
- A self-loop is drawn as a spline between two anchors on one side with `via` points.
- Serif text is measured with the sans metrics and pinned to that width (in the PDF it is stretched to that same width).
- A cutting plane is drawn over the whole solid, not hidden behind its near faces.
- Text is `sans` or `serif`; there is no monospace option.
