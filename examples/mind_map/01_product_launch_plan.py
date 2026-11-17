"""Mind map: Product Launch Plan (MIND_MAP domain, Simple).

A central launch topic with four colour-coded branches radiating left and
right, each carrying two or three sub-topics joined by curved branch lines.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

BRANCHES = [
    # (label, colour, side, y, children)
    ("Marketing", "#E4572E", "left", 120, ["Teaser Campaign", "Press Kit", "Launch Webinar"]),
    ("Product", "#2E86AB", "right", 120, ["Feature Freeze", "Beta Feedback", "Release Notes"]),
    ("Sales", "#3BA55C", "left", 380, ["Pricing Tiers", "Partner Briefing"]),
    ("Support", "#8E5CC4", "right", 380, ["Help Center", "On-call Rota"]),
]


def diagram() -> Diagram:
    with Diagram("Product Launch Plan Mind Map", theme="pastel_light") as diag:
        cx, cy = 520.0, 250.0
        root = diag.shape(
            "**Product Launch**\nQ3 Release", 190, 70,
            style=Style(radius=35, fill="#FFE8A3", stroke="#C99A00", stroke_width=2.5, font_size=17),
        ).at(cx, cy, anchor="center")
        for label, colour, side, y, children in BRANCHES:
            sign = -1 if side == "left" else 1
            bx = cx + sign * 260
            branch = diag.shape(
                f"**{label}**", 130, 46,
                style=Style(radius=23, fill=colour, stroke=colour, text_color="#FFFFFF", font_size=15),
            ).at(bx, y, anchor="center")
            diag.connect(
                root.anchor(side, 0.5), branch.anchor("right" if sign < 0 else "left", 0.5),
                routing="curve", color=colour, width=3.5, head="none",
            )
            n = len(children)
            for i, child in enumerate(children):
                ty = y + (i - (n - 1) / 2) * 50
                tx = bx + sign * 210
                leaf = diag.shape(
                    child, 150, 34,
                    style=Style(radius=17, fill="#FFFFFF", stroke=colour, stroke_width=1.5, font_size=13),
                ).at(tx, ty, anchor="center")
                diag.connect(
                    branch.anchor(side, 0.5), leaf.anchor("right" if sign < 0 else "left", 0.5),
                    routing="curve", color=colour, width=1.8, head="none",
                )
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "01_product_launch_plan")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
