"""LoRA at the weight level: a frozen matrix plus a trainable low-rank update.

The pretrained weight $W_0 \\in \\mathbf{R}^{d \\times k}$ is never changed. Its
update is factored as $\\Delta W = B A$ with rank $r \\ll \\min(d, k)$, so only
$r(d + k)$ numbers are trained. $B$ starts at zero, so training begins exactly
at the pretrained model. Box proportions follow the matrix shapes.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

FROZEN = Style(font_size=13, fill="#E4E4E4", stroke="#777777", dash="5,4")
TRAIN = Style(font_size=12, fill="#D9EAD3", stroke="#2E6B2E", stroke_width=1.8)
DATA = Style(font_size=13, fill="#EFE3CF", stroke="#5A4520")
OP = Style(font_size=13, fill="#FFFFFF")
LINE = {"width": 1.3}


def diagram() -> Diagram:
    with Diagram("LoRA low-rank weight update", theme="paper") as diag:
        out = diag.shape("**Output** $h$\n$(B, n, d)$", 150, 54, style=DATA).at(400, 40, anchor="center")
        add = diag.shape("+", 34, 34, style=Style(radius=17, font_size=18)).at(400, 130, anchor="center")
        w0 = diag.shape("**Pretrained** $W_0$\n$d \\times k$\n**frozen**", 220, 170, style=FROZEN).at(
            230, 330, anchor="center")
        scale = diag.shape("$\\times\\, \\alpha / r$", 90, 30, style=OP).at(590, 190, anchor="center")
        b = diag.shape("$B$\n$d \\times r$", 70, 170, style=TRAIN).at(590, 330, anchor="center")
        a = diag.shape("**$A$**  $r \\times k$,  trainable", 220, 34, style=TRAIN).at(590, 480, anchor="center")
        x = diag.shape("**Input** $x$\n$(B, n, k)$", 150, 54, style=DATA).at(400, 590, anchor="center")

        x.anchor("left", 0.5) >> diag.edge(corner_radius=8, **LINE) >> w0.anchor("bottom", 0.5)
        x.anchor("right", 0.5) >> diag.edge(corner_radius=8, **LINE) >> a.anchor("bottom", 0.5)
        a >> diag.edge(**LINE) >> b.anchor("bottom", 0.5)
        b >> diag.edge(**LINE) >> scale
        w0.anchor("top", 0.5) >> diag.edge(corner_radius=8, **LINE) >> add.anchor("left", 0.5)
        scale.anchor("top", 0.5) >> diag.edge(corner_radius=8, **LINE) >> add.anchor("right", 0.5)
        add >> diag.edge(**LINE) >> out

        diag.text("$(B, n, r)$", size=12).at(600, 440, anchor="left_center")
        diag.text("$W_0 x$", size=12).at(235, 205, anchor="left_center")
        diag.text("**Forward pass**\n$h = W_0 x + \\frac{\\alpha}{r}\\, B A x$", size=14, align="left").at(
            760, 110, anchor="left_center")
        diag.text(
            "**Initialisation**\n$A \\sim \\mathrm{N}(0, \\sigma^2)$, $B = 0$\nso $\\Delta W = 0$ at step 0",
            size=13, align="left").at(760, 235, anchor="left_center")
        diag.text(
            "**Trainable parameters**\nfull: $d \\cdot k = 4096^2 \\approx 16.8$ M\n"
            "LoRA: $r(d + k) = 8 \\cdot 8192 = 65{,}536$\n$\\approx 0.39\\%$ of the full matrix",
            size=13, align="left").at(760, 360, anchor="left_center")
        diag.text(
            "**After training**\nmerge: $W = W_0 + \\frac{\\alpha}{r} B A$\nno extra inference latency",
            size=13, align="left").at(760, 495, anchor="left_center")
        diag.caption("**Figure 9:** LoRA freezes $W_0$ and learns a rank-$r$ update; box sizes follow the matrix shapes",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "09_lora_weight_update")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
