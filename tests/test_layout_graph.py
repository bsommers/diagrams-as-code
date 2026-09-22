from __future__ import annotations

from diagrams_as_code import Diagram
from diagrams_as_code.layout.graph import (
    LABEL_BELOW_EXTRA,
    build_scope_graph,
    lift,
    node_size,
    pinned_ids,
    scope_children,
)


def _nested() -> tuple[Diagram, dict]:
    d = Diagram()
    with d.group("Outer") as outer:
        with d.group("Inner") as inner:
            a = d.shape("A")
        b = d.shape("B")
    c = d.shape("C")
    a >> c
    a >> c
    b >> a
    return d, {"outer": outer, "inner": inner, "a": a, "b": b, "c": c}


def test_scope_children_in_declaration_order() -> None:
    d, e = _nested()
    assert [x.label for x in scope_children(d, None)] == ["Outer", "C"]
    assert [x.label for x in scope_children(d, e["outer"])] == ["Inner", "B"]


def test_lift_finds_the_direct_child_of_the_scope() -> None:
    d, e = _nested()
    assert lift(e["a"], None) is e["outer"]
    assert lift(e["a"], e["outer"]) is e["inner"]
    assert lift(e["c"], e["outer"]) is None


def test_edges_are_lifted_and_parallel_edges_merge() -> None:
    d, e = _nested()
    root = build_scope_graph(d, None, pinned=set())
    assert [(x.source, x.target, x.weight) for x in root.edges] == [
        (e["outer"].id, e["c"].id, 2)
    ]
    outer = build_scope_graph(d, e["outer"], pinned=set())
    assert [(x.source, x.target, x.weight) for x in outer.edges] == [
        (e["b"].id, e["inner"].id, 1)
    ]


def test_pinned_nodes_and_their_edges_are_excluded() -> None:
    d, e = _nested()
    g = build_scope_graph(d, None, pinned={e["c"].id})
    assert [n.id for n in g.nodes] == [e["outer"].id]
    assert g.edges == ()


def test_pinned_ids_cover_user_constraints_and_absolute_descendants() -> None:
    d = Diagram()
    with d.group("G") as g:
        a = d.shape("A").at(10, 10)
        b = d.shape("B")
    c = d.shape("C").right_of(b)
    ids = pinned_ids(d.solver.all_elements())
    assert ids == {a.id, g.id, c.id}


def test_node_size_reserves_room_for_labels_below() -> None:
    d = Diagram()
    inside = d.shape("In", width=100, height=50)
    icon = d.shape("Icon", width=48, height=48, kind="icon")
    below = d.shape("Below", width=100, height=50, label_position="bottom")
    assert node_size(inside) == (100, 50)
    assert node_size(icon) == (48, 48 + LABEL_BELOW_EXTRA)
    assert node_size(below) == (100, 50 + LABEL_BELOW_EXTRA)
