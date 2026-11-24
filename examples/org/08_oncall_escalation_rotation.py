"""Example: On-call escalation ladder with weekly rotation (ORGANISATION domain).

The standing policy rather than one incident: who is paged, in what order and after
how long without acknowledgement (left), and who holds each tier in each week of a
four-week rotation (right). The secondary this week becomes the primary next week,
so every engineer shadows before they lead.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port, Style
from diagrams_as_code.output import render_all

ENGINEERS = ("Ana", "Ben", "Chi", "Dev")
MANAGERS = ("Mia", "Noor")
TIERS = (
    ("L1 Primary on-call", "acknowledge within 5 min", Style(fill="#D9E3F5", stroke="#2F4B86")),
    ("L2 Secondary on-call", "joins if no ack in 5 min", Style(fill="#E4F1E8", stroke="#3C8D53")),
    ("L3 Engineering manager", "paged if no ack in 10 min", Style(fill="#FBF0C8", stroke="#B8860B")),
    ("L4 Director of engineering", "paged if no ack in 15 min", Style(fill="#F6D9CC", stroke="#B0502E")),
)
#: who holds tier t in week w.
def holder(tier: int, week: int) -> str:
    if tier == 0:
        return ENGINEERS[week % 4]
    if tier == 1:
        return ENGINEERS[(week + 1) % 4]
    if tier == 2:
        return MANAGERS[week % 2]
    return "Oscar"


TIER_W, TIER_H, ROW_GAP = 250.0, 64.0, 66.0
LABEL_W, CELL_W, CELL_GAP = 120.0, 92.0, 10.0
X0, Y0 = 60.0, 110.0
LINK = 90.0  # gap between ladder and table, carries the "staffed by" label
TX = X0 + TIER_W + LINK


def diagram() -> Diagram:
    with Diagram("On-call escalation ladder with rotation", theme="paper") as diag:
        tiers = []
        for t, (name, rule, style) in enumerate(TIERS):
            y = Y0 + t * (TIER_H + ROW_GAP)
            tiers.append(diag.shape(f"{name}\n{rule}", TIER_W, TIER_H, style=style).at(X0, y))
            diag.shape(name.split(" ", 1)[1].split(" on-call")[0].replace("Engineering manager", "Manager"),
                       LABEL_W, TIER_H, style=Style(fill="#F4F6F9", stroke="#6B7280")).at(TX, y)
            for w in range(4):
                diag.shape(holder(t, w), CELL_W, TIER_H, style=style).at(
                    TX + LABEL_W + CELL_GAP + w * (CELL_W + CELL_GAP), y)
        for upper, lower, wait in zip(tiers, tiers[1:], ("no ack, 5 min", "no ack, 10 min", "no ack, 15 min")):
            upper >> diag.edge(wait, source_port=Port.SOUTH, target_port=Port.NORTH) >> lower
        for w in range(4):
            diag.shape(f"Week {w + 1}", CELL_W, 36, style=Style(fill="#2F4B86", stroke="#2F4B86", text_color="#FFFFFF")).at(
                TX + LABEL_W + CELL_GAP + w * (CELL_W + CELL_GAP), Y0 - 52)
        diag.text("**Ladder**", size=15).at(X0, Y0 - 84)
        diag.text("**Four-week rotation**", size=15).at(TX, Y0 - 84)
        diag.text("Handover Monday 10:00. The secondary this week is the primary next week.",
                  size=12).at(X0, Y0 + 4 * TIER_H + 3 * ROW_GAP + 28)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "08_oncall_escalation_rotation")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
