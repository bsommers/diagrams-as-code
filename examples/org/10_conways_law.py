"""Example: Conway's law (ORGANISATION domain).

"Any organisation that designs a system will produce a design whose structure is a
copy of the organisation's communication structure." Top panel: teams split by
technical layer produce a layered system in which every feature crosses every team.
Bottom panel: the inverse Conway manoeuvre, where teams are aligned to business
capabilities first and the architecture follows.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port, Style
from diagrams_as_code.output import render_all

TEAM = Style(fill="#D9E3F5", stroke="#2F4B86")
SERVICE = Style(fill="#E4F1E8", stroke="#3C8D53")
COMM = "#B8860B"
W, H = 190.0, 56.0
XS = (80.0, 400.0, 720.0)  # column spacing leaves room for edge labels
X_LABEL = 1010.0


def panel(diag: Diagram, y: float, title: str, teams: tuple[str, ...], services: tuple[str, ...],
          links: tuple[tuple[int, int], ...], note: str) -> None:
    diag.text(f"**{title}**", size=15).at(XS[0], y - 40)
    team_shapes = [diag.shape(t, W, H, style=TEAM).at(x, y) for t, x in zip(teams, XS)]
    service_shapes = [diag.shape(s, W, H, style=SERVICE).at(x, y + 130) for s, x in zip(services, XS)]
    for k, (t, s) in enumerate(zip(team_shapes, service_shapes)):
        t >> diag.edge("owns" if k == 0 else "", arrow_head=False) >> s
    for a, b in links:
        team_shapes[a] >> diag.edge("handoffs" if (a, b) == links[0] else "", style="dashed", color=COMM,
                                    two_way=True, source_port=Port.EAST, target_port=Port.WEST) >> team_shapes[b]
        service_shapes[a] >> diag.edge("calls" if (a, b) == links[0] else "",
                                       source_port=Port.EAST, target_port=Port.WEST) >> service_shapes[b]
    diag.text(note, size=12, max_width=250).at(X_LABEL - 60, y + 4)


def diagram() -> Diagram:
    with Diagram("Conway's law", theme="paper") as diag:
        panel(diag, 100.0, "Teams by technical layer: the system mirrors the split",
              ("UI team", "API team", "Database team"),
              ("Web UI", "API tier", "Database tier"),
              ((0, 1), (1, 2)),
              "Every feature needs a ticket in all three queues, so every release crosses two handoffs.")
        panel(diag, 400.0, "Inverse Conway manoeuvre: shape the teams, get the design",
              ("Catalogue team", "Checkout team", "Payments team"),
              ("Catalogue service", "Checkout service", "Payments service"),
              ((1, 2),),
              "Each team ships its own slice; the one dependency is a deliberate, versioned interface.")
        diag.text("Dashed amber: team communication.  Solid arrow: service call.  Plain vertical line: ownership.", size=12).at(XS[0], 600)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "10_conways_law")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
