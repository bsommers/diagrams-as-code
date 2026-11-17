"""Mind map: Sprint Planning Meeting Notes (MIND_MAP domain, Simple).

Notes from one meeting captured as a mind map: who attended and the open
questions on the left, decisions and owner-tagged action items on the right.
Action items carry a heavier outline so they stand out when the map is
shared after the meeting.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 560.0, 180.0
PITCH = 46.0
GAP = 34.0

TOPICS = {
    "left": [
        ("Attendees", "#A7F3D0", ["Ana (PM)", "Raj (Tech Lead)", "Mei (Design)"]),
        ("Open Questions", "#FDE68A", ["Mobile scope in Q1?", "Who owns analytics?"]),
    ],
    "right": [
        ("Decisions", "#93C5FD", ["Ship SSO before billing", "Freeze API on Thursday"]),
        ("Action Items", "#FCA5A5", ["**Raj**: fix SSO redirect (Fri)", "**Mei**: billing mock-ups (Wed)", "**Ana**: update roadmap (Mon)"]),
    ],
}


def diagram() -> Diagram:
    with Diagram("Sprint 42 Planning Meeting Notes", theme="emerald") as diag:
        root = diag.shape(
            "**Sprint 42 Planning**\n14 Nov · 30 min", 210, 74,
            style=Style(radius=37, fill="#ECFDF5", stroke="#34D399", stroke_width=3, text_color="#064E3B", font_size=17),
        ).at(CX, CY, anchor="center")

        for side, topics in TOPICS.items():
            sign = -1 if side == "left" else 1
            inner = "right" if side == "left" else "left"
            total = sum(len(t[2]) * PITCH for t in topics) + GAP * (len(topics) - 1)
            top = CY - total / 2
            for label, colour, items in topics:
                block = len(items) * PITCH
                topic = diag.shape(
                    f"**{label}**", 150, 46,
                    style=Style(radius=23, fill=colour, stroke=colour, text_color="#022C22", font_size=15),
                ).at(CX + sign * 250, top + block / 2, anchor="center")
                diag.connect(root.anchor(side, 0.5), topic.anchor(inner, 0.5),
                             routing="curve", color=colour, width=3.5, head="none")
                is_action = label == "Action Items"
                for i, item in enumerate(items):
                    leaf = diag.shape(
                        item, 230, 34,
                        style=Style(radius=17, fill="#064E3B", stroke=colour,
                                    stroke_width=2.5 if is_action else 1.4, text_color="#ECFDF5", font_size=13),
                    ).at(CX + sign * 500, top + PITCH * (i + 0.5), anchor="center")
                    diag.connect(topic.anchor(side, 0.5), leaf.anchor(inner, 0.5),
                                 routing="curve", color=colour, width=1.8, head="none")
                top += block + GAP
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "04_meeting_notes_action_items")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
