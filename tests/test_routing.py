from __future__ import annotations

import pytest

from iiot_diagrams import (
    Anchor,
    CubicBezier,
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


def test_edge_clearance_default_and_setter() -> None:
    """Verify Edge clearance default of 15.0px and setter behavior."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 0)

    # Default is 15.0px (D-02)
    edge = Edge(s1, s2)
    assert edge.clearance == 15.0
    assert isinstance(edge.clearance, float)

    # Explicit initialization
    edge_custom = Edge(s1, s2, clearance=25.0)
    assert edge_custom.clearance == 25.0

    # Setter update with float and int
    edge.clearance = 30.0
    assert edge.clearance == 30.0

    edge.clearance = 10
    assert edge.clearance == 10.0
    assert isinstance(edge.clearance, float)

    # Zero clearance is valid
    edge.clearance = 0
    assert edge.clearance == 0.0

    # None resets to default 15.0
    edge.clearance = None  # type: ignore
    assert edge.clearance == 15.0


def test_edge_clearance_validation() -> None:
    """Verify clearance input validation rejecting negative numbers, non-numeric strings, booleans, nan, inf."""
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 0)

    # Negative values
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance=-1.0)
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance=-0.001)

    # Non-numeric strings
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance="15")  # type: ignore
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance="invalid")  # type: ignore

    # Boolean values
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance=True)  # type: ignore
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance=False)  # type: ignore

    # NaN and Inf
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance=float("nan"))
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance=float("inf"))
    with pytest.raises(ValueError, match="non-negative finite float"):
        Edge(s1, s2, clearance=float("-inf"))

    # Setter validation
    e = Edge(s1, s2)
    with pytest.raises(ValueError, match="non-negative finite float"):
        e.clearance = -5.0
    with pytest.raises(ValueError, match="non-negative finite float"):
        e.clearance = "bad"  # type: ignore
    with pytest.raises(ValueError, match="non-negative finite float"):
        e.clearance = True  # type: ignore
    with pytest.raises(ValueError, match="non-negative finite float"):
        e.clearance = float("nan")


def test_edge_clearance_diagram_cascading() -> None:
    """Verify clearance cascading from Diagram and EdgeBuilder to Edge instances via resolve_edge_style."""
    from diagrams_as_code.diagram import Diagram
    from diagrams_as_code.layout.pipeline import resolve_edge_style

    diag = Diagram("Clearance Cascade", clearance=28.0)
    s1 = diag.shape("S1")
    s2 = diag.shape("S2")

    # Inherit diagram-level default clearance without per-site edge mutation
    e1 = diag.connect(s1, s2)
    assert e1._clearance is None
    assert e1.clearance == 15.0
    assert resolve_edge_style(e1, diag).clearance == 28.0

    # Explicit override on connect
    e2 = diag.connect(s1, s2, clearance=12.0)
    assert e2._clearance == 12.0
    assert e2.clearance == 12.0
    assert resolve_edge_style(e2, diag).clearance == 12.0

    # Fluent edge builder inheriting diagram clearance
    s1 >> diag.edge() >> s2
    assert diag.edges[-1]._clearance is None
    assert resolve_edge_style(diag.edges[-1], diag).clearance == 28.0

    # Fluent edge builder with explicit clearance override
    s1 >> diag.edge(clearance=8.0) >> s2
    assert diag.edges[-1]._clearance == 8.0
    assert resolve_edge_style(diag.edges[-1], diag).clearance == 8.0


def test_curve_router_obstacle_filtering() -> None:
    """Verify CurveRouter._normalize_obstacles filters endpoints, matching IDs, and enclosing groups."""
    router = CurveRouter()
    s1 = Shape("s1", "Source", 100, 50).at(0, 100)
    s2 = Shape("s2", "Target", 100, 50).at(400, 100)
    edge = Edge(s1, s2)
    p_start = s1.bounds.get_anchor(Port.EAST.to_anchor())
    p_end = s2.bounds.get_anchor(Port.WEST.to_anchor())

    # Duplicate / matching ID element
    s1_dup = Shape("s1", "Dup", 100, 50).at(0, 100)

    # Enclosing container group that contains s1 / p_start
    g1_rect = Rect(-10, 50, 150, 150)

    # Intervening obstacle shape
    intervening = Shape("s3", "Obstacle", 100, 50).at(200, 100)

    # Bare Rect obstacle
    bare_rect = Rect(220, 200, 60, 40)

    obstacles = [s1, s2, s1_dup, g1_rect, intervening, bare_rect]

    norm = router._normalize_obstacles(edge, obstacles, p_start, p_end)

    # s1 and s2 excluded (D-03)
    # s1_dup excluded because id == "s1" (D-03)
    # g1_rect excluded because it contains p_start (D-03)
    # intervening and bare_rect retained
    assert intervening.bounds in norm
    assert bare_rect in norm
    assert len(norm) == 2

    # None obstacles returns []
    assert router._normalize_obstacles(edge, None, p_start, p_end) == []


def test_curve_router_collision_detection() -> None:
    """Verify CurveRouter._detect_collisions detects clearance-inflated intersections."""
    router = CurveRouter()
    curve = CubicBezier(
        Point(0, 100),
        Point(100, 100),
        Point(200, 100),
        Point(300, 100),
    )

    # Obstacle directly intersecting candidate curve
    obs_hit = Rect(130, 80, 40, 40)

    # Obstacle placed 25px away from curve (y: 125..165, curve is at y=100)
    obs_far = Rect(130, 125, 40, 40)

    # With clearance=15.0px, obs_far expanded is [115, 110, 70, 70] (top=110 > 100) -> no collision
    collisions = router._detect_collisions(curve, [obs_hit, obs_far], clearance=15.0)
    assert obs_hit in collisions
    assert obs_far not in collisions

    # With clearance=30.0px, obs_far expanded top is 125 - 30 = 95 (< 100) -> collision!
    collisions_large = router._detect_collisions(curve, [obs_hit, obs_far], clearance=30.0)
    assert obs_hit in collisions_large
    assert obs_far in collisions_large


def test_curve_router_reverse_flow_automatic_port_resolution() -> None:
    """Verify CurveRouter.resolve_ports auto-resolves reverse-flow edges to lateral cardinal ports."""
    router = CurveRouter()

    # 1. Forward flow horizontal (dx > 0): resolves to (EAST, WEST)
    s_fwd1 = Shape("f1", "Src", 100, 50).at(0, 100)
    s_fwd2 = Shape("f2", "Tgt", 100, 50).at(300, 100)
    assert router.resolve_ports(Edge(s_fwd1, s_fwd2)) == (Port.EAST, Port.WEST)

    # 2. Horizontal reverse flow (dx = -300 < 0) with unspecified ports: resolves to (NORTH, NORTH)
    s_rev1 = Shape("r1", "Src", 100, 50).at(400, 100)
    s_rev2 = Shape("r2", "Tgt", 100, 50).at(100, 100)
    assert router.resolve_ports(Edge(s_rev1, s_rev2)) == (Port.NORTH, Port.NORTH)

    # 3. Horizontal reverse flow constrained at top canvas boundary (y <= 30): resolves to (SOUTH, SOUTH)
    s_top1 = Shape("t1", "Src", 100, 50).at(400, 20)
    s_top2 = Shape("t2", "Tgt", 100, 50).at(100, 20)
    assert router.resolve_ports(Edge(s_top1, s_top2)) == (Port.SOUTH, Port.SOUTH)

    # 4. Horizontal reverse flow with north corridor obstacle: resolves to (SOUTH, SOUTH)
    obs_north = Rect(200, 80, 100, 15)  # occupies y=80..95, s_rev1/s_rev2 are at y=100
    assert router.resolve_ports(Edge(s_rev1, s_rev2), obstacles=[obs_north]) == (Port.SOUTH, Port.SOUTH)

    # 5. Forward flow vertical (dy > 0): resolves to (SOUTH, NORTH)
    s_vfwd1 = Shape("vf1", "Src", 100, 50).at(100, 0)
    s_vfwd2 = Shape("vf2", "Tgt", 100, 50).at(100, 300)
    assert router.resolve_ports(Edge(s_vfwd1, s_vfwd2)) == (Port.SOUTH, Port.NORTH)

    # 6. Vertical reverse flow (dy = -200 < 0) with unspecified ports: resolves to (EAST, EAST)
    s_vrev1 = Shape("vr1", "Src", 100, 50).at(100, 300)
    s_vrev2 = Shape("vr2", "Tgt", 100, 50).at(100, 100)
    assert router.resolve_ports(Edge(s_vrev1, s_vrev2)) == (Port.EAST, Port.EAST)

    # 7. Vertical reverse flow with east corridor obstacle: resolves to (WEST, WEST)
    obs_east = Rect(205, 150, 40, 100)  # occupies x=205..245, s_vrev1/s_vrev2 right is 200
    assert router.resolve_ports(Edge(s_vrev1, s_vrev2), obstacles=[obs_east]) == (Port.WEST, Port.WEST)


def test_curve_router_reverse_flow_explicit_ports_escape() -> None:
    """Verify reverse-flow edges with explicit ports route via lateral escape corridor (D-13, D-15, T-10-04)."""
    import math

    router = CurveRouter()

    # Source at right: x=400..500, y=100..150; Target at left: x=100..200, y=100..150
    s1 = Shape("s1", "Source", 100, 50).at(400, 100)
    s2 = Shape("s2", "Target", 100, 50).at(100, 100)
    edge = Edge(s1, s2, source_port=Port.EAST, target_port=Port.WEST, routing=Routing.CURVE)

    # 1. Route with obstacles provided triggers lateral escape corridor (3-segment spline = 10 waypoints)
    pts = router.route(edge, obstacles=[s1, s2])
    assert len(pts) == 10  # 3N+1 points (D-06)

    p0, c0a, c0b, w_esc1, c1a, c1b, w_esc2, c2a, c2b, p3 = pts

    # Anchors match ports
    assert p0 == Point(500.0, 125.0)  # s1 EAST anchor
    assert p3 == Point(100.0, 125.0)  # s2 WEST anchor

    # Clearance margin checks: >= 30.0px beyond boundaries (D-13, D-15)
    margin = 30.0
    assert w_esc1.x >= s1.bounds.right + margin  # >= 530.0
    assert w_esc2.x <= s2.bounds.left - margin   # <= 70.0
    assert w_esc1.y <= min(s1.bounds.top, s2.bounds.top) - margin  # <= 70.0
    assert w_esc2.y <= min(s1.bounds.top, s2.bounds.top) - margin  # <= 70.0

    # Intermediate control handles maintain >= 20.0px minimum clamp (D-02, D-15, T-10-02)
    assert p0.distance_to(c0a) >= 20.0
    assert w_esc1.distance_to(c0b) >= 20.0
    assert w_esc1.distance_to(c1a) >= 20.0
    assert w_esc2.distance_to(c1b) >= 20.0
    assert w_esc2.distance_to(c2a) >= 20.0
    assert p3.distance_to(c2b) >= 20.0

    # 2. Verify no self-intersection or bow-tie loops (T-10-04)
    seg1 = CubicBezier(p0, c0a, c0b, w_esc1)
    seg2 = CubicBezier(w_esc1, c1a, c1b, w_esc2)
    seg3 = CubicBezier(w_esc2, c2a, c2b, p3)

    bbox1 = seg1.bbox()
    bbox3 = seg3.bbox()
    # Segment 1 and Segment 3 bounding boxes must be disjoint along x-axis
    assert bbox1.left >= 500.0
    assert bbox3.right <= 100.0
    assert not bbox1.intersects(bbox3)

    # 3. Verify corridor expands further when an intervening obstacle is present
    obs_roof = Rect(200, 40, 100, 30)  # top at y=40, above s1 and s2
    pts_with_obs = router.route(edge, obstacles=[s1, s2, obs_roof])
    w_esc1_obs = pts_with_obs[3]
    # Escape corridor y should be at or above obs_roof.top - margin = 40 - 30 = 10.0
    assert w_esc1_obs.y <= obs_roof.top - margin

    # 4. Verify coincident anchor node robustness against zero-division / NaN (T-10-02)
    s_same = Shape("same", "Same", 100, 50).at(100, 100)
    e_same = Edge(s_same, s_same, source_port=Port.EAST, target_port=Port.WEST, routing=Routing.CURVE)
    pts_same = router.route(e_same, obstacles=[s_same])
    assert len(pts_same) == 10
    for pt in pts_same:
        assert not math.isnan(pt.x)
        assert not math.isnan(pt.y)
        assert not math.isinf(pt.x)
        assert not math.isinf(pt.y)


def test_curve_deflection_single_obstacle_compact() -> None:
    """Verify single apex waypoint (7 points / 2 segments) for compact obstacle deflection (D-07, CURVEOBS-02)."""
    router = CurveRouter()
    s1 = Shape("s1", "Source", 100, 50).at(100, 100)
    s2 = Shape("s2", "Target", 100, 50).at(500, 100)
    edge = Edge(s1, s2, routing=Routing.CURVE)

    # Compact obstacle: width 20px <= 2 * clearance (30.0px)
    obs = Shape("obs", "Obstacle", 20, 50).at(300, 100)

    pts = router.route(edge, obstacles=[s1, s2, obs])
    assert len(pts) == 7  # 3N+1 points with N=2
    assert edge.waypoints == pts

    p0, c0a, c0b, w, c1a, c1b, p3 = pts
    assert p0 == Point(200.0, 125.0)  # s1 EAST anchor
    assert p3 == Point(500.0, 125.0)  # s2 WEST anchor
    assert w.x == 310.0  # obstacle center x
    # Waypoint deflected either above (y <= 85.0) or below (y >= 165.0)
    assert w.y <= 85.0 or w.y >= 165.0


def test_curve_deflection_wide_obstacle_two_waypoints() -> None:
    """Verify 2 corner clearance waypoints (10 points / 3 segments) for wide obstacle deflection (D-07, CURVEOBS-02)."""
    router = CurveRouter()
    s1 = Shape("s1", "Source", 100, 50).at(100, 100)
    s2 = Shape("s2", "Target", 100, 50).at(500, 100)
    edge = Edge(s1, s2, routing=Routing.CURVE)

    # Wide obstacle: width 100px > 2 * clearance (30.0px)
    obs = Shape("obs", "Obstacle", 100, 50).at(250, 100)

    pts = router.route(edge, obstacles=[s1, s2, obs])
    assert len(pts) == 10  # 3N+1 points with N=3
    assert edge.waypoints == pts

    p0, c0a, c0b, w1, c1a, c1b, w2, c2a, c2b, p3 = pts
    assert p0 == Point(200.0, 125.0)
    assert p3 == Point(500.0, 125.0)

    # Corner clearance waypoints
    assert w1.x <= obs.bounds.left - 15.0  # <= 235.0
    assert w2.x >= obs.bounds.right + 15.0  # >= 365.0
    assert w1.y == w2.y
    assert w1.y <= 85.0 or w1.y >= 165.0

    # Middle bypass segment has collinear handles along corridor line
    assert c1a.y == w1.y
    assert c1b.y == w2.y


def test_curve_deflection_corner_clearance_invariant() -> None:
    """Verify all deflection waypoints maintain >= 15.0px distance from all obstacle corners (D-11, T-10-03)."""
    router = CurveRouter()
    s1 = Shape("s1", "Source", 100, 50).at(100, 100)
    s2 = Shape("s2", "Target", 100, 50).at(500, 100)

    # 1. Compact obstacle
    obs_compact = Shape("obs_c", "Obstacle", 20, 50).at(300, 100)
    edge_compact = Edge(s1, s2, routing=Routing.CURVE)
    pts_compact = router.route(edge_compact, obstacles=[s1, s2, obs_compact])
    w_compact = pts_compact[3]

    corners_c = [
        Point(obs_compact.bounds.left, obs_compact.bounds.top),
        Point(obs_compact.bounds.right, obs_compact.bounds.top),
        Point(obs_compact.bounds.left, obs_compact.bounds.bottom),
        Point(obs_compact.bounds.right, obs_compact.bounds.bottom),
    ]
    for c in corners_c:
        assert w_compact.distance_to(c) >= 15.0

    # 2. Wide obstacle
    obs_wide = Shape("obs_w", "Obstacle", 120, 60).at(240, 95)
    edge_wide = Edge(s1, s2, routing=Routing.CURVE)
    pts_wide = router.route(edge_wide, obstacles=[s1, s2, obs_wide])
    w1, w2 = pts_wide[3], pts_wide[6]

    corners_w = [
        Point(obs_wide.bounds.left, obs_wide.bounds.top),
        Point(obs_wide.bounds.right, obs_wide.bounds.top),
        Point(obs_wide.bounds.left, obs_wide.bounds.bottom),
        Point(obs_wide.bounds.right, obs_wide.bounds.bottom),
    ]
    for corner in corners_w:
        assert w1.distance_to(corner) >= 15.0
        assert w2.distance_to(corner) >= 15.0


def test_curve_deflection_secondary_obstacle_bypass() -> None:
    """Verify curve routes to alternative corridor or expands when secondary obstacles block preferred corridor (D-10)."""
    router = CurveRouter()
    s1 = Shape("s1", "Source", 100, 50).at(100, 100)
    s2 = Shape("s2", "Target", 100, 50).at(500, 100)

    # Primary obstacle directly in between
    obs_mid = Shape("obs_mid", "Obstacle", 100, 50).at(250, 100)
    # Secondary obstacle above, blocking the TOP corridor (y = 85)
    obs_roof = Rect(250, 40, 100, 45)  # top=40, bottom=85

    edge = Edge(s1, s2, routing=Routing.CURVE)
    pts = router.route(edge, obstacles=[s1, s2, obs_mid, obs_roof])
    # Must deflect via BOTTOM corridor: y >= 150 + 15 = 165
    w1 = pts[3]
    assert w1.y >= 165.0

    # If BOTH top and bottom are blocked, expand corridor further outward (D-10)
    obs_floor = Rect(250, 155, 100, 40)  # top=155, bottom=195
    pts_exp = router.route(edge, obstacles=[s1, s2, obs_mid, obs_roof, obs_floor])
    w_exp = pts_exp[3]
    # Either above obs_roof (y <= 40 - 15 = 25) or below obs_floor (y >= 195 + 15 = 210)
    assert w_exp.y <= 25.0 or w_exp.y >= 210.0


def test_curve_deflection_c1_continuity() -> None:
    """Verify strict C1 continuity (u_out == u_in within 1e-5 tolerance) at all intermediate waypoints (D-05)."""
    import math

    router = CurveRouter()
    s1 = Shape("s1", "Source", 100, 50).at(100, 100)
    s2 = Shape("s2", "Target", 100, 50).at(500, 100)

    # Test compact obstacle (N=2, 1 intermediate waypoint)
    obs_c = Shape("obs_c", "Obstacle", 20, 50).at(300, 100)
    pts_c = router.route(Edge(s1, s2, routing=Routing.CURVE), obstacles=[s1, s2, obs_c])
    w_c, c_in_c, c_out_c = pts_c[3], pts_c[2], pts_c[4]
    v_in = Point(w_c.x - c_in_c.x, w_c.y - c_in_c.y)
    v_out = Point(c_out_c.x - w_c.x, c_out_c.y - w_c.y)
    l_in = math.hypot(v_in.x, v_in.y)
    l_out = math.hypot(v_out.x, v_out.y)
    u_in = Point(v_in.x / l_in, v_in.y / l_in)
    u_out = Point(v_out.x / l_out, v_out.y / l_out)
    assert abs(u_in.x - u_out.x) < 1e-5
    assert abs(u_in.y - u_out.y) < 1e-5

    # Test wide obstacle (N=3, 2 intermediate waypoints)
    obs_w = Shape("obs_w", "Obstacle", 100, 50).at(250, 100)
    pts_w = router.route(Edge(s1, s2, routing=Routing.CURVE), obstacles=[s1, s2, obs_w])
    for w_idx, in_idx, out_idx in [(3, 2, 4), (6, 5, 7)]:
        w, c_in, c_out = pts_w[w_idx], pts_w[in_idx], pts_w[out_idx]
        v_in = Point(w.x - c_in.x, w.y - c_in.y)
        v_out = Point(c_out.x - w.x, c_out.y - w.y)
        l_in = math.hypot(v_in.x, v_in.y)
        l_out = math.hypot(v_out.x, v_out.y)
        u_in = Point(v_in.x / l_in, v_in.y / l_in)
        u_out = Point(v_out.x / l_out, v_out.y / l_out)
        assert abs(u_in.x - u_out.x) < 1e-5
        assert abs(u_in.y - u_out.y) < 1e-5


def test_curve_routing_unobstructed_backward_compatibility() -> None:
    """Verify unobstructed curves return exact 4 points identical to Phase 8 (D-16)."""
    router = CurveRouter()
    s1 = Shape("s1", "Source", 100, 50).at(100, 100)
    s2 = Shape("s2", "Target", 100, 50).at(300, 100)
    edge = Edge(s1, s2, routing=Routing.CURVE)

    pts_none = router.route(edge, obstacles=None)
    pts_empty = router.route(edge, obstacles=[])
    pts_clear = router.route(edge, obstacles=[Shape("obs", "Far", 50, 50).at(1000, 1000)])

    assert len(pts_none) == 4
    assert len(pts_empty) == 4
    assert len(pts_clear) == 4
    assert pts_none == pts_empty == pts_clear








