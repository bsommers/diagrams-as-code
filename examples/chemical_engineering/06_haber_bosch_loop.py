"""The Haber-Bosch ammonia synthesis loop with recycle and purge.

N2 + 3 H2 -> 2 NH3 at about 450 C and 200 bar over an iron catalyst. Only part of
the nitrogen reacts per pass, so the gas leaving the condensing separator is
recycled; the argon that enters with the make-up gas cannot react or condense
and would build up, so a purge bleeds it off. The basis is 25 kmol/h N2 and
75 kmol/h H2 of make-up with 0.6 kmol/h argon, 4 mol % argon in the loop gas and
18 % per-pass N2 conversion. The purge, recycle, reactor feed and product rates
are solved from the atom balances, not typed in; NH3 left in the recycle gas is
neglected.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

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


N2_MAKE, H2_MAKE, AR_MAKE = 25.0, 75.0, 0.6  # kmol/h
Y_AR, CONV = 0.04, 0.18


def loop_balance():
    purge = AR_MAKE / Y_AR  # argon leaves only in the purge
    n2_purge = purge * (1 - Y_AR) / 4.0  # loop gas is N2:H2 = 1:3 apart from argon
    n2_react = N2_MAKE - n2_purge
    nh3 = 2.0 * n2_react
    n2_in = n2_react / CONV
    vapour = (n2_in - n2_react) / ((1 - Y_AR) / 4.0)  # separator vapour
    recycle = vapour - purge
    feed = N2_MAKE + H2_MAKE + AR_MAKE + recycle
    return purge, nh3, recycle, feed


def compressor(d, x, y, direction="right"):
    s = 1 if direction == "right" else -1
    d.polygon([(x - s * 15, y - 17), (x + s * 15, y - 8), (x + s * 15, y + 8), (x - s * 15, y + 17)],
              style=WHITE, z=2)


def diagram() -> Diagram:
    purge, nh3, recycle, feed = loop_balance()
    yf, ye, yr = 250.0, 160.0, 50.0  # forward leg, effluent leg, recycle leg
    rx, sx = 560.0, 900.0
    with Diagram("Haber-Bosch Ammonia Loop with Recycle and Purge", theme="paper") as d:
        # Make-up gas, compressor C-401, mixing point, preheater E-401.
        stream(d, [(30, yf), (92, yf)])
        note(d, 30, yf - 30, f"**Make-up gas**\n{N2_MAKE:g} N$_2$ + {H2_MAKE:g} H$_2$ + {AR_MAKE:g} Ar kmol/h", anchor="bottom_left", size=11)

        compressor(d, 110, yf)
        tag(d, 110, yf + 30, "C-401", "make-up\ncompressor")
        stream(d, [(128, yf), (240, yf)], head=False)
        d.point(240, yf, dot=True, radius=3.5)
        stream(d, [(240, yf), (318, yf)])
        exchanger(d, 340, yf)
        tag(d, 352, yf - 26, "E-401", "feed / effluent\nexchanger", anchor="bottom_left")
        stream(d, [(362, yf), (rx, yf), (rx, 283)])
        note(d, 470, yf - 14, f"{feed:.0f} kmol/h to reactor", anchor="bottom_left")
        # Converter R-401 with two catalyst beds.
        vessel(d, rx, 270, 470, 100)
        for y in (350, 410):
            d.polygon([(rx - 44, y), (rx + 44, y), (rx + 44, y + 14), (rx - 44, y + 14)],
                      style=Style(fill="#D9C7A5", stroke=INK, stroke_width=0.9), z=2)
        note(d, rx + 62, 360, "Fe catalyst beds", anchor="left_center")
        note(d, rx + 62, 380, "450 °C, 200 bar", anchor="left_center")
        tag(d, rx + 62, 296, "R-401", "ammonia converter", anchor="top_left")
        # Effluent back through E-401 (shell side), then cooler E-402.
        stream(d, [(rx, 470), (rx, 520), (340, 520), (340, yf + 22)], head=False)
        stream(d, [(340, yf - 22), (340, ye), (738, ye)])
        note(d, 350, 470, "hot effluent", anchor="left_center")
        exchanger(d, 760, ye)
        tag(d, 760, ye + 70, "E-402", "cooler / condenser")
        stream(d, [(760, 222), (760, ye + 22)])
        stream(d, [(760, ye - 22), (760, 102)])
        note(d, 770, 220, "CW in", anchor="left_center")
        note(d, 770, 108, "CW out", anchor="left_center")
        stream(d, [(782, ye), (830, ye), (830, 330), (sx - 43, 330)])
        # Separator V-401: NH3 liquid out, gas to recycle and purge.
        vessel(d, sx, 280, 440, 90)
        tag(d, sx - 56, 400, "V-401", "NH$_3$ separator\n35 °C, 200 bar", anchor="top_right")

        stream(d, [(sx, 440), (sx, 490), (1010, 490)])
        note(d, 1016, 490, f"Liquid NH$_3$\n{nh3:.1f} kmol/h", anchor="left_center", size=12)
        stream(d, [(sx, 280), (sx, yr), (583, yr)], head=False)
        d.point(sx, 130, dot=True, radius=3.5)
        stream(d, [(sx, 130), (1010, 130)])
        note(d, 1016, 130, f"Purge\n{purge:.0f} kmol/h", anchor="left_center", size=12)
        compressor(d, 560, yr, direction="left")
        tag(d, 560, yr + 30, "C-402", "recycle\ncompressor")
        stream(d, [(543, yr), (240, yr), (240, yf - 4)])
        note(d, 400, yr - 14, f"Recycle {recycle:.0f} kmol/h", anchor="bottom_center")
        # Basis.
        note(d, 30, 350,
             "**Loop basis**\n"
             f"Argon {Y_AR:.0%} in loop gas sets purge = {AR_MAKE:g}/{Y_AR:g} = {purge:.0f} kmol/h\n"
             f"N$_2$ converted per pass {CONV:.0%}; N$_2$ reacted = {N2_MAKE - purge * (1 - Y_AR) / 4:.1f} kmol/h\n"
             f"NH$_3$ = 2 x N$_2$ reacted = {nh3:.1f} kmol/h\n"
             f"Reactor feed {feed:.0f} = make-up {N2_MAKE + H2_MAKE + AR_MAKE:g} + recycle {recycle:.0f}",
             anchor="top_left", line_height=1.5, size=12)
        d.caption("**Figure 6:** Ammonia synthesis loop: make-up compression, converter, condensation, recycle and argon purge",
                  small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "06_haber_bosch_loop")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
