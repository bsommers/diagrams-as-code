from dataclasses import FrozenInstanceError
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
from iiot_diagrams import (
    BLUEPRINT,
    CYBER_SLATE,
    IIOT_DARK_GOLD,
    IIOT_LIGHT,
    THEMES,
    ShapeLibrary,
    ShapeRenderer,
    Theme,
    get_theme,
    register_theme,
    reset_themes,
)


def test_package_exports() -> None:
    """Verify Theme and Shape symbols exported from root package."""
    assert Theme is not None
    assert get_theme is not None
    assert register_theme is not None
    assert reset_themes is not None
    assert THEMES is not None
    assert IIOT_DARK_GOLD is not None
    assert IIOT_LIGHT is not None
    assert BLUEPRINT is not None
    assert CYBER_SLATE is not None
    assert ShapeLibrary is not None
    assert ShapeRenderer is ShapeLibrary


def test_theme_presets_brief_contract() -> None:
    """Verify exact brief contract test for default dark and light presets."""
    dark = get_theme("iiot_dark_gold")
    assert dark.background == "#000000"
    assert dark.accent == "#FFC000"
    light = get_theme("iiot_light")
    assert light.background == "#FFFFFF"


def test_theme_all_presets_and_fields() -> None:
    """Verify all four required presets exist and have valid contrast fields."""
    preset_names = ["iiot_dark_gold", "iiot_light", "blueprint", "cyber_slate"]
    for name in preset_names:
        theme = get_theme(name)
        assert theme.name == name
        assert theme.background.startswith("#")
        assert theme.group_bg.startswith("#")
        assert theme.group_stroke.startswith("#")
        assert theme.node_fill.startswith("#")
        assert theme.node_stroke.startswith("#")
        assert theme.accent.startswith("#")
        assert theme.text.startswith("#")
        assert theme.subtext.startswith("#")
        assert theme.edge_color.startswith("#")
        assert len(theme.font_family) > 0

        # Verify property aliases for backwards compatibility
        assert theme.accent_gold == theme.accent
        assert theme.text_color == theme.text
        assert theme.subtext_color == theme.subtext


def test_theme_case_insensitivity_and_whitespace() -> None:
    """Verify theme lookup handles mixed casing and surrounding whitespace."""
    dark_upper = get_theme("IIOT_DARK_GOLD")
    assert dark_upper.name == "iiot_dark_gold"
    light_mixed = get_theme("  IioT_Light  ")
    assert light_mixed.name == "iiot_light"
    bp = get_theme("BLUEPRINT")
    assert bp.name == "blueprint"
    cs = get_theme("Cyber_Slate")
    assert cs.name == "cyber_slate"


def test_theme_fallback_on_unknown() -> None:
    """Verify unknown theme names fall back gracefully to default dark gold."""
    default_theme = get_theme()
    assert default_theme.name == "iiot_dark_gold"

    fallback = get_theme("non_existent_custom_theme")
    assert fallback.name == "iiot_dark_gold"
    assert fallback == default_theme


def test_theme_registration_retrieval_and_reset() -> None:
    """Verify registering a custom theme, isolation, and reset_themes()."""
    custom = Theme(
        name="industrial_amber",
        background="#121212",
        group_bg="#1E1E1E",
        group_stroke="#333333",
        node_fill="#242424",
        node_stroke="#FFA000",
        accent="#FFA000",
        text="#F5F5F5",
        subtext="#9E9E9E",
        edge_color="#FFA000",
    )
    register_theme(custom)

    fetched = get_theme("industrial_amber")
    assert fetched.name == "industrial_amber"
    assert fetched.accent == "#FFA000"

    fetched_upper = get_theme("INDUSTRIAL_AMBER")
    assert fetched_upper.name == "industrial_amber"

    # Verify reset_themes removes custom themes and preserves default presets
    reset_themes()
    assert "industrial_amber" not in THEMES
    fallback = get_theme("industrial_amber")
    assert fallback.name == "iiot_dark_gold"


def test_theme_immutability() -> None:
    """Verify Theme dataclass is frozen and prevents attribute mutation."""
    dark = get_theme("iiot_dark_gold")
    with pytest.raises(FrozenInstanceError):
        dark.background = "#FF0000"  # type: ignore[misc]


def test_theme_type_validation() -> None:
    """Verify input validation for theme retrieval and registration."""
    with pytest.raises(TypeError, match="Theme name must be a str"):
        get_theme(123)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="Expected Theme instance"):
        register_theme("not_a_theme")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Theme name must be a non-empty string"):
        register_theme(
            Theme(
                name="",
                background="#000",
                group_bg="#000",
                group_stroke="#000",
                node_fill="#000",
                node_stroke="#000",
                accent="#000",
                text="#000",
                subtext="#000",
                edge_color="#000",
            )
        )


def test_shape_library_svg_box_brief_contract() -> None:
    """Verify exact brief contract test for ShapeLibrary render_box."""
    lib = ShapeLibrary()
    rect_svg = lib.render_box(
        10, 10, 100, 50, fill="#1A1A1A", stroke="#FFC000", radius=8
    )
    assert "<rect" in rect_svg
    assert 'rx="8"' in rect_svg
    assert 'fill="#1A1A1A"' in rect_svg
    assert 'stroke="#FFC000"' in rect_svg


def test_render_box_attributes_and_defaults() -> None:
    """Verify render_box XML attributes, defaults, and XML well-formedness."""
    lib = ShapeLibrary()
    box_svg = lib.render_box(20.0, 30.0, 150.0, 80.0, "#222222", "#FFCC00")

    # Wrap in root svg to parse as XML
    root = ET.fromstring(f"<svg>{box_svg}</svg>")
    rect = root.find("rect")
    assert rect is not None
    assert rect.attrib["x"] == "20.0"
    assert rect.attrib["y"] == "30.0"
    assert rect.attrib["width"] == "150.0"
    assert rect.attrib["height"] == "80.0"
    assert rect.attrib["fill"] == "#222222"
    assert rect.attrib["stroke"] == "#FFCC00"
    assert rect.attrib["stroke-width"] == "2.0"
    assert rect.attrib["rx"] == "6.0"


def test_render_cylinder_svg() -> None:
    """Verify render_cylinder generates valid path and ellipse for 3D tank/cylinder."""
    lib = ShapeLibrary()
    cyl_svg = lib.render_cylinder(10.0, 20.0, 100.0, 60.0, "#333333", "#00D2FF")

    root = ET.fromstring(f"<svg>{cyl_svg}</svg>")
    path = root.find("path")
    ellipse = root.find("ellipse")
    assert path is not None
    assert ellipse is not None

    assert path.attrib["fill"] == "#333333"
    assert path.attrib["stroke"] == "#00D2FF"
    assert ellipse.attrib["fill"] == "#333333"
    assert ellipse.attrib["stroke"] == "#00D2FF"
    assert ellipse.attrib["cx"] == "60.0"  # 10 + 100/2
    assert ellipse.attrib["rx"] == "50.0"  # 100/2


def test_render_diamond_svg() -> None:
    """Verify render_diamond generates 4-point rhombus path."""
    lib = ShapeLibrary()
    diamond_svg = lib.render_diamond(
        10.0, 10.0, 80.0, 80.0, fill="#202020", stroke="#FFC000", stroke_width=3.0
    )

    root = ET.fromstring(f"<svg>{diamond_svg}</svg>")
    path = root.find("path")
    assert path is not None
    assert "M 50.0 10.0" in path.attrib["d"]
    assert "L 90.0 50.0" in path.attrib["d"]
    assert "L 50.0 90.0" in path.attrib["d"]
    assert "L 10.0 50.0" in path.attrib["d"]
    assert path.attrib["stroke-width"] == "3.0"


def test_render_cloud_svg() -> None:
    """Verify render_cloud generates smooth cubic bezier closed path."""
    lib = ShapeLibrary()
    cloud_svg = lib.render_cloud(0.0, 0.0, 120.0, 80.0, "#1F2937", "#60A5FA")

    root = ET.fromstring(f"<svg>{cloud_svg}</svg>")
    path = root.find("path")
    assert path is not None
    assert path.attrib["d"].startswith("M")
    assert "C" in path.attrib["d"]
    assert path.attrib["d"].endswith("Z")
    assert path.attrib["fill"] == "#1F2937"
    assert path.attrib["stroke"] == "#60A5FA"


def test_render_server_rack_svg() -> None:
    """Verify render_server_rack chassis, blade units, and LED indicators."""
    lib = ShapeLibrary()
    rack_svg = lib.render_server_rack(
        10.0, 20.0, 120.0, 160.0, fill="#1E1E24", stroke="#FFC000", num_units=4
    )

    root = ET.fromstring(f"<svg>{rack_svg}</svg>")
    rects = root.findall("rect")
    # Outer rack frame + 4 blade units = 5 rects
    assert len(rects) == 5
    assert rects[0].attrib["width"] == "120.0"
    assert rects[0].attrib["height"] == "160.0"

    circles = root.findall("circle")
    # 2 LEDs per blade * 4 blades = 8 LED circles
    assert len(circles) == 8

    lines = root.findall("line")
    # Flange lines (2) + vent lines (4) = 6 lines
    assert len(lines) >= 6


def test_render_database_container_svg() -> None:
    """Verify multi-tier database container shape rendering and XML validity."""
    lib = ShapeLibrary()
    db_svg = lib.render_database(
        10.0, 10.0, 100.0, 120.0, fill="#24242A", stroke="#00E5A3", num_tiers=3
    )

    root = ET.fromstring(f"<svg>{db_svg}</svg>")
    paths = root.findall("path")
    # Body path + 2 intermediate tier shelf curves = 3 paths
    assert len(paths) == 3
    ellipse = root.find("ellipse")
    assert ellipse is not None
    assert ellipse.attrib["cx"] == "60.0"
    assert ellipse.attrib["rx"] == "50.0"


def test_render_badge_svg_and_escaping() -> None:
    """Verify render_badge pill container, text positioning, and XML entity escaping."""
    lib = ShapeLibrary()
    badge_svg = lib.render_badge(
        50.0,
        100.0,
        "MQTT & TLS > v1.3",
        fill="#FFC000",
        text_color="#000000",
        font_family="\"Fira Code\", 'Consolas', <sans-serif>&",
    )

    root = ET.fromstring(f"<svg>{badge_svg}</svg>")
    g = root.find("g")
    assert g is not None
    assert g.attrib.get("class") == "badge"

    rect = g.find("rect")
    assert rect is not None
    assert rect.attrib["fill"] == "#FFC000"
    assert float(rect.attrib["width"]) > 24.0

    text = g.find("text")
    assert text is not None
    assert text.text == "MQTT & TLS > v1.3"
    assert text.attrib["fill"] == "#000000"
    # Font family should have escaped quotes/tags
    assert "&lt;" not in text.attrib["font-family"] or "<" not in badge_svg


def test_shape_dimension_guards() -> None:
    """Verify non-positive dimensions raise ValueError across all shape primitives."""
    lib = ShapeLibrary()

    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_box(0, 0, 0, 50, "#000", "#fff")
    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_box(0, 0, 100, -10, "#000", "#fff")

    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_cylinder(0, 0, -5, 50, "#000", "#fff")
    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_cylinder(0, 0, 50, 0, "#000", "#fff")

    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_diamond(0, 0, 0, 50, "#000", "#fff")
    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_diamond(0, 0, 50, -5, "#000", "#fff")

    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_cloud(0, 0, -20, 50, "#000", "#fff")
    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_cloud(0, 0, 50, 0, "#000", "#fff")

    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_server_rack(0, 0, 0, 100, "#000", "#fff")
    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_server_rack(0, 0, 100, -10, "#000", "#fff")

    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_database(0, 0, -1, 100, "#000", "#fff")
    with pytest.raises(ValueError, match="Width and height must be positive"):
        lib.render_database(0, 0, 100, 0, "#000", "#fff")

    with pytest.raises(ValueError, match="font_size must be positive"):
        lib.render_badge(0, 0, "test", font_size=0)
    with pytest.raises(ValueError, match="height must be positive"):
        lib.render_badge(0, 0, "test", height=-5)

    with pytest.raises(ValueError, match="size must be positive"):
        lib.render_icon("sensor", 0, 0, size=0)


def test_builtin_vector_icons_availability_and_aliases() -> None:
    """Verify built-in icon presence and alias resolution for required components."""
    lib = ShapeLibrary()
    required_names = [
        "sensor",
        "gateway",
        "edge",
        "broker",
        "database",
        "influx",
        "queue",
        "kafka",
        "cloud",
        "dashboard",
        "grafana",
    ]
    for name in required_names:
        assert lib.has_icon(name), f"Missing icon or alias: {name}"

    canonical = lib.list_icons()
    assert "sensor" in canonical
    assert "gateway" in canonical
    assert "broker" in canonical
    assert "database" in canonical
    assert "queue" in canonical
    assert "cloud" in canonical
    assert "dashboard" in canonical


def test_builtin_vector_icons_render_svg() -> None:
    """Verify render_icon generates valid transformed SVG group for all canonical icons."""
    lib = ShapeLibrary()
    for name in lib.list_icons():
        icon_svg = lib.render_icon(name, 10.0, 20.0, size=32.0, color="#00E5A3")
        assert f"icon-{name}" in icon_svg

        # Verify XML validity
        root = ET.fromstring(f"<svg>{icon_svg}</svg>")
        g = root.find("g")
        assert g is not None
        assert "translate(10.0, 20.0)" in g.attrib["transform"]
        assert "scale(" in g.attrib["transform"]


def test_builtin_vector_icons_convenience_methods() -> None:
    """Verify dedicated convenience rendering methods on ShapeLibrary."""
    lib = ShapeLibrary()
    s = lib.render_sensor(0, 0)
    assert "icon-sensor" in s
    gw = lib.render_gateway(0, 0)
    assert "icon-gateway" in gw
    edge = lib.render_edge(0, 0)
    assert "icon-gateway" in edge
    b = lib.render_broker(0, 0)
    assert "icon-broker" in b
    db = lib.render_database_icon(0, 0)
    assert "icon-database" in db
    inf = lib.render_influx(0, 0)
    assert "icon-database" in inf
    q = lib.render_queue(0, 0)
    assert "icon-queue" in q
    k = lib.render_kafka(0, 0)
    assert "icon-queue" in k
    c = lib.render_cloud_icon(0, 0)
    assert "icon-cloud" in c
    dash = lib.render_dashboard(0, 0)
    assert "icon-dashboard" in dash
    graf = lib.render_grafana(0, 0)
    assert "icon-dashboard" in graf


def test_builtin_vector_icons_unknown_raises_key_error() -> None:
    """Verify unknown icon request raises KeyError with informative message."""
    lib = ShapeLibrary()
    with pytest.raises(KeyError, match="Unknown icon 'unsupported_gadget'"):
        lib.render_icon("unsupported_gadget", 0, 0)


def test_domain_icons_and_aliases() -> None:
    """Verify domain icons across Cloud, AI, Computer, Datacenter, Business Process, Cybersecurity, and Network Engineering."""
    lib = ShapeLibrary()
    domain_icons = [
        "vpc", "serverless", "storage", "api_gateway", "cdn", "firewall", "dns",
        "brain", "model", "agent", "chip", "vector_db", "vision", "workflow",
        "server", "terminal", "laptop", "mobile", "plc", "router",
        "cluster", "storage_array", "cooling", "ups", "container", "kubernetes",
        "user", "document", "decision", "message", "shield", "analytics",
        # Cybersecurity
        "lock", "key", "shield_check", "siem", "soc", "malware_scan", "vault", "honeypot",
        # Network Engineering
        "switch", "core_router", "bgp", "mpls", "firewall_ha", "load_balancer", "patch_panel", "fiber_optic",
    ]
    for icon in domain_icons:
        assert lib.has_icon(icon)
        rendered = lib.render_icon(icon, 10.0, 20.0, size=24.0, color="#10B981")
        assert f"icon-{icon}" in rendered
        root = ET.fromstring(f"<svg>{rendered}</svg>")
        assert root.find("g") is not None

    # Verify key aliases
    aliases = {
        "lambda": "serverless",
        "s3": "storage",
        "llm": "model",
        "gpu": "chip",
        "k8s": "kubernetes",
        "actor": "user",
        "audit": "shield",
        # Cybersecurity aliases
        "crypto": "lock",
        "pki": "key",
        "radar": "siem",
        "hsm": "vault",
        # Network engineering aliases
        "l3_switch": "switch",
        "lb": "load_balancer",
        "fiber": "fiber_optic",
    }
    for alias, canonical in aliases.items():
        assert lib.has_icon(alias)
        rendered = lib.render_icon(alias, 0, 0)
        assert f"icon-{canonical}" in rendered


def test_custom_icon_file_and_directory_loading(tmp_path: Path) -> None:
    """Verify dynamic loading of custom external SVG icons."""
    lib = ShapeLibrary()
    custom_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg>'
    svg_file = tmp_path / "custom_spark.svg"
    svg_file.write_text(custom_svg, encoding="utf-8")

    name = lib.load_icon_file(svg_file)
    assert name == "custom_spark"
    assert lib.has_icon("custom_spark")

    rendered = lib.render_icon("custom_spark", 5.0, 5.0, size=30.0, color="#FF0055")
    assert "icon-custom_spark" in rendered
    assert '<circle cx="12" cy="12" r="10"/>' in rendered

    # Directory loading
    sub_dir = tmp_path / "extra_icons"
    sub_dir.mkdir()
    (sub_dir / "spark_a.svg").write_text(custom_svg, encoding="utf-8")
    (sub_dir / "spark_b.svg").write_text(custom_svg, encoding="utf-8")
    loaded = lib.load_icons_from_directory(sub_dir)
    assert "spark_a" in loaded
    assert "spark_b" in loaded
    assert lib.has_icon("spark_a")
    assert lib.has_icon("spark_b")


def test_new_theme_presets_evaluation() -> None:
    """Verify newly added themes (nord, emerald, crimson, monochrome)."""
    from iiot_diagrams.theme import CRIMSON, EMERALD, MONOCHROME, NORD, get_theme

    for theme_name in ("nord", "emerald", "crimson", "monochrome"):
        t = get_theme(theme_name)
        assert t.name == theme_name
        assert t.background.startswith("#")
        assert t.accent.startswith("#")
        assert t.node_stroke.startswith("#")

    assert NORD.name == "nord"
    assert EMERALD.name == "emerald"
    assert CRIMSON.name == "crimson"
    assert MONOCHROME.name == "monochrome"


def test_theme_expansion_and_helpers() -> None:
    """Verify new themes (solarized_light, pastel_light, dracula, synthwave, high_contrast) and helpers."""
    from diagrams_as_code.theme import (
        DRACULA,
        HIGH_CONTRAST,
        PASTEL_LIGHT,
        SOLARIZED_LIGHT,
        SYNTHWAVE,
        create_theme,
        get_dark_themes,
        get_light_themes,
        get_theme,
        list_themes,
    )

    all_names = list_themes()
    assert "solarized_light" in all_names
    assert "pastel_light" in all_names
    assert "dracula" in all_names
    assert "synthwave" in all_names
    assert "high_contrast" in all_names

    # Check light/dark classification
    light_names = get_light_themes()
    assert "iiot_light" in light_names
    assert "monochrome" in light_names
    assert "solarized_light" in light_names
    assert "pastel_light" in light_names

    dark_names = get_dark_themes()
    assert "iiot_dark_gold" in dark_names
    assert "blueprint" in dark_names
    assert "cyber_slate" in dark_names
    assert "nord" in dark_names
    assert "dracula" in dark_names
    assert "synthwave" in dark_names

    # Check theme instance passed to get_theme
    t_solar = get_theme("solarized_light")
    assert get_theme(t_solar) == t_solar

    # Check create_theme
    custom = create_theme("my_brand", base="solarized_light", accent="#FF4400")
    assert custom.name == "my_brand"
    assert custom.accent == "#FF4400"
    assert custom.background == t_solar.background

