"""A 300 mm wafer map: reticle shots, dies and a sort-test bin map (SEMICONDUCTOR domain).

The wafer is stepped in reticle fields (26 x 33 mm here), each holding a 2 x 2 array
of 13 x 16.5 mm dies. Every die that lies fully inside the 3 mm edge exclusion is
coloured by its probe bin. The defect model is synthetic and seeded (an edge-weighted
random fail rate plus one particle cluster and one scratch), so the picture is
reproducible, not measured data. How yield is managed across a fab is in
examples/manufacturing/05_yield_management.py; this figure is the geometry underneath it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
MM = 1.7                      # pixels per millimetre
CX, CY = 330.0, 330.0
R_WAFER, R_EDGE = 150.0, 147.0  # mm: wafer radius and edge-exclusion radius
SHOT_W, SHOT_H = 26.0, 33.0
DIE_W, DIE_H = 13.0, 16.5
GOOD, MARGINAL, FAIL, PARTIAL = "#7DBE7D", "#F2D45C", "#D9534F", "#E4E4E4"


class Lcg:
    """A tiny seeded generator so the map is identical on every run."""

    def __init__(self, seed: int) -> None:
        self.s = seed

    def next(self) -> float:
        self.s = (1103515245 * self.s + 12345) % 2147483648
        return self.s / 2147483648


def rect_path(x0: float, y0: float, x1: float, y1: float) -> str:
    return f"M {x0:.2f} {y0:.2f} L {x1:.2f} {y0:.2f} L {x1:.2f} {y1:.2f} L {x0:.2f} {y1:.2f} Z"


def sort_dies() -> tuple[dict[str, list[tuple[float, float]]], list[tuple[float, float]]]:
    """Die lower-left corners (mm from wafer centre) by bin, plus the incomplete edge dies."""
    rng = Lcg(20240607)
    bins: dict[str, list[tuple[float, float]]] = {"good": [], "marginal": [], "fail": []}
    partial: list[tuple[float, float]] = []
    nx, ny = int(2 * R_WAFER / DIE_W) + 2, int(2 * R_WAFER / DIE_H) + 2
    for i in range(-nx // 2, nx // 2 + 1):
        for j in range(-ny // 2, ny // 2 + 1):
            x0, y0 = i * DIE_W, j * DIE_H
            corners = [(x0, y0), (x0 + DIE_W, y0), (x0, y0 + DIE_H), (x0 + DIE_W, y0 + DIE_H)]
            far = max(math.hypot(x, y) for x, y in corners)
            near = min(math.hypot(x, y) for x, y in corners)
            if near > R_WAFER:
                continue
            if far > R_WAFER:
                continue            # not a whole die on the wafer
            if far > R_EDGE:
                partial.append((x0, y0))
                continue
            mx, my = x0 + DIE_W / 2, y0 + DIE_H / 2
            r = math.hypot(mx, my) / R_WAFER
            p_fail = 0.03 + 0.30 * r ** 4
            if math.hypot(mx + 62, my - 48) < 34:                       # particle cluster
                p_fail += 0.7
            if abs((mx - 20) * 0.5 + (my + 10) * 0.866 - 20) < 4 and mx > 10:  # scratch
                p_fail += 0.8
            u = rng.next()
            kind = "fail" if u < p_fail else "marginal" if u < p_fail + 0.07 else "good"
            bins[kind].append((x0, y0))
    return bins, partial


def diagram() -> Diagram:
    bins, partial = sort_dies()
    total = sum(len(v) for v in bins.values())
    with Diagram("300 mm wafer map: reticle shots and sort yield (synthetic data)", theme="paper") as diag:
        k = Draft(diag, size=11.5)

        def px(x_mm: float, y_mm: float) -> tuple[float, float]:
            return CX + x_mm * MM, CY - y_mm * MM

        def die_d(x0: float, y0: float, w: float = DIE_W, h: float = DIE_H) -> str:
            a, b = px(x0, y0 + h), px(x0 + w, y0)
            return rect_path(a[0], a[1], b[0], b[1])

        rw = R_WAFER * MM
        notch_w = 4.0 * MM
        diag.path(f"M {CX - rw:.2f} {CY:.2f} a {rw:.2f} {rw:.2f} 0 1 0 {2 * rw:.2f} 0 "
                  f"a {rw:.2f} {rw:.2f} 0 1 0 {-2 * rw:.2f} 0 Z",
                  style=Style(fill="none", stroke=INK, stroke_width=2.4), z=-1)
        diag.path(f"M {CX - notch_w:.2f} {CY + rw:.2f} L {CX:.2f} {CY + rw - notch_w:.2f} L {CX + notch_w:.2f} {CY + rw:.2f} Z",
                  style=Style(fill="#FFFFFF", stroke=INK, stroke_width=1.6), z=-1)
        diag.path(" ".join(die_d(x, y) for x, y in partial),
                  style=Style(fill=PARTIAL, stroke="#9A9A9A", stroke_width=0.5), z=-4)
        colours = {"good": GOOD, "marginal": MARGINAL, "fail": FAIL}
        for name, pts in bins.items():
            if pts:
                diag.path(" ".join(die_d(x, y) for x, y in pts),
                          style=Style(fill=colours[name], stroke="#4A4A4A", stroke_width=0.5), z=-4)
        # reticle shot grid, drawn only where a shot touches the wafer
        shots = []
        for i in range(-7, 7):
            for j in range(-6, 6):
                x0, y0 = i * SHOT_W, j * SHOT_H
                cs = [(x0, y0), (x0 + SHOT_W, y0), (x0, y0 + SHOT_H), (x0 + SHOT_W, y0 + SHOT_H)]
                if min(math.hypot(x, y) for x, y in cs) < R_WAFER:
                    shots.append(die_d(x0, y0, SHOT_W, SHOT_H))
        diag.path(" ".join(shots), style=Style(fill="none", stroke="#1F2F57", stroke_width=1.5), z=-3)

        # edge exclusion ring
        re_ = R_EDGE * MM
        diag.path(f"M {CX - re_:.2f} {CY:.2f} a {re_:.2f} {re_:.2f} 0 1 0 {2 * re_:.2f} 0 "
                  f"a {re_:.2f} {re_:.2f} 0 1 0 {-2 * re_:.2f} 0 Z",
                  style=Style(fill="none", stroke="#6B4FA0", stroke_width=1.0, dash="5,4"), z=-2)
        k.dimension((CX - rw, CY + rw + 6), (CX + rw, CY + rw + 6), "$\\emptyset 300$ mm", offset=26, side=1)

        # legend and statistics
        lx, ly = 700.0, 90.0
        diag.text("Sort bins", size=15).at(lx, ly, anchor="left_center")
        for n, (label, col, count) in enumerate((("pass (bin 1)", GOOD, len(bins["good"])),
                                                  ("marginal (bin 2)", MARGINAL, len(bins["marginal"])),
                                                  ("fail", FAIL, len(bins["fail"])),
                                                  ("edge-exclusion dies, not sorted", PARTIAL, len(partial)))):
            y = ly + 30 + n * 28
            diag.polygon([(lx, y), (lx + 22, y), (lx + 22, y + 16), (lx, y + 16)],
                         style=Style(fill=col, stroke="#4A4A4A", stroke_width=0.8))
            diag.text(f"{label}: {count}", size=12.5).at(lx + 32, y + 8, anchor="left_center")
        yield_pct = 100.0 * len(bins["good"]) / total
        diag.text(f"Tested dies: {total}\nPass yield: {yield_pct:.1f}%\n"
                  "Edge-weighted random failures, one\nparticle cluster (upper left) and\none scratch (right of centre).",
                  size=12.5).at(lx, ly + 160, anchor="top_left")
        # one reticle field, enlarged
        ix, iy, s = lx + 20, ly + 330, 5.0
        diag.text("One reticle field (shot)", size=13).at(ix, iy - 18, anchor="left_center")
        for a in range(2):
            for b in range(2):
                diag.polygon([(ix + a * DIE_W * s, iy + b * DIE_H * s), (ix + (a + 1) * DIE_W * s, iy + b * DIE_H * s),
                              (ix + (a + 1) * DIE_W * s, iy + (b + 1) * DIE_H * s), (ix + a * DIE_W * s, iy + (b + 1) * DIE_H * s)],
                             style=Style(fill="#CFE0F3", stroke=INK, stroke_width=1.0), z=-3)
        k.dimension((ix, iy + 2 * DIE_H * s), (ix + 2 * DIE_W * s, iy + 2 * DIE_H * s), "$26$ mm", offset=22, side=1)
        k.dimension((ix, iy), (ix, iy + 2 * DIE_H * s), "$33$ mm", offset=22, side=1)
        diag.text("2 x 2 dies of 13 x 16.5 mm", size=11.5, color="#444444").at(ix + DIE_W * s, iy + 2 * DIE_H * s + 52, anchor="top_center")
        diag.caption("**Figure 7:** Wafer map with reticle shots and a synthetic sort-bin map. Schematic geometry; "
                     "the failure pattern is generated, not measured.", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "07_wafer_map_yield")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
