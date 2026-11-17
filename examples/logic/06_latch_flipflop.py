"""An SR latch built from NOR gates, and a D flip-flop, each with a timing diagram.

The latch is two cross-coupled NOR gates. Its waveforms are simulated by the
script: after every input change the gate equations Q = NOR(R, Q') and
Q' = NOR(S, Q) are iterated until they settle, and each output
changes a short propagation delay after the input that caused it. The D
flip-flop copies $D$ to $Q$ on each rising clock edge and holds it otherwise;
dashed guides mark the edges that sample $D$.
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



PX = 38.0  # pixels per time unit
SLOPE = 3.0
AMP = 22.0
PITCH = 44.0
WAVE = Style(stroke="#111111", stroke_width=1.6)
GUIDE = Style(stroke="#777777", stroke_width=0.7, dash="3,3")
LATCH_DELAY = (0.12, 0.26)  # propagation delay of the first and second NOR gate


def settle(s: int, r: int, q: int, qb: int) -> tuple[int, int]:
    """Iterate the two NOR equations until the latch is stable."""
    for _ in range(8):
        q2, qb2 = 1 - (r | qb), 1 - (s | q)
        if (q2, qb2) == (q, qb):
            break
        q, qb = q2, qb2
    return q, qb


def level_changes(events: list[tuple[float, int]], start: int = 0) -> list[float]:
    """Times at which a signal given as (time, new value) steps actually changes."""
    out, cur = [], start
    for t, v in events:
        if v != cur:
            out.append(t)
            cur = v
    return out


def latch_waveforms():
    """S, R as pulses; Q and Q-bar by simulation. Returns {name: (start level, change times)}."""
    s_events = [(1.0, 1), (2.0, 0), (5.0, 1), (6.0, 0)]
    r_events = [(3.0, 1), (4.0, 0)]
    times = sorted({t for t, _ in s_events + r_events})
    s = r = 0
    q, qb = settle(0, 1, 0, 1)  # start in the reset state
    q_events, qb_events = [], []
    for t in times:
        s = dict(s_events).get(t, s)
        r = dict(r_events).get(t, r)
        nq, nqb = settle(s, r, q, qb)
        assert not (s and r), "S = R = 1 is the forbidden input"
        if nq != q:
            q_events.append((t + LATCH_DELAY[0], nq))
        if nqb != qb:
            qb_events.append((t + LATCH_DELAY[1], nqb))
        q, qb = nq, nqb
    return {
        "S": (0, level_changes(s_events)), "R": (0, level_changes(r_events)),
        "Q": (0, level_changes(q_events)), "$Q'$": (1, level_changes(qb_events, 1)),
    }


def dff_waveforms():
    clk_rise = [1.0, 3.0, 5.0, 7.0]
    clk = [t for r in clk_rise for t in (r, r + 1.0)]
    d_events = [(2.3, 1), (4.4, 0), (6.2, 1)]
    d_changes = level_changes(d_events)

    def d_at(t: float) -> int:
        return sum(1 for c in d_changes if c <= t) % 2

    q_events, q = [], 0
    for r in clk_rise:
        if d_at(r - 0.01) != q:
            q = d_at(r - 0.01)
            q_events.append(r + 0.15)
    return clk_rise, {"CLK": (0, clk), "D": (0, d_changes), "Q": (0, q_events)}


def wave_points(x0: float, y_top: float, start: int, changes: list[float], t_end: float):
    def y(level: int) -> float:
        return y_top + (0.0 if level else AMP)

    level, pts = start, [(x0, y(start))]
    for t in changes:
        x = x0 + t * PX
        pts += [(x - SLOPE / 2, y(level)), (x + SLOPE / 2, y(1 - level))]
        level = 1 - level
    return pts + [(x0 + t_end * PX, y(level))]


def timing(diag: Diagram, x0: float, y0: float, waves: dict, t_end: float, guides: list[float] | None = None) -> float:
    """Draw a timing diagram; returns its bottom y."""
    bottom = y0 + PITCH * len(waves)
    for t in guides or []:
        diag.polyline([(x0 + t * PX, y0 - 16), (x0 + t * PX, bottom)], style=GUIDE, obstacle=False)
    for row, (name, (start, changes)) in enumerate(waves.items()):
        top = y0 + row * PITCH
        label = name if name.startswith("$") else f"${name}$"
        diag.text(label, size=14).at(x0 - 14, top + AMP / 2, anchor="right_center")
        diag.polyline(wave_points(x0, top, start, changes, t_end), style=WAVE)
    return bottom


def diagram() -> Diagram:
    with Diagram("SR latch and D flip-flop", theme="paper") as diag:
        # ---- SR latch schematic (NOR gates) -----------------------------------------------------
        gx, y1, y2 = 150.0, 50.0, 150.0
        in1, out1 = gate(diag, "NOR", gx, y1)
        in2, out2 = gate(diag, "NOR", gx, y2)
        left = 60.0
        pin = in1[0][0]
        # R into the first gate, S into the second
        diag.polyline([(left, in1[0][1]), (pin, in1[0][1])], style=WIRE, obstacle=False)
        diag.polyline([(left, in2[1][1]), (pin, in2[1][1])], style=WIRE, obstacle=False)
        diag.text("$R$", size=15).at(left - 8, in1[0][1], anchor="right_center")
        diag.text("$S$", size=15).at(left - 8, in2[1][1], anchor="right_center")
        # cross-coupling: Q to the second gate, Q-bar to the first
        xr, gap_q, gap_qb = out1[0] + 24, 118.0, 132.0
        xl_q, xl_qb = pin - 30, pin - 54
        diag.polyline([out1, (xr, out1[1]), (xr, gap_q), (xl_q, gap_q), (xl_q, in2[0][1]), in2[0]],
                      style=WIRE, obstacle=False)
        diag.polyline([out2, (xr, out2[1]), (xr, gap_qb), (xl_qb, gap_qb), (xl_qb, in1[1][1]), in1[1]],
                      style=WIRE, obstacle=False)
        diag.polyline([(xr, out1[1]), (xr + 50, out1[1])], style=WIRE, obstacle=False)
        diag.polyline([(xr, out2[1]), (xr + 50, out2[1])], style=WIRE, obstacle=False)
        diag.point(xr, out1[1], dot=True, radius=3)
        diag.point(xr, out2[1], dot=True, radius=3)
        diag.text("$Q$", size=15).at(xr + 58, out1[1], anchor="left_center")
        diag.text("$Q'$", size=15).at(xr + 58, out2[1], anchor="left_center")
        diag.text("**SR latch** (NOR)", size=13, align="center").at(gx + 40, y2 + GH + 24, anchor="top_center")

        # ---- D flip-flop symbol -----------------------------------------------------------------
        bx, by, bw, bh = 560.0, 70.0, 100.0, 120.0
        diag.polygon([(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh)],
                     style=Style(fill="#F3F3F3", stroke="#111111", stroke_width=1.6))
        dy, cy = by + 30, by + bh - 30
        diag.polyline([(bx - 40, dy), (bx, dy)], style=WIRE, obstacle=False)
        diag.polyline([(bx - 40, cy), (bx, cy)], style=WIRE, obstacle=False)
        diag.polyline([(bx, cy - 9), (bx + 14, cy), (bx, cy + 9)], style=Style(stroke="#111111", stroke_width=1.4),
                      obstacle=False)
        diag.polyline([(bx + bw, dy), (bx + bw + 40, dy)], style=WIRE, obstacle=False)
        diag.polyline([(bx + bw, cy), (bx + bw + 40, cy)], style=WIRE, obstacle=False)
        diag.text("$D$", size=15).at(bx - 48, dy, anchor="right_center")
        diag.text("CLK", size=13).at(bx - 48, cy, anchor="right_center")
        diag.text("$Q$", size=15).at(bx + bw + 48, dy, anchor="left_center")
        diag.text("$Q'$", size=15).at(bx + bw + 48, cy, anchor="left_center")
        diag.text("**D flip-flop**\n*(rising-edge)*", size=13, align="center").at(
            bx + bw / 2, by + bh / 2, anchor="center")

        # ---- timing diagrams --------------------------------------------------------------------
        ty = 330.0
        t_end = 8.5
        sx = 100.0
        latch = latch_waveforms()
        bottom = timing(diag, sx, ty, latch, t_end)
        for t0, t1, name in ((1.0, 2.0, "set"), (3.0, 4.0, "reset"), (5.0, 6.0, "set")):
            diag.text(f"*{name}*", size=11, font="serif").at(sx + (t0 + t1) / 2 * PX, ty - 18, anchor="bottom_center")
        diag.text("*hold*", size=11, font="serif", color="#666666").at(sx + 2.5 * PX, ty - 18, anchor="bottom_center")
        diag.text("*hold*", size=11, font="serif", color="#666666").at(sx + 4.5 * PX, ty - 18, anchor="bottom_center")
        diag.text("*hold*", size=11, font="serif", color="#666666").at(sx + 7.0 * PX, ty - 18, anchor="bottom_center")

        dx = 560.0 - 30
        rises, dff = dff_waveforms()
        timing(diag, dx, ty, dff, t_end, guides=rises)
        for k, r in enumerate(rises):
            diag.text(f"{k + 1}", size=11, color="#555555").at(dx + r * PX, ty - 20, anchor="bottom_center")
        diag.text("*rising clock edges sample $D$*", size=11, font="serif").at(dx, ty - 40, anchor="bottom_left")

        diag.text("time $\\to$", size=12, font="serif").at(sx + t_end * PX, bottom + 8, anchor="top_right")
        diag.text("time $\\to$", size=12, font="serif").at(dx + t_end * PX, bottom + 8, anchor="top_right")
        diag.text(
            "S = R = 1 is the forbidden input of the NOR latch and is not applied. "
            "At each rising edge the flip-flop takes the value $D$ had just before it.",
            size=12, font="serif", italic=True, max_width=820,
        ).at(60, bottom + 40)
        diag.caption(
            "**Figure 6:** An SR latch from NOR gates and a rising-edge D flip-flop, each with its timing diagram",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/logic") -> Path:
    return render_all(diagram(), output_dir, "06_latch_flipflop")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/logic")
    build_diagram(dest)
