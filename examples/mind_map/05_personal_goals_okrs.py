"""Mind map: Personal Goals and OKRs (MIND_MAP domain, Simple).

A year of personal objectives as a mind map. Each objective is a branch and
its key results are the leaves; a leaf's fill deepens with progress and a
completed result gets a double border, so the map doubles as a status board.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 560.0, 180.0
PITCH = 46.0
GAP = 34.0

OBJECTIVES = {
    "left": [
        ("Health", "#0EA5E9", [("Run a half marathon", 0.6), ("Sleep 7h, 5 nights/week", 0.8), ("Cook at home 4x/week", 0.4)]),
        ("Finances", "#10B981", [("Six-month emergency fund", 0.9), ("Max out pension", 0.3)]),
    ],
    "right": [
        ("Career", "#F59E0B", [("Lead one launch", 0.5), ("Give a conference talk", 0.1), ("Mentor two juniors", 1.0)]),
        ("Learning", "#8B5CF6", [("Pass cloud certification", 0.7), ("Read 20 books", 0.45)]),
    ],
}


def _mix(colour: str, amount: float) -> str:
    """``colour`` blended into white: 0 gives white, 1 the colour itself."""
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(255 + (c - 255) * amount):02X}" for c in (r, g, b))


def diagram() -> Diagram:
    with Diagram("Personal Goals and OKRs Mind Map", theme="iiot_light") as diag:
        root = diag.shape(
            "**2027 Personal OKRs**", 210, 64,
            style=Style(radius=32, fill="#1E293B", stroke="#1E293B", text_color="#FFFFFF", font_size=17),
        ).at(CX, CY, anchor="center")

        for side, objectives in OBJECTIVES.items():
            sign = -1 if side == "left" else 1
            inner = "right" if side == "left" else "left"
            total = sum(len(o[2]) * PITCH for o in objectives) + GAP * (len(objectives) - 1)
            top = CY - total / 2
            for label, colour, results in objectives:
                block = len(results) * PITCH
                objective = diag.shape(
                    f"**{label}**", 130, 46,
                    style=Style(radius=23, fill=colour, stroke=colour, text_color="#FFFFFF", font_size=15),
                ).at(CX + sign * 240, top + block / 2, anchor="center")
                diag.connect(root.anchor(side, 0.5), objective.anchor(inner, 0.5),
                             routing="curve", color=colour, width=3.5, head="none")
                for i, (kr, progress) in enumerate(results):
                    done = progress >= 1.0
                    leaf = diag.shape(
                        f"{kr} · **{round(progress * 100)}%**", 250, 34,
                        style=Style(radius=17, fill=_mix(colour, 0.08 + 0.55 * progress), stroke=colour,
                                    stroke_width=2.2 if done else 1.5, text_color="#0F172A",
                                    font_size=13, double=3 if done else None),
                    ).at(CX + sign * 495, top + PITCH * (i + 0.5), anchor="center")
                    diag.connect(objective.anchor(side, 0.5), leaf.anchor(inner, 0.5),
                                 routing="curve", color=colour, width=1.8, head="none")
                top += block + GAP
    return diag


def build_diagram(output_dir: Path | str = "examples/mind_map") -> Path:
    return render_all(diagram(), output_dir, "05_personal_goals_okrs")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/mind_map")
    build_diagram(dest)
