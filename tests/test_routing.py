from __future__ import annotations

import pytest

from iiot_diagrams import (
    Anchor,
    Edge,
    Element,
    Group,
    OrthogonalRouter,
    Point,
    Port,
    Rect,
    Routing,
    Shape,
)


def test_package_exports() -> None:
    """Verify connections and routing entities are re-exported in iiot_diagrams."""
    import iiot_diagrams

    assert hasattr(iiot_diagrams, "Port")
    assert hasattr(iiot_diagrams, "Routing")
    assert hasattr(iiot_diagrams, "Edge")
    assert hasattr(iiot_diagrams, "OrthogonalRouter")
    assert "Port" in iiot_diagrams.__all__
    assert "Routing" in iiot_diagrams.__all__
    assert "Edge" in iiot_diagrams.__all__
    assert "OrthogonalRouter" in iiot_diagrams.__all__


def test_port_enum_values_and_anchor_mapping() -> None:
    """Verify Port enum values and anchor mapping."""
    assert Port.NORTH.value == "north"
    assert Port.SOUTH.value == "south"
    assert Port.EAST.value == "east"
    assert Port.WEST.value == "west"

    assert Port.NORTH.to_anchor() == Anchor.TOP_CENTER
    assert Port.SOUTH.to_anchor() == Anchor.BOTTOM_CENTER
    assert Port.EAST.to_anchor() == Anchor.RIGHT_CENTER
    assert Port.WEST.to_anchor() == Anchor.LEFT_CENTER


def test_routing_enum_values() -> None:
    """Verify Routing enum values."""
    assert Routing.DIRECT.value == "direct"
    assert Routing.ORTHOGONAL.value == "orthogonal"
    assert Routing.CURVE.value == "curve"


def test_edge_initialization_defaults_and_attributes() -> None:
    """Verify Edge default attributes and custom property storage."""
    s1 = Shape("s1", "Source", 100, 50).at(0, 0)
    s2 = Shape("s2", "Target", 100, 50).at(200, 0)

    edge = Edge(s1, s2)
    assert edge.source is s1
    assert edge.target is s2
    assert edge.label == ""
    assert edge.color is None
    assert edge.style == "solid"
    assert edge.source_port is None
    assert edge.target_port is None
    assert edge.arrow_head is True
    assert edge.arrow_tail is False
    assert edge.routing == Routing.ORTHOGONAL


def test_edge_custom_attributes_and_type_coercion() -> None:
    """Verify Edge accepts custom attributes and coerces string enums."""
    s1 = Shape("s1", "Source", 100, 50).at(0, 0)
    s2 = Shape("s2", "Target", 100, 50).at(200, 0)

    edge = Edge(
        source=s1,
        target=s2,
        label="Telemetry",
        color="#FFC000",
        style="dashed",
        source_port="east",
        target_port="west",
        arrow_head=False,
        arrow_tail=True,
        routing="curve",
    )
    assert edge.label == "Telemetry"
    assert edge.color == "#FFC000"
    assert edge.style == "dashed"
    assert edge.source_port == Port.EAST
    assert edge.target_port == Port.WEST
    assert edge.arrow_head is False
    assert edge.arrow_tail is True
    assert edge.routing == Routing.CURVE


def test_edge_type_validation() -> None:
    """Verify Edge raises TypeError on invalid source, target, or enum values."""
    s1 = Shape("s1", "A", 100, 50)

    with pytest.raises(TypeError, match="source must be an Element"):
        Edge("invalid_source", s1)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="target must be an Element"):
        Edge(s1, 123)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        Edge(s1, s1, source_port="invalid_port")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        Edge(s1, s1, routing="unknown_routing")  # type: ignore[arg-type]


def test_brief_automatic_port_selection() -> None:
    """Verify automatic port selection from brief."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 0)
    edge = Edge(s1, s2, label="MQTT")
    router = OrthogonalRouter()
    ports = router.resolve_ports(edge)
    assert ports == (Port.EAST, Port.WEST)


def test_brief_orthogonal_manhattan_waypoints() -> None:
    """Verify orthogonal Manhattan waypoints calculation from brief."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 150)
    edge = Edge(s1, s2)
    router = OrthogonalRouter()
    waypoints = router.route(edge)
    assert len(waypoints) >= 3
    assert waypoints[0] == s1.bounds.get_anchor(Port.EAST.to_anchor())
    assert waypoints[-1] == s2.bounds.get_anchor(Port.WEST.to_anchor())


def test_port_resolution_horizontal() -> None:
    """Verify port resolution when elements are horizontally separated."""
    router = OrthogonalRouter()

    # Target strictly to right
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 0)
    assert router.resolve_ports(Edge(s1, s2)) == (Port.EAST, Port.WEST)

    # Target strictly to left
    s3 = Shape("s3", "C", 100, 50).at(200, 0)
    s4 = Shape("s4", "D", 100, 50).at(0, 0)
    assert router.resolve_ports(Edge(s3, s4)) == (Port.WEST, Port.EAST)


def test_port_resolution_vertical() -> None:
    """Verify port resolution when elements are vertically separated."""
    router = OrthogonalRouter()

    # Target strictly below
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(0, 200)
    assert router.resolve_ports(Edge(s1, s2)) == (Port.SOUTH, Port.NORTH)

    # Target strictly above
    s3 = Shape("s3", "C", 100, 50).at(0, 200)
    s4 = Shape("s4", "D", 100, 50).at(0, 0)
    assert router.resolve_ports(Edge(s3, s4)) == (Port.NORTH, Port.SOUTH)


def test_port_resolution_diagonal() -> None:
    """Verify port resolution on diagonal relative placements based on dominance."""
    router = OrthogonalRouter()

    # dx dominant (dx=300 > dy=100)
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 100)
    assert router.resolve_ports(Edge(s1, s2)) == (Port.EAST, Port.WEST)

    # dy dominant (dy=300 > dx=100)
    s3 = Shape("s3", "C", 100, 50).at(0, 0)
    s4 = Shape("s4", "D", 100, 50).at(100, 300)
    assert router.resolve_ports(Edge(s3, s4)) == (Port.SOUTH, Port.NORTH)

    # dx == dy diagonal tie-breaker (|dx| >= |dy| selects horizontal)
    s5 = Shape("s5", "E", 100, 50).at(0, 0)
    s6 = Shape("s6", "F", 100, 50).at(200, 200)
    assert router.resolve_ports(Edge(s5, s6)) == (Port.EAST, Port.WEST)


def test_port_resolution_explicit_ports() -> None:
    """Verify explicit port overrides take precedence."""
    router = OrthogonalRouter()
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 0)

    # Both explicit
    edge_both = Edge(s1, s2, source_port=Port.NORTH, target_port=Port.SOUTH)
    assert router.resolve_ports(edge_both) == (Port.NORTH, Port.SOUTH)

    # Source explicit, target auto
    edge_src = Edge(s1, s2, source_port=Port.NORTH)
    assert router.resolve_ports(edge_src) == (Port.NORTH, Port.WEST)

    # Target explicit, source auto
    edge_tgt = Edge(s1, s2, target_port=Port.SOUTH)
    assert router.resolve_ports(edge_tgt) == (Port.EAST, Port.SOUTH)


def test_manhattan_routing_horizontal_pair_waypoints() -> None:
    """Verify exact Manhattan waypoints for horizontal port pair."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 100)
    edge = Edge(s1, s2)
    router = OrthogonalRouter()
    waypoints = router.route(edge)

    # s1 East: (100, 25); s2 West: (200, 125); mid_x = 150
    expected = [
        Point(100.0, 25.0),
        Point(150.0, 25.0),
        Point(150.0, 125.0),
        Point(200.0, 125.0),
    ]
    assert waypoints == expected
    assert waypoints[0].y == waypoints[1].y  # Segment 1: horizontal
    assert waypoints[1].x == waypoints[2].x  # Segment 2: vertical
    assert waypoints[2].y == waypoints[3].y  # Segment 3: horizontal


def test_manhattan_routing_vertical_pair_waypoints() -> None:
    """Verify exact Manhattan waypoints for vertical port pair."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(100, 200)
    edge = Edge(s1, s2)
    router = OrthogonalRouter()
    waypoints = router.route(edge)

    # s1 South: (50, 50); s2 North: (150, 200); mid_y = 125
    expected = [
        Point(50.0, 50.0),
        Point(50.0, 125.0),
        Point(150.0, 125.0),
        Point(150.0, 200.0),
    ]
    assert waypoints == expected
    assert waypoints[0].x == waypoints[1].x  # Segment 1: vertical
    assert waypoints[1].y == waypoints[2].y  # Segment 2: horizontal
    assert waypoints[2].x == waypoints[3].x  # Segment 3: vertical


def test_manhattan_routing_perpendicular_ports() -> None:
    """Verify Manhattan waypoints for orthogonal corner routing with perpendicular ports."""
    router = OrthogonalRouter()

    # Horizontal exit (EAST), Vertical entry (NORTH)
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 100)
    edge1 = Edge(s1, s2, source_port=Port.EAST, target_port=Port.NORTH)
    pts1 = router.route(edge1)
    # s1 East: (100, 25); s2 North: (250, 100); corner: (250, 25)
    assert pts1 == [Point(100.0, 25.0), Point(250.0, 25.0), Point(250.0, 100.0)]
    assert pts1[0].y == pts1[1].y
    assert pts1[1].x == pts1[2].x

    # Vertical exit (SOUTH), Horizontal entry (WEST)
    edge2 = Edge(s1, s2, source_port=Port.SOUTH, target_port=Port.WEST)
    pts2 = router.route(edge2)
    # s1 South: (50, 50); s2 West: (200, 125); corner: (50, 125)
    assert pts2 == [Point(50.0, 50.0), Point(50.0, 125.0), Point(200.0, 125.0)]
    assert pts2[0].x == pts2[1].x
    assert pts2[1].y == pts2[2].y


def test_direct_routing() -> None:
    """Verify DIRECT routing returns direct source-to-target anchor line."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 100)
    edge = Edge(s1, s2, routing=Routing.DIRECT)
    router = OrthogonalRouter()
    waypoints = router.route(edge)
    assert len(waypoints) == 2
    assert waypoints[0] == Point(100.0, 25.0)
    assert waypoints[1] == Point(200.0, 125.0)


def test_routing_with_groups() -> None:
    """Verify Edge and OrthogonalRouter operate seamlessly with Group containers."""
    g1 = Group("g1", "Plant Group", padding=20.0).at(0.0, 0.0)
    s1 = Shape("s1", "Controller", 100, 50).at(20, 40)
    g1.add(s1)
    g1.calculate_bounds()

    assert g1.bounds.left == 0.0
    assert g1.bounds.top == -15.0
    assert g1.bounds.right == 140.0
    assert g1.bounds.bottom == 110.0

    s2 = Shape("s2", "Cloud Gateway", 100, 50).at(400, 0)
    edge = Edge(g1, s2, label="OPC UA")

    router = OrthogonalRouter()
    ports = router.resolve_ports(edge)
    assert ports == (Port.EAST, Port.WEST)
    waypoints = router.route(edge)
    assert len(waypoints) == 4
    assert waypoints[0] == g1.bounds.get_anchor(Port.EAST.to_anchor())
    assert waypoints[-1] == s2.bounds.get_anchor(Port.WEST.to_anchor())


def test_collinear_straight_line_simplification() -> None:
    """Verify collinear horizontal or vertical alignment simplifies to 2 points."""
    router = OrthogonalRouter()

    # Perfectly aligned horizontally
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 0)
    edge_h = Edge(s1, s2)
    waypoints_h = router.route(edge_h)
    assert len(waypoints_h) == 2
    assert waypoints_h[0] == Point(100.0, 25.0)
    assert waypoints_h[1] == Point(300.0, 25.0)

    # Perfectly aligned vertically
    s3 = Shape("s3", "C", 100, 50).at(0, 0)
    s4 = Shape("s4", "D", 100, 50).at(0, 300)
    edge_v = Edge(s3, s4)
    waypoints_v = router.route(edge_v)
    assert len(waypoints_v) == 2
    assert waypoints_v[0] == Point(50.0, 50.0)
    assert waypoints_v[1] == Point(50.0, 300.0)

