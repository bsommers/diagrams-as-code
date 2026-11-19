"""Ray diagram for a converging thin lens, with the image found by construction.

The focal length $f$ and the object distance $d_o$ are the inputs. The three
principal rays are computed from them: the parallel ray bends through the far
focus, the ray through the near focus leaves parallel, and the ray through the
lens centre goes straight. Where they meet is checked against the lens
equation $1/f = 1/d_o + 1/d_i$.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

F, DO, H = 60.0, 150.0, 50.0          # focal length, object distance, object height (cm)
PX = 2.5                               # px per cm
LENS_X, AXIS_Y = 470.0, 260.0
INK = "#111111"
RAY_COLORS = ("#9C2F2F", "#1F2F57", "#2E6B3F")


def X(u: float) -> float:
    """Pixel x of a position u (cm) measured from the lens, positive downstream."""
    return LENS_X + u * PX


def Y(v: float) -> float:
    """Pixel y of a height v (cm) above the axis."""
    return AXIS_Y - v * PX


def diagram() -> Diagram:
    di = F * DO / (DO - F)            # image distance from 1/f = 1/do + 1/di
    hi = -H * di / DO                 # signed image height
    mag = hi / H
    tip = (-DO, H)
    image = (di, hi)
    overshoot = 28.0                  # how far the rays run past the image, cm

    def extend(p, q, until_x):
        """Point on the line p->q at x = until_x."""
        t = (until_x - p[0]) / (q[0] - p[0])
        return (until_x, p[1] + t * (q[1] - p[1]))

    # Each ray: tip, point on the lens plane, the outgoing line's second point.
    ray1_lens = (0.0, H)                       # parallel ray, bent through the far focus
    ray1_out = (F, 0.0)
    ray2_lens = (0.0, 0.0)                     # through the optical centre
    ray2_out = image
    ray3_lens = (0.0, H * (1 - DO / (DO - F)))  # through the near focus, leaves parallel
    ray3_out = (di, ray3_lens[1])
    x_end = di + overshoot

    def pt(p):
        return (X(p[0]), Y(p[1]))

    with Diagram("Thin lens ray diagram", theme="paper") as diag:
        diag.connect((X(-DO - 45 / PX), AXIS_Y), (X(x_end + 22 / PX * 0 + 8), AXIS_Y), routing="direct",
                     arrow_head=False, width=0.9, color="#555555")
        diag.connect((LENS_X, Y(62)), (LENS_X, Y(-62)), routing="direct", two_way=True, width=2.2,
                     head="stealth", color=INK)
        diag.text("lens", size=12).at(LENS_X + 8, Y(62), anchor="left_center")

        # Object and image.
        diag.connect(pt((-DO, 0)), pt(tip), routing="direct", width=3.0, head="stealth", color=INK)
        diag.connect(pt((di, 0)), pt(image), routing="direct", width=3.0, head="stealth", color=INK)
        diag.text("object", size=13).at(X(-DO), Y(-4), anchor="top_center")
        diag.text("image (real, inverted)", size=13).at(X(di), AXIS_Y - 12, anchor="bottom_center")

        for color, (lens_pt, out_pt) in zip(RAY_COLORS, ((ray1_lens, ray1_out), (ray2_lens, ray2_out),
                                                          (ray3_lens, ray3_out))):
            diag.connect(pt(tip), pt(lens_pt), routing="direct", arrow_head=False, width=1.5, color=color)
            end = extend(lens_pt, out_pt, x_end)
            diag.connect(pt(lens_pt), pt(end), routing="direct", width=1.5, head="stealth", color=color)
            mid = ((tip[0] + lens_pt[0]) / 2, (tip[1] + lens_pt[1]) / 2)
        for k, (color, lens_pt) in enumerate(zip(RAY_COLORS, (ray1_lens, ray2_lens, ray3_lens)), 1):
            # a small numeral on each incoming ray, a third of the way from the object
            a = (tip[0] + (lens_pt[0] - tip[0]) * 0.3, tip[1] + (lens_pt[1] - tip[1]) * 0.3)
            diag.text(f"**{k}**", size=12, color=color).at(X(a[0]), Y(a[1]) - 9, anchor="bottom_center")

        # Focal points and twice the focal length.
        for u, name in ((-2 * F, "$2F$"), (-F, "$F$"), (F, "$F'$"), (2 * F, "$2F'$")):
            diag.point(X(u), AXIS_Y, dot=True, radius=3)
            diag.text(name, size=13).at(X(u), AXIS_Y + 9, anchor="top_center")

        # Distances.
        dim_y = Y(hi) + 40
        light = Style(fill="none", stroke="#888888", stroke_width=0.7, dash="3,3")
        for u, top in ((-DO, AXIS_Y + 2), (0.0, AXIS_Y + 2), (di, Y(hi) + 6)):
            diag.polyline([(X(u), top), (X(u), dim_y + 6)], style=light, obstacle=False)
        arrow = dict(routing="direct", two_way=True, width=0.8, arrow_size=0.6)
        diag.connect((X(-DO), dim_y), (LENS_X, dim_y), **arrow)
        diag.connect((LENS_X, dim_y), (X(di), dim_y), **arrow)
        diag.text(f"$d_o = {DO:g}$ cm", size=13).at((X(-DO) + LENS_X) / 2, dim_y + 6, anchor="top_center")
        diag.text(f"$d_i = {di:g}$ cm", size=13).at((X(di) + LENS_X) / 2, dim_y + 6, anchor="top_center")

        diag.text(
            "Principal rays\n"
            "**1** parallel to the axis, then through $F'$\n"
            "**2** through the centre, undeflected\n"
            "**3** through $F$, then parallel to the axis",
            size=12,
        ).at(X(-DO) - 20, Y(112), anchor="top_left")
        diag.text(
            f"$f = {F:g}$ cm,  $h = {H:g}$ cm\n"
            f"$1/d_i = 1/f - 1/d_o$,  so $d_i = {di:g}$ cm\n"
            f"$m = -d_i / d_o = {mag:.3f}$,  $h_i = {hi:.1f}$ cm",
            size=12,
        ).at(X(40), Y(112), anchor="top_left")
        diag.caption("**Figure 4:** Image formation by a converging lens with the object beyond $F$, from the three principal rays",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/physics") -> Path:
    return render_all(diagram(), output_dir, "04_thin_lens_rays")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/physics")
    build_diagram(dest)
