"""Refraction at a plane interface: two panels governed by Snell's law.

Panel (a) is air to glass, where the ray bends towards the normal; panel (b) is
glass to air, where it bends away. Every direction is computed from
$n_1 \\sin\\theta_1 = n_2 \\sin\\theta_2$ and the law of reflection; the figure also
reports the critical angle of the glass-air interface.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#111111"
INCIDENT, REFLECTED, REFRACTED = "#1F2F57", "#8A8F9C", "#9C2F2F"
N_AIR, N_GLASS = 1.00, 1.50
HALF, DEPTH, RAY = 220.0, 190.0, 170.0
FINE = Style(fill="none", stroke="#222222", stroke_width=0.9)


def snell(n1: float, n2: float, theta1: float):
    """The refraction angle in radians, or None past the critical angle."""
    s = n1 * math.sin(theta1) / n2
    return math.asin(s) if abs(s) <= 1 else None


def panel(diag: Diagram, cx: float, cy: float, n1: float, n2: float, theta1_deg: float,
          names: tuple[str, str], tag: str) -> None:
    th1 = math.radians(theta1_deg)
    th2 = snell(n1, n2, th1)
    assert th2 is not None
    # Shade the denser medium.
    lower_dense = n2 > n1
    y0, y1 = (cy, cy + DEPTH) if lower_dense else (cy - DEPTH, cy)
    diag.polygon([(cx - HALF, y0), (cx + HALF, y0), (cx + HALF, y1), (cx - HALF, y1)],
                 style=Style(fill="#E4EBF5", stroke="none"), z=-2)
    diag.polygon([(cx - HALF, cy - DEPTH), (cx + HALF, cy - DEPTH), (cx + HALF, cy + DEPTH), (cx - HALF, cy + DEPTH)],
                 style=Style(fill="none", stroke=INK, stroke_width=1.0), z=-1)
    diag.polyline([(cx - HALF, cy), (cx + HALF, cy)], style=Style(stroke=INK, stroke_width=1.6))
    diag.polyline([(cx, cy - DEPTH + 10), (cx, cy + DEPTH - 10)],
                  style=Style(stroke="#555555", stroke_width=0.9, dash="5,4"), obstacle=False)
    diag.text("normal", size=11, color="#555555").at(cx + 5, cy - DEPTH + 12, anchor="top_left")

    inc = (cx - RAY * math.sin(th1), cy - RAY * math.cos(th1))
    ref = (cx + RAY * 0.85 * math.sin(th1), cy - RAY * 0.85 * math.cos(th1))
    rfr = (cx + RAY * math.sin(th2), cy + RAY * math.cos(th2))
    diag.connect(inc, (cx, cy), routing="direct", width=2.0, color=INCIDENT, head="stealth")
    diag.connect((cx, cy), ref, routing="direct", width=1.3, color=REFLECTED, head="stealth", style="dashed")
    diag.connect((cx, cy), rfr, routing="direct", width=2.0, color=REFRACTED, head="stealth")

    def arc(r, ang, up, side, label, color, size=14):
        """An arc from the normal through ``ang`` on one side, with a label just outside it."""
        ny = -1 if up else 1
        sx = side
        p0 = (cx, cy + ny * r)
        p1 = (cx + sx * r * math.sin(ang), cy + ny * r * math.cos(ang))
        sweep = 1 if (sx * ny) < 0 else 0
        diag.path(f"M {p0[0]:.2f} {p0[1]:.2f} A {r} {r} 0 0 {sweep} {p1[0]:.2f} {p1[1]:.2f}",
                  style=Style(fill="none", stroke=color, stroke_width=1.1))
        mid = ang / 2
        diag.text(label, size=size, color=color).at(cx + sx * (r + 20) * math.sin(mid),
                                                    cy + ny * (r + 20) * math.cos(mid), anchor="center")

    arc(62, th1, True, -1, "$\\theta_1$", INCIDENT)
    arc(88, th1, True, 1, "$\\theta_1$", "#555555")
    arc(62, th2, False, 1, "$\\theta_2$", REFRACTED)

    top_name, bottom_name = names
    diag.text(f"{top_name}\n$n_1 = {n1:.2f}$", size=13).at(cx - HALF + 12, cy - DEPTH + 34, anchor="top_left")
    diag.text(f"{bottom_name}\n$n_2 = {n2:.2f}$", size=13).at(cx - HALF + 12, cy + DEPTH - 12, anchor="bottom_left")
    diag.text(tag, size=14).at(cx - HALF, cy - DEPTH - 8, anchor="bottom_left")
    diag.text(
        f"$n_1 \\sin\\theta_1 = n_2 \\sin\\theta_2$\n"
        f"${n1:.2f} \\sin {theta1_deg:g}^\\circ = {n2:.2f} \\sin {math.degrees(th2):.1f}^\\circ$",
        size=13, align="center",
    ).at(cx, cy + DEPTH + 16, anchor="top_center")


def diagram() -> Diagram:
    crit = math.degrees(math.asin(N_AIR / N_GLASS))
    with Diagram("Refraction at an interface", theme="paper") as diag:
        panel(diag, 250, 250, N_AIR, N_GLASS, 50.0, ("air", "glass"), "**(a)** air to glass: bends towards the normal")
        panel(diag, 250 + 2 * HALF + 70, 250, N_GLASS, N_AIR, 35.0, ("glass", "air"),
              "**(b)** glass to air: bends away from the normal")
        diag.text(
            f"Critical angle for glass to air: $\\theta_c$ = arcsin($n_2 / n_1$) = ${crit:.1f}^\\circ$; beyond it the ray is totally reflected.",
            size=12, font="serif", italic=True,
        ).at(250 + HALF + 35, 250 + DEPTH + 80, anchor="top_center")
        diag.caption("**Figure 5:** Refraction and partial reflection at a plane interface, with angles from Snell's law",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/physics") -> Path:
    return render_all(diagram(), output_dir, "05_refraction_snell")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/physics")
    build_diagram(dest)
