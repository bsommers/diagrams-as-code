# How-To Recipes & Troubleshooting Guide

## Recipe 1: Creating a Simple 3-Tier Web Architecture

```python
from pathlib import Path
from diagrams_as_code import Diagram, Shape

with Diagram("3-Tier Web Architecture", theme="blueprint") as diag:
    # 1. Declare Public Ingress
    with diag.group("Public Edge") as g_public:
        client = diag.add(Shape("client", "Web Client", icon="mobile"))
        alb = diag.add(Shape("alb", "Application LB", icon="api_gateway"))
        alb.below(client, margin=25)

    # 2. Declare Compute Tier
    with diag.group("Application Tier") as g_app:
        app1 = diag.add(Shape("app1", "Service Node 01", icon="server"))
        app2 = diag.add(Shape("app2", "Service Node 02", icon="server"))
        app2.below(app1, margin=25)

    # 3. Declare Database Tier
    with diag.group("Database Tier") as g_db:
        primary_db = diag.add(Shape("db", "Primary DB", icon="database", kind="cylinder"))

    # 4. Position Groups
    g_public.at(60.0, 80.0)
    g_app.right_of(g_public, margin=90)
    g_db.right_of(g_app, margin=90)

    # 5. Connect Elements with Protocols
    client >> diag.edge("HTTPS :443") >> alb
    alb >> diag.edge("gRPC :50051") >> app1
    alb >> diag.edge("gRPC :50051") >> app2
    app1 >> diag.edge("TCP :5432") >> primary_db
    app2 >> diag.edge("TCP :5432") >> primary_db

# 6. Render outputs
diag.render_svg("architecture.svg")
diag.render_png("architecture.png")
diag.render_pdf("architecture.pdf")  # vector PDF, no extra software needed
diag.generate_readme("architecture.svg", "README.md")
```

---

## Recipe 2: Switching Themes & Creating Custom Brand Palettes

### Using Built-in Themes

```python
from diagrams_as_code import Diagram

# Built-in theme options:
# Dark: "iiot_dark_gold", "blueprint", "cyber_slate", "nord", "emerald", "crimson", "dracula", "synthwave"
# Light: "iiot_light", "monochrome", "solarized_light", "pastel_light", "paper"
# Accessibility: "high_contrast"

with Diagram("Arctic Cloud Fabric", theme="nord") as diag:
    ...
```

### Deriving a Custom Theme with Overrides

```python
from diagrams_as_code import Diagram, create_theme

# Derive custom corporate theme from solarized_light
corporate_theme = create_theme(
    "acme_corp",
    base="solarized_light",
    accent="#FF5500",
    node_stroke="#FF5500",
    edge_color="#FF5500",
)

with Diagram("Acme Microservices", theme=corporate_theme) as diag:
    ...
```

---

## Recipe 3: Eliminating Text Spilling: Text Below Graphic & Multi-Line Labels

### Text Below Graphic Mode (`label_position="bottom"`)

For compact icon tiles with labels positioned cleanly beneath the graphic:

```python
from diagrams_as_code import Shape

# Label rendered centered beneath the 64x56 graphic tile
auth_key = Shape(
    "auth_key",
    label="Hardware Security Key",
    icon="mobile",
    width=64,
    height=56,
    label_position="bottom",
)
```

### Automatic Multi-Line Wrapping Inside Cards

Long labels inside standard cards automatically wrap onto multiple lines using SVG `<tspan>` tags without clipping:

```python
# Automatically wraps into 2 balanced lines: 'Cloud IdP' and '(Okta/Entra)'
idp = Shape("idp", "Cloud IdP (Okta/Entra)", icon="key")
```

---

## Recipe 4: Using Standalone Vector Icons (`kind="icon"`)

Render pure vector icons without bounding rectangle boxes (like Cisco / AWS architecture schematics):

```python
from diagrams_as_code import Shape

# Renders crisp standalone router vector icon with drop shadow and label below
core_router = Shape(
    "core_router",
    label="Core BGP Router",
    kind="icon",
    icon="router",
)
```

---

## Recipe 5: Living Documentation & BOM Generation

Every diagram automatically tracks component properties and serializes them into Bill of Materials documentation:

```python
from diagrams_as_code import Shape

server = Shape(
    "app_srv",
    label="App Server",
    icon="server",
    cpu="16 vCPU",
    memory="64 GB",
    storage="1 TB NVMe",
    operating_system="Debian 12",
    cost_per_month="$140.00",
)

# Emits markdown tables and JSON specifications
diag.generate_readme("output.svg", "output_README.md")
diag.generate_bom_json("output_bom.json")
```

---

## Recipe 6: CI/CD Automated Diagram Testing (GitHub Actions)

Add this workflow step to `.github/workflows/ci.yml` to automatically verify all diagrams stay clean, compiled, and un-stacked:

```yaml
- name: Verify Architecture Diagrams & Anti-Stacking Tests
  run: |
    uv run pytest tests/test_domain_examples.py
```

---

## Recipe 7: Let the Engine Lay Out a Diagram

Set `layout="auto"` and skip `.at()` / `.right_of()` entirely — the layered
engine places every shape and group from the edge structure, left-to-right
by default:

```python
from diagrams_as_code import Diagram

with Diagram("Order Pipeline", theme="nord", layout="auto", direction="LR") as diag:
    with diag.group("Ingress") as ingress:
        client = diag.shape("Client", icon="mobile")
        gw = diag.shape("API Gateway", icon="api_gateway")
    with diag.group("Compute") as compute:
        worker = diag.shape("Worker", icon="server")

    client >> diag.edge("HTTPS") >> gw
    gw >> diag.edge("invoke") >> worker
```

Use `direction="TB"` to rank top-to-bottom instead. Ranks follow edge
direction; ties break by declaration order, so re-running the same script
produces the same layout every time.

### Mixing pinned and auto-placed shapes

A shape or group positioned with `.at()`, or anchored with `.right_of()` /
`.below()` / etc., stays exactly where you put it — the auto engine only
places elements that have no position constraint of their own. Relative
placement can target an auto-placed sibling, since its position is resolved
before the render:

```python
with Diagram("Mixed Layout", layout="auto") as diag:
    gw = diag.shape("API Gateway", icon="api_gateway")   # auto-placed
    note = diag.shape("Ops Note", kind="diamond")
    note.right_of(gw, margin=40)                          # pinned, relative to an auto shape
```

If a pin ends up overlapping an auto-placed sibling in the same scope, the
render issues a `LayoutWarning` naming both shapes:

```
LayoutWarning: pinned 'Ops Note' overlaps auto-placed 'API Gateway'; move the pin or give both explicit positions
```

The warning doesn't fail the render — fix it by moving the pin, giving the
auto-placed shape an explicit position too, or widening the margin.

### The layout file workflow

Export the positions a script resolved to, hand-edit them, and reuse them on
later renders instead of guessing coordinates:

```bash
uv run diagrams-as-code layout export my_diagram.py
# wrote my_diagram.layout.json
```

Open `my_diagram.layout.json` and adjust any `x`/`y` pair. Each entry is
keyed by the shape's or group's **label path** — ancestor group labels and
its own label joined by `/` (e.g. `"Ingress/API Gateway"`) — unless the
element was created with an explicit `id=`, in which case its key is that id.
Give a shape `id=` when its label isn't unique within its scope, or when you
want a key that survives a label rename. A key that names a **group** moves
every child in that group together, preserving their positions relative to
each other.

Render with the edited file layered on top of the script's own layout:

```bash
uv run diagrams-as-code render my_diagram.py --layout-file my_diagram.layout.json
```

or, from Python, pass it to the constructor directly. Pass the same `layout=`
mode the script itself uses — the file records positions, not the layout mode,
and `layout` still defaults to `"manual"`:

```python
with Diagram("My Diagram", layout="auto", layout_file="my_diagram.layout.json") as diag:
    ...
```

A layout file entry always wins over both manual constraints and the auto
engine's placement for that key; a stale entry that matches no element in
the current script emits a `LayoutWarning` and is otherwise ignored.

The canvas always grows to fit whatever lands outside it, plus the framing
margin — an edited layout-file coordinate, an auto-placed shape, or a plain
`.at()` call in `manual` mode with no layout file at all. A `width`/`height`
you passed is a floor, not a ceiling: it's honored whenever content already
fits, and widened past it otherwise. It never shrinks below what you passed.

### Changing settings after construction

`diag.configure(layout=..., direction=..., theme=..., layout_file=...,
rank_gap=..., node_gap=...)` updates the settings you name and re-solves on the
next render. `None` means "leave this one alone", so **`configure(layout_file=None)`
does not clear a layout file** that was set earlier — there is no way to go back
to "no layout file" on an existing `Diagram`; build a new one instead. For the
same reason `configure(theme=...)` re-resolves the named theme and drops any
`theme_overrides` passed to the constructor.

---

## Recipe 8: Routing Curved Bezier Edges with Obstacle Deflection

Create organic cubic Bezier splines (`routing="curve"`) that automatically calculate port normal tangents, detect intervening obstacles, and route minimal-deviation collision-free detour splines:

```python
from diagrams_as_code import Diagram, Shape, Routing

with Diagram("Event Pipeline", theme="nord") as diag:
    producer = diag.shape("Event Producer", icon="server")
    obstacle = diag.shape("Intervening Gateway", icon="firewall").right_of(producer, margin=80)
    consumer = diag.shape("Event Consumer", icon="database").right_of(obstacle, margin=80)

    # Automatically detects intervening obstacle, evaluates deflection corridors,
    # and emits a smooth C1-continuous cubic Bezier spline around it
    producer >> diag.edge("Stream Events", routing=Routing.CURVE) >> consumer
```

### Reverse-flow Back-edges

Edges connecting nodes backward against the primary flow (e.g. consumer back to producer) automatically resolve to North/South cardinal ports and route through lateral clearance escape corridors (>= 30px):

```python
    # Routes upward from consumer's North port, over obstacles, into producer's North port
    consumer >> diag.edge("Telemetry Sync", routing="curve") >> producer
```

---

## Recipe 9: Smoothing Orthogonal Edges with Rounded Corner Fillets

Round sharp 90-degree orthogonal corners into sleek arcs using `corner_radius` (or `arc_radius`):

```python
from diagrams_as_code import Diagram, Shape

# Set a diagram-wide default corner radius (e.g. 12px)
with Diagram("Microservice Mesh", theme="synthwave", corner_radius=12.0) as diag:
    svc_a = diag.shape("Service A", icon="server")
    svc_b = diag.shape("Service B", icon="server").below(svc_a, margin=40).right_of(svc_a, margin=60)

    # Inherits diagram-level corner_radius=12.0
    svc_a >> diag.edge("gRPC Call") >> svc_b

    # Override corner radius for a specific edge, or pass 0.0 for sharp corners
    svc_b >> diag.edge("Audit Trail", corner_radius=6.0) >> svc_a
```

> **Dynamic Budget Protection**: If an intermediate orthogonal segment is too short to accommodate the requested radius, the engine automatically clamps `R_eff = min(corner_radius, L_in/2, L_out/2)` and suppresses bends under 2.0px to eliminate "dog-ear" visual glitches.

---

## Recipe 10: Generating Interactive SVGs with Pan-Zoom, Search, and Minimap

For complex architectures or large diagrams, enable embedded interactive navigation:

```python
from diagrams_as_code import Diagram

with Diagram("Enterprise Datacenter Map", theme="blueprint", interactive=True) as diag:
    # Build large multi-tier topology...
    ...

# Emits an interactive SVG vector file
diag.render_svg("enterprise_map.svg")
```

When opened in any modern browser, the SVG provides:
- **Pan & Zoom**: Click-and-drag mouse navigation and mouse wheel zooming.
- **Search HUD**: Top-left search bar with real-time text matching, node pulsing, and non-match dimming.
- **Minimap Navigator**: Bottom-right live radar overview with a synchronized viewport bounding box.
- **View Controls**: Zoom in (`+`), zoom out (`-`), and reset view (`⟲`) buttons.

---

## Troubleshooting Matrix

| Problem | Root Cause | Solution |
|---|---|---|
| **Shapes stacked at (0, 0)** | Rendering called inside `with` context block before `solve()`. | Move `diag.render_svg(...)` outside the `with Diagram(...)` context, or rely on auto-solve dirty checks. |
| **Labels clipping / spilling out** | Label exceeded shape width without wrapping. | Use `label_position="bottom"`, or rely on built-in `<tspan>` auto-wrapping and dynamic font scaling. |
| **Protocol badges overlapping boxes** | Gap between groups was smaller than badge text width. | Increase inter-group margin from `50` to `80`–`100` (`g_2.right_of(g_1, margin=90)`). |
| **`RuntimeError: Cycle detected`** | Circular relative constraints (e.g. A right of B, B right of A). | Inspect relative constraints to ensure the spatial DAG has no loops. |
| **Fillet rendered sharp instead of rounded** | Intermediate segment was shorter than 4px (`R_eff < 2.0px`). | Increase spacing between shapes so orthogonal segments have room to fillet. |
| **Curved edge clips intervening shape** | Shape added after edge declaration, or clearance buffer too small. | Declare shapes before edges, or set explicit `clearance=25.0` on the edge. |
| **Unknown icon name error** | Typo in icon name or unregistered custom icon. | Check `icons/icons.yaml` for canonical names and aliases, or load custom SVG via `ShapeLibrary.load_icon_file(...)`. |
