from __future__ import annotations

from diagrams_as_code import Diagram, SVGRenderer
from diagrams_as_code.router import OrthogonalRouter


def _diag() -> Diagram:
    with Diagram(layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    return d


def test_solve_routes_every_edge() -> None:
    d = _diag()
    (edge,) = d.edges
    assert d.routes[id(edge)] == OrthogonalRouter().route(edge)


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


def test_renderer_still_routes_when_no_routes_are_given() -> None:
    d = _diag()
    svg = SVGRenderer(d.theme).render(elements=d.shapes, groups=d.groups, edges=d.edges, width=d.width, height=d.height)
    assert "<path" in svg
