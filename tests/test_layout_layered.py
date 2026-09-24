from __future__ import annotations

import pytest

from diagrams_as_code.geometry import Rect
from diagrams_as_code.layout.base import LayoutEdge, LayoutGraph, LayoutNode
from diagrams_as_code.layout.layered import LayeredLayout


def graph(nodes: list[tuple[str, float, float]], edges: list[tuple[str, str]]) -> LayoutGraph:
    return LayoutGraph(
        nodes=tuple(LayoutNode(n, w, h, i) for i, (n, w, h) in enumerate(nodes)),
        edges=tuple(LayoutEdge(s, t) for s, t in edges),
    )


def rects(g: LayoutGraph, pos) -> dict[str, Rect]:
    return {n.id: Rect(pos[n.id].x, pos[n.id].y, n.width, n.height) for n in g.nodes}


def test_empty_graph() -> None:
    assert LayeredLayout().arrange(LayoutGraph((), ())) == {}


def test_chain_left_to_right() -> None:
    g = graph([("a", 100, 50), ("b", 100, 50), ("c", 100, 50)], [("a", "b"), ("b", "c")])
    pos = LayeredLayout(rank_gap=80).arrange(g)
    assert [(pos[n].x, pos[n].y) for n in "abc"] == [(0, 0), (180, 0), (360, 0)]


def test_chain_top_to_bottom() -> None:
    g = graph([("a", 100, 50), ("b", 100, 50)], [("a", "b")])
    pos = LayeredLayout(direction="TB", rank_gap=80).arrange(g)
    assert (pos["a"].x, pos["a"].y, pos["b"].x, pos["b"].y) == (0, 0, 0, 130)


def test_diamond_stacks_the_middle_rank_and_centers_the_ends() -> None:
    g = graph([(n, 100, 50) for n in "abcd"], [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    pos = LayeredLayout(node_gap=40).arrange(g)
    assert pos["b"].x == pos["c"].x == 180
    assert pos["c"].y - pos["b"].y == 90
    assert pos["a"].y == pos["d"].y == 45  # centered on the 140-tall middle rank


def test_ordering_removes_an_avoidable_crossing() -> None:
    g = graph([("a", 50, 50), ("b", 50, 50), ("c", 50, 50), ("d", 50, 50)], [("a", "d"), ("b", "c")])
    pos = LayeredLayout().arrange(g)
    assert pos["d"].y < pos["c"].y


def test_cycle_is_ranked_in_declaration_order() -> None:
    g = graph([("a", 50, 50), ("b", 50, 50)], [("a", "b"), ("b", "a")])
    pos = LayeredLayout().arrange(g)
    assert pos["a"].x < pos["b"].x


def test_self_loops_and_unknown_endpoints_are_ignored() -> None:
    g = graph([("a", 50, 50)], [("a", "a"), ("a", "ghost")])
    assert LayeredLayout().arrange(g) == {"a": LayeredLayout().arrange(g)["a"]}


def _messy() -> LayoutGraph:
    names = [f"n{i}" for i in range(12)]
    sizes = [(n, 60 + 10 * (i % 4), 40 + 15 * (i % 3)) for i, n in enumerate(names)]
    edges = [(names[i], names[(i * 7 + 3) % 12]) for i in range(12)]
    return graph(sizes, edges)


@pytest.mark.parametrize("direction", ["LR", "TB"])
def test_no_two_nodes_overlap(direction: str) -> None:
    g = _messy()
    r = rects(g, LayeredLayout(direction=direction).arrange(g))
    ids = sorted(r)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            assert not r[a].intersects(r[b]), (a, b)


def test_arrange_is_deterministic() -> None:
    assert LayeredLayout().arrange(_messy()) == LayeredLayout().arrange(_messy())


def test_invalid_arguments() -> None:
    with pytest.raises(ValueError, match="direction"):
        LayeredLayout(direction="RL")
    with pytest.raises(ValueError, match="non-negative"):
        LayeredLayout(rank_gap=-1)


@pytest.mark.parametrize("direction", ["LR", "TB"])
def test_rank_order_respected_for_forward_edges(direction: str) -> None:
    """For every forward edge u→v (source index < target index), rank(u) < rank(v)."""
    g = _messy()
    # Extract only forward edges (source index < target index)
    node_index = {n.id: n.index for n in g.nodes}
    forward_edges = [
        (e.source, e.target)
        for e in g.edges
        if node_index[e.source] < node_index[e.target]
    ]
    # Create graph with only forward edges
    acyclic = LayoutGraph(
        nodes=g.nodes,
        edges=tuple(LayoutEdge(s, t) for s, t in forward_edges),
    )
    pos = LayeredLayout(direction=direction).arrange(acyclic)

    # For LR: rank order is x order; for TB: rank order is y order
    axis = "x" if direction == "LR" else "y"
    for source, target in forward_edges:
        source_pos = getattr(pos[source], axis)
        target_pos = getattr(pos[target], axis)
        assert source_pos < target_pos, f"Edge {source}→{target}: {source} at {source_pos} not < {target} at {target_pos}"


def test_multi_rank_edges_handled_in_ordering() -> None:
    """Verify edges spanning >= 2 ranks are properly ordered without crash or overlap."""
    nodes = [
        ("a", 50, 50),
        ("b", 50, 50),
        ("c", 50, 50),
        ("d", 50, 50),
        ("e", 50, 50),
    ]
    edges = [
        ("a", "c"),  # rank 0 -> rank 1
        ("c", "e"),  # rank 1 -> rank 2
        ("b", "e"),  # rank 0/1 -> rank 2
        ("a", "e"),  # rank 0 -> rank 2 (multi-rank!)
        ("d", "e"),  # rank 1 -> rank 2
    ]
    g = graph(nodes, edges)
    pos = LayeredLayout().arrange(g)
    assert len(pos) == 5
    # Confirm valid coordinates for all nodes
    for nid in "abcde":
        assert nid in pos
        assert pos[nid].x >= 0
        assert pos[nid].y >= 0
    # a must be rank 0 (x=0)
    assert pos["a"].x == 0
    # e must be at the highest rank
    assert pos["e"].x > pos["a"].x

