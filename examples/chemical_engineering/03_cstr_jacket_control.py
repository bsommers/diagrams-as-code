"""A jacketed CSTR with a temperature control loop on the coolant valve.

Exothermic first-order reaction A -> B in a 2 m3 stirred tank. At steady state
the conversion is X = k tau / (1 + k tau), the heat released is
(-dHr) F_A0 X, and the jacket must remove that heat less what the feed needs to
warm up to the reactor temperature:
Q_jacket = (-dHr) F_A0 X - q rho cp (T - T_feed). The coolant flow follows from
Q_jacket and the cooling-water rise. All values below are computed from the
basis, so the printed duties are consistent.
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


VOL, Q_VOL, CA0 = 2.0, 0.10, 2.0  # m3, m3/min feed, kmol/m3
K, DHR = 0.10, 60.0  # 1/min at reactor temperature, kJ/mol released
T_R, T_F = 80.0, 70.0  # reactor and feed temperature, C
RHO_CP = 4.0e3  # kJ/(m3 K) for the aqueous mixture
T_IN, T_OUT, CP_W = 25.0, 35.0, 4.18  # cooling water, C and kJ/(kg K)


def basis():
    tau = VOL / Q_VOL
    x = K * tau / (1 + K * tau)
    q_rxn = DHR * CA0 * 1000.0 * Q_VOL * x / 60.0  # kJ/s = kW
    q_sens = RHO_CP * Q_VOL / 60.0 * (T_R - T_F)
    q_jac = q_rxn - q_sens
    return tau, x, q_rxn, q_sens, q_jac, q_jac / (CP_W * (T_OUT - T_IN))


def diagram() -> Diagram:
    tau, x, q_rxn, q_sens, q_jac, m_cw = basis()
    cx, top, bot, w = 400.0, 150.0, 400.0, 130.0
    cap = w * 0.3
    with Diagram("CSTR with Cooling Jacket and Temperature Control Loop", theme="paper") as d:
        # Jacket first so the vessel draws over it.
        rj = w / 2 + 14
        d.polygon([(cx + rj, 235), (cx + rj, bot - cap)] + _arc(cx, bot - cap, rj, cap + 10, 0, math.pi)[1:]
                  + [(cx - rj, 235)],
                  style=Style(fill="#DCEBF7", stroke=INK, stroke_width=1.3), z=0)
        vessel(d, cx, top, bot, w)
        # Agitator: motor, shaft and flat-blade impeller.
        d.polyline([(cx, 108), (cx, 330)], style=Style(fill="none", stroke=INK, stroke_width=1.8), z=2)
        d.polyline([(cx - 32, 330), (cx + 32, 330)], style=Style(fill="none", stroke=INK, stroke_width=3.0), z=2)
        circle(d, cx, 96, 13)
        d.text("M", size=11, z=6).at(cx, 96, anchor="center")
        tag(d, 300, 392, "R-201", "Jacketed CSTR", anchor="top_right")
        note(d, 307, 300, "cooling\njacket", anchor="right_center")
        # Feed in, product out.
        stream(d, [(130, 195), (cx - w / 2 + 2, 195)])
        note(d, 130, 183, f"Feed A, {T_F:g} °C", anchor="bottom_left")
        note(d, 130, 210, f"{Q_VOL * 60:g} m³/h, {CA0:g} kmol/m³", anchor="top_left")
        stream(d, [(cx, bot), (cx, 470), (560, 470)])
        note(d, 566, 470, f"Product A + B, {T_R:g} °C", anchor="left_center")
        note(d, 566, 488, f"conversion X = {x:.2f}", anchor="left_center")
        # Coolant: in through TV-201 at the jacket bottom, out at the top.
        stream(d, [(720, 345), (cx + rj, 345)])
        control_valve(d, 640, 345)
        note(d, 720, 360, f"Cooling water in, {T_IN:g} °C", anchor="top_right")
        tag(d, 654, 322, "TV-201", "fail open", anchor="bottom_left")
        stream(d, [(cx - rj, 250), (200, 250)])
        note(d, 200, 262, f"CW out, {T_OUT:g} °C", anchor="top_left")
        # Control loop: thermowell -> TT-201 -> TIC-201 -> TV-201.
        d.polyline([(430, 270), (430, 110), (454, 110)], style=Style(fill="none", stroke=INK, stroke_width=1.2), z=2)
        bubble(d, 470, 110, "TT", "201")
        bubble(d, 640, 170, "TIC", "201", panel=True)
        d.connect((486, 110), (640, 154), via=[(640, 110)], arrow_head=True, **SIGNAL)
        d.connect((640, 186), (640, 312), routing="direct", arrow_head=True, **SIGNAL)
        note(d, 662, 170, f"SP = {T_R:g} °C", anchor="left_center")
        # Basis and steady-state energy balance.
        note(d, 130, 530,
             "**Steady-state basis**\n"
             f"V = {VOL:g} m³, q = {Q_VOL:g} m³/min, $\\tau = V/q = {tau:g}$ min, "
             f"k = {K:g} min$^{{-1}}$, $X = k\\tau/(1+k\\tau) = {x:.3f}$\n"
             f"Reaction heat {q_rxn:.0f} kW, feed warm-up {q_sens:.0f} kW, "
             f"jacket duty $Q_j$ = {q_jac:.0f} kW, cooling water {m_cw:.2f} kg/s",
             anchor="top_left", line_height=1.5, size=12)
        d.text("$Q_j = (-\\Delta H_r)\\,F_{A0}\\,X - q\\,\\rho c_p\\,(T - T_{\\mathrm{feed}})$", size=14).at(
            130, 600, anchor="top_left")
        d.caption("**Figure 3:** Jacketed CSTR with a feedback temperature loop that throttles the cooling-water valve",
                  small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "03_cstr_jacket_control")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
