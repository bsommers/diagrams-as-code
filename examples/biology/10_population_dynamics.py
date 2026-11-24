"""Population dynamics: logistic growth and the Lotka-Volterra predator-prey model.

Logistic: dN/dt = r N (1 - N/K) with r = 0.4 per day, K = 1000 and N(0) = 10, integrated with the plot
kit's RK4 solver and compared with unchecked exponential growth. The growth rate peaks at N = K/2
(value rK/4), which is the inflection of the S-curve at t = ln((K - N0)/N0) / r.

Lotka-Volterra: dx/dt = a x - b x y (prey) and dy/dt = d x y - g y (predator) with a = 1.0, b = 0.1,
d = 0.075 and g = 1.5, integrated with RK4. The equilibrium is x* = g/d = 20, y* = a/b = 10; orbits
around it are closed (the quantity d x - g ln x + b y - a ln y is conserved) and the populations
oscillate with the predator peak lagging the prey peak.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
BLUE, RED, GREEN, AMBER = "#2F5FA8", "#B03A3A", "#2E6B3F", "#8A5A00"
R, K, N0 = 0.4, 1000.0, 10.0
A, B, D, G = 1.0, 0.1, 0.075, 1.5
EQ = (G / D, A / B)


def lv(x, y):
    return (A * x - B * x * y, D * x * y - G * y)


def rk4(f, start, t_end, dt=0.01):
    """RK4 for a planar system; returns [(t, x, y), ...]."""
    x, y = start
    out = [(0.0, x, y)]
    for i in range(round(t_end / dt)):
        k1 = f(x, y)
        k2 = f(x + dt / 2 * k1[0], y + dt / 2 * k1[1])
        k3 = f(x + dt / 2 * k2[0], y + dt / 2 * k2[1])
        k4 = f(x + dt * k3[0], y + dt * k3[1])
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        out.append(((i + 1) * dt, x, y))
    return out


def period(start):
    """Time for the orbit through ``start`` to return to it (first return, by minimum distance)."""
    run = rk4(lv, start, 12.0, dt=0.005)
    best = min((row for row in run if row[0] > 2.0), key=lambda r: math.hypot(r[1] - start[0], r[2] - start[1]))
    return best[0]


def diagram() -> Diagram:
    t_inflect = math.log((K - N0) / N0) / R
    peak_rate = R * K / 4
    starts = [(10.0, 5.0), (14.0, 7.0), (18.0, 9.0)]
    big = rk4(lv, starts[0], period(starts[0]))
    x_max = math.ceil(max(r[1] for r in big) / 10) * 10
    y_max = math.ceil(max(r[2] for r in big) / 5) * 5 + 5
    series = rk4(lv, starts[0], 20.0)
    s_max = math.ceil(max(max(r[1], r[2]) for r in series) / 10) * 10 + 10

    with Diagram("Population dynamics", theme="paper") as diag:
        # ------------------------------------------------ logistic N(t)
        diag.text("**Logistic growth**", size=14).at(110, 40, anchor="top_left")
        diag.text("$dN/dt = rN(1 - N/K)$,  $r = 0.4$ day$^{-1}$,  $K = 1000$", size=12).at(110, 64, anchor="top_left")
        a = Plot(diag, x=(0, 24), y=(0, 1100), origin=(110, 340), size=(420, 220))
        a.grid(xstep=4, ystep=200)
        a.axes(xlabel="Time $t$ (days)", ylabel="Population $N$", xstep=4, ystep=200, through_zero=False, arrows=False)
        a.function(lambda t: N0 * math.exp(R * t), stroke=RED, width=1.8, dash="6,4")
        pts = a.solve_ode(lambda t, n: R * n * (1 - n / K), 0.0, N0, 24.0, steps=480, stroke=BLUE, width=2.6)
        a.hline(K, stroke=AMBER)
        a.label(24, K, "carrying capacity $K$", size=12, anchor="bottom_right", dy=-4, color=AMBER)
        a.hline(K / 2, stroke="#9AA3B8", dash="2,4")
        a.vline(t_inflect, stroke="#9AA3B8", dash="2,4")
        n_inf = min(pts, key=lambda p: abs(p[0] - t_inflect))[1]
        a.dot(t_inflect, K / 2, radius=4.0, label=f"inflection: $N = K/2$ at day {t_inflect:.1f}", size=11, dx=10, dy=18, anchor="top_left")
        a.label(14.8, 700, "logistic", size=12, anchor="left_center", color=BLUE)
        a.label(8.2, 880, "exponential, $e^{rt}$", size=12, anchor="right_center", color=RED)
        assert abs(n_inf - K / 2) < 8

        # ------------------------------------------------ growth rate vs N
        diag.text("**Growth rate is greatest at half capacity**", size=14).at(110, 396, anchor="top_left")
        b = Plot(diag, x=(0, K), y=(0, 120), origin=(110, 690), size=(420, 220))
        b.grid(xstep=200, ystep=20)
        b.axes(xlabel="Population $N$", ylabel="$dN/dt$ (per day)", xstep=200, ystep=20, through_zero=False, arrows=False)
        b.function(lambda n: R * n * (1 - n / K), stroke=BLUE, width=2.6)
        b.dot(K / 2, peak_rate, radius=4.0, label=f"maximum $rK/4 = {peak_rate:.0f}$ at $N = K/2$", size=11, dx=0, dy=-12, anchor="bottom_center")
        b.vline(K / 2, stroke="#9AA3B8", dash="2,4")

        # ------------------------------------------------ Lotka-Volterra time series
        diag.text("**Lotka-Volterra: prey and predator**", size=14).at(660, 40, anchor="top_left")
        diag.text("$dx/dt = ax - bxy$,  $dy/dt = dxy - gy$", size=12).at(660, 64, anchor="top_left")
        c = Plot(diag, x=(0, 20), y=(0, s_max), origin=(660, 340), size=(420, 220))
        c.grid(xstep=4, ystep=10)
        c.axes(xlabel="Time $t$", ylabel="Population", xstep=4, ystep=10, through_zero=False, arrows=False)
        c.hline(EQ[0], stroke="#A9C0DD", dash="2,4")
        c.hline(EQ[1], stroke="#E0B4B4", dash="2,4")
        c.polyline([(t, x) for t, x, _ in series], stroke=BLUE, width=2.4)
        c.polyline([(t, y) for t, _, y in series], stroke=RED, width=2.4)
        c.legend([("prey $x$", BLUE, ""), ("predator $y$", RED, "")], at=(c.ox + 10, c.oy - c.h + 4), size=12)

        # ------------------------------------------------ phase plane
        diag.text("**Phase plane: closed orbits around the equilibrium**", size=14).at(660, 396, anchor="top_left")
        d = Plot(diag, x=(0, x_max), y=(0, y_max), origin=(660, 690), size=(420, 220))
        d.grid(xstep=10, ystep=5)
        d.axes(xlabel="Prey $x$", ylabel="Predator $y$", xstep=10, ystep=5, through_zero=False, arrows=False)
        d.vline(EQ[0], stroke=AMBER)
        d.hline(EQ[1], stroke=AMBER)
        for s in starts:
            d.orbit(lv, s, t_back=0.0, t_fwd=period(s), arrows=(0.2, 0.7), steps=800, stroke=GREEN, width=2.0, head=9.0)
        d.dot(*EQ, radius=4.0)
        d.label(x_max, EQ[1], "$dx/dt = 0$", size=11, anchor="bottom_right", dy=-3, color=AMBER)
        d.label(EQ[0], y_max, "$dy/dt = 0$", size=11, anchor="top_left", dx=5, dy=4, color=AMBER)

        diag.caption(
            "**Figure 10:** Left: unchecked exponential growth versus logistic growth, where the rate is greatest at $N = K/2$. Right: Lotka-Volterra cycles; the predator peak\n"
            "lags the prey peak, and the phase-plane orbits are closed curves around $(g/d,\\ a/b)$ (amber lines are the nullclines, meeting at the equilibrium)",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "10_population_dynamics")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
