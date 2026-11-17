"""Candlestick chart with a 10-day moving average and volume bars (synthetic data)."""
from __future__ import annotations

import random
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

SEED, DAYS, WINDOW = 42, 48, 10


def series() -> list[tuple[int, float, float, float, float, float]]:
    """(day, open, high, low, close, volume) from a seeded random walk."""
    rng = random.Random(SEED)
    price, rows = 100.0, []
    for day in range(1, DAYS + 1):
        o = price
        c = o * (1 + rng.gauss(0.002, 0.014))
        h = max(o, c) * (1 + abs(rng.gauss(0, 0.006)))
        lo = min(o, c) * (1 - abs(rng.gauss(0, 0.006)))
        vol = 2.0 + 6.0 * abs(c - o) / o * 25 + rng.uniform(0, 2.5)
        rows.append((day, o, h, lo, c, vol))
        price = c
    return rows


def diagram() -> Diagram:
    rows = series()
    closes = [r[4] for r in rows]
    ma = [(rows[i][0], sum(closes[i - WINDOW + 1:i + 1]) / WINDOW) for i in range(WINDOW - 1, DAYS)]
    lo_p = int(min(r[3] for r in rows)) - 1
    hi_p = int(max(r[2] for r in rows)) + 2
    with Diagram("Candlestick chart", theme="paper") as diag:
        top = Plot(diag, x=(0, DAYS + 1), y=(lo_p, hi_p), origin=(90, 330), size=(640, 250))
        top.grid(xstep=6)
        top.axes(ylabel="Price", xstep=6, labels=True, arrows=False, through_zero=False)
        top.candles([(r[0], r[1], r[2], r[3], r[4]) for r in rows], width=0.6)
        top.polyline(ma, stroke="#1F2F57", width=2.0)
        top.line((1, hi_p - 1.2), (3.5, hi_p - 1.2), stroke="#1F2F57", width=2.0)
        top.label(4, hi_p - 1.2, f"{WINDOW}-day moving average", size=12)
        vmax = 12
        vol = Plot(diag, x=(0, DAYS + 1), y=(0, vmax), origin=(90, 460), size=(640, 70))
        vol.axes(xlabel="", ystep=6, xstep=6, labels=True, arrows=False, through_zero=False)
        vol.bar_chart([(r[0], r[5]) for r in rows], width=0.6, fill="#B9C6DC")
        vol.label(0, vmax, "Volume", anchor="bottom_left", dx=-60, dy=-6)
        diag.text("Trading day", size=13).at(410, 500, anchor="top_center")
        diag.caption(
            "**Figure 1:** Candlestick chart with a 10-day moving average and volume bars. "
            "Green candles close above their open, red below.\n"
            f"The data are synthetic: a seeded random walk (seed {SEED}), not market prices.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/finance") -> Path:
    return render_all(diagram(), output_dir, "01_candlestick_chart")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/finance"))
