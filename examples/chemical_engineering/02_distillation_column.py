"""A distillation column with overhead condenser, reflux drum and reboiler.

Benzene-toluene separation at 1.013 bar. Basis: feed F = 100 kmol/h of 50 mol %
benzene as saturated liquid, distillate xD = 0.95 and bottoms xB = 0.05, so the
overall balance gives D = B = 50 kmol/h. At a reflux ratio R = 2 the liquid
reflux is L = R D = 100 kmol/h and the overhead vapour V = L + D = 150 kmol/h
(the feed is saturated liquid, so the stripping-section vapour is also 150).
Condenser and reboiler duties are V times the molar latent heat of benzene
(30.7 kJ/mol) and of toluene (33.2 kJ/mol).
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


F, XF, XD, XB, R = 100.0, 0.50, 0.95, 0.05, 2.0
D = F * (XF - XB) / (XD - XB)
B = F - D
L = R * D
V = L + D
QC = V / 3600.0 * 30.7e3 / 1000.0  # kmol/h -> mol/s x kJ/mol -> MW
QR = V / 3600.0 * 33.2e3 / 1000.0


def diagram() -> Diagram:
    cx, top, bot, w = 330.0, 140.0, 540.0, 90.0
    lw, rw = cx - w / 2, cx + w / 2
    with Diagram("Distillation Column with Condenser, Reboiler and Reflux", theme="paper") as d:
        vessel(d, cx, top, bot, w)
        thin = Style(fill="none", stroke=INK, stroke_width=1.1)
        for k in range(12):
            y = 190 + 26 * k
            if k % 2 == 0:
                d.polyline([(lw + 2, y), (rw - 16, y)], style=thin, z=2)
            else:
                d.polyline([(lw + 16, y), (rw - 2, y)], style=thin, z=2)
        tag(d, lw - 12, 200, "C-101", "Distillation column\n20 trays (schematic)", anchor="top_right")
        # Feed.
        stream(d, [(100, 330), (lw + 2, 330)])
        note(d, 100, 318, "Feed F, saturated liquid", anchor="bottom_left")
        note(d, 100, 346, f"{F:g} kmol/h, {XF:.0%} benzene", anchor="top_left")
        # Overhead: vapour to condenser E-101, condensate to reflux drum V-101.
        stream(d, [(cx, top), (cx, 100), (498, 100)], head=False)
        exchanger(d, 520, 100)
        stream(d, [(520, 52), (520, 78)])
        stream(d, [(520, 122), (520, 160)])
        note(d, 520, 46, "cooling water in, 30 °C", anchor="bottom_center")
        note(d, 532, 160, "out, 40 °C", anchor="top_left")
        tag(d, 498, 88, "E-101", "Overhead condenser", anchor="bottom_right")
        note(d, 400, 112, "81 °C vapour", anchor="top_left")
        stream(d, [(542, 100), (600, 100), (600, 187)])
        hvessel(d, 600, 215, 130, 56)
        tag(d, 640, 252, "V-101", "Reflux drum")
        # Reflux pump P-101 and the reflux / distillate split.
        stream(d, [(555, 243), (555, 300), (522, 300)])
        pump(d, 505, 300, direction="left")
        tag(d, 505, 324, "P-101", "Reflux pump")
        stream(d, [(488, 300), (430, 300)], head=False)
        stream(d, [(430, 300), (430, 172), (rw + 2, 172)])
        stream(d, [(430, 300), (430, 400), (780, 400)])
        d.point(430, 300, dot=True, radius=3.5)
        note(d, 442, 240, f"Reflux L =\n{L:g} kmol/h", anchor="left_center")
        note(d, 786, 400, "Distillate D", anchor="left_center", size=12)
        note(d, 786, 418, f"{D:g} kmol/h, {XD:.0%} benzene", anchor="left_center")
        # Bottoms: reboiler E-102 (thermosyphon) and product draw.
        stream(d, [(cx, bot), (cx, 600)], head=False)
        stream(d, [(cx, 600), (620, 600), (620, 567)])
        exchanger(d, 620, 545, vertical=True)
        stream(d, [(620, 523), (620, 500), (rw - 3, 500)])
        stream(d, [(720, 545), (642, 545)])
        note(d, 726, 545, "LP steam", anchor="left_center")
        stream(d, [(598, 545), (560, 545)])
        note(d, 552, 545, "condensate", anchor="right_center")
        tag(d, 645, 478, "E-102", "Reboiler", anchor="bottom_left")
        stream(d, [(cx, 600), (cx, 650), (200, 650)])
        d.point(cx, 600, dot=True, radius=3.5)
        note(d, 194, 650, "Bottoms B", anchor="right_center", size=12)
        note(d, 194, 668, f"{B:g} kmol/h, {XB:.0%} benzene", anchor="right_center")
        note(d, 342, 625, "109 °C", anchor="left_center")
        # Design basis.
        note(d, 800, 120,
             "**Design basis, benzene / toluene**\n"
             f"F = {F:g} kmol/h, z = {XF:.2f}, saturated liquid\n"
             f"D = {D:g} kmol/h, xD = {XD:.2f}\n"
             f"B = {B:g} kmol/h, xB = {XB:.2f}\n"
             f"R = L/D = {R:g}, L = {L:g}, V = {V:g} kmol/h\n"
             f"Qc = {QC:.2f} MW, Qr = {QR:.2f} MW\n"
             "P = 1.013 bar (top), feed on tray 9 (figure 9)",
             anchor="top_left", line_height=1.5)
        d.caption("**Figure 2:** Distillation column with overhead condenser, reflux drum, reflux pump and thermosyphon reboiler",
                  small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "02_distillation_column")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
