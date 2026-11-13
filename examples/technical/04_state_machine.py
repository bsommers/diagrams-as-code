"""A finite state machine: the lifecycle of a client connection.

Six states from *Idle* to the final *Closed*, with a retry loop through
*Backoff* guarded by the attempt counter $n$, and a self-loop on *Established*
for data transfer. Transitions read *event* [guard] / action.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

W, H = 140.0, 50.0
STATE = Style(radius=H / 2, font_size=14)
FINAL = Style(radius=H / 2, font_size=14, double=4)
LINE = {"width": 1.2}
LABEL = {"size": 12, "padding": 2}


def diagram() -> Diagram:
    with Diagram("Connection state machine", theme="paper") as diag:

        def state(name: str, x: float, y: float, style: Style = STATE):
            return diag.shape(name, W, H, style=style).at(x, y, anchor="center")

        def label(body: str, x: float, y: float, anchor: str = "bottom_center", align: str = "center"):
            return diag.text(body, align=align, **LABEL).at(x, y, anchor=anchor)

        start = diag.shape("", 14, 14, style=Style(fill="#000000", radius=7)).at(40, 220, anchor="center")
        idle = state("Idle", 150, 220)
        connecting = state("Connecting", 410, 220)
        established = state("Established", 700, 220)
        backoff = state("Backoff", 410, 70)
        closing = state("Closing", 700, 400)
        closed = state("Closed", 410, 400, FINAL)

        start >> diag.edge(**LINE) >> idle.anchor("left", 0.5)
        idle.anchor("right", 0.5) >> diag.edge(**LINE) >> connecting.anchor("left", 0.5)
        connecting.anchor("right", 0.5) >> diag.edge(**LINE) >> established.anchor("left", 0.5)
        established.anchor("bottom", 0.5) >> diag.edge(**LINE) >> closing.anchor("top", 0.5)
        closing.anchor("left", 0.5) >> diag.edge(**LINE) >> closed.anchor("right", 0.5)
        connecting.anchor("bottom", 0.5) >> diag.edge(**LINE) >> closed.anchor("top", 0.5)

        # The retry loop: up on the left, back down on the right.
        connecting.anchor("top", 0.3) >> diag.edge(**LINE) >> backoff.anchor("bottom", 0.3)
        backoff.anchor("bottom", 0.7) >> diag.edge(**LINE) >> connecting.anchor("top", 0.7)

        # Self-loop: a curve leaving and re-entering the top of the state.
        diag.connect(
            established.anchor("top", 0.3), established.anchor("top", 0.7), routing="spline",
            via=[(660, 150), (700, 132), (740, 150)], **LINE,
        )

        label("*open* / send SYN", 270, 214)
        label("*SYN+ACK* / send ACK", 555, 214)
        label("*data* $[w > 0]$ / send", 700, 124)
        label("*timeout*\n$[n < n_{\\max}]$", 372, 145, "right_center", "right")
        label("*after* $2^{n} t_0$\n/ $n := n + 1$", 448, 145, "left_center", "left")
        label("*timeout*\n$[n \\geq n_{\\max}]$", 420, 310, "left_center", "left")
        label("*close* / send FIN", 710, 310, "left_center", "left")
        label("*ACK* $\\lor\\; [t > 2\\,\\mathrm{MSL}]$", 555, 394)

        diag.text(
            "Transitions read\n*event* [guard] / action;\n$n$ counts connection attempts,\n$w$ is the send window.",
            size=12, font="serif",
        ).at(80, 365)
        diag.caption(
            "**Figure 4:** Connection lifecycle with bounded retries; a double border marks the final state",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "04_state_machine")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
