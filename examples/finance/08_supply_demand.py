"""Supply and demand with the equilibrium and the consumer and producer surplus."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
AMBER = "#8A5A00"
D_INTERCEPT, D_SLOPE = 100.0, 1.0   # inverse demand  P = 100 - Q
S_INTERCEPT, S_SLOPE = 20.0, 1.0    # inverse supply  P = 20 + Q


def demand(q: float) -> float:
    return D_INTERCEPT - D_SLOPE * q


def supply(q: float) -> float:
    return S_INTERCEPT + S_SLOPE * q


def diagram() -> Diagram:
    q_star = (D_INTERCEPT - S_INTERCEPT) / (D_SLOPE + S_SLOPE)
    p_star = demand(q_star)
    consumer = 0.5 * q_star * (D_INTERCEPT - p_star)
    producer = 0.5 * q_star * (p_star - S_INTERCEPT)
    with Diagram("Supply and demand", theme="paper") as diag:
        p = Plot(diag, x=(0, 100), y=(0, 105), origin=(100, 360), size=(520, 300))
        p.axes(xlabel="Quantity $Q$", ylabel="Price $P$", xstep=20, ystep=20, arrows=True)
        p.area(demand, 0, q_star, g=lambda q: p_star, fill="#DCE6F2", opacity=1.0)
        p.area(lambda q: p_star, 0, q_star, g=supply, fill="#F3D9D5", opacity=1.0)
        p.function(demand, 0, 100, stroke=INK, width=2.4)
        p.function(supply, 0, 100, stroke="#C0392B", width=2.4)
        p.line((0, p_star), (q_star, p_star), stroke=AMBER)
        p.line((q_star, 0), (q_star, p_star), stroke=AMBER)
        p.dot(q_star, p_star, radius=4.5)
        p.label(q_star, p_star, "equilibrium $E$", size=13, anchor="left_center", dx=12, dy=-14)
        p.label(q_star, 0, f"$Q^* = {q_star:g}$", size=12, anchor="top_center", dy=22, color=AMBER)
        p.label(0, p_star, f"$P^* = {p_star:g}$", size=12, anchor="right_center", dx=-30, color=AMBER)
        p.label(11, p_star + 13, f"consumer\nsurplus\n$= {consumer:g}$", size=12, anchor="center")
        p.label(11, p_star - 13, f"producer\nsurplus\n$= {producer:g}$", size=12, anchor="center")
        p.label(88, demand(88), "demand $D$", size=13, anchor="bottom_left", dx=2, dy=-8, color=INK)
        p.label(88, supply(88), "supply $S$", size=13, anchor="top_left", dx=2, dy=8, color="#C0392B")
        diag.caption(
            "**Figure 8:** Linear supply and demand, $P = 100 - Q$ and $P = 20 + Q$. The market clears at "
            f"$Q^* = {q_star:g}$, $P^* = {p_star:g}$.\n"
            "Consumer surplus (blue) is the area between demand and price; producer surplus (red) is the area between price and supply.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/finance") -> Path:
    return render_all(diagram(), output_dir, "08_supply_demand")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/finance"))
