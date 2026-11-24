"""A simple process flow diagram: feed, preheater, reactor and flash separator.

Feed from tank T-101 is pumped to 10 bar, heated from 25 to 150 C with low-pressure
steam in the shell-and-tube exchanger E-101, converted in the stirred reactor R-101
and let down through pressure-control valve PV-101 into the flash drum V-101, which
splits a vapour product from a liquid product. Symbols follow ISO 10628 / ISA 5.1
conventions (circle with zigzag for a tube bundle, bowtie for a valve); every
symbol is drawn from primitives.
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


Y = 380.0  # main process line


def diagram() -> Diagram:
    with Diagram("Simple Process Flow: Feed, Exchanger, Reactor, Separator", theme="paper") as d:
        # Feed tank T-101 and pump P-101.
        vessel(d, 110, 290, 410, 80)
        tag(d, 110, 420, "T-101", "Feed tank")
        stream(d, [(20, 330), (72, 330)])
        note(d, 22, 345, "Feed", anchor="top_left", size=12)
        stream(d, [(150, Y), (232, Y)], head=False)
        pump(d, 250, Y)
        tag(d, 250, 405, "P-101", "Feed pump")
        # Preheater E-101 with LP steam on the shell side.
        stream(d, [(267, Y), (358, Y)], head=False)
        exchanger(d, 380, Y)
        stream(d, [(402, Y), (490, Y)])
        stream(d, [(380, 270), (380, Y - 22)])
        stream(d, [(380, Y + 22), (380, 470)])
        note(d, 380, 262, "LP steam, 4 bar", anchor="bottom_center")
        note(d, 380, 478, "condensate", anchor="top_center")
        tag(d, 368, 300, "E-101", "Feed preheater", anchor="top_right")
        # Reactor R-101: jacket-free stirred tank with agitator.
        vessel(d, 530, 290, 450, 100)
        d.polyline([(530, 262), (530, 380)], style=Style(fill="none", stroke=INK, stroke_width=1.6), z=2)
        d.polyline([(512, 380), (548, 380)], style=Style(fill="none", stroke=INK, stroke_width=2.4), z=2)
        circle(d, 530, 250, 12)
        d.text("M", size=11).at(530, 250, anchor="center")
        tag(d, 530, 462, "R-101", "Stirred reactor")
        # Reactor outlet to pressure control valve PV-101 and flash drum V-101.
        d.polyline([(560, 297), (560, 200), (690, 200)], style=Style(fill="none", stroke=INK, stroke_width=1.8), z=0)
        d.polyline([(690, 200), (790, 200), (790, 300)], style=Style(fill="none", stroke=INK, stroke_width=1.8), z=0)
        control_valve(d, 690, 200)
        note(d, 706, 182, "PV-101", anchor="left_center")
        bubble(d, 620, 130, "PIC", "101", panel=True)
        d.connect((620, 200), (620, 146), routing="direct", arrow_head=False, **SIGNAL)
        d.connect((636, 130), (690, 174), via=[(690, 130)], arrow_head=True, **SIGNAL)
        # Flash drum V-101.
        vessel(d, 790, 300, 440, 90)
        tag(d, 738, 400, "V-101", "Flash separator", anchor="top_right")
        stream(d, [(790, 270), (790, 220)], head=False)
        stream(d, [(790, 440), (790, 480), (880, 480)])
        note(d, 886, 480, "Liquid product", size=12)
        stream(d, [(835, 340), (890, 340)])
        note(d, 896, 340, "Vapour product", size=12)
        # Stream numbers.
        snum(d, 50, 308, 1)
        snum(d, 190, Y - 17, 2)
        snum(d, 445, Y - 17, 3)
        snum(d, 775, 183, 4)
        snum(d, 862, 323, 5)
        snum(d, 840, 463, 6)
        note(d, 190, Y + 16, "25 \u00b0C\n1.5 bar", anchor="top_center", size=11)
        note(d, 445, Y + 16, "150 \u00b0C\n10 bar", anchor="top_center", size=11)
        note(d, 740, 218, "150 \u00b0C, 2 bar", anchor="top_center", size=11)
        # Key.
        kx, ky = 60.0, 570.0
        note(d, kx, ky - 22, "**Key**", size=12)
        pump(d, kx + 20, ky + 14, 12)
        note(d, kx + 40, ky + 14, "pump")
        valve(d, kx + 140, ky + 14, 9)
        note(d, kx + 158, ky + 14, "valve")
        exchanger(d, kx + 270, ky + 14, 15)
        note(d, kx + 292, ky + 14, "exchanger (tubes as zigzag)")
        bubble(d, kx + 520, ky + 14, "PIC", "1", r=14, panel=True)
        note(d, kx + 540, ky + 14, "control-room instrument, dashed = signal")
        snum(d, kx + 840, ky + 14, "n")
        note(d, kx + 856, ky + 14, "stream number")
        d.caption("**Figure 1:** Simple process flow diagram with feed preheater, reactor and flash separator",
                  small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "01_simple_process_flow")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
