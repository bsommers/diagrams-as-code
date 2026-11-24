"""A shell-and-tube heat exchanger network with duties, temperatures and areas.

A cold feed (heat-capacity flow 20 kW/K) is heated from 30 to 150 C against a hot
reactor effluent (25 kW/K, 180 to 40 C). Recovery exchanger E-301 passes the hot
effluent against the cold feed; steam heater E-302 trims the feed to 150 C; and
cooler E-303 brings the effluent down to 40 C against cooling water. Duties
follow from Q = (m cp) dT, log-mean temperature differences from the terminal
temperatures of each unit (counter-current), and areas from A = Q / (U LMTD).
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


HOT, COLD = "#A33A3A", "#2F5F9E"
CP_H, CP_C = 25.0, 20.0  # heat-capacity flow rates, kW/K
TH_IN, TH_OUT, TC_IN, TC_OUT = 180.0, 40.0, 30.0, 150.0
T_STEAM, TW_IN, TW_OUT = 180.0, 25.0, 35.0


def lmtd(a: float, b: float) -> float:
    return a if abs(a - b) < 1e-9 else (a - b) / math.log(a / b)


def network():
    """Duty, LMTD, U and area for E-301 (recovery), E-302 (heater), E-303 (cooler)."""
    q301 = CP_C * (110.0 - TC_IN)  # cold feed 30 -> 110 C
    th_mid = TH_IN - q301 / CP_H  # hot effluent leaves E-301
    q302 = CP_C * (TC_OUT - 110.0)
    q303 = CP_H * (th_mid - TH_OUT)
    l301 = lmtd(TH_IN - 110.0, th_mid - TC_IN)
    l302 = lmtd(T_STEAM - 110.0, T_STEAM - TC_OUT)
    l303 = lmtd(th_mid - TW_OUT, TH_OUT - TW_IN)
    rows = [("E-301", q301, l301, 0.5), ("E-302", q302, l302, 0.8), ("E-303", q303, l303, 0.6)]
    return th_mid, [(n, q, lm, u, q / (u * lm)) for n, q, lm, u in rows]


def diagram() -> Diagram:
    th_mid, units = network()
    (_, q301, _, _, a301), (_, q302, _, _, a302), (_, q303, _, _, a303) = units
    assert abs(CP_H * (TH_IN - TH_OUT) - (q301 + q303)) < 1e-6
    assert abs(CP_C * (TC_OUT - TC_IN) - (q301 + q302)) < 1e-6
    yc, yh = 420.0, 220.0
    x1, x2 = 330.0, 580.0
    with Diagram("Shell-and-Tube Exchanger Network: Duties and Temperatures", theme="paper") as d:
        # Cold feed line through E-301 and E-302 (tube side).
        stream(d, [(60, yc), (x1 - 22, yc)], color=COLD)
        stream(d, [(x1 + 22, yc), (x2 - 22, yc)], color=COLD)
        stream(d, [(x2 + 22, yc), (800, yc)], color=COLD)
        exchanger(d, x1, yc)
        exchanger(d, x2, yc)
        note(d, 60, yc - 14, f"Cold feed, {CP_C:g} kW/K", anchor="bottom_left", size=12)
        note(d, 60, yc + 14, f"{TC_IN:g} °C", anchor="top_left")
        note(d, (x1 + x2) / 2, yc - 12, "110 °C", anchor="bottom_center")
        note(d, 806, yc, f"{TC_OUT:g} °C to reactor", anchor="left_center", size=12)
        # Hot effluent: shell side of E-301, then tube side of cooler E-303.
        stream(d, [(920, yh), (x1, yh), (x1, yc - 22)], color=HOT)
        note(d, 920, yh - 14, f"Hot reactor effluent, {CP_H:g} kW/K", anchor="bottom_right", size=12)
        note(d, 760, yh + 14, f"{TH_IN:g} °C", anchor="top_center")
        stream(d, [(x1, yc + 22), (x1, 498)], color=HOT)
        note(d, x1 + 12, 462, f"{th_mid:.0f} °C", anchor="left_center")
        exchanger(d, x1, 520, vertical=True)
        stream(d, [(x1, 542), (x1, 620)], color=HOT)
        note(d, x1 + 12, 600, f"{TH_OUT:g} °C to storage", anchor="left_center", size=12)
        # Cooling water on the shell side of E-303.
        stream(d, [(170, 520), (x1 - 22, 520)], color=COLD)
        stream(d, [(x1 + 22, 520), (470, 520)], color=COLD)
        note(d, 170, 508, f"cooling water in, {TW_IN:g} °C", anchor="bottom_left")
        note(d, 470, 508, f"out, {TW_OUT:g} °C", anchor="bottom_right")
        # Steam and condensate on the shell side of E-302.
        stream(d, [(x2, 290), (x2, yc - 22)], color="#555555")
        stream(d, [(x2, yc + 22), (x2, 500)], color="#555555")
        note(d, x2 + 12, 276, f"steam, 10 bar, {T_STEAM:g} °C", anchor="left_center")
        note(d, x2 + 12, 490, "condensate", anchor="left_center")
        # Equipment tags with duty and area.
        tag(d, x1 - 16, 340, "E-301", f"recovery\nQ = {q301:.0f} kW\nA = {a301:.0f} m²", anchor="top_right")
        tag(d, x2 + 16, 318, "E-302", f"steam heater\nQ = {q302:.0f} kW\nA = {a302:.0f} m²", anchor="top_left")
        tag(d, x1 - 16, 540, "E-303", f"cooler\nQ = {q303:.0f} kW\nA = {a303:.0f} m²", anchor="top_right")
        # Exchanger data table.
        cols = [640, 712, 790, 868, 930]
        heads = ["Unit", "Q, kW", "LMTD, K", "U, kW/m²K", "A, m²"]
        ty = 540
        for x, h in zip(cols, heads):
            d.text(f"**{h}**", size=11).at(x, ty, anchor="left_center")
        for r, (n, q, lm, u, a) in enumerate(units):
            for x, v in zip(cols, [n, f"{q:.0f}", f"{lm:.1f}", f"{u:g}", f"{a:.0f}"]):
                d.text(v, size=11).at(x, ty + 22 * (r + 1), anchor="left_center")
        d.polyline([(cols[0], ty + 11), (cols[-1] + 50, ty + 11)], style=Style(fill="none", stroke=INK, stroke_width=0.8), z=1)
        note(d, 640, 640,
             f"Hot: {CP_H:g} x ({TH_IN:g} - {TH_OUT:g}) = {CP_H * (TH_IN - TH_OUT):.0f} kW = {q301:.0f} + {q303:.0f}\n"
             f"Cold: {CP_C:g} x ({TC_OUT:g} - {TC_IN:g}) = {CP_C * (TC_OUT - TC_IN):.0f} kW = {q301:.0f} + {q302:.0f}",
             anchor="top_left", line_height=1.5)
        d.caption("**Figure 4:** Heat recovery network with steam trim heater and cooling-water cooler",
                  small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "04_heat_exchanger_network")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
