"""An X-bar control chart with two rule violations, and the fishbone used to find the cause.

Twenty-seven subgroups of five bores each are plotted as the deviation of the
subgroup mean from the 25.000 mm nominal. The control limits are three sigma
of the mean, computed from the average range with the Shewhart constant
$A_2 = 0.577$ for $n = 5$; dashed lines mark the one- and two-sigma zones.
The script tests the data itself: subgroup 18 is beyond the upper limit, and
subgroups 20 to 27 are eight in a row above the centre line. Below the chart,
an Ishikawa (cause-and-effect) diagram lists the candidate causes of the
first signal under the six M's.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

# Subgroup mean minus nominal, in micrometres.
MEANS = [-2, 3, 1, -4, 2, 0, -3, 5, -1, 2, -6, 1, 3, -2, 0, 4, -3, 13, -2, 2, 4, 3, 5, 2, 6, 4, 3]
R_AVG, A2 = 20.0, 0.577  # average subgroup range (um) and the constant for n = 5
LIMIT = A2 * R_AVG  # three sigma of the subgroup mean
RUN = 8  # points in a row on one side of the centre line that signal a shift

X0, PITCH = 150.0, 28.0  # x of subgroup 1, and px between subgroups
TOP, SPAN, PX = 90.0, 16.0, 8.75  # top of the plot, +/- um shown, px per um
CL_Y = TOP + SPAN * PX
X_END = X0 + (len(MEANS) - 1) * PITCH + 30
LIMIT_LINE = Style(fill="none", stroke="#A33A3A", stroke_width=1.2)
CENTRE = Style(fill="none", stroke_width=1.0)
ZONE = Style(fill="none", stroke="#999999", stroke_width=0.7, dash="4,3")
DATA = Style(fill="none", stroke="#1F2F57", stroke_width=1.2)
BONE = Style(fill="none", stroke_width=1.1)
SPINE = Style(fill="none", stroke_width=2.0)
HEAD = Style(fill="#F1D3D3", font_size=13)

CAUSES = [
    ("Machine", ["spindle thermal growth", "boring-bar wear"]),
    ("Method", ["tool offset not updated", "feed rate changed"]),
    ("Material", ["new bar-stock lot", "hardness variation"]),
    ("Measurement", ["air-gauge drift", "master not re-zeroed"]),
    ("Man", ["new operator", "warm-up cycle skipped"]),
    ("Environment", ["coolant temperature", "shop ambient swing"]),
]


def y_of(um: float) -> float:
    return CL_Y - um * PX


def x_of(j: int) -> float:
    return X0 + j * PITCH


def diagram() -> Diagram:
    beyond = [j for j, m in enumerate(MEANS) if abs(m) > LIMIT]
    run_end = next(j for j in range(RUN - 1, len(MEANS))
                   if all(m > 0 for m in MEANS[j - RUN + 1:j + 1]))
    run_start = run_end - RUN + 1

    with Diagram("SPC X-bar Chart and Ishikawa Root-Cause Diagram", theme="paper") as diag:
        # Limits, centre line and sigma zones.
        for um, style, name in ((LIMIT, LIMIT_LINE, "UCL"), (-LIMIT, LIMIT_LINE, "LCL"), (0.0, CENTRE, "CL")):
            diag.polyline([(X0 - 20, y_of(um)), (X_END, y_of(um))], style=style)
            diag.text(f"{name} = {25 + um / 1000:.4f} mm", size=11).at(X_END + 8, y_of(um), anchor="left_center")
        for k in (1, 2):
            for sign in (1, -1):
                um = sign * k * LIMIT / 3
                diag.polyline([(X0 - 20, y_of(um)), (X_END, y_of(um))], style=ZONE)

        # Highlight the run before drawing the data over it.
        top_run = y_of(max(MEANS[run_start:run_end + 1])) - 12
        diag.polygon([(x_of(run_start) - 10, top_run), (x_of(run_end) + 10, top_run),
                      (x_of(run_end) + 10, CL_Y), (x_of(run_start) - 10, CL_Y)],
                     style=Style(fill="#F5E6C8", stroke="none"), z=-1)
        diag.text(f"rule 2: {RUN} in a row above CL", size=11, italic=True, color="#8A5A00").at(
            (x_of(run_start) + x_of(run_end)) / 2, top_run - 4, anchor="bottom_center")

        diag.polyline([(x_of(j), y_of(m)) for j, m in enumerate(MEANS)], style=DATA)
        for j, m in enumerate(MEANS):
            diag.point(x_of(j), y_of(m), dot=True, radius=3.0)
        for j in beyond:
            diag.path(f"M {x_of(j) - 8} {y_of(MEANS[j])} a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0",
                      style=Style(fill="none", stroke="#A33A3A", stroke_width=1.4))
            diag.text(f"rule 1: subgroup {j + 1} beyond UCL", size=11, italic=True, color="#A33A3A").at(
                x_of(j) - 14, y_of(MEANS[j]), anchor="right_center")

        # Axes.
        bottom = TOP + 2 * SPAN * PX
        ticks = " ".join(f"M {X0 - 20} {y_of(u)} h -5" for u in range(-15, 16, 5))
        ticks += " " + " ".join(f"M {x_of(j)} {bottom} v 5" for j in range(0, len(MEANS), 2))
        diag.path(f"M {X0 - 20} {TOP} V {bottom} H {X_END} {ticks}", style=CENTRE)
        for u in range(-15, 16, 5):
            diag.text(f"{u:+d}" if u else "0", size=11).at(X0 - 28, y_of(u), anchor="right_center")
        for j in range(0, len(MEANS), 2):
            diag.text(str(j + 1), size=11).at(x_of(j), bottom + 8, anchor="top_center")
        diag.text("subgroup $j$", size=12).at((X0 + X_END) / 2, bottom + 26, anchor="top_center")
        diag.text("$m_j - 25.000$ mm, in $\\mu$m", size=12).at(X0 - 20, TOP - 12, anchor="bottom_center")
        diag.text(
            f"$\\mathrm{{UCL}}, \\mathrm{{LCL}} = \\mu_0 \\pm A_2 R_{{\\mathrm{{avg}}}}$, "
            f"$A_2 = {A2}$, $R_{{\\mathrm{{avg}}}} = {R_AVG:g}\\,\\mu\\mathrm{{m}}$, $n = 5$",
            size=12,
        ).at(X_END, TOP - 12, anchor="bottom_right")

        # Ishikawa diagram for the rule 1 signal.
        spine_y = bottom + 210
        spine_l, spine_r = X0 + 20, X_END - 10
        diag.text(f"**Cause and effect: subgroup {beyond[0] + 1} beyond UCL**", size=13).at(
            X0 - 20, bottom + 62, anchor="top_left")
        head = diag.shape("**Bore diameter**\n**oversize**", 150, 56, style=HEAD).at(spine_r, spine_y, anchor="left_center")
        diag.connect((spine_l, spine_y), head.anchor("left", 0.5), routing="direct", width=2.0)
        reach, rise = 70.0, 110.0
        for k, (category, causes) in enumerate(CAUSES):
            above = k < 3
            bx = spine_l + 90 + (k % 3) * 210
            end_y = spine_y - rise if above else spine_y + rise
            diag.polyline([(bx, end_y), (bx + reach, spine_y)], style=BONE)
            diag.text(f"**{category}**", size=12).at(
                bx, end_y - 4 if above else end_y + 4, anchor="bottom_center" if above else "top_center")
            for t, cause in zip((0.35, 0.7), causes):
                cx = bx + reach * t
                cy = end_y + (spine_y - end_y) * t
                diag.polyline([(cx - 12, cy), (cx, cy)], style=BONE)
                diag.text(cause, size=11).at(cx - 16, cy, anchor="right_center")

        diag.caption(
            "**Figure 10:** Western Electric rule signals on an X-bar chart, "
            "and the cause-and-effect diagram for the first one",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "10_spc_control_chart_fishbone")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/manufacturing")
    build_diagram(dest)
