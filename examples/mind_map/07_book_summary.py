"""Mind map: Book Summary of Designing Data-Intensive Applications (MIND_MAP domain, Moderate).

A three-level reading summary. The book sits at the centre, its parts are
the main branches, chapters are the sub-topics and each chapter ends in a
dashed one-line takeaway. Grey levels instead of hues keep the map
print-friendly; node size shrinks with depth.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 700.0, 210.0
PITCH = 44.0
GAP = 30.0

PARTS = {
    "left": [
        ("Part I**\n**Foundations", "#1F1F1F", [
            ("Reliability", "Faults are not failures"),
            ("Scalability", "Describe load, then percentiles"),
            ("Data Models", "Relational vs document vs graph"),
            ("Storage Engines", "LSM-trees vs B-trees"),
        ]),
        ("Part III**\n**Derived Data", "#6B6B6B", [
            ("Batch Processing", "Immutable inputs, rerunnable"),
            ("Stream Processing", "Logs as the source of truth"),
        ]),
    ],
    "right": [
        ("Part II**\n**Distributed Data", "#444444", [
            ("Replication", "Leader, multi-leader, leaderless"),
            ("Partitioning", "Key range vs hash"),
            ("Transactions", "Isolation levels differ"),
            ("Consistency", "Linearizability costs latency"),
            ("Consensus", "Total order broadcast"),
        ]),
        ("Takeaways", "#8A8A8A", [
            ("Trade-offs", "No one-size database"),
        ]),
    ],
}


def diagram() -> Diagram:
    with Diagram("Book Summary: Designing Data-Intensive Applications", theme="monochrome") as diag:
        root = diag.shape(
            "**Designing Data-Intensive**\n**Applications**\n*M. Kleppmann*", 230, 92,
            style=Style(radius=30, fill="#FFFFFF", stroke="#000000", stroke_width=3, double=4, font_size=16),
        ).at(CX, CY, anchor="center")

        for side, parts in PARTS.items():
            sign = -1 if side == "left" else 1
            inner = "right" if side == "left" else "left"
            total = sum(len(p[2]) * PITCH for p in parts) + GAP * (len(parts) - 1)
            top = CY - total / 2
            for label, shade, chapters in parts:
                block = len(chapters) * PITCH
                part = diag.shape(
                    f"**{label}**", 150, 54,
                    style=Style(radius=27, fill=shade, stroke=shade, text_color="#FFFFFF", font_size=14),
                ).at(CX + sign * 230, top + block / 2, anchor="center")
                diag.connect(root.anchor(side, 0.5), part.anchor(inner, 0.5),
                             routing="curve", color=shade, width=4, head="none")
                for i, (chapter, takeaway) in enumerate(chapters):
                    y = top + PITCH * (i + 0.5)
                    node = diag.shape(
                        chapter, 150, 32,
                        style=Style(radius=16, fill="#F2F2F2", stroke=shade, stroke_width=1.6, font_size=13),
                    ).at(CX + sign * 470, y, anchor="center")
                    diag.connect(part.anchor(side, 0.5), node.anchor(inner, 0.5),
                                 routing="curve", color=shade, width=2, head="none")
                    note = diag.shape(
                        f"*{takeaway}*", 220, 28,
                        style=Style(radius=14, fill="#FFFFFF", stroke=shade, stroke_width=1, dash="4,3",
                                    shadow=False, font_size=12),
                    ).at(CX + sign * 690, y, anchor="center")
                    diag.connect(node.anchor(side, 0.5), note.anchor(inner, 0.5),
                                 routing="curve", color=shade, width=1, head="none", style="dashed")
                top += block + GAP
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "07_book_summary")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
