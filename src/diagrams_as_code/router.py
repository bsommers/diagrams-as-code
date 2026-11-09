from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
from typing import Any, Iterable, Optional, Sequence

from diagrams_as_code.connections import Edge, EdgeStyle, Port, Routing
from diagrams_as_code.elements import Element
from diagrams_as_code.geometry import CubicBezier, PathKind, Point, Rect, RoutedPath
from diagrams_as_code.groups import Group


@dataclass(frozen=True)
class RoutingScene:
    """Immutable snapshot of diagram geometry and element hierarchies for routing."""

    rects: dict[Element, Rect]
    ancestors: dict[Element, frozenset[Group]]
    canvas: Rect

    @classmethod
    def build(
        cls,
        elements: Sequence[Element],
        canvas: Optional[Rect] = None,
    ) -> RoutingScene:
        """Construct a RoutingScene by inspecting element bounds and group hierarchies."""
        rects: dict[Element, Rect] = {}
        ancestors: dict[Element, set[Group]] = {}
        for el in elements:
            rects[el] = el.bounds
            curr = getattr(el, "parent", None)
            anc: set[Group] = set()
            while curr is not None:
                anc.add(curr)
                curr = getattr(curr, "parent", None)
            ancestors[el] = anc
        return cls(
            rects=rects,
            ancestors={k: frozenset(v) for k, v in ancestors.items()},
            canvas=canvas or Rect(0.0, 0.0, 1200.0, 800.0),
        )

    def obstacles_for(self, edge: Edge, clearance: float = 0.0) -> list[Rect]:
        """Return obstacle bounding boxes relevant to an edge, excluding endpoints and ancestors."""
        excluded: set[Element] = {edge.source, edge.target}
        excluded.update(self.ancestors.get(edge.source, frozenset()))
        excluded.update(self.ancestors.get(edge.target, frozenset()))

        result: list[Rect] = []
        for el, r in self.rects.items():
            if el not in excluded:
                result.append(r.expand(clearance) if clearance > 0.0 else r)
        return result


def segment_intersects_rect(p1: Point, p2: Point, rect: Rect) -> bool:
    """Return True if the open line segment between p1 and p2 enters rect's interior."""
    if p1.y == p2.y:
        y = p1.y
        if rect.top < y < rect.bottom:
            x1, x2 = min(p1.x, p2.x), max(p1.x, p2.x)
            return x1 < rect.right and x2 > rect.left
        return False
    if p1.x == p2.x:
        x = p1.x
        if rect.left < x < rect.right:
            y1, y2 = min(p1.y, p2.y), max(p1.y, p2.y)
            return y1 < rect.bottom and y2 > rect.top
        return False

    # General line segment test (slab method)
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    t_min, t_max = 0.0, 1.0
    for p, q in [
        (-dx, p1.x - rect.left),
        (dx, rect.right - p1.x),
        (-dy, p1.y - rect.top),
        (dy, rect.bottom - p1.y),
    ]:
        if p == 0:
            if q <= 0:
                return False
        else:
            t = q / p
            if p < 0:
                if t > t_min:
                    t_min = t
            else:
                if t < t_max:
                    t_max = t
            if t_min >= t_max:
                return False
    return t_min < t_max and t_max > 0.0 and t_min < 1.0


PORT_NORMALS: dict[Port, Point] = {
    Port.EAST: Point(1.0, 0.0),
    Port.WEST: Point(-1.0, 0.0),
    Port.SOUTH: Point(0.0, 1.0),
    Port.NORTH: Point(0.0, -1.0),
}


def _normalize_route_args(
    scene: Any, style: Any, obstacles: Any, clearance: Any
) -> tuple[Optional[RoutingScene], Optional[EdgeStyle], Optional[Iterable[Any]], Optional[float]]:
    """Sort the loosely typed ``route()`` arguments into their proper roles.

    ``scene`` and ``style`` may be passed in either order, ``style`` may be a bare
    numeric clearance, and either may be an iterable of obstacle elements (the
    legacy call shapes). Each role may be supplied only once: giving the same
    role both positionally and by keyword, or twice positionally, is a
    ``TypeError`` rather than a silent overwrite.
    """
    out_scene: Optional[RoutingScene] = None
    out_style: Optional[EdgeStyle] = None
    out_obstacles = obstacles
    out_clearance = None if clearance is None else float(clearance)

    for arg in (scene, style):
        if arg is None:
            continue
        if isinstance(arg, RoutingScene):
            if out_scene is not None:
                raise TypeError("route() got more than one RoutingScene")
            out_scene = arg
        elif isinstance(arg, EdgeStyle):
            if out_style is not None:
                raise TypeError("route() got more than one EdgeStyle")
            out_style = arg
        elif isinstance(arg, bool):
            raise TypeError("route() clearance must be a number, not bool")
        elif isinstance(arg, (int, float)):
            if out_clearance is not None:
                raise TypeError("route() got clearance both positionally and by keyword")
            out_clearance = float(arg)
        else:
            if out_obstacles is not None:
                raise TypeError("route() got obstacles both positionally and by keyword")
            out_obstacles = arg
    return out_scene, out_style, out_obstacles, out_clearance


class CurveRouter:
    """Computes cubic Bezier control handles from port normal vectors."""

    def _normalize_obstacles(
        self,
        edge: Edge,
        obstacles: Optional[Iterable[Any]],
        p_start: Point,
        p_end: Point,
    ) -> list[Rect]:
        """Normalize obstacles, filtering out endpoints, matching IDs, and enclosing container groups."""
        if obstacles is None:
            return []
        norm: list[Rect] = []
        src_id = getattr(edge.source, "id", None)
        tgt_id = getattr(edge.target, "id", None)
        filter_ids = {i for i in (src_id, tgt_id) if i is not None}
        for item in obstacles:
            if item is edge.source or item is edge.target:
                continue
            if hasattr(item, "id") and item.id in filter_ids:
                continue
            if hasattr(item, "bounds") and isinstance(item.bounds, Rect):
                r = item.bounds
            elif isinstance(item, Rect):
                r = item
            else:
                continue

            # Skip if start or end point is inside the obstacle (e.g. enclosing group)
            if (r.left <= p_start.x <= r.right and r.top <= p_start.y <= r.bottom) or (
                r.left <= p_end.x <= r.right and r.top <= p_end.y <= r.bottom
            ):
                continue
            norm.append(r)
        return norm

    def _detect_collisions(
        self,
        curve: CubicBezier,
        obstacles: list[Rect],
        clearance: float,
    ) -> list[Rect]:
        """Collect and return obstacles that intersect candidate curve inflated by clearance."""
        return [
            obs for obs in obstacles if curve.intersects_rect(obs.expand(clearance))
        ]

    def resolve_ports(
        self,
        edge: Edge,
        obstacles: Optional[Iterable[Any]] = None,
    ) -> tuple[Port, Port]:
        """Determine connection ports for source and target elements, auto-resolving reverse flows."""
        if edge.source_port and edge.target_port:
            return (edge.source_port, edge.target_port)

        sb, tb = edge.source.bounds, edge.target.bounds
        dx = tb.center.x - sb.center.x
        dy = tb.center.y - sb.center.y

        if abs(dx) >= abs(dy):
            if dx < 0 and edge.source_port is None and edge.target_port is None:
                # Reverse-flow horizontal detected! Resolve to outward lateral cardinal ports (D-14).
                min_top = min(sb.top, tb.top)
                north_constrained = min_top <= 30.0
                if not north_constrained and obstacles:
                    x_span_min = min(sb.left, tb.left)
                    x_span_max = max(sb.right, tb.right)
                    for item in obstacles:
                        r = item if isinstance(item, Rect) else getattr(item, "bounds", None)
                        if not isinstance(r, Rect):
                            continue
                        if item is edge.source or item is edge.target:
                            continue
                        src_id = getattr(edge.source, "id", None)
                        tgt_id = getattr(edge.target, "id", None)
                        filter_ids = {i for i in (src_id, tgt_id) if i is not None}
                        if hasattr(item, "id") and item.id in filter_ids:
                            continue
                        if r.right >= x_span_min and r.left <= x_span_max:
                            if r.top < min_top and r.bottom >= min_top - 30.0:
                                north_constrained = True
                                break
                if north_constrained:
                    return (Port.SOUTH, Port.SOUTH)
                return (Port.NORTH, Port.NORTH)
            src_p = Port.EAST if dx > 0 else Port.WEST
            tgt_p = Port.WEST if dx > 0 else Port.EAST
        else:
            if dy < 0 and edge.source_port is None and edge.target_port is None:
                # Reverse-flow vertical detected! Resolve to outward lateral cardinal ports (D-14).
                max_right = max(sb.right, tb.right)
                east_constrained = False
                if obstacles:
                    y_span_min = min(sb.top, tb.top)
                    y_span_max = max(sb.bottom, tb.bottom)
                    for item in obstacles:
                        r = item if isinstance(item, Rect) else getattr(item, "bounds", None)
                        if not isinstance(r, Rect):
                            continue
                        if item is edge.source or item is edge.target:
                            continue
                        src_id = getattr(edge.source, "id", None)
                        tgt_id = getattr(edge.target, "id", None)
                        filter_ids = {i for i in (src_id, tgt_id) if i is not None}
                        if hasattr(item, "id") and item.id in filter_ids:
                            continue
                        if r.bottom >= y_span_min and r.top <= y_span_max:
                            if r.right > max_right and r.left <= max_right + 30.0:
                                east_constrained = True
                                break
                if east_constrained:
                    return (Port.WEST, Port.WEST)
                return (Port.EAST, Port.EAST)
            src_p = Port.SOUTH if dy > 0 else Port.NORTH
            tgt_p = Port.NORTH if dy > 0 else Port.SOUTH

        return (edge.source_port or src_p, edge.target_port or tgt_p)

    def _is_reverse_flow_explicit(
        self, edge: Edge, src_port: Port, tgt_port: Port
    ) -> bool:
        """Check if edge is reverse-flow with opposing/facing explicit ports."""
        if edge.source_port is None and edge.target_port is None:
            return False
        sb = edge.source.bounds
        tb = edge.target.bounds
        dx = tb.center.x - sb.center.x
        dy = tb.center.y - sb.center.y
        is_reverse_x = (abs(dx) >= abs(dy) and dx < 0) or (edge.source == edge.target)
        if is_reverse_x:
            if src_port in (Port.EAST, Port.WEST) and tgt_port in (Port.EAST, Port.WEST):
                return src_port == Port.EAST or tgt_port == Port.WEST
        return False

    def _route_reverse_flow_explicit_ports(
        self,
        edge: Edge,
        p_start: Point,
        p_end: Point,
        src_port: Port,
        tgt_port: Port,
        obstacles: list[Rect],
        clearance: float,
    ) -> list[Point]:
        """Route reverse-flow connection with explicit facing ports via lateral escape corridor (D-13, D-15)."""
        margin = max(clearance, 30.0)
        sb = edge.source.bounds
        tb = edge.target.bounds

        # Determine escape corridor level: above both nodes and any obstacles (D-13)
        min_top = min(sb.top, tb.top, *(o.top for o in obstacles)) if obstacles else min(sb.top, tb.top)
        y_corridor = min_top - margin

        # Escape waypoints projected laterally beyond shape boundaries (D-13, D-15)
        w_esc1_x = sb.right + margin if src_port == Port.EAST else sb.left - margin
        w_esc2_x = tb.right + margin if tgt_port == Port.EAST else tb.left - margin

        w_esc1 = Point(w_esc1_x, y_corridor)
        w_esc2 = Point(w_esc2_x, y_corridor)

        # Direction unit vector along escape corridor from w_esc1 to w_esc2
        dx_esc = w_esc2.x - w_esc1.x
        t_x = -1.0 if dx_esc <= 0 else 1.0
        tangent = Point(t_x, 0.0)

        n_src = PORT_NORMALS[src_port]
        n_tgt = PORT_NORMALS[tgt_port]

        # Segment 1: p_start to w_esc1
        l1 = p_start.distance_to(w_esc1)
        h0 = max(20.0, min(0.35 * l1, 0.5 * abs(w_esc1.x - p_start.x)))
        h1_in = max(20.0, min(0.35 * l1, 0.5 * abs(w_esc1.x - p_start.x)))

        c0a = Point(p_start.x + n_src.x * h0, p_start.y + n_src.y * h0)
        c0b = Point(w_esc1.x - tangent.x * h1_in, w_esc1.y - tangent.y * h1_in)

        # Segment 2: w_esc1 to w_esc2 (corridor bypass)
        l_mid = abs(w_esc2.x - w_esc1.x)
        h_mid = max(20.0, l_mid / 3.0)

        c1a = Point(w_esc1.x + tangent.x * h_mid, w_esc1.y)
        c1b = Point(w_esc2.x - tangent.x * h_mid, w_esc2.y)

        # Segment 3: w_esc2 to p_end
        l3 = w_esc2.distance_to(p_end)
        h2_out = max(20.0, min(0.35 * l3, 0.5 * abs(p_end.x - w_esc2.x)))
        h3 = max(20.0, min(0.35 * l3, 0.5 * abs(p_end.x - w_esc2.x)))

        c2a = Point(w_esc2.x + tangent.x * h2_out, w_esc2.y)
        c2b = Point(p_end.x + n_tgt.x * h3, p_end.y + n_tgt.y * h3)

        return [p_start, c0a, c0b, w_esc1, c1a, c1b, w_esc2, c2a, c2b, p_end]

    def route(
        self,
        edge: Edge,
        scene: Optional[RoutingScene] = None,
        style: Optional[EdgeStyle] = None,
        obstacles: Optional[Iterable[Any]] = None,
        clearance: Optional[float] = None,
    ) -> RoutedPath:
        """Compute ordered path waypoints for cubic Bezier curve."""
        scene, style, obstacles, clearance = _normalize_route_args(
            scene, style, obstacles, clearance
        )

        if clearance is not None:
            eff_clearance = clearance
        elif style is not None:
            eff_clearance = style.clearance
        elif getattr(edge, "clearance", None) is not None:
            eff_clearance = edge.clearance
        else:
            eff_clearance = 15.0

        if scene is not None:
            cand_obstacles: Optional[Iterable[Any]] = scene.obstacles_for(edge, clearance=0.0)
            res_obstacles = cand_obstacles
        else:
            cand_obstacles = obstacles
            res_obstacles = obstacles

        src_port, tgt_port = self.resolve_ports(edge, obstacles=res_obstacles)
        p_start = edge.source.bounds.get_anchor(src_port.to_anchor())
        p_end = edge.target.bounds.get_anchor(tgt_port.to_anchor())

        norm_obstacles = self._normalize_obstacles(edge, cand_obstacles, p_start, p_end)
        if (scene is not None or obstacles is not None) and self._is_reverse_flow_explicit(edge, src_port, tgt_port):
            pts = self._route_reverse_flow_explicit_ports(
                edge, p_start, p_end, src_port, tgt_port, norm_obstacles, eff_clearance
            )
            return RoutedPath(kind=PathKind.BEZIER_CHAIN, points=tuple(pts))

        n_src = PORT_NORMALS[src_port]
        n_tgt = PORT_NORMALS[tgt_port]

        dx = p_end.x - p_start.x
        dy = p_end.y - p_start.y

        is_src_horiz = src_port in (Port.EAST, Port.WEST)
        is_tgt_horiz = tgt_port in (Port.EAST, Port.WEST)

        if is_src_horiz != is_tgt_horiz:
            # Perpendicular ports (D-05)
            d_x = max(0.5 * abs(dx), 25.0)
            d_y = max(0.5 * abs(dy), 25.0)
            d1 = d_x if is_src_horiz else d_y
            d2 = d_x if is_tgt_horiz else d_y
        elif src_port == tgt_port:
            # Same-side / parallel ports (D-06)
            sep = abs(dx) if not is_src_horiz else abs(dy)
            d = max(0.5 * sep, 30.0)
            d1 = d2 = d
        else:
            # Facing or opposing ports (D-01, D-02, D-03, D-07)
            if is_src_horiz:
                axis_delta = dx if src_port == Port.EAST else -dx
                lat_delta = abs(dy)
            else:
                axis_delta = dy if src_port == Port.SOUTH else -dy
                lat_delta = abs(dx)

            if axis_delta > 0:
                # Forward flow (D-01, D-02, D-03)
                d = max(0.5 * axis_delta, 0.25 * lat_delta, 20.0)
                d1 = d2 = d
            else:
                # Backward flow (D-07)
                d = max(0.25 * lat_delta, 30.0)
                d1 = d2 = d

        # Minimum handle separation invariant (D-02, D-15)
        d1 = max(d1, 20.0)
        d2 = max(d2, 20.0)

        c1 = Point(p_start.x + n_src.x * d1, p_start.y + n_src.y * d1)
        c2 = Point(p_end.x + n_tgt.x * d2, p_end.y + n_tgt.y * d2)

        cand = CubicBezier(p_start, c1, c2, p_end)
        if not norm_obstacles:
            return RoutedPath(kind=PathKind.BEZIER_CHAIN, points=(p_start, c1, c2, p_end))

        hits = self._detect_collisions(cand, norm_obstacles, eff_clearance)
        if not hits:
            return RoutedPath(kind=PathKind.BEZIER_CHAIN, points=(p_start, c1, c2, p_end))

        pts = self._select_deflected_corridor(
            p_start, p_end, n_src, n_tgt, hits, norm_obstacles, eff_clearance
        )
        return RoutedPath(kind=PathKind.BEZIER_CHAIN, points=tuple(pts))

    def _build_deflected_spline_horizontal(
        self,
        p0: Point,
        p3: Point,
        n_src: Point,
        n_tgt: Point,
        obs_block: Rect,
        y_corridor: float,
        clearance: float = 15.0,
    ) -> list[Point]:
        """Synthesize C1 continuous multi-segment spline deflected along horizontal corridor (D-05, D-07, D-08)."""
        w_obs = obs_block.width
        dx = p3.x - p0.x
        t_x = 1.0 if dx >= 0 else -1.0
        tangent = Point(t_x, 0.0)

        if w_obs <= 2.0 * clearance:
            # Compact obstacle: single apex waypoint (D-07)
            w = Point(obs_block.center.x, y_corridor)
            l1 = p0.distance_to(w)
            l2 = w.distance_to(p3)
            h0 = max(20.0, min(0.35 * l1, 80.0))
            h1 = max(20.0, min(0.35 * l1, 80.0))
            h2 = max(20.0, min(0.35 * l2, 80.0))
            h3 = max(20.0, min(0.35 * l2, 80.0))
            c0a = Point(p0.x + n_src.x * h0, p0.y + n_src.y * h0)
            c0b = Point(w.x - tangent.x * h1, w.y - tangent.y * h1)
            c1a = Point(w.x + tangent.x * h2, w.y + tangent.y * h2)
            c1b = Point(p3.x + n_tgt.x * h3, p3.y + n_tgt.y * h3)
            return [p0, c0a, c0b, w, c1a, c1b, p3]
        else:
            # Wide obstacle: 2 corner clearance waypoints (D-07, D-11)
            if dx >= 0:
                w1_x = obs_block.left - clearance
                w2_x = obs_block.right + clearance
            else:
                w1_x = obs_block.right + clearance
                w2_x = obs_block.left - clearance

            w1 = Point(w1_x, y_corridor)
            w2 = Point(w2_x, y_corridor)

            # Segment 1: p0 -> w1
            l1 = p0.distance_to(w1)
            h0 = max(20.0, min(0.35 * l1, 80.0))
            h1_in = max(20.0, min(0.35 * l1, 80.0))
            c0a = Point(p0.x + n_src.x * h0, p0.y + n_src.y * h0)
            c0b = Point(w1.x - tangent.x * h1_in, w1.y)

            # Segment 2: w1 -> w2
            l_mid = abs(w2.x - w1.x)
            h_mid = max(20.0, l_mid / 3.0)
            c1a = Point(w1.x + tangent.x * h_mid, w1.y)
            c1b = Point(w2.x - tangent.x * h_mid, w2.y)

            # Segment 3: w2 -> p3
            l3 = w2.distance_to(p3)
            h2_out = max(20.0, min(0.35 * l3, 80.0))
            h3 = max(20.0, min(0.35 * l3, 80.0))
            c2a = Point(w2.x + tangent.x * h2_out, w2.y)
            c2b = Point(p3.x + n_tgt.x * h3, p3.y + n_tgt.y * h3)

            return [p0, c0a, c0b, w1, c1a, c1b, w2, c2a, c2b, p3]

    def _build_deflected_spline_vertical(
        self,
        p0: Point,
        p3: Point,
        n_src: Point,
        n_tgt: Point,
        obs_block: Rect,
        x_corridor: float,
        clearance: float = 15.0,
    ) -> list[Point]:
        """Synthesize C1 continuous multi-segment spline deflected along vertical corridor (D-05, D-07, D-08)."""
        h_obs = obs_block.height
        dy = p3.y - p0.y
        t_y = 1.0 if dy >= 0 else -1.0
        tangent = Point(0.0, t_y)

        if h_obs <= 2.0 * clearance:
            # Compact obstacle: single apex waypoint (D-07)
            w = Point(x_corridor, obs_block.center.y)
            l1 = p0.distance_to(w)
            l2 = w.distance_to(p3)
            h0 = max(20.0, min(0.35 * l1, 80.0))
            h1 = max(20.0, min(0.35 * l1, 80.0))
            h2 = max(20.0, min(0.35 * l2, 80.0))
            h3 = max(20.0, min(0.35 * l2, 80.0))
            c0a = Point(p0.x + n_src.x * h0, p0.y + n_src.y * h0)
            c0b = Point(w.x - tangent.x * h1, w.y - tangent.y * h1)
            c1a = Point(w.x + tangent.x * h2, w.y + tangent.y * h2)
            c1b = Point(p3.x + n_tgt.x * h3, p3.y + n_tgt.y * h3)
            return [p0, c0a, c0b, w, c1a, c1b, p3]
        else:
            # Tall obstacle: 2 corner clearance waypoints (D-07, D-11)
            if dy >= 0:
                w1_y = obs_block.top - clearance
                w2_y = obs_block.bottom + clearance
            else:
                w1_y = obs_block.bottom + clearance
                w2_y = obs_block.top - clearance

            w1 = Point(x_corridor, w1_y)
            w2 = Point(x_corridor, w2_y)

            # Segment 1: p0 -> w1
            l1 = p0.distance_to(w1)
            h0 = max(20.0, min(0.35 * l1, 80.0))
            h1_in = max(20.0, min(0.35 * l1, 80.0))
            c0a = Point(p0.x + n_src.x * h0, p0.y + n_src.y * h0)
            c0b = Point(w1.x, w1.y - tangent.y * h1_in)

            # Segment 2: w1 -> w2
            l_mid = abs(w2.y - w1.y)
            h_mid = max(20.0, l_mid / 3.0)
            c1a = Point(w1.x, w1.y + tangent.y * h_mid)
            c1b = Point(w2.x, w2.y - tangent.y * h_mid)

            # Segment 3: w2 -> p3
            l3 = w2.distance_to(p3)
            h2_out = max(20.0, min(0.35 * l3, 80.0))
            h3 = max(20.0, min(0.35 * l3, 80.0))
            c2a = Point(w2.x, w2.y + tangent.y * h2_out)
            c2b = Point(p3.x + n_tgt.x * h3, p3.y + n_tgt.y * h3)

            return [p0, c0a, c0b, w1, c1a, c1b, w2, c2a, c2b, p3]

    def _test_spline_collisions(
        self, pts: list[Point], obstacles: list[Rect], clearance: float
    ) -> list[Rect]:
        """Detect any obstacles intersecting the multi-segment spline."""
        num_segs = (len(pts) - 1) // 3
        hit_obs: list[Rect] = []
        for k in range(num_segs):
            seg = CubicBezier(pts[k * 3], pts[k * 3 + 1], pts[k * 3 + 2], pts[k * 3 + 3])
            for obs in obstacles:
                if obs not in hit_obs and seg.intersects_rect(obs.expand(clearance)):
                    hit_obs.append(obs)
        return hit_obs

    def _select_deflected_corridor(
        self,
        p0: Point,
        p3: Point,
        n_src: Point,
        n_tgt: Point,
        colliding: list[Rect],
        all_obstacles: list[Rect],
        clearance: float,
    ) -> list[Point]:
        """Select minimal deviation collision-free corridor or expand past secondary obstacles (D-09, D-10)."""
        min_x = min(r.left for r in colliding)
        min_y = min(r.top for r in colliding)
        max_x = max(r.right for r in colliding)
        max_y = max(r.bottom for r in colliding)
        block = Rect(min_x, min_y, max_x - min_x, max_y - min_y)

        dx = p3.x - p0.x
        dy = p3.y - p0.y
        is_horiz = abs(dx) >= abs(dy)

        if is_horiz:
            y_top = block.top - clearance
            y_bot = block.bottom + clearance
            cand_top = self._build_deflected_spline_horizontal(
                p0, p3, n_src, n_tgt, block, y_top, clearance
            )
            cand_bot = self._build_deflected_spline_horizontal(
                p0, p3, n_src, n_tgt, block, y_bot, clearance
            )

            hits_top = self._test_spline_collisions(cand_top, all_obstacles, clearance)
            hits_bot = self._test_spline_collisions(cand_bot, all_obstacles, clearance)

            if not hits_top and not hits_bot:
                segs_top = (len(cand_top) - 1) // 3
                len_top = sum(
                    CubicBezier(
                        cand_top[k * 3], cand_top[k * 3 + 1], cand_top[k * 3 + 2], cand_top[k * 3 + 3]
                    ).arc_length(16)
                    for k in range(segs_top)
                )
                segs_bot = (len(cand_bot) - 1) // 3
                len_bot = sum(
                    CubicBezier(
                        cand_bot[k * 3], cand_bot[k * 3 + 1], cand_bot[k * 3 + 2], cand_bot[k * 3 + 3]
                    ).arc_length(16)
                    for k in range(segs_bot)
                )
                return cand_top if len_top <= len_bot else cand_bot
            elif not hits_top:
                return cand_top
            elif not hits_bot:
                return cand_bot
            else:
                y_top_exp = min(o.top for o in hits_top) - clearance
                cand_top_exp = self._build_deflected_spline_horizontal(
                    p0, p3, n_src, n_tgt, block, y_top_exp, clearance
                )
                hits_top_exp = self._test_spline_collisions(cand_top_exp, all_obstacles, clearance)
                if not hits_top_exp:
                    return cand_top_exp

                y_bot_exp = max(o.bottom for o in hits_bot) + clearance
                cand_bot_exp = self._build_deflected_spline_horizontal(
                    p0, p3, n_src, n_tgt, block, y_bot_exp, clearance
                )
                hits_bot_exp = self._test_spline_collisions(cand_bot_exp, all_obstacles, clearance)
                if not hits_bot_exp:
                    return cand_bot_exp

                return cand_top_exp if len(hits_top_exp) <= len(hits_bot_exp) else cand_bot_exp
        else:
            x_left = block.left - clearance
            x_right = block.right + clearance
            cand_left = self._build_deflected_spline_vertical(
                p0, p3, n_src, n_tgt, block, x_left, clearance
            )
            cand_right = self._build_deflected_spline_vertical(
                p0, p3, n_src, n_tgt, block, x_right, clearance
            )

            hits_left = self._test_spline_collisions(cand_left, all_obstacles, clearance)
            hits_right = self._test_spline_collisions(cand_right, all_obstacles, clearance)

            if not hits_left and not hits_right:
                segs_left = (len(cand_left) - 1) // 3
                len_left = sum(
                    CubicBezier(
                        cand_left[k * 3], cand_left[k * 3 + 1], cand_left[k * 3 + 2], cand_left[k * 3 + 3]
                    ).arc_length(16)
                    for k in range(segs_left)
                )
                segs_right = (len(cand_right) - 1) // 3
                len_right = sum(
                    CubicBezier(
                        cand_right[k * 3], cand_right[k * 3 + 1], cand_right[k * 3 + 2], cand_right[k * 3 + 3]
                    ).arc_length(16)
                    for k in range(segs_right)
                )
                return cand_left if len_left <= len_right else cand_right
            elif not hits_left:
                return cand_left
            elif not hits_right:
                return cand_right
            else:
                x_left_exp = min(o.left for o in hits_left) - clearance
                cand_left_exp = self._build_deflected_spline_vertical(
                    p0, p3, n_src, n_tgt, block, x_left_exp, clearance
                )
                hits_left_exp = self._test_spline_collisions(cand_left_exp, all_obstacles, clearance)
                if not hits_left_exp:
                    return cand_left_exp

                x_right_exp = max(o.right for o in hits_right) + clearance
                cand_right_exp = self._build_deflected_spline_vertical(
                    p0, p3, n_src, n_tgt, block, x_right_exp, clearance
                )
                hits_right_exp = self._test_spline_collisions(cand_right_exp, all_obstacles, clearance)
                if not hits_right_exp:
                    return cand_right_exp

                return cand_left_exp if len(hits_left_exp) <= len(hits_right_exp) else cand_right_exp


class OrthogonalRouter:
    """Computes orthogonal Manhattan waypoints and resolves port anchors."""

    def resolve_ports(
        self, edge: Edge, obstacles: Optional[Iterable[Any]] = None
    ) -> tuple[Port, Port]:
        """Determine connection ports for source and target elements."""
        if edge.source_port and edge.target_port:
            return (edge.source_port, edge.target_port)

        sb, tb = edge.source.bounds, edge.target.bounds
        dx = tb.center.x - sb.center.x
        dy = tb.center.y - sb.center.y

        if abs(dx) >= abs(dy):
            src_p = Port.EAST if dx > 0 else Port.WEST
            tgt_p = Port.WEST if dx > 0 else Port.EAST
        else:
            src_p = Port.SOUTH if dy > 0 else Port.NORTH
            tgt_p = Port.NORTH if dy > 0 else Port.SOUTH

        return (edge.source_port or src_p, edge.target_port or tgt_p)

    def _clamp_fillet_obstacles(
        self,
        pts: list[Point],
        corner_radius: float,
        obstacles: Sequence[Rect],
    ) -> float:
        n = len(pts)
        if n < 3 or corner_radius <= 0.0 or not obstacles:
            return corner_radius

        seg_lens: list[float] = []
        seg_units: list[Point] = []
        for j in range(n - 1):
            vx = pts[j + 1].x - pts[j].x
            vy = pts[j + 1].y - pts[j].y
            l = math.hypot(vx, vy)
            seg_lens.append(l)
            seg_units.append(Point(vx / l, vy / l) if l > 1e-6 else Point(0.0, 0.0))

        clamped = corner_radius
        for i in range(1, n - 1):
            l_in = seg_lens[i - 1]
            l_out = seg_lens[i]
            if l_in < 1e-6 or l_out < 1e-6:
                continue

            u_in = seg_units[i - 1]
            u_out = seg_units[i]

            dot = u_in.x * u_out.x + u_in.y * u_out.y
            if abs(dot) > 1e-6:
                continue

            p_c = pts[i]
            dx_apex = -0.25 * (u_in.x - u_out.x)
            dy_apex = -0.25 * (u_in.y - u_out.y)

            for obs in obstacles:
                exp = obs.expand(4.0)
                apex_x = p_c.x + clamped * dx_apex
                apex_y = p_c.y + clamped * dy_apex
                if exp.left < apex_x < exp.right and exp.top < apex_y < exp.bottom:
                    safe_r = clamped
                    cands: list[float] = []
                    if abs(dx_apex) > 1e-6:
                        target_x = exp.right if dx_apex < 0 else exp.left
                        cands.append((target_x - p_c.x) / dx_apex)
                    if abs(dy_apex) > 1e-6:
                        target_y = exp.bottom if dy_apex < 0 else exp.top
                        cands.append((target_y - p_c.y) / dy_apex)
                    valid_cands = [c for c in cands if c >= 0.0]
                    if valid_cands:
                        safe_r = min(safe_r, *valid_cands)
                    else:
                        safe_r = 0.0
                    clamped = min(clamped, safe_r)

        return clamped

    def route(
        self,
        edge: Edge,
        scene: Optional[RoutingScene] = None,
        style: Optional[EdgeStyle] = None,
        obstacles: Optional[Iterable[Any]] = None,
        clearance: Optional[float] = None,
    ) -> RoutedPath:
        """Compute ordered path waypoints between source and target elements."""
        scene, style, obstacles, clearance = _normalize_route_args(
            scene, style, obstacles, clearance
        )

        if clearance is not None:
            eff_clearance = clearance
        elif style is not None:
            eff_clearance = style.clearance
        elif getattr(edge, "clearance", None) is not None:
            eff_clearance = edge.clearance
        else:
            eff_clearance = 15.0

        if style is not None:
            eff_cr = style.corner_radius
            eff_routing = style.routing
        else:
            eff_cr = (
                edge._corner_radius
                if edge._corner_radius is not None
                else getattr(edge, "corner_radius", 0.0) or 0.0
            )
            eff_routing = (
                edge._routing
                if edge._routing is not None
                else getattr(edge, "routing", Routing.ORTHOGONAL)
            )

        if isinstance(eff_routing, str):
            eff_routing = Routing(eff_routing)

        src_port, tgt_port = self.resolve_ports(edge)
        p_start = edge.source.bounds.get_anchor(src_port.to_anchor())
        p_end = edge.target.bounds.get_anchor(tgt_port.to_anchor())

        if eff_routing == Routing.DIRECT:
            return RoutedPath(kind=PathKind.POLYLINE, points=(p_start, p_end), corner_radius=0.0)

        # Step default Manhattan midpoint
        default_pts = self._default_manhattan(p_start, p_end, src_port, tgt_port)

        if scene is not None:
            raw_obs = scene.obstacles_for(edge, clearance=0.0)
            norm_obstacles = [
                r
                for r in raw_obs
                if not (
                    (r.left <= p_start.x <= r.right and r.top <= p_start.y <= r.bottom)
                    or (r.left <= p_end.x <= r.right and r.top <= p_end.y <= r.bottom)
                )
            ]
        elif obstacles is not None:
            norm_obstacles = self._normalize_obstacles(edge, obstacles, p_start, p_end)
        else:
            norm_obstacles = []

        if not norm_obstacles:
            pts = default_pts
        else:
            # Fast path: check if default path has collision
            has_collision = False
            for i in range(len(default_pts) - 1):
                p_a, p_b = default_pts[i], default_pts[i + 1]
                for obs in norm_obstacles:
                    if segment_intersects_rect(p_a, p_b, obs):
                        has_collision = True
                        break
                if has_collision:
                    break

            if not has_collision:
                pts = default_pts
            else:
                # Compute detour path around obstacles
                detour = self._find_detour_path(
                    p_start, p_end, src_port, tgt_port, norm_obstacles, eff_clearance
                )
                pts = detour if detour is not None else default_pts

        # Clamping fillet corner radius against obstacles (D-16)
        if eff_cr > 0.0:
            clamped_cr = eff_cr
            if len(pts) >= 3 and norm_obstacles:
                clamped_cr = self._clamp_fillet_obstacles(pts, clamped_cr, norm_obstacles)
            if clamped_cr < 2.0:
                clamped_cr = 0.0
        else:
            clamped_cr = 0.0

        return RoutedPath(kind=PathKind.POLYLINE, points=tuple(pts), corner_radius=clamped_cr)

    def _default_manhattan(
        self, p_start: Point, p_end: Point, src_port: Port, tgt_port: Port
    ) -> list[Point]:
        if src_port in (Port.EAST, Port.WEST) and tgt_port in (Port.EAST, Port.WEST):
            if p_start.y == p_end.y:
                raw_pts = [p_start, p_end]
            else:
                mid_x = (p_start.x + p_end.x) / 2.0
                raw_pts = [p_start, Point(mid_x, p_start.y), Point(mid_x, p_end.y), p_end]
        elif src_port in (Port.NORTH, Port.SOUTH) and tgt_port in (Port.NORTH, Port.SOUTH):
            if p_start.x == p_end.x:
                raw_pts = [p_start, p_end]
            else:
                mid_y = (p_start.y + p_end.y) / 2.0
                raw_pts = [p_start, Point(p_start.x, mid_y), Point(p_end.x, mid_y), p_end]
        elif src_port in (Port.NORTH, Port.SOUTH):
            raw_pts = [p_start, Point(p_start.x, p_end.y), p_end]
        else:
            raw_pts = [p_start, Point(p_end.x, p_start.y), p_end]

        return self._dedup(raw_pts)

    def _normalize_obstacles(
        self, edge: Edge, obstacles: Iterable[Any], p_start: Point, p_end: Point
    ) -> list[Rect]:
        norm: list[Rect] = []
        for item in obstacles:
            if item is edge.source or item is edge.target:
                continue
            if hasattr(item, "id") and item.id in (edge.source.id, edge.target.id):
                continue
            if hasattr(item, "bounds") and isinstance(item.bounds, Rect):
                r = item.bounds
            elif isinstance(item, Rect):
                r = item
            else:
                continue

            # Skip if start or end point is inside the obstacle (e.g. enclosing group)
            if (r.left <= p_start.x <= r.right and r.top <= p_start.y <= r.bottom) or (
                r.left <= p_end.x <= r.right and r.top <= p_end.y <= r.bottom
            ):
                continue
            norm.append(r)
        return norm

    def _find_detour_path(
        self,
        p_start: Point,
        p_end: Point,
        src_port: Port,
        tgt_port: Port,
        obstacles: list[Rect],
        clearance: float,
    ) -> list[Point] | None:
        expanded: list[Rect] = []
        for obs in obstacles:
            exp = obs.expand(clearance)
            if (exp.left < p_start.x < exp.right and exp.top < p_start.y < exp.bottom) or (
                exp.left < p_end.x < exp.right and exp.top < p_end.y < exp.bottom
            ):
                exp = obs
            expanded.append(exp)

        xs = {p_start.x, p_end.x}
        ys = {p_start.y, p_end.y}
        for exp in expanded:
            xs.add(exp.left)
            xs.add(exp.right)
            ys.add(exp.top)
            ys.add(exp.bottom)

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        xs.add(min_x - clearance)
        xs.add(max_x + clearance)
        ys.add(min_y - clearance)
        ys.add(max_y + clearance)

        sorted_x = sorted(xs)
        sorted_y = sorted(ys)
        x_to_idx = {x: i for i, x in enumerate(sorted_x)}
        y_to_idx = {y: j for j, y in enumerate(sorted_y)}

        def is_h_passable(i1: int, i2: int, j: int) -> bool:
            x_mid = (sorted_x[i1] + sorted_x[i2]) / 2.0
            y = sorted_y[j]
            for exp in expanded:
                if exp.left < x_mid < exp.right and exp.top < y < exp.bottom:
                    return False
            return True

        def is_v_passable(i: int, j1: int, j2: int) -> bool:
            x = sorted_x[i]
            y_mid = (sorted_y[j1] + sorted_y[j2]) / 2.0
            for exp in expanded:
                if exp.left < x < exp.right and exp.top < y_mid < exp.bottom:
                    return False
            return True

        start_i, start_j = x_to_idx[p_start.x], y_to_idx[p_start.y]
        target_i, target_j = x_to_idx[p_end.x], y_to_idx[p_end.y]

        dist: dict[tuple[int, int, int], float] = {}
        parent: dict[tuple[int, int, int], tuple[int, int, int]] = {}

        dist[(start_i, start_j, 0)] = 0.0
        h_init = abs(p_start.x - p_end.x) + abs(p_start.y - p_end.y)
        pq: list[tuple[float, int, float, int, int, int]] = [
            (0.0, 0, h_init, start_i, start_j, 0)
        ]

        target_state: tuple[int, int, int] | None = None

        while pq:
            cost, bends, _, i, j, dir_mode = heapq.heappop(pq)
            if i == target_i and j == target_j:
                target_state = (i, j, dir_mode)
                break

            if cost > dist.get((i, j, dir_mode), float("inf")):
                continue

            # Transitions: Left, Right, Up, Down
            transitions: list[tuple[int, int, int, float, bool]] = []
            # Left (dir_mode=1)
            if i > 0 and is_h_passable(i - 1, i, j):
                if not (i == start_i and j == start_j and src_port == Port.EAST):
                    transitions.append((i - 1, j, 1, sorted_x[i] - sorted_x[i - 1], True))
            # Right (dir_mode=1)
            if i < len(sorted_x) - 1 and is_h_passable(i, i + 1, j):
                if not (i == start_i and j == start_j and src_port == Port.WEST):
                    transitions.append((i + 1, j, 1, sorted_x[i + 1] - sorted_x[i], True))
            # Up (dir_mode=2)
            if j > 0 and is_v_passable(i, j - 1, j):
                if not (i == start_i and j == start_j and src_port == Port.SOUTH):
                    transitions.append((i, j - 1, 2, sorted_y[j] - sorted_y[j - 1], False))
            # Down (dir_mode=2)
            if j < len(sorted_y) - 1 and is_v_passable(i, j, j + 1):
                if not (i == start_i and j == start_j and src_port == Port.NORTH):
                    transitions.append((i, j + 1, 2, sorted_y[j + 1] - sorted_y[j], False))

            for ni, nj, new_dir, dist_step, is_h in transitions:
                bend_step = 0
                if dir_mode != 0 and dir_mode != new_dir:
                    bend_step = 1
                elif dir_mode == 0:
                    if is_h and src_port in (Port.NORTH, Port.SOUTH):
                        bend_step = 1
                    elif not is_h and src_port in (Port.EAST, Port.WEST):
                        bend_step = 1

                step_cost = dist_step + 25.0 * bend_step
                new_cost = cost + step_cost
                state_key = (ni, nj, new_dir)
                if new_cost < dist.get(state_key, float("inf")):
                    dist[state_key] = new_cost
                    parent[state_key] = (i, j, dir_mode)
                    h = abs(sorted_x[ni] - p_end.x) + abs(sorted_y[nj] - p_end.y)
                    heapq.heappush(pq, (new_cost, bends + bend_step, h, ni, nj, new_dir))

        if target_state is None:
            return None

        # Reconstruct path
        path_indices: list[tuple[int, int]] = []
        curr: tuple[int, int, int] | None = target_state
        while curr is not None:
            path_indices.append((curr[0], curr[1]))
            curr = parent.get(curr)

        path_indices.reverse()
        pts = [Point(sorted_x[idx_i], sorted_y[idx_j]) for idx_i, idx_j in path_indices]
        return self._simplify_collinear(pts)

    def _simplify_collinear(self, points: list[Point]) -> list[Point]:
        if len(points) <= 2:
            return points
        simplified = [points[0]]
        for i in range(1, len(points) - 1):
            prev_p = simplified[-1]
            curr_p = points[i]
            next_p = points[i + 1]
            if (prev_p.x == curr_p.x == next_p.x) or (prev_p.y == curr_p.y == next_p.y):
                continue
            simplified.append(curr_p)
        simplified.append(points[-1])
        return self._dedup(simplified)

    def _dedup(self, points: list[Point]) -> list[Point]:
        deduped: list[Point] = []
        for p in points:
            if not deduped or p != deduped[-1]:
                deduped.append(p)
        return deduped


class EdgeRouter:
    """Unified routing facade dispatching across DIRECT, ORTHOGONAL, and CURVE strategies."""

    def __init__(self) -> None:
        self.orthogonal = OrthogonalRouter()
        self.curve = CurveRouter()

    def resolve_ports(
        self, edge: Edge, obstacles: Optional[Iterable[Any]] = None
    ) -> tuple[Port, Port]:
        """Determine connection ports for source and target elements."""
        if edge.routing in (Routing.CURVE, "curve"):
            return self.curve.resolve_ports(edge, obstacles=obstacles)
        return self.orthogonal.resolve_ports(edge, obstacles=obstacles)

    def route(
        self,
        edge: Edge,
        scene: Optional[RoutingScene] = None,
        style: Optional[EdgeStyle] = None,
        obstacles: Optional[Iterable[Any]] = None,
        clearance: Optional[float] = None,
    ) -> RoutedPath:
        """Compute ordered path waypoints using the appropriate routing strategy."""
        scene, style, obstacles, clearance = _normalize_route_args(
            scene, style, obstacles, clearance
        )

        if style is None:
            eff_routing = (
                edge._routing
                if edge._routing is not None
                else getattr(edge, "routing", Routing.ORTHOGONAL)
            )
            if isinstance(eff_routing, str):
                eff_routing = Routing(eff_routing)
            eff_cr = (
                edge._corner_radius
                if edge._corner_radius is not None
                else (getattr(edge, "corner_radius", 0.0) or 0.0)
            )
            eff_clearance = (
                clearance
                if clearance is not None
                else (
                    edge._clearance
                    if edge._clearance is not None
                    else getattr(edge, "clearance", 15.0)
                )
            )
            style = EdgeStyle(
                routing=eff_routing,
                corner_radius=float(eff_cr),
                clearance=float(eff_clearance),
            )

        routing = style.routing
        if isinstance(routing, str):
            routing = Routing(routing)

        if routing == Routing.DIRECT:
            obs = obstacles or (scene.obstacles_for(edge, clearance=0.0) if scene else None)
            src_port, tgt_port = self.resolve_ports(edge, obstacles=obs)
            p_start = edge.source.bounds.get_anchor(src_port.to_anchor())
            p_end = edge.target.bounds.get_anchor(tgt_port.to_anchor())
            return RoutedPath(kind=PathKind.POLYLINE, points=(p_start, p_end), corner_radius=0.0)

        if routing == Routing.CURVE:
            return self.curve.route(
                edge, scene=scene, style=style, obstacles=obstacles, clearance=clearance
            )

        return self.orthogonal.route(
            edge, scene=scene, style=style, obstacles=obstacles, clearance=clearance
        )


def route_all(
    edges: Sequence[Edge],
    elements: Sequence[Element],
    groups: Sequence[Group] = (),
    canvas: Optional[Rect] = None,
) -> dict[Edge, RoutedPath]:
    """Route all edges against a scene built from elements and groups."""
    all_elements: list[Element] = list(elements) + [g for g in groups if g not in elements]
    scene = RoutingScene.build(all_elements, canvas=canvas)
    er = EdgeRouter()
    routes: dict[Edge, RoutedPath] = {}
    for edge in edges:
        if edge.manual_waypoints:
            routes[edge] = RoutedPath(
                kind=PathKind.POLYLINE,
                points=tuple(edge.manual_waypoints),
                corner_radius=float(edge._corner_radius or 0.0),
            )
        else:
            style = EdgeStyle(
                routing=edge.routing,
                corner_radius=float(edge._corner_radius or 0.0),
                clearance=float(edge.clearance),
            )
            routes[edge] = er.route(edge, scene=scene, style=style)
    return routes

