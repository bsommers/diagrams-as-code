"""Energy levels of the hydrogen atom with the Lyman and Balmer transitions.

Levels follow the Bohr formula $E_n = -13.606\\,\\mathrm{eV} / n^2$ on a linear
energy scale. Each transition arrow drops from level $n$ to the series limit
level ($n = 1$ for Lyman, $n = 2$ for Balmer), and its wavelength is computed
from $\\lambda = hc / \\Delta E$ with $hc = 1239.84$ eV nm. The Balmer arrows are
tinted to suggest the colour of each visible line.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

E1, HC = 13.606, 1239.84      # ionisation energy (eV) and h c (eV nm)
LEVELS = [1, 2, 3, 4, 5, 6]
X0, X1 = 110.0, 700.0         # level lines run from X0 to X1
Y_TOP, PX_PER_EV = 110.0, 28.0
INK = "#111111"
LYMAN = "#5B3A8A"
BALMER = {3: "#D62828", 4: "#1A9DB5", 5: "#3B4CC0", 6: "#7A2C9E"}  # H-alpha .. H-delta


def energy(n: int) -> float:
    return -E1 / n ** 2


def y_of(e: float) -> float:
    return Y_TOP - e * PX_PER_EV


def wavelength(n_hi: int, n_lo: int) -> float:
    return HC / (energy(n_hi) - energy(n_lo))


def spread(ys: list[float], gap: float) -> list[float]:
    """Push labels apart (top to bottom) so no two are closer than ``gap``."""
    out = list(ys)
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + gap)
    return out


def diagram() -> Diagram:
    with Diagram("Hydrogen energy levels", theme="paper") as diag:
        # Energy axis with ticks every 2 eV.
        ax = 60.0
        diag.connect((ax, y_of(-14.4)), (ax, y_of(0.9)), routing="direct", width=1.2, head="stealth")
        ticks = []
        for ev in range(0, -15, -2):
            y = y_of(ev)
            ticks.append(f"M {ax - 4} {y:.2f} h 8")
            diag.text(f"{ev}".replace("-", "−"), size=11).at(ax - 9, y, anchor="right_center")
        diag.path(" ".join(ticks), style=Style(fill="none", stroke=INK, stroke_width=0.9))
        diag.text("$E$ (eV)", size=13).at(ax, y_of(0.9) - 12, anchor="bottom_center")

        # Level lines.
        diag.polyline([(X0, y_of(0)), (X1, y_of(0))], style=Style(stroke=INK, stroke_width=1.4, dash="6,4"))
        for n in LEVELS:
            diag.polyline([(X0, y_of(energy(n))), (X1, y_of(energy(n)))], style=Style(stroke=INK, stroke_width=1.8))

        # Level labels at the right, fanned out with leaders where the levels crowd together.
        names = [(y_of(0), "$n = \\infty$,  $0$ eV  (ionised)")]
        names += [(y_of(energy(n)), f"$n = {n}$,  ${energy(n):.2f}$ eV".replace("$-", "$−")) for n in reversed(LEVELS)]
        placed = spread([y for y, _ in names], 19.0)
        for (y, text), yl in zip(names, placed):
            diag.polyline([(X1, y), (X1 + 22, yl)], style=Style(stroke="#888888", stroke_width=0.7), obstacle=False)
            diag.text(text, size=12).at(X1 + 26, yl, anchor="left_center")

        # Lyman series: n -> 1, ultraviolet.
        n1 = y_of(energy(1))
        for k, n in enumerate(range(2, 7)):
            x = X0 + 35 + 52 * k
            diag.connect((x, y_of(energy(n))), (x, n1), routing="direct", width=1.8, color=LYMAN, head="stealth")
            diag.text(f"{wavelength(n, 1):.1f} nm", size=11, color=LYMAN).at(x, n1 + 8, anchor="top_center")
        diag.text("**Lyman series** ($n \\to 1$), ultraviolet", size=13, color=LYMAN).at(
            X0 + 35 + 52 * 2, y_of(energy(2)) - 8 - 150, anchor="bottom_center")

        # Balmer series: n -> 2, visible.
        n2 = y_of(energy(2))
        for k, n in enumerate(range(3, 7)):
            x = 430 + 62 * k
            diag.connect((x, y_of(energy(n))), (x, n2), routing="direct", width=2.2, color=BALMER[n], head="stealth")
            diag.text(f"{wavelength(n, 2):.1f} nm", size=11, color=BALMER[n]).at(x, n2 + 8, anchor="top_center")
        diag.text("**Balmer series** ($n \\to 2$), visible", size=13, color=BALMER[3]).at(
            430 + 62 * 1.5, y_of(energy(2)) - 8 - 150, anchor="bottom_center")

        diag.text("$E_n = -13.606\\,\\mathrm{eV} / n^2$,   $\\lambda = hc / (E_i - E_f)$", size=13).at(
            (X0 + X1) / 2, n1 + 50, anchor="top_center")
        diag.caption("**Figure 10:** Energy levels of hydrogen with the Lyman and Balmer series, wavelengths from the level differences",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/physics") -> Path:
    return render_all(diagram(), output_dir, "10_hydrogen_energy_levels")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/physics")
    build_diagram(dest)
