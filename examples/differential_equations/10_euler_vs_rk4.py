"""Euler against RK4 on y' = y, y(0) = 1, whose exact solution is e^x.

Left: with the same coarse step h = 0.5 the Euler polygon falls visibly below
the exact curve while RK4 sits on it. Right: the global error at x = 3 against
step size on log-log axes (both axes hold base-10 logarithms). Euler's error
falls like h (slope 1), RK4's like h^4 (slope 4); the fitted slopes are printed
on the lines and checked by the script.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "10_euler_vs_rk4"
X_END = 3.0
INK, BLUE, RED, AMBER = "#1F2F57", "#2E6F9E", "#9C2B2B", "#8A5A00"


def f(x: float, y: float) -> float:
    return y


def euler(h: float, x_end: float = X_END) -> list[tuple[float, float]]:
    n = round(x_end / h)
    x, y = 0.0, 1.0
    out = [(x, y)]
    for _ in range(n):
        y += h * f(x, y)
        x += h
        out.append((x, y))
    return out


def rk4(h: float, x_end: float = X_END) -> list[tuple[float, float]]:
    n = round(x_end / h)
    x, y = 0.0, 1.0
    out = [(x, y)]
    for _ in range(n):
        k1 = f(x, y)
        k2 = f(x + h / 2, y + h / 2 * k1)
        k3 = f(x + h / 2, y + h / 2 * k2)
        k4 = f(x + h, y + h * k3)
        y += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        x += h
        out.append((x, y))
    return out


def diagram() -> Diagram:
    with Diagram("Euler versus RK4", theme="paper") as diag:
        a = Plot(diag, x=(0, X_END), y=(0, 22), origin=(80, 440), size=(400, 330))
        a.grid(xstep=0.5, ystep=5)
        a.axes(xlabel="$x$", ylabel="$y$", xstep=0.5, ystep=5)
        a.function(math.exp, stroke="#7C8AA8", width=3.2)
        e, r = euler(0.5), rk4(0.5)
        a.polyline(e, stroke=RED, width=1.8)
        a.polyline(r, stroke=BLUE, width=1.8, dash="")
        for x, y in e:
            a.dot(x, y, radius=3)
        for x, y in r:
            cx, cy = a.px(x, y)
            diag.path(f"M {cx - 3.5} {cy - 3.5} h 7 v 7 h -7 Z", style=Style(
                fill="#FFFFFF", stroke=BLUE, stroke_width=1.4), z=3)
        a.label(1.0, 17.5, "exact $e^x$", size=12, color="#5A6A88", anchor="left_center")
        a.label(1.0, 15.0, "RK4, $h = 0.5$", size=12, color=BLUE, anchor="left_center")
        a.label(1.0, 12.5, "Euler, $h = 0.5$", size=12, color=RED, anchor="left_center")
        a.line((0.2, 17.5), (0.9, 17.5), stroke="#7C8AA8", width=3.2)
        a.line((0.2, 15.0), (0.9, 15.0), stroke=BLUE, width=1.8)
        a.line((0.2, 12.5), (0.9, 12.5), stroke=RED, width=1.8)
        diag.text("Same step, different accuracy", size=14).at(280, 82, anchor="bottom_center")

        # Global error at x = 3 against h, in decades.
        hs = [1 / 2**k for k in range(0, 9)]
        err_e = [abs(euler(h)[-1][1] - math.exp(X_END)) for h in hs]
        err_r = [abs(rk4(h)[-1][1] - math.exp(X_END)) for h in hs]
        lx, le, lr = [math.log10(h) for h in hs], [math.log10(v) for v in err_e], [math.log10(v) for v in err_r]

        def slope(xs, ys):
            return (ys[-1] - ys[-3]) / (xs[-1] - xs[-3])

        s_e, s_r = slope(lx, le), slope(lx, lr)
        assert abs(s_e - 1) < 0.1 and abs(s_r - 4) < 0.15
        b = Plot(diag, x=(-2.8, 0.2), y=(-12, 2), origin=(620, 440), size=(360, 330))
        b.grid(xstep=1, ystep=2)
        b.axes(xlabel="$h$", ylabel="error", labels=False, through_zero=False, xstep=1, ystep=2)
        for k in (-2, -1, 0):
            b.label(k, -12, f"$10^{{{k}}}$" if k else "$1$", size=11, anchor="top_center", dy=8)
        for k in range(-12, 3, 2):
            b.label(-2.8, k, f"$10^{{{k}}}$" if k else "$1$", size=11, anchor="right_center", dx=-7)
        b.polyline(list(zip(lx, le)), stroke=RED, width=1.9)
        b.polyline(list(zip(lx, lr)), stroke=BLUE, width=1.9)
        for u, v in zip(lx, le):
            b.dot(u, v, radius=3)
        for u, v in zip(lx, lr):
            cx, cy = b.px(u, v)
            diag.path(f"M {cx - 3.5} {cy - 3.5} h 7 v 7 h -7 Z", style=Style(
                fill="#FFFFFF", stroke=BLUE, stroke_width=1.4), z=3)
        b.label(-1.4, -1.8, f"Euler: slope {s_e:.2f}", size=12, color=RED, anchor="top_left")
        b.label(-2.1, lr[6] - 2.5, f"RK4: slope {s_r:.2f}", size=12, color=BLUE, anchor="top_left")
        diag.text("Error at $x = 3$ against step", size=14).at(800, 82, anchor="bottom_center")
        diag.caption(
            "**Figure 10:** Euler and fourth-order Runge-Kutta on $y' = y$: the same step $h = 0.5$ "
            "(left) and global error against step size, slopes 1 and 4 (right)",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/differential_equations") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/differential_equations")
    build_diagram(dest)
