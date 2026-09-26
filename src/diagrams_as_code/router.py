from __future__ import annotations

import heapq
from typing import Any, Iterable, Optional

from diagrams_as_code.connections import Edge, Port, Routing
from diagrams_as_code.geometry import Point, Rect


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


class CurveRouter:
    """Computes cubic Bezier control handles from port normal vectors."""

    def resolve_ports(self, edge: Edge) -> tuple[Port, Port]:
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

    def route(
        self,
        edge: Edge,
        obstacles: Optional[Iterable[Any]] = None,
        clearance: float = 15.0,
    ) -> list[Point]:
        """Compute ordered path waypoints [P_start, C_1, C_2, P_end] for cubic Bezier curve."""
        src_port, tgt_port = self.resolve_ports(edge)
        p_start = edge.source.bounds.get_anchor(src_port.to_anchor())
        p_end = edge.target.bounds.get_anchor(tgt_port.to_anchor())

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

        return [p_start, c1, c2, p_end]


class OrthogonalRouter:
    """Computes orthogonal Manhattan waypoints and resolves port anchors."""

    def resolve_ports(self, edge: Edge) -> tuple[Port, Port]:
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

    def route(
        self,
        edge: Edge,
        obstacles: Optional[Iterable[Any]] = None,
        clearance: float = 15.0,
    ) -> list[Point]:
        """Compute ordered path waypoints between source and target elements."""
        if edge.routing in (Routing.CURVE, "curve"):
            return CurveRouter().route(edge, obstacles=obstacles, clearance=clearance)

        src_port, tgt_port = self.resolve_ports(edge)
        p_start = edge.source.bounds.get_anchor(src_port.to_anchor())
        p_end = edge.target.bounds.get_anchor(tgt_port.to_anchor())

        if edge.routing == Routing.DIRECT:
            return [p_start, p_end]

        # Step default Manhattan midpoint
        default_pts = self._default_manhattan(p_start, p_end, src_port, tgt_port)

        if obstacles is None:
            return default_pts

        norm_obstacles = self._normalize_obstacles(edge, obstacles, p_start, p_end)
        if not norm_obstacles:
            return default_pts

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
            return default_pts

        # Compute detour path around obstacles
        detour = self._find_detour_path(
            p_start, p_end, src_port, tgt_port, norm_obstacles, clearance
        )
        return detour if detour is not None else default_pts

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

    def resolve_ports(self, edge: Edge) -> tuple[Port, Port]:
        """Determine connection ports for source and target elements."""
        if edge.routing in (Routing.CURVE, "curve"):
            return self.curve.resolve_ports(edge)
        return self.orthogonal.resolve_ports(edge)

    def route(
        self,
        edge: Edge,
        obstacles: Optional[Iterable[Any]] = None,
        clearance: float = 15.0,
    ) -> list[Point]:
        """Compute ordered path waypoints using the appropriate routing strategy."""
        if edge.routing in (Routing.CURVE, "curve"):
            return self.curve.route(edge, obstacles=obstacles, clearance=clearance)
        return self.orthogonal.route(edge, obstacles=obstacles, clearance=clearance)

