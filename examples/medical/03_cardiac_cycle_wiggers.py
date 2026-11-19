"""Wiggers diagram: ECG, aortic, ventricular and atrial pressure and ventricular volume.

Every trace is computed from a simple piecewise model of one 0.8 s cycle (75 beats/min)
using textbook magnitudes: aortic pressure 80 to 120 mmHg, end-diastolic volume 120 mL,
end-systolic volume 50 mL (stroke volume 70 mL). Time zero is the R wave.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import ecg_beat
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
RED, BLUE, GREEN, PURPLE = "#B03A3A", "#2F5FA8", "#2E6B3F", "#6B3F8A"
CYCLE = 0.8
T_IVC, T_AO, T_AC, T_MO = 0.0, 0.05, 0.35, 0.43   # mitral close, aortic open/close, mitral open


def sm(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def gauss(t, mu, s, a):
    return a * math.exp(-((t - mu) / s) ** 2)


def lv_pressure(t: float) -> float:
    if t < T_AO:                                   # isovolumic contraction
        return 8 + 72 * sm(t / T_AO)
    if t < T_AC:                                   # ejection
        u = (t - T_AO) / (T_AC - T_AO)
        return 80 + 20 * u + 30 * math.sin(math.pi * u ** 0.8)
    if t < T_MO:                                   # isovolumic relaxation
        return 100 - 95 * sm((t - T_AC) / (T_MO - T_AC))
    return 5 + 3 * (t - T_MO) / (CYCLE - T_MO) + gauss(t, 0.75, 0.03, 4)   # filling + atrial kick


def aortic_pressure(t: float) -> float:
    if T_AO <= t < T_AC:
        return lv_pressure(t) - 2
    tt = t - T_AC if t >= T_AC else t + CYCLE - T_AC
    p = 80 + 20 * math.exp(-tt / 0.12)
    if t >= T_AC:
        p -= 5 * math.exp(-(t - T_AC) / 0.02)      # dicrotic notch
    return p


def atrial_pressure(t: float) -> float:
    s = 0.10 if t < 0.41 else 0.03
    return 7 + gauss(t, 0.75, 0.03, 5) + gauss(t, 0.04, 0.015, 2) + 7 * math.exp(-((t - 0.41) / s) ** 2)


def lv_volume(t: float) -> float:
    if t < T_AO:
        return 120.0
    if t < T_AC:
        return 120 - 70 * sm(((t - T_AO) / (T_AC - T_AO)) ** 0.8)
    if t < T_MO:
        return 50.0
    if t < 0.55:
        return 50 + 55 * sm((t - T_MO) / (0.55 - T_MO))
    if t < 0.70:
        return 105 + 7 * (t - 0.55) / 0.15
    return 112 + 8 * sm((t - 0.70) / 0.10)


def ecg(t: float) -> float:
    return ecg_beat(((t - 0.015) / CYCLE + 0.31) % 1.0)


def diagram() -> Diagram:
    ox, w = 120.0, 760.0
    with Diagram("Wiggers diagram of the cardiac cycle", theme="paper") as diag:
        e = Plot(diag, x=(0, CYCLE), y=(-0.4, 1.1), origin=(ox, 165), size=(w, 75))
        p = Plot(diag, x=(0, CYCLE), y=(0, 140), origin=(ox, 410), size=(w, 200))
        v = Plot(diag, x=(0, CYCLE), y=(40, 150), origin=(ox, 560), size=(w, 110))
        # Phase bands behind everything.
        bands = [(0.0, T_AO, "#F2D9D9"), (T_AO, T_AC, "#F8ECEC"), (T_AC, T_MO, "#DDE6F4"), (T_MO, CYCLE, "#EEF3FA")]
        for a, b, colour in bands:
            x0, x1 = e.px(a, 0)[0], e.px(b, 0)[0]
            diag.polygon([(x0, 100), (x1, 100), (x1, 560), (x0, 560)], style=Style(fill=colour, stroke=colour, stroke_width=0), z=-5)
        for n, (a, b, _) in enumerate(bands, start=1):
            diag.text(str(n), size=13, color=INK).at(e.px((a + b) / 2, 0)[0], 90, anchor="center")
        for name, t in (("MC", T_IVC), ("AO", T_AO), ("AC", T_AC), ("MO", T_MO)):
            x = e.px(t, 0)[0]
            diag.path(f"M {x:.1f} 100 V 560", style=Style(fill="none", stroke="#6B7390", stroke_width=0.8, dash="3,3"), z=-1)
            diag.text(name, size=11, color=INK).at(x, 72, anchor="center")
        # ECG.
        diag.text("ECG", size=13).at(ox - 12, 135, anchor="right_center")
        e.axes(through_zero=False, labels=False, xlabels=False, arrows=False)
        e.function(ecg, stroke="#111111", width=1.8, n=800)
        # Pressures.
        diag.text("Pressure (mmHg)", size=12).at(ox + 8, 195, anchor="left_center")
        p.axes(ystep=40, through_zero=False, xlabels=False, arrows=False)
        p.function(aortic_pressure, stroke=RED, width=2.2, n=800)
        p.function(lv_pressure, stroke=BLUE, width=2.2, n=800)
        p.function(atrial_pressure, stroke=GREEN, width=2.2, n=800)
        p.label(0.58, 80, "Aortic", size=12, anchor="bottom_center", dy=-6, color=RED)
        p.label(0.23, 127, "Left ventricular", size=12, anchor="left_center", color=BLUE)
        p.label(0.60, 22, "Left atrial", size=12, anchor="bottom_center", dy=-4, color=GREEN)
        # Volume.
        v.axes(xlabel="Time (s)", xstep=0.1, ystep=40, through_zero=False, arrows=False)
        v.function(lv_volume, stroke=PURPLE, width=2.2, n=800)
        v.label(0.0, 149, "Ventricular volume (mL)", size=12, anchor="left_center", dx=8)
        v.label(0.0, 120, "EDV 120 mL", size=12, anchor="bottom_left", dx=6, dy=-4)
        v.label(0.37, 50, "ESV 50 mL", size=12, anchor="bottom_center", dy=-8)
        v.label(0.47, 66, "$\\mathrm{SV} = \\mathrm{EDV} - \\mathrm{ESV} = 70$ mL", size=12, anchor="left_center", dx=24)
        # Key to the phases.
        diag.text(
            "Phases: 1 isovolumic contraction; 2 ejection; 3 isovolumic relaxation; 4 filling (rapid, diastasis, atrial systole)\n"
            "Valves: MC mitral closes; AO aortic opens; AC aortic closes; MO mitral opens",
            size=12,
        ).at(ox, 612, anchor="top_left")
        diag.caption(
            "**Figure 3:** Wiggers diagram of one cardiac cycle (0.8 s, 75 beats/min). The ventricle ejects while its pressure\n"
            "exceeds the aortic, and the aortic valve closing produces the dicrotic notch",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/medical") -> Path:
    return render_all(diagram(), output_dir, "03_cardiac_cycle_wiggers")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/medical"))
