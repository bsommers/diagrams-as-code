"""One iteration of gradient-descent training, with the equation each stage computes.

Five stages in a row, each naming its operation and the equation that governs
it; the quantity handed on labels each arrow, and a feedback line carries the
updated parameters back to the start. Side notes say what stays fixed.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style, distribute
from diagrams_as_code.output import render_all

BLOCK = Style(fill="#ECECEF", font_size=13)
W, H, GAP = 146.0, 70.0, 48.0

# The math subset has no accents, so the prediction is p rather than y-hat.
STAGES = [
    ("Sample batch", "$(x_i, y_i) \\sim D$"),
    ("Forward pass", "$p_i = f_\\theta(x_i)$"),
    ("Loss", "$L = \\sum_i (y_i - p_i)^2$"),
    ("Backward pass", "$g = \\nabla_\\theta L$"),
    ("Optimizer step", "$\\theta \\leftarrow \\theta - \\eta\\,g$"),
]
HANDED_ON = ["$x_i$", "$p_i$", "$L$", "$g$"]


def diagram() -> Diagram:
    with Diagram("Training pipeline", theme="paper") as diag:
        with diag.band(
            "Training iteration $t$",
            notes=[
                "The data set $D$ and the learning rate $\\eta$ are fixed.",
                "Only the parameters $\\theta$ change between iterations.",
                "Stop when $L$ no longer falls.",
            ],
            note_width=170,
        ):
            blocks = [diag.shape(f"**{name}**\n{equation}", W, H, style=BLOCK) for name, equation in STAGES]
            blocks[0].at(70, 100)
            distribute(blocks, "right", gap=GAP)
            for (a, b), carried in zip(zip(blocks, blocks[1:]), HANDED_ON):
                a >> diag.edge(label=carried, width=1.2) >> b

            # Feedback: under the row, from the last stage back to the first.
            left, right = 70 + W / 2, 70 + 4 * (W + GAP) + W / 2
            low = 100 + H + 46
            diag.connect(
                blocks[-1].anchor("bottom", 0.5), blocks[0].anchor("bottom", 0.5), routing="direct",
                via=[(right, low), (left, low)], width=1.2, style="dashed",
            )
            diag.text("updated $\\theta$;  $t \\leftarrow t + 1$", size=12).at(
                (left + right) / 2, low + 6, anchor="top_center")
        diag.caption("**Figure 8:** One iteration of gradient-descent training and the equation of each stage",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "08_pipeline_equations")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
