"""A feedback control loop as a block diagram.

The reference $r(t)$ is compared with the measured output at a summing
junction; the error drives a PI controller, a load disturbance enters at a
second junction ahead of the plant, and a sensor closes the loop.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

AXIS = 150.0  # y of the forward path
R = 15.0  # radius of a summing junction
BLOCK = Style(font_size=13)
SIGNAL = {"size": 13, "padding": 2}
LINE = {"width": 1.2}


def diagram() -> Diagram:
    with Diagram("Feedback control loop", theme="paper") as diag:

        def junction(x: float):
            # A box whose corner radius is half its side is a circle.
            return diag.shape("", 2 * R, 2 * R, style=Style(radius=R)).at(x, AXIS, anchor="center")

        def block(label: str, x: float, y: float = AXIS):
            return diag.shape(label, 150, 64, style=BLOCK).at(x, y, anchor="center")

        def signal(body: str, x: float, y: float = AXIS - 8, anchor: str = "bottom_center"):
            return diag.text(body, **SIGNAL).at(x, y, anchor=anchor)

        error = junction(150)
        controller = block("**Controller**\n$C(s) = K_p + K_i s^{-1}$", 300)
        load = junction(450)
        plant = block("**Plant**\n$G(s) = K / (\\tau s + 1)$", 600)
        sensor = block("**Sensor**\n$H(s) = 1 / (T_m s + 1)$", 450, AXIS + 130)
        tap = diag.point(730, AXIS, dot=True)

        # Forward path.
        diag.connect((50, AXIS), error.anchor("left", 0.5), routing="direct", **LINE)
        error.anchor("right", 0.5) >> diag.edge(**LINE) >> controller.anchor("left", 0.5)
        controller.anchor("right", 0.5) >> diag.edge(**LINE) >> load.anchor("left", 0.5)
        load.anchor("right", 0.5) >> diag.edge(**LINE) >> plant.anchor("left", 0.5)
        diag.connect(plant.anchor("right", 0.5), tap, routing="direct", arrow_head=False, **LINE)
        diag.connect(tap, (830, AXIS), routing="direct", **LINE)

        # Disturbance in from above; feedback back through the sensor.
        diag.connect((450, AXIS - 90), load.anchor("top", 0.5), routing="direct", **LINE)
        diag.connect(tap, sensor.anchor("right", 0.5), via=[(730, AXIS + 130)], **LINE)
        diag.connect(sensor.anchor("left", 0.5), error.anchor("bottom", 0.5), via=[(150, AXIS + 130)], **LINE)

        signal("$r(t)$", 85)
        signal("$e(t)$", 195)
        signal("$u(t)$", 400)
        signal("$y(t)$", 785)
        signal("$d(t)$", 460, AXIS - 78, "bottom_left")
        signal("$y_m(t)$", 260, AXIS + 122)

        # Signs of the summing junctions, beside the line they belong to.
        signal("+", 127, AXIS + 6, "top_right")
        signal("−", 142, AXIS + R + 4, "top_right")
        signal("+", 427, AXIS + 6, "top_right")
        signal("+", 442, AXIS - R - 4, "bottom_right")

        diag.caption(
            "**Figure 2:** Closed-loop control with a load disturbance; "
            "$e(t) = r(t) - y_m(t)$",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "02_control_loop")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
