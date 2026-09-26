from __future__ import annotations

import pytest

from iiot_diagrams import (
    Anchor,
    CurveRouter,
    Edge,
    EdgeRouter,
    Element,
    Group,
    OrthogonalRouter,
    Point,
    Port,
    PORT_NORMALS,
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
    assert hasattr(iiot_diagrams, "CurveRouter")
    assert hasattr(iiot_diagrams, "EdgeRouter")
    assert hasattr(iiot_diagrams, "PORT_NORMALS")
    assert "Port" in iiot_diagrams.__all__
    assert "Routing" in iiot_diagrams.__all__
    assert "Edge" in iiot_diagrams.__all__
    assert "OrthogonalRouter" in iiot_diagrams.__all__
    assert "CurveRouter" in iiot_diagrams.__all__
    assert "EdgeRouter" in iiot_diagrams.__all__
    assert "PORT_NORMALS" in iiot_diagrams.__all__


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


def test_segment_intersects_rect() -> None:
    """Verify orthogonal segment intersection against rectangle interior."""
    from diagrams_as_code.router import segment_intersects_rect

    r = Rect(100.0, 100.0, 100.0, 100.0)

    # Horizontal crossing through interior
    assert segment_intersects_rect(Point(50, 150), Point(250, 150), r)
    assert segment_intersects_rect(Point(250, 150), Point(50, 150), r)

    # Vertical crossing through interior
    assert segment_intersects_rect(Point(150, 50), Point(150, 250), r)
    assert segment_intersects_rect(Point(150, 250), Point(150, 50), r)

    # Completely outside
    assert not segment_intersects_rect(Point(50, 50), Point(250, 50), r)
    assert not segment_intersects_rect(Point(50, 50), Point(50, 250), r)

    # Touching boundary but not interior
    assert not segment_intersects_rect(Point(50, 100), Point(250, 100), r)
    assert not segment_intersects_rect(Point(100, 50), Point(100, 250), r)


def test_obstacle_avoidance_horizontal() -> None:
    """Verify route detours around an intermediate obstacle on horizontal path."""
    from diagrams_as_code.router import segment_intersects_rect

    s1 = Shape("s1", "Source", 100, 50).at(0, 100)
    s2 = Shape("s2", "Target", 100, 50).at(400, 100)
    obs = Shape("obs", "Obstacle", 100, 100).at(200, 75)
    edge = Edge(s1, s2, source_port=Port.EAST, target_port=Port.WEST)

    router = OrthogonalRouter()
    # Without obstacles: direct horizontal line
    direct_route = router.route(edge)
    assert len(direct_route) == 2
    assert direct_route[0] == Point(100.0, 125.0)
    assert direct_route[1] == Point(400.0, 125.0)

    # With obstacle: must detour around obs
    detour_route = router.route(edge, obstacles=[obs], clearance=15.0)
    assert len(detour_route) > 2
    assert detour_route[0] == Point(100.0, 125.0)
    assert detour_route[-1] == Point(400.0, 125.0)

    # Check each segment does not penetrate obstacle bounds
    for p_a, p_b in zip(detour_route[:-1], detour_route[1:]):
        assert not segment_intersects_rect(p_a, p_b, obs.bounds), f"Segment {p_a}->{p_b} intersects obstacle"
        assert p_a.x == p_b.x or p_a.y == p_b.y


def test_obstacle_avoidance_vertical() -> None:
    """Verify route detours around an intermediate obstacle on vertical path."""
    from diagrams_as_code.router import segment_intersects_rect

    s1 = Shape("s1", "Source", 100, 50).at(100, 0)
    s2 = Shape("s2", "Target", 100, 50).at(100, 400)
    obs = Shape("obs", "Obstacle", 100, 100).at(100, 150)
    edge = Edge(s1, s2, source_port=Port.SOUTH, target_port=Port.NORTH)

    router = OrthogonalRouter()
    detour_route = router.route(edge, obstacles=[obs], clearance=15.0)
    assert len(detour_route) > 2
    assert detour_route[0] == Point(150.0, 50.0)
    assert detour_route[-1] == Point(150.0, 400.0)

    for p_a, p_b in zip(detour_route[:-1], detour_route[1:]):
        assert not segment_intersects_rect(p_a, p_b, obs.bounds)
        assert p_a.x == p_b.x or p_a.y == p_b.y


def test_obstacle_avoidance_multi_obstacles() -> None:
    """Verify route detours around multiple obstacles without collision."""
    from diagrams_as_code.router import segment_intersects_rect

    s1 = Shape("s1", "Source", 80, 50).at(0, 100)
    s2 = Shape("s2", "Target", 80, 50).at(500, 100)
    obs1 = Shape("obs1", "Obstacle 1", 80, 80).at(150, 85)
    obs2 = Shape("obs2", "Obstacle 2", 80, 80).at(300, 85)
    edge = Edge(s1, s2, source_port=Port.EAST, target_port=Port.WEST)

    router = OrthogonalRouter()
    detour_route = router.route(edge, obstacles=[obs1, obs2], clearance=10.0)
    assert len(detour_route) > 2
    for p_a, p_b in zip(detour_route[:-1], detour_route[1:]):
        assert not segment_intersects_rect(p_a, p_b, obs1.bounds)
        assert not segment_intersects_rect(p_a, p_b, obs2.bounds)
        assert p_a.x == p_b.x or p_a.y == p_b.y


def test_obstacle_avoidance_backward_compatibility() -> None:
    """Verify exact coordinate equality when obstacles are omitted or None."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 100)
    edge = Edge(s1, s2)
    router = OrthogonalRouter()

    default_waypoints = router.route(edge)
    none_waypoints = router.route(edge, obstacles=None)
    empty_waypoints = router.route(edge, obstacles=[])

    assert default_waypoints == none_waypoints == empty_waypoints


def test_curve_routing_edge_dispatch() -> None:
    """Verify Routing.CURVE and 'curve' return 4 points across CurveRouter, OrthogonalRouter, and EdgeRouter."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 0)

    # With enum
    edge_enum = Edge(s1, s2, routing=Routing.CURVE)
    # With string
    edge_str = Edge(s1, s2, routing="curve")

    for edge in (edge_enum, edge_str):
        curve_pts = CurveRouter().route(edge)
        assert len(curve_pts) == 4
        assert curve_pts[0] == s1.bounds.get_anchor(Port.EAST.to_anchor())
        assert curve_pts[3] == s2.bounds.get_anchor(Port.WEST.to_anchor())

        # OrthogonalRouter delegation
        ortho_pts = OrthogonalRouter().route(edge)
        assert ortho_pts == curve_pts

        # EdgeRouter facade
        edge_pts = EdgeRouter().route(edge)
        assert edge_pts == curve_pts

    # EdgeRouter also dispatches DIRECT and ORTHOGONAL correctly
    edge_direct = Edge(s1, s2, routing=Routing.DIRECT)
    assert len(EdgeRouter().route(edge_direct)) == 2

    edge_ortho = Edge(s1, s2, routing=Routing.ORTHOGONAL)
    assert EdgeRouter().route(edge_ortho) == OrthogonalRouter().route(edge_ortho)


def test_curve_router_port_tangent_alignment() -> None:
    """Verify all 16 cardinal port pairs produce strictly collinear tangents with zero perpendicular drift."""
    import math

    ports = [Port.EAST, Port.WEST, Port.NORTH, Port.SOUTH]
    router = CurveRouter()

    for sp in ports:
        for tp in ports:
            s1 = Shape("s1", "Src", 100, 60).at(50, 50)
            s2 = Shape("s2", "Tgt", 100, 60).at(400, 350)
            edge = Edge(s1, s2, source_port=sp, target_port=tp, routing=Routing.CURVE)
            pts = router.route(edge)
            assert len(pts) == 4, f"Failed for {sp} -> {tp}: expected 4 waypoints"
            p0, c1, c2, p3 = pts

            n_src = PORT_NORMALS[sp]
            n_tgt = PORT_NORMALS[tp]

            # Vector (c1 - p0) must be parallel to outward normal n_src:
            # 2D cross product: v.x * n.y - v.y * n.x == 0
            v_exit = c1 - p0
            cross_exit = v_exit.x * n_src.y - v_exit.y * n_src.x
            dot_exit = v_exit.x * n_src.x + v_exit.y * n_src.y
            assert math.isclose(cross_exit, 0.0, abs_tol=1e-6), (
                f"{sp}->{tp}: Exit tangent drift {cross_exit}"
            )
            assert dot_exit > 0.0, f"{sp}->{tp}: Exit tangent must point along outward normal"

            # Vector (p3 - c2) must be antiparallel to outward normal n_tgt (pointing inward):
            # 2D cross product: v.x * n.y - v.y * n.x == 0
            v_entry = p3 - c2
            cross_entry = v_entry.x * n_tgt.y - v_entry.y * n_tgt.x
            dot_entry = v_entry.x * n_tgt.x + v_entry.y * n_tgt.y
            assert math.isclose(cross_entry, 0.0, abs_tol=1e-6), (
                f"{sp}->{tp}: Entry tangent drift {cross_entry}"
            )
            assert dot_entry < 0.0, f"{sp}->{tp}: Entry tangent must point inward toward target"

            # Minimum handle separation invariant (D-02, D-15)
            assert p0.distance_to(c1) >= 20.0
            assert p3.distance_to(c2) >= 20.0


def test_curve_router_handle_scaling_heuristics() -> None:
    """Verify D-01 through D-07 handle scaling heuristics and minimum clamp D-15."""
    import math

    router = CurveRouter()

    # D-01 / D-02: Forward flow scaling along primary axis
    # s1 EAST anchor: (100, 25); s2 WEST anchor: (300, 25) -> dx = 200, dy = 0
    # axis_delta = 200, lat_delta = 0 -> d = max(0.5 * 200, 0, 20.0) = 100.0
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 0)
    e_forward = Edge(s1, s2, source_port=Port.EAST, target_port=Port.WEST, routing=Routing.CURVE)
    p0, c1, c2, p3 = router.route(e_forward)
    assert p0 == Point(100.0, 25.0)
    assert p3 == Point(300.0, 25.0)
    assert c1 == Point(200.0, 25.0)
    assert c2 == Point(200.0, 25.0)
    assert math.isclose(p0.distance_to(c1), 100.0)
    assert math.isclose(p3.distance_to(c2), 100.0)

    # D-03: Lateral blending when axis separation is small but lateral offset is large
    # s1 EAST anchor: (100, 25); s2 WEST anchor: (110, 225) -> dx = 10, dy = 200
    # axis_delta = 10, lat_delta = 200 -> d = max(0.5 * 10, 0.25 * 200, 20.0) = max(5, 50, 20) = 50.0
    s3 = Shape("s3", "C", 100, 50).at(0, 0)
    s4 = Shape("s4", "D", 100, 50).at(110, 200)
    e_lateral = Edge(s3, s4, source_port=Port.EAST, target_port=Port.WEST, routing=Routing.CURVE)
    p0, c1, c2, p3 = router.route(e_lateral)
    assert math.isclose(p0.distance_to(c1), 50.0)
    assert math.isclose(p3.distance_to(c2), 50.0)

    # D-05: Perpendicular ports (e.g. EAST to SOUTH)
    # s1 EAST anchor: (100, 25); s2 SOUTH anchor: (250, 250) -> dx = 150, dy = 225
    # d_x = max(0.5 * 150, 25.0) = 75.0 (horizontal source EAST)
    # d_y = max(0.5 * 225, 25.0) = 112.5 (vertical target SOUTH)
    s5 = Shape("s5", "E", 100, 50).at(0, 0)
    s6 = Shape("s6", "F", 100, 50).at(200, 200)
    e_perp = Edge(s5, s6, source_port=Port.EAST, target_port=Port.SOUTH, routing=Routing.CURVE)
    p0, c1, c2, p3 = router.route(e_perp)
    assert math.isclose(p0.distance_to(c1), 75.0)
    assert math.isclose(p3.distance_to(c2), 112.5)

    # D-06: Same-side / parallel ports (e.g. NORTH to NORTH)
    # s5 NORTH anchor: (50, 0); s6 NORTH anchor: (250, 200) -> dx = 200, dy = 200
    # ports are vertical -> sep = |dx| = 200 -> d = max(0.5 * 200, 30.0) = 100.0
    e_parallel_v = Edge(s5, s6, source_port=Port.NORTH, target_port=Port.NORTH, routing=Routing.CURVE)
    p0, c1, c2, p3 = router.route(e_parallel_v)
    assert math.isclose(p0.distance_to(c1), 100.0)
    assert math.isclose(p3.distance_to(c2), 100.0)

    # Parallel horizontal ports (EAST to EAST)
    # s1 EAST anchor: (100, 25); s_eh EAST anchor: (300, 125) -> dx = 200, dy = 100
    # ports are horizontal -> sep = |dy| = 100 -> d = max(0.5 * 100, 30.0) = 50.0
    s_eh = Shape("s_eh", "EH", 100, 50).at(200, 100)
    e_parallel_h = Edge(s1, s_eh, source_port=Port.EAST, target_port=Port.EAST, routing=Routing.CURVE)
    p0, c1, c2, p3 = router.route(e_parallel_h)
    assert math.isclose(p0.distance_to(c1), 50.0)
    assert math.isclose(p3.distance_to(c2), 50.0)

    # D-07: Backward flow 30px minimum clearance
    # s7 at x=200 facing EAST; s8 at x=0 facing WEST -> backward flow (dx = -300 <= 0)
    s7 = Shape("s7", "G", 100, 50).at(200, 0)
    s8 = Shape("s8", "H", 100, 50).at(0, 0)
    e_backward = Edge(s7, s8, source_port=Port.EAST, target_port=Port.WEST, routing=Routing.CURVE)
    p0, c1, c2, p3 = router.route(e_backward)
    assert p0 == Point(300.0, 25.0)
    assert p3 == Point(0.0, 25.0)
    assert math.isclose(p0.distance_to(c1), 30.0)
    assert math.isclose(p3.distance_to(c2), 30.0)
    assert c1 == Point(330.0, 25.0)
    assert c2 == Point(-30.0, 25.0)

    # D-02, D-15: Minimum handle separation >= 20px on extremely close shapes
    s9 = Shape("s9", "I", 100, 50).at(0, 0)
    s10 = Shape("s10", "J", 100, 50).at(102, 0)
    e_close = Edge(s9, s10, source_port=Port.EAST, target_port=Port.WEST, routing=Routing.CURVE)
    p0, c1, c2, p3 = router.route(e_close)
    assert p0.distance_to(c1) >= 20.0
    assert p3.distance_to(c2) >= 20.0


def test_edge_corner_radius_and_arc_radius_alias() -> None:
    """Verify Edge corner_radius default, explicit setting, arc_radius alias, and bidirectional sync."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 0)

    # Default is None (sharp corners)
    default_edge = Edge(s1, s2)
    assert default_edge.corner_radius is None
    assert default_edge.arc_radius is None

    # Explicit corner_radius
    e_cr = Edge(s1, s2, corner_radius=12.0)
    assert e_cr.corner_radius == 12.0
    assert e_cr.arc_radius == 12.0

    # Explicit arc_radius alias
    e_ar = Edge(s1, s2, arc_radius=8.5)
    assert e_ar.corner_radius == 8.5
    assert e_ar.arc_radius == 8.5

    # Bidirectional setter sync
    e = Edge(s1, s2)
    e.corner_radius = 15.0
    assert e.corner_radius == 15.0
    assert e.arc_radius == 15.0

    e.arc_radius = 6.0
    assert e.corner_radius == 6.0
    assert e.arc_radius == 6.0

    e.corner_radius = None
    assert e.corner_radius is None
    assert e.arc_radius is None


def test_edge_corner_radius_validation() -> None:
    """Verify corner_radius input validation rejecting negative, non-numeric, nan, inf."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 0)

    # Integer coercion to float
    e_int = Edge(s1, s2, corner_radius=10)
    assert e_int.corner_radius == 10.0
    assert isinstance(e_int.corner_radius, float)

    # Float zero
    e_zero = Edge(s1, s2, corner_radius=0)
    assert e_zero.corner_radius == 0.0

    # Negative values
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, corner_radius=-1.0)
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, arc_radius=-0.5)

    # Non-numeric strings
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, corner_radius="invalid")
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, arc_radius="10px")
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, corner_radius="12.0")

    # Booleans
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, corner_radius=True)  # type: ignore
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, corner_radius=False)  # type: ignore

    # NaN and Inf
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, corner_radius=float("nan"))
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, corner_radius=float("inf"))
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, corner_radius=float("-inf"))

    # Setter validation
    e = Edge(s1, s2)
    with pytest.raises(ValueError, match="non-negative finite float"):
        e.corner_radius = -2.0
    with pytest.raises(ValueError, match="non-negative finite float"):
        e.arc_radius = -2.0
    with pytest.raises(ValueError, match="non-negative finite float"):
        e.corner_radius = "bad"  # type: ignore



