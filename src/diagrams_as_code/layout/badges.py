"""Choose where each edge's label badge sits along its route.

A badge starts at the midpoint of its edge. If that spot covers a node, another
badge, or another edge's line, the badge slides along its own route to the
nearest spot that is clear. If no spot is clear it is wrapped onto two or three
lines and tried again; failing that it takes the spot with the fewest conflicts.
Edges that carry the same label along a shared trunk get one badge between
them. The edge geometry is never changed.
"""
from __future__ import annotations

import math
from typing import Any, Optional, Sequence

from diagrams_as_code.geometry import Point, Rect, RoutedPath, flatten, segment_enters
from diagrams_as_code.labels import BADGE_FONT_SIZE, badge_block, edge_badge_rect

#: Distance between candidate positions along a route.
STEP = 6.0
#: Clear space kept between two badges, and between a badge and a node.
GAP = 3.0
NODE_COST = 100.0
BADGE_COST = 100.0
LINE_COST = 30.0
#: Cost per pixel moved away from the midpoint; breaks ties toward the middle.
DRIFT_COST = 0.02
#: Cost of each extra line of wrapping; an unwrapped badge wins when equally clear.
WRAP_COST = 1.0
#: Fractions of the unwrapped text width to wrap at: about two lines, then three.
WRAP_FRACTIONS = (0.6, 0.42)

Segment = tuple[Point, Point]


def _samples(points: Sequence[Point]) -> list[Point]:
    """Points every ``STEP`` along a polyline, end points excluded."""
    out: list[Point] = []
    carry = STEP
    for a, b in zip(points, points[1:]):
        length = math.hypot(b.x - a.x, b.y - a.y)
        if length <= 0.0:
            continue
        at = carry
        while at < length:
            t = at / length
            out.append(Point(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t))
            at += STEP
        carry = at - length
    return out


def _overlaps(a: Rect, b: Rect, gap: float = 0.0) -> bool:
    return (
        a.left < b.right + gap and b.left < a.right + gap
        and a.top < b.bottom + gap and b.top < a.bottom + gap
    )


def _on_route(p: Point, pts: Sequence[Point], tol: float = 1.0) -> bool:
    for a, b in zip(pts, pts[1:]):
        dx, dy = b.x - a.x, b.y - a.y
        length2 = dx * dx + dy * dy
        t = 0.0 if length2 == 0.0 else max(0.0, min(1.0, ((p.x - a.x) * dx + (p.y - a.y) * dy) / length2))
        if math.hypot(p.x - (a.x + dx * t), p.y - (a.y + dy * t)) <= tol:
            return True
    return False


def _wrap_widths(edge: Any) -> list[Optional[float]]:
    """Text widths to try: unwrapped, then about two and three lines."""
    meta = getattr(edge, "metadata", {}) or {}
    block = badge_block(edge.label, float(meta.get("font_size", BADGE_FONT_SIZE)))
    if len(block.lines) > 1 or " " not in edge.label.strip():
        return [None]
    return [None] + [block.width * fraction for fraction in WRAP_FRACTIONS]


def place_badges(edges: Sequence[Any], routes: dict[Any, RoutedPath], nodes: Sequence[Rect]) -> None:
    """Set the badge position, wrap width and sharing of every labelled edge."""
    lines: dict[int, tuple[Any, list[Segment]]] = {}
    labelled: list[tuple[float, int, Any, RoutedPath, list[Point]]] = []
    for index, edge in enumerate(edges):
        edge._label_anchor = edge._label_wrap = edge._label_owner = None
        path = routes.get(edge)
        if path is None:
            continue
        pts = flatten(path)
        lines[id(edge)] = (edge, list(zip(pts, pts[1:])))
        if edge.label and len(pts) >= 2:
            length = sum(math.hypot(b.x - a.x, b.y - a.y) for a, b in zip(pts, pts[1:]))
            labelled.append((length, index, edge, path, pts))

    placed: list[tuple[Any, Rect]] = []
    # Shortest routes first: they have the fewest places to go.
    for _, _, edge, path, pts in sorted(labelled, key=lambda item: item[:2]):
        # One badge serves every edge that carries the same label along a trunk.
        owner = next(
            (
                o for o, r in placed
                if o.label == edge.label
                and _on_route(Point(r.x + r.width / 2.0, r.y + r.height / 2.0), pts)
            ),
            None,
        )
        if owner is not None:
            edge._label_owner = owner
            continue

        # Lines that carry the same label may run under the badge: they share it.
        others = [
            segs for other, segs in lines.values()
            if other is not edge and other.label != edge.label
        ]
        candidates = _samples(pts)
        best: Optional[tuple[float, Point, Optional[float], Rect]] = None
        for penalty, wrap in enumerate(_wrap_widths(edge)):
            edge._label_anchor, edge._label_wrap = None, wrap
            home = edge_badge_rect(edge, path)
            assert home is not None
            w, h = home.width, home.height
            hx, hy = home.x + w / 2.0, home.y + h / 2.0

            def cost(x: float, y: float) -> float:
                rect = Rect(x - w / 2.0, y - h / 2.0, w, h)
                clear = Rect(rect.x - GAP, rect.y - GAP, w + 2.0 * GAP, h + 2.0 * GAP)
                total = NODE_COST * sum(1 for n in nodes if _overlaps(rect, n))
                total += BADGE_COST * sum(1 for _, b in placed if _overlaps(rect, b, GAP))
                total += LINE_COST * sum(
                    1 for segs in others if any(segment_enters(a, b, clear, 0.0) for a, b in segs)
                )
                return total + WRAP_COST * penalty + DRIFT_COST * math.hypot(x - hx, y - hy)

            for cand in [Point(hx, hy)] + candidates:
                c = cost(cand.x, cand.y)
                if best is None or c < best[0] - 1e-9:
                    best = (c, cand, wrap, Rect(cand.x - w / 2.0, cand.y - h / 2.0, w, h))
            if best is not None and best[0] < LINE_COST:
                break
        assert best is not None
        edge._label_anchor, edge._label_wrap = best[1], best[2]
        placed.append((edge, best[3]))
