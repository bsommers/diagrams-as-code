"""Fractional anchors, point endpoints, a shared trunk, leaders and splines (PRIM-06)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Anchors, leaders and splines", theme="paper") as diag:
        mux = diag.shape("Multiplexer", 120, 160).at(260, 60)
        inputs = [diag.shape(f"in {i}", 70, 30).at(60, 65 + i * 40) for i in range(4)]
        for i, source in enumerate(inputs):
            # Each input lands a fixed fraction of the way down the left side.
            source >> diag.edge(width=1.0) >> mux.anchor("left", (i + 0.5) / 4)
        out = diag.shape("out", 70, 30).at(470, 125)
        mux.anchor("right", 0.5) >> diag.edge(width=2.5) >> out

        # One trunk leaving the output, splitting to three sinks.
        sinks = [diag.shape(f"sink {i}", 80, 30).at(390 + i * 110, 260) for i in range(3)]
        diag.fan_out(out.anchor("bottom", 0.5), [s.anchor("top", 0.5) for s in sinks], trunk=40, width=1.0)

        # A line from a bare point, a free curve through given points, and leaders.
        diag.connect((60, 300), mux.anchor("bottom", 0.25), routing="direct", width=1.0, style="dashed")
        diag.connect(
            inputs[0].anchor("top", 0.5), out.anchor("top", 0.5), routing="spline",
            via=[(180, 20), (420, 30)], width=1.0, head="open",
        )
        diag.leader("select lines enter\nat the bottom edge", mux.anchor("bottom", 0.75), at=(150, 330), head="circle")
        diag.leader("feedback path", (300, 22), at=(520, 40))
        diag.caption("**Figure 6:** Lines attached anywhere on a side, at points, and along a shared trunk", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "06_anchors_leaders_splines")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
