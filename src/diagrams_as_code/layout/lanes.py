"""Move apart orthogonal edges that were routed along the same lane.

Each edge is routed on its own, so two detours around the same obstacle pick
the same corridor and are drawn on top of each other. This pass finds interior
segments of different edges that run along one line and shifts all but one of
them sideways onto a free parallel lane. An end segment is moved only when no
interior one can be, by sliding its port along the node side; arrival
directions are untouched. Edges that may share a line (one
source, one target, or an exact bus) are left alone.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Optional, Sequence

from diagrams_as_code.connections import may_share_a_line
from diagrams_as_code.geometry import PathKind, Point, Rect, RoutedPath, segment_enters

#: Distance between neighbouring lanes; clears a badge sitting on the next lane.
PITCH = 14.0
#: Lanes tried on each side of the original one.
MAX_LANES = 4
#: Overlap shorter than this is a crossing or a touch, not a shared run.
MIN_RUN = 6.0
#: A port moved along a node side stays this far from the corners.
PORT_MARGIN = 8.0
EPS = 0.5

Segment = tuple[Point, Point]


def _shared(s1: Segment, s2: Segment) -> float:
    """Length two axis-aligned segments run on top of each other."""
    (a, b), (c, d) = s1, s2
    if abs(a.y - b.y) <= EPS and abs(c.y - d.y) <= EPS and abs(a.y - c.y) <= EPS:
        return min(max(a.x, b.x), max(c.x, d.x)) - max(min(a.x, b.x), min(c.x, d.x))
    if abs(a.x - b.x) <= EPS and abs(c.x - d.x) <= EPS and abs(a.x - c.x) <= EPS:
        return min(max(a.y, b.y), max(c.y, d.y)) - max(min(a.y, b.y), min(c.y, d.y))
    return 0.0


def _orthogonal(pts: Sequence[Point]) -> bool:
    return all(abs(a.x - b.x) <= EPS or abs(a.y - b.y) <= EPS for a, b in zip(pts, pts[1:]))


def _shifted(pts: list[Point], i: int, offset: float) -> Optional[list[Point]]:
    """``pts`` with segment ``i`` moved sideways, or None if that would fold the path."""
    a, b = pts[i], pts[i + 1]
    horizontal = abs(a.y - b.y) <= EPS
    dx, dy = (0.0, offset) if horizontal else (offset, 0.0)
    out = list(pts)
    out[i], out[i + 1] = Point(a.x + dx, a.y + dy), Point(b.x + dx, b.y + dy)
    # The neighbours must stay perpendicular stubs that still point the same way.
    for j in (i - 1, i + 1):
        if j < 0 or j + 1 >= len(pts):
            continue
        before = (pts[j + 1].x - pts[j].x, pts[j + 1].y - pts[j].y)
        after = (out[j + 1].x - out[j].x, out[j + 1].y - out[j].y)
        if before[0] * after[0] + before[1] * after[1] <= 0.0:
            return None
        if abs(after[0]) > EPS and abs(after[1]) > EPS:
            return None
    return out


def _on_side(p: Point, box: Rect) -> bool:
    """True if ``p`` is on the border of ``box``, clear of its corners."""
    on_x = abs(p.x - box.left) <= EPS or abs(p.x - box.right) <= EPS
    on_y = abs(p.y - box.top) <= EPS or abs(p.y - box.bottom) <= EPS
    if on_x and box.top + PORT_MARGIN <= p.y <= box.bottom - PORT_MARGIN:
        return True
    return on_y and box.left + PORT_MARGIN <= p.x <= box.right - PORT_MARGIN


def separate_lanes(edges: Sequence[Any], routes: dict[Any, RoutedPath], nodes: Sequence[Rect]) -> None:
    """Shift overlapping interior segments of unrelated edges onto separate lanes."""
    links = {(id(e.source), id(e.target)) for e in edges}

    def _related(e1: Any, e2: Any) -> bool:
        return may_share_a_line(e1, e2, links)

    movable: list[Any] = []
    points: dict[int, list[Point]] = {}
    for edge in edges:
        path = routes.get(edge)
        if path is None:
            continue
        pts = list(path.points)
        if path.kind != PathKind.POLYLINE or not _orthogonal(pts):
            continue
        points[id(edge)] = pts
        if not getattr(edge, "manual_waypoints", None) and len(pts) >= 3:
            movable.append(edge)

    def segments(edge: Any) -> list[Segment]:
        pts = points[id(edge)]
        return list(zip(pts, pts[1:]))

    def clashes(edge: Any, pts: list[Point], i: int) -> bool:
        """True if segment ``i`` of ``pts``, or a stub beside it, is in the way."""
        for j in (i - 1, i, i + 1):
            if j < 0 or j + 1 >= len(pts):
                continue
            seg = (pts[j], pts[j + 1])
            if any(segment_enters(seg[0], seg[1], n) for n in nodes):
                return True
            for other in edges:
                if other is edge or id(other) not in points or _related(edge, other):
                    continue
                if any(_shared(seg, s) > MIN_RUN for s in segments(other)):
                    return True
        return False

    changed: set[int] = set()
    # A second pass lets a segment move once its neighbour's port has slid clear.
    for edge in movable + movable:
        pts = points[id(edge)]
        # Interior segments first; an end segment moves its port, so only if needed.
        last = len(pts) - 2
        for i in list(range(1, last)) + [0, last]:
            seg = (pts[i], pts[i + 1])
            overlapping = any(
                _shared(seg, s) > MIN_RUN
                for other in edges
                if other is not edge and id(other) in points and not _related(edge, other)
                for s in segments(other)
            )
            if not overlapping:
                continue

            def usable(cand: Optional[list[Point]]) -> bool:
                if cand is None or clashes(edge, cand, i):
                    return False
                if i == 0 and not _on_side(cand[0], edge.source.bounds):
                    return False
                if i == last and not _on_side(cand[-1], edge.target.bounds):
                    return False
                return True

            for lane in range(1, MAX_LANES + 1):
                moved = next(
                    (
                        cand for cand in (_shifted(pts, i, lane * PITCH), _shifted(pts, i, -lane * PITCH))
                        if usable(cand)
                    ),
                    None,
                )
                if moved is not None:
                    pts = points[id(edge)] = moved
                    changed.add(id(edge))
                    break

    for edge in movable:
        if id(edge) in changed:
            path = dataclasses.replace(routes[edge], points=tuple(points[id(edge)]))
            routes[edge] = routes[id(edge)] = path
            edge._resolved_path = path
