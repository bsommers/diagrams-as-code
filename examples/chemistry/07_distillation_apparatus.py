"""Simple distillation apparatus, drawn from lines, arcs and tube outlines.

The glassware is plain geometry: a round-bottom flask is a circle with a neck
(one arc path), tubes are a dark line with a white line on top, and the Liebig
condenser is a slanted tube inside a pale-blue water jacket. The condenser axis
runs from the still head, down a slope of 0.34, to the receiver; the jacket
ends are placed along that axis, so the geometry stays consistent when the
numbers change. Cold water enters the jacket at its low end and leaves at its
high end so the jacket stays full.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK, WATER, GLASS, LIQUID = "#1F2F57", "#CFE0F2", "#FFFFFF", "#F2E3B8"
RED, BLUE = "#9C2F2F", "#2F5FA8"
HEAD_X, JUNCTION_Y = 200.0, 228.0       # still head axis and side-arm height
SLOPE = 0.34                            # condenser drop per px of run
END_X = 640.0                           # where the condenser tube ends
BENCH_Y = 560.0


def on_axis(x: float) -> tuple[float, float]:
    return (x, JUNCTION_Y + SLOPE * (x - HEAD_X))


def flask_path(cx: float, cy: float, r: float, neck_top: float, half: float = 15.0) -> str:
    """Round-bottom flask outline: neck lines joined by the large arc of the circle."""
    y = cy - math.sqrt(r * r - half * half)
    return (f"M {cx - half:.2f} {neck_top:.2f} L {cx - half:.2f} {y:.2f} "
            f"A {r} {r} 0 1 0 {cx + half:.2f} {y:.2f} L {cx + half:.2f} {neck_top:.2f}")


def liquid_path(cx: float, cy: float, r: float, level: float) -> str:
    half = math.sqrt(r * r - (level - cy) ** 2)
    return (f"M {cx - half:.2f} {level:.2f} L {cx + half:.2f} {level:.2f} "
            f"A {r} {r} 0 0 1 {cx - half:.2f} {level:.2f} Z")


def circle(diag, x, y, r, fill, stroke=INK, width=1.0, z=3):
    diag.polygon([(x + r * math.cos(k * math.pi / 12), y + r * math.sin(k * math.pi / 12)) for k in range(24)],
                 style=Style(fill=fill, stroke=stroke, stroke_width=width), z=z)


def diagram() -> Diagram:
    ux, uy = 1 / math.hypot(1, SLOPE), SLOPE / math.hypot(1, SLOPE)
    with Diagram("Simple distillation apparatus", theme="paper") as diag:
        k = Draft(diag, ink=INK, size=13)
        solid = lambda w, c=INK, fill="none": Style(fill=fill, stroke=c, stroke_width=w)

        # Bench, lab jack and heater.
        diag.polyline([(40, BENCH_Y), (820, BENCH_Y)], style=solid(2.4))
        diag.polygon([(130, 468), (270, 468), (270, BENCH_Y), (130, BENCH_Y)], style=solid(1.4, fill="#E6E6E6"), z=0)
        diag.polygon([(120, 432), (280, 432), (280, 468), (120, 468)], style=solid(1.8, fill="#BDBDBD"), z=1)
        diag.text("heater", size=12).at(200, 450, anchor="center")

        # Retort stand and clamp holding the boiling flask by its neck.
        diag.polyline([(60, 270), (60, BENCH_Y)], style=solid(7, "#555555"))
        diag.polyline([(60, 270), (60, BENCH_Y)], style=solid(4.6, "#C9C9C9"))
        diag.polygon([(40, BENCH_Y), (110, BENCH_Y), (110, BENCH_Y - 8), (40, BENCH_Y - 8)], style=solid(1.4, fill="#C9C9C9"))
        diag.polyline([(60, 283), (184, 283)], style=solid(5, "#555555"))
        diag.polygon([(184, 273), (216, 273), (216, 293), (184, 293)], style=solid(1.6, "#555555", "#D9D9D9"), z=3)

        # Boiling flask with liquid, stir-free boiling chips and bubbles.
        diag.path(liquid_path(200, 365, 62, 372), style=solid(0, LIQUID, LIQUID), z=0)
        diag.path(flask_path(200, 365, 62, 250), style=solid(2.0), z=2)
        for bx, by, br in ((180, 400, 3), (205, 410, 3.5), (222, 395, 2.5), (192, 385, 2.5), (215, 380, 3)):
            circle(diag, bx, by, br, "none", INK, 1.0, z=2)

        # Tubes: all dark layers first, then all white layers, so the joints read as one piece.
        a, b = on_axis(HEAD_X), (END_X, on_axis(END_X)[1])
        j0, j1 = on_axis(305), on_axis(590)             # water jacket extent
        tubes = [
            ([(HEAD_X, 252), (HEAD_X, 206)], 32, 28),               # still head
            ([a, (END_X + 15, on_axis(END_X + 15)[1])], 16, 12),    # side arm and condenser tube
            ([(END_X + 15, on_axis(END_X + 15)[1]), (END_X + 15, 438)], 16, 12),   # drop into receiver
        ]
        diag.polyline([(j0[0] - ux * 2, j0[1] - uy * 2), (j1[0] + ux * 2, j1[1] + uy * 2)], style=solid(46), z=1)
        diag.polyline([j0, j1], style=solid(42, WATER), z=1.5)
        for pts, w_out, _ in tubes:
            diag.polyline(pts, style=solid(w_out), z=2)
        for pts, _, w_in in tubes:
            diag.polyline(pts, style=solid(w_in, GLASS), z=2.5)

        # Thermometer through a stopper, bulb level with the side arm.
        diag.polygon([(186, 200), (214, 200), (211, 214), (189, 214)], style=solid(1.2, "#555555", "#8C8C8C"), z=4)
        diag.polyline([(HEAD_X, 128), (HEAD_X, JUNCTION_Y + 4)], style=solid(7), z=3)
        diag.polyline([(HEAD_X, 128), (HEAD_X, JUNCTION_Y + 4)], style=solid(4.6, GLASS), z=3.5)
        diag.polyline([(HEAD_X, JUNCTION_Y + 4), (HEAD_X, 178)], style=solid(2.2, RED), z=4)
        circle(diag, HEAD_X, JUNCTION_Y + 5, 5.5, RED, INK, 1.0, z=4)

        # Receiving flask with distillate and a drip from the tube.
        rx, ry = END_X + 15, 512
        diag.path(liquid_path(rx, ry, 48, 524), style=solid(0, LIQUID, LIQUID), z=0)
        diag.path(flask_path(rx, ry, 48, 420), style=solid(2.0), z=2)
        circle(diag, rx, 456, 2.6, LIQUID, INK, 1.0, z=4)
        circle(diag, rx, 478, 2.6, LIQUID, INK, 1.0, z=4)

        # Flow arrows: vapour (red) and cooling water (blue), drawn as filled heads on top of the glass.
        def arrow(p, q, color, head=9.0):
            dx, dy = q[0] - p[0], q[1] - p[1]
            n = math.hypot(dx, dy)
            vx, vy = dx / n, dy / n
            base = (q[0] - vx * head, q[1] - vy * head)
            diag.polyline([p, base], style=solid(2.0, color), z=5)
            diag.polygon([q, (base[0] - vy * head * 0.4, base[1] + vx * head * 0.4),
                          (base[0] + vy * head * 0.4, base[1] - vx * head * 0.4)],
                         style=Style(fill=color, stroke=color, stroke_width=0.5), z=5)
        arrow((HEAD_X, 300), (HEAD_X, 266), RED)
        sx = on_axis(250)
        arrow((sx[0] - 20, sx[1] - 20 * SLOPE), (sx[0] + 22, sx[1] + 22 * SLOPE), RED)
        wx = on_axis(600)[0] - 8
        arrow((wx, 420), (wx, 382), BLUE)
        ox = on_axis(318)[0] + 6
        arrow((ox, 246), (ox, 208), BLUE)

        # Labels with leaders.
        k.leader((HEAD_X, 140), (260, 96), "thermometer: bulb level with the side arm", anchor="left_center")
        k.leader((186, 238), (150, 205), "still head", anchor="right_center")
        k.leader((240, 395), (292, 395), "round-bottom flask,\nliquid and boiling chips", anchor="left_center")
        k.leader((200, 500), (305, 505), "heater on a lab jack", anchor="left_center")
        k.leader(on_axis(440), (400, 168), "Liebig condenser (water jacket)", anchor="left_center")
        diag.text("water out\n(top)", size=12, color=BLUE).at(ox, 196, anchor="bottom_center")
        diag.text("cold water in\n(bottom)", size=12, color=BLUE).at(wx, 426, anchor="top_center")
        k.leader((rx + 46, 520), (745, 470), "receiving flask: distillate", anchor="left_center")
        diag.text("vapour", size=12, color=RED).at(sx[0] + 8, sx[1] - 26, anchor="bottom_center")

        diag.text(
            "**How it works**\n"
            "The mixture is heated to its boiling point. The more\n"
            "volatile component evaporates first, passes through the\n"
            "side arm, condenses in the cooled tube and drips into\n"
            "the receiver. The thermometer reads the vapour\n"
            "temperature, which holds steady while one\n"
            "component distils.",
            size=13,
        ).at(690, 110, anchor="top_left")
        diag.text(
            "**Good practice**\n"
            "Water in at the low end, so the jacket stays full.\n"
            "Never heat a closed system: vent the receiver.\n"
            "Simple distillation needs boiling points about\n"
            "25 K apart or more; otherwise use a\n"
            "fractionating column.",
            size=13,
        ).at(690, 260, anchor="top_left")
        diag.caption("**Figure 7:** Simple distillation apparatus: boiling flask, still head with thermometer, Liebig condenser and receiver",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "07_distillation_apparatus")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
