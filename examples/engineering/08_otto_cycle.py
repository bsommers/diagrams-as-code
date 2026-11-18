"""The air-standard Otto cycle on P-v and T-s diagrams.

Air with $c_v = 0.718$ kJ/(kg K), $R = 0.287$ kJ/(kg K), $\\gamma = 1.4$; compression
ratio $r = 8$, $T_1 = 300$ K, $P_1 = 100$ kPa, peak temperature $T_3 = 1800$ K.
States: 1-2 isentropic compression, 2-3 constant-volume heat addition, 3-4
isentropic expansion, 4-1 constant-volume heat rejection. Entropy is measured from
state 1; isochores on the T-s plane follow $T = T_a e^{(s - s_a)/c_v}$.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

CV, R, GAMMA = 0.718, 0.287, 1.4
RATIO, T1, P1, T3 = 8.0, 300.0, 100.0, 1800.0
RED, BLUE, INK = "#9C2F2F", "#1F2F57", "#111111"


def diagram() -> Diagram:
    v1 = R * T1 / P1
    v2 = v1 / RATIO
    t2 = T1 * RATIO ** (GAMMA - 1)
    p2 = P1 * RATIO ** GAMMA
    p3 = p2 * T3 / t2
    t4 = T3 / RATIO ** (GAMMA - 1)
    p4 = p3 / RATIO ** GAMMA
    s3 = CV * math.log(T3 / t2)
    qin, qout = CV * (T3 - t2), CV * (t4 - T1)
    eta = 1 - qout / qin
    assert abs(eta - (1 - RATIO ** (1 - GAMMA))) < 1e-9
    P = {1: (v1, P1), 2: (v2, p2), 3: (v2, p3), 4: (v1, p4)}
    S = {1: (0.0, T1), 2: (0.0, t2), 3: (s3, T3), 4: (s3, t4)}
    with Diagram("Otto cycle", theme="paper") as diag:
        a = Plot(diag, x=(0, 1.0), y=(-500, 5500), origin=(110.0, 470.0), size=(400.0, 330.0))
        a.grid(xstep=0.2, ystep=1000)
        a.axes(xlabel="$v$ (m$^3$/kg)", ylabel="$P$ (kPa)", xstep=0.2, ystep=1000, through_zero=False)
        loop = ([a.px(v, p2 * (v2 / v) ** GAMMA) for v in [v2 + (v1 - v2) * i / 60 for i in range(61)]]
                + [a.px(v1, p4)]
                + [a.px(v, p3 * (v2 / v) ** GAMMA) for v in [v1 - (v1 - v2) * i / 60 for i in range(61)]])
        diag.polygon(loop, style=Style(fill="#F2DADA", fill_opacity=0.8, stroke="none"), z=-2)
        a.function(lambda v: P1 * (v1 / v) ** GAMMA, v2, v1, stroke=BLUE, width=2.4)
        a.function(lambda v: p3 * (v2 / v) ** GAMMA, v2, v1, stroke=RED, width=2.4)
        a.polyline([P[2], P[3]], stroke=RED, width=2.4)
        a.polyline([P[4], P[1]], stroke=BLUE, width=2.4)
        offs = {1: (10, 4, "top_left"), 2: (-10, 4, "top_right"), 3: (-10, -4, "bottom_right"), 4: (10, -4, "bottom_left")}
        for i, (v, p) in P.items():
            dx, dy, an = offs[i]
            a.dot(v, p, radius=4, label=f"**{i}**", size=14, dx=dx, dy=dy, anchor=an)
        a.legend([("1-2 compression, 4-1 heat rejection", BLUE, ""),
                  ("2-3 heat addition, 3-4 expansion", RED, "")], at=(300.0, 200.0), size=12)

        b = Plot(diag, x=(-0.1, 1.0), y=(0, 2000), origin=(640.0, 470.0), size=(400.0, 330.0))
        b.grid(xstep=0.2, ystep=500)
        b.axes(xlabel="$s - s_1$ (kJ/kg K)", ylabel="$T$ (K)", xstep=0.2, ystep=500, through_zero=False)

        def isochore(sa, ta):
            return lambda s: ta * math.exp((s - sa) / CV)
        b.polyline([(0.0, T1), (0.0, t2)], stroke=BLUE, width=2.4)
        b.polyline([(s3, T3), (s3, t4)], stroke=RED, width=2.4)
        b.function(isochore(0.0, t2), 0.0, s3, stroke=RED, width=2.4)
        b.function(isochore(0.0, T1), 0.0, s3, stroke=BLUE, width=2.4)
        for i, (s, t) in S.items():
            dx, dy, an = {1: (-10, 4, "top_right"), 2: (-10, -4, "bottom_right"),
                          3: (10, -4, "bottom_left"), 4: (10, 4, "top_left")}[i]
            b.dot(s, t, radius=4, label=f"**{i}**", size=14, dx=dx, dy=dy, anchor=an)
        b.label(0.30, 900, "$v = v_1$", size=11, anchor="left_center", color=BLUE)
        b.label(0.20, 1750, "$v = v_2$", size=11, anchor="left_center", color=RED, dx=-20, dy=-8)
        diag.text(f"$r = {RATIO:g}$,  $T_2 = {t2:.0f}$ K,  $T_4 = {t4:.0f}$ K,  $P_3 = {p3:.0f}$ kPa\n"
                  f"$q_{{in}} = c_v(T_3 - T_2) = {qin:.0f}$ kJ/kg,  $q_{{out}} = c_v(T_4 - T_1) = {qout:.0f}$ kJ/kg\n"
                  f"$\\eta = 1 - r^{{1-\\gamma}} = {eta * 100:.1f}\\,\\%$", size=13).at(110.0, 540.0, anchor="top_left")
        diag.caption(
            "**Figure 8:** Air-standard Otto cycle on P-v and T-s diagrams with computed state points and thermal efficiency",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/engineering") -> Path:
    return render_all(diagram(), output_dir, "08_otto_cycle")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/engineering")
    build_diagram(dest)
