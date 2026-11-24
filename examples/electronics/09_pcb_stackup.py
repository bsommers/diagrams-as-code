"""A 4-layer PCB stackup in cross-section, with three via types and a microstrip impedance.

The stack is signal / ground / power / signal (1.6 mm). Layer thicknesses are
data, so the total, the copper weights and the microstrip impedance
(IPC-2141 formula, trace over the 0.2 mm prepreg) are computed from them. The
drawing is not to scale: thin layers are drawn at least 10 px tall so they stay legible.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#111111"
WIRE = Style(fill="none", stroke=INK, stroke_width=2.0)
WHITE = Style(fill="#FFFFFF", stroke=INK, stroke_width=2.0)


def seg(*pts) -> str:
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def frame(a, b):
    """Length of a->b and a map from local (along, across) to canvas points."""
    (x0, y0), (x1, y1) = a, b
    n = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    return n, lambda u, v: (x0 + u * ux - v * uy, y0 + u * uy + v * ux)


# (key, label, thickness in mm, drawn height in px, fill)
MASK_F, CU_F, PRE_F, CORE_F = "#6FAE74", "#C98A3C", "#F0E6B8", "#E3D18F"
LAYERS = [
    ("mask_t", "Solder mask", 0.025, 14, MASK_F),
    ("L1", "L1 top: signal", 0.035, 18, CU_F),
    ("pre_t", "Prepreg 1080, $\\varepsilon_r$ = 4.2", 0.200, 44, PRE_F),
    ("L2", "L2: GND plane", 0.0175, 16, CU_F),
    ("core", "Core FR-4, $\\varepsilon_r$ = 4.5", 1.045, 130, CORE_F),
    ("L3", "L3: PWR plane", 0.0175, 16, CU_F),
    ("pre_b", "Prepreg 1080, $\\varepsilon_r$ = 4.2", 0.200, 44, PRE_F),
    ("L4", "L4 bottom: signal", 0.035, 18, CU_F),
    ("mask_b", "Solder mask", 0.025, 14, MASK_F),
]
COPPER_OZ = {"L1": 1.0, "L2": 0.5, "L3": 0.5, "L4": 1.0}     # 1 oz = 35 um
X0, X1, Y0 = 110.0, 560.0, 100.0
PAD, HOLE, CLEAR = 22.0, 10.0, 26.0                           # pad / hole half widths, antipad half width
INK_L, GREY = "#333333", "#555555"
EPS_PRE, W_TRACE, DRILL = 4.2, 0.35, 0.30                     # relative permittivity, trace width mm, via drill mm
# (name, x, first layer, last layer, plane layers it touches)
VIAS = [("through via", 200.0, "L1", "L4", {"L1", "L4"}),
        ("blind via to GND", 300.0, "L1", "L2", {"L1", "L2"}),
        ("blind via to PWR", 400.0, "L1", "L3", {"L1", "L3"})]


def microstrip_z0(h: float, w: float, t: float, er: float) -> float:
    return 87 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))


def diagram() -> Diagram:
    total = sum(t for _, _, t, _, _ in LAYERS)
    ys, y = {}, Y0
    for key, _, _, h, _ in LAYERS:
        ys[key] = (y, y + h)
        y += h
    h_pre, t_cu = 0.200, 0.035
    z0 = microstrip_z0(h_pre, W_TRACE, t_cu, EPS_PRE)
    stack_order = [k for k, *_ in LAYERS]
    with Diagram("Four-layer PCB stackup and via types", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=13, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        def rect(xa, ya, xb, yb, fill, stroke=INK_L, width=1.0, z=0):
            diag.polygon([(xa, ya), (xb, ya), (xb, yb), (xa, yb)], style=Style(fill=fill, stroke=stroke, stroke_width=width), z=z)

        trace_x = (450.0, 540.0)
        for key, label, thick, h, fill in LAYERS:
            ya, yb = ys[key]
            if key in ("L1", "L4"):
                # signal layers: a pad at each via that reaches the layer, plus one trace on L1
                spans = [(vx - PAD, vx + PAD) for _, vx, a, b, ends in VIAS if key in ends]
                if key == "L1":
                    spans.append((trace_x[0], trace_x[1]))
                for xa, xb in spans:
                    rect(xa, ya, xb, yb, fill)
            elif key in ("L2", "L3"):
                # planes: full width, except an antipad where a via passes through without touching
                gaps = sorted((vx - CLEAR, vx + CLEAR) for _, vx, a, b, _ in VIAS
                              if stack_order.index(a) < stack_order.index(key) < stack_order.index(b))
                edge = X0
                for ga, gb in gaps + [(X1, X1)]:
                    if ga > edge:
                        rect(edge, ya, ga, yb, fill)
                    edge = gb
            else:
                rect(X0, ya, X1, yb, fill)
            # label with a short leader
            yc = (ya + yb) / 2
            diag.path(seg((X1 + 4, yc), (X1 + 24, yc)), style=Style(fill="none", stroke=GREY, stroke_width=0.8), obstacle=False)
            if key in COPPER_OZ:
                tag = f"{label}: Cu {COPPER_OZ[key]:g} oz, {thick * 1e3:g} $\\mu$m"
            else:
                tag = f"{label}, {thick:g} mm"
            text(tag, X1 + 30, yc, anchor="left_center", size=12)
        # vias: hole, then the two plated walls
        for name, vx, a, b, ends in VIAS:
            top, bot = ys[a][0], ys[b][1]
            rect(vx - HOLE, top, vx + HOLE, bot, "#FFFFFF", stroke="none", width=0.0, z=2)
            rect(vx - HOLE, top, vx - HOLE + 3.5, bot, CU_F, stroke="none", width=0.0, z=3)
            rect(vx + HOLE - 3.5, top, vx + HOLE, bot, CU_F, stroke="none", width=0.0, z=3)
            text(name, vx, Y0 - 24, size=12)
            diag.path(seg((vx, Y0 - 14), (vx, top)), style=Style(fill="none", stroke=GREY, stroke_width=0.8, dash="2,3"), obstacle=False)
        # microstrip dimensions
        tx = (trace_x[0] + trace_x[1]) / 2
        text(f"$w$ = {W_TRACE:g} mm", tx, ys["L1"][0] - 22, anchor="bottom_center", size=12)
        ya, yb = ys["L1"][1], ys["L2"][0]
        dx = trace_x[1] - 14
        diag.path(seg((dx, ya), (dx, yb)) + f" M {dx - 3} {ya + 7} L {dx} {ya} L {dx + 3} {ya + 7}"
                  + f" M {dx - 3} {yb - 7} L {dx} {yb} L {dx + 3} {yb - 7}",
                  style=Style(fill="none", stroke=INK, stroke_width=1.0), z=5, obstacle=False)
        text(f"$h$ = {h_pre:g} mm", trace_x[1] - 22, (ya + yb) / 2, anchor="right_center", size=12)

        text(
            f"**Stackup:** {len(COPPER_OZ)} copper layers, total thickness = {total:.3f} mm\n"
            f"mask {2 * 0.025:.3f} + copper {sum(COPPER_OZ[k] * 0.035 for k in COPPER_OZ):.3f} + prepreg {2 * 0.2:.3f} + core {1.045:.3f} mm\n"
            f"**Microstrip on L1** over the L2 ground plane (IPC-2141):\n"
            f"$Z_0 = \\dfrac{{87}}{{\\sqrt{{\\varepsilon_r + 1.41}}}} \\ln \\dfrac{{5.98\\,h}}{{0.8\\,w + t}}"
            f" = {z0:.1f}\\,\\Omega$ with $h$ = {h_pre:g}, $w$ = {W_TRACE:g}, $t$ = {t_cu:g} mm, $\\varepsilon_r$ = {EPS_PRE:g}\n"
            f"Through-via aspect ratio = {total:.1f} mm / {DRILL:g} mm drill = {total / DRILL:.1f}:1\n"
            "A buried L2-L3 via would short GND to PWR, so this stack uses none.",
            X0, ys["mask_b"][1] + 40, anchor="top_left", size=13)
        diag.caption("**Figure 9:** A signal / ground / power / signal 4-layer stackup with through and blind vias (not to scale)",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "09_pcb_stackup")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
