"""Three feature operations: extrude, revolve and sweep (profile to solid).

Each panel shows the 2D sketch, the operation and the resulting solid in
isometric view (x to the lower right, z to the lower left, y up). Faces,
ellipses and tube sections are computed from the stated sizes in millimetres.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
SC = 2.3  # px per mm
PANEL = 440.0


def make_iso(ox, oy):
    def iso(x, y, z):
        return (ox + (x - z) * C30 * SC, oy + (-y + (x + z) * S30) * SC)
    return iso


def arrow(diag, a, b, color=INK):
    ux, uy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    diag.path(f"M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}", style=Style(fill="none", stroke=color, stroke_width=1.8))
    px, py = -uy, ux
    tip = b
    diag.path(f"M {tip[0]:.1f} {tip[1]:.1f} L {tip[0] - ux * 11 + px * 5:.1f} {tip[1] - uy * 11 + py * 5:.1f} "
              f"L {tip[0] - ux * 11 - px * 5:.1f} {tip[1] - uy * 11 - py * 5:.1f} Z",
              style=Style(fill=color, stroke=color, stroke_width=0.5))


def extrude(diag, k, x0):
    L = [(0, 0), (36, 0), (36, 12), (12, 12), (12, 30), (0, 30)]  # profile in the x-z plane
    h = 22.0
    # 2D sketch.
    s2 = 2.6
    sk = [(x0 + 20 + x * s2, 210 + z * s2) for x, z in L]
    diag.polygon(sk, style=Style(fill="#E6EEF8", stroke=INK, stroke_width=2.0))
    k.dimension(sk[0], sk[1], "$36$", offset=-22, side=1)
    diag.text("Sketch", size=12).at(x0 + 20 + 18 * s2, 300, anchor="center")
    arrow(diag, (x0 + 130, 250), (x0 + 168, 250))
    diag.text(f"extrude\n{h:g} mm", size=11).at(x0 + 149, 280, anchor="center")
    iso = make_iso(x0 + 300, 300)
    area = 0.5 * sum(L[i][0] * L[(i + 1) % len(L)][1] - L[(i + 1) % len(L)][0] * L[i][1] for i in range(len(L)))
    sign = 1 if area > 0 else -1
    faces = []
    for i in range(len(L)):
        (ax, az), (bx, bz) = L[i], L[(i + 1) % len(L)]
        nx, nz = sign * (bz - az), -sign * (bx - ax)
        if nx + nz > 0:  # faces the viewer
            quad = [iso(ax, 0, az), iso(bx, 0, bz), iso(bx, h, bz), iso(ax, h, az)]
            faces.append(((ax + bx + az + bz) / 2, quad, "#B9C9DE" if abs(nx) > abs(nz) else "#D3DEEC"))
    for _, quad, col in sorted(faces, key=lambda f: f[0]):
        diag.polygon(quad, style=Style(fill=col, stroke=INK, stroke_width=1.6))
    diag.polygon([iso(x, h, z) for x, z in L], style=Style(fill="#EAF0F8", stroke=INK, stroke_width=1.8))
    diag.text("1  Extrude", size=15).at(x0 + 160, 60, anchor="center")
    diag.text(f"profile area $= {abs(area):g}$ mm$^2$, volume $= {abs(area) * h:,.0f}$ mm$^3$".replace(",", "\\,"), size=11).at(x0 + 160, 420, anchor="center")


def ellipse_pts(iso, r, y, n=40):
    return [iso(r * math.cos(i / n * math.tau), y, r * math.sin(i / n * math.tau)) for i in range(n)]


def revolve(diag, k, x0):
    bands = [(0, 8, 16, 16), (8, 34, 9, 9), (34, 42, 9, 5)]  # y0, y1, r0, r1
    # 2D half profile, axis on the left.
    s2 = 3.0
    ax = x0 + 40
    base_y = 330.0
    prof = [(ax, base_y), (ax + 16 * s2, base_y), (ax + 16 * s2, base_y - 8 * s2), (ax + 9 * s2, base_y - 8 * s2),
            (ax + 9 * s2, base_y - 34 * s2), (ax + 5 * s2, base_y - 42 * s2), (ax, base_y - 42 * s2)]
    diag.polygon(prof, style=Style(fill="#E6EEF8", stroke=INK, stroke_width=2.0))
    k.centerline((ax, base_y + 14), (ax, base_y - 42 * s2 - 14))
    diag.text("Sketch + axis", size=12).at(ax + 30, base_y - 42 * s2 - 30, anchor="center")
    k.dimension((ax, base_y), (ax + 16 * s2, base_y), "$16$", offset=26, side=1)
    arrow(diag, (x0 + 130, 250), (x0 + 168, 250))
    diag.text("revolve\n$360^\\circ$", size=11).at(x0 + 149, 280, anchor="center")
    iso = make_iso(x0 + 300, 330)
    for y0, y1, r0, r1 in bands:
        low = ellipse_pts(iso, r0, y0)
        high = ellipse_pts(iso, r1, y1)
        # Silhouette: extreme left/right points of both ellipses, front arcs between them.
        lo_front = [p for p in sorted(low, key=lambda p: p[0])]
        poly = []
        # Outline path: left tangent, bottom front arc, right tangent, top back arc.
        li, ri = min(range(len(low)), key=lambda i: low[i][0]), max(range(len(low)), key=lambda i: low[i][0])
        n = len(low)
        # front arc = points with larger screen y between li and ri.
        def arc(pts, a, b):
            seq = [pts[(a + j) % n] for j in range(0, (b - a) % n + 1)]
            return seq if sum(p[1] for p in seq) > sum(p[1] for p in [pts[(b + j) % n] for j in range(0, (a - b) % n + 1)]) else \
                [pts[(a - j) % n] for j in range(0, (a - b) % n + 1)]
        bottom = arc(low, li, ri)
        top = arc(high, ri, li)
        poly = bottom + top
        diag.polygon(poly, style=Style(fill="#C9D6E8", stroke=INK, stroke_width=1.6))
        diag.polygon(high, style=Style(fill="#EAF0F8", stroke=INK, stroke_width=1.6))
    k.centerline(iso(0, -6, 0), iso(0, 52, 0))
    diag.text("2  Revolve", size=15).at(x0 + 160, 60, anchor="center")
    vol = math.pi * (16 ** 2 * 8 + 9 ** 2 * 26 + (8 / 3) * (81 + 45 + 25))
    diag.text(f"volume $= {vol:,.0f}$ mm$^3$ (Pappus / disc sum)".replace(",", "\\,"), size=11).at(x0 + 160, 420, anchor="center")


def sweep(diag, k, x0):
    rho, Rb, lead = 5.0, 36.0, 34.0
    # 2D sketch: the circular profile and the path in plan.
    cx, cy = x0 + 50, 210
    diag.path(f"M {cx - rho * 4:.1f} {cy} a {rho * 4} {rho * 4} 0 1 0 {rho * 8} 0 a {rho * 4} {rho * 4} 0 1 0 {-rho * 8} 0",
              style=Style(fill="#E6EEF8", stroke=INK, stroke_width=2.0))
    diag.text("Profile $\\emptyset10$", size=12).at(cx, cy + 38, anchor="center")
    diag.path(f"M {cx - 30} {cy + 80} L {cx - 30} {cy + 105} A 40 40 0 0 0 {cx + 10} {cy + 145} L {cx + 40} {cy + 145}",
              style=Style(fill="none", stroke=INK, stroke_width=1.4, dash="6,3"))
    diag.text("Path", size=12).at(cx + 56, cy + 128, anchor="left_center")
    arrow(diag, (x0 + 130, 250), (x0 + 168, 250))
    diag.text("sweep\nalong path", size=11).at(x0 + 149, 280, anchor="center")
    iso = make_iso(x0 + 290, 300)
    pts = [(0.0, 0.0, lead + Rb + 12 - j) for j in range(0)]
    path = []
    for j in range(0, 21):
        path.append((0.0, 0.0, Rb + lead - lead * j / 20))
    for j in range(1, 31):
        a = math.radians(180 + 90 * j / 30)
        path.append((Rb + Rb * math.cos(a), 0.0, Rb + Rb * math.sin(a)))
    for j in range(1, 21):
        path.append((Rb + lead * j / 20, 0.0, 0.0))
    discs = []
    for i, p in enumerate(path):
        q0, q1 = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        t = (q1[0] - q0[0], q1[1] - q0[1], q1[2] - q0[2])
        tn = math.sqrt(sum(c * c for c in t))
        t = tuple(c / tn for c in t)
        nvec = (t[1] * 0 - t[2] * 1, 0.0, t[0] * 1)  # t x (0,1,0) = (-tz, 0, tx)
        ring = []
        for m in range(24):
            ph = m / 24 * math.tau
            ring.append(iso(p[0] + rho * math.cos(ph) * nvec[0], rho * math.sin(ph), p[2] + rho * math.cos(ph) * nvec[2]))
        discs.append((p[0] + p[2], i, ring))
    for _, i, ring in sorted(discs):
        end = i in (0, len(path) - 1)
        diag.polygon(ring, style=Style(fill="#C9D6E8" if not end else "#EAF0F8", stroke=INK if end else "#7F93B0",
                                       stroke_width=1.6 if end else 0.5))
    diag.text("3  Sweep", size=15).at(x0 + 160, 60, anchor="center")
    length = 2 * lead + math.pi * Rb / 2
    diag.text(f"path length $= {length:.1f}$ mm; volume $= {math.pi * rho ** 2 * length:,.0f}$ mm$^3$".replace(",", "\\,"),
              size=11).at(x0 + 160, 420, anchor="center")


def diagram() -> Diagram:
    with Diagram("Extrude, revolve and sweep", theme="paper") as diag:
        k = Draft(diag)
        extrude(diag, k, 0.0)
        revolve(diag, k, PANEL)
        sweep(diag, k, 2 * PANEL)
        for i in (1, 2):
            diag.path(f"M {i * PANEL - 12} 50 L {i * PANEL - 12} 440", style=Style(fill="none", stroke="#C5CBD8", stroke_width=0.8, dash="4,4"))
        diag.caption(
            "**Figure 8:** Feature operations turn a 2D profile into a solid by extruding it, revolving it about an axis or sweeping it along a path",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/cad") -> Path:
    return render_all(diagram(), output_dir, "08_extrude_revolve_sweep")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cad")
    build_diagram(dest)
