"""Mass-balance blocks with a stream table: n-butane isomerisation with recycle.

Fresh n-butane (100 kmol/h) is mixed with recycle and fed to a reactor that
converts 25 % of the n-butane to isobutane per pass. A separator returns all
unreacted n-butane and delivers pure isobutane. Isomerisation conserves moles
and mass, so every block balances in kmol/h and in kg/h. With a recycle the
unknowns are solved from the overall balance: the product equals the fresh feed
(100 kmol/h), the reactor feed is product / X = 400 kmol/h, and the recycle is
reactor feed minus fresh feed = 300 kmol/h. The table and the block checks are
computed from these numbers.
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


MW = 58.12  # kg/kmol, C4H10
FRESH, X = 100.0, 0.25
BLOCK = Style(fill="#E6EDF5", font_size=13)


def streams():
    """(number, description, n-butane, isobutane) in kmol/h."""
    rin = FRESH / X  # reactor feed
    rec = rin - FRESH
    return [
        (1, "Fresh feed", FRESH, 0.0),
        (2, "Reactor feed", rin, 0.0),
        (3, "Reactor effluent", rin * (1 - X), rin * X),
        (4, "Product", 0.0, rin * X),
        (5, "Recycle", rec, 0.0),
    ]


def diagram() -> Diagram:
    s = {n: (a, b) for n, _, a, b in streams()}
    tot = {n: a + b for n, (a, b) in s.items()}
    assert abs(tot[1] + tot[5] - tot[2]) < 1e-9  # mixer
    assert abs(tot[2] - tot[3]) < 1e-9  # reactor conserves moles
    assert abs(tot[3] - tot[4] - tot[5]) < 1e-9  # separator
    y = 190.0
    with Diagram("Mass-Balance Blocks with Stream Table", theme="paper") as d:

        def block(label, x):
            return d.shape(label, 170, 80, style=BLOCK).at(x, y, anchor="center")

        mixer = block("**Mixer** M-101", 200)
        reactor = block(f"**Reactor** R-101\nX = {X:.0%} per pass", 440)
        sep = block("**Separator** V-101\nsharp split", 680)
        for a, b in ((mixer, reactor), (reactor, sep)):
            d.connect(a.anchor("right", 0.5), b.anchor("left", 0.5), routing="direct", **PIPE)
        stream(d, [(30, y), (115, y)])
        stream(d, [(765, y), (900, y)])
        # Recycle from separator bottom back to the mixer.
        yr = y + 110
        stream(d, [(680, y + 40), (680, yr), (200, yr), (200, y + 40)])
        for x, num, dy in ((62, 1, -22), (320, 2, -22), (560, 3, -22), (840, 4, -22), (440, 5, 22)):
            yy = yr + dy if num == 5 else y + dy
            snum(d, x, yy, num)
        note(d, 30, y + 14, "n-butane feed", anchor="top_left")
        note(d, 840, y + 14, "isobutane product", anchor="top_center")
        note(d, 440, yr + 34, "unreacted n-butane", anchor="top_center")
        # Block balances.
        checks = [
            (200, f"in {tot[1]:g} + {tot[5]:g} = out {tot[2]:g}"),
            (440, f"in {tot[2]:g} = out {tot[3]:g}"),
            (680, f"in {tot[3]:g} = out {tot[4]:g} + {tot[5]:g}"),
        ]
        for x, text in checks:
            note(d, x, y - 52, text + " kmol/h", anchor="bottom_center", size=11)
        # Stream table.
        cols = [70, 120, 290, 410, 540, 660, 790]
        heads = ["No.", "Stream", "n-butane, kmol/h", "isobutane, kmol/h", "total, kmol/h", "mass, kg/h", "n-C4 mol %"]
        ty = 400.0
        for x, h in zip(cols, heads):
            d.text(f"**{h}**", size=12).at(x, ty, anchor="left_center")
        d.polyline([(cols[0] - 6, ty + 14), (cols[-1] + 100, ty + 14)],
                   style=Style(fill="none", stroke=INK, stroke_width=1.0), z=1)
        for r, (n, name, a, b) in enumerate(streams()):
            t = a + b
            vals = [str(n), name, f"{a:.0f}", f"{b:.0f}", f"{t:.0f}", f"{t * MW:,.0f}", f"{100 * a / t:.0f}"]
            for x, v in zip(cols, vals):
                d.text(v, size=12).at(x, ty + 30 + 24 * r, anchor="left_center")
        d.polyline([(cols[0] - 6, ty + 30 + 24 * 5 - 12), (cols[-1] + 100, ty + 30 + 24 * 5 - 12)],
                   style=Style(fill="none", stroke=INK, stroke_width=0.8), z=1)
        d.text(
            f"Overall: in {tot[1]:g} kmol/h = out {tot[4]:g} kmol/h ({tot[1] * MW:,.0f} kg/h). "
            f"Recycle ratio R/F = {tot[5] / tot[1]:g}; reactor feed = F/X = {tot[2]:g} kmol/h. "
            f"M = {MW} kg/kmol.", size=12, italic=True,
        ).at(70, ty + 30 + 24 * 5 + 14, anchor="top_left")
        d.caption("**Figure 5:** Block flow diagram of an isomerisation loop with the stream table that closes the balance",
                  small_caps=True)
    return d


def build_diagram(output_dir: Path | str = "examples/chemical_engineering") -> Path:
    return render_all(diagram(), output_dir, "05_mass_balance_blocks")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemical_engineering")
    build_diagram(dest)
