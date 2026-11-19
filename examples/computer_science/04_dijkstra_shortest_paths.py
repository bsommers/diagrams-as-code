"""Dijkstra's algorithm on a weighted digraph, with its run laid out as a table.

The graph has six vertices and nine weighted arcs. Heavy arcs form the
shortest-path tree from $s$; each vertex shows its final distance $d(v)$.
The table beside it is the distance vector after each vertex is taken from
the priority queue; the shaded cell is the vertex settled at that step. The
distances and the table are computed by running the algorithm in the script.
"""
from __future__ import annotations

import heapq
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

VERTICES = {"s": (90, 220), "a": (290, 100), "b": (290, 340), "c": (510, 100), "d": (510, 340), "t": (710, 220)}
ARCS = [("s", "a", 7), ("s", "b", 2), ("b", "a", 3), ("a", "c", 2), ("b", "c", 8),
        ("b", "d", 5), ("c", "d", 1), ("c", "t", 6), ("d", "t", 2)]
D = 62.0
NODE = Style(radius=D / 2, font_size=13)
SOURCE = Style(radius=D / 2, font_size=13, double=4)
TREE = {"routing": "direct", "width": 2.6, "arrow_size": 0.9}
OTHER = {"routing": "direct", "width": 0.9, "color": "#888888", "style": "dashed", "arrow_size": 0.9}
CELL_W, CELL_H = 42.0, 28.0
HEAD = Style(fill="#E4E4E8", font_size=12)
PLAIN = Style(fill="#FFFFFF", font_size=12)
SETTLED = Style(fill="#9FA6B8", font_size=12)


def dijkstra(source: str):
    """Final distances, predecessors and the distance vector after each extraction."""
    inf = float("inf")
    dist = {v: inf for v in VERTICES}
    pred: dict[str, str] = {}
    dist[source] = 0
    heap, done, trace = [(0, source)], set(), []
    while heap:
        du, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for x, y, w in ARCS:
            if x == u and du + w < dist[y]:
                dist[y], pred[y] = du + w, u
                heapq.heappush(heap, (dist[y], y))
        trace.append((u, dict(dist)))
    return dist, pred, trace


def diagram() -> Diagram:
    dist, pred, trace = dijkstra("s")
    with Diagram("Dijkstra shortest paths on a weighted digraph", theme="paper") as diag:
        nodes = {}
        for name, (x, y) in VERTICES.items():
            label = f"$\\mathbf{{{name}}}$\n$d = {dist[name]:g}$"
            nodes[name] = diag.shape(label, D, D, style=SOURCE if name == "s" else NODE).at(x, y, anchor="center")

        for u, v, w in ARCS:
            in_tree = pred.get(v) == u
            # Circles are boxes to the router, so end the arcs on the circles by hand.
            (x1, y1), (x2, y2) = VERTICES[u], VERTICES[v]
            length = math.hypot(x2 - x1, y2 - y1)
            ux, uy, r = (x2 - x1) / length, (y2 - y1) / length, D / 2 + 1
            diag.connect((x1 + ux * r, y1 + uy * r), (x2 - ux * r, y2 - uy * r), label=f"{w}",
                         **(TREE if in_tree else OTHER))

        # The run, one row per extraction from the queue.
        x0, y0 = 820.0, 80.0
        order = list(VERTICES)
        diag.text("**Distance vector after each step**", size=13).at(x0, y0 - 10, anchor="bottom_left")
        header = ["step", *order]
        for col, title in enumerate(header):
            text = title if col == 0 else f"$d({title})$"
            diag.shape(text, CELL_W + (14 if col == 0 else 0), CELL_H, style=HEAD, fit_label=False).at(
                x0 + col * CELL_W + (14 if col else 0), y0)
        for row, (settled, vector) in enumerate(trace, start=1):
            y = y0 + row * CELL_H
            diag.shape(f"{row}: ${settled}$", CELL_W + 14, CELL_H, style=PLAIN, fit_label=False).at(x0, y)
            for col, name in enumerate(order, start=1):
                value = "$\\infty$" if vector[name] == float("inf") else f"{vector[name]:g}"
                diag.shape(value, CELL_W, CELL_H, style=SETTLED if name == settled else PLAIN,
                           fit_label=False).at(x0 + col * CELL_W + 14, y)

        bottom = y0 + (len(trace) + 1) * CELL_H
        diag.text(
            "**Relaxation** of arc $(u, v)$ with weight $w$:\n"
            "$d(v) \\leftarrow \\min(d(v),\\; d(u) + w(u, v))$\n\n"
            "**Cost** with a binary heap: $O((V + E) \\log V)$\n"
            "with a Fibonacci heap: $O(E + V \\log V)$\n"
            "Correct only for weights $w \\geq 0$.",
            size=12,
        ).at(x0, bottom + 24)
        diag.text("heavy: shortest-path tree\ndashed: arcs outside the tree", size=11,
                  font="serif", italic=True, color="#555555").at(60, 400)
        diag.caption("**Figure 4:** Single-source shortest paths from $s$; $d(t) = 9$ along "
                     "$s \\to b \\to d \\to t$", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/computer_science") -> Path:
    return render_all(diagram(), output_dir, "04_dijkstra_shortest_paths")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/computer_science")
    build_diagram(dest)
