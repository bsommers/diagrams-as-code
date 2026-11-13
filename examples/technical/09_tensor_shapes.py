"""Tensor shapes through a small convolutional network.

Each feature map is a cuboid in oblique projection: its thickness along the
row is the channel count, its front-to-back depth the width and its height the
height. Two strided convolutions halve the spatial size while the channels
grow; the last map is flattened into a vector and reduced to ten class scores.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.solids import oblique

ANGLE, DEPTH_SCALE = 45.0, 0.5
KX = DEPTH_SCALE * math.cos(math.radians(ANGLE))  # screen shift per unit of depth
KY = DEPTH_SCALE * math.sin(math.radians(ANGLE))
MID_Y, SHAPE_Y, GAP = 150.0, 262.0, 118.0
MAP = Style(fill="#DCE6F2", stroke="#1F2F57")
VECTOR = Style(fill="#EFE3CF", stroke="#5A4520")
DIM = {"routing": "direct", "width": 0.75, "head": "bar", "tail": "bar", "two_way": True, "arrow_size": 0.8}

# (thickness, height, depth) in px, the shape under it, and the operation that leads to the next one.
# Feature maps: 2 px per pixel and per channel (the 3-channel input is drawn 12 px thick to stay visible).
STAGES = [
    ((12, 128, 128), r"$3 \times 64 \times 64$", "conv $3 \\times 3$\nstride 2", MAP),
    ((32, 64, 64), r"$16 \times 32 \times 32$", "conv $3 \\times 3$\nstride 2", MAP),
    ((64, 32, 32), r"$32 \times 16 \times 16$", "flatten", MAP),
    ((10, 150, 10), r"$8192$", "linear", VECTOR),
    ((10, 44, 10), r"$10$", "", VECTOR),
]


def diagram() -> Diagram:
    with Diagram("Tensor shapes through a small CNN", theme="paper") as diag:
        left, solids, labels = 110.0, [], []
        for (w, h, d), shape, _, style in STAGES:
            extent = w + d * KX
            solid = diag.cuboid("", w, h, d, projection=oblique(ANGLE, DEPTH_SCALE), style=style)
            solid.at(left + extent / 2, MID_Y, anchor="center")
            labels.append(diag.text(shape, size=13).at(left + extent / 2, SHAPE_Y, anchor="top_center"))
            solids.append((solid, left, extent))
            left += extent + GAP

        for ((a, a_left, a_extent), (b, b_left, _)), (_, _, operation, _) in zip(zip(solids, solids[1:]), STAGES):
            start, end = (a_left + a_extent + 10, MID_Y), (b_left - 10, MID_Y)
            diag.connect(start, end, routing="direct", width=1.2)
            diag.text(operation, size=11, align="center").at((start[0] + end[0]) / 2, MID_Y - 8, anchor="bottom_center")

        # Dimension lines on the input: its front face is drawn true, the depth recedes at 45 degrees.
        (w, h, d), (cube, x0, _) = STAGES[0][0], solids[0]
        bottom = MID_Y + (h + d * KY) / 2
        top = bottom - h
        diag.connect((x0 - 14, top), (x0 - 14, bottom), **DIM)
        diag.text("$H$", size=13).at(x0 - 22, (top + bottom) / 2, anchor="right_center")
        diag.connect((x0, bottom + 12), (x0 + w, bottom + 12), **DIM)
        diag.text("$C$", size=13).at(x0 + w + 8, bottom + 12, anchor="left_center")
        # The depth line runs 10 px off the receding edge, through the empty corner of the
        # cuboid's bounding box, so its ends and its letter are nested in the cuboid.
        off = 10 / math.sqrt(2)
        near = diag.point(0, 0).inside(cube, "top_left", -off, d * KY - off)
        far = diag.point(0, 0).inside(cube, "top_left", d * KX - off, -off)
        diag.connect(near, far, **DIM)
        diag.text("$W$", size=13).inside(cube, "top_left", d * KX / 2 - off - 18, d * KY / 2 - off - 20)

        maps = diag.bracket("feature maps, $C \\times H \\times W$", side="bottom", shape="square", depth=6)
        maps.spanning(labels[0], labels[2], gap=8)
        vectors = diag.bracket("vectors", side="bottom", shape="square", depth=6)
        vectors.spanning(labels[3], labels[4], gap=8)
        diag.caption(
            "**Figure 9:** Tensor shapes through a small convolutional network; "
            "the spatial size halves as the channels grow",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "09_tensor_shapes")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
