"""The PCR cycle and the thermocycler temperature trace that drives it.

Each cycle has three steps: denaturation (about 95 C, double strand to single strands), annealing
(about 55-65 C, primers bind their complementary sites) and extension (72 C, Taq polymerase extends
each primer 5' to 3'). Cycles repeat 25-35 times; each ideally doubles the target, so n cycles give 2^n
copies. The trace below shows an initial denaturation, three full cycles (hold times and ramps), a break
for the cycles not drawn, then final extension and a 4 °C hold. Time is to scale only up to the break.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
RED, BLUE, GREEN = "#B03A3A", "#2F5FA8", "#2E6B3F"
BOX = Style(fill="#DCE6F2", stroke=INK, stroke_width=1.6, radius=8)
DENAT_T, ANNEAL_T, EXTEND_T, HOLD_T = 95.0, 58.0, 72.0, 4.0
PERIOD = 2.9      # minutes per cycle
T0 = 3.6          # end of initial denaturation
BREAK = (T0 + 3 * PERIOD, 14.2)   # trace resumes after the cycles that are not drawn


def cycle(t):
    """Trace points of one cycle starting at time t (min) at 95 C, with colour per hold."""
    return [
        ((t, DENAT_T), (t + 0.5, DENAT_T), RED),
        ((t + 0.5, DENAT_T), (t + 0.8, ANNEAL_T), INK),
        ((t + 0.8, ANNEAL_T), (t + 1.3, ANNEAL_T), BLUE),
        ((t + 1.3, ANNEAL_T), (t + 1.5, EXTEND_T), INK),
        ((t + 1.5, EXTEND_T), (t + 2.5, EXTEND_T), GREEN),
        ((t + 2.5, EXTEND_T), (t + 2.9, DENAT_T), INK),
    ]


def strands(diag, x, y, state):
    """A tiny 5'/3' schematic of the two template strands in the given step."""
    w = 200.0
    gap = 14.0 if state == "denature" else 46.0
    top, bot = y, y + gap
    line = Style(stroke="#444444", stroke_width=2.2)
    diag.polyline([(x, top), (x + w, top)], style=line)
    diag.polyline([(x, bot), (x + w, bot)], style=line)
    if state == "denature":  # shown as the intact duplex that is about to melt: rungs
        for k in range(0, 11):
            diag.polyline([(x + 10 + k * 18, top), (x + 10 + k * 18, bot)], style=Style(stroke="#8A93A8", stroke_width=1.2))
    diag.text("5'", size=10).at(x - 6, top, anchor="right_center")
    diag.text("3'", size=10).at(x + w + 6, top, anchor="left_center")
    diag.text("3'", size=10).at(x - 6, bot, anchor="right_center")
    diag.text("5'", size=10).at(x + w + 6, bot, anchor="left_center")
    if state == "anneal":
        # Forward primer pairs with the bottom strand (left); reverse primer pairs with the top strand (right).
        diag.polyline([(x + 6, bot - 7), (x + 54, bot - 7)], style=Style(stroke=RED, stroke_width=4.0))
        diag.polyline([(x + w - 6, top + 7), (x + w - 54, top + 7)], style=Style(stroke=RED, stroke_width=4.0))
    if state == "extend":
        diag.connect((x + 6, bot - 7), (x + w - 8, bot - 7), routing="direct", width=3.4, color=GREEN, head="stealth")
        diag.connect((x + w - 6, top + 7), (x + 8, top + 7), routing="direct", width=3.4, color=GREEN, head="stealth")
        diag.polyline([(x + 6, bot - 7), (x + 54, bot - 7)], style=Style(stroke=RED, stroke_width=4.0), z=2)
        diag.polyline([(x + w - 6, top + 7), (x + w - 54, top + 7)], style=Style(stroke=RED, stroke_width=4.0), z=2)


def diagram() -> Diagram:
    copies = 2 ** 30
    with Diagram("PCR cycle and thermocycler trace", theme="paper") as diag:
        # ---------------------------------------------------------- the three steps
        steps = [
            ("**1  Denaturation**\n95 °C, 15-30 s", "denature", "heat separates the two strands"),
            ("**2  Annealing**\n55-65 °C, 15-30 s", "anneal", "primers (red) bind their target sites"),
            ("**3  Extension**\n72 °C, about 1 min per kb", "extend", "Taq polymerase extends each primer 5' to 3'"),
        ]
        xs = [110.0, 410.0, 710.0]
        boxes = []
        for (label, state, note), x in zip(steps, xs):
            b = diag.shape(label, 220, 56, style=BOX, fit_label=False).at(x + 100, 120, anchor="center")
            boxes.append(b)
            strands(diag, x, 195 if state != "denature" else 205, state)
            diag.text(note, size=11, color="#333333").at(x + 100, 270, anchor="top_center")
        diag.connect(boxes[0], boxes[1], routing="direct", width=2.2, color=INK, head="stealth")
        diag.connect(boxes[1], boxes[2], routing="direct", width=2.2, color=INK, head="stealth")
        diag.connect(boxes[2].anchor("top", 0.5), boxes[0].anchor("top", 0.5), routing="orthogonal", width=2.2, color=INK, head="stealth",
                     via=[(xs[2] + 100, 62), (xs[0] + 100, 62)])
        diag.text("repeat 25-35 cycles", size=12).at((xs[0] + xs[2]) / 2 + 100, 56, anchor="bottom_center")
        diag.text(f"Each cycle ideally doubles the target: $n$ cycles give $2^n$ copies ($2^{{30}} = {copies:,}$)", size=12, color="#333333").at(110, 300, anchor="top_left")

        # ---------------------------------------------------------- temperature trace
        p = Plot(diag, x=(0, 22.6), y=(0, 110), origin=(110, 640), size=(820, 270))
        p.grid(xstep=2, ystep=20)
        p.axes(ylabel="Block temperature ($^\\circ$C)", ystep=20, xstep=2, through_zero=False, arrows=False, xlabels=False)
        for t in range(2, 14, 2):
            if t <= BREAK[0] + 0.01:
                p.label(t, 0, str(t), size=11, anchor="top_center", dy=6)
        p.label(11.3, 0, "min", size=11, anchor="top_left", dx=40, dy=6)
        for temp in (DENAT_T, ANNEAL_T, EXTEND_T):
            p.hline(temp, stroke="#C9CFDC", dash="2,5")
        # Initial denaturation.
        p.polyline([(0, 25), (0.6, DENAT_T)], stroke=INK, width=2.2)
        p.polyline([(0.6, DENAT_T), (T0, DENAT_T)], stroke=RED, width=3.2)
        p.label(1.9, DENAT_T, "initial denaturation 3 min", size=11, anchor="bottom_center", dy=-6)
        for n in range(3):
            for a, b, colour in cycle(T0 + n * PERIOD):
                p.polyline([a, b], stroke=colour, width=3.2 if colour != INK else 2.0)
        # Break in the time axis for the undrawn cycles.
        p.polyline([(BREAK[0], DENAT_T), (BREAK[1], DENAT_T)], stroke=INK, width=1.6, dash="3,4")
        p.label((BREAK[0] + BREAK[1]) / 2, DENAT_T, "cycles 4 to n (time axis broken)", size=11, anchor="bottom_center", dy=-6)
        bx = p.px((BREAK[0] + BREAK[1]) / 2, 0)
        for dx in (-4, 4):
            diag.polyline([(bx[0] + dx - 4, bx[1] - 8), (bx[0] + dx + 4, bx[1] + 8)], style=Style(stroke=INK, stroke_width=1.4))
        # Final extension and hold.
        p.polyline([(BREAK[1], DENAT_T), (BREAK[1] + 0.4, EXTEND_T)], stroke=INK, width=2.0)
        p.polyline([(BREAK[1] + 0.4, EXTEND_T), (19.4, EXTEND_T)], stroke=GREEN, width=3.2)
        p.polyline([(19.4, EXTEND_T), (20.4, HOLD_T)], stroke=INK, width=2.0)
        p.polyline([(20.4, HOLD_T), (22.4, HOLD_T)], stroke=BLUE, width=3.2)
        p.label(16.9, EXTEND_T, "final extension 5 min", size=11, anchor="bottom_center", dy=-6)
        p.label(21.6, HOLD_T, "hold 4 °C", size=11, anchor="bottom_center", dy=-8)
        c = T0 + PERIOD
        p.label(c + 0.25, DENAT_T, "denature", size=11, anchor="bottom_center", dy=-6, color=RED)
        p.label(c + 1.05, ANNEAL_T, "anneal", size=11, anchor="top_center", dy=8, color=BLUE)
        p.label(c + 2.0, EXTEND_T, "extend", size=11, anchor="bottom_center", dy=-6, color=GREEN)
        diag.caption(
            "**Figure 9:** PCR. Repeated heat-anneal-extend cycles in a thermocycler double the target region each time;\n"
            "the temperature trace shows the initial denaturation, three cycles, then final extension and a 4 °C hold",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "09_pcr_thermocycling")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
