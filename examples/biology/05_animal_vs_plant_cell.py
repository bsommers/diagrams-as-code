"""Animal and plant cells side by side, drawn as schematic organic outlines.

Shared: plasma membrane, nucleus (nucleolus), mitochondria, rough ER, Golgi, ribosomes. Animal only:
centrioles and prominent lysosomes. Plant only: cell wall, chloroplasts (with grana) and a large central
vacuole. Outlines are smooth closed curves through hand-placed points; this is a teaching schematic, not
to scale.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
RED, GREEN = "#B03A3A", "#2E6B3F"
CYTO = "#F8F3E3"
S = 0.88  # drawing scale for local coordinates


def ell(cx, cy, rx, ry, rot=0.0, n=12, wob=0.0, phase=0.0):
    """Points on a slightly wobbly ellipse (smooth when passed to a Catmull-Rom outline)."""
    pts = []
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n):
        t = 2 * math.pi * i / n
        f = 1 + wob * math.sin(3 * t + phase) + wob * 0.6 * math.sin(5 * t + 2 * phase)
        x, y = rx * f * math.cos(t), ry * f * math.sin(t)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def rounded_rect(x0, y0, x1, y1, r):
    return (f"M {x0 + r} {y0} L {x1 - r} {y0} Q {x1} {y0} {x1} {y0 + r} L {x1} {y1 - r} Q {x1} {y1} {x1 - r} {y1} "
            f"L {x0 + r} {y1} Q {x0} {y1} {x0} {y1 - r} L {x0} {y0 + r} Q {x0} {y0} {x0 + r} {y0} Z")


class Cell:
    """Drawing helpers in a local frame centred on the cell."""

    def __init__(self, diag, cx, cy):
        self.diag, self.cx, self.cy = diag, cx, cy
        self.k = Draft(diag)

    def p(self, x, y):
        return (self.cx + x * S, self.cy + y * S)

    def pts(self, seq):
        return [self.p(x, y) for x, y in seq]

    def nucleus(self, x, y, r):
        self.k.smooth_closed(self.pts(ell(x, y, r, r * 0.94, wob=0.02)), fill="#D9D2EA", stroke=INK, width=1.8, z=1)
        nx, ny = self.p(x - r * 0.25, y - r * 0.15)
        self.diag.polygon(ell(nx, ny, 11 * S, 11 * S, n=14), style=Style(fill="#8E80B8", stroke=INK, stroke_width=1.0), z=2)

    def mito(self, x, y, rx, ry, rot):
        self.k.smooth_closed(self.pts(ell(x, y, rx, ry, rot, n=12)), fill="#F4C9A8", stroke="#9C4A12", width=1.5, z=1)
        inner = []
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for i in range(7):  # cristae: a folded inner membrane
            u = -0.65 + i * 0.2167
            v = ry * 0.45 * (1 if i % 2 == 0 else -1)
            inner.append((x + rx * u * c - v * s, y + rx * u * s + v * c))
        self.k.smooth_open(self.pts(inner), stroke="#9C4A12", width=1.1, tension=0.6, z=2)

    def golgi(self, x, y, width=64):
        for j in range(4):
            w = width - j * 6
            yy = y + j * 9
            self.k.smooth_open(self.pts([(x - w / 2, yy + 3), (x, yy - 3), (x + w / 2, yy + 3)]), stroke="#8A5A00", width=3.0, z=2)

    def er(self, x, y, r, a0=-65, a1=65):
        """Rough ER: folded sheets hugging the nucleus, studded with ribosomes."""
        for j, rr in enumerate((r + 12, r + 24, r + 36)):
            seg = []
            for i in range(11):
                a = math.radians(a0 + (a1 - a0) * i / 10)
                w = rr + 3.0 * math.sin(i * 1.9 + j)
                seg.append((x + w * math.cos(a), y + w * math.sin(a)))
            self.k.smooth_open(self.pts(seg), stroke="#2F5FA8", width=2.2, z=2)
            if j == 2:
                for i in range(1, 10, 2):
                    a = math.radians(a0 + (a1 - a0) * i / 10)
                    w = rr + 6.0
                    self.dot(x + w * math.cos(a), y + w * math.sin(a), 1.8, "#2F5FA8")

    def dot(self, x, y, r=1.8, color=INK):
        px, py = self.p(x, y)
        self.diag.polygon(ell(px, py, r, r, n=8), style=Style(fill=color, stroke=color, stroke_width=0.5), z=3)

    def ribosomes(self, spots):
        for x, y in spots:
            self.dot(x, y, 1.9, "#444444")

    def blob(self, x, y, r, fill, stroke, z=1):
        self.k.smooth_closed(self.pts(ell(x, y, r, r, n=10)), fill=fill, stroke=stroke, width=1.4, z=z)

    def label(self, tip, side, text, ly):
        """A leader from a local feature point to a label in the column beside the cell (ly is local y)."""
        tx, ty = self.p(*tip)
        ex = self.cx + side * (self.half_w + 40)
        self.k.leader((tx, ty), (ex, self.cy + ly * S), text, anchor="left_center" if side > 0 else "right_center")

    def label_top(self, tip, text):
        """A vertical leader to a label above the cell."""
        tx, ty = self.p(*tip)
        self.k.leader((tx, ty), (tx, self.cy - 160 * S - 26), text, anchor="bottom_center")


def diagram() -> Diagram:
    with Diagram("Animal and plant cells", theme="paper") as diag:
        ay, py = 330.0, 330.0
        # ------------------------------------------------------------ animal cell
        A = Cell(diag, 330.0, ay)
        A.half_w = 200 * S
        outline = ell(0, 0, 200, 160, wob=0.045, phase=0.8, n=16)
        A.k.smooth_closed(A.pts(outline), fill=CYTO, stroke=INK, width=2.4, z=-1)
        A.nucleus(-30, -10, 58)
        A.er(-30, -10, 58)
        A.golgi(110, -105)
        A.mito(-125, 95, 40, 20, 22)
        A.mito(95, 98, 40, 20, -15)
        A.blob(-135, -70, 11, "#E3B6B6", RED)
        A.blob(-92, -122, 9, "#E3B6B6", RED)
        A.blob(150, 15, 10, "#E3B6B6", RED)
        # Centriole pair at right angles.
        for (x, y, w, h) in ((-150, 12, 8, 26), (-136, 34, 26, 8)):
            px, py_ = A.p(x - w / 2, y - h / 2)
            diag.polygon([(px, py_), (px + w * S, py_), (px + w * S, py_ + h * S), (px, py_ + h * S)],
                         style=Style(fill="#F2D77A", stroke="#8A5A00", stroke_width=1.3), z=2)
        A.ribosomes([(-80, 110), (-30, 120), (20, 105), (60, 60), (130, -40), (-5, -118), (-170, -20), (40, 125), (-95, 50)])
        diag.text("**Animal cell**", size=17).at(330, ay - 160 * S - 70, anchor="bottom_center")
        A.label_top((-30, -68), "Nucleus + nucleolus")
        A.label((-143, -73), -1, "**Lysosome**", -95)
        A.label((-150, 8), -1, "**Centrioles**", 12)
        A.label((-150, 100), -1, "Mitochondrion", 100)
        A.label((110, -100), 1, "Golgi apparatus", -100)
        A.label((64, -10), 1, "Rough ER (ribosomes)", -30)
        A.label((158, 15), 1, "Lysosome", 20)
        A.label((125, 106), 1, "Mitochondrion", 80)
        A.label(outline[2], 1, "Plasma membrane", 130)

        # ------------------------------------------------------------ plant cell
        P = Cell(diag, 1030.0, py)
        hw, hh = 190 * S, 160 * S
        P.half_w = hw + 12
        diag.path(rounded_rect(P.cx - hw - 12, P.cy - hh - 12, P.cx + hw + 12, P.cy + hh + 12, 26),
                  style=Style(fill="#CFC08A", stroke="#6B5A1E", stroke_width=2.2), z=-2)
        diag.path(rounded_rect(P.cx - hw, P.cy - hh, P.cx + hw, P.cy + hh, 20),
                  style=Style(fill=CYTO, stroke=INK, stroke_width=1.8), z=-1)
        P.k.smooth_closed(P.pts(ell(45, 20, 70, 92, wob=0.05, phase=1.5, n=14)), fill="#DCEBFA", stroke="#2F5FA8", width=1.6, z=1)
        diag.text("central\nvacuole", size=12, color="#2F5FA8").at(*P.p(45, 20), anchor="center")
        P.nucleus(-125, -75, 40)
        P.er(-125, -75, 40, a0=-55, a1=55)
        P.golgi(95, -118, 56)
        P.mito(-135, 60, 34, 17, -25)
        P.mito(15, -122, 34, 17, 8)
        # Chloroplasts with grana stacks.
        for (x, y, rot) in ((148, -40, -70), (148, 62, 70), (-55, 124, 5)):
            P.k.smooth_closed(P.pts(ell(x, y, 36, 19, rot, n=12)), fill="#BFE0B5", stroke=GREEN, width=1.6, z=1)
            c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            for u in (-14, 0, 14):
                gx, gy = x + u * c, y + u * s
                P.k.smooth_closed(P.pts(ell(gx, gy, 5, 8, rot + 90, n=8)), fill="#4E8F3C", stroke=GREEN, width=0.8, z=2)
        P.ribosomes([(-170, 20), (-90, 110), (-105, 0), (60, 130), (170, 5), (-170, -130), (170, -125), (-20, 70)])
        diag.text("**Plant cell**", size=17).at(1030, ay - 160 * S - 70, anchor="bottom_center")
        P.label_top((-125 + 76 * math.cos(math.radians(-50)), -75 + 76 * math.sin(math.radians(-50))), "Rough ER")
        P.label((-163, -82), -1, "Nucleus + nucleolus", -95)
        P.label((-190, -30), -1, "Plasma membrane", -45)
        P.label((-190 - 6 / S, 8), -1, "**Cell wall**", 0)
        P.label((-150, 62), -1, "Mitochondrion", 62)
        P.label((95, -118), 1, "Golgi apparatus", -110)
        P.label((148, -50), 1, "**Chloroplast** (grana)", -45)
        P.label((114, 20), 1, "**Large central vacuole**", 20)

        # Comparison key.
        diag.text("**Both:** nucleus, mitochondria, rough ER, Golgi, ribosomes, plasma membrane", size=13).at(80, 550, anchor="top_left")
        diag.text("**Animal only:** centrioles, prominent lysosomes, no cell wall, no chloroplasts", size=13, color=RED).at(80, 576, anchor="top_left")
        diag.text("**Plant only:** cellulose cell wall, chloroplasts (photosynthesis), large central vacuole", size=13, color=GREEN).at(80, 602, anchor="top_left")
        diag.caption(
            "**Figure 5:** Animal and plant cells. Both are eukaryotic and share the nucleus, mitochondria and secretory machinery;\n"
            "the plant cell adds a rigid cell wall, chloroplasts and a large vacuole. Schematic, not to scale",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "05_animal_vs_plant_cell")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
