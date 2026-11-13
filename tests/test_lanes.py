"""LAYOUT-03: unrelated edges do not run along the same line."""
from __future__ import annotations

from diagrams_as_code import Diagram
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.connections import may_share_a_line
from diagrams_as_code.geometry import PathKind, Point, Rect, RoutedPath
from diagrams_as_code.layout.lanes import PITCH, separate_lanes


class _Node:
    pass


class _Edge:
    def __init__(self, source=None, target=None) -> None:
        self.source, self.target = source or _Node(), target or _Node()
        self.manual_waypoints = None
        self._resolved_path = None


def _line(*pts: tuple[float, float]) -> RoutedPath:
    return RoutedPath(kind=PathKind.POLYLINE, points=tuple(Point(x, y) for x, y in pts))


def _ys(path: RoutedPath) -> list[float]:
    return [p.y for p in path.points]


def test_overlapping_detours_are_moved_to_separate_lanes():
    a, b = _Edge(), _Edge()
    routes = {
        a: _line((0, 0), (20, 0), (20, 100), (300, 100), (300, 0), (320, 0)),
        b: _line((200, 0), (220, 0), (220, 100), (500, 100), (500, 0), (520, 0)),
    }
    separate_lanes([a, b], routes, [])
    lanes = {_ys(routes[a])[2], _ys(routes[b])[2]}
    assert len(lanes) == 2 and abs(max(lanes) - min(lanes)) == PITCH
    # End points never move.
    assert routes[a].points[0] == Point(0, 0) and routes[a].points[-1] == Point(320, 0)
    assert routes[b].points[0] == Point(200, 0) and routes[b].points[-1] == Point(520, 0)
    assert a._resolved_path is routes[a] or b._resolved_path is routes[b]


def test_fan_out_trunk_is_left_alone():
    src = _Node()
    a, b = _Edge(source=src), _Edge(source=src)
    before = {
        a: _line((0, 0), (20, 0), (20, 100), (300, 100), (300, 0), (320, 0)),
        b: _line((0, 0), (20, 0), (20, 100), (500, 100), (500, 0), (520, 0)),
    }
    routes = dict(before)
    separate_lanes([a, b], routes, [])
    assert routes == before


def test_a_lane_inside_a_node_is_not_used():
    a, b = _Edge(), _Edge()
    routes = {
        a: _line((0, 0), (20, 0), (20, 100), (300, 100), (300, 0), (320, 0)),
        b: _line((200, 0), (220, 0), (220, 100), (500, 100), (500, 0), (520, 0)),
    }
    below = Rect(0, 104, 600, 40)
    separate_lanes([a, b], routes, [below])
    moved = [e for e in (a, b) if _ys(routes[e])[2] != 100]
    assert len(moved) == 1 and _ys(routes[moved[0]])[2] == 100 - PITCH


def test_exact_bus_may_share_a_line_but_a_partial_one_may_not():
    s1, s2, t1, t2 = _Node(), _Node(), _Node(), _Node()
    e1, e2 = _Edge(s1, t1), _Edge(s2, t2)
    full = {(id(s1), id(t1)), (id(s2), id(t2)), (id(s1), id(t2)), (id(s2), id(t1))}
    partial = {(id(s1), id(t1)), (id(s2), id(t2))}
    assert may_share_a_line(e1, e2, full)
    assert not may_share_a_line(e1, e2, partial)


def test_opposite_edges_between_one_pair_are_two_straight_lines():
    with Diagram("t", theme="monochrome") as d:
        a = d.shape("A", width=120, height=60).at(60, 80)
        b = d.shape("B", width=120, height=60).at(310, 80)
        c = d.shape("C", width=120, height=60).at(560, 80)
        d.connect(a, b, label="Request")
        d.connect(b, a, label="Accept")
        d.connect(b, c)
    d.solve()
    there, back = d.routes[d.edges[0]], d.routes[d.edges[1]]
    assert len(there.points) == 2 and len(back.points) == 2
    assert there.points[0].y == there.points[1].y != back.points[0].y
    assert "edge_on_edge" not in audit_diagram(d)
