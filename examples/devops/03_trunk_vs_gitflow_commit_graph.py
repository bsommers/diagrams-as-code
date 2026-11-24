"""Trunk-based development versus GitFlow, drawn as commit graphs.

Both panels share one column grid: a column is one step in time. Commits are
placed by lane and column from a small data model in this script, so the
branching and merging structure can be read off the geometry: trunk-based work
stays on one long-lived line with branches that live for a single step, while
GitFlow keeps develop, release and hotfix lines alive and merges between them.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

X0, DX, R = 230.0, 62.0, 8.0
INK = "#1F2F57"
TAG_FILL = "#F3D98B"
TAG_EDGE = "#8A6D1A"
COLOURS = {
    "main": "#2F6DB5", "develop": "#2E8B57", "release": "#B8860B", "hotfix": "#B03A2E",
    "feature": "#7B4FB0", "short": "#7B4FB0",
}
LONG_LIVED = ("main", "develop")

# lanes: (name, colour key, y); commits: lane -> columns; links join (lane, column) pairs.
TRUNK = {
    "lanes": [("main", "main", 150.0), ("short-lived branch", "short", 230.0)],
    "commits": {"main": [0, 1, 2, 4, 5, 7, 8, 10, 11, 12], "short-lived branch": [3, 6, 9]},
    "merges": {("main", 4), ("main", 7), ("main", 10)},
    "links": [(("main", 2), ("short-lived branch", 3)), (("short-lived branch", 3), ("main", 4)),
              (("main", 5), ("short-lived branch", 6)), (("short-lived branch", 6), ("main", 7)),
              (("main", 8), ("short-lived branch", 9)), (("short-lived branch", 9), ("main", 10))],
    "tags": [("main", 4, "v1.0"), ("main", 7, "v1.1"), ("main", 10, "v1.2")],
    "lane_lines": ["main"],
}
Y1 = 440.0
FLOW = {
    "lanes": [("main", "main", Y1), ("hotfix", "hotfix", Y1 + 62), ("release", "release", Y1 + 124),
              ("develop", "develop", Y1 + 186), ("feature/search", "feature", Y1 + 248),
              ("feature/login", "feature", Y1 + 310)],
    "commits": {"main": [0, 9, 11], "hotfix": [10], "release": [7, 8],
                "develop": [0, 3, 6, 9, 11], "feature/search": [4, 5], "feature/login": [1, 2]},
    "merges": {("main", 9), ("main", 11), ("develop", 3), ("develop", 6), ("develop", 9), ("develop", 11)},
    "links": [(("develop", 0), ("feature/login", 1)), (("feature/login", 2), ("develop", 3)),
              (("develop", 3), ("feature/search", 4)), (("feature/search", 5), ("develop", 6)),
              (("develop", 6), ("release", 7)), (("release", 8), ("main", 9)), (("release", 8), ("develop", 9)),
              (("main", 9), ("hotfix", 10)), (("hotfix", 10), ("main", 11)), (("hotfix", 10), ("develop", 11))],
    "tags": [("main", 0, "v0.9"), ("main", 9, "v1.0"), ("main", 11, "v1.0.1")],
    "lane_lines": ["main", "develop", "release", "feature/search", "feature/login"],
}


def draw_panel(diag: Diagram, panel: dict, title: str, top: float) -> None:
    pos, colour = {}, {}
    for name, key, y in panel["lanes"]:
        colour[name] = COLOURS[key]
        diag.text(f"**{name}**", size=12).at(X0 - 56, y, anchor="right_center")
        for col in panel["commits"][name]:
            pos[(name, col)] = (X0 + col * DX, y)
    diag.text(f"**{title}**", size=15).at(40, top, anchor="left_center")
    # Straight runs along each lane, then the branch and merge links between lanes.
    for name in panel["lane_lines"]:
        cols = sorted(panel["commits"][name])
        for a, b in zip(cols, cols[1:]):
            diag.connect(pos[(name, a)], pos[(name, b)], routing="direct", arrow_head=False,
                         width=2.6, color=colour[name])
    for a, b in panel["links"]:
        branch = a if a[0] not in LONG_LIVED else b
        diag.connect(pos[a], pos[b], routing="direct", arrow_head=False, width=2.0, color=colour[branch[0]])
    for (name, col), (x, y) in pos.items():
        ring = (name, col) in panel["merges"]
        size = 2 * R + (4 if ring else 0)
        diag.shape("", size, size, fit_label=False,
                   style=Style(fill="#FFFFFF" if ring else colour[name], stroke=colour[name],
                               stroke_width=3.0 if ring else 1.5, radius=size / 2, shadow=False)).at(
            x, y, anchor="center")
    for name, col, text in panel["tags"]:
        x, y = pos[(name, col)]
        diag.shape(text, 54, 20, fit_label=False,
                   style=Style(fill=TAG_FILL, stroke=TAG_EDGE, radius=10, shadow=False, font_size=11)).at(
            x, y - 36, anchor="center")
        diag.connect((x, y - 26), (x, y - R - 4), routing="direct", arrow_head=False, width=1.0, color=TAG_EDGE)


def diagram() -> Diagram:
    with Diagram("Trunk-based development vs GitFlow", theme="paper") as diag:
        draw_panel(diag, TRUNK, "Trunk-based: one long-lived line, branches live for a day", 70.0)
        diag.text("Unfinished work ships dark behind feature flags;\nevery tag is cut straight from main.",
                  size=12, italic=True).at(X0 + 12.5 * DX + 30, 150.0, anchor="left_center")
        draw_panel(diag, FLOW, "GitFlow: develop, release and hotfix lines run in parallel", 360.0)
        diag.text("Release branches stabilise, then merge to main\nand back to develop; hotfixes branch from main.",
                  size=12, italic=True).at(X0 + 12.5 * DX + 30, Y1 + 124, anchor="left_center")
        ly = Y1 + 400
        diag.shape("", 16, 16, fit_label=False, style=Style(fill=INK, stroke=INK, radius=8, shadow=False)).at(
            X0, ly, anchor="center")
        diag.text("commit", size=11).at(X0 + 16, ly, anchor="left_center")
        diag.shape("", 20, 20, fit_label=False, style=Style(fill="#FFFFFF", stroke=INK, stroke_width=3.0, radius=10,
                                                            shadow=False)).at(X0 + 110, ly, anchor="center")
        diag.text("merge commit", size=11).at(X0 + 128, ly, anchor="left_center")
        diag.shape("v1.0", 54, 20, fit_label=False,
                   style=Style(fill=TAG_FILL, stroke=TAG_EDGE, radius=10, shadow=False, font_size=11)).at(
            X0 + 260, ly, anchor="left_center")
        diag.text("release tag", size=11).at(X0 + 324, ly, anchor="left_center")
    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "03_trunk_vs_gitflow_commit_graph")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
