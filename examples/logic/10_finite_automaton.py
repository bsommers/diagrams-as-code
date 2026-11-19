"""A deterministic finite automaton for binary numbers divisible by three.

The state is the remainder of the bits read so far. Reading a bit b turns a
remainder r into (2r + b) mod 3, and the script builds the transition
function from exactly that rule, then draws every arc from it: arcs between
the same two states are merged, opposite arcs bow apart, and a state that
loops to itself gets a loop above it. The start arrow marks $q_0$, and the
double border marks the accepting state. A worked run on the input 1001 (nine)
is traced from the same function.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

R = 30.0
STATES = [0, 1, 2]
CENTRES = {0: (170.0, 200.0), 1: (400.0, 200.0), 2: (630.0, 200.0)}
ACCEPT = {0}
INK = "#111111"
LINE = Style(fill="none", stroke=INK, stroke_width=1.5)
HEAD = Style(fill=INK, stroke=INK, stroke_width=0.5)

Point = tuple[float, float]


def delta(r: int, bit: int) -> int:
    return (2 * r + bit) % 3


def on_circle(c: Point, deg: float) -> Point:
    a = math.radians(deg)
    return (c[0] + R * math.cos(a), c[1] + R * math.sin(a))


def arrowhead(diag: Diagram, tip: Point, frm: Point, length: float = 11.0, half: float = 4.5) -> None:
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    n = math.hypot(dx, dy) or 1.0
    ux, uy = dx / n, dy / n
    base = (tip[0] - ux * length, tip[1] - uy * length)
    diag.polygon([tip, (base[0] - uy * half, base[1] + ux * half), (base[0] + uy * half, base[1] - ux * half)],
                 style=HEAD, obstacle=False)


def bezier(t: float, pts: list[Point]) -> Point:
    n = len(pts) - 1
    return (sum(math.comb(n, i) * (1 - t) ** (n - i) * t ** i * p[0] for i, p in enumerate(pts)),
            sum(math.comb(n, i) * (1 - t) ** (n - i) * t ** i * p[1] for i, p in enumerate(pts)))


def curve(diag: Diagram, pts: list[Point]) -> None:
    """A quadratic or cubic bezier from pts[0] to pts[-1], with an arrowhead that stops at the end point."""
    tip = pts[-1]
    d = ("M {:.2f} {:.2f} ".format(*pts[0])
         + ("Q {:.2f} {:.2f} {:.2f} {:.2f}" if len(pts) == 3 else "C {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}").format(
             *[v for p in pts[1:] for v in p]))
    diag.path(d, style=LINE, obstacle=False)
    arrowhead(diag, tip, pts[-2])


def diagram() -> Diagram:
    arcs: dict[tuple[int, int], list[str]] = {}
    for r in STATES:
        for bit in (0, 1):
            arcs.setdefault((r, delta(r, bit)), []).append(str(bit))

    with Diagram("DFA for multiples of three", theme="paper") as diag:
        diag.text(
            r"$L = \{\, w \in \{0,1\}^{*} \mid \mathrm{val}(w) \equiv 0 \ (\mathrm{mod}\ 3) \,\}$",
            size=16,
        ).at(400, 50, anchor="center")

        for s in STATES:
            diag.shape(f"$q_{s}$", 2 * R, 2 * R, style=Style(
                radius=R, font_size=16, fill="#FFFFFF", stroke_width=1.6, double=4 if s in ACCEPT else 0,
            )).at(*CENTRES[s], anchor="center")

        # start arrow into q0
        q0 = CENTRES[0]
        diag.polyline([(q0[0] - R - 70, q0[1]), (q0[0] - R - 10, q0[1])], style=LINE, obstacle=False)
        arrowhead(diag, (q0[0] - R, q0[1]), (q0[0] - R - 20, q0[1]))
        diag.text("start", size=12, font="serif", italic=True).at(q0[0] - R - 40, q0[1] - 10, anchor="bottom_center")

        for (a, b), bits in sorted(arcs.items()):
            label = ", ".join(bits)
            ca, cb = CENTRES[a], CENTRES[b]
            if a == b:
                s, e = on_circle(ca, -125), on_circle(ca, -55)
                curve(diag, [s, (s[0] - 22, s[1] - 58), (e[0] + 22, e[1] - 58), e])
                diag.text(label, size=14).at(ca[0], ca[1] - R - 52, anchor="bottom_center")
            else:
                up = a < b  # left-to-right arcs bow upward, right-to-left arcs bow downward
                sign = -1 if up else 1
                s, e = (on_circle(ca, -40), on_circle(cb, -140)) if up else (on_circle(ca, 140), on_circle(cb, 40))
                ctrl = ((s[0] + e[0]) / 2, (s[1] + e[1]) / 2 + sign * 62)
                curve(diag, [s, ctrl, e])
                mid = bezier(0.5, [s, ctrl, e])
                diag.text(label, size=14).at(mid[0], mid[1] + sign * 6,
                                             anchor="bottom_center" if up else "top_center")

        # transition table
        tx, ty, cw, ch = 70.0, 330.0, 56.0, 30.0
        for j, h in enumerate((r"$\delta$", "0", "1")):
            diag.polygon(_rect(tx + j * cw, ty, cw, ch), h, style=Style(fill="#D9DCE3", stroke_width=1.2, font_size=14))
        for i, s in enumerate(STATES):
            row = (rf"$q_{s}$", rf"$q_{delta(s, 0)}$", rf"$q_{delta(s, 1)}$")
            for j, text in enumerate(row):
                diag.polygon(_rect(tx + j * cw, ty + (i + 1) * ch, cw, ch), text,
                             style=Style(fill="#D9DCE3" if j == 0 else "#FFFFFF", stroke_width=1.0, font_size=14))
        diag.text(r"$\delta(r, b) = (2r + b)\ \mathrm{mod}\ 3$", size=13, align="center").at(
            tx + 1.5 * cw, ty + 4 * ch + 12, anchor="top_center")

        # trace of one run
        word = "1001"
        value = int(word, 2)
        state, run = 0, [0]
        for bit in word:
            state = delta(state, int(bit))
            run.append(state)
        px, py, step = 400.0, 360.0, 64.0
        diag.text(f"**Run on** {word} (= {value})", size=13).at(px, ty - 6, anchor="bottom_left")
        for k, s in enumerate(run):
            x = px + 20 + k * step
            diag.polygon(_circle_box(x, py, 18), rf"$q_{s}$",
                         style=Style(fill="#BFD3EC" if (k == len(run) - 1 and s in ACCEPT) else "#FFFFFF",
                                     stroke_width=1.3, font_size=13), obstacle=False)
            if k:
                x0 = px + 20 + (k - 1) * step + 18
                diag.polyline([(x0, py), (x - 18 - 8, py)], style=Style(stroke=INK, stroke_width=1.2), obstacle=False)
                arrowhead(diag, (x - 18, py), (x - 30, py), length=9, half=3.5)
                diag.text(word[k - 1], size=13).at((x0 + x - 18) / 2, py - 6, anchor="bottom_center")
        verdict = "accepted" if run[-1] in ACCEPT else "rejected"
        diag.text(f"ends in $q_{run[-1]}$: {verdict}", size=12, font="serif", italic=True).at(
            px, py + 34, anchor="top_left")
        diag.caption(
            "**Figure 10:** A DFA over $\\{0,1\\}$ that accepts binary numbers divisible by 3; $q_0$, double-bordered, is accepting",
            small_caps=True,
        )
    return diag


def _rect(x: float, y: float, w: float, h: float) -> list[Point]:
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def _circle_box(cx: float, cy: float, r: float) -> list[Point]:
    return [(cx + r * math.cos(math.tau * k / 48), cy + r * math.sin(math.tau * k / 48)) for k in range(48)]


def build_diagram(output_dir: Path | str = "examples/logic") -> Path:
    return render_all(diagram(), output_dir, "10_finite_automaton")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/logic")
    build_diagram(dest)
