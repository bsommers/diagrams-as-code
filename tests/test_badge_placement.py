"""LAYOUT-02: edge badges avoid nodes, other badges and other edges' lines."""
from __future__ import annotations

from diagrams_as_code import Diagram
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.geometry import PathKind, Point, Rect, RoutedPath
from diagrams_as_code.labels import edge_badge_rect
from diagrams_as_code.layout.badges import place_badges


class _Edge:
    def __init__(self, label: str) -> None:
        self.label = label
        self.metadata: dict = {}


def _line(*pts: tuple[float, float]) -> RoutedPath:
    return RoutedPath(kind=PathKind.POLYLINE, points=tuple(Point(x, y) for x, y in pts))


def test_clear_badge_stays_at_the_midpoint():
    e = _Edge("MQTT")
    routes = {e: _line((0, 0), (200, 0))}
    place_badges([e], routes, [])
    assert e._label_anchor == Point(100, 0) and e._label_wrap is None and e._label_owner is None


def test_badge_slides_off_a_node():
    e = _Edge("MQTT")
    path = _line((0, 0), (400, 0))
    node = Rect(170, -30, 60, 60)
    place_badges([e], {e: path}, [node])
    rect = edge_badge_rect(e, path)
    assert rect.right <= node.left or rect.left >= node.right
    assert e._label_anchor.y == 0


def test_badge_slides_off_a_crossing_line():
    e, other = _Edge("MQTT"), _Edge("")
    path = _line((0, 0), (400, 0))
    routes = {e: path, other: _line((200, -100), (200, 100))}
    place_badges([e, other], routes, [])
    rect = edge_badge_rect(e, path)
    assert not rect.left < 200 < rect.right


def test_two_badges_do_not_overlap():
    a, b = _Edge("Alpha"), _Edge("Beta")
    routes = {a: _line((0, 0), (300, 0)), b: _line((0, 6), (300, 6))}
    place_badges([a, b], routes, [])
    ra, rb = edge_badge_rect(a, routes[a]), edge_badge_rect(b, routes[b])
    assert ra.right <= rb.left or rb.right <= ra.left or ra.bottom <= rb.top or rb.bottom <= ra.top


def test_long_label_in_a_short_gap_is_wrapped():
    e = _Edge("Upload Police Report & Photos")
    path = _line((120, 30), (250, 30))
    nodes = [Rect(0, 0, 120, 60), Rect(250, 0, 120, 60)]
    place_badges([e], {e: path}, nodes)
    rect = edge_badge_rect(e, path)
    assert e._label_wrap is not None
    assert rect.left >= 120 and rect.right <= 250


def test_same_label_on_a_shared_trunk_gets_one_badge():
    a, b = _Edge("ECMP"), _Edge("ECMP")
    routes = {a: _line((0, 0), (200, 0)), b: _line((0, 0), (200, 0), (200, 80))}
    place_badges([a, b], routes, [])
    assert b._label_owner is a
    assert edge_badge_rect(b, routes[b]) is None
    assert edge_badge_rect(a, routes[a]) is not None


def test_different_labels_on_a_shared_trunk_keep_their_own_badges():
    a, b = _Edge("ECMP"), _Edge("BGP")
    routes = {a: _line((0, 0), (200, 0)), b: _line((0, 0), (200, 0), (200, 80))}
    place_badges([a, b], routes, [])
    assert a._label_owner is None and b._label_owner is None


def test_replacing_resets_previous_choices():
    e = _Edge("Upload Police Report & Photos")
    place_badges([e], {e: _line((120, 30), (250, 30))}, [Rect(0, 0, 120, 60), Rect(250, 0, 120, 60)])
    place_badges([e], {e: _line((0, 0), (600, 0))}, [])
    assert e._label_wrap is None and e._label_anchor == Point(300, 0)


def test_diagram_badges_are_drawn_where_the_audit_looks():
    with Diagram("t", theme="monochrome") as d:
        a = d.shape("A", width=120, height=60).at(60, 80)
        b = d.shape("B", width=120, height=60).at(310, 80)
        d.connect(a, b, label="Upload Police Report & Photos")
    svg = d.render_svg()
    counts = audit_diagram(d)
    assert "badge_over_node" not in counts
    assert svg.count('class="badge"') == 1


def test_badge_sits_beside_its_line_when_the_line_is_shared_end_to_end():
    e, other = _Edge("Alpha"), _Edge("Beta")
    path = _line((0, 0), (120, 0))
    routes = {e: path, other: _line((0, 0), (120, 0))}
    place_badges([other, e], routes, [])
    rect = edge_badge_rect(e, path)
    assert rect.bottom < 0 or rect.top > 0
