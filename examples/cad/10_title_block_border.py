"""ISO-style drawing sheet: border, zone grid, title block, revision table and a part.

An A4 landscape sheet (297 x 210 mm) is laid out in sheet millimetres and
drawn at 3.2 px per mm. The L-bracket of Figures 1 and 2 is shown at 1:2 in
third angle. Every dimension value is the real part size, not the drawn one.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

K = 3.2           # px per sheet mm
OX, OY = 30.0, 30.0
SHEET_W, SHEET_H = 297.0, 210.0
LEFT, RIGHT, TOP, BOT = 20.0, 287.0, 10.0, 200.0   # inner frame (binding margin on the left)
INK = "#1F2F57"
M = 0.5           # drawing scale 1:2
W, D, H, T_, DH = 80.0, 50.0, 45.0, 10.0, 10.0


def P(x, y):
    return (OX + x * K, OY + y * K)


def rect(x0, y0, x1, y1):
    return [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]


def diagram() -> Diagram:
    thin = Style(fill="none", stroke=INK, stroke_width=1.0)
    with Diagram("Drawing sheet with title block", theme="paper") as diag:
        k = Draft(diag)
        diag.polygon(rect(0, 0, SHEET_W, SHEET_H), style=Style(fill="#FFFFFF", stroke="#8A93A6", stroke_width=1.0), z=-6)
        diag.polygon(rect(LEFT, TOP, RIGHT, BOT), style=Style(fill="none", stroke=INK, stroke_width=2.4), z=-5)
        # Zone grid: columns 1-6 along the top and bottom, rows A-D down both sides.
        cw, rh = (RIGHT - LEFT) / 6, (BOT - TOP) / 4
        for i in range(6):
            x = LEFT + i * cw
            if i:
                for y0, y1 in ((TOP - 5, TOP), (BOT, BOT + 5)):
                    k.d.path(f"M {P(x, y0)[0]:.1f} {P(x, y0)[1]:.1f} L {P(x, y1)[0]:.1f} {P(x, y1)[1]:.1f}", style=thin)
            for y in (TOP - 2.5, BOT + 2.5):
                diag.text(str(i + 1), size=9).at(*P(x + cw / 2, y), anchor="center")
        for j, letter in enumerate("ABCD"):
            y = TOP + j * rh
            if j:
                for x0, x1 in ((LEFT - 5, LEFT), (RIGHT, RIGHT + 5)):
                    k.d.path(f"M {P(x0, y)[0]:.1f} {P(x0, y)[1]:.1f} L {P(x1, y)[0]:.1f} {P(x1, y)[1]:.1f}", style=thin)
            for x in (LEFT - 2.5, RIGHT + 2.5):
                diag.text(letter, size=9).at(*P(x, y + rh / 2), anchor="center")
        # Title block (bottom right, 180 x 45 mm).
        tx, ty = RIGHT - 180.0, BOT - 45.0
        rows = [
            [("TITLE", "L-BRACKET", 130), ("DRAWING NO.", "CAD-0010", 50)],
            [("MATERIAL", "S235JR", 45), ("GENERAL TOL.", "ISO 2768-m", 45), ("SCALE", "1:2", 30), ("SHEET", "1 / 1", 30), ("UNITS", "mm", 30)],
            [("DRAWN", "BS  2026-03-02", 60), ("CHECKED", "AB  2026-03-04", 60), ("PROJECTION", None, 60)],
        ]
        for r, row in enumerate(rows):
            x = tx
            y0 = ty + r * 15.0
            for label, value, w in row:
                diag.polygon(rect(x, y0, x + w, y0 + 15.0), style=Style(fill="#FFFFFF", stroke=INK, stroke_width=1.4), z=-4)
                diag.text(label, size=8).at(*P(x + 1.5, y0 + 3.2), anchor="left_center")
                if value:
                    diag.text(value, size=13 if r == 0 else 11).at(*P(x + w / 2, y0 + 9.5), anchor="center")
                else:  # third-angle projection symbol
                    sx, sy = x + 12.0, y0 + 8.0
                    for rr in (2.6, 4.4):
                        c = P(sx, sy)
                        diag.path(f"M {c[0] - rr * K:.1f} {c[1]:.1f} a {rr * K:.1f} {rr * K:.1f} 0 1 0 {2 * rr * K:.1f} 0 "
                                  f"a {rr * K:.1f} {rr * K:.1f} 0 1 0 {-2 * rr * K:.1f} 0", style=Style(fill="none", stroke=INK, stroke_width=1.1))
                    diag.polygon([P(sx + 9, sy - 4.4), P(sx + 16, sy - 3.0), P(sx + 16, sy + 3.0), P(sx + 9, sy + 4.4)],
                                 style=Style(fill="none", stroke=INK, stroke_width=1.1))
                    k.centerline(P(sx - 6, sy), P(sx + 19, sy))
                    diag.text("THIRD ANGLE", size=8).at(*P(x + 44, y0 + 8), anchor="center")
                x += w
        # Revision table above the title block.
        rx, ry = RIGHT - 100.0, ty - 30.0
        cols = [("REV", 12), ("DESCRIPTION", 50), ("DATE", 24), ("BY", 14)]
        revs = [("A", "First issue", "2026-03-02", "BS"), ("B", "Holes 10 to 10.5", "2026-05-11", "BS")]
        for r, row in enumerate([tuple(c for c, _ in cols)] + revs):
            x = rx
            for (name, w), txt in zip(cols, row):
                diag.polygon(rect(x, ry + r * 10.0, x + w, ry + (r + 1) * 10.0),
                             style=Style(fill="#E6ECF5" if r == 0 else "#FFFFFF", stroke=INK, stroke_width=1.0), z=-4)
                diag.text(txt, size=9).at(*P(x + (2 if name == "DESCRIPTION" else w / 2), ry + r * 10.0 + 5.0),
                                         anchor="left_center" if name == "DESCRIPTION" else "center")
                x += w
        # Notes block.
        diag.text("NOTES\n1. Break sharp edges 0.5 max.\n2. Unspecified tolerances ISO 2768-m.\n3. Dimensions in mm.",
                  size=9).at(*P(LEFT + 4, ty + 3), anchor="top_left")
        # The part at 1:2, third angle: top above front, right to the right of front.
        fx, fy = 55.0, 122.0       # front view bottom-left (sheet mm)
        gap = 18.0
        hz = (T_ + D) / 2

        def front(x, y):
            return P(fx + x * M, fy - y * M)

        def top(x, z):
            return P(fx + x * M, fy - H * M - gap - (D - z) * M)

        rx0 = fx + W * M + gap + 6

        def right(z, y):
            return P(rx0 + (D - z) * M, fy - y * M)

        fill = Style(fill="#DCE6F2", stroke="none")
        fv = [front(0, 0), front(W, 0), front(W, H), front(0, H)]
        diag.polygon(fv, style=fill, z=-2)
        k.outline(fv)
        k.d.path(f"M {front(0, T_)[0]:.1f} {front(0, T_)[1]:.1f} L {front(W, T_)[0]:.1f} {front(W, T_)[1]:.1f}",
                 style=Style(fill="none", stroke=INK, stroke_width=1.4))
        tv = [top(0, 0), top(W, 0), top(W, D), top(0, D)]
        diag.polygon(tv, style=fill, z=-2)
        k.outline(tv)
        k.d.path(f"M {top(0, T_)[0]:.1f} {top(0, T_)[1]:.1f} L {top(W, T_)[0]:.1f} {top(W, T_)[1]:.1f}",
                 style=Style(fill="none", stroke=INK, stroke_width=1.4))
        for hx in (W * 0.25, W * 0.75):
            c, r = top(hx, hz), DH / 2 * M * K
            diag.path(f"M {c[0] - r:.1f} {c[1]:.1f} a {r:.1f} {r:.1f} 0 1 0 {2 * r:.1f} 0 a {r:.1f} {r:.1f} 0 1 0 {-2 * r:.1f} 0",
                      style=Style(fill="#FFFFFF", stroke=INK, stroke_width=2.0))
            k.centerline((c[0] - r - 5, c[1]), (c[0] + r + 5, c[1]))
            k.centerline((c[0], c[1] - r - 5), (c[0], c[1] + r + 5))
            for off in (-DH / 2, DH / 2):
                k.hidden_line([front(hx + off, 0), front(hx + off, T_)])
        rv = [right(D, 0), right(0, 0), right(0, H), right(T_, H), right(T_, T_), right(D, T_)]
        diag.polygon(rv, style=fill, z=-2)
        k.outline(rv)
        # Dimensions with the true part sizes.
        k.dimension(front(0, 0), front(W, 0), f"${W:g}$", offset=26, side=1)
        k.dimension(front(0, 0), front(0, H), "", offset=30, side=-1)
        diag.text(f"${H:g}$", size=11).at(front(0, H / 2)[0] - 30 - 12, front(0, H / 2)[1], anchor="right_center")
        k.dimension(right(D, 0), right(0, 0), f"${D:g}$", offset=26, side=1)
        diag.text(f"$\\emptyset{DH:g}$ THRU, 2 $\\times$", size=10).at(*top(W * 0.75, hz - 14), anchor="center") if False else None
        diag.text("FRONT", size=10).at(front(W / 2, 0)[0], front(0, 0)[1] + 62, anchor="center")
        diag.text("TOP", size=10).at(front(W / 2, 0)[0], top(0, 0)[1] + 20, anchor="center")
        diag.text("RIGHT", size=10).at(right(D / 2, 0)[0], front(0, 0)[1] + 62, anchor="center")
        diag.caption(
            "**Figure 10:** A drawing sheet with border, zone grid, title block, revision table, projection symbol and a part view at 1:2",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/cad") -> Path:
    return render_all(diagram(), output_dir, "10_title_block_border")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cad")
    build_diagram(dest)
