"""Unit and integration tests for pure-Python standalone SVG renderer."""
from __future__ import annotations

import xml.etree.ElementTree as ET
import pytest

import iiot_diagrams
from iiot_diagrams.connections import Edge
from iiot_diagrams.elements import Shape
from iiot_diagrams.geometry import Rect
from iiot_diagrams.groups import Group
from iiot_diagrams.renderer_svg import SVGRenderer
from iiot_diagrams.theme import get_theme


def test_package_exports() -> None:
    """Verify SVGRenderer is exposed in top-level package and __all__."""
    assert hasattr(iiot_diagrams, "SVGRenderer")
    assert "SVGRenderer" in iiot_diagrams.__all__


def test_svg_render_contains_elements() -> None:
    """Verify basic diagram rendering contains groups, shapes, edges, and markers (brief contract)."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    g = Group("g1", label="Production Plant").at(20, 20)
    s1 = Shape("s1", label="Allen-Bradley PLC", width=140, height=60).at(40, 70)
    s2 = Shape("s2", label="IIoT Edge Gateway", width=140, height=60).at(240, 70)
    g.add(s1, s2)
    edge = Edge(s1, s2, label="Modbus TCP")

    svg = renderer.render(
        elements=[s1, s2], groups=[g], edges=[edge], width=600, height=300
    )
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Production Plant" in svg
    assert "Allen-Bradley PLC" in svg
    assert "Modbus TCP" in svg
    assert 'marker-end="url(#arrow)"' in svg


def test_svg_xml_parse_validation() -> None:
    """Verify rendered SVG is strictly well-formed XML and parseable by standard XML parsers."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("node_a", label="Sensor Node").at(50, 50)
    s2 = Shape("node_b", label="Gateway Node").at(250, 50)
    e = Edge(s1, s2, label="OPC-UA")

    svg = renderer.render(elements=[s1, s2], edges=[e], width=800, height=600)
    root = ET.fromstring(svg)

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["viewBox"] == "0 0 800 600"
    assert root.attrib["width"] == "800"
    assert root.attrib["height"] == "600"


def test_svg_structural_elements_existence() -> None:
    """Verify presence of defs, markers, filters, shadow, background rect, and badges."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("plc", label="ControlLogix").at(50, 80)
    s2 = Shape("scada", label="Ignition SCADA").at(300, 80)
    edge = Edge(s1, s2, label="EtherNet/IP")

    svg = renderer.render(elements=[s1, s2], edges=[edge], width=700, height=400)
    root = ET.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Defs, markers, feDropShadow filters
    defs = root.find("svg:defs", ns)
    assert defs is not None
    marker = defs.find("svg:marker", ns)
    assert marker is not None
    assert marker.attrib["id"] == "arrow"

    filter_el = defs.find("svg:filter", ns)
    assert filter_el is not None
    assert filter_el.attrib["id"] == "shadow"
    drop_shadow = filter_el.find("svg:feDropShadow", ns)
    assert drop_shadow is not None

    # Canvas background fill rect
    rects = root.findall("svg:rect", ns)
    assert any(r.attrib.get("width") == "100%" and r.attrib.get("height") == "100%" for r in rects)

    # Edge protocol badge element
    assert 'class="badge"' in svg or "badge" in svg
    assert "EtherNet/IP" in svg


def test_all_shape_kinds_rendering() -> None:
    """Verify dispatching to ShapeLibrary for box, cylinder, database, server_rack, cloud, and diamond."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s_box = Shape("s_box", label="Box Element", kind="box").at(50, 50)
    s_cyl = Shape("s_cyl", label="Silo Tank", kind="cylinder").at(200, 50)
    s_db = Shape("s_db", label="TimeScale DB", kind="database").at(350, 50)
    s_rack = Shape("s_rack", label="IPC Rack", kind="server_rack").at(500, 50)
    s_cloud = Shape("s_cloud", label="AWS Cloud", kind="cloud").at(650, 50)
    s_dia = Shape("s_dia", label="Quality Gate", kind="diamond").at(800, 50)

    shapes = [s_box, s_cyl, s_db, s_rack, s_cloud, s_dia]
    svg = renderer.render(elements=shapes, width=1000, height=300)

    # XML well-formedness
    root = ET.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Verify each shape group exists
    for s in shapes:
        g_el = root.find(f'.//svg:g[@id="{s.id}"]', ns)
        assert g_el is not None, f"Missing group for {s.id}"

    # Specific geometric elements expected from shapes
    # Cylinder and database have ellipses
    assert svg.count("<ellipse") >= 2
    # Server rack has activity LED circles
    assert svg.count("<circle") >= 2
    # Diamond and cloud have path definitions
    assert "Quality Gate" in svg
    assert "AWS Cloud" in svg


def test_shape_with_embedded_icons() -> None:
    """Verify embedded vector icons are rendered inside shapes with labels and standalone."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("sensor1", label="Vibration Sensor", icon="sensor").at(50, 50)
    s2 = Shape("gw1", label="IoT Gateway", icon="gateway").at(220, 50)
    s3 = Shape("broker1", label="MQTT Broker", icon="broker").at(390, 50)
    s4 = Shape("dash_icon", label="", icon="dashboard").at(560, 50)

    svg = renderer.render(elements=[s1, s2, s3, s4], width=800, height=300)
    ET.fromstring(svg)

    assert "icon-sensor" in svg
    assert "icon-gateway" in svg
    assert "icon-broker" in svg
    assert "icon-dashboard" in svg
    assert "Vibration Sensor" in svg


def test_edge_styles_and_colors() -> None:
    """Verify solid, dashed, dotted line styles and custom edge colors with matching arrow markers."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("s1", label="A").at(50, 50)
    s2 = Shape("s2", label="B").at(250, 50)
    s3 = Shape("s3", label="C").at(50, 180)
    s4 = Shape("s4", label="D").at(250, 180)
    s5 = Shape("s5", label="E").at(50, 310)
    s6 = Shape("s6", label="F").at(250, 310)

    e_solid = Edge(s1, s2, style="solid")
    e_dashed = Edge(s3, s4, style="dashed", color="#00E5A3")
    e_dotted = Edge(s5, s6, style="dotted", arrow_head=False, arrow_tail=True)

    svg = renderer.render(
        elements=[s1, s2, s3, s4, s5, s6],
        edges=[e_solid, e_dashed, e_dotted],
        width=500,
        height=500,
    )
    root = ET.fromstring(svg)

    # Dashed line style
    assert 'stroke-dasharray="5,5"' in svg or 'stroke-dasharray="6,4"' in svg
    # Dotted line style
    assert 'stroke-dasharray="2,2"' in svg or 'stroke-dasharray="2,3"' in svg

    # Custom color edge produces custom arrowhead marker in defs
    assert "#00E5A3" in svg
    # Arrow tail marker existence
    assert 'marker-start="url(#arrow-tail)"' in svg or 'marker-start=' in svg


def test_edge_protocol_labels_and_badges() -> None:
    """Verify protocol labels are rendered with centered badges that mask edge lines."""
    theme = get_theme("blueprint")
    renderer = SVGRenderer(theme)

    s1 = Shape("plc", label="Siemens S7-1500").at(100, 100)
    s2 = Shape("cloud", label="Industrial Cloud", kind="cloud").at(400, 100)
    edge = Edge(s1, s2, label="HTTPS / REST")

    svg = renderer.render(elements=[s1, s2], edges=[edge], width=700, height=400)
    root = ET.fromstring(svg)

    assert "HTTPS / REST" in svg
    # Badge element exists
    assert 'class="badge"' in svg


def test_special_character_escaping() -> None:
    """Verify XML entity escaping for special characters (&, <, >, quotes) in labels and ids."""
    theme = get_theme("cyber_slate")
    renderer = SVGRenderer(theme)

    g = Group("g_special", label='Plant & Fleet <Zone 1> "Core"').at(10, 10)
    s1 = Shape("node<1>", label='Sensor <Temp & Hum> "Alpha"').at(30, 60)
    s2 = Shape("node'2'", label="Gateway 'Edge' & Broker").at(250, 60)
    g.add(s1, s2)
    edge = Edge(s1, s2, label='Protocol: <JSON> & "CBOR"')

    svg = renderer.render(elements=[s1, s2], groups=[g], edges=[edge], width=600, height=300)

    # Must be 100% valid XML parseable without entity errors
    root = ET.fromstring(svg)
    assert root is not None

    # Verify escaping in raw SVG string
    assert "&amp;" in svg
    assert "&lt;" in svg
    assert "&gt;" in svg


def test_nested_groups_rendering_order() -> None:
    """Verify parent groups are rendered before child groups so nested groups aren't occluded."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    outer = Group("outer", label="Factory Site").at(10, 10)
    inner = Group("inner", label="Line 1 Workcell").at(30, 50)
    outer.add(inner)
    s = Shape("plc", label="PLC 1").at(50, 90)
    inner.add(s)

    outer.calculate_bounds()
    inner.calculate_bounds()

    svg = renderer.render(elements=[s], groups=[outer, inner], width=600, height=400)
    root = ET.fromstring(svg)

    outer_pos = svg.find('id="outer"')
    inner_pos = svg.find('id="inner"')
    assert outer_pos != -1 and inner_pos != -1
    assert outer_pos < inner_pos, "Outer group must appear before inner group in SVG DOM"


def test_empty_diagram_renders_valid_svg() -> None:
    """Verify rendering with empty collections produces valid canvas SVG."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    svg = renderer.render(elements=[], groups=[], edges=[], width=400, height=300)
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["width"] == "400"
    assert root.attrib["height"] == "300"


def test_multiple_themes_rendering() -> None:
    """Verify themes correctly apply distinct backgrounds, strokes, and font families."""
    s = Shape("node", label="Test")

    for theme_name, expected_bg in [
        ("iiot_dark_gold", "#000000"),
        ("iiot_light", "#FFFFFF"),
        ("blueprint", "#0B1E36"),
        ("cyber_slate", "#181B20"),
    ]:
        theme = get_theme(theme_name)
        renderer = SVGRenderer(theme)
        svg = renderer.render(elements=[s], width=300, height=200)
        assert f'fill="{expected_bg}"' in svg
        assert theme.font_family in svg


def test_contrast_color_calculation() -> None:
    """Verify _contrast_color with light/dark fills, 3-char shorthand, and invalid/None inputs."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    # 6-char hex light -> dark text
    assert renderer._contrast_color("#FFFFFF") == "#000000"
    assert renderer._contrast_color("#F0F0F0") == "#000000"
    assert renderer._contrast_color("#FFFF00") == "#000000"

    # 6-char hex dark -> light text
    assert renderer._contrast_color("#000000") == "#FFFFFF"
    assert renderer._contrast_color("#1A1A1E") == "#FFFFFF"
    assert renderer._contrast_color("#24242A") == "#FFFFFF"

    # 3-char hex shorthand
    assert renderer._contrast_color("#FFF") == "#000000"
    assert renderer._contrast_color("#fff") == "#000000"
    assert renderer._contrast_color("#000") == "#FFFFFF"
    assert renderer._contrast_color("#222") == "#FFFFFF"

    # Invalid and non-string inputs fallback to theme.text
    assert renderer._contrast_color(None) == theme.text
    assert renderer._contrast_color(12345) == theme.text
    assert renderer._contrast_color("invalid_hex") == theme.text
    assert renderer._contrast_color("") == theme.text
    assert renderer._contrast_color("#GGGGGG") == theme.text


def test_group_metadata_custom_fill_and_stroke() -> None:
    """Verify group fill and stroke overrides via metadata."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    g = Group(
        "custom_g",
        label="Custom Security Zone",
        metadata={"fill": "#2D3748", "stroke": "#4FD1C5"},
    ).at(10, 10)
    s = Shape("node", label="Secure Node").at(30, 40)
    g.add(s)

    svg = renderer.render(elements=[s], groups=[g], width=500, height=300)
    assert 'fill="#2D3748"' in svg
    assert 'stroke="#4FD1C5"' in svg


def test_edge_metadata_and_badge_customization() -> None:
    """Verify Edge metadata stores attributes and customizes protocol badge styling."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("a", label="A").at(50, 50)
    s2 = Shape("b", label="B").at(250, 50)
    edge = Edge(
        s1,
        s2,
        label="Custom Protocol",
        metadata={"badge_fill": "#4A5568", "badge_text_color": "#E2E8F0"},
    )
    assert edge.metadata == {"badge_fill": "#4A5568", "badge_text_color": "#E2E8F0"}

    svg = renderer.render(elements=[s1, s2], edges=[edge], width=500, height=200)
    assert 'fill="#4A5568"' in svg
    assert 'fill="#E2E8F0"' in svg


def test_text_wrapping_multiline_tspan() -> None:
    """Verify long labels wrap with <tspan> elements when rendered inside nodes."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s = Shape("s_long", label="Cloud IdP (Okta/Entra)", icon="key", width=120, height=60).at(50, 50)
    svg = renderer.render(elements=[s], width=400, height=300)
    assert "<tspan" in svg
    assert "Cloud IdP" in svg
    assert "(Okta/Entra)" in svg


def test_label_position_bottom() -> None:
    """Verify label_position='bottom' places text below the graphic tile."""
    theme = get_theme("monochrome")
    renderer = SVGRenderer(theme)

    s = Shape(
        "s_bottom",
        label="Hardware Security Key",
        icon="mobile",
        width=80,
        height=60,
        label_position="bottom",
    ).at(50, 50)
    svg = renderer.render(elements=[s], width=400, height=300)
    assert 'class="icon icon-mobile"' in svg
    assert "Hardware" in svg
    assert "Security Key" in svg
    # The text y coordinate must be strictly below the graphic tile (50 + 60 = 110)
    assert 'y="124.0"' in svg or 'y="125.0"' in svg or 'y="126.0"' in svg or 'y="128.0"' in svg



def test_kind_icon_pure_rendering() -> None:
    """Verify kind='icon' renders standalone vector icon without bounding card box."""
    theme = get_theme("cyber_slate")
    renderer = SVGRenderer(theme)

    s = Shape("s_icon", label="Border Gateway", kind="icon", icon="router").at(100, 100)
    svg = renderer.render(elements=[s], width=400, height=300)
    assert 'class="icon icon-router"' in svg
    assert "Border Gateway" in svg
    # Should NOT have card rectangle box
    assert '<rect x="100.0" y="100.0"' not in svg


def test_interactive_svg_rendering_structure() -> None:
    """Verify interactive mode includes styles, HUD controls, CDATA script, and is valid XML."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("node_a", label="Sensor A").at(50, 50)
    s2 = Shape("node_b", label="Sensor B").at(250, 50)
    e = Edge(s1, s2, label="MQTT")

    svg = renderer.render(
        elements=[s1, s2], edges=[e], width=800, height=600, interactive=True
    )

    # Strictly valid XML
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert "diagram-interactive" in root.attrib.get("class", "")

    # Script tag with CDATA and client-side logic
    assert "<script" in svg
    assert "<![CDATA[" in svg
    assert "svg-pan-zoom-controls" in svg
    assert "btn-zoom-in" in svg
    assert "btn-zoom-out" in svg
    assert "btn-zoom-reset" in svg
    assert "updateViewBox" in svg
    assert "zoomAt" in svg

    # Interactive style rules
    assert ".diagram-interactive" in svg
    assert ".group-header" in svg
    assert ".group-toggle" in svg
    assert ".hud-btn" in svg


def test_interactive_svg_collapsible_groups_and_edges() -> None:
    """Verify interactive group headers, toggle icons, hierarchy metadata, and edge group tagging."""
    theme = get_theme("cyber_slate")
    renderer = SVGRenderer(theme)

    parent_grp = Group("parent_g", label="Factory OT Network").at(20, 20)
    child_grp = Group("child_g", label="Cell Zone 1").at(40, 60)
    parent_grp.add(child_grp)

    s1 = Shape("plc1", label="PLC 1").at(60, 100)
    child_grp.add(s1)

    s2 = Shape("hmi", label="Plant HMI").at(300, 100)
    parent_grp.add(s2)

    s3 = Shape("cloud", label="AWS IoT").at(600, 100)

    e_internal = Edge(s1, s2, label="OPC-UA")
    e_external = Edge(s2, s3, label="HTTPS")

    svg = renderer.render(
        elements=[s1, s2, s3],
        groups=[parent_grp, child_grp],
        edges=[e_internal, e_external],
        width=1000,
        height=700,
        interactive=True,
    )

    # Valid XML
    ET.fromstring(svg)

    # Group attributes
    assert 'class="diagram-group"' in svg
    assert 'data-group-id="parent_g"' in svg
    assert 'data-collapsed="false"' in svg
    assert 'data-parent-group="parent_g"' in svg
    assert 'class="group-header"' in svg
    assert 'class="group-toggle"' in svg
    assert "▼" in svg

    # Shape parent tagging
    assert 'data-parent-group="child_g"' in svg
    assert 'data-parent-group="parent_g"' in svg

    # Edge group tagging
    assert 'class="diagram-edge"' in svg
    assert 'data-source-group="child_g"' in svg
    assert 'data-target-group="parent_g"' in svg
    assert 'data-source-group="parent_g"' in svg


def test_diagram_interactive_flag_and_configuration() -> None:
    """Verify Diagram(interactive=True) flows through render_svg and configure toggles."""
    from diagrams_as_code.diagram import Diagram

    d = Diagram(
        "Interactive Test",
        width=600,
        height=400,
        theme="nord_frost",
        interactive=True,
    )
    n1 = Shape("n1", label="Node 1").at(50, 50)
    n2 = Shape("n2", label="Node 2").at(250, 50)
    d.add(n1, n2, Edge(n1, n2))

    svg_interactive = d.render_svg()
    assert 'class="diagram-interactive"' in svg_interactive
    assert "svg-pan-zoom-controls" in svg_interactive
    assert "<script" in svg_interactive

    # Reconfigure to non-interactive
    d.configure(interactive=False)
    assert not d.interactive
    svg_plain = d.render_svg()
    assert 'class="diagram-interactive"' not in svg_plain
    assert "svg-pan-zoom-controls" not in svg_plain
    assert "<script" not in svg_plain


def test_interactive_svg_search_controls() -> None:
    """Verify HUD contains foreignObject search input, styles, and applySearch script."""
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)

    s1 = Shape("node_a", label="Sensor Alpha").at(50, 50)
    s2 = Shape("node_b", label="Gateway Beta").at(250, 50)
    e = Edge(s1, s2, label="MQTT")

    svg = renderer.render(elements=[s1, s2], edges=[e], width=800, height=600, interactive=True)

    # Valid XML parse
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"

    # Search input element & foreignObject
    assert "foreignObject" in svg
    assert 'id="diagram-search-input"' in svg
    assert 'placeholder="Search..."' in svg
    assert "#diagram-search-input" in svg

    # Script contains search filtering logic
    assert "applySearch" in svg
    assert "diagram-node" in svg
    assert "matchedNodeIds" in svg
    assert "Escape" in svg


def test_interactive_svg_node_and_edge_search_metadata() -> None:
    """Verify shapes and edges contain node IDs, labels, and source/target IDs in interactive mode."""
    theme = get_theme("cyber_slate")
    renderer = SVGRenderer(theme)

    grp = Group("g1", label="Control Zone").at(20, 20)
    s1 = Shape("plc1", label="PLC Alpha").at(50, 60)
    s2 = Shape("scada1", label="SCADA Beta").at(250, 60)
    grp.add(s1)
    e = Edge(s1, s2, label="OPC-UA")

    svg_interactive = renderer.render(
        elements=[s1, s2], groups=[grp], edges=[e], width=800, height=600, interactive=True
    )
    ET.fromstring(svg_interactive)

    # Node metadata
    assert 'class="diagram-node"' in svg_interactive
    assert 'data-node-id="plc1"' in svg_interactive
    assert 'data-label="PLC Alpha"' in svg_interactive
    assert 'data-node-id="scada1"' in svg_interactive
    assert 'data-label="SCADA Beta"' in svg_interactive

    # Edge metadata
    assert 'data-source-id="plc1"' in svg_interactive
    assert 'data-target-id="scada1"' in svg_interactive

    # Group metadata
    assert 'data-label="Control Zone"' in svg_interactive

    # Non-interactive mode must not leak interactive attributes
    svg_plain = renderer.render(
        elements=[s1, s2], groups=[grp], edges=[e], width=800, height=600, interactive=False
    )
    assert 'id="diagram-search-input"' not in svg_plain
    assert 'class="diagram-node"' not in svg_plain
    assert 'data-node-id=' not in svg_plain
    assert 'data-source-id=' not in svg_plain





