"""Geometric checks on routed edges, shared by tests and ``tools/audit_gallery.py``."""
from __future__ import annotations

from typing import Any, Iterator

from diagrams_as_code.geometry import PathKind, Point, Rect, RoutedPath

EPS = 0.5


def _inset(r: Rect, d: float) -> tuple[float, float, float, float]:
    return (r.left + d, r.top + d, r.right - d, r.bottom - d)


def segment_enters(a: Point, b: Point, r: Rect, inset: float = 1.0) -> bool:
    """True if segment a-b passes through the interior of ``r`` shrunk by ``inset``."""
    x0, y0, x1, y1 = _inset(r, inset)
    if x0 >= x1 or y0 >= y1:
        return False
    dx, dy = b.x - a.x, b.y - a.y
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a.x - x0), (dx, x1 - a.x), (-dy, a.y - y0), (dy, y1 - a.y)):
        if p == 0:
            if q <= 0:
                return False
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 >= t1:
                return False
    return True


def flatten(path: RoutedPath, steps: int = 16) -> list[Point]:
    """Polyline approximation of a routed path."""
    pts = list(path.points)
    if path.kind != PathKind.BEZIER_CHAIN or len(pts) < 4:
        return pts
    out = [pts[0]]
    for i in range(0, len(pts) - 3, 3):
        p0, p1, p2, p3 = pts[i : i + 4]
        for k in range(1, steps + 1):
            t = k / steps
            u = 1 - t
            out.append(
                Point(
                    u**3 * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t**3 * p3.x,
                    u**3 * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t**3 * p3.y,
                )
            )
    return out


def _side(p: Point, r: Rect) -> str | None:
    if abs(p.x - r.left) <= EPS and r.top - EPS <= p.y <= r.bottom + EPS:
        return "W"
    if abs(p.x - r.right) <= EPS and r.top - EPS <= p.y <= r.bottom + EPS:
        return "E"
    if abs(p.y - r.top) <= EPS and r.left - EPS <= p.x <= r.right + EPS:
        return "N"
    if abs(p.y - r.bottom) <= EPS and r.left - EPS <= p.x <= r.right + EPS:
        return "S"
    return None


def edge_problems(edge: Any, path: RoutedPath, others: list[Rect]) -> Iterator[str]:
    """Yield the names of invariants ``path`` violates for ``edge``.

    ``others`` are the boxes of unrelated nodes the path must stay out of.
    """
    pts = flatten(path)
    if len(pts) < 2:
        yield "degenerate"
        return
    for p in pts:
        if p.x != p.x or p.y != p.y or abs(p.x) == float("inf") or abs(p.y) == float("inf"):
            yield "non_finite"
            return
    segs = list(zip(pts, pts[1:]))
    sb, tb = edge.source.bounds, edge.target.bounds
    nested = sb.intersects(tb) and edge.source is not edge.target
    if not nested:
        if any(segment_enters(a, b, sb) or segment_enters(a, b, tb) for a, b in segs):
            yield "through_own_endpoint"
        if path.kind == PathKind.POLYLINE and not edge.manual_waypoints:
            for end_pt, nxt, box in ((pts[-1], pts[-2], tb), (pts[0], pts[1], sb)):
                side = _side(end_pt, box)
                if side in ("E", "W") and abs(nxt.y - end_pt.y) > EPS and abs(nxt.x - end_pt.x) <= EPS:
                    yield "tangent_arrival"
                    break
                if side in ("N", "S") and abs(nxt.x - end_pt.x) > EPS and abs(nxt.y - end_pt.y) <= EPS:
                    yield "tangent_arrival"
                    break
    if any(segment_enters(a, b, r) for a, b in segs for r in others):
        yield "through_other_node"
