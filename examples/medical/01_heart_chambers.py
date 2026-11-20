"""Anterior view of the heart: four chambers, valves and the path of blood.

Chambers are smooth organic outlines; blue marks deoxygenated blood and red
oxygenated blood. Flow arrows follow the textbook sequence: vena cavae, right
atrium, right ventricle, pulmonary artery, lungs, pulmonary veins, left atrium,
left ventricle, aorta.
"""
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


def tube(k, pts, fill, width=18):
    """A vessel: an inked outer stroke with a pale core, drawn behind the chambers."""
    k.smooth_open(pts, stroke=INK, width=width + 3.2, z=-4)
    k.smooth_open(pts, stroke=fill, width=width, z=-3)


def flow(diag, pts, color, head=True, width=2.6):
    """A flow line along a vessel centre line, optionally ending in an arrowhead."""
    Draft(diag).smooth_open(pts, stroke=color, width=width, z=4)
    if head:
        diag.connect(pts[-2], pts[-1], routing="direct", width=width, color=color, head="stealth", z=4)


def leaflets(diag, annulus, tip):
    """Two valve cusps hinged on the annulus, bowing out and meeting at ``tip`` in the ventricle."""
    (x1, y1), (x2, y2) = annulus
    tx, ty = tip
    for hx, hy, bow in ((x1, y1, 5), (x2, y2, -5)):
        diag.path(f"M {hx} {hy} Q {(hx + tx) / 2 + bow} {(hy + ty) / 2 - 3} {tx} {ty}",
                  style=Style(fill="none", stroke=INK, stroke_width=3.0), z=5)


def diagram() -> Diagram:
    with Diagram("Heart chambers and blood flow", theme="paper") as diag:
        k = Draft(diag)
        # Vessel centre lines: the tubes and the flow arrows share them.
        svc = [(262, 80), (262, 140), (264, 215)]
        ivc = [(262, 505), (262, 410), (264, 330), (268, 290)]
        pa_trunk = [(352, 400), (358, 330), (364, 255), (370, 205)]
        pa_r = [(370, 205), (350, 168), (318, 142)]
        pa_l = [(370, 205), (386, 160), (406, 112)]
        ao = [(432, 410), (432, 330), (434, 245), (444, 178), (480, 130), (542, 126), (596, 156)]
        pv_up = [(650, 238), (606, 242), (555, 248)]
        pv_lo = [(650, 290), (606, 286), (552, 282)]
        for pts in (svc, ivc, pa_trunk, pa_r, pa_l):
            tube(k, pts, BLUE_FILL)
        for pts in (ao, pv_up, pv_lo):
            tube(k, pts, RED_FILL)
        # Ventricles: the left one carries the apex; the septum is their shared border.
        k.smooth_closed([(398, 304), (462, 298), (522, 318), (540, 384), (514, 456), (462, 512),
                         (414, 534), (410, 450), (404, 372)], fill=RED_FILL, width=1.8)
        k.smooth_closed([(292, 322), (340, 298), (398, 304), (404, 372), (410, 450), (414, 534),
                         (370, 500), (322, 450), (296, 388)], fill=BLUE_FILL, width=1.8)
        # Atria sit on top of the ventricles.
        k.smooth_closed([(224, 205), (268, 184), (314, 204), (326, 252), (312, 302), (270, 320),
                         (230, 292), (214, 248)], fill=BLUE_FILL, width=1.8)       # right atrium
        k.smooth_closed([(468, 218), (512, 202), (556, 218), (574, 256), (556, 296), (514, 308),
                         (476, 292), (462, 254)], fill=RED_FILL, width=1.8)        # left atrium
        # Atrioventricular valves: cusps hinged on each annulus.
        leaflets(diag, ((278, 311), (322, 311)), (300, 340))
        leaflets(diag, ((478, 306), (534, 306)), (506, 334))
        # Blood flow: vessels in, through the valves, out.
        flow(diag, [(262, 88), (262, 140), (264, 205)], BLUE)
        flow(diag, [(262, 498), (262, 410), (264, 350), (266, 326)], BLUE)
        flow(diag, [(298, 258), (302, 318), (326, 378)], BLUE)
        flow(diag, pa_trunk, BLUE, head=False)
        flow(diag, pa_r, BLUE)
        flow(diag, pa_l, BLUE)
        flow(diag, [(652, 238), (606, 242), (560, 248)], RED)
        flow(diag, [(652, 290), (606, 286), (558, 282)], RED)
        flow(diag, [(514, 262), (506, 318), (486, 384)], RED)
        flow(diag, [(438, 420), (432, 330), (434, 245), (444, 178), (480, 130), (542, 126), (596, 156)], RED)
        # Labels (left column, right column); no leader crosses a vessel.
        L, R = 150, 690
        k.leader((240, 214), (L, 175), "Right atrium", anchor="right_center")
        k.leader((279, 311), (L, 255), "Tricuspid valve", anchor="right_center")
        k.leader((258, 100), (L, 100), "Superior vena cava", anchor="right_center")
        k.leader((258, 470), (L, 470), "Inferior vena cava", anchor="right_center")
        k.leader((330, 450), (300, 548), "Right ventricle", anchor="right_center")
        k.leader((382, 150), (362, 62), "Pulmonary artery (to lungs)", anchor="bottom_center")
        k.leader((552, 226), (R, 190), "Left atrium", anchor="left_center")
        k.leader((534, 306), (R, 352), "Mitral valve", anchor="left_center")
        k.leader((516, 420), (R, 430), "Left ventricle", anchor="left_center")
        k.leader((412, 450), (412, 566), "Septum", anchor="top_center")
        k.leader((488, 127), (R, 76), "Aorta", anchor="left_center")
        diag.text("from lungs", size=11, color=RED).at(650, 262, anchor="bottom_center")
        diag.text("to body", size=11, color=RED).at(606, 176, anchor="left_center")
        diag.text("to right lung", size=11, color=BLUE).at(312, 126, anchor="bottom_center")
        # Key.
        diag.polygon([(130, 615), (150, 615), (150, 627), (130, 627)], style=Style(fill=BLUE_FILL, stroke=INK, stroke_width=0.8))
        diag.text("Deoxygenated blood", size=12).at(158, 621, anchor="left_center")
        diag.polygon([(330, 615), (350, 615), (350, 627), (330, 627)], style=Style(fill=RED_FILL, stroke=INK, stroke_width=0.8))
        diag.text("Oxygenated blood", size=12).at(358, 621, anchor="left_center")
        diag.caption(
            "**Figure 1:** Anterior view of the heart. Deoxygenated blood enters the right atrium, passes the\n"
            "tricuspid valve to the right ventricle and leaves by the pulmonary artery; oxygenated blood returns to\n"
            "the left atrium, crosses the mitral valve to the left ventricle and leaves by the aorta",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/medical") -> Path:
    return render_all(diagram(), output_dir, "01_heart_chambers")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/medical"))
