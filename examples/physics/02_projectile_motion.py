"""Projectile motion from a cliff, with the velocity resolved at five instants.

Launch speed $v_0$, angle $\\theta$ and height $h_0$ fix everything: the path is
sampled from $x = v_0 \\cos\\theta\\, t$ and $y = h_0 + v_0 \\sin\\theta\\, t - g t^2 / 2$,
and the velocity arrows come from $v_x = v_0\\cos\\theta$ (constant) and
$v_y = v_0 \\sin\\theta - g t$. The apex, the flight time and the range are solved,
not read off.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

V0, THETA, H0, G = 30.0, math.radians(50.0), 8.0, 9.81
VX = V0 * math.cos(THETA)
VY0 = V0 * math.sin(THETA)
SCALE = 2.2  # px per m/s
INK, BLUE, GREEN, RED = "#111111", "#1F2F57", "#2E6B3F", "#9C2F2F"


def height(t: float) -> float:
    return H0 + VY0 * t - G * t * t / 2


def diagram() -> Diagram:
    t_apex = VY0 / G
    t_land = (VY0 + math.sqrt(VY0 ** 2 + 2 * G * H0)) / G
    h_max = height(t_apex)
    rng = VX * t_land

    with Diagram("Projectile motion", theme="paper") as diag:
        p = Plot(diag, x=(-10, 115), y=(0, 40), origin=(80, 320), size=(775, 248))
        p.grid(xstep=10, ystep=10)
        diag.polygon([p.px(-10, 0), p.px(0, 0), p.px(0, H0), p.px(-10, H0)],
                     style=Style(fill="#E6E8EE", stroke=INK, stroke_width=1.2), z=0)
        p.axes(xlabel="$x$ (m)", ylabel="$y$ (m)", through_zero=False, xstep=10, ystep=10, labels=False)
        for tx in range(-10, 111, 10):
            q = p.px(tx, 0)
            diag.text(str(tx).replace("-", "\u2212"), size=11).at(q[0], q[1] + 6, anchor="top_center")
        for ty in range(10, 41, 10):
            q = p.px(-10, ty)
            diag.text(str(ty), size=11).at(q[0] - 7, q[1], anchor="right_center")
        p.parametric(lambda t: VX * t, lambda t: height(t), 0, t_land, width=2.0, dash="6,4")
        p.hline(h_max, stroke="#888888", dash="3,3")
        p.dot(rng, 0, label=f"$R = {rng:.1f}$ m", dx=8, dy=-4, anchor="bottom_left")
        p.label(-9.5, h_max, f"$H = {h_max:.1f}$ m", dy=-10, anchor="bottom_left")

        def arrow(a, b, color, width=1.8, dash=False):
            opts = dict(routing="direct", width=width, color=color, head="stealth")
            if dash:
                opts["style"] = "dashed"
            diag.connect(a, b, **opts)

        for t in (0.0, 1.5, t_apex, 3.5, 4.6):
            x, y = VX * t, height(t)
            vy = VY0 - G * t
            o = p.px(x, y)
            diag.point(*o, dot=True, radius=3)
            tip = (o[0] + VX * SCALE, o[1] - vy * SCALE)
            if abs(vy) > 1.0:
                arrow(o, (o[0] + VX * SCALE, o[1]), BLUE, 1.0)
                arrow(o, (o[0], o[1] - vy * SCALE), GREEN, 1.0)
                diag.polyline([(o[0] + VX * SCALE, o[1]), tip], style=Style(stroke="#888888", stroke_width=0.7, dash="2,2"))
                diag.polyline([(o[0], o[1] - vy * SCALE), tip], style=Style(stroke="#888888", stroke_width=0.7, dash="2,2"))
            arrow(o, tip, RED, 2.2)

        # Labels for the launch and the apex.
        o0, oa = p.px(0, H0), p.px(VX * t_apex, h_max)
        diag.text("$v_0$", size=14, color=RED).at(o0[0] + VX * SCALE - 6, o0[1] - VY0 * SCALE - 2, anchor="bottom_right")
        diag.text("$v_{0x}$", size=12, color=BLUE).at(o0[0] + VX * SCALE / 2, o0[1] + 6, anchor="top_center")
        diag.text("$v_{0y}$", size=12, color=GREEN).at(o0[0] - 6, o0[1] - VY0 * SCALE / 2, anchor="right_center")
        diag.text("$v = v_x$", size=12, color=RED).at(oa[0] + VX * SCALE / 2, oa[1] - 10, anchor="bottom_center")
        r = 52.0
        a1 = (o0[0] + r * math.cos(THETA), o0[1] - r * math.sin(THETA))
        diag.path(f"M {o0[0] + r:.2f} {o0[1]:.2f} A {r} {r} 0 0 0 {a1[0]:.2f} {a1[1]:.2f}",
                  style=Style(fill="none", stroke=INK, stroke_width=0.9))
        diag.text("$\\theta$", size=13).at(o0[0] + r + 10, o0[1] - 12, anchor="center")

        vy_end = VY0 - G * 4.6
        diag.text(
            f"$v_0 = {V0:g}$ m/s, $\\theta = {math.degrees(THETA):g}^\\circ$, $h_0 = {H0:g}$ m\n"
            f"$v_x = v_0\\cos\\theta = {VX:.1f}$ m/s (constant)\n"
            f"$v_y = v_0\\sin\\theta - g t$: from {VY0:.1f} m/s to \u2212{abs(vy_end):.1f} m/s at $t = 4.6$ s\n"
            f"Apex at $t = {t_apex:.2f}$ s; lands at $t = {t_land:.2f}$ s",
            size=12,
        ).at(p.px(28, 17)[0], p.px(28, 17)[1], anchor="top_left")
        diag.caption(
            "**Figure 2:** Projectile motion from a cliff; the horizontal velocity is constant while the vertical one falls linearly",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/physics") -> Path:
    return render_all(diagram(), output_dir, "02_projectile_motion")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/physics")
    build_diagram(dest)
