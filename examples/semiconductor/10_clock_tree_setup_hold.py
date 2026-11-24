"""A clock tree with skew, and the setup and hold timing check it drives (SEMICONDUCTOR domain).

Top: a clock root fans out through buffers to four flip-flops; the launch flop FF1
sees the clock at 0.40 ns and the capture flop FF2 at 0.46 ns, a skew of 0.06 ns.
Bottom: the resulting timing diagram for the FF1 -> logic -> FF2 path at a 1 ns
period. The data changes somewhere inside the hatched window (between the fastest
and the slowest path); it must be stable one setup time before the capture edge and
one hold time after it. All numbers are illustrative and computed once in the script,
so the margins quoted are the ones drawn.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.draft import Draft
from diagrams_as_code.output import render_all

INK = "#1F2F57"
PX_PER_NS = 200.0
T, T_CQ_MIN, T_MAX, T_SU, T_H, SKEW = 1.0, 0.15, 0.725, 0.15, 0.06, 0.06  # ns
# T_CQ_MIN is t_cq + minimum logic delay; T_MAX is t_cq + maximum logic delay.
SETUP_SLACK = T + SKEW - T_MAX - T_SU
HOLD_MARGIN = T_CQ_MIN - T_H - SKEW
X0 = 130.0  # launch clock edge, x pixels


def diagram() -> Diagram:
    with Diagram("Clock tree skew and setup / hold timing (schematic, illustrative numbers)", theme="paper") as diag:
        k = Draft(diag, size=11.5)

        # ------------------------------------------------------------------ clock tree
        def node(label, x, y, w=120, h=44, fill="#FFFFFF"):
            return diag.shape(label, w, h, style=Style(fill=fill, stroke=INK, stroke_width=1.3)).at(x, y)

        root = node("Clock root\n(PLL output)", 390, 40, 140, 50, "#DDE6F5")
        b1 = node("Buffer L1a", 200, 140)
        b2 = node("Buffer L1b", 600, 140)
        ffs = [node("FF1  (launch)\nt = 0.40 ns", 90, 250, 140, 50, "#F4E3C1"),
               node("FF2  (capture)\nt = 0.46 ns", 280, 250, 140, 50, "#F4E3C1"),
               node("FF3\nt = 0.43 ns", 500, 250, 140, 50),
               node("FF4\nt = 0.45 ns", 690, 250, 140, 50)]
        for src, dst in ((root, b1), (root, b2), (b1, ffs[0]), (b1, ffs[1]), (b2, ffs[2]), (b2, ffs[3])):
            src >> diag.edge(width=1.4, color="#555555") >> dst
        # data path from FF1 through logic into FF2
        logic = node("combinational\nlogic", 160, 345, 150, 44, "#EEEEEE")
        ffs[0].anchor("bottom", 0.4) >> diag.edge("Q", color="#B03060", width=1.8) >> logic.anchor("left", 0.5)
        logic.anchor("right", 0.5) >> diag.edge("D", color="#B03060", width=1.8) >> ffs[1].anchor("bottom", 0.4)
        diag.text(f"clock skew = 0.46 - 0.40 = {SKEW:.2f} ns (balanced by CTS, never exactly zero)", size=12,
                  color="#444444").at(520, 345, anchor="left_center")

        # ------------------------------------------------------------------ timing diagram
        def X(t_ns: float) -> float:
            return X0 + t_ns * PX_PER_NS

        base_y = {"launch": 490.0, "data": 580.0, "capture": 670.0}
        H = 34.0

        def clock(y: float, delay: float) -> list[tuple[float, float]]:
            pts = [(X(-0.3 + delay), y)]
            t = -0.0 + delay
            while t < 2.05:
                pts += [(X(t), y), (X(t + 0.015), y - H), (X(t + 0.5), y - H), (X(t + 0.515), y), (X(t + 1.0), y)]
                t += 1.0
            return pts

        for name, label in (("launch", "CLK at FF1"), ("capture", "CLK at FF2")):
            diag.text(label, size=13).at(X0 - 150, base_y[name] - H / 2, anchor="left_center")
        diag.text("data  Q$\\to$D", size=13).at(X0 - 150, base_y["data"] - H / 2, anchor="left_center")
        diag.polyline(clock(base_y["launch"], 0.0), style=Style(fill="none", stroke=INK, stroke_width=1.8))
        diag.polyline(clock(base_y["capture"], SKEW), style=Style(fill="none", stroke=INK, stroke_width=1.8))

        # data: two rails that cross inside the unstable windows (hatched)
        y_hi, y_lo = base_y["data"] - H, base_y["data"]
        rails_style = Style(fill="none", stroke=INK, stroke_width=1.8)
        windows = [(T_CQ_MIN, T_MAX), (T_CQ_MIN + T, T_MAX + T)]
        last = X(2.05)
        diag.polyline([(X(-0.3), y_hi), (X(windows[0][0]), y_hi)], style=rails_style)
        diag.polyline([(X(-0.3), y_lo), (X(windows[0][0]), y_lo)], style=rails_style)
        for i, (a, b) in enumerate(windows):
            poly = [(X(a), y_hi), (X(b), y_hi), (X(b), y_lo), (X(a), y_lo)]
            diag.polygon(poly, style=Style(fill="#FBFBFB", stroke=INK, stroke_width=1.0), z=-3)
            k.hatch(poly, angle=45, gap=5, width=0.6)
            nxt = X(windows[i + 1][0]) if i + 1 < len(windows) else last
            for yy in (y_hi, y_lo):
                diag.polyline([(X(b), yy), (nxt, yy)], style=rails_style)
        diag.text("may change", size=11, color="#444444").at(X(sum(windows[0]) / 2), y_hi - 10, anchor="bottom_center")

        # guides at launch and capture edges
        top, bot = base_y["launch"] - H - 24, base_y["capture"] + 14
        k.hidden_line([(X(0), top), (X(0), bot)])
        k.hidden_line([(X(T + SKEW), top), (X(T + SKEW), bot)])
        diag.text("launch edge", size=12).at(X(0), top - 4, anchor="bottom_center")
        diag.text("capture edge", size=12).at(X(T + SKEW), top - 4, anchor="bottom_center")

        # dimensions
        dy = y_lo + 14
        k.dimension((X(0), y_lo + 14), (X(T_MAX), y_lo + 14), f"$t_{{cq}} + t_{{logic,max}} = {T_MAX:.3f}$ ns", offset=20, side=1)
        xe = X(T + SKEW)
        for x0, x1, col in ((xe - T_SU * PX_PER_NS, xe, "#4C8BD0"), (xe, xe + T_H * PX_PER_NS, "#E08A2E")):
            diag.polygon([(x0, top + 20), (x1, top + 20), (x1, bot), (x0, bot)],
                         style=Style(fill=col, stroke="none", stroke_width=0, fill_opacity=0.35), z=-4)
        diag.text("$t_{su}$", size=12).at(xe - 4, bot + 4, anchor="top_right")
        diag.text("$t_h$", size=12).at(xe + T_H * PX_PER_NS + 3, bot + 4, anchor="top_left")

        # equations
        diag.text("Setup:  $T + t_{skew} \\ge t_{cq} + t_{logic,max} + t_{su}$"
                  f"   ({T + SKEW:.2f} $\\ge$ {T_MAX + T_SU:.3f},  slack {SETUP_SLACK:.3f} ns)\n"
                  "Hold:  $t_{cq} + t_{logic,min} \\ge t_h + t_{skew}$"
                  f"   ({T_CQ_MIN:.2f} $\\ge$ {T_H + SKEW:.2f},  margin {HOLD_MARGIN:.2f} ns)\n"
                  "$t_{skew}$ = capture clock arrival minus launch clock arrival; later capture helps setup and hurts hold.",
                  size=12.5).at(X0 - 150, base_y["capture"] + 60, anchor="top_left")
        diag.caption("**Figure 10:** Clock tree skew and the setup / hold check on one flop-to-flop path. "
                     "Schematic with illustrative numbers.", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "10_clock_tree_setup_hold")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
