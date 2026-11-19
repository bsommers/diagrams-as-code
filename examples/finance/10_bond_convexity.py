"""Bond price against yield: convexity, and the duration tangent that approximates it."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
AMBER = "#8A5A00"
FACE, COUPON, YEARS = 100.0, 0.05, 10  # annual coupons
Y0 = 5.0  # yield at which the tangent touches, %


def price(y_pct: float) -> float:
    y = y_pct / 100.0
    return sum(FACE * COUPON / (1 + y) ** t for t in range(1, YEARS + 1)) + FACE / (1 + y) ** YEARS


def durations(y_pct: float) -> tuple[float, float]:
    """Macaulay and modified duration, in years."""
    y = y_pct / 100.0
    flows = [(t, FACE * COUPON + (FACE if t == YEARS else 0.0)) for t in range(1, YEARS + 1)]
    pv = sum(c / (1 + y) ** t for t, c in flows)
    mac = sum(t * c / (1 + y) ** t for t, c in flows) / pv
    return mac, mac / (1 + y)


def diagram() -> Diagram:
    p0 = price(Y0)
    mac, mod = durations(Y0)
    with Diagram("Bond price-yield convexity", theme="paper") as diag:
        p = Plot(diag, x=(0, 12), y=(50, 160), origin=(100, 360), size=(520, 300))
        p.grid(xstep=2, ystep=20)
        p.axes(xlabel="Yield $y$ (%)", ylabel="Price", xstep=2, ystep=20, through_zero=False)
        slope = -mod * p0 / 100.0  # dP/dy per percentage point
        tangent = lambda y: p0 + slope * (y - Y0)
        p.area(price, 0.5, 11.0, g=tangent, fill="#DCE6F2", opacity=1.0)
        p.function(price, 0, 12, stroke=INK, width=2.4)
        p.line((Y0 - 5.0, tangent(Y0 - 5.0)), (Y0 + 6.5, tangent(Y0 + 6.5)), stroke=AMBER, width=1.6)
        p.dot(Y0, p0, radius=4.5)
        p.label(Y0, p0, f"$y = {Y0:g}$%, $P = {p0:.2f}$ (par)", size=12, anchor="bottom_left", dx=12, dy=-12)
        p.label(12, price(12), "price", size=13, anchor="left_center", dx=8, color=INK)
        p.label(9.6, tangent(9.6), "duration tangent", size=12, anchor="top_right", dx=0, dy=12, color=AMBER)
        diag.text(
            f"$D_{{\\mathrm{{mod}}}} = {mod:.2f}$ years, slope $= -D_{{\\mathrm{{mod}}}} P = {slope:.2f}$ per point",
            size=12, color=AMBER,
        ).at(*p.px(6.3, 138), anchor="left_center")
        # Convexity gap: the curve lies above its tangent on both sides.
        diag.leader("convexity gap", p.px(0.9, (price(0.9) + tangent(0.9)) / 2),
                    at=p.px(2.6, 152), size=12)
        diag.caption(
            f"**Figure 10:** Price of a {YEARS}-year 5% annual-coupon bond against its yield, with the tangent at "
            f"{Y0:g}% whose slope is the modified duration ($D_{{\\mathrm{{mod}}}} = {mod:.2f}$; Macaulay duration {mac:.2f} years).\n"
            "The shaded gap between curve and tangent is convexity: yield falls raise the price more than duration predicts, "
            "rises cut it less.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/finance") -> Path:
    return render_all(diagram(), output_dir, "10_bond_convexity")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/finance"))
