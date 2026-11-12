"""Visual defect checks on a solved diagram.

Tests prove the code runs; these checks look at the picture. Each one counts a
kind of defect a reader would see: a label spilling out of its box, a line
drawn through a node, two labels on top of each other. ``audit_diagram`` is the
entry point; ``tools/audit_gallery.py`` runs it over every example.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterator, Optional

from diagrams_as_code.geometry import PathKind, Point, Rect, RoutedPath
from diagrams_as_code.metrics import AVG_CHAR_EM, badge_width, wrap_text

EPS = 0.5

#: Every count ``audit_diagram`` can report, in display order.
DEFECTS: tuple[str, ...] = (
    "edge_through_node",
    "edge_through_own_endpoint",
    "tangent_arrival",
    "edge_on_edge",
    "edge_through_badge",
    "badge_over_node",
    "badge_over_badge",
    "label_overflow",
    "node_overlap",
    "content_clipped",
    "canvas_mostly_empty",
)


def segment_enters(a: Point, b: Point, r: Rect, inset: float = 1.0) -> bool:
    """True if segment a-b passes through the interior of ``r`` shrunk by ``inset``."""
    x0, y0, x1, y1 = r.left + inset, r.top + inset, r.right - inset, r.bottom - inset
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


def _side(p: Point, r: Rect) -> Optional[str]:
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
    """Yield the routing defects of one edge.

    ``others`` are the boxes of unrelated nodes the path must stay out of.
    """
    pts = flatten(path)
    if len(pts) < 2:
        yield "degenerate"
        return
    if any(v != v or abs(v) == float("inf") for p in pts for v in (p.x, p.y)):
        yield "non_finite"
        return
    segs = list(zip(pts, pts[1:]))
    sb, tb = edge.source.bounds, edge.target.bounds
    nested = sb.intersects(tb) and edge.source is not edge.target
    if not nested:
        if any(segment_enters(a, b, sb) or segment_enters(a, b, tb) for a, b in segs):
            yield "edge_through_own_endpoint"
        if path.kind == PathKind.POLYLINE and not edge.manual_waypoints:
            for end_pt, nxt, box in ((pts[-1], pts[-2], tb), (pts[0], pts[1], sb)):
                side = _side(end_pt, box)
                along_ew = abs(nxt.x - end_pt.x) <= EPS and abs(nxt.y - end_pt.y) > EPS
                along_ns = abs(nxt.y - end_pt.y) <= EPS and abs(nxt.x - end_pt.x) > EPS
                if (side in ("E", "W") and along_ew) or (side in ("N", "S") and along_ns):
                    yield "tangent_arrival"
                    break
    if any(segment_enters(a, b, r) for a, b in segs for r in others):
        yield "edge_through_node"


def _overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _box(r: Rect) -> tuple[float, float, float, float]:
    return (r.left, r.top, r.right, r.bottom)


def _shared_run(s1: tuple[Point, Point], s2: tuple[Point, Point]) -> float:
    """Length two axis-aligned segments run on top of each other."""
    (a, b), (c, d) = s1, s2
    if abs(a.y - b.y) <= EPS and abs(c.y - d.y) <= EPS and abs(a.y - c.y) <= EPS:
        lo, hi = max(min(a.x, b.x), min(c.x, d.x)), min(max(a.x, b.x), max(c.x, d.x))
        return hi - lo
    if abs(a.x - b.x) <= EPS and abs(c.x - d.x) <= EPS and abs(a.x - c.x) <= EPS:
        lo, hi = max(min(a.y, b.y), min(c.y, d.y)), min(max(a.y, b.y), max(c.y, d.y))
        return hi - lo
    return 0.0


def label_overflows(shape: Any, label_position: str) -> bool:
    """True if a label drawn inside ``shape`` needs more height than it has."""
    if not shape.label or getattr(shape, "kind", "box") == "icon":
        return False
    pos = shape.label_position if shape.label_position != "auto" else "inside"
    if pos != "inside":
        return False
    b = shape.bounds
    lines = wrap_text(shape.label, max(10, int(b.width / 7.2)))
    font = 12.0 if len(lines) == 1 else (11.0 if len(lines) == 2 else 10.0)
    need = len(lines) * font * 1.25
    if getattr(shape, "icon", None):
        need += min(24.0, max(16.0, b.height * 0.38)) + 4.0
    too_tall = need > b.height - 4.0
    too_wide = max(len(line) for line in lines) * font * AVG_CHAR_EM * 0.9 > b.width - 4.0
    return too_tall or too_wide


def audit_diagram(diagram: Any) -> Counter[str]:
    """Count the visual defects in ``diagram`` (solving it first if needed)."""
    diagram._ensure_solved()
    counts: Counter[str] = Counter()
    shapes = list(diagram.shapes)
    boxes = [_box(s.bounds) for s in shapes]

    flat: list[tuple[Any, list[tuple[Point, Point]]]] = []
    badges: list[tuple[Any, tuple[float, float, float, float]]] = []
    for edge in diagram.edges:
        path = diagram.routes.get(edge)
        if path is None:
            counts["edge_through_node"] += 1
            continue
        others = [s.bounds for s in shapes if s is not edge.source and s is not edge.target]
        for problem in edge_problems(edge, path, others):
            counts[problem] += 1
        pts = flatten(path)
        flat.append((edge, list(zip(pts, pts[1:]))))
        if edge.label:
            lx, ly = path.label_anchor()
            meta = getattr(edge, "metadata", {}) or {}
            font = float(meta.get("font_size", 10.0))
            w, h = badge_width(edge.label, font), float(meta.get("badge_height", 18.0))
            badges.append((edge, (lx - w / 2, ly - h / 2, lx + w / 2, ly + h / 2)))

    for i, (e1, segs1) in enumerate(flat):
        for e2, segs2 in flat[i + 1 :]:
            # A shared trunk out of one source, or into one target, is intended.
            if e1.source is e2.source or e1.target is e2.target:
                continue
            if any(_shared_run(a, b) > 6.0 for a in segs1 for b in segs2):
                counts["edge_on_edge"] += 1

    for edge, bb in badges:
        counts["badge_over_node"] += sum(1 for box in boxes if _overlap(bb, box))
        inner = Rect(bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1])
        for other, segs in flat:
            if other is not edge and any(segment_enters(a, b, inner, 2.0) for a, b in segs):
                counts["edge_through_badge"] += 1
    for i in range(len(badges)):
        for j in range(i + 1, len(badges)):
            if _overlap(badges[i][1], badges[j][1]):
                counts["badge_over_badge"] += 1

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if _overlap(boxes[i], boxes[j]):
                counts["node_overlap"] += 1

    counts["label_overflow"] += sum(
        1 for s in shapes if label_overflows(s, getattr(diagram, "label_position", "inside"))
    )

    extents = [s.bounds for s in shapes] + [g.bounds for g in diagram.groups]
    if extents:
        right, bottom = max(r.right for r in extents), max(r.bottom for r in extents)
        if right > diagram.width + EPS or bottom > diagram.height + EPS:
            counts["content_clipped"] += 1
        if right < diagram.width * 0.6 or bottom < diagram.height * 0.6:
            counts["canvas_mostly_empty"] += 1
    return Counter({k: v for k, v in counts.items() if v})
