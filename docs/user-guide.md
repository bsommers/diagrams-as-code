# User Guide

[← Back to Documentation Hub](README.md) · [Project README](../README.md)

A task-oriented guide to writing diagrams as Python code and rendering them to SVG, PNG and Markdown/JSON Bill-of-Materials (BOM) files. For deeper recipes see [how-to.md](how-to.md); for installation details see [running.md](running.md); for internals see [architecture.md](architecture.md).

## Table of Contents
- [Concepts](#concepts)
- [Install and first diagram](#install-and-first-diagram)
- [Building blocks](#building-blocks)
- [Positioning: manual, relative, auto](#positioning-manual-relative-auto)
- [Edges and routing](#edges-and-routing)
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

## Themes

Thirteen built-in themes:

- Dark: `iiot_dark_gold` (default), `blueprint`, `cyber_slate`, `nord`, `emerald`, `crimson`, `dracula`, `synthwave`
- Light: `iiot_light`, `monochrome`, `solarized_light`, `pastel_light`
- Accessibility: `high_contrast`

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
diagrams-as-code layout export SCRIPT [-o FILE] [--layout ...] [--direction ...] [--layout-file ...] [--debug]
diagrams-as-code themes
diagrams-as-code icons [--domain DOMAIN]
```

- `--format` defaults to `svg,bom`; PNG is opt-in because its bytes vary by backend.
- `render` accepts scripts or directories; directories are scanned recursively for files defining `diagram()`.
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
