"""Group titles fit their group and are kept clear of edge badges."""
from __future__ import annotations

from diagrams_as_code import Diagram
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.labels import edge_badge_rect, group_title_rect


def test_group_widens_to_fit_its_title():
    with Diagram("t", theme="monochrome") as d:
        with d.group("A Rather Long Group Title Indeed") as g:
            s = d.shape("A", width=100, height=50).at(100, 150)
    d.solve()
    title = group_title_rect(g)
    assert title.right <= g.bounds.right - 4
    # Widened evenly: the child stays centred.
    assert abs((s.bounds.left - g.bounds.left) - (g.bounds.right - s.bounds.right)) < 1e-6
    assert "title_overflow" not in audit_diagram(d)


def test_short_title_leaves_the_group_alone():
    with Diagram("t", theme="monochrome") as d:
        with d.group("G", padding=25) as g:
            d.shape("A", width=100, height=50).at(100, 150)
    d.solve()
    assert g.bounds.width == 150


def test_badge_does_not_cover_a_group_title():
    with Diagram("t", theme="monochrome") as d:
        with d.group("Upper"):
            a = d.shape("A", width=140, height=60).at(80, 110)
        with d.group("Lower Layer Title") as low:
            b = d.shape("B", width=140, height=60).below(a, margin=110)
        edge = d.connect(a, b, label="handoff")
    d.solve()
    badge, title = edge_badge_rect(edge, d.routes[edge]), group_title_rect(low)
    assert badge.right <= title.left or badge.left >= title.right or badge.bottom <= title.top or badge.top >= title.bottom
    assert "badge_over_title" not in audit_diagram(d)
