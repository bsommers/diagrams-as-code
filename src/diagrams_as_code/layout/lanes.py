"""Move apart orthogonal edges that were routed along the same lane.

Each edge is routed on its own, so two detours around the same obstacle pick
the same corridor and are drawn on top of each other. This pass finds interior
segments of different edges that run along one line and shifts all but one of
them sideways onto a free parallel lane. End segments stay where they are, so
ports and arrival directions are untouched. Edges that may share a line (one
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
    """``pts`` with interior segment ``i`` moved sideways, or None if that would fold the path."""
    a, b = pts[i], pts[i + 1]
    horizontal = abs(a.y - b.y) <= EPS
    dx, dy = (0.0, offset) if horizontal else (offset, 0.0)
    out = list(pts)
    out[i], out[i + 1] = Point(a.x + dx, a.y + dy), Point(b.x + dx, b.y + dy)
    # The neighbours must stay perpendicular stubs that still point the same way.
    for p, q, r, s in ((pts[i - 1], a, out[i - 1], out[i]), (b, pts[i + 2], out[i + 1], out[i + 2])):
        before = (q.x - p.x, q.y - p.y)
        after = (s.x - r.x, s.y - r.y)
        if before[0] * after[0] + before[1] * after[1] <= 0.0:
            return None
        if abs(after[0]) > EPS and abs(after[1]) > EPS:
            return None
    return out


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
        if not getattr(edge, "manual_waypoints", None) and len(pts) >= 4:
            movable.append(edge)

    def segments(edge: Any) -> list[Segment]:
        pts = points[id(edge)]
        return list(zip(pts, pts[1:]))

    def clashes(edge: Any, pts: list[Point], i: int) -> bool:
        """True if segment ``i`` of ``pts``, or a stub beside it, is in the way."""
        for j in (i - 1, i, i + 1):
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
    for edge in movable:
        pts = points[id(edge)]
        for i in range(1, len(pts) - 2):
            seg = (pts[i], pts[i + 1])
            overlapping = any(
                _shared(seg, s) > MIN_RUN
                for other in edges
                if other is not edge and id(other) in points and not _related(edge, other)
                for s in segments(other)
            )
            if not overlapping:
                continue
            for lane in range(1, MAX_LANES + 1):
                moved = next(
                    (
                        cand for cand in (_shifted(pts, i, lane * PITCH), _shifted(pts, i, -lane * PITCH))
                        if cand is not None and not clashes(edge, cand, i)
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
