"""One-compartment pharmacokinetics: IV bolus and first-order oral absorption.

IV bolus:  C(t) = (D / V) e^{-k t}.  Oral:  C(t) = F D k_a / (V (k_a - k)) (e^{-k t} - e^{-k_a t}).
Illustrative drug: D = 500 mg, V = 50 L, k = 0.173 /h so that t_half = ln 2 / k = 4.0 h;
k_a = 0.5 /h, F = 0.8. Concentration is on a log axis, so the elimination phase is straight.
"""
import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

INK = "#1F2F57"
RED, BLUE, AMBER = "#B03A3A", "#2F5FA8", "#8A5A00"
D, V, F = 500.0, 50.0, 0.8        # mg, L, oral bioavailability
T_HALF = 4.0                      # h
K = math.log(2) / T_HALF          # 1/h
KA = 0.5                          # 1/h
C0 = D / V                        # mg/L at t = 0 after the bolus


def iv(t):
    return C0 * math.exp(-K * t)


def oral(t):
    return F * D * KA / (V * (KA - K)) * (math.exp(-K * t) - math.exp(-KA * t))


def diagram() -> Diagram:
    tmax = math.log(KA / K) / (KA - K)    # time of peak oral concentration
    cmax = oral(tmax)
    with Diagram("Pharmacokinetic concentration-time curves", theme="paper") as diag:
        pl = Plot(diag, x=(0, 24), y=(0.1, 20), origin=(110, 440), size=(620, 330), yscale="log")
        pl.grid(xstep=4)
        pl.axes(xlabel="Time (h)", ylabel="Plasma concentration $C$ (mg/L)", xstep=4, through_zero=False, arrows=False,
                ytick_labels={0.1: "0.1", 0.2: "0.2", 0.5: "0.5", 1: "1", 2: "2", 5: "5", 10: "10", 20: "20"})
        pl.function(iv, lo=0, hi=24, stroke=RED, width=2.4)
        pl.function(oral, lo=0, hi=24, stroke=BLUE, width=2.4)
        # Half-life: C falls from C0 to C0/2 in T_HALF (read off the IV curve at two successive halvings).
        for n in range(3):
            t = n * T_HALF
            pl.dot(t, iv(t), radius=3.5)
            pl.line((t, iv(t)), (t + T_HALF, iv(t)), stroke=AMBER, dash="5,4")
            pl.line((t + T_HALF, iv(t)), (t + T_HALF, iv(t) / 2), stroke=AMBER, dash="5,4")
        pl.dot(3 * T_HALF, iv(3 * T_HALF), radius=3.5)
        pl.label(T_HALF, C0 * 0.71, "$t_{1/2} = 4$ h", size=12, anchor="left_center", dx=6, color=AMBER)
        pl.label(0, C0, f"$C_0 = D/V = {C0:g}$ mg/L", size=12, anchor="bottom_left", dx=8, dy=-8)
        pl.dot(tmax, cmax, radius=4.0)
        pl.label(tmax, cmax, "$C_{\\max}$", size=12, anchor="bottom_right", dx=-6, dy=-6, color=BLUE)
        pl.label(19, iv(19), "IV bolus", size=13, anchor="top_right", dx=0, dy=12, color=RED)
        pl.label(14, oral(14), "Oral", size=13, anchor="bottom_right", dx=0, dy=-10, color=BLUE)
        diag.text(
            "IV: $C = (D/V)\\,e^{-kt}$\n"
            "Oral: $C = F D k_a (e^{-kt} - e^{-k_a t}) / [V (k_a - k)]$\n"
            f"$D = {D:g}$ mg, $V = {V:g}$ L, $F = {F:g}$\n"
            f"$k = \\ln 2 / t_{{1/2}} = {K:.3f}$ h$^{{-1}}$, $k_a = {KA:g}$ h$^{{-1}}$\n"
            f"$C_{{\\max}} = {cmax:.1f}$ mg/L at $t_{{\\max}} = {tmax:.1f}$ h\n"
            f"AUC (oral) $= F D / (V k) = {F * D / (V * K):.0f}$ mg$\\cdot$h/L",
            size=12,
        ).at(770, 140, anchor="top_left")
        diag.caption(
            "**Figure 4:** One-compartment pharmacokinetics on a log axis. After an IV bolus concentration halves every\n"
            "$t_{1/2}$ = 4 h; after oral dosing it rises at rate $k_a$ to $C_{\\max}$, then declines parallel to the IV curve",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/medical") -> Path:
    return render_all(diagram(), output_dir, "04_pharmacokinetics")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/medical"))
