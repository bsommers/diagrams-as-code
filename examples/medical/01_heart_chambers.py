"""Anterior view of the heart: four chambers, valves and the path of blood.

Chambers are smooth organic outlines; blue marks deoxygenated blood and red
oxygenated blood. Flow arrows follow the textbook sequence: vena cavae, right
atrium, right ventricle, pulmonary artery, lungs, pulmonary veins, left atrium,
left ventricle, aorta.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
BLUE = "#3A5FA8"
RED = "#B03A3A"
BLUE_FILL = "#C9D6EE"
RED_FILL = "#F0C9C9"


def blob(cx, cy, rx, ry, n=10, wob=0.05, phase=0.0):
    """Points around an ellipse with a gentle radial wobble."""
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = 1 + wob * math.sin(3 * a + phase)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return pts


def flow(diag, pts, color, width=3.0):
    """A thick vessel path ending in an arrowhead."""
    k = Draft(diag)
    k.smooth_open(pts, stroke=color, width=width)
    diag.connect(pts[-2], pts[-1], routing="direct", width=width, color=color, head="stealth")


def diagram() -> Diagram:
    with Diagram("Heart chambers and blood flow", theme="paper") as diag:
        k = Draft(diag)
        # Vessels first (behind the chambers); the arrows reuse the same centre lines.
        svc = [(240, 90), (246, 140), (251, 183)]
        ivc = [(235, 480), (235, 390), (242, 285)]
        pa = [(350, 330), (350, 230), (342, 140), (285, 108)]
        ao = [(445, 340), (445, 240), (455, 140), (500, 105), (580, 118)]
        pv = [(670, 238), (625, 241), (590, 241)]
        for pts, c in ((svc, BLUE_FILL), (ivc, BLUE_FILL), (pa, BLUE_FILL), (ao, RED_FILL), (pv, RED_FILL)):
            k.smooth_open(pts, stroke=c, width=15, z=-3)
        # Chambers.
        k.smooth_closed(blob(275, 235, 56, 56, phase=0.4), fill=BLUE_FILL, width=1.8)   # RA
        k.smooth_closed(blob(322, 392, 66, 74, phase=1.0), fill=BLUE_FILL, width=1.8)   # RV
        k.smooth_closed(blob(545, 240, 52, 46, phase=2.0), fill=RED_FILL, width=1.8)    # LA
        k.smooth_closed(blob(470, 385, 82, 88, phase=0.2), fill=RED_FILL, width=1.8)    # LV
        # Valves as short bars on the atrioventricular openings.
        for (a, b) in (((282, 292), (308, 306)), ((508, 296), (530, 306))):
            diag.path(f"M {a[0]} {a[1]} L {b[0]} {b[1]}", style=Style(fill="none", stroke=INK, stroke_width=3.5), z=3)
        # Blood flow arrows.
        flow(diag, svc, BLUE)
        flow(diag, ivc, BLUE)
        flow(diag, [(280, 262), (292, 295), (300, 345)], BLUE)
        flow(diag, pa, BLUE)
        flow(diag, [(540, 268), (520, 320), (495, 360)], RED)
        flow(diag, ao, RED)
        flow(diag, pv, RED)
        # Labels.
        L, R = 150, 650
        k.leader((228, 250), (L, 230), "Right atrium", anchor="right_center")
        k.leader((290, 410), (L, 410), "Right ventricle", anchor="right_center")
        k.leader((240, 120), (L, 110), "Superior vena cava", anchor="right_center")
        k.leader((235, 450), (L, 480), "Inferior vena cava", anchor="right_center")
        k.leader((295, 300), (L, 330), "Tricuspid valve", anchor="right_center")
        k.leader((300, 112), (L, 70), "Pulmonary artery (to lungs)", anchor="right_center")
        k.leader((580, 262), (R, 310), "Left atrium", anchor="left_center")
        k.leader((519, 301), (R, 345), "Mitral valve", anchor="left_center")
        k.leader((540, 410), (R, 420), "Left ventricle", anchor="left_center")
        k.leader((372, 420), (372, 505), "Septum", anchor="top_center")
        k.leader((580, 118), (R, 70), "Aorta", anchor="left_center")
        diag.text("from lungs", size=11, color=RED).at(668, 215, anchor="bottom_center")
        diag.text("to body", size=11, color=RED).at(640, 100, anchor="left_center")
        # Key.
        diag.polygon([(130, 575), (150, 575), (150, 587), (130, 587)], style=Style(fill=BLUE_FILL, stroke=INK, stroke_width=0.8))
        diag.text("Deoxygenated blood", size=12).at(158, 581, anchor="left_center")
        diag.polygon([(330, 575), (350, 575), (350, 587), (330, 587)], style=Style(fill=RED_FILL, stroke=INK, stroke_width=0.8))
        diag.text("Oxygenated blood", size=12).at(358, 581, anchor="left_center")
        diag.caption(
            "**Figure 1:** Anterior view of the heart. Deoxygenated blood enters the right atrium, passes the\n"
            "tricuspid valve to the right ventricle and leaves by the pulmonary artery; oxygenated blood returns to\n"
            "the left atrium, crosses the mitral valve to the left ventricle and leaves by the aorta",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/medical") -> Path:
    return render_all(diagram(), output_dir, "01_heart_chambers")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/medical"))
