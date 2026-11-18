"""The eukaryotic cell cycle drawn as a ring, with checkpoints and the cyclin-CDK driver.

Arc spans are proportional to the duration of each phase in a typical 24-hour human cell
line: G1 11 h, S 8 h, G2 4 h, M 1 h; G0 is an exit branch. Angles are computed from the hours.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
RED = "#B03A3A"
CX, CY, R_OUT, R_IN = 380.0, 330.0, 170.0, 105.0
PHASES = [  # name, hours, fill, note
    ("G1", 11.0, "#CFE0F3", "growth, normal function"),
    ("S", 8.0, "#F4D9A8", "DNA replication"),
    ("G2", 4.0, "#D7EBCB", "growth, prepares for division"),
    ("M", 1.0, "#F0C4C4", "mitosis and cytokinesis"),
]
TOTAL = sum(h for _, h, _, _ in PHASES)


def polar(r: float, theta: float):
    """Point at radius r and clockwise angle theta (degrees, 0 = top)."""
    a = math.radians(theta)
    return (CX + r * math.sin(a), CY - r * math.cos(a))


def arc_poly(a0: float, a1: float, r0: float, r1: float, step: float = 3.0):
    n = max(2, int((a1 - a0) / step))
    outer = [polar(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    inner = [polar(r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return outer + inner


def diagram() -> Diagram:
    with Diagram("Cell cycle", theme="paper") as diag:
        k = Draft(diag)
        angle = 0.0
        spans = {}
        for name, hours, fill, note in PHASES:
            span = 360.0 * hours / TOTAL
            spans[name] = (angle, angle + span)
            diag.polygon(arc_poly(angle, angle + span, R_IN, R_OUT), style=Style(fill=fill, stroke=INK, stroke_width=1.6))
            mid = angle + span / 2
            if name != "M":
                p = polar((R_IN + R_OUT) / 2, mid)
                diag.text(f"**{name}**\n{hours:g} h", size=15).at(p[0], p[1], anchor="center")
            angle += span
        diag.text("**Interphase**\nG1 + S + G2\n23 h", size=14).at(CX, CY - 10, anchor="center")
        diag.text("**M**  1 h", size=14).at(CX, CY + 50, anchor="center")
        # Direction of progress: clockwise arrow just outside the ring.
        diag.connect(polar(R_OUT + 14, 100), polar(R_OUT + 14, 130), routing="direct", width=1.8, color=INK, head="stealth")
        # Phase notes (radial leaders to labels outside the ring).
        for name, ang, side in (("G1", 80, 1), ("S", 225, -1), ("G2", 305, -1)):
            text = f"{name}: {PHASES[[n for n, *_ in PHASES].index(name)][3]}"
            k.leader(polar(R_OUT - 4, ang), polar(R_OUT + 40, ang), text, anchor="left_center" if side > 0 else "right_center")
        m_mid = sum(spans["M"]) / 2
        k.leader(polar(R_OUT - 3, m_mid), polar(R_OUT + 40, m_mid), "M: mitosis and cytokinesis", anchor="bottom_left")
        # Checkpoints: red bars across the ring with labelled leaders.
        for ang, text, end, anchor in (
            (spans["G1"][1], "G1/S checkpoint (DNA intact? cell large enough?)", (CX + 150, CY + R_OUT + 60), "left_center"),
            (spans["G2"][1], "G2/M checkpoint (DNA fully replicated?)", (CX - 135, CY - R_OUT - 52), "right_center"),
        ):
            a, b = polar(R_IN - 8, ang), polar(R_OUT + 8, ang)
            diag.path(f"M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}", style=Style(fill="none", stroke=RED, stroke_width=3.2), z=3)
            k.leader(b, end, text, anchor=anchor, dot=False)
        # Exit to quiescence from G1 (a branch off the ring).
        g0a, g0b = polar(R_OUT + 4, 35), polar(R_OUT + 52, 35)
        diag.connect(g0a, g0b, routing="direct", width=1.6, color=INK, head="stealth", style="dashed")
        diag.text("$G_0$ (quiescent)", size=12).at(g0b[0] + 6, g0b[1] - 2, anchor="left_center")
        diag.caption(
            "**Figure 8:** The cell cycle. Interphase (G1, S, G2) takes 23 h of a 24-h cycle and mitosis (M) 1 h; arc length is proportional to duration.\n"
            "Red bars mark checkpoints where the cycle halts if DNA is damaged or incomplete",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/medical") -> Path:
    return render_all(diagram(), output_dir, "08_cell_cycle")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/medical"))
