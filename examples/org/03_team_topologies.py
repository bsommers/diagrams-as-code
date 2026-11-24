"""Example: Team Topologies (ORGANISATION domain).

The four fundamental team types (stream-aligned, enabling, complicated-subsystem,
platform) joined by the three interaction modes: collaboration, X-as-a-Service and
facilitating. Stream-aligned teams own a flow of change; the others exist to reduce
their cognitive load.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

STREAM = Style(fill="#D9E3F5", stroke="#2F4B86")
PLATFORM = Style(fill="#E4F1E8", stroke="#3C8D53")
ENABLING = Style(fill="#FBF0C8", stroke="#B8860B")
SUBSYSTEM = Style(fill="#F6D9CC", stroke="#B0502E")
COLLAB, XAAS, FACIL = "#B0502E", "#2F4B86", "#8A6D00"
W, H = 170.0, 74.0
Y_STREAMS = 150.0


def diagram() -> Diagram:
    with Diagram("Team Topologies", theme="paper") as diag:
        enabling = diag.shape("Security Enablement\nenabling team", W, H, style=ENABLING).at(60, Y_STREAMS)
        xs = (400.0, 610.0, 820.0)
        streams = [
            diag.shape(f"{name}\nstream-aligned team", W, H, style=STREAM).at(x, Y_STREAMS)
            for name, x in zip(("Checkout", "Catalogue", "Recommendations"), xs)
        ]
        subsystem = diag.shape("Fraud Scoring Engine\ncomplicated-subsystem team", W + 20, H, style=SUBSYSTEM).at(1110, Y_STREAMS)
        platform_x, platform_w = xs[0], xs[-1] + W - xs[0]
        platform = diag.shape("Internal Developer Platform\nplatform team: CI/CD, runtime, observability",
                              platform_w, H, style=PLATFORM).at(platform_x, Y_STREAMS + 210)

        enabling >> diag.edge("facilitating", style="dotted", color=FACIL, width=2.2,
                              source_port=Port.EAST, target_port=Port.WEST) >> streams[0]
        streams[2] >> diag.edge("collaboration", color=COLLAB, width=3.0, two_way=True,
                                source_port=Port.EAST, target_port=Port.WEST) >> subsystem
        for s, x in zip(streams, xs):
            frac = (x + W / 2 - platform_x) / platform_w
            s.anchor("bottom", 0.5) >> diag.edge("X-as-a-Service" if x == xs[1] else "", style="dashed", color=XAAS,
                                                  width=1.8) >> platform.anchor("top", frac)

        p = Plot(diag, x=(0, 1), y=(0, 1))  # only for its legend key
        p.legend([("Collaboration: work together for a time-boxed discovery", COLLAB, ""),
                  ("X-as-a-Service: consume with minimal collaboration", XAAS, "5,4"),
                  ("Facilitating: one team coaches another, then steps back", FACIL, "2,2")],
                 at=(400, 468), size=12)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "03_team_topologies")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
