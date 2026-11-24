"""An SPI mode-0 transfer: chip select, clock, MOSI and MISO for one byte each way.

Mode 0 (CPOL = 0, CPHA = 0) idles the clock low and samples on the rising edge,
while the data lines change on the falling edge. The bit pattern drawn on each data
line (0xA5 out, 0x3C back, MSB first) is generated from the byte values, and the
timing figures follow from the clock frequency. A table lists the four modes.
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


F_SCLK = 1e6                  # hertz
MOSI_BYTE, MISO_BYTE = 0xA5, 0x3C
X0, SLOT, EDGE, HALF = 190.0, 62.0, 5.0, 14.0   # first bit, bit width, edge slope, half swing in px
BLUE, RED, GREEN = "#1F2F57", "#9C2F2F", "#2F6B3A"
SIG = Style(fill="none", stroke=BLUE, stroke_width=2.2)


def bits(byte: int):
    return [(byte >> (7 - k)) & 1 for k in range(8)]


def digital(y: float, edges):
    """Path for a logic signal: ``edges`` is [(x, level)], level 1 high, 0 low; first entry sets the start."""
    pts = [(edges[0][0], y - HALF if edges[0][1] else y + HALF)]
    for x, lvl in edges[1:]:
        prev_y = pts[-1][1]
        new_y = y - HALF if lvl else y + HALF
        pts += [(x, prev_y), (x + EDGE, new_y)]
    return seg(*pts)


def bus_cell(y: float, xa: float, xb: float):
    return [(xa, y), (xa + EDGE, y - HALF), (xb - EDGE, y - HALF), (xb, y), (xb - EDGE, y + HALF), (xa + EDGE, y + HALF)]


def diagram() -> Diagram:
    t_bit = 1e6 / F_SCLK                       # microseconds per bit
    ys = {"cs": 120.0, "sclk": 200.0, "mosi": 290.0, "miso": 370.0}
    xe = X0 + 8 * SLOT
    with Diagram("SPI mode 0 timing", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=13, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        # chip select: high, falls just before the first bit, rises after the last falling clock edge
        diag.path(digital(ys["cs"], [(X0 - 70, 1), (X0 - 18, 0), (xe + 24, 1), (xe + 90, 1)]), style=SIG)
        # clock: low, rising mid-slot, falling at the slot boundary
        clk = [(X0 - 70, 0)]
        for k in range(8):
            clk += [(X0 + SLOT * k + SLOT / 2, 1), (X0 + SLOT * (k + 1), 0)]
        clk.append((xe + 90, 0))
        diag.path(digital(ys["sclk"], clk), style=SIG)
        # data lines: idle (flat) lines at the ends and one hexagon per bit
        for key, byte, colour in (("mosi", MOSI_BYTE, BLUE), ("miso", MISO_BYTE, GREEN)):
            y = ys[key]
            diag.path(seg((X0 - 70, y), (X0 - 18, y)) + " " + seg((xe + 24, y), (xe + 90, y)),
                      style=Style(fill="none", stroke="#8A8F9C", stroke_width=1.6, dash="4,3"))
            for k, b in enumerate(bits(byte)):
                xa, xb = X0 + SLOT * k, X0 + SLOT * (k + 1)
                diag.polygon(bus_cell(y, xa, xb), style=Style(fill="#EEF2FA" if key == "mosi" else "#EAF3EC",
                                                              stroke=colour, stroke_width=1.8))
                text(str(b), (xa + xb) / 2, y, size=14)
        # left-hand names
        for key, name, sub in (("cs", "CS", "active low"), ("sclk", "SCLK", "CPOL = 0: idle low"),
                               ("mosi", "MOSI", f"controller out: 0x{MOSI_BYTE:02X}"),
                               ("miso", "MISO", f"peripheral out: 0x{MISO_BYTE:02X}")):
            text(f"**{name}**", X0 - 84, ys[key] - 8, anchor="right_center", size=14)
            text(sub, X0 - 84, ys[key] + 10, anchor="right_center", size=11, color="#555555")
        # bit numbers above the chip-select row
        for k in range(8):
            text(f"D{7 - k}", X0 + SLOT * k + SLOT / 2, ys["cs"] - 40, size=12, color="#555555")
        text("MSB first", X0 + 4 * SLOT, ys["cs"] - 58, size=12, color="#555555")
        # sample points on the rising edges
        for k in range(8):
            x = X0 + SLOT * k + SLOT / 2
            gaps = " ".join([
                seg((x, ys["sclk"] - HALF - 6), (x, ys["mosi"] - HALF - 3)),
                seg((x, ys["mosi"] + HALF + 3), (x, ys["miso"] - HALF - 3)),
                seg((x, ys["miso"] + HALF + 3), (x, ys["miso"] + HALF + 14))])
            diag.path(gaps, style=Style(fill="none", stroke=RED, stroke_width=0.9, dash="3,4"), obstacle=False)
        text("sample on rising edge", X0 + SLOT * 0.5, ys["miso"] + 44, size=12, color=RED)
        text("data changes on falling edge", X0 + SLOT * 2.0, ys["miso"] + 62, size=12, color="#555555")
        # clock period and bit time
        yb = ys["sclk"] + 42
        diag.connect((X0 + SLOT * 2.5, yb), (X0 + SLOT * 3.5, yb), routing="direct", two_way=True, width=0.9, arrow_size=0.6)
        text(f"$T_{{SCLK}} = {t_bit:g}\\,\\mu\\mathrm{{s}}$", X0 + SLOT * 3.0, yb + 4, anchor="top_center", size=12)
        diag.connect((X0 - 18, ys["cs"] + 34), (xe + 24, ys["cs"] + 34), routing="direct", two_way=True, width=0.9, arrow_size=0.6)
        text(f"CS low for 8 bits = {8 * t_bit:g} $\\mu$s at $f_{{SCLK}}$ = {F_SCLK / 1e6:g} MHz",
             (X0 - 18 + xe + 24) / 2, ys["cs"] + 38, anchor="top_center", size=12)

        ty = ys["miso"] + 100
        text("**The four SPI modes**", X0 - 120, ty, anchor="left_center", size=13)
        rows = [("mode", "CPOL", "CPHA", "clock idle", "sample edge"), ("0", "0", "0", "low", "rising (shown)"),
                ("1", "0", "1", "low", "falling"), ("2", "1", "0", "high", "falling"), ("3", "1", "1", "high", "rising")]
        cols = [0, 56, 112, 170, 270]
        diag.path(seg((X0 - 120, ty + 31), (X0 + 160, ty + 31)), style=Style(fill="none", stroke=INK, stroke_width=1.0))
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                text(f"**{cell}**" if r == 0 else cell, X0 - 120 + cols[c], ty + 18 + 22 * r + (8 if r else 0), anchor="left_center", size=12)
        text(f"Result: the controller sent 0x{MOSI_BYTE:02X} = {MOSI_BYTE:08b} and read back 0x{MISO_BYTE:02X} = {MISO_BYTE:08b}.",
             X0 - 120, ty + 140, anchor="top_left", size=13, font="serif", italic=True)
        diag.caption("**Figure 7:** SPI mode 0 exchanges one byte in each direction while chip select is held low", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "07_spi_mode0_timing")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
