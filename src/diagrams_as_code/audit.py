"""Visual defect checks on a solved diagram.

Tests prove the code runs; these checks look at the picture. Each one counts a
kind of defect a reader would see: a label spilling out of its box, a line
drawn through a node, two labels on top of each other. ``audit_diagram`` is the
entry point; ``tools/audit_gallery.py`` runs it over every example.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterator, Optional

from diagrams_as_code.connections import may_share_a_line
from diagrams_as_code.geometry import PathKind, Point, Rect, RoutedPath, flatten, segment_enters
from diagrams_as_code.labels import edge_badge_rect, group_title_rect, node_label

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
    "badge_over_title",
    "edge_through_title",
    "title_overflow",
    "label_overflow",
    "node_overlap",
    "group_overlap",
    "content_clipped",
    "canvas_mostly_empty",
)


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


def label_overflows(shape: Any) -> bool:
    """True if a label drawn inside ``shape`` does not fit it at any size."""
    if not shape.label:
        return False
    return not node_label(shape).fits


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
        rect = edge_badge_rect(edge, path)
        if rect is not None:
            badges.append((edge, _box(rect)))

    links = {(id(e.source), id(e.target)) for e in diagram.edges}
    for i, (e1, segs1) in enumerate(flat):
        for e2, segs2 in flat[i + 1 :]:
            if may_share_a_line(e1, e2, links):
                continue
            if any(_shared_run(a, b) > 6.0 for a in segs1 for b in segs2):
                counts["edge_on_edge"] += 1

    for edge, bb in badges:
        counts["badge_over_node"] += sum(1 for box in boxes if _overlap(bb, box))
        inner = Rect(bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1])
        for other, segs in flat:
            # A line under a badge that carries that line's own label is labelled
            # correctly: edges with one label on a shared trunk share the badge.
            if other is edge or other.label == edge.label:
                continue
            if any(segment_enters(a, b, inner, 2.0) for a, b in segs):
                counts["edge_through_badge"] += 1
    titles = [(g, t) for g in diagram.groups for t in [group_title_rect(g)] if t is not None]
    for _, bb in badges:
        counts["badge_over_title"] += sum(1 for _, t in titles if _overlap(bb, _box(t)))
    for _, segs in flat:
        counts["edge_through_title"] += sum(
            1 for _, t in titles if any(segment_enters(p, q, t, 1.0) for p, q in segs)
        )
    # A title wider than its group runs out over the frame.
    counts["title_overflow"] += sum(1 for g, t in titles if t.right > g.bounds.right - 4.0)
    for i in range(len(badges)):
        for j in range(i + 1, len(badges)):
            if _overlap(badges[i][1], badges[j][1]):
                counts["badge_over_badge"] += 1

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if _overlap(boxes[i], boxes[j]):
                counts["node_overlap"] += 1

    def _inside(inner: Any, outer: Any) -> bool:
        parent = getattr(inner, "parent", None)
        while parent is not None:
            if parent is outer:
                return True
            parent = getattr(parent, "parent", None)
        return False

    # Two groups, or a group and a node outside it, that cover each other.
    groups = list(diagram.groups)
    for i, g1 in enumerate(groups):
        for g2 in groups[i + 1 :]:
            if not _inside(g1, g2) and not _inside(g2, g1) and _overlap(_box(g1.bounds), _box(g2.bounds)):
                counts["group_overlap"] += 1
        for s in shapes:
            if not _inside(s, g1) and _overlap(_box(g1.bounds), _box(s.bounds)):
                counts["group_overlap"] += 1

    counts["label_overflow"] += sum(1 for s in shapes if label_overflows(s))

    extents = [s.bounds for s in shapes] + [g.bounds for g in diagram.groups]
    if extents:
        right, bottom = max(r.right for r in extents), max(r.bottom for r in extents)
        if right > diagram.width + EPS or bottom > diagram.height + EPS:
            counts["content_clipped"] += 1
        if right < diagram.width * 0.6 or bottom < diagram.height * 0.6:
            counts["canvas_mostly_empty"] += 1
    return Counter({k: v for k, v in counts.items() if v})
