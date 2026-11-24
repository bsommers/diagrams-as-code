"""A convolutional backbone and its feature pyramid network.

The backbone halves the resolution at each stage (stride 2) while the channels
double. The pyramid taps stages $C_2$ to $C_5$ with $1 \\times 1$ lateral
convolutions, adds in the upsampled coarser level on the way down and smooths
the sum with a $3 \\times 3$ convolution, giving 256 channels at every scale.
Cuboid sizes are schematic: thickness is channels, height is spatial size.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.solids import oblique

PROJ = oblique(45, 0.5)
MAP = Style(fill="#DCE6F2", stroke="#1F2F57")
IMG = Style(fill="#EFE3CF", stroke="#5A4520")
PYR = Style(font_size=12, fill="#D9EAD3", stroke="#2E6B2E")
HEAD = Style(font_size=12, fill="#F2F2F2")
LINE = {"width": 1.3}
Y_BACK = 400.0
Y_PYR = 190.0
DEPTH = 30.0

# name, x, (thickness, height), shape, stride
STAGES = [
    ("$C_2$", 320, (14, 120), "$256 \\times 128 \\times 128$", 4),
    ("$C_3$", 510, (22, 90), "$512 \\times 64 \\times 64$", 8),
    ("$C_4$", 700, (30, 66), "$1024 \\times 32 \\times 32$", 16),
    ("$C_5$", 890, (38, 46), "$2048 \\times 16 \\times 16$", 32),
]
PYR_SHAPES = ["$256 \\times 128 \\times 128$", "$256 \\times 64 \\times 64$", "$256 \\times 32 \\times 32$",
              "$256 \\times 16 \\times 16$"]


def diagram() -> Diagram:
    with Diagram("CNN backbone with feature pyramid", theme="paper") as diag:
        img = diag.cuboid("", 8, 150, DEPTH, projection=PROJ, style=IMG).at(90, Y_BACK, anchor="center")
        diag.text("**Image**\n$3 \\times 512 \\times 512$", size=12, align="center").at(90, Y_BACK + 110, anchor="top_center")
        prev = (90 + (8 + 10) / 2 + 8)
        ops = ["conv $7 \\times 7$, s2\nmax-pool $3 \\times 3$, s2\n+ res. stage", "res. stage\nstride 2", "res. stage\nstride 2",
               "res. stage\nstride 2"]
        backbone, pyramid = [], []
        for (name, x, (t, h), shape, stride), op in zip(STAGES, ops):
            c = diag.cuboid("", t, h, DEPTH, projection=PROJ, style=MAP).at(x, Y_BACK, anchor="center")
            backbone.append(c)
            left = x - (t + 10) / 2 - 8
            diag.connect((prev, Y_BACK), (left, Y_BACK), routing="direct", **LINE)
            diag.text(op, size=11, align="center").at((prev + left) / 2, Y_BACK - 12, anchor="bottom_center")
            prev = x + (t + 10) / 2 + 8
            diag.text(f"**{name}**  stride {stride}\n{shape}", size=12, align="center").at(
                x, Y_BACK + 110, anchor="top_center")

        for i, (name, x, _, _, stride) in enumerate(STAGES):
            p = diag.shape(f"**$P_{i + 2}$**\n{PYR_SHAPES[i]}", 130, 50, style=PYR).at(x, Y_PYR, anchor="center")
            pyramid.append(p)
        for i, ((_, x, (t, h), _, _), p) in enumerate(zip(STAGES, pyramid)):
            diag.connect(diag.point(x, Y_BACK - h / 2 - 10), p.anchor("bottom", 0.5), routing="direct",
                         label="$1 \\times 1$ conv, 256", **LINE)
        for i in range(3, 0, -1):
            pyramid[i].anchor("left", 0.5) >> diag.edge(**LINE) >> pyramid[i - 1].anchor("right", 0.5)
        for i in range(3, 0, -1):
            mid = (STAGES[i][1] + STAGES[i - 1][1]) / 2
            diag.text("$\\times 2$ up\n+ add", size=11, align="center").at(mid, Y_PYR - 32, anchor="bottom_center")

        heads = diag.shape("**Shared head** (per level)\n$3 \\times 3$ conv, then class and box outputs", 740, 40,
                           style=HEAD).at(605, 60, anchor="center")
        for (_, x, *_), p in zip(STAGES, pyramid):
            p.anchor("top", 0.5) >> diag.edge(label="$3 \\times 3$ conv", **LINE) >> heads.anchor(
                "bottom", (x - 235) / 740)
        diag.text("**Backbone** (bottom-up)", size=13).at(110, Y_BACK - 130, anchor="center")
        diag.text("**Top-down pathway**", size=13).at(80, Y_PYR, anchor="center")
        diag.caption("**Figure 7:** A strided backbone and a feature pyramid; spatial size halves as channels grow",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "07_cnn_feature_pyramid")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
