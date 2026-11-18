"""A pin-jointed truss solved by the method of joints.

Seven members and three support reactions (pin at A, roller at C) give ten
unknowns for the ten equilibrium equations of five joints. The equations
$\\sum F_x = 0$, $\\sum F_y = 0$ at every joint are assembled and solved by
Gaussian elimination; positive member force is tension.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

BAY, H = 4.0, 4.0 * math.sqrt(3) / 2        # metres; equilateral triangles
NODES = {"A": (0.0, 0.0), "B": (BAY, 0.0), "C": (2 * BAY, 0.0), "D": (BAY / 2, H), "E": (1.5 * BAY, H)}
MEMBERS = [("A", "B"), ("B", "C"), ("A", "D"), ("D", "B"), ("B", "E"), ("E", "C"), ("D", "E")]
LOADS = {"D": (0.0, -30.0), "E": (0.0, -10.0)}      # kN (x, y)
PX = 62.0                                           # pixels per metre
RED, BLUE, INK, GREY = "#9C2F2F", "#1F2F57", "#111111", "#666666"


def solve(a, b):
    """Gaussian elimination with partial pivoting for a square system."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


def member_forces():
    names = list(NODES)
    unknowns = len(MEMBERS) + 3                      # members, then Ax, Ay, Cy
    rows, rhs = [], []
    for j in names:
        rx, ry = [0.0] * unknowns, [0.0] * unknowns
        for i, (p, q) in enumerate(MEMBERS):
            if j in (p, q):
                o = q if j == p else p
                dx, dy = NODES[o][0] - NODES[j][0], NODES[o][1] - NODES[j][1]
                d = math.hypot(dx, dy)
                rx[i], ry[i] = dx / d, dy / d        # tension pulls the joint toward the other end
        if j == "A":
            rx[len(MEMBERS)], ry[len(MEMBERS) + 1] = 1.0, 1.0
        if j == "C":
            ry[len(MEMBERS) + 2] = 1.0
        fx, fy = LOADS.get(j, (0.0, 0.0))
        rows += [rx, ry]
        rhs += [-fx, -fy]
    x = solve(rows, rhs)
    return x[:len(MEMBERS)], x[len(MEMBERS):]


def diagram() -> Diagram:
    forces, (ax, ay, cy) = member_forces()
    ox, oy = 120.0, 400.0
    pt = {k: (ox + x * PX, oy - y * PX) for k, (x, y) in NODES.items()}
    with Diagram("Truss, method of joints", theme="paper") as diag:
        for (p, q), f in zip(MEMBERS, forces):
            col = BLUE if f > 1e-6 else RED if f < -1e-6 else GREY
            diag.polyline([pt[p], pt[q]], style=Style(stroke=col, stroke_width=4.0, fill="none"), z=0)
            mx, my = (pt[p][0] + pt[q][0]) / 2, (pt[p][1] + pt[q][1]) / 2
            kind = "T" if f > 0 else "C"
            side = {("A", "D"): (-1, 0), ("D", "B"): (1, 0), ("B", "E"): (1, 0), ("E", "C"): (1, 0),
                    ("A", "B"): (0, 1), ("B", "C"): (0, 1), ("D", "E"): (0, 1)}[(p, q)]
            anchor = "right_center" if side[0] < 0 else "left_center" if side[0] > 0 else "top_center"
            diag.text(f"${abs(f):.1f}$ kN ({kind})", size=13, color=col).at(
                mx + side[0] * 16, my + side[1] * 12, anchor=anchor)
        for k, (x, y) in pt.items():
            diag.polygon([(x + 7 * math.cos(2 * math.pi * i / 16), y + 7 * math.sin(2 * math.pi * i / 16)) for i in range(16)],
                         style=Style(fill="#FFFFFF", stroke=INK, stroke_width=1.6), z=2)
            dxl, dyl = {"A": (-18, -14), "B": (0, 20), "C": (18, -14), "D": (-20, -4), "E": (20, -4)}[k]
            diag.text(f"**{k}**", size=15).at(x + dxl, y + dyl, anchor="center")
        # Supports.
        for k, kind in (("A", "pin"), ("C", "roller")):
            x, y = pt[k]
            diag.polygon([(x, y + 7), (x - 16, y + 30), (x + 16, y + 30)],
                         style=Style(fill="#EEF0F4", stroke=INK, stroke_width=1.4), z=1)
            diag.path(f"M {x - 24:.1f} {y + 36:.1f} h 48" if kind == "roller" else f"M {x - 24:.1f} {y + 30:.1f} h 48",
                      style=Style(fill="none", stroke=INK, stroke_width=1.6))
        # Applied loads and reactions.
        for k, (fx, fy) in LOADS.items():
            x, y = pt[k]
            diag.connect((x, y - 8 - abs(fy) * 3.0), (x, y - 8), routing="direct", width=2.6, color=RED, head="stealth")
            diag.text(f"${abs(fy):g}$ kN", size=13, color=RED).at(x + 10, y - 8 - abs(fy) * 3.0, anchor="left_center")
        for k, (rx, ry) in (("A", (ax, ay)), ("C", (0.0, cy))):
            x, y = pt[k]
            diag.connect((x, y + 80), (x, y + 44), routing="direct", width=2.6, color="#2E6B3F", head="stealth")
            diag.text(f"$R_{k} = {ry:.1f}$ kN", size=13, color="#2E6B3F").at(x + 12, y + 70, anchor="left_center")
        diag.text(f"$A_x = {ax:.0f}$ kN", size=13, color="#2E6B3F").at(pt["A"][0] - 100, pt["A"][1] + 6, anchor="left_center")
        diag.text("Blue: tension (T). Red: compression (C). Equilateral bays of 4 m; "
                  "$\\sum F_x = \\sum F_y = 0$ at each joint.", size=12).at(ox, oy + 130, anchor="left_center")
        diag.caption(
            "**Figure 4:** Pin-jointed truss with member forces from the method of joints",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/engineering") -> Path:
    return render_all(diagram(), output_dir, "04_truss_method_of_joints")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/engineering")
    build_diagram(dest)
