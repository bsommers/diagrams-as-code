"""Mean-variance frontier of three assets, the tangency portfolio and the capital market line."""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
AMBER = "#8A5A00"
ASSETS = [("A", 5.0, 10.0), ("B", 9.0, 18.0), ("C", 13.0, 26.0)]  # name, mean %, volatility %
CORR = {(0, 1): 0.3, (0, 2): 0.1, (1, 2): 0.4}
RF = 2.0  # risk-free rate, %


def covariance() -> list[list[float]]:
    n = len(ASSETS)
    cov = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            rho = 1.0 if i == j else CORR[(min(i, j), max(i, j))]
            cov[i][j] = rho * ASSETS[i][2] * ASSETS[j][2]
    return cov


def solve(a: list[list[float]], b: list[float]) -> list[float]:
    """Solve a x = b by Gaussian elimination with partial pivoting."""
    n = len(b)
    m = [row[:] + [v] for row, v in zip(a, b)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[piv] = m[piv], m[c]
        for r in range(c + 1, n):
            f = m[r][c] / m[c][c]
            m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    x = [0.0] * n
    for r in reversed(range(n)):
        x[r] = (m[r][n] - sum(m[r][k] * x[k] for k in range(r + 1, n))) / m[r][r]
    return x


def model():
    cov = covariance()
    mu = [a[1] for a in ASSETS]
    ones = [1.0] * len(mu)
    inv1, invmu = solve(cov, ones), solve(cov, mu)
    A = sum(inv1)
    B = sum(x * m for x, m in zip(inv1, mu))
    C = sum(x * m for x, m in zip(invmu, mu))
    d = A * C - B * B

    def sigma(m: float) -> float:
        return math.sqrt((A * m * m - 2 * B * m + C) / d)

    z = solve(cov, [m - RF for m in mu])  # tangency weights, proportional to cov^-1 (mu - rf)
    w = [x / sum(z) for x in z]
    mu_t = sum(x * m for x, m in zip(w, mu))
    sig_t = math.sqrt(sum(w[i] * cov[i][j] * w[j] for i in range(3) for j in range(3)))
    return sigma, B / A, (sig_t, mu_t), w


def diagram() -> Diagram:
    sigma, mu_gmv, (sig_t, mu_t), w = model()
    sharpe = (mu_t - RF) / sig_t

    def sigma_inv(s: float) -> float:
        """Return of the efficient portfolio with volatility s (bisection on the upper branch)."""
        lo, hi = mu_gmv, 60.0
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if sigma(mid) < s else (lo, mid)
        return lo
    with Diagram("Efficient frontier", theme="paper") as diag:
        p = Plot(diag, x=(0, 32), y=(0, 18), origin=(100, 360), size=(520, 300))
        p.grid(xstep=4, ystep=2)
        p.axes(xlabel="Risk $\\sigma$ (%)", ylabel="Expected return $\\mu$ (%)", xstep=4, ystep=2, through_zero=False)
        # Whole minimum-variance parabola, dashed below the global minimum-variance portfolio.
        lower = [(sigma(m), m) for m in [mu_gmv - i * 0.05 for i in range(0, 80)]]
        upper = [(sigma(m), m) for m in [mu_gmv + i * 0.05 for i in range(0, 300)]]
        p.polyline(lower, stroke="#9AA3B5", width=1.8, dash="5,4")
        p.polyline(upper, stroke=INK, width=2.4)
        # Capital market line from the risk-free asset through the tangency portfolio.
        p.line((0, RF), (32, RF + sharpe * 32), stroke=AMBER, width=1.8)
        p.dot(0, RF, radius=3.5)
        p.label(0, RF, "risk-free $r_f$", size=12, anchor="top_left", dx=8, dy=8)
        p.dot(sig_t, mu_t, radius=4.5)
        p.label(sig_t, mu_t, f"tangency portfolio $T$\n($\\sigma = {sig_t:.1f}$, $\\mu = {mu_t:.1f}$)", size=12,
                anchor="top_left", dx=10, dy=10)
        p.dot(sigma(mu_gmv), mu_gmv, radius=3.5)
        p.label(sigma(mu_gmv), mu_gmv, "minimum variance", size=12, anchor="bottom_right", dx=-6, dy=-6)
        for name, m, s in ASSETS:
            p.dot(s, m, radius=3.2)
            left = name == "A"
            p.label(s, m, name, size=13, anchor="right_center" if left else "top_left", dx=-8 if left else 7,
                    dy=2 if left else 3)
        p.label(25, RF + sharpe * 25, "capital market line", size=12, anchor="bottom_right", dy=-8, dx=-4, color=AMBER)
        p.label(28.5, 10.2, "efficient frontier", size=12, anchor="top_center")
        diag.connect(p.px(28.5, 10.0), p.px(28.5, sigma_inv(28.5)), routing="direct", width=0.8, head="stealth")
        wtxt = ", ".join(f"{n} {x:.0%}" for (n, _, _), x in zip(ASSETS, w))
        diag.caption(
            "**Figure 6:** Efficient frontier of three risky assets (means 5, 9, 13%; volatilities 10, 18, 26%), computed from the "
            "mean-variance model.\n"
            f"The capital market line leaves $r_f = {RF:g}$% and touches the frontier at the tangency portfolio "
            f"({wtxt}), with Sharpe ratio {sharpe:.2f}.",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/finance") -> Path:
    return render_all(diagram(), output_dir, "06_efficient_frontier")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/finance"))
