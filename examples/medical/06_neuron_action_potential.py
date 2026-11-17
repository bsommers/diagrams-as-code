"""A myelinated motor neuron with the action potential recorded at one point on its axon.

The membrane potential is built from textbook values: resting -70 mV, threshold -55 mV,
peak +40 mV, undershoot -80 mV. Phases are joined with smooth steps; times in ms.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
RED, AMBER = "#B03A3A", "#8A5A00"
CELL, MYELIN = "#DCE6F2", "#F3E3B3"
REST, THRESH, PEAK, UNDER = -70.0, -55.0, 40.0, -80.0


def sm(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def membrane(t: float) -> float:
    """Membrane potential (mV) at time t (ms) after the stimulus begins."""
    if t < 0.6:
        return REST
    if t < 1.0:
        return REST + (THRESH - REST) * sm((t - 0.6) / 0.4)
    if t < 1.8:
        return THRESH + (PEAK - THRESH) * sm((t - 1.0) / 0.8)
    if t < 3.0:
        return PEAK + (UNDER - PEAK) * sm((t - 1.8) / 1.2)
    return UNDER + (REST - UNDER) * sm((t - 3.0) / 2.0)


def diagram() -> Diagram:
    with Diagram("Neuron and action potential", theme="paper") as diag:
        k = Draft(diag)
        cy = 150.0
        # Dendrites: branching open curves leaving the soma on the left.
        for pts in (
            [(172, 140), (140, 110), (115, 85), (100, 60)], [(140, 110), (118, 112), (95, 105)],
            [(165, 128), (140, 95), (140, 65)], [(160, 165), (130, 175), (105, 168)],
            [(130, 175), (112, 195), (100, 215)], [(172, 180), (150, 205), (140, 235)],
            [(150, 205), (125, 215), (112, 232)],
        ):
            k.smooth_open(pts, stroke=INK, width=2.2)
        # Soma, nucleus.
        soma = [(190 + 40 * math.cos(a) * (1 + 0.07 * math.sin(3 * a)), cy + 34 * math.sin(a) * (1 + 0.07 * math.sin(3 * a)))
                for a in [2 * math.pi * i / 10 for i in range(10)]]
        k.smooth_closed(soma, fill=CELL, width=1.8, z=1)
        k.smooth_closed([(190 + 13 * math.cos(a), cy + 12 * math.sin(a)) for a in [2 * math.pi * i / 8 for i in range(8)]],
                        fill="#9DB3D6", width=1.2, z=2)
        # Axon hillock (a tapering wedge) and axon.
        diag.polygon([(222, cy - 20), (262, cy - 3), (262, cy + 3), (222, cy + 20)], style=Style(fill=CELL, stroke=INK, stroke_width=1.6), z=1)
        diag.path(f"M 262 {cy} H 650", style=Style(fill="none", stroke=INK, stroke_width=3), z=1)
        # Myelin sheaths: rounded segments separated by nodes of Ranvier.
        sheaths = [(280, 350), (362, 432), (444, 514), (526, 596)]
        for a, b in sheaths:
            diag.polygon([(a, cy - 12), (b, cy - 12), (b + 4, cy - 6), (b + 4, cy + 6), (b, cy + 12), (a, cy + 12), (a - 4, cy + 6), (a - 4, cy - 6)],
                         style=Style(fill=MYELIN, stroke=INK, stroke_width=1.4), z=2)
        # Axon terminals and boutons.
        for pts in ([(650, cy), (680, cy - 10), (705, cy - 38)], [(650, cy), (690, cy)], [(650, cy), (680, cy + 12), (705, cy + 40)]):
            k.smooth_open(pts, stroke=INK, width=2.2)
            x, y = pts[-1]
            diag.polygon([(x + 9 * math.cos(a), y + 9 * math.sin(a)) for a in [2 * math.pi * i / 14 for i in range(14)]],
                         style=Style(fill=CELL, stroke=INK, stroke_width=1.4), z=2)
        # Direction of the impulse.
        diag.connect((440, 28), (610, 28), routing="direct", width=1.6, color=RED, head="stealth")
        diag.text("direction of impulse", size=12, color=RED).at(525, 36, anchor="top_center")
        # Labels.
        k.leader((112, 232), (60, 262), "Dendrites", anchor="top_center", dot=True)
        k.leader((160, cy + 24), (200, 262), "Soma (cell body)", anchor="top_center")
        k.leader((190, cy), (245, 40), "Nucleus", anchor="bottom_center")
        k.leader((240, cy + 12), (275, 262), "Axon hillock", anchor="top_center")
        k.leader((316, cy + 12), (330, 218), "Myelin sheath", anchor="top_center")
        k.leader((356, cy), (400, 90), "Node of Ranvier", anchor="bottom_center")
        k.leader((670, cy - 8), (700, 90), "Axon terminals", anchor="bottom_left")
        k.leader((480, cy), (480, 262), "Axon", anchor="top_center")
        # Action potential plot.
        pl = Plot(diag, x=(0, 5), y=(-100, 50), origin=(130, 570), size=(560, 230))
        pl.grid(xstep=1, ystep=40)
        pl.axes(xlabel="Time (ms)", ylabel="Membrane potential (mV)", xstep=1, ystep=40, through_zero=False, arrows=False)
        pl.hline(REST, stroke="#8890A8")
        pl.hline(THRESH, stroke=AMBER)
        pl.function(membrane, stroke=RED, width=2.6, n=800)
        pl.label(0, REST, "resting $-70$ mV", size=12, anchor="top_left", dx=6, dy=6)
        pl.label(0, THRESH, "threshold $-55$ mV", size=12, anchor="bottom_left", dx=6, dy=-4, color=AMBER)
        pl.dot(1.8, PEAK, radius=4.0)
        pl.label(1.8, PEAK, "peak $+40$ mV", size=12, anchor="left_center", dx=10)
        pl.dot(3.0, UNDER, radius=4.0)
        pl.label(3.0, UNDER, "undershoot (hyperpolarisation) $-80$ mV", size=12, anchor="top_left", dx=2, dy=10)
        pl.label(1.2, -15, "depolarisation", size=12, anchor="right_center", dx=-14)
        pl.label(2.4, -15, "repolarisation", size=12, anchor="left_center", dx=14)
        diag.caption(
            "**Figure 6:** A myelinated neuron (top) and the action potential at one point on its axon (bottom). Once depolarisation\n"
            "reaches the threshold, the impulse travels from the axon hillock to the terminals, jumping between nodes of Ranvier",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/medical") -> Path:
    return render_all(diagram(), output_dir, "06_neuron_action_potential")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/medical"))
