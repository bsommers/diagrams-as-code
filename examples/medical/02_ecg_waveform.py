"""One cardiac cycle on ECG paper with the P, QRS and T waves and the standard intervals.

Waveform from the Draft helper's `ecg_beat` (Gaussian P, Q, R, S and T components);
the cycle is taken as 0.8 s (75 beats/min). Grid: small box 0.04 s by 0.1 mV, large box
0.2 s by 0.5 mV. Interval durations are computed from the wave phases.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft, ecg_beat
from diagrams_as_code.output import render_all

INK = "#1F2F57"
RED = "#B03A3A"
CYCLE = 0.8            # seconds per beat
BX, BY = 34.0, 22.0    # pixels per small box: 0.04 s wide, 0.1 mV high
OX, BASE = 140.0, 330.0
WIDTH = 20 * BX        # 0.8 s
AMP = 10 * BY          # 1.0 mV


def tx(phase):
    return OX + WIDTH * phase


def ty(phase):
    return BASE - AMP * ecg_beat(phase)


def diagram() -> Diagram:
    with Diagram("ECG waveform and intervals", theme="paper") as diag:
        k = Draft(diag)
        top, bot = BASE - 11 * BY, BASE + 7 * BY
        # ECG paper.
        minor, major = [], []
        for i in range(21):
            (major if i % 5 == 0 else minor).append(f"M {OX + i * BX:.1f} {top:.1f} V {bot:.1f}")
        for j in range(-7, 12):
            y = BASE - j * BY
            (major if j % 5 == 0 else minor).append(f"M {OX:.1f} {y:.1f} H {OX + WIDTH:.1f}")
        diag.path(" ".join(minor), style=Style(fill="none", stroke="#F0D4D4", stroke_width=0.6), z=-3)
        diag.path(" ".join(major), style=Style(fill="none", stroke="#DDA9A9", stroke_width=1.0), z=-2)
        # Axis ticks.
        for i in range(0, 21, 5):
            diag.text(f"{i * 0.04:.1f}", size=11).at(OX + i * BX, bot + 12, anchor="center")
        diag.text("Time (s)", size=12).at(OX + WIDTH / 2, bot + 32, anchor="center")
        for mv in (-0.5, 0.0, 0.5, 1.0):
            diag.text(f"{mv:g}", size=11).at(OX - 8, BASE - mv * AMP, anchor="right_center")
        diag.text("Voltage (mV)", size=12).at(OX - 50, top - 14, anchor="left_center")
        # Trace.
        k.wave((OX, BASE), WIDTH, AMP, ecg_beat, beats=1, samples=400, stroke="#111111", line=2.0)
        # Wave labels.
        k.leader((tx(0.16), ty(0.16)), (tx(0.10), BASE - 120), "P", anchor="bottom_center", dot=True)
        k.leader((tx(0.285), ty(0.285)), (tx(0.215), BASE + 85), "Q", anchor="center", dot=True)
        k.leader((tx(0.31), ty(0.31)), (tx(0.40), top + 10), "R", anchor="left_center", dot=True)
        k.leader((tx(0.335), ty(0.335)), (tx(0.395), BASE + 85), "S", anchor="center", dot=True)
        k.leader((tx(0.55), ty(0.55)), (tx(0.62), BASE - 150), "T", anchor="bottom_left", dot=True)
        # Intervals (phases of onset / offset read from the Gaussian components).
        p_on, q_on, qrs_off, t_off = 0.10, 0.26, 0.36, 0.65
        rows = [bot + 58, bot + 92, bot + 126]
        diag.text("PR segment", size=11).at(tx(0.225), BASE - 70, anchor="bottom_center")
        diag.path(f"M {tx(0.225):.1f} {BASE - 68:.1f} V {BASE - 2:.1f}", style=Style(fill="none", stroke=INK, stroke_width=0.8), z=2)
        diag.text("ST segment", size=11).at(tx(0.40), BASE - 14, anchor="bottom_center")
        spans = [
            (p_on, q_on, f"PR interval {(q_on - p_on) * CYCLE:.2f} s"),
            (q_on, qrs_off, f"QRS duration {(qrs_off - q_on) * CYCLE:.2f} s"),
            (q_on, t_off, f"QT interval {(t_off - q_on) * CYCLE:.2f} s"),
        ]
        guides = []
        for ph in (p_on, q_on, qrs_off, t_off):
            guides.append(f"M {tx(ph):.1f} {BASE:.1f} V {rows[-1]:.1f}")
        diag.path(" ".join(guides), style=Style(fill="none", stroke="#555555", stroke_width=0.7, dash="3,3"), z=1)
        for (a, b, text), y in zip(spans, rows):
            k.dimension((tx(a), y), (tx(b), y), text, offset=0, side=-1, ext_gap=0, ext_over=0)
        diag.caption(
            "**Figure 2:** One cardiac cycle on ECG paper (0.8 s, 75 beats/min). The P wave is atrial\n"
            "depolarisation, the QRS complex ventricular depolarisation and the T wave ventricular\n"
            "repolarisation; intervals are measured from wave onsets",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/medical") -> Path:
    return render_all(diagram(), output_dir, "02_ecg_waveform")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/medical"))
