"""An I2C write transaction: START, address byte, ACK, data byte, ACK and STOP.

SCL idles high; SDA may change only while SCL is low, except for START (SDA falls
while SCL is high) and STOP (SDA rises while SCL is high). The bit values drawn on
SDA are generated from the 7-bit address 0x48 and the data byte 0xA5, the ACK slots
are driven low by the peripheral, and the timing follows from a 100 kHz clock.
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


F_SCL = 100e3                       # hertz (standard mode)
ADDR7, DATA = 0x48, 0xA5
VDD, RP, CB = 3.3, 4.7e3, 100e-12   # volt, pull-up ohm, bus capacitance farad
XS, W, EDGE, HALF = 200.0, 32.0, 4.0, 14.0
BLUE, RED, GREEN = "#1F2F57", "#9C2F2F", "#2F6B3A"
SIG = Style(fill="none", stroke=BLUE, stroke_width=2.2)


def diagram() -> Diagram:
    t_bit = 1e6 / F_SCL                                  # microseconds per clock
    addr_bits = [(ADDR7 >> (6 - k)) & 1 for k in range(7)]
    data_bits = [(DATA >> (7 - k)) & 1 for k in range(8)]
    # one entry per SCL slot: (label, SDA level, driven by the peripheral?)
    slots = ([(f"A{6 - k}", b, False) for k, b in enumerate(addr_bits)] + [("W", 0, False), ("ACK", 0, True)]
             + [(f"D{7 - k}", b, False) for k, b in enumerate(data_bits)] + [("ACK", 0, True)])
    s0 = XS + W / 2                                      # SCL falls: first slot starts
    slot_x = [s0 + W * k for k in range(len(slots) + 1)]
    x_stop = slot_x[-1] + W * 0.75                       # SDA rises while SCL is high
    x_end = x_stop + 50
    y_scl, y_sda = 170.0, 280.0
    hi, lo = lambda y: y - HALF, lambda y: y + HALF
    with Diagram("I2C start, acknowledge and stop", theme="paper") as diag:
        def text(s, x, yy, anchor="center", size=13, **kw):
            diag.text(s, size=size, **kw).at(x, yy, anchor=anchor)

        # SCL: high idle, one low-then-high pulse per slot, high again after the last slot
        pts = [(XS - 70, hi(y_scl)), (XS + W / 2, hi(y_scl))]
        for k in range(len(slots) + 1):
            s = slot_x[k]
            pts += [(s + EDGE, lo(y_scl)), (s + W / 2, lo(y_scl)), (s + W / 2 + EDGE, hi(y_scl))]
            if k == len(slots):
                break
            pts += [(slot_x[k + 1], hi(y_scl))]
        pts.append((x_end, hi(y_scl)))
        diag.path(seg(*pts), style=SIG)
        # SDA: high idle, START, one level per slot (changing a quarter slot after SCL falls), STOP
        sda = [(XS - 70, hi(y_sda)), (XS, hi(y_sda)), (XS + EDGE, lo(y_sda))]
        level = 0
        for k, (_, b, _p) in enumerate(slots):
            x = slot_x[k] + W / 4
            if b != level:
                sda += [(x, lo(y_sda) if level == 0 else hi(y_sda)), (x + EDGE, hi(y_sda) if b else lo(y_sda))]
                level = b
        sda += [(x_stop, lo(y_sda)), (x_stop + EDGE, hi(y_sda)), (x_end, hi(y_sda))]
        diag.path(seg(*sda), style=SIG)
        # shaded ACK slots, the peripheral driving SDA low
        for k, (name, b, periph) in enumerate(slots):
            if periph:
                xa, xb = slot_x[k] + W / 4, slot_x[k + 1] + W / 4
                diag.polygon([(xa, y_sda - 34), (xb, y_sda - 34), (xb, y_sda + 34), (xa, y_sda + 34)],
                             style=Style(fill="#E4F1E7", stroke="none", stroke_width=0.0), z=-2)
                diag.path(seg((xa + EDGE, lo(y_sda)), (xb, lo(y_sda))), style=Style(fill="none", stroke=GREEN, stroke_width=2.6))
        # labels: bit names above SCL, bit values under SDA
        for k, (name, b, periph) in enumerate(slots):
            xc = slot_x[k] + 0.75 * W
            text(name, xc, y_scl - 40, size=11, color=GREEN if periph else "#555555")
            text(str(b), xc, y_sda + 40, size=12, color=GREEN if periph else BLUE)
        # START and STOP markers
        for x, name, ytxt in ((XS, "START", 86.0), (x_stop, "STOP", 86.0)):
            diag.path(seg((x, ytxt + 8), (x, y_sda + HALF + 4)), style=Style(fill="none", stroke=RED, stroke_width=1.0, dash="3,4"),
                      obstacle=False)
            text(f"**{name}**", x, ytxt, size=13, color=RED, anchor="bottom_center")
        text("SDA falls while SCL is high", XS - 8, 62, size=11, color=RED, anchor="bottom_left")
        text("SDA rises while SCL is high", x_stop + 8, 62, size=11, color=RED, anchor="bottom_right")
        # byte brackets
        for ka, kb, name in ((0, 8, "address byte"), (9, 17, "data byte")):
            xa, xb = slot_x[ka] + 4, slot_x[kb] - 4 + W
            yb = y_sda + 62
            diag.path(seg((xa, yb - 6), (xa, yb), (xb, yb), (xb, yb - 6)), style=Style(fill="none", stroke="#555555", stroke_width=1.0))
            text(name, (xa + xb) / 2, yb + 6, size=12, anchor="top_center")
        # names on the left
        for y, name, sub in ((y_scl, "SCL", "controller drives"), (y_sda, "SDA", "open drain, shared")):
            text(f"**{name}**", XS - 84, y - 8, anchor="right_center", size=14)
            text(sub, XS - 84, y + 10, anchor="right_center", size=11, color="#555555")
        t_rise = 0.8473 * RP * CB
        text(
            f"Standard mode, $f_{{SCL}}$ = {F_SCL / 1e3:g} kHz: one bit = {t_bit:g} $\\mu$s, so the 9-clock address phase takes {9 * t_bit:g} $\\mu$s\n"
            f"and the whole 18-clock frame {18 * t_bit:g} $\\mu$s. Address 0x{ADDR7:02X} = {ADDR7:07b}b goes out as 0x{(ADDR7 << 1):02X} with R/W = 0 (write).\n"
            f"The peripheral ACKs by holding SDA low for the 9th clock; the controller then sends 0x{DATA:02X} = {DATA:08b}b.\n"
            f"Pull-ups ($R_p$ = {RP / 1e3:g} k$\\Omega$ to {VDD:g} V) with {CB * 1e12:g} pF of bus capacitance give a 30%-70% rise time "
            f"$0.847\\,R_p C_b$ = {t_rise * 1e9:.0f} ns, inside the 1000 ns limit.",
            XS - 130, y_sda + 118, anchor="top_left", size=13)
        diag.caption("**Figure 8:** An I2C write: START, address, ACK, data, ACK and STOP", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/electronics") -> Path:
    return render_all(diagram(), output_dir, "08_i2c_start_ack_stop")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/electronics")
    build_diagram(dest)
