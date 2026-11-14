"""One transformer encoder block, drawn bottom to top as in the original paper.

Token embeddings plus a positional encoding enter a block of two sub-layers,
multi-head self-attention and a position-wise feed-forward network. Each
sub-layer is wrapped by a residual connection and layer normalisation; the
block is repeated $N$ times and keeps the tensor shape $(B, n, d)$ throughout.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX = 330.0  # the axis the data flows up
SKIP_X = 195.0  # the residual connections run up this line
NOTE_X = 485.0
LAYER = Style(font_size=13)
NORM = Style(font_size=13, fill="#EDEDED")
LINE = {"width": 1.2}
NOTE = {"size": 12}


def diagram() -> Diagram:
    with Diagram("Transformer encoder block", theme="paper") as diag:

        def layer(label: str, y: float, style: Style = LAYER, height: float = 50):
            return diag.shape(label, 210, height, style=style).at(CX, y, anchor="center")

        def note(body: str, y: float, x: float = NOTE_X):
            return diag.text(body, **NOTE).at(x, y, anchor="left_center")

        # The repeated block: a backdrop the lines may cross.
        block = diag.shape(
            "", 300, 420, z=-1, obstacle=False, style=Style(fill="#F8F8F8", radius=10, dash="6,4"),
        ).at(CX - 15, 290, anchor="center")

        norm2 = layer("Add & Norm", 125, NORM, 40)
        ffn = layer("**Feed-Forward**\n$\\mathrm{ReLU}(x W_1 + b_1) W_2 + b_2$", 205)
        norm1 = layer("Add & Norm", 315, NORM, 40)
        attention = layer("**Multi-Head Self-Attention**\n$Q = K = V = x$", 395)
        add = diag.shape("+", 30, 30, style=Style(radius=15, font_size=16)).at(CX, 555, anchor="center")
        embed = layer("Input Embedding", 640)
        encoding = diag.shape("Positional\nEncoding", 110, 50, style=LAYER).at(SKIP_X - 35, 555, anchor="center")
        tokens = diag.text("Tokens $(B, n)$", size=13, padding=3).at(CX, 720, anchor="center")
        out = diag.text("to block $l + 1$", size=13, padding=3).at(CX, 35, anchor="center")

        # The data path, bottom to top.
        tokens >> diag.edge(**LINE) >> embed.anchor("bottom", 0.5)
        embed.anchor("top", 0.5) >> diag.edge(**LINE) >> add.anchor("bottom", 0.5)
        encoding.anchor("right", 0.5) >> diag.edge(**LINE) >> add.anchor("left", 0.5)
        add.anchor("top", 0.5) >> diag.edge(**LINE) >> attention.anchor("bottom", 0.5)
        attention.anchor("top", 0.5) >> diag.edge(**LINE) >> norm1.anchor("bottom", 0.5)
        norm1.anchor("top", 0.5) >> diag.edge(**LINE) >> ffn.anchor("bottom", 0.5)
        ffn.anchor("top", 0.5) >> diag.edge(**LINE) >> norm2.anchor("bottom", 0.5)
        norm2.anchor("top", 0.5) >> diag.edge(**LINE) >> out

        # Residual connections: tapped below each sub-layer, routed round it.
        for tap_y, target, y in ((455, norm1, 315), (265, norm2, 125)):
            tap = diag.point(CX, tap_y, dot=True)
            diag.connect(
                tap, target.anchor("left", 0.5), corner_radius=8,
                via=[(SKIP_X, tap_y), (SKIP_X, y)], **LINE,
            )

        diag.bracket("$N \\times$", side="left", font_size=15).spanning(block, block, gap=10)

        # Tensor shapes: two beside the line they describe, the rest beside their layer.
        note("$(B, n, d_{\\mathrm{model}})$", 60, CX + 12)
        note("$d_{\\mathrm{model}} \\to d_{\\mathrm{ff}} \\to d_{\\mathrm{model}}$", 205)
        note("$\\mathrm{LayerNorm}(x + \\mathrm{Sublayer}(x))$", 315)
        note("$h$ heads, $d_k = d_{\\mathrm{model}} / h$", 395)
        note("$x \\in \\mathbf{R}^{B \\times n \\times d_{\\mathrm{model}}}$", 522, CX + 12)
        note("lookup in $E \\in \\mathbf{R}^{|V| \\times d_{\\mathrm{model}}}$", 640)

        diag.caption(
            "**Figure 3:** A transformer encoder block; residual connections bypass both sub-layers",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "03_transformer_block")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
