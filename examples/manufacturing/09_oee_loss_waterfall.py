"""Overall equipment effectiveness (OEE) for one shift, as a loss waterfall.

Each bar is drawn to scale from the shift's numbers. Planned stops are taken
off the shift to give planned production time; downtime then gives run time
(availability); slow and small stops give net run time (performance); and
rejected parts give fully productive time (quality). OEE is the product of
the three ratios, which equals fully productive time over planned production
time. The bars and the numbers in the formulas are computed from the same
inputs, so they always agree.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

# One eight-hour shift.
SHIFT, PLANNED_STOPS, DOWNTIME = 480.0, 60.0, 47.0  # minutes
IDEAL_CYCLE, TOTAL, GOOD = 1.0, 19271, 18848  # seconds per part, parts made, good parts

X0, Y0, SCALE = 260.0, 110.0, 1.5  # left of the bars, top of the first bar, px per minute
BAR, PITCH = 34.0, 58.0
VALUE = Style(fill="#9DB8DA", stroke_width=0.8)
LOSS = Style(fill="#F1D3D3", stroke="#A33A3A", stroke_width=0.8, dash="3,2")
STOP = Style(fill="#E2E2E2", stroke="#777777", stroke_width=0.8, dash="3,2")
AXIS = Style(fill="none", stroke_width=0.9)


def diagram() -> Diagram:
    planned = SHIFT - PLANNED_STOPS
    run = planned - DOWNTIME
    net = IDEAL_CYCLE * TOTAL / 60.0
    productive = IDEAL_CYCLE * GOOD / 60.0
    a, p, q = run / planned, net / run, GOOD / TOTAL
    rows = [
        ("Shift length", SHIFT, None, ""),
        ("Planned production time", planned, STOP, f"planned stops {PLANNED_STOPS:g} min"),
        ("Run time", run, LOSS, f"availability loss {DOWNTIME:g} min"),
        ("Net run time", net, LOSS, f"performance loss {run - net:.1f} min"),
        ("Fully productive time", productive, LOSS, f"quality loss {net - productive:.1f} min"),
    ]

    with Diagram("OEE Loss Waterfall for One Shift", theme="paper") as diag:

        def rect(x0: float, x1: float, y: float, style: Style) -> None:
            diag.polygon([(x0, y), (x1, y), (x1, y + BAR), (x0, y + BAR)], style=style)

        previous = SHIFT
        for k, (name, minutes, loss_style, loss_text) in enumerate(rows):
            y = Y0 + k * PITCH
            end = X0 + minutes * SCALE
            rect(X0, end, y, VALUE)
            diag.text(f"{minutes:.1f} min" if minutes % 1 else f"{minutes:g} min", size=12).at(
                end - 8, y + BAR / 2, anchor="right_center")
            if loss_style is not None:
                rect(end, X0 + previous * SCALE, y, loss_style)
                diag.text(loss_text, size=12, italic=True, color="#7A2A2A").at(
                    X0 + SHIFT * SCALE + 16, y + BAR / 2, anchor="left_center")
            diag.text(f"**{name}**", size=13).at(X0 - 14, y + BAR / 2, anchor="right_center")
            previous = minutes

        # Time axis under the bars.
        axis_y = Y0 + len(rows) * PITCH - 6
        ticks = " ".join(f"M {X0 + m * SCALE} {axis_y} v 5" for m in range(0, int(SHIFT) + 1, 60))
        diag.path(f"M {X0} {axis_y} H {X0 + SHIFT * SCALE} {ticks}", style=AXIS)
        for m in range(0, int(SHIFT) + 1, 60):
            diag.text(str(m), size=11, color="#444444").at(X0 + m * SCALE, axis_y + 8, anchor="top_center")
        diag.text("minutes", size=11, italic=True).at(X0 + SHIFT * SCALE + 16, axis_y + 8, anchor="top_left")

        # The three ratios and their product.
        eq_y = axis_y + 50
        lines = [
            f"$A = t_{{\\mathrm{{run}}}} / t_{{\\mathrm{{plan}}}} = {run:g} / {planned:g} = {a:.3f}$",
            f"$P = (t_{{\\mathrm{{ideal}}}} \\cdot n_{{\\mathrm{{total}}}}) / t_{{\\mathrm{{run}}}}"
            f" = {net:.1f} / {run:g} = {p:.3f}$",
            f"$Q = n_{{\\mathrm{{good}}}} / n_{{\\mathrm{{total}}}} = {GOOD} / {TOTAL} = {q:.3f}$",
        ]
        for k, line in enumerate(lines):
            diag.text(line, size=15).at(X0, eq_y + k * 32, anchor="top_left")
        terms = [
            "$t_{\\mathrm{plan}}$  planned production time",
            "$t_{\\mathrm{run}}$  run time",
            "$t_{\\mathrm{ideal}}$  ideal cycle time per part",
            "$n_{\\mathrm{total}}, n_{\\mathrm{good}}$  parts made, good parts",
        ]
        diag.text("**Where**\n" + "\n".join(terms), size=12, line_height=1.5).at(
            X0 + 460, eq_y, anchor="top_left")
        diag.text(
            f"$\\mathrm{{OEE}} = A \\times P \\times Q = {a:.3f} \\times {p:.3f} \\times {q:.3f} = {a * p * q:.3f}$",
            size=17,
        ).at(X0, eq_y + 3 * 32 + 12, anchor="top_left")
        diag.text(
            f"Check: fully productive / planned = {productive:.1f} / {planned:g} = {productive / planned:.3f}. "
            f"Ideal cycle time {IDEAL_CYCLE:g} s per part.",
            size=12, font="serif", italic=True,
        ).at(X0, eq_y + 4 * 32 + 30, anchor="top_left")

        diag.caption("**Figure 9:** OEE as availability, performance and quality losses over one shift",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "09_oee_loss_waterfall")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/manufacturing")
    build_diagram(dest)
