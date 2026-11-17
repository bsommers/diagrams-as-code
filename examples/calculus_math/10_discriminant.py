"""The three cases of the quadratic discriminant.

Three parabolas y = x^2 - 2x + c differ only in c. Their discriminants
b^2 - 4ac are computed, and the roots are drawn only where the discriminant
allows real ones: two crossings, one touching point, or none.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot

NAME = "10_discriminant"
A, B = 1.0, -2.0
CASES = [(-1.0, "#1F2F57"), (1.0, "#2E8B57"), (3.0, "#C0392B")]
SIZE = (210.0, 220.0)


def diagram() -> Diagram:
    with Diagram("Discriminant cases of a quadratic", theme="paper") as diag:
        for i, (c, colour) in enumerate(CASES):
            ox = 60 + i * 290
            disc = B * B - 4 * A * c
            f = lambda x, c=c: A * x * x + B * x + c
            p = Plot(diag, x=(-1.5, 3.5), y=(-2, 6), origin=(ox, 340), size=SIZE)
            p.grid(1, 2)
            p.axes(xstep=1, ystep=2, size=10)
            p.function(f, stroke=colour, width=2.4)
            h = -B / (2 * A)
            p.dot(h, f(h), radius=3.5)
            if disc > 0:
                roots = [(-B - math.sqrt(disc)) / (2 * A), (-B + math.sqrt(disc)) / (2 * A)]
                kind, note = "$b^2 - 4ac > 0$", "two real roots"
            elif disc == 0:
                roots = [-B / (2 * A)]
                kind, note = "$b^2 - 4ac = 0$", "one repeated root"
            else:
                roots, kind, note = [], "$b^2 - 4ac < 0$", "no real roots"
            for r in roots:
                p.dot(r, 0, radius=4.5)
            diag.text(f"**{note.capitalize()}**", size=13, color=colour).at(ox, 340 - SIZE[1] - 58, anchor="left_center")
            diag.text(kind, size=12).at(ox, 340 - SIZE[1] - 36, anchor="left_center")
            diag.text(f"$y = x^2 {B:+g}x {c:+g}$".replace("-", "−"), size=12).at(ox, 382, anchor="left_center")
            diag.text(f"$b^2 - 4ac = {disc:g}$", size=12, color=colour).at(ox, 406, anchor="left_center")
            if roots:
                shown = "$ and $".join(f"{r:.3f}".rstrip("0").rstrip(".").replace("-", "−") for r in roots)
                diag.text(f"$x = {shown}$", size=12).at(ox, 430, anchor="left_center")
            else:
                re, im = -B / (2 * A), math.sqrt(-disc) / (2 * A)
                diag.text(f"$x = {re:g} \\pm {im:.3f}\\,i$".replace(".000", ""), size=12).at(ox, 430, anchor="left_center")
        diag.caption(
            "**Figure 10:** The sign of the discriminant decides whether the parabola crosses the "
            "axis twice, touches it once, or stays clear of it",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/calculus_math") -> Path:
    return render_all(diagram(), output_dir, NAME)["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/calculus_math"))
