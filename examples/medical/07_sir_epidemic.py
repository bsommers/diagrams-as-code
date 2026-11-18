"""SIR epidemic model integrated with RK4 from its differential equations.

dS/dt = -beta S I, dI/dt = beta S I - gamma I, dR/dt = gamma I  (S, I, R are population
fractions). Infectious period 1/gamma = 5 days (gamma = 0.2 per day); R0 = beta / gamma.
Left: R0 = 2.5. Right: infected fraction for three values of R0.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
BLUE, RED, GREEN, AMBER = "#2F5FA8", "#B03A3A", "#2E6B3F", "#8A5A00"
GAMMA = 0.2
I0 = 1e-3
DAYS = 100.0


def simulate(r0: float, days: float = DAYS, dt: float = 0.1):
    """RK4 for the SIR system; returns a list of (t, S, I, R)."""
    beta = r0 * GAMMA

    def f(s, i):
        return -beta * s * i, beta * s * i - GAMMA * i

    s, i = 1.0 - I0, I0
    out = [(0.0, s, i, 1.0 - s - i)]
    n = round(days / dt)
    for k in range(n):
        a1, b1 = f(s, i)
        a2, b2 = f(s + dt / 2 * a1, i + dt / 2 * b1)
        a3, b3 = f(s + dt / 2 * a2, i + dt / 2 * b2)
        a4, b4 = f(s + dt * a3, i + dt * b3)
        s += dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        i += dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        out.append(((k + 1) * dt, s, i, 1.0 - s - i))
    return out


def diagram() -> Diagram:
    r0 = 2.5
    run = simulate(r0)
    t_pk, _, i_pk, _ = max(run, key=lambda row: row[2])
    herd = 1.0 - 1.0 / r0
    final = run[-1][3]
    with Diagram("SIR epidemic curves", theme="paper") as diag:
        a = Plot(diag, x=(0, DAYS), y=(0, 1), origin=(100, 430), size=(470, 300))
        a.grid(xstep=20, ystep=0.25)
        a.axes(xlabel="Days", ylabel="Fraction of population", xstep=20, ystep=0.25, through_zero=False, arrows=False)
        a.polyline([(t, s) for t, s, _, _ in run], stroke=BLUE, width=2.4)
        a.polyline([(t, i) for t, _, i, _ in run], stroke=RED, width=2.4)
        a.polyline([(t, r) for t, _, _, r in run], stroke=GREEN, width=2.4)
        a.hline(1 / r0, stroke=AMBER)
        a.label(DAYS, 1 / r0, "$S = 1/R_0$", size=12, anchor="bottom_right", dy=-4, color=AMBER)
        a.dot(t_pk, i_pk, radius=4.0)
        a.label(t_pk, i_pk, f"peak $I = {i_pk:.2f}$ at day {t_pk:.0f}", size=12, anchor="bottom_left", dx=10, dy=-6)
        a.label(46, 0.21, "Susceptible $S$", size=13, anchor="left_center", color=BLUE)
        a.label(58, 0.065, "Infected $I$", size=13, anchor="left_center", color=RED)
        a.label(DAYS, final, "Recovered $R$", size=13, anchor="top_right", dy=-26, color=GREEN)
        diag.text(
            "$R_0 = \\beta / \\gamma = 2.5$, $\\gamma = 0.2$ day$^{-1}$\n"
            f"Peak infected fraction $1 - (1 + \\ln R_0)/R_0 = {i_pk:.2f}$\n"
            f"Herd-immunity threshold $1 - 1/R_0 = {herd:.0%}$\n"
            f"Final epidemic size {final:.0%} of the population",
            size=12,
        ).at(100, 470, anchor="top_left")

        b = Plot(diag, x=(0, DAYS), y=(0, 0.5), origin=(680, 430), size=(390, 300))
        b.grid(xstep=20, ystep=0.1)
        b.axes(xlabel="Days", ylabel="Infected fraction $I$", xstep=20, ystep=0.1, through_zero=False, arrows=False)
        for r, colour, x_lab in ((1.5, GREEN, 70), (2.5, RED, 40), (4.0, BLUE, 22)):
            sim = simulate(r)
            b.polyline([(t, i) for t, _, i, _ in sim], stroke=colour, width=2.4)
            tp, _, ip, _ = max(sim, key=lambda row: row[2])
            b.dot(tp, ip, radius=3.2)
            b.label(tp, ip, f"$R_0 = {r:g}$", size=12, anchor="bottom_left", dx=8, dy=-4, color=colour)
        diag.caption(
            "**Figure 7:** SIR model integrated numerically. Left: with $R_0 = 2.5$ infection peaks when the susceptible fraction falls to $1/R_0$.\n"
            "Right: a larger $R_0$ gives an earlier, taller epidemic; for $R_0 < 1$ infection would die out",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/medical") -> Path:
    return render_all(diagram(), output_dir, "07_sir_epidemic")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/medical"))
