"""Example: Org chart with solid-line and dotted-line reports (ORGANISATION domain).

Solid lines are the formal reporting line (who writes your review); dashed lines
are dotted-line relationships (who sets your professional standards or budget).
Positions come from a small leaf-slot tree layout (each management level is one row).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port, Style
from diagrams_as_code.output import render_all

EXEC = Style(fill="#D9E3F5", stroke="#2F4B86")
VP = Style(fill="#E4F1E8", stroke="#3C8D53")
IC = Style(fill="#FFFFFF", stroke="#6B7280")
DOTTED = "#B8860B"


#: (key, label, style, children); the tree is laid out by counting leaf slots.
TREE = ("CEO", EXEC, [
    ("CTO", "CTO", EXEC, [
        ("sec", "Head of Security", VP, [("seceng", "Security Engineer", IC, [])]),
        ("eng", "VP Engineering", VP, [
            ("be", "Backend Lead", IC, []),
            ("fe", "Frontend Lead", IC, []),
        ]),
    ]),
    ("CPO", "Chief Product Officer", EXEC, [
        ("pm", "Group Product Manager", VP, []),
        ("design", "Head of Design", VP, [("ux", "UX Researcher", IC, [])]),
    ]),
    ("CFO", "CFO", EXEC, [
        ("fin", "Finance Controller", VP, [("analyst", "FP&A Analyst", IC, [])]),
    ]),
])
SLOT_W, BOX_W, BOX_H, ROW_H = 168.0, 148.0, 50.0, 110.0
X0, Y0 = 60.0, 90.0


def diagram() -> Diagram:
    with Diagram("Org chart with dotted-line reports", theme="paper") as diag:
        nodes: dict[str, object] = {}
        edges: list[tuple[str, str]] = []
        next_slot = [0]

        def place(key, label, style, kids, depth):
            """Lay out a subtree; return its centre x. Leaves take consecutive slots."""
            if kids:
                xs = [place(*k, depth + 1) for k in kids]
                cx = (xs[0] + xs[-1]) / 2
                edges.extend((key, k[0]) for k in kids)
            else:
                cx = X0 + (next_slot[0] + 0.5) * SLOT_W
                next_slot[0] += 1
            nodes[key] = diag.shape(label, BOX_W, BOX_H, style=style).at(
                cx - BOX_W / 2, Y0 + depth * ROW_H)
            return cx

        place("ceo", "CEO", TREE[1], TREE[2], 0)

        for parent, child in edges:
            nodes[parent] >> diag.edge(source_port=Port.SOUTH, target_port=Port.NORTH,
                                       arrow_head=False) >> nodes[child]

        # Dotted-line relationships run sideways between neighbours on one row.
        nodes["eng"] >> diag.edge("delivery priorities", style="dashed", color=DOTTED,
                                  source_port=Port.EAST, target_port=Port.WEST,
                                  arrow_head=False) >> nodes["pm"]
        nodes["fe"] >> diag.edge("craft standards", style="dashed", color=DOTTED,
                                 source_port=Port.EAST, target_port=Port.WEST,
                                 arrow_head=False) >> nodes["ux"]
        diag.text("Solid line: formal reporting.  Dashed line: dotted-line (functional) relationship.",
                  size=12).at(X0, 40)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "01_org_chart_dotted_line")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
