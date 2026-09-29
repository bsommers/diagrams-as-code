"""Comprehensive End-to-End (E2E) Test Suite for IIoT Diagrams-as-Code.

Verifies:
1. Decoupled shape definition, late placement, move_to, translate, and clone().
2. UnitBasis coordinate mapping (fractional floats and percentage strings).
3. Group auto-bounding and group-to-group flow placement (below, right_of, align).
4. Directed orthogonal routing with custom ports and protocol badges.
5. Living documentation: BOM table, connections table, JSON export, README generation.
6. Dynamic theme switching (dark gold vs light).
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from iiot_diagrams import (
    Diagram,
    Edge,
    Group,
    PathKind,
    Point,
    Port,
    Rect,
    Routing,
    Shape,
    Size,
    UnitBasis,
    get_theme,
)


def test_e2e_decoupled_shape_definition_cloning_and_relocation() -> None:
    """Shapes can be defined without location, cloned as templates, added later, and relocated."""
    # 1. Define decoupled shape templates outside of any diagram context
    sensor_template = Shape(
        "tpl_sensor",
        "Sensor Template",
        width=120.0,
        height=60.0,
        kind="box",
        icon="sensor",
        metadata={"category": "Field Sensor", "tier": "L1"},
    )
    gateway_template = Shape(
        "tpl_gateway",
        "Gateway Template",
        width=140.0,
        height=65.0,
        kind="box",
        icon="gateway",
        metadata={"category": "Edge Gateway", "tier": "L2"},
    )

    # Initial shapes have default bounds at origin with no diagram attached
    assert sensor_template.bounds == Rect(0.0, 0.0, 120.0, 60.0)
    assert sensor_template._diagram is None

    # 2. Clone from templates with customized properties
    s1 = sensor_template.clone("temp_sensor_1", label="Temperature Sensor")
    s2 = sensor_template.clone("press_sensor_1", label="Pressure Sensor")
    gw = gateway_template.clone("edge_gw_1", label="Plant Edge Gateway")

    assert s1.id == "temp_sensor_1"
    assert s1.label == "Temperature Sensor"
    assert s1.metadata["tier"] == "L1"
    assert gw.id == "edge_gw_1"
    assert gw.kind == "box"

    # 3. Instantiate diagram and add cloned elements
    diag = Diagram("Decoupled Architecture", width=1000.0, height=600.0)
    diag.add(s1, s2, gw)

    # Elements now associated with diagram
    assert s1._diagram is diag
    assert gw._diagram is diag

    # 4. Apply late placement constraints
    s1.at(100.0, 120.0)
    s2.below(s1, margin=40.0)
    gw.right_of(s1, margin=150.0, align="center")

    diag.solve()

    assert s1.bounds.x == 100.0
    assert s1.bounds.y == 120.0
    assert s2.bounds.x == 100.0
    assert s2.bounds.y == 120.0 + 60.0 + 40.0  # 220.0
    assert gw.bounds.left == s1.bounds.right + 150.0  # 100 + 120 + 150 = 370.0
    assert gw.bounds.center.y == s1.bounds.center.y  # 120 + 30 = 150.0

    # 5. Relocate shape via move_to (clears constraints and sets new absolute position)
    s1.move_to(200.0, 250.0)
    diag.solve()

    assert s1.bounds.x == 200.0
    assert s1.bounds.y == 250.0
    # s2 and gw automatically track s1's new position
    assert s2.bounds.x == 200.0
    assert s2.bounds.y == 250.0 + 60.0 + 40.0  # 350.0
    assert gw.bounds.left == 200.0 + 120.0 + 150.0  # 470.0

    # 6. Relocate shape via translate
    s1.translate(50.0, -30.0)
    assert s1.bounds.x == 250.0
    assert s1.bounds.y == 220.0


def test_e2e_unit_basis_coordinates() -> None:
    """Canvas unit-basis converts fractional floats and percentage strings to absolute pixels."""
    diag = Diagram("Unit Basis Diagram", width=1600.0, height=800.0)
    ub = diag.unit_basis
    assert ub.canvas_size == Size(1600.0, 800.0)

    # Fractional float coordinates
    pt_quarter = ub.to_absolute(0.25, 0.50)
    assert pt_quarter.x == 400.0
    assert pt_quarter.y == 400.0

    # Percentage string coordinates
    pt_pct = ub.to_absolute("75%", "25%")
    assert pt_pct.x == 1200.0
    assert pt_pct.y == 200.0

    # Position elements using unit-basis coordinates
    with diag:
        s1 = diag.shape("Northwest Node").at(pt_quarter.x, pt_quarter.y)
        s2 = diag.shape("Northeast Node").at(pt_pct.x, pt_pct.y)
        pt_center = ub.to_absolute("50%", "50%")
        s3 = diag.shape("Central Switch").at(pt_center.x, pt_center.y)

    assert s1.bounds.x == 400.0
    assert s1.bounds.y == 400.0
    assert s2.bounds.x == 1200.0
    assert s2.bounds.y == 200.0
    assert s3.bounds.x == 800.0
    assert s3.bounds.y == 400.0


def test_e2e_group_auto_bounding_and_flow_placement() -> None:
    """Groups calculate bounds enclosing children, and groups can be placed relative to other groups."""
    diag = Diagram("Group Flow Layout", width=1400.0, height=900.0)

    with diag:
        # Group 1: Plant Site 1
        with diag.group("Plant Site 1", padding=25.0, header_height=35.0) as g1:
            s1 = diag.shape("PLC 1", width=120.0, height=60.0).at(100.0, 100.0)
            s2 = diag.shape("PLC 2", width=120.0, height=60.0).below(s1, margin=30.0)

        # Group 2: Plant Site 2 positioned below Group 1
        with diag.group("Plant Site 2", padding=25.0, header_height=35.0) as g2:
            s3 = diag.shape("PLC 3", width=120.0, height=60.0)
            s4 = diag.shape("PLC 4", width=120.0, height=60.0).below(s3, margin=30.0)

        g2.below(g1, margin=40.0, align="left")

        # Group 3: Central UNS positioned right of Group 1
        with diag.group("Central UNS", padding=30.0, header_height=40.0) as g3:
            broker = diag.shape("Broker Cluster", width=160.0, height=80.0)

        g3.right_of(g1, margin=80.0, align="top")

    # Assert Group 1 bounds:
    # Children span x: 100..220 (w=120), y: 100..250 (h=150)
    # With padding 25 (top + bottom = 50) and header 35: x: 75, y: 40, w: 170, h: 235
    assert g1.bounds.x == 75.0
    assert g1.bounds.y == 40.0
    assert g1.bounds.width == 170.0
    assert g1.bounds.height == 235.0

    # Assert Group 2 below Group 1:
    assert g2.bounds.top == g1.bounds.bottom + 40.0  # 275 + 40 = 315.0
    assert g2.bounds.left == g1.bounds.left  # 75.0

    # Children of Group 2 translated with group:
    assert s3.bounds.x == g2.bounds.x + 25.0  # padding
    assert s3.bounds.y == g2.bounds.y + 25.0 + 35.0  # padding + header

    assert g3.bounds.left == g1.bounds.right + 80.0  # 245 + 80 = 325.0
    assert g3.bounds.top == g1.bounds.top  # 40.0


def test_e2e_directed_orthogonal_routing_with_ports_and_badges() -> None:
    """Orthogonal router computes Manhattan waypoints with custom ports and protocol badges."""
    diag = Diagram("Routing Showcase", width=1000.0, height=600.0)

    with diag:
        n1 = diag.shape("Publisher", width=120.0, height=60.0).at(100.0, 100.0)
        n2 = diag.shape("Subscriber", width=120.0, height=60.0).at(400.0, 250.0)

        # East to West with protocol badge
        n1 >> diag.edge(
            label="spBv1.0 Payload",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> n2

        # Direct feedback link with South to North
        n2 >> diag.edge(
            label="ACK Telemetry",
            source_port=Port.NORTH,
            target_port=Port.SOUTH,
            routing=Routing.ORTHOGONAL,
        ) >> n1

    svg_content = diag.render_svg()
    root = ET.fromstring(svg_content)
    assert root.tag.endswith("svg")

    # Verify edge paths rendered
    paths = root.findall(".//{http://www.w3.org/2000/svg}path")
    assert len(paths) >= 2

    # Verify protocol badges rendered with text
    badge_texts = [
        elem.text
        for elem in root.findall(".//{http://www.w3.org/2000/svg}text")
        if elem.text in ("spBv1.0 Payload", "ACK Telemetry")
    ]
    assert "spBv1.0 Payload" in badge_texts
    assert "ACK Telemetry" in badge_texts

    # Verify badge background pill rects exist
    assert '<g class="badge">' in svg_content


def test_e2e_living_documentation_bom_tables_and_json(tmp_path: Path) -> None:
    """Extract inventory BOM, connections table, export JSON, and generate Markdown README."""
    diag = Diagram("Complete Factory Architecture", width=1200.0, height=800.0)

    with diag:
        with diag.group("Cell 1") as cell:
            plc = diag.shape(
                "Cell PLC",
                kind="box",
                icon="sensor",
                metadata={"vendor": "Siemens", "part_no": "6ES7515-2AM02-0AB0"},
            ).at(100.0, 100.0)
            edge = diag.shape(
                "Cell Gateway",
                kind="box",
                icon="gateway",
                metadata={"vendor": "Advantech", "model": "UNO-2484G"},
            ).below(plc, margin=60.0)

            plc >> diag.edge(label="Profinet", source_port="south", target_port="north") >> edge

        broker = diag.shape(
            "MQTT Broker",
            kind="server_rack",
            icon="broker",
            metadata={"cluster": "3-node", "license": "Enterprise"},
        ).right_of(cell, margin=100.0, align="center")

        edge >> diag.edge(label="MQTT TLS", source_port="east", target_port="west") >> broker

    # 1. Component inventory verification
    items = diag.bom.items()
    assert len(items) == 3
    plc_item = next(it for it in items if it["id"] == plc.id)
    assert plc_item["label"] == "Cell PLC"
    assert plc_item["group"] == "Cell 1"
    assert plc_item["metadata"]["vendor"] == "Siemens"

    # 2. Connection inventory verification
    conns = diag.bom.connections()
    assert len(conns) == 2
    profinet_conn = next(c for c in conns if c["protocol"] == "Profinet")
    assert profinet_conn["source"] == plc.id
    assert profinet_conn["target"] == edge.id
    assert profinet_conn["source_port"] == "south"
    assert profinet_conn["target_port"] == "north"

    # 3. JSON serialization
    bom_json = diag.bom.to_json()
    bom_dict = json.loads(bom_json)
    assert bom_dict["title"] == "Complete Factory Architecture"
    assert bom_dict["total_components"] == 3
    assert bom_dict["total_connections"] == 2
    assert len(bom_dict["groups"]) == 1

    # 4. Markdown README generation
    readme_file = tmp_path / "README.md"
    content = diag.generate_readme("factory_diag.svg", output_path=readme_file)
    assert readme_file.exists()
    assert "# Complete Factory Architecture" in content
    assert "![Architecture Diagram](./factory_diag.svg)" in content
    assert "## Bill of Materials" in content
    assert "## Connections" in content
    assert "6ES7515-2AM02-0AB0" in content
    assert "Profinet" in content


def test_e2e_theme_switching_dark_gold_and_light() -> None:
    """Diagram can be rendered in dark gold theme and switched to light theme."""
    diag = Diagram("Themed Architecture", width=800.0, height=500.0, theme="iiot_dark_gold")

    with diag:
        s1 = diag.shape("Node A", kind="box").at(100.0, 100.0)
        s2 = diag.shape("Node B", kind="cylinder").right_of(s1, margin=80.0)
        s1 >> diag.edge(label="HTTPS") >> s2

    # Verify Dark Gold theme colors
    svg_dark = diag.render_svg()
    assert diag.theme.name == "iiot_dark_gold"
    assert diag.theme.background == "#000000"
    assert '<rect width="100%" height="100%" fill="#000000"/>' in svg_dark

    # Switch theme to IIoT Light
    diag.theme = get_theme("iiot_light")
    assert diag.theme.name == "iiot_light"
    assert diag.theme.background == "#FFFFFF"

    svg_light = diag.render_svg()
    assert '<rect width="100%" height="100%" fill="#FFFFFF"/>' in svg_light
    assert svg_dark != svg_light

    # Parse both SVGs to ensure valid XML in both themes
    root_dark = ET.fromstring(svg_dark)
    root_light = ET.fromstring(svg_light)
    assert root_dark.tag.endswith("svg")
    assert root_light.tag.endswith("svg")


def test_e2e_obstacle_avoidance_with_corner_fillets() -> None:
    """Verify obstacle detour path receives rounded corner fillets with apex clearance >= 4.0px."""
    import math
    import re
    from diagrams_as_code.geometry import Point, QuadraticBezier

    diag = Diagram("Obstacle Detour Fillets", width=800.0, height=400.0)
    with diag:
        s = diag.shape("Source", width=80.0, height=50.0).at(50.0, 100.0)
        t = diag.shape("Target", width=80.0, height=50.0).at(400.0, 100.0)
        obs = diag.shape("Obstacle", width=100.0, height=80.0).at(200.0, 70.0)
        edge = diag.connect(s, t, routing=Routing.ORTHOGONAL, corner_radius=12.0)

    # Waypoints must detour around obstacle (more than 2 points)
    assert edge.waypoints is not None
    assert len(edge.waypoints) > 2

    # Render to SVG
    svg_content = diag.render_svg()
    root = ET.fromstring(svg_content)
    assert root.tag.endswith("svg")

    # Find edge path
    ns = {"svg": "http://www.w3.org/2000/svg"}
    paths = [p for p in root.findall(".//svg:path", ns) if "marker-end" in p.attrib]
    assert len(paths) == 1
    path_d = paths[0].attrib["d"]

    # Verify Q commands exist for each 90-degree detour corner
    num_corners = len(edge.waypoints) - 2
    q_matches = re.findall(r"L\s+([\d.]+)\s+([\d.]+)\s+Q\s+([\d.]+)\s+([\d.]+),\s+([\d.]+)\s+([\d.]+)", path_d)
    assert len(q_matches) == num_corners
    assert path_d.count(" Q ") == num_corners

    # Verify fillet apex maintains >= 4.0px clearance margin from obstacle
    obs_bounds = obs.bounds
    for match in q_matches:
        p0_x, p0_y, ctrl_x, ctrl_y, p2_x, p2_y = map(float, match)
        q = QuadraticBezier(Point(p0_x, p0_y), Point(ctrl_x, ctrl_y), Point(p2_x, p2_y))
        apex = q.point_at(0.5)

        # Distance from apex to obstacle bounding box
        dx = max(0.0, obs_bounds.left - apex.x, apex.x - obs_bounds.right)
        dy = max(0.0, obs_bounds.top - apex.y, apex.y - obs_bounds.bottom)
        clearance = math.hypot(dx, dy)
        assert clearance >= 4.0, f"Apex {apex} has clearance {clearance}px < 4.0px from obstacle {obs_bounds}"


def test_e2e_curved_obstacle_avoidance_single_and_wide() -> None:
    """E2E verification of compact and wide obstacle avoidance for curved routing (CURVEOBS-01, CURVEOBS-02)."""
    with Diagram("Curved Avoidance", width=1200.0, height=800.0) as diag:
        # Pair 1: Compact obstacle (width 20px <= 2 * 15px)
        s1 = diag.shape("Source 1", width=80.0, height=50.0).at(50.0, 100.0)
        t1 = diag.shape("Target 1", width=80.0, height=50.0).at(450.0, 100.0)
        obs_c = diag.shape("Compact Obstacle", width=20.0, height=60.0).at(250.0, 95.0)
        e1 = diag.connect(s1, t1, label="COMPACT_CORR", routing=Routing.CURVE)

        # Pair 2: Wide obstacle (width 120px > 2 * 15px)
        s2 = diag.shape("Source 2", width=80.0, height=50.0).at(50.0, 400.0)
        t2 = diag.shape("Target 2", width=80.0, height=50.0).at(550.0, 400.0)
        obs_w = diag.shape("Wide Obstacle", width=120.0, height=60.0).at(240.0, 395.0)
        e2 = diag.connect(s2, t2, label="WIDE_CORR", routing=Routing.CURVE)

    # 1. Compact obstacle verification
    assert e1.waypoints is not None
    assert len(e1.waypoints) == 7  # 1 apex waypoint (2 segments)
    w_apex = e1.waypoints[3]
    # Deflected by >= 15.0px clearance from obstacle bounds
    assert w_apex.y <= obs_c.bounds.top - 15.0 or w_apex.y >= obs_c.bounds.bottom + 15.0

    # 2. Wide obstacle verification
    assert e2.waypoints is not None
    assert len(e2.waypoints) == 10  # 2 corner waypoints (3 segments)
    w1, w2 = e2.waypoints[3], e2.waypoints[6]
    corners_w = [
        Point(obs_w.bounds.left, obs_w.bounds.top),
        Point(obs_w.bounds.right, obs_w.bounds.top),
        Point(obs_w.bounds.left, obs_w.bounds.bottom),
        Point(obs_w.bounds.right, obs_w.bounds.bottom),
    ]
    for c in corners_w:
        assert w1.distance_to(c) >= 15.0
        assert w2.distance_to(c) >= 15.0

    # 3. SVG rendering & XML verification
    svg = diag.render_svg()
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")

    ns = {"svg": "http://www.w3.org/2000/svg"}
    paths = [p for p in root.findall(".//svg:path", ns) if "marker-end" in p.attrib]
    assert len(paths) == 2

    # Verify both paths contain chained C commands
    for path in paths:
        d = path.attrib["d"]
        assert d.startswith("M ")
        assert " C " in d
        assert " L " not in d


def test_e2e_curved_reverse_flow_escape_routing() -> None:
    """E2E verification of reverse-flow escape routing for curved edges (D-13..D-15, CURVEOBS-03)."""
    with Diagram("Reverse Flow Escape", width=800.0, height=600.0) as diag:
        # Source at right: x=400, Target at left: x=100
        src = diag.shape("Producer", width=100.0, height=50.0).at(400.0, 200.0)
        tgt = diag.shape("Consumer", width=100.0, height=50.0).at(100.0, 200.0)
        # Reverse flow edge with automatic port resolution
        e_auto = diag.connect(src, tgt, routing=Routing.CURVE)

        # Reverse flow edge with explicit ports
        src2 = diag.shape("Producer 2", width=100.0, height=50.0).at(400.0, 400.0)
        tgt2 = diag.shape("Consumer 2", width=100.0, height=50.0).at(100.0, 400.0)
        e_expl = diag.connect(
            src2,
            tgt2,
            source_port=Port.EAST,
            target_port=Port.WEST,
            routing=Routing.CURVE,
        )

    # 1. Automatic back-edge port resolution: NORTH/NORTH or SOUTH/SOUTH (D-14)
    from diagrams_as_code.router import CurveRouter
    router = CurveRouter()
    ports_auto = router.resolve_ports(e_auto, obstacles=[src, tgt])
    assert ports_auto in ((Port.NORTH, Port.NORTH), (Port.SOUTH, Port.SOUTH))

    # 2. Explicit ports: outer lateral clearance corridor >= 30.0px (D-13, D-15)
    assert e_expl.waypoints is not None
    assert len(e_expl.waypoints) == 10  # 3 segments
    w_esc1, w_esc2 = e_expl.waypoints[3], e_expl.waypoints[6]
    # Lateral extension >= 30.0px beyond boundaries
    assert w_esc1.x >= src2.bounds.right + 30.0
    assert w_esc2.x <= tgt2.bounds.left - 30.0

    # 3. Verify disjoint bounding boxes: no bow-tie self-intersection (T-10-04)
    from diagrams_as_code.geometry import CubicBezier
    seg1 = CubicBezier(e_expl.waypoints[0], e_expl.waypoints[1], e_expl.waypoints[2], e_expl.waypoints[3])
    seg3 = CubicBezier(e_expl.waypoints[6], e_expl.waypoints[7], e_expl.waypoints[8], e_expl.waypoints[9])
    assert not seg1.bbox().intersects(seg3.bbox())

    # 4. XML parse validity
    svg = diag.render_svg()
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")


def test_e2e_mixed_orthogonal_and_curved_routing_with_obstacles() -> None:
    """E2E verification of orthogonal filleted and curved edges coexisting on the same canvas (FILLET-01, CURVEOBS-01)."""
    with Diagram("Mixed Routing", width=900.0, height=600.0) as diag:
        s1 = diag.shape("Source A", width=80.0, height=50.0).at(50.0, 100.0)
        t1 = diag.shape("Target A", width=80.0, height=50.0).at(450.0, 100.0)
        obs1 = diag.shape("Obs A", width=100.0, height=60.0).at(220.0, 95.0)

        s2 = diag.shape("Source B", width=80.0, height=50.0).at(50.0, 350.0)
        t2 = diag.shape("Target B", width=80.0, height=50.0).at(450.0, 350.0)
        obs2 = diag.shape("Obs B", width=100.0, height=60.0).at(220.0, 345.0)

        # Curved edge around obs1
        e_curve = diag.connect(s1, t1, label="CURVE_EDGE", routing=Routing.CURVE)
        # Orthogonal filleted edge around obs2
        e_ortho = diag.connect(
            s2, t2, label="ORTHO_EDGE", routing=Routing.ORTHOGONAL, corner_radius=12.0
        )

    svg = diag.render_svg()
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")

    ns = {"svg": "http://www.w3.org/2000/svg"}
    paths = [p for p in root.findall(".//svg:path", ns) if "marker-end" in p.attrib]
    assert len(paths) == 2

    path_ds = [p.attrib["d"] for p in paths]
    # One path has Q commands (orthogonal filleted)
    has_q = any(" Q " in d for d in path_ds)
    # One path has chained C commands (curved multi-segment)
    has_c = any(" C " in d for d in path_ds)
    assert has_q, "Expected at least one orthogonal path with Q fillet commands"
    assert has_c, "Expected at least one curved path with C bezier commands"

    # Both badges are rendered and readable
    badges = [r for r in root.findall(".//svg:rect", ns) if r.attrib.get("rx") == "9.0"]
    assert len(badges) == 2


def test_e2e_fluent_chain_inherits_diagram_curved_routing() -> None:
    with Diagram(routing="curve") as d:
        s1 = d.shape("Sensor 1")
        s2 = d.shape("Sensor 2")
        s3 = d.shape("Gateway")
        s1 >> s3
        s2 >> s3

    assert len(d.edges) == 2
    for e in d.edges:
        assert e.routing == Routing.CURVE
        path = d.routes[e]
        assert path.kind == PathKind.BEZIER_CHAIN

    svg = d.render_svg()
    assert 'd="M' in svg
    assert "C " in svg



