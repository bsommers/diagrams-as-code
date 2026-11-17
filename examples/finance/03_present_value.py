"""Present value of a cash-flow stream: each flow is discounted back to today."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"
AMBER = "#8A5A00"
RATE = 0.06
FLOWS = [100.0, 100.0, 100.0, 100.0, 1100.0]  # years 1..5: four coupons, then coupon plus principal
X0, DX, AXIS_Y = 230.0, 120.0, 250.0


def diagram() -> Diagram:
    factors = [1 / (1 + RATE) ** t for t in range(1, len(FLOWS) + 1)]
    pvs = [cf * f for cf, f in zip(FLOWS, factors)]
    total = sum(pvs)
    xs = [X0 + t * DX for t in range(len(FLOWS) + 1)]
    with Diagram("Present value timeline", theme="paper") as diag:
        # Timeline with ticks and year labels.
        diag.connect((xs[0] - 40, AXIS_Y), (xs[-1] + 50, AXIS_Y), routing="direct", width=1.4, head="stealth")
        diag.path(" ".join(f"M {x} {AXIS_Y - 4} v 8" for x in xs), style=Style(fill="none", stroke=INK, stroke_width=1.2))
        diag.text("Year $t$", size=13).at(xs[-1] + 56, AXIS_Y, anchor="left_center")
        for t, x in enumerate(xs):
            diag.text(f"{t}", size=13).at(x, AXIS_Y + 10, anchor="top_center")
        diag.text("today", size=12, italic=True, font="serif").at(xs[0], AXIS_Y + 30, anchor="top_center")

        # Cash flows as upward arrows, drawn to a height that grows with the amount.
        for x, cf in zip(xs[1:], FLOWS):
            h = 40 + 70 * (cf / max(FLOWS)) ** 0.5
            diag.connect((x, AXIS_Y), (x, AXIS_Y - h), routing="direct", width=2.2, head="stealth", color=INK)
            diag.text(f"{cf:,.0f}", size=14).at(x, AXIS_Y - h - 6, anchor="bottom_center")
        diag.text("cash flow $C_t$", size=12, italic=True, font="serif").at(xs[0], AXIS_Y - 60, anchor="bottom_center")

        # Rows of the discounting table, ruled.
        rows = [("discount factor $(1+r)^{-t}$", 340), ("present value $C_t (1+r)^{-t}$", 400)]
        left = 20
        for label, y in rows:
            diag.polyline([(left, y - 24), (xs[-1] + 60, y - 24)], style=Style(fill="none", stroke="#9AA3B5", stroke_width=0.7))
            diag.text(label, size=13).at(left, y, anchor="left_center")
        diag.polyline([(left, 424), (xs[-1] + 60, 424)], style=Style(fill="none", stroke="#9AA3B5", stroke_width=0.7))
        for x, f, pv in zip(xs[1:], factors, pvs):
            diag.text(f"{f:.4f}", size=13).at(x, 340, anchor="center")
            diag.text(f"{pv:,.2f}", size=13, color=AMBER).at(x, 400, anchor="center")
            # A dashed guide from the cash flow down to its present value.
            for a, b in ((AXIS_Y + 50, 324), (356, 376)):
                diag.connect((x, a), (x, b), routing="direct", width=0.8, style="dashed", head="stealth", color="#9AA3B5")
        diag.text(f"$PV = \\sum_{{t=1}}^{{5}} C_t (1+r)^{{-t}} = {total:,.2f}$", size=15, color=AMBER).at(
            (xs[0] + xs[-1]) / 2 + 30, 450, anchor="top_center")
        diag.text(f"discount rate $r = {RATE:.0%}$", size=13).at(left, 200, anchor="left_center")
        diag.caption(
            "**Figure 3:** Present value of a five-year 10% bond with a face value of 1,000, discounted at 6%.\n"
            "Each flow is multiplied by its discount factor; the present values sum to the price today.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/finance") -> Path:
    return render_all(diagram(), output_dir, "03_present_value")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/finance"))
