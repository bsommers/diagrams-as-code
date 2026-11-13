"""Visual defect checks on a solved diagram.

Tests prove the code runs; these checks look at the picture. Each one counts a
kind of defect a reader would see: a label spilling out of its box, a line
drawn through a node, two labels on top of each other. ``audit_diagram`` is the
entry point; ``tools/audit_gallery.py`` runs it over every example.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
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
        if path.kind == PathKind.POLYLINE and not getattr(edge, "fixed_route", edge.manual_waypoints):
            for end_pt, nxt, box in ((pts[-1], pts[-2], tb), (pts[0], pts[1], sb)):
                if box.width <= 0.0 or box.height <= 0.0:
                    continue  # a point has no side to arrive along
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


@dataclass(frozen=True)
class Finding:
    """One visual defect: its kind (a name in ``DEFECTS``) and what it is about."""

    kind: str
    detail: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.detail}"


def _name(el: Any) -> str:
    label = " ".join((getattr(el, "label", "") or "").split())
    if len(label) > 40:
        label = label[:37] + "..."
    return f"'{label}'" if label else str(getattr(el, "id", "?"))


def _edge_name(edge: Any) -> str:
    return f"{_name(edge.source)} -> {_name(edge.target)}"


def audit_diagram(diagram: Any) -> Counter[str]:
    """Count the visual defects in ``diagram`` (solving it first if needed)."""
    return Counter(f.kind for f in audit_findings(diagram))


def audit_findings(diagram: Any) -> list[Finding]:
    """Every visual defect in ``diagram``, each named so it can be found and fixed."""
    diagram._ensure_solved()
    found: list[Finding] = []

    def add(kind: str, detail: str) -> None:
        found.append(Finding(kind, detail))

    # Annotations edges may cross (a caption, a junction point) are not nodes. Nor
    # are free outlines (a path, a polygon, a polyline): they are drawing, laid
    # over one another and written on by design, and only their bounding boxes
    # are known here.
    shapes = [
        s for s in diagram.shapes
        if getattr(s, "obstacle", True) and not getattr(s, "self_placed", False)
    ]
    # A shape holding others is a frame: badges and lines inside it are in place.
    solid = [s for s in shapes if not getattr(s, "children", None)]

    def _within(inner: Any, outer: Any) -> bool:
        parent = getattr(inner, "parent", None)
        while parent is not None:
            if parent is outer:
                return True
            parent = getattr(parent, "parent", None)
        return False

    def _spans_inside(el: Any, outer: Any) -> bool:
        """True if ``el`` is a bracket along things that are all in ``outer``."""
        spans = [c for c in getattr(el, "constraints", []) if getattr(c, "type", "") == "span"]
        return bool(spans) and all(
            t is None or _within(t, outer) for c in spans for t in (c.target, c.other)
        )

    def _pinned_in(end: Any, shape: Any) -> bool:
        """True if ``end`` is a bare point set inside ``shape``: a line drawn to a spot on it."""
        b = end.bounds
        r, c = shape.bounds, b.center
        return b.width <= 0.0 and b.height <= 0.0 and r.left <= c.x <= r.right and r.top <= c.y <= r.bottom

    flat: list[tuple[Any, list[tuple[Point, Point]]]] = []
    badges: list[tuple[Any, tuple[float, float, float, float]]] = []
    for edge in diagram.edges:
        path = diagram.routes.get(edge)
        if path is None:
            add("edge_through_node", f"{_edge_name(edge)} has no route")
            continue
        ends = (edge.source, edge.target)
        others = [
            s
            for s in shapes
            if s not in ends
            and not any(_within(e, s) or _within(s, e) or _pinned_in(e, s) for e in ends)
        ]
        for problem in edge_problems(edge, path, [s.bounds for s in others]):
            detail = _edge_name(edge)
            if problem == "edge_through_node":
                segs = list(zip(flatten(path), flatten(path)[1:]))
                hit = [s for s in others if any(segment_enters(a, b, s.bounds) for a, b in segs)]
                detail += " crosses " + ", ".join(_name(s) for s in hit)
            add(problem, detail)
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
                add("edge_on_edge", f"{_edge_name(e1)} runs along {_edge_name(e2)}")

    for edge, bb in badges:
        for s in solid:
            if _overlap(bb, _box(s.bounds)):
                add("badge_over_node", f"label '{edge.label}' covers {_name(s)}")
        inner = Rect(bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1])
        for other, segs in flat:
            # A line under a badge that carries that line's own label is labelled
            # correctly: edges with one label on a shared trunk share the badge.
            if other is edge or other.label == edge.label:
                continue
            if any(segment_enters(a, b, inner, 2.0) for a, b in segs):
                add("edge_through_badge", f"{_edge_name(other)} crosses label '{edge.label}'")
    titles = [(g, t) for g in diagram.groups for t in [group_title_rect(g)] if t is not None]
    for edge, bb in badges:
        for g, t in titles:
            if _overlap(bb, _box(t)):
                add("badge_over_title", f"label '{edge.label}' covers the title of {_name(g)}")
    for edge, segs in flat:
        for g, t in titles:
            if any(segment_enters(p, q, t, 1.0) for p, q in segs):
                add("edge_through_title", f"{_edge_name(edge)} crosses the title of {_name(g)}")
    # A title wider than its group runs out over the frame.
    for g, t in titles:
        if t.right > g.bounds.right - 4.0:
            add("title_overflow", f"the title of {_name(g)} is wider than its frame")
    for i in range(len(badges)):
        for j in range(i + 1, len(badges)):
            if _overlap(badges[i][1], badges[j][1]):
                add("badge_over_badge", f"labels '{badges[i][0].label}' and '{badges[j][0].label}' overlap")

    for i, s1 in enumerate(shapes):
        for s2 in shapes[i + 1 :]:
            if _within(s1, s2) or _within(s2, s1):
                continue  # nested on purpose
            if _spans_inside(s1, s2) or _spans_inside(s2, s1):
                continue  # a bracket beside shapes nested in the other
            if _overlap(_box(s1.bounds), _box(s2.bounds)):
                add("node_overlap", f"{_name(s1)} overlaps {_name(s2)}")

    # Two groups, or a group and a node outside it, that cover each other.
    groups = list(diagram.groups)
    for i, g1 in enumerate(groups):
        for g2 in groups[i + 1 :]:
            if not _within(g1, g2) and not _within(g2, g1) and _overlap(_box(g1.bounds), _box(g2.bounds)):
                add("group_overlap", f"groups {_name(g1)} and {_name(g2)} overlap")
        for s in shapes:
            if not _within(s, g1) and not _spans_inside(s, g1) and _overlap(_box(g1.bounds), _box(s.bounds)):
                add("group_overlap", f"{_name(s)} overlaps group {_name(g1)} without being in it")

    for s in shapes:
        if not getattr(s, "annotation", False) and label_overflows(s):
            add("label_overflow", f"the label of {_name(s)} does not fit its shape")

    extents = [s.bounds for s in diagram.shapes] + [g.bounds for g in diagram.groups]
    if extents:
        right, bottom = max(r.right for r in extents), max(r.bottom for r in extents)
        if right > diagram.width + EPS or bottom > diagram.height + EPS:
            add("content_clipped", f"content reaches ({right:.0f}, {bottom:.0f}) on a "
                f"{diagram.width:.0f} x {diagram.height:.0f} canvas")
        if right < diagram.width * 0.6 or bottom < diagram.height * 0.6:
            add("canvas_mostly_empty", f"content ends at ({right:.0f}, {bottom:.0f}) on a "
                f"{diagram.width:.0f} x {diagram.height:.0f} canvas")
    return found
