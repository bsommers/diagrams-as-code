"""Concentration against time for zero-, first- and second-order reactions of A.

All three start at $[\\mathrm{A}]_0 = 1.00$ M and are given rate constants that make the
first half-life 10 s, so the three curves cross at $(10\\ \\mathrm{s}, 0.50\\ \\mathrm{M})$:
$k_0 = [\\mathrm{A}]_0 / 2t_{1/2} = 0.050$ M/s, $k_1 = \\ln 2 / t_{1/2} = 0.0693$ /s and
$k_2 = 1/([\\mathrm{A}]_0 t_{1/2}) = 0.100$ /(M s). The integrated rate laws are
$[\\mathrm{A}] = [\\mathrm{A}]_0 - k_0 t$, $\\ln[\\mathrm{A}] = \\ln[\\mathrm{A}]_0 - k_1 t$ and
$1/[\\mathrm{A}] = 1/[\\mathrm{A}]_0 + k_2 t$. Each linearisation turns exactly one order
into a straight line, which is how the order is found from data.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

A0, T_HALF = 1.00, 10.0
K0 = A0 / (2 * T_HALF)
K1 = math.log(2) / T_HALF
K2 = 1 / (A0 * T_HALF)
RED, BLUE, GREEN, INK = "#9C2F2F", "#1F2F57", "#2E6B3F", "#111111"
TMAX = 40.0


def zero(t: float) -> float:
    return max(A0 - K0 * t, 0.0)


def first(t: float) -> float:
    return A0 * math.exp(-K1 * t)


def second(t: float) -> float:
    return A0 / (1 + A0 * K2 * t)


ORDERS = [("zero", zero, RED), ("first", first, BLUE), ("second", second, GREEN)]


def diagram() -> Diagram:
    with Diagram("Reaction order kinetics", theme="paper") as diag:
        # (a) concentration against time
        a = Plot(diag, x=(0, TMAX), y=(0, 1.05), origin=(80, 370), size=(360, 240))
        a.grid(xstep=10, ystep=0.25)
        a.axes(xlabel="$t$ (s)", ylabel="$[\\mathrm{A}]$ (M)", xstep=10, ystep=0.25, through_zero=False)
        for _, f, color in ORDERS:
            a.function(f, 0, TMAX, stroke=color, width=2.4)
        a.vline(T_HALF, stroke="#888888", width=0.9)
        a.hline(0.5, stroke="#888888", width=0.9)
        a.dot(T_HALF, 0.5, radius=4.0)
        a.label(T_HALF, 0.5, "first half-life, 10 s", size=12, anchor="bottom_left", dx=8, dy=-10)
        a.label(16, 0.16, "zero order", size=12, anchor="right_center", color=RED, dx=-6, dy=8)
        a.label(33, 0.185, "first order", size=12, anchor="center", color=BLUE)
        a.label(27, 0.30, "second order", size=12, anchor="bottom_left", color=GREEN)
        diag.text("**(a)** $[\\mathrm{A}]$ against $t$", size=14).at(40, 78, anchor="left_center")

        # (b) ln[A] against time
        b = Plot(diag, x=(0, TMAX), y=(-3, 0.5), origin=(570, 290), size=(330, 120))
        b.grid(xstep=10, ystep=1)
        b.axes(xlabel="$t$ (s)", ylabel="$\\ln[\\mathrm{A}]$", xstep=10, ystep=1, through_zero=False, size=10)
        for name, f, color in ORDERS:
            b.function(lambda t, f=f: math.log(max(f(t), 1e-12)), 0, TMAX, stroke=color, width=2.2 if name == "first" else 1.5,
                       dash="" if name == "first" else "5,4")
        b.label(1, -2.45, f"slope $= -k_1 = -{K1:.4f}$ /s", size=11, anchor="left_center", color=BLUE)
        diag.text("**(b)** first order is straight in $\\ln[\\mathrm{A}]$", size=14).at(540, 78, anchor="left_center")

        # (c) 1/[A] against time
        c = Plot(diag, x=(0, TMAX), y=(0, 6), origin=(570, 520), size=(330, 120))
        c.grid(xstep=10, ystep=2)
        c.axes(xlabel="$t$ (s)", ylabel="$1/[\\mathrm{A}]$ (/M)", xstep=10, ystep=2, through_zero=False, size=10)
        for name, f, color in ORDERS:
            c.function(lambda t, f=f: 1 / f(t) if f(t) > 1e-9 else 1e9, 0, TMAX, stroke=color,
                       width=2.2 if name == "second" else 1.5, dash="" if name == "second" else "5,4", n=800)
        c.label(18, 0.9, f"slope $= +k_2 = {K2:.3f}$ /(M s)", size=12, anchor="left_center", color=GREEN)
        diag.text("**(c)** second order is straight in $1/[\\mathrm{A}]$", size=14).at(540, 342, anchor="left_center")

        # Summary table.
        y0, rows = 440, [
            ("**order**", "**rate law**", "**integrated**", "**straight plot (slope)**", "**half-life**"),
            ("0", "$\\mathrm{rate} = k$", "$[\\mathrm{A}] = [\\mathrm{A}]_0 - kt$", "$[\\mathrm{A}]$ vs $t$ ($-k$)", "$[\\mathrm{A}]_0 / 2k$"),
            ("1", "$\\mathrm{rate} = k[\\mathrm{A}]$", "$\\ln[\\mathrm{A}] = \\ln[\\mathrm{A}]_0 - kt$", "$\\ln[\\mathrm{A}]$ vs $t$ ($-k$)", "$\\ln 2 / k$"),
            ("2", "$\\mathrm{rate} = k[\\mathrm{A}]^2$", "$1/[\\mathrm{A}] = 1/[\\mathrm{A}]_0 + kt$", "$1/[\\mathrm{A}]$ vs $t$ ($+k$)", "$1/(k[\\mathrm{A}]_0)$"),
        ]
        cols = (40, 85, 220, 400, 540)
        # Table sits under panel (a); the right-hand column is taken by (b) and (c).
        cols = (30, 82, 180, 345, 470)
        for r, row in enumerate(rows):
            for x, text in zip(cols, row):
                diag.text(text, size=12).at(x, y0 + 28 + r * 28, anchor="left_center")
        diag.text("units of $k$:  zero order M/s,  first order /s,  second order /(M s)", size=12).at(
            30, y0 + 28 + 4 * 28, anchor="left_center")
        diag.text("Only the first half-life is the same. The next halving takes 5 s (zero), 10 s (first)\n"
                  "and 20 s (second) from 0.50 M, because the half-life of a second-order reaction\n"
                  "grows as $[\\mathrm{A}]$ falls and that of a zero-order reaction shrinks.\n"
                  "In (b) and (c) the dashed curves are the other two orders: they bend.",
                  size=12).at(30, y0 + 28 + 5 * 28 - 6, anchor="top_left")
        diag.caption("**Figure 10:** Zero-, first- and second-order decay of A with the same first half-life, and the plot that straightens each",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "10_reaction_order_kinetics")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
