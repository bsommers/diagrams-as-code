from __future__ import annotations

import warnings

import pytest

from diagrams_as_code import Diagram, Edge, Routing
from diagrams_as_code.geometry import Point, RoutedPath
from diagrams_as_code.layout import LayoutWarning, export_layout
from diagrams_as_code.layout.pipeline import EdgeStyle, resolve_edge_style


def _bounds(d: Diagram) -> dict[str, tuple[float, float, float, float]]:
    return {e.id: (e.bounds.x, e.bounds.y, e.bounds.width, e.bounds.height) for e in d.all_elements()}


def test_manual_is_the_default_and_leaves_unplaced_shapes_alone() -> None:
    with Diagram() as d:
        a = d.shape("A")
    assert d.layout == "manual"
    assert (a.bounds.x, a.bounds.y) == (0.0, 0.0)


def test_auto_chain_flows_left_to_right_from_the_frame_margin() -> None:
    with Diagram(layout="auto") as d:
        a, b, c = d.shape("A"), d.shape("B"), d.shape("C")
        a >> b >> c
    assert (a.bounds.x, a.bounds.y) == (60.0, 80.0)
    assert a.bounds.right < b.bounds.x < b.bounds.right < c.bounds.x
    assert a.bounds.y == b.bounds.y == c.bounds.y


def test_auto_top_to_bottom() -> None:
    with Diagram(layout="auto", direction="TB") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    assert a.bounds.x == b.bounds.x
    assert a.bounds.bottom < b.bounds.y


def test_groups_are_laid_out_inside_then_placed_as_blocks() -> None:
    with Diagram(layout="auto") as d:
        with d.group("Left") as left:
            a1, a2 = d.shape("A1"), d.shape("A2")
            a1 >> a2
        with d.group("Right") as right:
            b1 = d.shape("B1")
        a2 >> b1
    assert left.bounds.right < right.bounds.x
    for child in (a1, a2):
        assert left.bounds.x < child.bounds.x and child.bounds.right < left.bounds.right
    assert a1.bounds.y > left.bounds.y + left.header_height


def test_pinned_shapes_stay_put_and_can_anchor_to_auto_ones() -> None:
    with Diagram(layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        p = d.shape("P").at(900, 600)
        c = d.shape("C").below(b, margin=30, align="left")
        a >> b
    assert (p.bounds.x, p.bounds.y) == (900.0, 600.0)
    assert (c.bounds.x, c.bounds.y) == (b.bounds.x, b.bounds.bottom + 30)


def test_overlap_between_pinned_and_auto_is_warned() -> None:
    with pytest.warns(LayoutWarning, match="'P'.*'A'"):
        with Diagram(layout="auto") as d:
            d.shape("A")
            d.shape("P").at(70, 90)


def test_no_warning_when_nothing_overlaps() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", LayoutWarning)
        with Diagram(layout="auto") as d:
            a, b = d.shape("A"), d.shape("B")
            a >> b


def test_canvas_grows_to_fit_but_never_shrinks() -> None:
    with Diagram(layout="auto", width=400, height=300) as d:
        shapes = [d.shape(f"S{i}") for i in range(8)]
        for s, t in zip(shapes, shapes[1:]):
            s >> t
    assert d.width == shapes[-1].bounds.right + 60.0
    assert d.height == 300.0


def test_solve_is_idempotent() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", LayoutWarning)
        with Diagram(layout="auto") as d:
            with d.group("G"):
                a, b = d.shape("A"), d.shape("B")
                a >> b
            c = d.shape("C").right_of(b, margin=40)
        first = _bounds(d)
        d.solve()
    assert _bounds(d) == first


def test_manual_width_change_persists_across_resolve() -> None:
    with Diagram() as d:
        d.shape("A")
    d.width = 2000.0
    d.solve()
    assert d.width == 2000.0


def test_auto_user_width_larger_than_content_is_kept() -> None:
    with Diagram(layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    d.width = 5000.0
    d.solve()
    assert d.width == 5000.0


def test_configure_switches_layout_and_resolves_on_render() -> None:
    with Diagram() as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    d.configure(layout="auto")
    d.render_svg()
    assert a.bounds.right < b.bounds.x


def test_invalid_layout_options() -> None:
    with pytest.raises(ValueError, match="layout"):
        Diagram(layout="grid")
    with pytest.raises(ValueError, match="direction"):
        Diagram(direction="RL")


def test_a_layout_file_grows_the_canvas_in_manual_mode(tmp_path) -> None:
    with Diagram(layout="auto", width=400, height=300) as auto:
        a, b, c = auto.shape("A"), auto.shape("B"), auto.shape("C")
        a >> b >> c
    path = export_layout(auto, tmp_path / "chain.layout.json")

    with Diagram(width=400, height=300, layout_file=path) as replay:
        x, y, z = replay.shape("A"), replay.shape("B"), replay.shape("C")
        x >> y >> z

    assert (z.bounds.x, z.bounds.y) == (c.bounds.x, c.bounds.y)
    assert (replay.width, replay.height) == (auto.width, auto.height)
    assert z.bounds.right <= replay.width


def test_manual_canvas_grows_to_fit_content_placed_past_it() -> None:
    """Hand-placed content outside the declared canvas used to be clipped."""
    with Diagram(width=400, height=300) as d:
        a = d.shape("A").at(900, 700)
    assert d.width == a.bounds.right + 60.0
    assert d.height == a.bounds.bottom + 80.0


def test_canvas_that_already_fits_is_left_alone() -> None:
    with Diagram(width=400, height=300) as d:
        d.shape("A").at(60, 80)
    assert (d.width, d.height) == (400.0, 300.0)


def test_group_keeps_a_child_anchored_to_a_shape_outside_it() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", LayoutWarning)
        with Diagram(layout="auto", width=900, height=500) as d:
            anchor = d.shape("Anchor").at(700, 400)
            with d.group("G") as g:
                inside = d.shape("Inside").right_of(anchor, margin=10)
                other = d.shape("Other")
            inside >> other
    assert (inside.bounds.x, inside.bounds.y) == (anchor.bounds.right + 10.0, anchor.bounds.y)
    assert g.bounds.intersects(inside.bounds)


def test_resolve_edge_style_precedence() -> None:
    with Diagram(routing="curve", corner_radius=12.0, clearance=25.0) as d:
        s1, s2 = d.shape("A"), d.shape("B")

        # Edge 1: Inherits all diagram defaults
        e1 = Edge(source=s1, target=s2)
        st1 = resolve_edge_style(e1, d)
        assert st1 == EdgeStyle(routing=Routing.CURVE, corner_radius=12.0, clearance=25.0)

        # Edge 2: Overrides routing explicitly, corner_radius=0.0 forces sharp corners (D-03)
        e2 = Edge(source=s1, target=s2, routing="orthogonal", corner_radius=0.0)
        st2 = resolve_edge_style(e2, d)
        assert st2 == EdgeStyle(routing=Routing.ORTHOGONAL, corner_radius=0.0, clearance=25.0)


def test_diagram_configure_invalidates_cache() -> None:
    d = Diagram()
    d._is_solved = True
    d.configure(routing="curve")
    assert d._is_solved is False
    assert d.routing == Routing.CURVE


def test_resolve_edge_style_system_fallbacks() -> None:
    d = Diagram()
    s1, s2 = d.shape("A"), d.shape("B")
    e = Edge(source=s1, target=s2)
    style = resolve_edge_style(e, d)
    assert style == EdgeStyle(routing=Routing.ORTHOGONAL, corner_radius=0.0, clearance=15.0)


def test_diagram_connect_and_fluent_do_not_mutate_edge_instances() -> None:
    with Diagram(routing="curve", corner_radius=12.0, clearance=25.0) as d:
        s1, s2, s3 = d.shape("A"), d.shape("B"), d.shape("C")
        e_conn = d.connect(s1, s2)
        s2 >> s3

    e_fluent = d.edges[1]
    assert e_conn._routing is None
    assert e_conn._corner_radius is None
    assert e_conn._clearance is None
    assert e_fluent._routing is None
    assert e_fluent._corner_radius is None
    assert e_fluent._clearance is None

    assert resolve_edge_style(e_conn, d) == EdgeStyle(
        routing=Routing.CURVE, corner_radius=12.0, clearance=25.0
    )
    assert resolve_edge_style(e_fluent, d) == EdgeStyle(
        routing=Routing.CURVE, corner_radius=12.0, clearance=25.0
    )


def test_diagram_routing_validation() -> None:
    d = Diagram()
    assert d.routing is None

    d.routing = "curve"
    assert d.routing == Routing.CURVE

    d.routing = Routing.DIRECT
    assert d.routing == Routing.DIRECT

    d.routing = None
    assert d.routing is None

    with pytest.raises(TypeError, match="routing must be Routing or str"):
        d.routing = 123  # type: ignore

    with pytest.raises(ValueError):
        d.routing = "unknown_strategy"


def test_pipeline_routing_before_canvas_growth() -> None:
    with Diagram(layout="manual", width=500, height=300) as d:
        s1 = d.shape("A", width=50, height=50)
        s2 = d.shape("B", width=50, height=50)
        s1.at(50, 50)
        s2.at(400, 50)
        s1 >> s2
        e = d.edges[0]

    # Routes are keyed by both the edge and its id, and share one path object
    # that is also recorded on the edge itself.
    path = d.routes[e]
    assert isinstance(path, RoutedPath)
    assert d.routes[id(e)] is path
    assert e._resolved_path is path
    # Routing happened against the pre-growth scene: the endpoints sit at the
    # original (unshifted) element positions.
    assert path.points[0].x == pytest.approx(s1.bounds.right)
    assert path.points[-1].x == pytest.approx(s2.bounds.x)


def test_pipeline_routing_with_manual_waypoints() -> None:
    with Diagram(layout="manual", width=500, height=300) as d:
        s1 = d.shape("A", width=50, height=50)
        s2 = d.shape("B", width=50, height=50)
        s1.at(50, 50)
        s2.at(400, 50)
        s1 >> s2
        e = d.edges[0]
        e.manual_waypoints = [Point(50, 50), Point(200, 200), Point(400, 50)]

    path = d.routes[e] if e in d.routes else d.routes[id(e)]
    assert isinstance(path, RoutedPath)
    assert path.points == (Point(50, 50), Point(200, 200), Point(400, 50))


def test_canvas_grows_for_deflected_or_arching_edge() -> None:
    with Diagram(layout="manual", width=300, height=300, routing="curve") as d:
        s1 = d.shape("A", width=50, height=50)
        s2 = d.shape("B", width=50, height=50)
        s1.at(50, 90)
        s2.at(200, 90)
        # An edge between them arching high or obstacle in middle forcing detour
        obs = d.shape("Obs", width=60, height=60)
        obs.at(120, 80)
        s1 >> s2

    # Width grows to hold the rightmost element plus FRAME_X: 200 + 50 + 60 = 310.
    # The curve's bbox (y 65..115) fits inside the 300px height, so it stays put.
    assert d.width == 310.0
    assert d.height == 300.0


def test_canvas_grows_for_edge_extrema_beyond_elements() -> None:
    with Diagram(layout="manual", width=300, height=300) as d:
        s1 = d.shape("A", width=50, height=50).at(50, 50)
        s2 = d.shape("B", width=50, height=50).at(150, 50)
        s1 >> s2
        # Edge waypoints detour past the 300x300 canvas
        d.edges[0].manual_waypoints = [Point(100, 75), Point(350, 320), Point(150, 75)]

    # 350 + FRAME_X (60) = 410, 320 + FRAME_Y (80) = 400
    assert d.width == 410.0
    assert d.height == 400.0


def test_frame_translates_for_negative_edge_extrema() -> None:
    with Diagram(layout="manual", width=300, height=300, routing="curve") as d:
        s1 = d.shape("A", width=50, height=50).at(50, 15)
        s2 = d.shape("B", width=50, height=50).at(200, 15)
        obs = d.shape("Obs", width=60, height=60).at(120, 10)
        s1 >> s2

    # Obstacle deflects curve upwards to negative y (-5.0).
    # _frame must translate roots and routes by offset_y = -(-5.0) + 80.0 = 85.0.
    # Elements at y=15 shift to 100.0, obstacle at y=10 shifts to 95.0.
    # The curve's minimum y must be >= FRAME_Y (80.0).
    edge = d.edges[0]
    path = d.routes[edge]
    assert path.bbox().y >= 80.0
    assert s1.bounds.y == 100.0
    assert obs.bounds.y == 95.0
    assert edge._resolved_path is not None
    assert edge._resolved_path.bbox().y >= 80.0



def test_frame_translates_for_negative_x_extrema() -> None:
    with Diagram(layout="manual", width=300, height=300) as d:
        s1 = d.shape("A", width=50, height=50).at(50, 50)
        s2 = d.shape("B", width=50, height=50).at(150, 50)
        s1 >> s2
        d.edges[0].manual_waypoints = [Point(100, 75), Point(-40, 150), Point(150, 75)]

    # min x = -40 shifts everything right by 60 - (-40) = 100.
    assert s1.bounds.x == 150.0
    assert s2.bounds.x == 250.0
    assert d.routes[d.edges[0]].bbox().x == 60.0


def test_canvas_already_large_enough_does_not_grow_or_shift() -> None:
    with Diagram(layout="manual", width=800, height=600) as d:
        s1 = d.shape("A", width=50, height=50).at(100, 100)
        s2 = d.shape("B", width=50, height=50).at(300, 100)
        s1 >> s2

    assert (d.width, d.height) == (800.0, 600.0)
    assert (s1.bounds.x, s1.bounds.y) == (100.0, 100.0)


def test_extrema_on_both_axes_shift_and_grow_together() -> None:
    with Diagram(layout="manual", width=300, height=300) as d:
        s1 = d.shape("A", width=50, height=50).at(50, 50)
        s2 = d.shape("B", width=50, height=50).at(150, 50)
        s1 >> s2
        d.edges[0].manual_waypoints = [Point(100, 75), Point(-20, -30), Point(350, 320)]

    # offset_x = 60 + 20 = 80, offset_y = 80 + 30 = 110
    assert (s1.bounds.x, s1.bounds.y) == (130.0, 160.0)
    box = d.routes[d.edges[0]].bbox()
    assert (box.x, box.y) == (60.0, 80.0)
    assert d.width == 350.0 + 80.0 + 60.0
    assert d.height == 320.0 + 110.0 + 80.0


def test_pipeline_does_not_mutate_waypoints_and_is_repeatable() -> None:
    waypoints = [Point(100, 75), Point(-40, 150), Point(150, 75)]
    with Diagram(layout="manual", width=300, height=300) as d:
        s1 = d.shape("A", width=50, height=50).at(50, 50)
        s2 = d.shape("B", width=50, height=50).at(150, 50)
        s1 >> s2
        d.edges[0].manual_waypoints = list(waypoints)

    assert d.edges[0].manual_waypoints == waypoints
    first = d.routes[d.edges[0]]
    d.solve()
    assert d.routes[d.edges[0]] == first
