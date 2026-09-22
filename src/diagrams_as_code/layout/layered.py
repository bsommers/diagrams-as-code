"""Layered (Sugiyama-style) placement for one scope of a diagram.

Ranks follow edge direction, each rank is ordered to reduce crossings, and
ranks are spaced evenly. Everything is deterministic: ties break by the
node's declaration index, and no unordered set is ever iterated.
Only edges between adjacent ranks inform ordering; longer edges still set
ranks but get no dummy nodes (v1).
"""
from __future__ import annotations

import heapq

from diagrams_as_code.geometry import Point
from diagrams_as_code.layout.base import LayoutGraph, LayoutNode

DIRECTIONS = ("LR", "TB")

Edges = dict[tuple[str, str], int]


class LayeredLayout:
    """Rank nodes by edge direction and space the ranks along one axis."""

    def __init__(
        self,
        direction: str = "LR",
        rank_gap: float = 80.0,
        node_gap: float = 40.0,
        sweeps: int = 4,
    ) -> None:
        if direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, got {direction!r}")
        if rank_gap < 0 or node_gap < 0:
            raise ValueError("rank_gap and node_gap must be non-negative")
        self.direction = direction
        self.rank_gap = float(rank_gap)
        self.node_gap = float(node_gap)
        self.sweeps = int(sweeps)

    def arrange(self, graph: LayoutGraph) -> dict[str, Point]:
        """Return the top-left corner of every node in ``graph``."""
        if not graph.nodes:
            return {}
        index = {n.id: n.index for n in graph.nodes}
        dag = _acyclic_edges(graph, index)
        rank = _ranks(dag, index)
        layers = _order(rank, dag, index, self.sweeps)
        return self._coordinates(layers, {n.id: n for n in graph.nodes})

    def _coordinates(
        self, layers: list[list[str]], nodes: dict[str, LayoutNode]
    ) -> dict[str, Point]:
        lr = self.direction == "LR"

        def along(n: LayoutNode) -> float:
            return n.width if lr else n.height

        def across(n: LayoutNode) -> float:
            return n.height if lr else n.width

        extents = [max(along(nodes[i]) for i in layer) for layer in layers]
        spans = [
            sum(across(nodes[i]) for i in layer) + self.node_gap * (len(layer) - 1)
            for layer in layers
        ]
        widest = max(spans)
        out: dict[str, Point] = {}
        offset = 0.0
        for layer, extent, span in zip(layers, extents, spans):
            cursor = (widest - span) / 2.0
            for nid in layer:
                n = nodes[nid]
                a = offset + (extent - along(n)) / 2.0
                out[nid] = Point(a, cursor) if lr else Point(cursor, a)
                cursor += across(n) + self.node_gap
            offset += extent + self.rank_gap
        return out


def _acyclic_edges(graph: LayoutGraph, index: dict[str, int]) -> Edges:
    """Merge parallel edges, drop self-loops, reverse DFS back edges."""
    weights: Edges = {}
    for e in graph.edges:
        if e.source == e.target or e.source not in index or e.target not in index:
            continue
        key = (e.source, e.target)
        weights[key] = weights.get(key, 0) + e.weight

    succ: dict[str, list[str]] = {n: [] for n in index}
    for s, t in weights:
        succ[s].append(t)
    for targets in succ.values():
        targets.sort(key=index.__getitem__)

    state: dict[str, int] = {}  # 1 = on the DFS stack, 2 = finished
    back: set[tuple[str, str]] = set()
    for root in sorted(index, key=index.__getitem__):
        if root in state:
            continue
        state[root] = 1
        stack = [(root, iter(succ[root]))]
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
            elif state.get(nxt) == 1:
                back.add((node, nxt))
            elif nxt not in state:
                state[nxt] = 1
                stack.append((nxt, iter(succ[nxt])))

    dag: Edges = {}
    for (s, t), w in weights.items():
        if (s, t) in back:
            s, t = t, s
        dag[(s, t)] = dag.get((s, t), 0) + w
    return dag


def _ranks(dag: Edges, index: dict[str, int]) -> dict[str, int]:
    """Longest-path ranking; sources and isolated nodes get rank 0."""
    preds: dict[str, list[str]] = {n: [] for n in index}
    succ: dict[str, list[str]] = {n: [] for n in index}
    indeg = {n: 0 for n in index}
    for s, t in dag:
        succ[s].append(t)
        preds[t].append(s)
        indeg[t] += 1
    heap = [(index[n], n) for n in index if indeg[n] == 0]
    heapq.heapify(heap)
    rank: dict[str, int] = {}
    while heap:
        _, n = heapq.heappop(heap)
        rank[n] = max((rank[p] + 1 for p in preds[n]), default=0)
        for t in succ[n]:
            indeg[t] -= 1
            if indeg[t] == 0:
                heapq.heappush(heap, (index[t], t))
    return rank


def _order(
    rank: dict[str, int], dag: Edges, index: dict[str, int], sweeps: int
) -> list[list[str]]:
    """Barycenter sweeps; a sweep is kept only if it lowers crossings."""
    layers: list[list[str]] = [[] for _ in range(max(rank.values()) + 1)]
    for n in sorted(rank, key=index.__getitem__):
        layers[rank[n]].append(n)
    adjacent = [(s, t, w) for (s, t), w in dag.items() if rank[t] - rank[s] == 1]

    best = [list(layer) for layer in layers]
    best_cross = crossings(best, adjacent)
    current = [list(layer) for layer in best]
    for i in range(sweeps):
        _sweep(current, adjacent, downward=(i % 2 == 0))
        c = crossings(current, adjacent)
        if c < best_cross:
            best, best_cross = [list(layer) for layer in current], c
        else:
            current = [list(layer) for layer in best]
    return best


def _sweep(
    layers: list[list[str]], adjacent: list[tuple[str, str, int]], downward: bool
) -> None:
    ranks = range(1, len(layers)) if downward else range(len(layers) - 2, -1, -1)
    for r in ranks:
        ref = layers[r - 1] if downward else layers[r + 1]
        ref_pos = {n: i for i, n in enumerate(ref)}
        mine = layers[r]
        mine_pos = {n: i for i, n in enumerate(mine)}
        acc: dict[str, list[float]] = {}
        for s, t, w in adjacent:
            node, other = (t, s) if downward else (s, t)
            if node in mine_pos and other in ref_pos:
                a = acc.setdefault(node, [0.0, 0.0])
                a[0] += ref_pos[other] * w
                a[1] += w

        def key(n: str) -> tuple[float, int]:
            a = acc.get(n)
            return (a[0] / a[1] if a else float(mine_pos[n]), mine_pos[n])

        layers[r] = sorted(mine, key=key)


def crossings(layers: list[list[str]], edges: list[tuple[str, str, int]]) -> int:
    """Weighted count of crossing edge pairs between adjacent layers."""
    pos: dict[str, int] = {}
    layer_of: dict[str, int] = {}
    for r, layer in enumerate(layers):
        for i, n in enumerate(layer):
            pos[n] = i
            layer_of[n] = r
    total = 0
    for r in range(len(layers) - 1):
        spans = [(pos[s], pos[t], w) for s, t, w in edges if layer_of[s] == r]
        for i, a in enumerate(spans):
            for b in spans[i + 1:]:
                if (a[0] - b[0]) * (a[1] - b[1]) < 0:
                    total += a[2] * b[2]
    return total
