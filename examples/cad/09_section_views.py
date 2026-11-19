"""Full, half and broken-out section views of a flanged bushing.

Part (mm): flange diameter 60 x 8 thick, body diameter 30, bore diameter 16,
overall height 40, four 6 mm holes on a 46 mm pitch circle. All three views
come from the same numbers; cut surfaces are hatched at 45 degrees.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

FD, FT, BD, BORE, HT = 60.0, 8.0, 30.0, 16.0, 40.0
HOLE, PCD = 6.0, 46.0
S = 3.2
BASE = 380.0
INK = "#1F2F57"
FILL = Style(fill="#DCE6F2", stroke=INK, stroke_width=2.0)


def X(cx, x):
    return cx + x * S


def Y(y):
    return BASE - y * S


def side(sign):
    """Cut pieces (x, y in mm) on one side of the axis; the flange hole splits the flange."""
    f, b, r, h = FD / 2, BD / 2, BORE / 2, PCD / 2
    hr = HOLE / 2
    outer = [(f, 0), (h + hr, 0), (h + hr, FT), (f, FT)]
    inner = [(h - hr, 0), (r, 0), (r, HT), (b, HT), (b, FT), (h - hr, FT)]
    return [[(sign * x, y) for x, y in piece] for piece in (outer, inner)]


def cut(diag, k, cx, pieces):
    for piece in pieces:
        pts = [(X(cx, x), Y(y)) for x, y in piece]
        diag.polygon(pts, style=FILL, z=-3)
        k.hatch(pts, angle=45, gap=7)


def top_view(diag, k, cx, cy, label):
    s = 1.5
    for r, w in ((FD / 2, 1.8), (BD / 2, 1.4), (BORE / 2, 1.4)):
        rr = r * s
        diag.path(f"M {cx - rr:.1f} {cy} a {rr:.1f} {rr:.1f} 0 1 0 {2 * rr:.1f} 0 a {rr:.1f} {rr:.1f} 0 1 0 {-2 * rr:.1f} 0",
                  style=Style(fill="none", stroke=INK, stroke_width=w))
    for a in (0, 90, 180, 270):
        hx, hy = cx + PCD / 2 * s * math.cos(math.radians(a)), cy - PCD / 2 * s * math.sin(math.radians(a))
        rr = HOLE / 2 * s
        diag.path(f"M {hx - rr:.1f} {hy:.1f} a {rr:.1f} {rr:.1f} 0 1 0 {2 * rr:.1f} 0 a {rr:.1f} {rr:.1f} 0 1 0 {-2 * rr:.1f} 0",
                  style=Style(fill="none", stroke=INK, stroke_width=1.2))
    k.centerline((cx - 44, cy), (cx + 44, cy), overshoot=0)
    k.centerline((cx, cy - 44), (cx, cy + 44))
    k.section_arrows((cx - FD / 2 * s - 14, cy), (cx + FD / 2 * s + 14, cy), label, direction=1, length=20)


def diagram() -> Diagram:
    with Diagram("Section views of a flanged bushing", theme="paper") as diag:
        k = Draft(diag)
        cxs = (190.0, 570.0, 950.0)
        names = ("Full section A-A", "Half section B-B", "Broken-out section")
        notes = ("cutting plane removes the near half", "left half cut, right half outside",
                 "a local break exposes one wall")
        for cx, nm, nt in zip(cxs, names, notes):
            diag.text(nm, size=15).at(cx, 50, anchor="center")
            diag.text(nt, size=11).at(cx, BASE + 48, anchor="center")
            k.centerline((cx, Y(0) + 12), (cx, Y(HT) - 12))

        # 1: full section.
        cx = cxs[0]
        cut(diag, k, cx, side(-1) + side(1))
        for sg in (-1, 1):
            k.centerline((X(cx, sg * PCD / 2), Y(-4)), (X(cx, sg * PCD / 2), Y(FT + 4)))
        top_view(diag, k, cx, 140.0, "A")
        k.dimension((X(cx, -FD / 2), Y(0)), (X(cx, FD / 2), Y(0)), f"$\\emptyset{FD:g}$", offset=22, side=1)
        k.dimension((X(cx, BORE / 2), Y(HT)), (X(cx, -BORE / 2), Y(HT)), f"$\\emptyset{BORE:g}$", offset=22, side=1)
        k.dimension((X(cx, FD / 2), Y(HT)), (X(cx, FD / 2), Y(0)), "", offset=18, side=-1)
        diag.text(f"${HT:g}$", size=11).at(X(cx, FD / 2) + 18 + 12, (Y(0) + Y(HT)) / 2, anchor="left_center")

        # 2: half section: left cut, right exterior.
        cx = cxs[1]
        cut(diag, k, cx, side(-1))
        k.centerline((X(cx, -PCD / 2), Y(-4)), (X(cx, -PCD / 2), Y(FT + 4)))
        ext = [(0, 0), (FD / 2, 0), (FD / 2, FT), (BD / 2, FT), (BD / 2, HT), (0, HT)]
        diag.path("M " + " L ".join(f"{X(cx, x):.1f} {Y(y):.1f}" for x, y in ext),
                  style=Style(fill="#EEF2F8", stroke=INK, stroke_width=2.0), z=-3)
        top_view(diag, k, cx, 140.0, "B")
        diag.polygon([(X(cx, -FD / 2), Y(0) - 0), (X(cx, -FD / 2), Y(0) - 0)], style=Style(fill="none", stroke="none"), z=-9) if False else None
        k.dimension((X(cx, -FD / 2), Y(0)), (X(cx, 0), Y(0)), f"$R{FD / 2:g}$", offset=22, side=1)
        diag.text(f"$R{PCD / 2:g}$ PCD", size=11).at(X(cx, -PCD / 4), Y(HT) - 6 - 0, anchor="center") if False else None

        # 3: broken-out section: exterior view with a local cut window at the right wall.
        cx = cxs[2]
        full = [(-FD / 2, 0), (FD / 2, 0), (FD / 2, FT), (BD / 2, FT), (BD / 2, HT), (-BD / 2, HT), (-BD / 2, FT), (-FD / 2, FT)]
        diag.polygon([(X(cx, x), Y(y)) for x, y in full], style=Style(fill="#EEF2F8", stroke=INK, stroke_width=2.0), z=-3)
        # Hidden bore and bolt-hole edges outside the window.
        k.hidden_line([(X(cx, -BORE / 2), Y(HT)), (X(cx, -BORE / 2), Y(0))])
        k.hidden_line([(X(cx, BORE / 2), Y(12.0)), (X(cx, BORE / 2), Y(0))])
        # Break window: wavy boundary on the left and bottom, outer wall on the right.
        y_lo, y_hi, x_l = 12.0, HT, 0.0
        wave = lambda t: 1.6 * math.sin(t * 3.0 * math.tau)
        left = [(X(cx, x_l + wave(i / 14)), Y(y_hi - (y_hi - y_lo) * i / 14)) for i in range(15)]
        bottom = [(X(cx, x_l + (BD / 2 - x_l) * i / 14), Y(y_lo + 1.2 * math.sin(i / 14 * math.tau * 1.5))) for i in range(1, 15)]
        window = [(X(cx, BD / 2), Y(y_hi)), (X(cx, x_l), Y(y_hi))] + left[1:] + bottom
        diag.polygon(window, style=Style(fill="#FFFFFF", stroke="none"), z=-2)
        wall = [(X(cx, BORE / 2), Y(y_hi)), (X(cx, BD / 2), Y(y_hi)), (X(cx, BD / 2), Y(y_lo)), (X(cx, BORE / 2), Y(y_lo))]
        diag.polygon(wall, style=Style(fill="#DCE6F2", stroke=INK, stroke_width=2.0), z=-1)
        k.hatch(wall, angle=45, gap=7)
        k.d.path("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in left), style=Style(fill="none", stroke=INK, stroke_width=1.0), z=0)
        k.d.path("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in [left[-1]] + bottom), style=Style(fill="none", stroke=INK, stroke_width=1.0), z=0)
        k.leader((X(cx, 0) + 6, Y(30)), (X(cx, FD / 2) + 52, Y(HT) + 6), "break line", anchor="left_center")
        k.d.path(f"M {X(cx, 0):.1f} {Y(30):.1f} L {X(cx, 0):.1f} {Y(30):.1f}", style=Style(fill="none", stroke="none"))
        diag.caption(
            "**Figure 9:** Section views of a flanged bushing: a full section, a half section that shows inside and outside at once, and a broken-out section that opens one local window",
            small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/cad") -> Path:
    return render_all(diagram(), output_dir, "09_section_views")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/cad")
    build_diagram(dest)
