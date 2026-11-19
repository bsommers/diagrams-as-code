"""Mind map: Auto-Laid-Out Cloud Certification Roadmap (MIND_MAP domain, Moderate).

A learning roadmap for a cloud certification path as a left-to-right topic
tree. Nothing is positioned by hand: the layered layout engine ranks each
topic from the branch structure, while styles colour every branch and make
nodes smaller with depth.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

TRACKS = [
    # (track, colour, [topic, ...])
    ("Foundations", "#7DD3FC", ["Cloud Concepts", "Billing & Pricing", "Shared Responsibility"]),
    ("Associate", "#86EFAC", ["Solutions Architect", "Developer", "SysOps Admin"]),
    ("Professional", "#FDE047", ["Architect Pro", "DevOps Engineer Pro"]),
    ("Specialty", "#F9A8D4", ["Security", "Advanced Networking", "Machine Learning"]),
]


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Cloud Certification Roadmap", theme="blueprint", layout="auto", direction="LR") as diag:
        root = diag.shape(
            "**Cloud Certification**\n**Roadmap**", 210, 74,
            style=Style(radius=37, fill="#E0F2FE", stroke="#E0F2FE", text_color="#0C2340", font_size=17),
        )
        for track, colour, topics in TRACKS:
            branch = diag.shape(
                f"**{track}**", 150, 46,
                style=Style(radius=23, fill=colour, stroke=colour, text_color="#0C2340", font_size=15),
            )
            root >> diag.edge(color=colour, routing="curve", width=3.5, head="none") >> branch
            for topic in topics:
                leaf = diag.shape(
                    topic, 190, 34,
                    style=Style(radius=17, fill="#0C2340", stroke=colour, stroke_width=1.5, text_color="#F0F9FF", font_size=13),
                )
                branch >> diag.edge(color=colour, routing="curve", width=1.8, head="none") >> leaf
    return diag


def build_diagram(output_dir: Path | str = "examples/mind_map") -> Path:
    return render_all(diagram(), output_dir, "11_auto_cloud_certification_roadmap")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/mind_map")
    build_diagram(dest)
