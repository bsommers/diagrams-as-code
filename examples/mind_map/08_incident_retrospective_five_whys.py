"""Mind map: Incident Retrospective with Five Whys (MIND_MAP domain, Advanced).

A blameless post-incident review. The incident sits at the centre; the left
half gathers the timeline, contributing factors and owner-tagged action items,
and the right half drills down a five-whys chain, with arrows pointing from
each symptom to its cause, until it reaches the double-bordered root cause.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX, CY = 640.0, 300.0
PITCH = 46.0
GAP = 30.0
WHY_COLOUR = "#FCA5A5"

LEFT = [
    ("Timeline", "#FDBA74", ["14:02 config deploy", "14:05 error-rate alert", "14:44 rollback complete"]),
    ("Contributing\nFactors", "#FDE68A", ["No canary for config", "Alert routed to email", "Runbook out of date"]),
    ("Action Items", "#A5B4FC", ["**SRE**: canary all configs", "**Platform**: pool-size lint", "**On-call**: page on 5xx > 2%"]),
]
WHYS = [
    "Checkout API returned 503s",
    "DB connection pool exhausted",
    "Pool size set to 5, not 50",
    "Config value typed in seconds",
    "Schema has no units or bounds",
]


def diagram() -> Diagram:
    with Diagram("Checkout Outage Incident Retrospective", theme="crimson") as diag:
        root = diag.shape(
            "**INC-2047**\nCheckout Outage\n42 min · SEV-1", 190, 92,
            style=Style(radius=34, fill="#FFF1F2", stroke="#F43F5E", stroke_width=3, text_color="#4C0519", font_size=16),
        ).at(CX, CY, anchor="center")

        # Left half: balanced blocks of sub-topics.
        total = sum(len(b[2]) * PITCH for b in LEFT) + GAP * (len(LEFT) - 1)
        top = CY - total / 2
        for label, colour, items in LEFT:
            block = len(items) * PITCH
            heading = "**" + label.replace("\n", "**\n**") + "**"
            branch = diag.shape(
                heading, 140, 52,
                style=Style(radius=26, fill=colour, stroke=colour, text_color="#450A0A", font_size=15),
            ).at(CX - 250, top + block / 2, anchor="center")
            diag.connect(root.anchor("left", 0.5), branch.anchor("right", 0.5),
                         routing="curve", color=colour, width=3.5, head="none")
            for i, item in enumerate(items):
                leaf = diag.shape(
                    item, 220, 34,
                    style=Style(radius=17, fill="#450A0A", stroke=colour, stroke_width=1.5, text_color="#FFF1F2", font_size=13),
                ).at(CX - 500, top + PITCH * (i + 0.5), anchor="center")
                diag.connect(branch.anchor("left", 0.5), leaf.anchor("right", 0.5),
                             routing="curve", color=colour, width=1.8, head="none")
            top += block + GAP

        # Right half: the five-whys chain, read top to bottom.
        whys_branch = diag.shape(
            "**5 Whys**", 120, 46,
            style=Style(radius=23, fill=WHY_COLOUR, stroke=WHY_COLOUR, text_color="#450A0A", font_size=15),
        ).at(CX + 240, CY, anchor="center")
        diag.connect(root.anchor("right", 0.5), whys_branch.anchor("left", 0.5),
                     routing="curve", color=WHY_COLOUR, width=3.5, head="none")
        step = 92.0
        nodes = []
        labels = [f"**Why {i + 1}** · {why}" for i, why in enumerate(WHYS)]
        labels.append("**Root cause:** config schema\naccepts unvalidated values")
        for i, label in enumerate(labels):
            last = i == len(WHYS)
            nodes.append(diag.shape(
                label, 290, 54 if last else 38,
                style=Style(radius=19, fill="#7F1D1D" if last else "#450A0A", stroke=WHY_COLOUR,
                            stroke_width=2.2 if last else 1.5, double=4 if last else None,
                            text_color="#FFF1F2", font_size=13),
            ).at(CX + 530, CY + (i - 2.5) * step, anchor="center"))
        diag.connect(whys_branch.anchor("right", 0.5), nodes[0].anchor("left", 0.5),
                     routing="curve", color=WHY_COLOUR, width=1.8, head="none")
        for upper, lower in zip(nodes, nodes[1:]):
            upper.anchor("bottom", 0.5) >> diag.edge(color=WHY_COLOUR, routing="direct", width=1.6) >> lower.anchor("top", 0.5)
    return diag


def build_diagram(output_dir: Path | str = "output/mind_map") -> Path:
    return render_all(diagram(), output_dir, "08_incident_retrospective_five_whys")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/mind_map")
    build_diagram(dest)
