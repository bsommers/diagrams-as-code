"""The six basic logic gate symbols, and a half adder built from two of them.

Each gate is a free path in the distinctive-shape (ANSI/IEEE 91) notation: a
flat back and round front for AND, a curved back for OR, a second curved back
for XOR, a triangle for NOT, and a small circle on the output for the inverting
forms. A half adder adds two bits with an XOR for the sum and an AND for the
carry; its truth table is computed from the two gate functions.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

GW, GH = 70.0, 50.0
BODY = Style(fill="#F3F3F3", stroke="#111111", stroke_width=1.6)
WIRE = Style(stroke="#111111", stroke_width=1.4)
BUBBLE_R = 5.0

# kind -> (body path with origin at its top-left corner, inverted output?, curved back?)
BODIES = {
    "AND": (f"M 0 0 H {GW / 2} A {GW / 2} {GH / 2} 0 0 1 {GW / 2} {GH} H 0 Z", False),
    "NAND": (f"M 0 0 H {GW / 2} A {GW / 2} {GH / 2} 0 0 1 {GW / 2} {GH} H 0 Z", True),
    "OR": (f"M 0 0 Q {GW * 0.45} 0 {GW} {GH / 2} Q {GW * 0.45} {GH} 0 {GH} Q {GW * 0.26} {GH / 2} 0 0 Z", False),
    "NOR": (f"M 0 0 Q {GW * 0.45} 0 {GW} {GH / 2} Q {GW * 0.45} {GH} 0 {GH} Q {GW * 0.26} {GH / 2} 0 0 Z", True),
    "XOR": (f"M 0 0 Q {GW * 0.45} 0 {GW} {GH / 2} Q {GW * 0.45} {GH} 0 {GH} Q {GW * 0.26} {GH / 2} 0 0 Z", False),
    "NOT": (f"M 0 0 L {GW * 0.78} {GH / 2} L 0 {GH} Z", True),
}
FUNCTIONS = {
    "AND": (r"$Y = A \cdot B$", lambda a, b: a & b),
    "OR": (r"$Y = A + B$", lambda a, b: a | b),
    "NOT": (r"$Y = \neg A$", None),
    "NAND": (r"$Y = \neg(A \cdot B)$", lambda a, b: 1 - (a & b)),
    "NOR": (r"$Y = \neg(A + B)$", lambda a, b: 1 - (a | b)),
    "XOR": (r"$Y = A \oplus B$", lambda a, b: a ^ b),
}
STUB = 16.0


def translate(path: str, dx: float, dy: float) -> str:
    """Shift absolute path data (M L H V Q A) by (dx, dy)."""
    tokens, out, cmd, n = path.split(), [], "", 0
    for tok in tokens:
        if tok.isalpha():
            cmd, n = tok, 0
            out.append(tok)
            continue
        v = float(tok)
        if cmd in ("M", "L", "Q"):
            v += dx if n % 2 == 0 else dy
        elif cmd == "H":
            v += dx
        elif cmd == "V":
            v += dy
        elif cmd == "A":
            k = n % 7
            if k == 5:
                v += dx
            elif k == 6:
                v += dy
        n += 1
        out.append(f"{v:.2f}")
    return " ".join(out)


def gate(diag: Diagram, kind: str, x: float, y: float, stubs: bool = True):
    """Draw gate ``kind`` with top-left corner (x, y); returns (input pins, output pin)."""
    body, inverted = BODIES[kind]
    diag.path(translate(body, x, y), style=BODY)
    if kind == "XOR":
        back = f"M {-9} 0 Q {GW * 0.26 - 9} {GH / 2} {-9} {GH}"
        diag.path(translate(back, x, y), style=Style(fill="none", stroke="#111111", stroke_width=1.6))
    mid = y + GH / 2
    if kind == "NOT":
        ins = [(x - STUB, mid)]
        tip = x + GW * 0.78
    else:
        ins = [(x - STUB, y + GH * 0.25), (x - STUB, y + GH * 0.75)]
        tip = x + GW
    out_x = tip
    if inverted:
        diag.path(
            f"M {tip:.2f} {mid:.2f} a {BUBBLE_R} {BUBBLE_R} 0 1 1 {2 * BUBBLE_R} 0 "
            f"a {BUBBLE_R} {BUBBLE_R} 0 1 1 {-2 * BUBBLE_R} 0 Z",
            style=Style(fill="#FFFFFF", stroke="#111111", stroke_width=1.6),
        )
        out_x = tip + 2 * BUBBLE_R
    # Input leads reach the back of the body; OR-type backs are curved, so run them in to the curve.
    inset = {"OR": 7.0, "NOR": 7.0, "XOR": 0.0}.get(kind, 0.0)
    back_x = x + inset
    leads = []
    if stubs:
        for px, py in ins:
            leads.append(((px, py), (back_x, py)))
        for a, b in leads:
            diag.polyline([a, b], style=WIRE, obstacle=False)
        diag.polyline([(out_x, mid), (out_x + STUB, mid)], style=WIRE, obstacle=False)
    return ins, (out_x + STUB, mid)


def diagram() -> Diagram:
    with Diagram("Logic gate symbols and a half adder", theme="paper") as diag:
        # --- the six gates, in two rows of three -------------------------------------------------
        order = ["AND", "OR", "NOT", "NAND", "NOR", "XOR"]
        col_w, row_h = 250.0, 130.0
        for k, kind in enumerate(order):
            x = 70 + (k % 3) * col_w
            y = 60 + (k // 3) * row_h
            gate(diag, kind, x, y)
            diag.text(f"**{kind}**", size=14, align="center").at(x + GW / 2, y + GH + 12, anchor="top_center")
            diag.text(FUNCTIONS[kind][0], size=12, align="center").at(x + GW / 2, y + GH + 32, anchor="top_center")

        # --- the half adder ---------------------------------------------------------------------
        top = 372.0
        diag.text("**Half adder**", size=16).at(70, top - 24, anchor="bottom_left")
        gx = 330.0
        y_xor, y_and = top + 10, top + 110
        xin, _ = gate(diag, "XOR", gx, y_xor)
        ain, _ = gate(diag, "AND", gx, y_and)
        x_in = 120.0
        bus_a, bus_b = 205.0, 245.0
        ya, yb = xin[0][1], xin[1][1]
        # A feeds the first input of both gates, B the second input of both.
        diag.polyline([(x_in, ya), (xin[0][0], ya)], style=WIRE, obstacle=False)
        diag.polyline([(bus_a, ya), (bus_a, ain[0][1]), (ain[0][0], ain[0][1])], style=WIRE, obstacle=False)
        diag.polyline([(x_in, yb), (bus_b, yb)], style=WIRE, obstacle=False)
        diag.polyline([(bus_b, yb), (xin[1][0], yb)], style=WIRE, obstacle=False)
        diag.polyline([(bus_b, yb), (bus_b, ain[1][1]), (ain[1][0], ain[1][1])], style=WIRE, obstacle=False)
        diag.point(bus_a, ya, dot=True, radius=3)
        diag.point(bus_b, yb, dot=True, radius=3)
        diag.text("$A$", size=15).at(x_in - 8, ya, anchor="right_center")
        diag.text("$B$", size=15).at(x_in - 8, yb, anchor="right_center")
        out_x = gx + GW + STUB + 2 * BUBBLE_R * 0
        for yy, name, tag in ((y_xor + GH / 2, "$S$", "sum"), (y_and + GH / 2, "$C$", "carry")):
            diag.polyline([(out_x, yy), (out_x + 60, yy)], style=WIRE, obstacle=False)
            diag.text(name, size=15).at(out_x + 68, yy, anchor="left_center")
            diag.text(f"({tag})", size=11, font="serif", italic=True).at(out_x + 90, yy, anchor="left_center")

        # --- its truth table, computed from the two gate functions ---------------------------------
        tx, ty, cw, ch = 640.0, top - 10, 44.0, 28.0
        heads = ("$A$", "$B$", "$C$", "$S$")
        for j, h in enumerate(heads):
            diag.polygon(_rect(tx + j * cw, ty, cw, ch), h, style=Style(fill="#D9DCE3", stroke_width=1.2, font_size=13))
        for i, (a, b) in enumerate(itertools.product((0, 1), repeat=2)):
            s, c = a ^ b, a & b
            for j, v in enumerate((a, b, c, s)):
                shade = "#BFD3EC" if (j >= 2 and v) else "#FFFFFF"
                diag.polygon(_rect(tx + j * cw, ty + ch * (i + 1), cw, ch), str(v),
                             style=Style(fill=shade, stroke_width=1.0, font_size=13))
        diag.text(r"$S = A \oplus B,\quad C = A \cdot B$", size=13, align="center").at(
            tx + 2 * cw, ty + ch * 5 + 10, anchor="top_center")
        diag.text(r"$2C + S = A + B$", size=12, font="serif", italic=True, align="center").at(
            tx + 2 * cw, ty + ch * 5 + 34, anchor="top_center")

        diag.caption(
            "**Figure 2:** The six basic gate symbols; a half adder adds two bits with an XOR (sum) and an AND (carry)",
            small_caps=True,
        )
    return diag


def _rect(x: float, y: float, w: float, h: float) -> list[tuple[float, float]]:
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def build_diagram(output_dir: Path | str = "examples/logic") -> Path:
    return render_all(diagram(), output_dir, "02_logic_gates")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/logic")
    build_diagram(dest)
