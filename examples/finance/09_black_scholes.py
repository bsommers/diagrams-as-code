"""Black-Scholes European call price against spot, with the delta that is its slope."""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
AMBER = "#8A5A00"
K, R, SIGMA, T = 100.0, 0.05, 0.20, 1.0


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def d1(s: float, t: float = T) -> float:
    return (math.log(s / K) + (R + 0.5 * SIGMA ** 2) * t) / (SIGMA * math.sqrt(t))


def call_price(s: float, t: float = T) -> float:
    if t <= 0:
        return max(s - K, 0.0)
    x1 = d1(s, t)
    x2 = x1 - SIGMA * math.sqrt(t)
    return s * norm_cdf(x1) - K * math.exp(-R * t) * norm_cdf(x2)


def delta(s: float, t: float = T) -> float:
    return norm_cdf(d1(s, t))


def diagram() -> Diagram:
    s0 = K
    c0, d0 = call_price(s0), delta(s0)
    with Diagram("Black-Scholes call price and delta", theme="paper") as diag:
        top = Plot(diag, x=(50, 150), y=(0, 60), origin=(100, 300), size=(520, 220))
        top.grid(xstep=10, ystep=20)
        top.axes(ylabel="Call price $C$", xstep=10, ystep=20, through_zero=False, arrows=False)
        top.function(lambda s: max(s - K, 0.0), stroke="#9AA3B5", width=1.6, dash="5,4")
        top.function(call_price, stroke=INK, width=2.4)
        top.function(lambda s: call_price(s, 0.25), stroke="#4F6D9A", width=1.6, dash="2,3")
        slope = top.tangent(call_price, s0, half=32)
        top.dot(s0, c0, radius=4.0)
        top.label(s0, c0, f"$C = {c0:.2f}$", size=12, anchor="right_center", dx=-12, dy=-12)
        legend = [("$T = 1$ year", INK, ""), ("$T = 0.25$ year", "#4F6D9A", "2,3"),
                  ("intrinsic value $\\max(S-K, 0)$", "#9AA3B5", "5,4"), ("tangent at $S = K$, slope $\\Delta$", AMBER, "")]
        for k, (name, colour, dash) in enumerate(legend):
            y = 56 - 6.5 * k
            top.line((52, y), (60, y), stroke=colour, width=2.0, dash=dash)
            top.label(62, y, name, size=12)

        bot = Plot(diag, x=(50, 150), y=(0, 1), origin=(100, 480), size=(520, 110))
        bot.grid(xstep=10, ystep=0.5)
        bot.axes(xlabel="Spot $S$", ylabel="Delta $\\Delta = N(d_1)$", xstep=10, ystep=0.5, through_zero=False, arrows=False)
        bot.function(delta, stroke=INK, width=2.4)
        bot.function(lambda s: delta(s, 0.25), stroke="#4F6D9A", width=1.6, dash="2,3")
        bot.vline(s0, stroke="#9AA3B5")
        bot.dot(s0, d0, radius=4.0)
        bot.label(s0, d0, f"$\\Delta = {d0:.3f}$", size=12, anchor="right_center", dx=-10, dy=-12)
        diag.caption(
            f"**Figure 9:** Black-Scholes European call, strike {K:g}, rate {R:.0%}, volatility {SIGMA:.0%}. "
            "Price (top) and delta $N(d_1)$ (bottom) against the spot $S$.\n"
            f"At $S = K$ the call costs {c0:.2f} and its tangent has slope {slope:.3f} = $\\Delta$; "
            "a shorter expiry (dotted) hugs the intrinsic value and makes delta steeper.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/finance") -> Path:
    return render_all(diagram(), output_dir, "09_black_scholes")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/finance"))
