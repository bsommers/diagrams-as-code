"""Simply supported beam with an off-centre point load: reactions, shear and moment.

Statics for span $L = 6$ m and load $P = 24$ kN at $a = 2$ m from the left support:
$R_A = P(L-a)/L$, $R_B = Pa/L$, then $V(x)$ and $M(x)$ by sections. All
numbers in the figure are computed from those expressions.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

L, A, P = 6.0, 2.0, 24.0
RED, BLUE, GREEN, INK = "#9C2F2F", "#1F2F57", "#2E6B3F", "#111111"


def shear(x: float) -> float:
    ra = P * (L - A) / L
    return ra if x < A else ra - P


def moment(x: float) -> float:
    ra = P * (L - A) / L
    return ra * x if x <= A else ra * x - P * (x - A)


def diagram() -> Diagram:
    ra, rb = P * (L - A) / L, P * A / L
    mmax = moment(A)
    ox, wd = 130.0, 520.0
    with Diagram("Beam shear and moment", theme="paper") as diag:
        # Free-body sketch of the beam.
        by = 150.0
        sx = lambda x: ox + x / L * wd
        diag.polygon([(sx(0), by), (sx(L), by), (sx(L), by + 14), (sx(0), by + 14)],
                     style=Style(fill="#DCE6F2", stroke=INK, stroke_width=1.8), z=0)
        for xp, kind in ((0, "pin"), (L, "roller")):
            x = sx(xp)
            diag.polygon([(x, by + 14), (x - 14, by + 36), (x + 14, by + 36)],
                         style=Style(fill="#EEF0F4", stroke=INK, stroke_width=1.4), z=0)
            if kind == "roller":
                diag.polygon([(x - 12, by + 36), (x + 12, by + 36), (x + 12, by + 42), (x - 12, by + 42)],
                             style=Style(fill="#EEF0F4", stroke=INK, stroke_width=1.0), z=0)
            else:
                diag.path(f"M {x - 20:.1f} {by + 36:.1f} h 40", style=Style(fill="none", stroke=INK, stroke_width=1.6))
        diag.connect((sx(A), by - 70), (sx(A), by), routing="direct", width=2.6, color=RED, head="stealth")
        diag.text(f"$P = {P:g}$ kN", size=14, color=RED).at(sx(A) + 12, by - 56, anchor="left_center")
        diag.connect((sx(0), by + 90), (sx(0), by + 44), routing="direct", width=2.6, color=BLUE, head="stealth")
        diag.connect((sx(L), by + 90), (sx(L), by + 44), routing="direct", width=2.6, color=BLUE, head="stealth")
        diag.text(f"$R_A = {ra:.0f}$ kN", size=14, color=BLUE).at(sx(0) + 12, by + 74, anchor="left_center")
        diag.text(f"$R_B = {rb:.0f}$ kN", size=14, color=BLUE).at(sx(L) - 12, by + 74, anchor="right_center")
        diag.text(f"$a = {A:g}$ m", size=12).at(sx(A / 2), by - 14, anchor="bottom_center")
        diag.text(f"$L = {L:g}$ m", size=12).at(sx(L / 2), by + 30, anchor="center")

        # Shear diagram.
        v = Plot(diag, x=(0, L), y=(-16, 20), origin=(ox, 540.0), size=(wd, 160.0))
        v.grid(xstep=1, ystep=10)
        v.axes(xlabel="$x$ (m)", ylabel="$V$ (kN)", xstep=1, ystep=10, size=11, xlabels=False)
        v.area(lambda x: shear(x) if x < A else 0.0, 0, A, fill="#DCE6F2")
        v.area(lambda x: shear(x) if x >= A else 0.0, A, L, fill="#F2DADA")
        v.polyline([(0, 0), (0, ra), (A, ra), (A, ra - P), (L, ra - P), (L, 0)], stroke=BLUE, width=2.2)
        v.label(A / 2, ra, f"$+{ra:.0f}$", dy=-10, anchor="bottom_center", size=12, color=BLUE)
        v.label((A + L) / 2, ra - P, f"$-{rb:.0f}$", dy=14, anchor="top_center", size=12, color=BLUE)

        # Moment diagram.
        m = Plot(diag, x=(0, L), y=(0, 40), origin=(ox, 790.0), size=(wd, 150.0))
        m.grid(xstep=1, ystep=10)
        m.axes(xlabel="$x$ (m)", ylabel="$M$ (kN$\\cdot$m)", xstep=1, ystep=10, size=11)
        m.area(moment, 0, L, fill="#E3EDE3")
        m.polyline([(0, 0), (A, mmax), (L, 0)], stroke=GREEN, width=2.2)
        m.dot(A, mmax, radius=3.5, label=f"$M_{{max}} = R_A a = {mmax:.0f}$ kN$\\cdot$m",
              dx=10, dy=-4, anchor="bottom_left", size=13)
        m.vline(A, stroke="#8A8A8A", dash="3,3")
        diag.text("$V = R_A$ for $x < a$, $V = R_A - P$ for $x > a$;  $M = R_A x$ for $x \\leq a$, "
                  "$M = R_A x - P(x - a)$ for $x > a$.", size=12).at(ox, 850, anchor="left_center")
        diag.caption(
            "**Figure 3:** Simply supported beam under a point load, with computed shear-force and bending-moment diagrams",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/engineering") -> Path:
    return render_all(diagram(), output_dir, "03_beam_shear_moment")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/engineering")
    build_diagram(dest)
