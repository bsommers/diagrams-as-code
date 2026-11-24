"""Residence time distributions for an ideal CSTR, three CSTRs in series and a PFR.

In dimensionless time theta = t / tau the exit-age density is
E(theta) = exp(-theta) for one CSTR, E = N (N theta)^(N-1) exp(-N theta) / (N-1)!
for N tanks in series (N = 3 here), and a Dirac delta at theta = 1 for plug flow.
The cumulative curve is F(theta) = integral of E. For a first-order reaction
with k tau = 2 the conversion is X = 1 - integral E(theta) exp(-k tau theta) dtheta,
which the script integrates numerically and checks against the closed forms
(CSTR: k tau/(1 + k tau); N tanks: 1 - (1 + k tau/N)^-N; PFR: 1 - exp(-k tau)).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

# --- ISO 10628-style schematic symbols (drawn from primitives; no icon catalog) ---
INK = "#1A1A1A"
BLUE = "#2F5F9E"
EQUIP = Style(fill="#EEF2F6", stroke=INK, stroke_width=1.6)
WHITE = Style(fill="#FFFFFF", stroke=INK, stroke_width=1.4)
PIPE = {"width": 1.8, "color": INK}
SIGNAL = {"width": 1.2, "color": BLUE, "style": "dashed"}


def _arc(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def vessel(d, cx, top, bot, w, cap=None, style=EQUIP):
    """Vertical vessel with elliptical heads."""
    r, cap = w / 2, cap or w * 0.3
    pts = _arc(cx, top + cap, r, cap, 0, -math.pi) + _arc(cx, bot - cap, r, cap, math.pi, 0)
    d.polygon(pts, style=style, z=1)


def circle(d, cx, cy, r, style=WHITE, z=1):
    d.polygon(_arc(cx, cy, r, r, 0, 2 * math.pi, 32), style=style, z=z)


def valve(d, x, y, s=11.0):
    d.polygon([(x - s, y - 0.62 * s), (x + s, y + 0.62 * s), (x + s, y - 0.62 * s), (x - s, y + 0.62 * s)],
              style=WHITE, z=2)


def control_valve(d, x, y, s=11.0):
    """Valve body with a diaphragm actuator on a stem above it."""
    d.polyline([(x, y), (x, y - 1.5 * s)], style=Style(fill="none", stroke=INK, stroke_width=1.4), z=1)
    d.polygon(_arc(x, y - 1.5 * s, 0.9 * s, 0.8 * s, math.pi, 2 * math.pi, 12), style=WHITE, z=2)
    valve(d, x, y, s)


def pump(d, cx, cy, r=17.0, direction="right"):
    circle(d, cx, cy, r)
    tri = [(-0.45 * r, -0.62 * r), (0.7 * r, 0.0), (-0.45 * r, 0.62 * r)]
    k = {"right": 0, "down": 1, "left": 2, "up": 3}[direction]
    c, s_ = round(math.cos(k * math.pi / 2)), round(math.sin(k * math.pi / 2))
    d.polygon([(cx + x * c - y * s_, cy + x * s_ + y * c) for x, y in tri],
              style=Style(fill=INK, stroke=INK, stroke_width=1.0), z=3)


def exchanger(d, cx, cy, r=22.0, vertical=False):
    """Shell-and-tube exchanger: circle with the tube bundle as a zigzag.

    The tube-side ports are the ends of the zigzag (left/right, or top/bottom
    when ``vertical``); the shell-side ports are on the other axis.
    """
    circle(d, cx, cy, r, style=EQUIP)
    pts = [(-r, 0.0)]
    for k, f in enumerate((-0.62, -0.38, -0.14, 0.1, 0.34, 0.58)):
        pts.append((f * r, (-0.5 if k % 2 == 0 else 0.5) * r))
    pts.append((r, 0.0))
    if vertical:
        pts = [(y, x) for x, y in pts]
    d.polyline([(cx + x, cy + y) for x, y in pts], style=Style(fill="none", stroke=INK, stroke_width=1.4), z=3)


def hvessel(d, cx, cy, length, dia, style=EQUIP):
    """Horizontal drum with elliptical heads."""
    cap = dia * 0.4
    x0, x1 = cx - length / 2 + cap, cx + length / 2 - cap
    pts = _arc(x1, cy, cap, dia / 2, -math.pi / 2, math.pi / 2) + _arc(x0, cy, cap, dia / 2, math.pi / 2, 3 * math.pi / 2)
    d.polygon(pts, style=style, z=1)


def bubble(d, x, y, code, number, r=16.0, panel=False):
    """ISA 5.1 instrument bubble; a bar through it means a control-room display."""
    circle(d, x, y, r, style=Style(fill="#FFFFFF", stroke=BLUE, stroke_width=1.3))
    if panel:
        d.polyline([(x - r, y), (x + r, y)], style=Style(fill="none", stroke=BLUE, stroke_width=1.0), z=3)
    d.text(code, size=10, color="#1F3F6E", z=6).at(x, y - 1.5, anchor="bottom_center")
    d.text(number, size=10, color="#1F3F6E", z=6).at(x, y + 1.5, anchor="top_center")


def stream(d, pts, head=True, **kw):
    opts = dict(PIPE)
    opts.update(kw)
    via = list(pts[1:-1])
    if via:
        return d.connect(pts[0], pts[-1], via=via, arrow_head=head, **opts)
    return d.connect(pts[0], pts[-1], routing="direct", arrow_head=head, **opts)


def snum(d, x, y, n):
    """Stream-number marker: a small diamond."""
    d.polygon([(x, y - 11), (x + 11, y), (x, y + 11), (x - 11, y)], style=WHITE, z=3)
    d.text(str(n), size=10, z=6).at(x, y, anchor="center")


def tag(d, x, y, name, desc="", anchor="top_center", size=12):
    d.text(f"**{name}**" + (f"\n{desc}" if desc else ""), size=size, line_height=1.3).at(x, y, anchor=anchor)


def note(d, x, y, text, size=11, anchor="left_center", **kw):
    d.text(text, size=size, **kw).at(x, y, anchor=anchor)


KT = 2.0  # k tau for the conversion comparison
N_SERIES = 3
BLUE, GREEN, RED, GREY = "#1F4E8C", "#2E6B3F", "#A33A3A", "#777777"


def e_cstr(th: float) -> float:
    return math.exp(-th)


def e_series(th: float, n: int = N_SERIES) -> float:
    return n * (n * th) ** (n - 1) * math.exp(-n * th) / math.factorial(n - 1)


def f_cstr(th: float) -> float:
    return 1.0 - math.exp(-th)


def f_series(th: float, n: int = N_SERIES) -> float:
    return 1.0 - math.exp(-n * th) * sum((n * th) ** i / math.factorial(i) for i in range(n))


def conversion(e, kt: float, upper: float = 40.0, steps: int = 40000) -> float:
    h = upper / steps
    total = sum(0.5 * h * (e(i * h) * math.exp(-kt * i * h) + e((i + 1) * h) * math.exp(-kt * (i + 1) * h))
                for i in range(steps))
    return 1.0 - total


def diagram() -> Diagram:
    x_cstr, x_ser, x_pfr = conversion(e_cstr, KT), conversion(e_series, KT), 1.0 - math.exp(-KT)
    assert abs(x_cstr - KT / (1 + KT)) < 1e-4
    assert abs(x_ser - (1 - (1 + KT / N_SERIES) ** -N_SERIES)) < 1e-4
    thin = Style(fill="none", stroke=INK, stroke_width=1.4)
    with Diagram("Residence Time Distribution: CSTR vs PFR", theme="paper") as d:
        # Reactor symbols: one stirred tank, three in series, a plug-flow tube.
        vessel(d, 150, 50, 130, 60)
        d.polyline([(150, 36), (150, 110)], style=thin, z=2)
        d.polyline([(136, 110), (164, 110)], style=Style(fill="none", stroke=INK, stroke_width=2.4), z=2)
        stream(d, [(60, 70), (121, 70)], width=1.4)
        stream(d, [(150, 130), (150, 150), (230, 150)], width=1.4)
        note(d, 150, 168, "**CSTR**, N = 1", anchor="top_center", size=12, color=BLUE)
        for k in range(N_SERIES):
            x = 420 + 70 * k
            vessel(d, x, 70, 130, 44)
            d.polyline([(x, 58), (x, 112)], style=thin, z=2)
            d.polyline([(x - 9, 112), (x + 9, 112)], style=Style(fill="none", stroke=INK, stroke_width=2.2), z=2)
            if k < N_SERIES - 1:
                stream(d, [(x + 22, 120), (x + 48, 120)], width=1.2)
        stream(d, [(360, 120), (398, 120)], width=1.2)
        stream(d, [(562, 120), (600, 120)], width=1.2)
        note(d, 490, 168, "**3 CSTRs in series**", anchor="top_center", size=12, color=GREEN)
        d.polygon([(740, 90), (900, 90), (900, 130), (740, 130)], style=EQUIP, z=1)
        for x in (775, 810, 845, 880):
            d.polyline([(x, 96), (x, 124)], style=Style(fill="none", stroke="#9AA5B1", stroke_width=0.8), z=2)
        stream(d, [(690, 110), (738, 110)], width=1.4)
        stream(d, [(902, 110), (950, 110)], width=1.4)
        note(d, 820, 168, "**PFR**, plug flow", anchor="top_center", size=12, color=RED)

        # E(theta).
        p = Plot(d, x=(0, 3), y=(0, 1.2), origin=(90.0, 560.0), size=(400.0, 300.0))
        p.grid(xstep=0.5, ystep=0.2)
        p.axes(xlabel="$\\theta = t/\\tau$", ylabel="$E(\\theta)$", xstep=0.5, ystep=0.2, through_zero=False)
        p.function(e_cstr, 0, 3, stroke=BLUE, width=2.6)
        p.function(e_series, 0, 3, stroke=GREEN, width=2.6)
        p.line((1, 0), (1, 1.12), stroke=RED, width=2.6)
        p.dot(1, 1.12, radius=4, fill=RED, stroke=RED)
        p.label(1, 1.12, "$\\delta(\\theta - 1)$", dx=8, dy=0, anchor="left_center", size=13, color=RED)
        p.label(0.08, 1.0, "CSTR $e^{-\\theta}$", dx=6, dy=-14, anchor="bottom_left", size=12, color=BLUE)
        p.label(0.3, e_series(0.3), "N = 3", dx=-8, dy=-8, anchor="bottom_right", size=12, color=GREEN)
        # F(theta).
        q = Plot(d, x=(0, 3), y=(0, 1.2), origin=(580.0, 560.0), size=(400.0, 300.0))
        q.grid(xstep=0.5, ystep=0.2)
        q.axes(xlabel="$\\theta = t/\\tau$", ylabel="$F(\\theta)$", xstep=0.5, ystep=0.2, through_zero=False)
        q.function(f_cstr, 0, 3, stroke=BLUE, width=2.6)
        q.function(f_series, 0, 3, stroke=GREEN, width=2.6)
        q.polyline([(0, 0), (1, 0), (1, 1), (3, 1)], stroke=RED, width=2.6)
        q.label(1, 0.5, "step at $\\theta = 1$", dx=8, anchor="left_center", size=12, color=RED)
        q.label(2.0, f_cstr(2.0), "CSTR", dx=2, dy=26, anchor="top_left", size=12, color=BLUE)
        q.label(0.62, f_series(0.62), "N = 3", dx=-8, dy=6, anchor="right_center", size=12, color=GREEN)
        # Comparison table.
        rows = [("", "variance $\\sigma_\\theta^2$", f"conversion, $k\\tau$ = {KT:g}"),
                ("CSTR", "1", f"{x_cstr:.3f}"),
                ("3 CSTRs", f"{1 / N_SERIES:.2f}", f"{x_ser:.3f}"),
                ("PFR", "0", f"{x_pfr:.3f}")]
        colors = [INK, BLUE, GREEN, RED]
        for r, (a, b, c) in enumerate(rows):
            y = 618 + 22 * r
            d.text(f"**{a}**" if a else "", size=12, color=colors[r]).at(90, y, anchor="left_center")
            d.text(f"**{b}**" if r == 0 else b, size=12).at(190, y, anchor="left_center")
            d.text(f"**{c}**" if r == 0 else c, size=12).at(380, y, anchor="left_center")
        d.text(
            "Both distributions have mean residence time $\\bar t = \\tau = V/q$. For a first-order reaction "
            "$X = 1 - \\int_0^\\infty E(\\theta)\\,e^{-k\\tau\\theta}\\,d\\theta$: back-mixing "
            "lowers conversion and the plug-flow reactor is the upper bound.",
            size=12, font="serif", italic=True).at(90, 720, anchor="top_left")
        d.caption("**Figure 10:** Exit-age distributions E and F of ideal flow patterns and their effect on conversion",
                  small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "10_residence_time_distribution")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
