"""Profit at expiry of a long call, long put, long straddle and bull call spread."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
K, CALL, PUT = 100.0, 6.0, 5.0         # strike and premiums of the single-option positions
K1, K2, C1, C2 = 95.0, 110.0, 9.0, 2.5  # bull spread: buy the K1 call, sell the K2 call
LO, HI = 70.0, 130.0


def call(s, k): return max(s - k, 0.0)
def put(s, k): return max(k - s, 0.0)


# name, profit function, break-evens computed from the premiums
STRATEGIES = [
    ("Long call", lambda s: call(s, K) - CALL, [K + CALL]),
    ("Long put", lambda s: put(s, K) - PUT, [K - PUT]),
    ("Long straddle", lambda s: call(s, K) + put(s, K) - CALL - PUT, [K - CALL - PUT, K + CALL + PUT]),
    ("Bull call spread", lambda s: call(s, K1) - call(s, K2) - (C1 - C2), [K1 + C1 - C2]),
]
ORIGINS = [(90, 240), (450, 240), (90, 500), (450, 500)]


def diagram() -> Diagram:
    with Diagram("Option payoff diagrams", theme="paper") as diag:
        for (name, f, breakevens), origin in zip(STRATEGIES, ORIGINS):
            p = Plot(diag, x=(LO - 5, HI), y=(-15, 30), origin=origin, size=(260, 160))
            p.grid(xstep=10, ystep=10)
            p.axes(xstep=10, ystep=10, arrows=False, size=10, labels=True)
            p.function(f, LO - 5, HI, stroke=INK, width=2.2, n=600)
            p.area(lambda s, f=f: max(f(s), 0), LO - 5, HI, fill="#DDEBDD", opacity=0.9)
            p.area(lambda s, f=f: min(f(s), 0), LO - 5, HI, fill="#F3D9D5", opacity=0.9)
            for be in breakevens:
                p.dot(be, 0, radius=3.5)
                p.label(be, 0, f"{be:g}", size=10, anchor="bottom_center", dy=-8, color="#8A5A00")
            diag.text(f"**{name}**", size=13).at(origin[0] + 130, origin[1] - 160 - 30, anchor="bottom_center")
            diag.text("$S_T$", size=12).at(origin[0] + 285, origin[1] - 160 * 15 / 45, anchor="left_center")
            diag.text("profit", size=11).at(origin[0], origin[1] - 160 - 14, anchor="bottom_center")
        diag.caption(
            "**Figure 5:** Profit at expiry against the underlying price $S_T$, premiums included. "
            "Break-evens (amber) are computed from the premiums:\n"
            f"call ${K:g} + {CALL:g}$, put ${K:g} - {PUT:g}$, straddle ${K:g} \\pm {CALL + PUT:g}$, "
            f"bull spread ${K1:g} + ({C1:g} - {C2:g})$. Strike {K:g}, spread strikes {K1:g} and {K2:g}.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/finance") -> Path:
    return render_all(diagram(), output_dir, "05_option_payoffs")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/finance"))
