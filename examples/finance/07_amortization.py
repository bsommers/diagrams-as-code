"""Yearly interest and principal paid on a 30-year fixed-rate mortgage."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
LOAN, RATE, YEARS = 200_000.0, 0.06, 30
PRINCIPAL_FILL, INTEREST_FILL = "#8FB3DE", "#E3A9A0"


def schedule() -> tuple[float, list[tuple[float, float]]]:
    """Monthly payment, and (interest, principal) summed per year."""
    r, n = RATE / 12, YEARS * 12
    payment = LOAN * r / (1 - (1 + r) ** -n)
    balance, years = LOAN, []
    for _ in range(YEARS):
        interest = principal = 0.0
        for _ in range(12):
            i = balance * r
            interest += i
            principal += payment - i
            balance -= payment - i
        years.append((interest, principal))
    return payment, years


def diagram() -> Diagram:
    payment, years = schedule()
    paid = payment * 12
    total_interest = sum(i for i, _ in years)
    with Diagram("Amortization schedule", theme="paper") as diag:
        p = Plot(diag, x=(0, YEARS + 1), y=(0, 20000), origin=(100, 340), size=(580, 280))
        p.grid(xstep=5, ystep=4000)
        p.axes(xlabel="Year", ylabel="Paid in the year", xstep=5, ystep=4000, through_zero=False, arrows=False)
        for k, (interest, principal) in enumerate(years, start=1):
            half = 0.38
            for lo, hi, fill in ((0.0, interest, INTEREST_FILL), (interest, interest + principal, PRINCIPAL_FILL)):
                pts = [p.px(k - half, lo), p.px(k - half, hi), p.px(k + half, hi), p.px(k + half, lo)]
                diag.polygon(pts, style=Style(fill=fill, stroke=INK, stroke_width=0.7), z=0)
        p.hline(paid, stroke="#8A5A00")
        p.label(YEARS + 1, paid, f"payments {paid:,.0f} a year", size=12, anchor="bottom_right", dy=-4, dx=-2)
        # Legend.
        for k, (name, fill) in enumerate((("Interest", INTEREST_FILL), ("Principal", PRINCIPAL_FILL))):
            x, y = p.px(1, 19000 - k * 1800)
            diag.polygon([(x, y - 6), (x + 18, y - 6), (x + 18, y + 6), (x, y + 6)],
                         style=Style(fill=fill, stroke=INK, stroke_width=0.7))
            diag.text(name, size=12).at(x + 26, y, anchor="left_center")
        diag.caption(
            f"**Figure 7:** Amortization of a {LOAN:,.0f} loan at {RATE:.0%} over {YEARS} years "
            f"(monthly payment {payment:,.2f}, paid annually {paid:,.0f}).\n"
            f"Early payments are mostly interest; total interest over the term is {total_interest:,.0f}.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/finance") -> Path:
    return render_all(diagram(), output_dir, "07_amortization")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/finance"))
