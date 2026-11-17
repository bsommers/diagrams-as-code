"""Run-to-run (R2R) process control with fault detection, as a block diagram.

The process tool is modelled as a linear gain $b$ on the recipe input plus an
offset $a_k$ that drifts as the chamber ages. After each run, metrology
measures the output $y_k$; an EWMA estimator updates the offset, and the
controller picks the next recipe so the predicted output hits the target $T$.
In parallel, fault detection and classification (FDC) watches the tool's trace
data during the run and, on a fault, holds the tool and stops the estimator
learning from a bad run.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

AXIS = 220.0  # y of the forward path
FEEDBACK = 370.0  # y of the feedback path
BLOCK = Style(fill="#ECECEF", font_size=13)
FAULT = Style(fill="#F4E4E4", font_size=13)
SIGNAL = {"size": 13, "padding": 2}
LINE = {"width": 1.2}


def diagram() -> Diagram:
    with Diagram("Run-to-Run Control with Fault Detection", theme="paper") as diag:

        def block(label: str, x: float, y: float, w: float = 210, style: Style = BLOCK):
            return diag.shape(label, w, 70, style=style).at(x, y, anchor="center")

        def signal(body: str, x: float, y: float, anchor: str = "bottom_center"):
            return diag.text(body, **SIGNAL).at(x, y, anchor=anchor)

        controller = block("**R2R controller**\n$u_{k+1} = (T - a_k) / b$", 220, AXIS)
        tool = block("**Process tool**\n$y_k = b\\,u_k + a_k + \\varepsilon_k$", 540, AXIS)
        metrology = block("**Metrology**\nthickness, CD or overlay", 860, AXIS)
        estimator = block(
            "**EWMA estimator**\n$a_k = \\lambda (y_k - b\\,u_k) + (1 - \\lambda)\\, a_{k-1}$", 540, FEEDBACK, w=340)
        fdc = block("**FDC model**\n$T^2 = (x - \\mu)' S^{-1} (x - \\mu) \\leq T^2_{\\mathrm{lim}}$",
                    800, 70, w=330, style=FAULT)

        # Forward path: target in, recipe to the tool, wafer to metrology.
        diag.connect((40, AXIS), controller.anchor("left", 0.5), routing="direct", **LINE)
        controller >> diag.edge(**LINE) >> tool
        tool >> diag.edge(**LINE) >> metrology
        signal("$T$", 75, AXIS - 8)
        signal("$u_{k+1}$", 380, AXIS - 8)
        signal("wafer", 700, AXIS - 8)

        # Feedback: measured output to the estimator, offset back to the controller.
        right, left = 860.0, 220.0
        diag.connect(metrology.anchor("bottom", 0.5), estimator.anchor("right", 0.5),
                     via=[(right, FEEDBACK)], **LINE)
        diag.connect(estimator.anchor("left", 0.5), controller.anchor("bottom", 0.5),
                     via=[(left, FEEDBACK)], **LINE)
        signal("$y_k$", right + 8, (AXIS + 35 + FEEDBACK) / 2, "left_center")
        signal("$a_k$", left - 8, (AXIS + 35 + FEEDBACK) / 2, "right_center")

        # Drift enters the tool from above; trace data leaves it for FDC.
        drift_x = 500.0
        diag.connect((drift_x, AXIS - 95), tool.anchor("top", (drift_x - 435) / 210), routing="direct", **LINE)
        signal("$d_k$: chamber drift, PM", drift_x - 6, AXIS - 92, "bottom_right")
        trace_x = 600.0
        diag.connect(tool.anchor("top", (trace_x - 435) / 210), fdc.anchor("left", 0.5),
                     via=[(trace_x, 70)], **LINE)
        signal("trace $x(t)$", trace_x + 8, AXIS - 60, "left_center")

        # A fault holds the tool and freezes the estimate.
        diag.connect(fdc.anchor("right", 0.5), estimator.anchor("right", 0.25),
                     via=[(1010, 70), (1010, FEEDBACK - 17.5)], style="dashed", **LINE)
        diag.text("fault: hold tool,\nskip $a_k$ update", size=12, italic=True).at(
            1022, (70 + FEEDBACK) / 2, anchor="left_center")

        diag.text(
            "$0 < \\lambda \\leq 1$: a larger $\\lambda$ follows drift faster but passes more "
            "metrology noise into the recipe.",
            size=12, font="serif", italic=True,
        ).at(220, FEEDBACK + 70, anchor="top_left")
        diag.caption(
            "**Figure 4:** EWMA run-to-run control of a process tool, with FDC interdiction",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "04_apc_run_to_run_fdc")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/manufacturing")
    build_diagram(dest)
