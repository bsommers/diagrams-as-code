"""Move apart orthogonal edges that were routed along the same lane.

Each edge is routed on its own, so two detours around the same obstacle pick
the same corridor and are drawn on top of each other. This pass finds interior
segments of different edges that run along one line and shifts all but one of
them sideways onto a parallel lane, whenever that shortens the overlap. An end segment is moved only when no
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
PASSES = 3

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

    def overlap(edge: Any, pts: list[Point]) -> float:
        """Total length ``pts`` runs on top of edges it may not share a line with."""
        total = 0.0
        for seg in zip(pts, pts[1:]):
            for other in edges:
                if other is edge or id(other) not in points or _related(edge, other):
                    continue
                total += sum(run for run in (_shared(seg, s) for s in segments(other)) if run > MIN_RUN)
        return total

    def hits_node(pts: list[Point], i: int) -> bool:
        return any(
            segment_enters(pts[j], pts[j + 1], n)
            for j in (i - 1, i, i + 1)
            if 0 <= j < len(pts) - 1
            for n in nodes
        )

    changed: set[int] = set()
    # Repeat: a segment may only be able to move once a neighbour has.
    for _ in range(PASSES):
        for edge in movable:
            pts = points[id(edge)]
            last = len(pts) - 2
            # Interior segments first; an end segment moves its port, so only if needed.
            for i in list(range(1, last)) + [0, last]:
                current = overlap(edge, pts)
                if current <= 0.0:
                    break
                best, best_overlap = None, current - 1.0
                for lane in range(1, MAX_LANES + 1):
                    for offset in (lane * PITCH, -lane * PITCH):
                        cand = _shifted(pts, i, offset)
                        if cand is None or hits_node(cand, i):
                            continue
                        if i == 0 and not _on_side(cand[0], edge.source.bounds):
                            continue
                        if i == last and not _on_side(cand[-1], edge.target.bounds):
                            continue
                        score = overlap(edge, cand)
                        if score < best_overlap - 1e-9:
                            best, best_overlap = cand, score
                if best is not None:
                    pts = points[id(edge)] = best
                    changed.add(id(edge))

    for edge in movable:
        if id(edge) in changed:
            path = dataclasses.replace(routes[edge], points=tuple(points[id(edge)]))
            routes[edge] = routes[id(edge)] = path
            edge._resolved_path = path
