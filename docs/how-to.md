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
diag.generate_readme("architecture.svg", "README.md")
```

---

## Recipe 2: Switching Themes & Creating Custom Brand Palettes

### Using Built-in Themes

```python
from diagrams_as_code import Diagram

# Built-in theme options:
# Dark: "iiot_dark_gold", "blueprint", "cyber_slate", "nord", "emerald", "crimson", "dracula", "synthwave"
# Light: "iiot_light", "monochrome", "solarized_light", "pastel_light"
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

## Troubleshooting Matrix

| Problem | Root Cause | Solution |
|---|---|---|
| **Shapes stacked at (0, 0)** | Rendering called inside `with` context block before `solve()`. | Move `diag.render_svg(...)` outside the `with Diagram(...)` context, or rely on auto-solve dirty checks. |
| **Labels clipping / spilling out** | Label exceeded shape width without wrapping. | Use `label_position="bottom"`, or rely on built-in `<tspan>` auto-wrapping and dynamic font scaling. |
| **Protocol badges overlapping boxes** | Gap between groups was smaller than badge text width. | Increase inter-group margin from `50` to `80`–`100` (`g_2.right_of(g_1, margin=90)`). |
| **`RuntimeError: Cycle detected`** | Circular relative constraints (e.g. A right of B, B right of A). | Inspect relative constraints to ensure the spatial DAG has no loops. |
| **Unknown icon name error** | Typo in icon name or unregistered custom icon. | Check `icons/icons.yaml` for canonical names and aliases, or load custom SVG via `ShapeLibrary.load_icon_file(...)`. |
