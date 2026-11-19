"""A full adder built from gates, with every signal traced for one input case.

Two half adders and an OR gate add three bits: $A$, $B$ and the carry-in
$C_{in}$. The script evaluates each gate for the chosen input case
($A = B = C_{in} = 1$) and draws each wire by its value: a heavy blue line
carries a 1, a thin grey one a 0. The sum and carry-out it computes are checked
against ordinary addition.
"""
from __future__ import annotations

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


HIGH = "#1F4E9C"
LOW = "#7A7A7A"
INPUT = {"A": 1, "B": 1, "Cin": 1}


def trace(a: int, b: int, cin: int) -> dict[str, int]:
    """Value on every wire of the full adder."""
    p = a ^ b
    g1 = a & b
    g2 = p & cin
    s = p ^ cin
    cout = g1 | g2
    assert 2 * cout + s == a + b + cin  # agrees with ordinary addition
    return {"A": a, "B": b, "Cin": cin, "P": p, "G1": g1, "G2": g2, "S": s, "Cout": cout}


def wire(diag: Diagram, points, value: int) -> None:
    style = Style(stroke=HIGH, stroke_width=2.4) if value else Style(stroke=LOW, stroke_width=1.3, dash="5,3")
    diag.polyline(points, style=style, obstacle=False)


def tag(diag: Diagram, text: str, value: int, x: float, y: float, anchor: str = "bottom_center") -> None:
    colour = HIGH if value else LOW
    diag.text(f"${text} = {value}$", size=12, color=colour, align="center").at(x, y, anchor=anchor)


def diagram() -> Diagram:
    v = trace(**{"a": INPUT["A"], "b": INPUT["B"], "cin": INPUT["Cin"]})
    with Diagram("Full adder", theme="paper") as diag:
        # Gates (pins are 16 px in front of the body, outputs 16 px behind it).
        x1, x2, xo = 210.0, 450.0, 670.0
        y_x1, y_a1 = 60.0, 170.0
        y_x2, y_a2 = 72.5, 260.0
        y_or = 182.5
        xin1, xout1 = gate(diag, "XOR", x1, y_x1, stubs=False)
        ain1, aout1 = gate(diag, "AND", x1, y_a1, stubs=False)
        xin2, xout2 = gate(diag, "XOR", x2, y_x2, stubs=False)
        ain2, aout2 = gate(diag, "AND", x2, y_a2, stubs=False)
        oin, oout = gate(diag, "OR", xo, y_or, stubs=False)

        def lead(pin, kind: str, x: float) -> list[tuple[float, float]]:
            inset = 7.0 if kind == "OR" else 0.0
            return [pin, (x + inset, pin[1])]

        # Gate leads carry the value of the wire that arrives there.
        wires: list[tuple[list[tuple[float, float]], int]] = []
        a, b, c = v["A"], v["B"], v["Cin"]
        left = 70.0
        bus_a, bus_b, bus_c = 135.0, 160.0, 395.0
        pa, pb = xin1[0][1], xin1[1][1]
        # A and B
        wires += [([(left, pa), (xin1[0][0], pa)], a), ([(bus_a, pa), (bus_a, ain1[0][1]), ain1[0]], a)]
        wires += [([(left, pb), (xin1[1][0], pb)], b), ([(bus_b, pb), (bus_b, ain1[1][1]), ain1[1]], b)]
        # P = A xor B to the second half adder
        wires += [([xout1, xin2[0]], v["P"]), ([(350, xout1[1]), (350, ain2[0][1]), ain2[0]], v["P"])]
        # carry-in
        cy = 345.0
        wires += [([(left, cy), (bus_c, cy), (bus_c, xin2[1][1]), xin2[1]], c), ([(bus_c, ain2[1][1]), ain2[1]], c)]
        # G1 and G2 into the OR
        wires += [([aout1, (oin[0][0] - 20, aout1[1]), oin[0]], v["G1"])]
        wires += [([aout2, (oin[1][0] - 40, aout2[1]), (oin[1][0] - 40, oin[1][1]), oin[1]], v["G2"])]
        # outputs
        wires += [([xout2, (850, xout2[1])], v["S"]), ([oout, (850, oout[1])], v["Cout"])]
        # Draw 0-wires first so 1-wires are on top at crossings.
        for pts, val in sorted(wires, key=lambda w: w[1]):
            wire(diag, pts, val)
        # Short leads from each pin into its gate body.
        for kind, pins, x, vals in (
            ("XOR", xin1, x1, (a, b)), ("AND", ain1, x1, (a, b)),
            ("XOR", xin2, x2, (v["P"], c)), ("AND", ain2, x2, (v["P"], c)),
            ("OR", oin, xo, (v["G1"], v["G2"])),
        ):
            for pin, val in zip(pins, vals):
                wire(diag, lead(pin, kind, x), val)
        for pin_out, val, x in ((xout1, v["P"], x1 + GW), (aout1, v["G1"], x1 + GW), (xout2, v["S"], x2 + GW),
                                (aout2, v["G2"], x2 + GW), (oout, v["Cout"], xo + GW)):
            wire(diag, [(x, pin_out[1]), pin_out], val)

        for x, y, val in ((bus_a, pa, a), (bus_b, pb, b), (350, xout1[1], v["P"]), (bus_c, ain2[1][1], c)):
            diag.point(x, y, dot=True, radius=3.2, color=HIGH if val else LOW)

        # Signal values.
        tag(diag, "A", a, left - 6, pa, "right_center")
        tag(diag, "B", b, left - 6, pb, "right_center")
        tag(diag, "C_{in}", c, left - 6, cy, "right_center")
        tag(diag, "P", v["P"], 382, xout1[1] - 7, "bottom_center")
        tag(diag, "G_1", v["G1"], 610, aout1[1] - 7, "bottom_center")
        tag(diag, "G_2", v["G2"], 596, aout2[1] + 7, "top_center")
        tag(diag, "S", v["S"], 850 + 6, xout2[1], "left_center")
        tag(diag, "C_{out}", v["Cout"], 850 + 6, oout[1], "left_center")

        # The two half adders, outlined.
        dash = Style(fill="none", stroke="#888888", stroke_width=1.0, dash="6,4")
        diag.polygon(_rect(x1 - 36, y_x1 - 22, GW + 36 + 40, 235), style=dash, obstacle=False)
        diag.text("*half adder 1*", size=12, font="serif").at(x1 - 36, y_x1 - 26, anchor="bottom_left")
        diag.polygon(_rect(x2 - 36, y_x2 - 22, GW + 36 + 40, 275), style=dash, obstacle=False)
        diag.text("*half adder 2*", size=12, font="serif").at(x2 - 36, y_x2 - 26, anchor="bottom_left")

        # The trace, one line per gate.
        sym = {"XOR": r"\oplus", "AND": r"\cdot", "OR": "+"}
        rows = [
            rf"$P = A \oplus B = {a} \oplus {b} = {v['P']}$",
            rf"$G_1 = A \cdot B = {a} \cdot {b} = {v['G1']}$",
            rf"$S = P \oplus C_{{in}} = {v['P']} \oplus {c} = {v['S']}$",
            rf"$G_2 = P \cdot C_{{in}} = {v['P']} \cdot {c} = {v['G2']}$",
            rf"$C_{{out}} = G_1 + G_2 = {v['G1']} + {v['G2']} = {v['Cout']}$",
        ]
        diag.text("**Trace for** $A = B = C_{in} = 1$", size=13).at(70, 400)
        diag.text("\n".join(rows), size=13).at(70, 426)
        diag.text(
            rf"Check: $A + B + C_{{in}} = {a + b + c}$ and $2C_{{out}} + S = {2 * v['Cout'] + v['S']}$.",
            size=12, font="serif", italic=True,
        ).at(480, 426)
        # Legend.
        diag.polyline([(480, 480), (520, 480)], style=Style(stroke=HIGH, stroke_width=2.4), obstacle=False)
        diag.text("logic 1", size=12).at(528, 480, anchor="left_center")
        diag.polyline([(610, 480), (650, 480)], style=Style(stroke=LOW, stroke_width=1.3, dash="5,3"), obstacle=False)
        diag.text("logic 0", size=12).at(658, 480, anchor="left_center")
        diag.caption(
            "**Figure 3:** A full adder from two half adders and an OR gate, with the signals traced for $A = B = C_{in} = 1$",
            small_caps=True,
        )
    return diag


def _rect(x: float, y: float, w: float, h: float) -> list[tuple[float, float]]:
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def build_diagram(output_dir: Path | str = "examples/logic") -> Path:
    return render_all(diagram(), output_dir, "03_full_adder")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/logic")
    build_diagram(dest)
