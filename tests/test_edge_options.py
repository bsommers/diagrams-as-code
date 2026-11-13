"""PRIM-05 / PRIM-06: line weights, arrowheads, anchors, points, trunks, leaders, splines."""
from __future__ import annotations

import re
import warnings

import pytest

from diagrams_as_code import AnchorRef, Diagram, Edge, Junction, PathKind, Point, Port, Routing, Shape
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.geometry import flatten


def _pair(**edge):
    with Diagram("t", theme="paper") as d:
        a = d.shape("A", 100, 40).at(60, 60)
        b = d.shape("B", 100, 40).at(400, 60)
        e = d.connect(a, b, **edge)
    return d, a, b, e


def _edge_lines(svg: str) -> list[str]:
    """Markup between the last node backdrop and the first node: the edges."""
    return [ln for ln in svg.splitlines() if ln.startswith("  <path")]


# ------------------------------------------------------- PRIM-05 weights, heads


def test_default_edge_is_unchanged_markers_and_theme_weight():
    d, *_ = _pair()
    (line,) = _edge_lines(d.render_svg())
    assert 'marker-end="url(#arrow)"' in line and 'stroke-width="1"' in line


def test_width_sets_the_stroke_and_draws_the_head_as_a_shape():
    d, a, b, _ = _pair(width=3)
    line, head = _edge_lines(d.render_svg())
    assert 'stroke-width="3"' in line and "marker" not in line
    assert 'fill="#000000"' in head and head.count(" L ") == 2
    # The head's point is on the target; the line stops inside the head, not at the tip.
    assert f"M {b.bounds.left:g} 80" in head
    end_x = float(re.search(r"L ([\d.]+) 80", line).group(1))
    assert b.bounds.left - 18 < end_x < b.bounds.left


@pytest.mark.parametrize("head", ["stealth", "open", "diamond", "circle", "bar"])
def test_each_head_style_is_drawn_at_the_target(head):
    d, a, b, _ = _pair(head=head)
    line, shape = _edge_lines(d.render_svg())
    assert "marker" not in line
    xs = [float(v) for v in re.findall(r"(?:M|L|C|,)? ?(\d+\.?\d*) (?:80|7\d|8\d)", shape)]
    assert max(xs) == pytest.approx(b.bounds.left, abs=0.01)


def test_head_none_and_arrow_head_false_draw_a_bare_line():
    for kwargs in ({"head": "none"}, {"arrow_head": False}, {"head": "none", "width": 2}):
        d, *_ = _pair(**kwargs)
        lines = _edge_lines(d.render_svg())
        assert len(lines) == 1 and "marker" not in lines[0], kwargs


def test_two_way_arrow_has_a_head_at_each_end():
    d, a, b, e = _pair(two_way=True)
    assert e.arrow_head and e.arrow_tail
    (line,) = _edge_lines(d.render_svg())
    assert "marker-start" in line and "marker-end" in line
    d, a, b, e = _pair(two_way=True, head="stealth", tail="circle")
    line, head, tail = _edge_lines(d.render_svg())
    assert f"M {b.bounds.left:g} 80" in head and " C " in tail


def test_arrow_size_scales_the_head():
    def head_length(**kwargs):
        d, a, b, _ = _pair(**kwargs)
        head = _edge_lines(d.render_svg())[1]
        xs = [float(x) for x in re.findall(r"[ML] ([\d.]+) ", head)]
        return max(xs) - min(xs)

    assert head_length(width=1, arrow_size=2) == pytest.approx(2 * head_length(width=1))
    assert head_length(width=4) > head_length(width=1)


def test_custom_edges_keep_colour_dash_and_curve():
    d, *_ = _pair(width=2, color="#AA0000", style="dashed", routing="curve")
    line, head = _edge_lines(d.render_svg())
    assert 'stroke="#AA0000"' in line and "stroke-dasharray" in line and " C " in line
    assert 'fill="#AA0000"' in head


def test_ellipsis_replaces_the_middle_with_three_dots():
    d, a, b, _ = _pair(ellipsis=True)
    lines = _edge_lines(d.render_svg())
    segments = [ln for ln in lines if 'fill="none"' in ln]
    dots = [ln for ln in lines if " C " in ln and 'fill="#000000"' in ln]
    assert len(segments) == 2 and len(dots) == 3
    mid = (a.bounds.right + b.bounds.left) / 2
    centres = sorted(float(re.search(r"M ([\d.]+) ", ln).group(1)) for ln in dots)
    assert centres[1] - 1.25 == pytest.approx(mid, abs=0.01)  # each path starts at the dot's right edge
    first_end = float(re.findall(r"L ([\d.]+) 80", segments[0])[-1])
    assert first_end < centres[0] - 1.25


@pytest.mark.parametrize(
    "kwargs", [{"head": "fancy"}, {"tail": "x"}, {"width": 0}, {"width": float("nan")}, {"arrow_size": -1}]
)
def test_bad_edge_options_are_rejected(kwargs):
    a, b = Shape("a", "A"), Shape("b", "B")
    with pytest.raises(ValueError):
        Edge(a, b, **kwargs)


def test_options_pass_through_the_fluent_builder_and_interactive_mode():
    with Diagram("t", theme="paper", interactive=True) as d:
        a = d.shape("A").at(60, 60)
        b = d.shape("B").at(400, 60)
        a >> d.edge("go", width=2.5, head="open", z=1) >> b
    e = d.edges[0]
    assert (e.width, e.head, e.z, e.label) == (2.5, "open", 1.0, "go")
    assert 'stroke-width="2.5"' in d.render_svg()
    with pytest.raises(TypeError):
        d.edge(colour="red")


# ------------------------------------------------- PRIM-06 fractional anchors


@pytest.mark.parametrize(
    "side, fraction, expected",
    [("right", 0.25, (200, 110)), ("left", 0.75, (100, 130)), ("top", 0.1, (110, 100)), ("bottom", 1.0, (200, 140))],
)
def test_anchor_point(side, fraction, expected):
    box = Shape("b", "B", 100, 40).at(100, 100)
    ref = box.anchor(side, fraction)
    assert isinstance(ref, AnchorRef) and (ref.point.x, ref.point.y) == expected


def test_anchor_accepts_compass_names_and_rejects_nonsense():
    box = Shape("b", "B")
    assert box.anchor("east").side == box.anchor(Port.EAST).side == box.anchor("right").side == "east"
    with pytest.raises(ValueError):
        box.anchor("middle")
    with pytest.raises(ValueError):
        box.anchor("left", 1.5)


def test_edge_ends_where_its_anchors_say():
    with Diagram("t", theme="paper") as d:
        a = d.shape("A", 100, 80).at(60, 60)
        b = d.shape("B", 100, 200).at(400, 60)
        e = d.connect(a.anchor("right", 0.25), b.anchor("left", 0.1))
    pts = d.routes[e].points
    assert (pts[0].x, pts[0].y) == (160, 80) and (pts[-1].x, pts[-1].y) == (400, 80)
    assert len(pts) == 2  # level anchors give a straight line
    assert (e.source_port, e.target_port) == (Port.EAST, Port.WEST)
    assert not audit_diagram(d)


def test_anchors_work_with_the_shift_operator_lists_and_builders():
    with Diagram("t", theme="paper") as d:
        hub = d.shape("Hub", 100, 200).at(400, 60)
        ins = [d.shape(f"in{i}", 80, 30).at(60, 70 + i * 50) for i in range(3)]
        for i, source in enumerate(ins):
            source >> hub.anchor("left", (i + 0.5) / 4)
        out = d.shape("Out", 80, 30).at(700, 145)
        hub.anchor("right", 0.5) >> d.edge("y", width=2) >> out
        [ins[0].anchor("top", 0.5)] >> d.edge(style="dashed") >> out.anchor("top", 0.5)
    assert len(d.edges) == 5
    assert [d.routes[e].points[-1].y for e in d.edges[:3]] == [85, 135, 185]
    assert d.edges[3].width == 2 and d.edges[3].source is hub and d.edges[4].target_port == Port.NORTH


def test_anchored_ends_are_not_moved_by_port_spreading_or_lane_separation():
    with Diagram("t", theme="paper") as d:
        a = d.shape("A", 100, 100).at(60, 60)
        b = d.shape("B", 100, 100).at(400, 60)
        out = d.connect(a.anchor("right", 0.5), b.anchor("left", 0.5))
        back = d.connect(b, a, source_port=Port.WEST, target_port=Port.EAST)
    pts = d.routes[out].points
    assert pts[0].y == 110 and pts[-1].y == 110  # exactly the middle, though the side is shared
    assert d.routes[back].points[0].y != 110


def test_resolving_after_moving_an_anchor_reroutes():
    d, a, b, e = _pair()
    before = d.routes[e].points[0].y
    e.source_anchor, e.source_port = 0.0, Port.EAST
    d.render_svg()
    assert d.routes[e].points[0].y < before


# ----------------------------------------------------- PRIM-06 point endpoints


def test_a_bare_point_is_an_endpoint():
    with Diagram("t", theme="paper") as d:
        box = d.shape("B", 100, 40).at(300, 100)
        e1 = d.connect((60, 120), box, routing="direct")
        e2 = d.connect(box, Point(600, 120), routing="direct")
    assert (d.routes[e1].points[0].x, d.routes[e1].points[0].y) == (60, 120)
    assert (d.routes[e2].points[-1].x, d.routes[e2].points[-1].y) == (600, 120)
    assert isinstance(e1.source, Junction) and e1.source in d.shapes and e1.source.id != e2.target.id
    assert d.width >= 600  # the canvas reaches the far point
    assert not audit_diagram(d)
    assert d.bom.items() == [{"id": box.id, "label": "B", "kind": "box", "group": None, "metadata": {}}]
    assert f'id="{e1.source.id}"' not in d.render_svg()  # an undotted point draws nothing


def test_points_shift_with_the_drawing_when_it_is_framed():
    with Diagram("t", theme="paper") as d:
        box = d.shape("B", 100, 40).at(-200, 100)
        e = d.connect((-300, 120), box, routing="direct")
    start = d.routes[e].points[0]
    assert start.x >= 0 and box.bounds.left - start.x == pytest.approx(100)


def test_junction_dot_joins_three_lines():
    with Diagram("t", theme="paper") as d:
        a = d.shape("A", 80, 40).at(60, 100)
        j = d.point(300, 120, dot=True, id="tee")
        b = d.shape("B", 80, 40).at(500, 40)
        c = d.shape("C", 80, 40).at(500, 160)
        d.connect(a, j, arrow_head=False)
        d.connect(j, b)
        d.connect(j, c)
    assert all(d.routes[e].points[0 if e.source is j else -1] == Point(300, 120) for e in d.edges)
    block = d.render_svg().split('<g id="tee"')[1].split("</g>")[0]
    assert " C " in block and 'fill="#000000"' in block
    assert not audit_diagram(d)


def test_points_are_pinned_under_auto_layout():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with Diagram("t", theme="paper", layout="auto") as d:
            a, b = d.shape("A"), d.shape("B")
            a >> b
            j = d.point(700, 500)
    assert (j.bounds.x, j.bounds.y) == (700, 500)


def test_edge_without_a_diagram_accepts_points_and_rejects_junk():
    e = Edge((10, 20), Shape("b", "B"))
    assert isinstance(e.source, Junction) and (e.source.bounds.x, e.source.bounds.y) == (10, 20)
    for junk in ("a", 5, (1, 2, 3), None):
        with pytest.raises(TypeError):
            Edge(junk, Shape("b", "B"))


# ------------------------------------------------------ PRIM-06 shared trunk


def test_fan_out_shares_one_trunk_then_splits():
    with Diagram("t", theme="paper") as d:
        src = d.shape("S", 100, 40).at(300, 60)
        sinks = [d.shape(f"T{i}", 80, 40).at(100 + i * 220, 240) for i in range(3)]
        edges = d.fan_out(src, sinks, trunk=50, source_port=Port.SOUTH, target_port=Port.NORTH)
    routes = [d.routes[e].points for e in edges]
    assert {(p[0].x, p[0].y) for p in routes} == {(350, 100)}
    assert {(p[1].x, p[1].y) for p in routes} == {(350, 150)}  # the split, 50 px out
    for pts, sink in zip(routes, sinks):
        assert pts[-1] == Point(sink.bounds.center.x, 240) and pts[-2].y == 150
    assert not audit_diagram(d)  # one source: the shared run is not an overlap defect


def test_fan_in_merges_before_the_target_and_horizontal_trunks_work():
    with Diagram("t", theme="paper") as d:
        sources = [d.shape(f"S{i}", 80, 40).at(60, 60 + i * 100) for i in range(3)]
        sink = d.shape("T", 100, 40).at(500, 160)
        edges = d.fan_in(sources, sink, trunk=60, source_port=Port.EAST, target_port=Port.WEST)
    for e in edges:
        pts = d.routes[e].points
        assert pts[-1] == Point(500, 180)
        if len(pts) > 2:
            assert pts[-2] == Point(440, 180) and pts[1].x == 440
    assert not audit_diagram(d)


def test_trunk_resolves_its_own_ports_when_none_are_given():
    with Diagram("t", theme="paper") as d:
        src = d.shape("S", 100, 40).at(60, 200)
        sinks = [d.shape(f"T{i}", 80, 40).at(400, 100 + i * 120) for i in range(3)]
        edges = d.fan_out(src, sinks, trunk=40)
    assert {d.routes[e].points[1].x for e in edges if len(d.routes[e].points) > 2} == {200}


# ------------------------------------------------- PRIM-06 splines, via, leaders


def test_spline_passes_through_its_via_points_smoothly():
    via = [(200, 20), (330, 180)]
    with Diagram("t", theme="paper") as d:
        a = d.shape("A", 80, 40).at(60, 80)
        b = d.shape("B", 80, 40).at(440, 80)
        e = d.connect(a, b, routing="spline", via=via)
    path = d.routes[e]
    assert path.kind == PathKind.BEZIER_CHAIN and e.routing == Routing.SPLINE
    knots = path.points[::3]
    assert [(p.x, p.y) for p in knots[1:-1]] == via
    # Smooth: the control points either side of a knot are collinear with it.
    for i in (3, 6):
        before, knot, after = path.points[i - 1], path.points[i], path.points[i + 1]
        cross = (knot.x - before.x) * (after.y - knot.y) - (knot.y - before.y) * (after.x - knot.x)
        assert abs(cross) < 1e-6
    # Ends leave from the sides facing the first and last via point.
    assert path.points[0].y == a.bounds.top or path.points[0].x == a.bounds.right
    assert " C " in d.render_svg()


def test_via_with_other_routing_is_straight_runs_and_keeps_explicit_ports():
    with Diagram("t", theme="paper") as d:
        a = d.shape("A", 80, 40).at(60, 80)
        b = d.shape("B", 80, 40).at(440, 80)
        e = d.connect(a, b, via=[(250, 200)], source_port=Port.SOUTH, target_port=Port.SOUTH)
        f = d.connect(a, b, via=[(250, 20)], corner_radius=8)
    pts = d.routes[e].points
    assert d.routes[e].kind == PathKind.POLYLINE
    assert [(p.x, p.y) for p in pts] == [(100, 120), (250, 200), (480, 120)]
    assert d.routes[f].corner_radius == 8 and d.routes[f].points[0] == Point(100, 80)


def test_spline_without_via_is_an_ordinary_curve():
    d, a, b, e = _pair(routing="spline")
    assert d.routes[e].kind == PathKind.BEZIER_CHAIN
    assert flatten(d.routes[e])[0] == Point(a.bounds.right, a.bounds.center.y)


def test_via_must_be_points():
    with pytest.raises(TypeError):
        Edge(Shape("a", "A"), Shape("b", "B"), via=["x"])


def test_leader_is_a_note_with_a_thin_line_that_stops_short_of_the_letters():
    with Diagram("t", theme="paper") as d:
        box = d.shape("B", 120, 60).at(300, 200)
        note = d.leader("see here", box.anchor("top", 0.25), at=(80, 60), head="circle")
        plain = d.leader("and here", (500, 120), at=(560, 40))
    e, f = d.edges
    assert e.source is note and (e.width, e.head, e.routing) == (0.75, "circle", Routing.DIRECT)
    assert d.routes[e].points[-1] == Point(330, 200)
    assert note.padding == 3 and note.size == 11
    assert f.arrow_head is False and d.routes[f].points[-1] == Point(500, 120)
    assert "see here" in d.render_svg()
    assert [i["label"] for i in d.bom.items()] == ["B"]
    assert not audit_diagram(d)


def test_unnamed_points_do_not_break_the_layout_file(tmp_path):
    from diagrams_as_code import export_layout, load_layout_file

    with Diagram("t", theme="paper") as d:
        box = d.shape("B", 100, 40).at(300, 100)
        d.connect((60, 120), box, routing="direct")
        d.connect(box, (600, 120), routing="direct")
        d.point(300, 300, id="tee")
        d.polygon([(0, 0), (40, 0), (20, 30)], obstacle=False)
    entries = load_layout_file(export_layout(d, tmp_path / "layout.json"))
    assert sorted(entries) == ["B", "tee"]  # named elements only; two anonymous points are not a clash
