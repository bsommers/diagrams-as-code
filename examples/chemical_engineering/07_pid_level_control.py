"""A level-control loop on a surge tank: instrumented schematic and block diagram.

The tank is an integrator, A dh/dt = q_in - q_out, so a PI controller on the
outlet valve gives a second-order closed loop with natural frequency
w_n = sqrt(Kp Kc / Ti) and damping zeta = (1/2) sqrt(Kp Kc Ti), where Kp is the
open-loop gain from valve opening (%) to level (% of range) per second. Kp is
computed from the tank diameter, level range and valve capacity below, and the
tuning (Kc, Ti) is chosen to give zeta of about 0.7. Instrument tags follow
ISA 5.1: a bubble with no bar is field-mounted, a bar means a control-room
display.
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


DIAM, RANGE_M, Q_MAX = 2.0, 3.0, 20.0  # tank diameter m, level range m, valve capacity m3/h
KC, TI = 10.0, 330.0  # controller gain (%/%) and integral time (s)
BLOCK = Style(fill="#E6EDF5", font_size=13)


def tuning():
    area = math.pi * DIAM ** 2 / 4.0
    kp = (Q_MAX / 3600.0 / 100.0) / area / RANGE_M * 100.0  # (% level / s) per % valve
    wn = math.sqrt(kp * KC / TI)
    zeta = 0.5 * math.sqrt(kp * KC * TI)
    return area, kp, wn, zeta


def diagram() -> Diagram:
    area, kp, wn, zeta = tuning()
    cx, top, bot, w = 200.0, 130.0, 330.0, 120.0
    cap = w * 0.3
    level_y = 232.0  # 50 % of the straight section
    with Diagram("PID Level-Control Loop on a Surge Tank", theme="paper") as d:
        # Tank with liquid and a level line.
        r = w / 2
        d.polygon([(cx + r, level_y), (cx + r, bot - cap)] + _arc(cx, bot - cap, r, cap, 0, math.pi)[1:] + [(cx - r, level_y)],
                  style=Style(fill="#BBD6EE", stroke="none", stroke_width=0), z=0)
        vessel(d, cx, top, bot, w, style=Style(fill="none", stroke=INK, stroke_width=1.6))
        d.polyline([(cx - r, level_y), (cx + r, level_y)],
                   style=Style(fill="none", stroke="#4A7BAA", stroke_width=1.0, dash="4,3"), z=2)
        tag(d, 100, 345, "T-101", "surge tank", anchor="top_right")
        stream(d, [(30, 175), (cx - r + 4, 175)])
        note(d, 30, 163, "Inflow $q_{in}$\n(disturbance)", anchor="bottom_left", size=12)
        stream(d, [(cx, bot), (cx, 410), (680, 410)])
        note(d, 686, 410, "to downstream unit", anchor="left_center")
        control_valve(d, 520, 410)
        tag(d, 548, 386, "LV-101", "fail open", anchor="bottom_left")
        # Differential-pressure level transmitter.
        thin = Style(fill="none", stroke=INK, stroke_width=1.1)
        d.polyline([(cx + r, 180), (360, 180), (360, 216)], style=thin, z=1)
        d.polyline([(cx + r, 292), (360, 292), (360, 248)], style=thin, z=1)
        bubble(d, 360, 232, "LT", "101")
        bubble(d, 520, 232, "LIC", "101", panel=True)
        d.connect((376, 232), (504, 232), routing="direct", arrow_head=True, **SIGNAL)
        d.connect((520, 248), (520, 372), routing="direct", arrow_head=True, **SIGNAL)
        d.connect((520, 150), (520, 216), routing="direct", arrow_head=True, **SIGNAL)
        note(d, 520, 140, "SP = 50 % (1.5 m)", anchor="bottom_center")
        note(d, 534, 300, f"PI: Kc = {KC:g} %/%, Ti = {TI:g} s", anchor="left_center")
        note(d, 590, 232, "PV = level, 0 to 3 m", anchor="left_center")
        # Block diagram of the same loop.
        yb = 540.0
        circ = lambda x: (circle(d, x, yb, 15), d.polyline([(x - 8, yb - 8), (x + 8, yb + 8)], style=thin, z=3),
                          d.polyline([(x - 8, yb + 8), (x + 8, yb - 8)], style=thin, z=3))
        circ(130)
        circ(570)
        pi = d.shape("**LIC-101**\nPI controller\n$K_c\\,(1 + 1/(T_i s))$", 170, 76, style=BLOCK).at(270, yb, anchor="center")
        lv = d.shape("**LV-101**\nvalve, % to m\u00b3/h", 130, 76, style=BLOCK).at(440, yb, anchor="center")
        tank = d.shape("**T-101**\nintegrator $1/(A s)$", 140, 76, style=BLOCK).at(700, yb, anchor="center")
        stream(d, [(40, yb), (115, yb)], width=1.4)
        note(d, 40, yb - 12, "SP", anchor="bottom_left")
        stream(d, [(145, yb), (185, yb)], width=1.4)
        note(d, 165, yb - 12, "e", anchor="bottom_center")
        stream(d, [(355, yb), (375, yb)], width=1.4)
        stream(d, [(505, yb), (555, yb)], width=1.4)
        note(d, 530, yb - 12, "$q_{out}$", anchor="bottom_center")
        stream(d, [(585, yb), (630, yb)], width=1.4)
        stream(d, [(770, yb), (880, yb)], width=1.4)
        note(d, 880, yb - 12, "$h$", anchor="bottom_right")
        d.point(820, yb, dot=True, radius=3.5)
        stream(d, [(570, 470), (570, yb - 15)], width=1.4)
        note(d, 582, 485, "$q_{in}$", anchor="left_center")
        note(d, 556, 520, "$-$", anchor="bottom_right", size=12)
        note(d, 580, 514, "$+$", anchor="bottom_left", size=12)
        d.connect((820, yb), (130, yb + 15), via=[(820, 620), (130, 620)], arrow_head=True, width=1.4, color=INK)
        note(d, 475, 632, "LT-101, measured level", anchor="top_center", size=12)
        note(d, 118, 520, "$+$", anchor="bottom_right", size=12)
        note(d, 118, 566, "$-$", anchor="top_right", size=12)
        d.text(
            f"Tank area $A = \\pi D^2/4 = {area:.2f}\\,\\mathrm{{m}}^2$; valve gain {Q_MAX:g} m³/h per 100 %; "
            f"$K_p = {kp * 1e4:.2f}\\times 10^{{-4}}$ (%/s)/%.   Closed loop: $\\omega_n = \\sqrt{{K_p K_c/T_i}} = {wn:.4f}$ rad/s, "
            f"$\\zeta = \\tfrac{{1}}{{2}}\\sqrt{{K_p K_c T_i}} = {zeta:.2f}$",
            size=12,
        ).at(40, 680, anchor="top_left")
        d.caption("**Figure 7:** Surge-tank level loop as a P&ID fragment and as a control block diagram", small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "07_pid_level_control")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
