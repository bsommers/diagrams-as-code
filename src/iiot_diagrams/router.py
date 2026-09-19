from __future__ import annotations

from iiot_diagrams.connections import Edge, Port, Routing
from iiot_diagrams.geometry import Point


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

    def route(self, edge: Edge) -> list[Point]:
        """Compute ordered path waypoints between source and target elements."""
        src_port, tgt_port = self.resolve_ports(edge)
        p_start = edge.source.bounds.get_anchor(src_port.to_anchor())
        p_end = edge.target.bounds.get_anchor(tgt_port.to_anchor())

        if edge.routing == Routing.DIRECT:
            return [p_start, p_end]

        # Step Manhattan midpoint with collinear straight-line simplification
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

        # Deduplicate consecutive identical waypoints
        deduped: list[Point] = []
        for p in raw_pts:
            if not deduped or p != deduped[-1]:
                deduped.append(p)
        return deduped
