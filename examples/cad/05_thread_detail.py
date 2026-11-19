"""ISO metric thread M10 x 1.5 in axial section, drawn from the standard profile.

Pitch P = 1.5 mm and the 60 degree flank angle fix everything: fundamental
height H = 0.866 P, external minor diameter d3 = d - 1.2269 P, pitch diameter
d2 = d - 0.6495 P, internal minor diameter D1 = d - 1.0825 P. Bolt crests are truncated by P/8 and nut crests by P/4 (ISO 68-1).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

D, P = 10.0, 1.5
H = math.sqrt(3) / 2 * P
D2 = D - 0.6495 * P
D3 = D - 1.2269 * P
D1 = D - 1.0825 * P
T30 = math.tan(math.radians(30))
S = 150.0          # px per mm
X0, R_REF = 110.0, 3.5
Y_REF = 400.0
N = 3
INK = "#1F2F57"


def X(x):
    return X0 + x * S


def Y(r):
    return Y_REF - (r - R_REF) * S


def screw_profile():
    r1, r0 = D / 2, D3 / 2
    f = (r1 - r0) * T30
    pts = []
    for i in range(-1, N + 1):
        c = i * P
        pts += [(c - P / 16, r1), (c + P / 16, r1), (c + P / 16 + f, r0), (c + P - P / 16 - f, r0)]
    return pts


def nut_profile():
    r1, r0 = D / 2, D1 / 2
    f = (r1 - r0) * T30
    pts = []
    for i in range(-1, N + 1):
        c = i * P + P / 2  # tooth tip centred over the screw root
        pts += [(c - P / 8 + 0 - P / 16 * 0 - P / 16, r0), (c + P / 8 + P / 16 - P / 16 * 0, r0)]
        pts += [(c + P / 8 + P / 16 + f, r1), (c + P - P / 8 - P / 16 - f, r1)]
    return pts


def diagram() -> Diagram:
    with Diagram("Thread detail M10 x 1.5", theme="paper") as diag:
        k = Draft(diag)
        xmin, xmax = 0.0, N * P
        sp = [(x, r) for x, r in screw_profile()]
        sp = [p for p in sp if xmin - P <= p[0] <= xmax + P]
        # Clip to the drawn window with straight vertical sides.
        win0, win1 = X(0.0), X(xmax)
        screw_px = [(X(x), Y(r)) for x, r in sp]
        screw_poly = [(win0 - 0, Y(3.6))] + screw_px + [(X(sp[-1][0]), Y(3.6))]
        np_ = nut_profile()
        nut_px = [(X(x), Y(r)) for x, r in np_]
        nut_poly = [(X(np_[0][0]), Y(5.7))] + nut_px + [(X(np_[-1][0]), Y(5.7))]

        def clip(poly):  # keep inside [win0, win1] horizontally by clamping x
            return [(min(max(x, win0), win1), y) for x, y in poly]

        screw_poly, nut_poly = clip(screw_poly), clip(nut_poly)
        diag.polygon(screw_poly, style=Style(fill="#DCE6F2", stroke="none"), z=-3)
        diag.polygon(nut_poly, style=Style(fill="#F1E4D2", stroke="none"), z=-3)
        k.hatch(screw_poly, angle=45, gap=9)
        k.hatch(nut_poly, angle=135, gap=9, stroke="#7A5A2B")
        k.d.path("M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in screw_px if win0 - 0.01 <= x <= win1 + 0.01),
                 style=Style(fill="none", stroke=INK, stroke_width=2.2))
        k.d.path("M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in nut_px if win0 - 0.01 <= x <= win1 + 0.01),
                 style=Style(fill="none", stroke="#7A5A2B", stroke_width=2.2))
        # Fundamental (sharp) V on the second screw tooth, dashed, with the 60 degree angle.
        apex_r = D3 / 2 + H * (1.0 - 0.0) * 1.0 - H + H  # crest apex of the sharp-V screw profile
        apex_r = D3 / 2 + (D / 2 - D3 / 2) + H / 8
        cx = 1 * P
        ax, ay = X(cx), Y(apex_r)
        k.hidden_line([(X(cx - (apex_r - D3 / 2) * T30), Y(D3 / 2)), (ax, ay), (X(cx + (apex_r - D3 / 2) * T30), Y(D3 / 2))])
        diag.path(f"M {ax - 14:.1f} {ay + 24:.1f} A 28 28 0 0 0 {ax + 14:.1f} {ay + 24:.1f}",
                  style=Style(fill="none", stroke=INK, stroke_width=0.9))
        diag.text("$60^\\circ$", size=13).at(ax, ay - 16, anchor="center")
        # Reference diameters across the profile.
        right = X(xmax) + 22
        for r, label in ((D / 2, f"major $d = {D:.3f}$"), (D2 / 2, f"pitch $d_2 = {D2:.3f}$"),
                         (D3 / 2, f"minor $d_3 = {D3:.3f}$")):
            k.centerline((X(0) - 20, Y(r)), (right, Y(r)))
            diag.text(label, size=12).at(right + 8, Y(r), anchor="left_center")
        # Pitch and thread depth.
        k.dimension((X(2 * P), Y(D / 2)), (X(3 * P), Y(D / 2)), f"$P = {P:g}$", offset=-64, side=1)
        k.dimension((X(0) - 30, Y(D3 / 2)), (X(0) - 30, Y(D / 2)), "", offset=34, side=-1)
        diag.text(f"$h_3 = {(D - D3) / 2:.3f}$", size=11).at(X(0) - 90, Y(4.55), anchor="right_center")
        diag.text("nut (internal thread)", size=12, color="#7A5A2B").at(X(xmax) + 30, Y(5.5), anchor="left_center")
        diag.text("bolt (external thread)", size=12).at(X(xmax) + 30, Y(3.8), anchor="left_center")
        diag.text(f"M10 $\\times$ 1.5: $H = 0.866P = {H:.3f}$ mm; bolt crest flat $P/8 = {P / 8:.3f}$, nut crest flat $P/4 = {P / 4:.3f}$ (mm); nut minor $D_1 = {D1:.3f}$",
                  size=12).at(X(0) - 60, 470, anchor="left_center")
        diag.caption(
            "**Figure 5:** Axial section of an ISO metric M10 $\\times$ 1.5 thread showing the 60 degree flank angle, pitch and the major, pitch and minor diameters",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/cad") -> Path:
    return render_all(diagram(), output_dir, "05_thread_detail")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/cad")
    build_diagram(dest)
