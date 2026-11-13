"""A linear program and its feasible region, beside the model-solver-solution chain.

The plot is computed from the model: each constraint line is clipped to the
plot window, the feasible polygon is the window cut by every half-plane, and
the optimum is the vertex of that polygon with the largest objective value.
Dashed level lines of the objective show why that vertex is the last one reached.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

# Constraints a . x <= b with their labels, and the objective c . x to maximise.
CONSTRAINTS = [
    ((1.0, 2.0), 10.0, r"$x_1 + 2x_2 \leq 10$"),
    ((3.0, 2.0), 18.0, r"$3x_1 + 2x_2 \leq 18$"),
    ((1.0, 0.0), 5.0, r"$x_1 \leq 5$"),
]
OBJECTIVE = (1.0, 1.0)
X_MAX, Y_MAX = 7.0, 6.0
ORIGIN, SCALE = (90.0, 340.0), 44.0  # px of the model origin, and px per model unit
LINE = Style(fill="none", stroke="#1F2F57", stroke_width=1.3)
LEVEL = Style(fill="none", stroke="#8A5A00", stroke_width=0.9, dash="5,4")
AXIS = {"routing": "direct", "width": 1.2, "head": "stealth"}


def px(p) -> tuple[float, float]:
    return (ORIGIN[0] + p[0] * SCALE, ORIGIN[1] - p[1] * SCALE)


def value(a, p) -> float:
    return a[0] * p[0] + a[1] * p[1]


def clip(polygon, a, b):
    """The part of a convex ``polygon`` where a . x <= b (Sutherland-Hodgman)."""
    out = []
    for p, q in zip(polygon, polygon[1:] + polygon[:1]):
        fp, fq = value(a, p) - b, value(a, q) - b
        if fp <= 0:
            out.append(p)
        if fp * fq < 0:
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def chord(a, b):
    """The two ends of the line a . x = b inside the plot window, left to right."""
    window = [(0.0, 0.0), (X_MAX, 0.0), (X_MAX, Y_MAX), (0.0, Y_MAX)]
    ends = [p for p in clip(window, a, b) if abs(value(a, p) - b) < 1e-9]
    return sorted(ends)


def diagram() -> Diagram:
    feasible = [(0.0, 0.0), (X_MAX, 0.0), (X_MAX, Y_MAX), (0.0, Y_MAX)]
    for a, b, _ in CONSTRAINTS:
        feasible = clip(feasible, a, b)
    best = max(feasible, key=lambda p: value(OBJECTIVE, p))
    z_best = value(OBJECTIVE, best)

    with Diagram("Feasible region of a linear program", theme="paper") as diag:
        diag.polygon([px(p) for p in feasible], style=Style(fill="#DCE6F2", stroke="none"), z=-1)
        ticks = [f"M {px((i, 0))[0]} {ORIGIN[1]} v 4" for i in range(1, int(X_MAX) + 1)]
        ticks += [f"M {ORIGIN[0]} {px((0, i))[1]} h -4" for i in range(1, int(Y_MAX) + 1)]
        diag.path(" ".join(ticks), style=Style(fill="none", stroke_width=0.9))

        # Level lines of the objective, the last one through the optimum.
        for z in (2.0, 4.0, z_best):
            low, high = chord(OBJECTIVE, z)
            diag.polyline([px(low), px(high)], style=LEVEL)
            name = "z^*" if z == z_best else "z"
            end = px(high)
            diag.text(f"${name} = {z:g}$", size=11, color="#8A5A00").at(end[0], end[1] + 9, anchor="top_center")
        for (a, b, label), anchor, dx, dy in zip(
            CONSTRAINTS, ("left_center", "bottom_center", "bottom_center"), (6, 0, 0), (0, -6, -6)
        ):
            low, high = chord(a, b)
            diag.polyline([px(low), px(high)], style=LINE)
            # The label goes at the end of the line that is away from the axes.
            end = px(high) if anchor == "left_center" else px(min(low, high, key=lambda p: -p[1]))
            diag.text(label, size=12).at(end[0] + dx, end[1] + dy, anchor=anchor)

        diag.connect(ORIGIN, px((X_MAX + 0.45, 0)), **AXIS)
        diag.connect(ORIGIN, px((0, Y_MAX + 0.45)), **AXIS)
        diag.text("$x_1$", size=14).at(*px((X_MAX + 0.6, 0)), anchor="left_center")
        diag.text("$x_2$", size=14).at(*px((0, Y_MAX + 0.6)), anchor="bottom_center")

        # The objective direction, drawn from one level line to the next.
        diag.connect(px((1, 1)), px((2, 2)), routing="direct", width=1.6, color="#8A5A00")
        diag.text("$c$", size=14, color="#8A5A00").at(*px((1.38, 1.62)), anchor="bottom_right")

        optimum = diag.point(*px(best), dot=True, radius=3.5)
        above = px((best[0], best[1] + 2.0))
        note = diag.leader("optimum $x^*$", optimum, at=above, anchor="center", size=12)

        model = diag.shape("**Model**\n$\\max\\; z = x_1 + x_2$\n$A x \\leq b,\\; x \\geq 0$", 150, 66).at(550, 282)
        solver = diag.shape("**Solver**\nsimplex method", 150, 50).at(550, 182)
        x, y = (f"{v:g}" for v in best)
        solution = diag.shape(f"**Solution**\n$x^* = ({x}, {y}),\\; z^* = {z_best:g}$", 150, 50)
        solution.at(550, above[1], anchor="left_center")
        model >> diag.edge(width=1.2) >> solver
        solver >> diag.edge(width=1.2) >> solution
        # The model defines the shaded region; the solution is its best vertex.
        inside = px((4.5, 0.57))
        diag.connect(model.anchor("left", 0.5), inside, routing="direct", width=0.9, style="dashed",
                     label="feasible set")
        diag.connect(solution, note, routing="direct", width=0.9, style="dashed")

        diag.caption(
            "**Figure 11:** A linear program: its feasible region, level lines of the objective, "
            "and the optimum the solver returns",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "11_constraint_region")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
