from __future__ import annotations

from diagrams_as_code import Diagram, SVGRenderer
from diagrams_as_code.router import OrthogonalRouter, route_all


def _diag() -> Diagram:
    with Diagram(layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    return d


def test_solve_routes_every_edge() -> None:
    d = _diag()
    (edge,) = d.edges
    assert edge.waypoints is not None
    assert edge.waypoints == OrthogonalRouter().route(edge)
    assert d.routes[id(edge)] == edge.waypoints


def test_renderer_uses_given_routes_without_calling_the_router(monkeypatch) -> None:
    d = _diag()

    def fail(self, edge):
        raise AssertionError("renderer must not route when routes are given")

    monkeypatch.setattr(OrthogonalRouter, "route", fail)
    svg = SVGRenderer(d.theme).render(
        elements=d.shapes, groups=d.groups, edges=d.edges,
        width=d.width, height=d.height, routes=d.routes,
    )
    assert "<path" in svg


def test_renderer_uses_edge_waypoints_directly_without_routes_dict(monkeypatch) -> None:
    d = _diag()

    def fail(self, edge):
        raise AssertionError("renderer must not call router when edge has waypoints")

    monkeypatch.setattr(OrthogonalRouter, "route", fail)
    svg = SVGRenderer(d.theme).render(
        elements=d.shapes, groups=d.groups, edges=d.edges,
        width=d.width, height=d.height, routes=None,
    )
    assert "<path" in svg


def test_renderer_routes_with_route_all() -> None:
    d = _diag()
    (edge,) = d.edges
    edge.waypoints = None
    routes = route_all(d.edges, d.shapes, d.groups)
    svg = SVGRenderer(d.theme).render(
        elements=d.shapes, groups=d.groups, edges=d.edges, width=d.width, height=d.height, routes=routes
    )
    assert "<path" in svg

