"""A pre-norm decoder-only transformer block with residual connections.

Normalisation comes before each sub-layer, so the residual stream is never
normalised and gradients reach the embeddings unattenuated. The block keeps the
tensor shape $(B, n, d_{model})$ throughout and is stacked $L$ times.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CX = 330.0
SKIP_X = 190.0
NOTE_X = 500.0
LAYER = Style(font_size=13)
NORM = Style(font_size=13, fill="#EDEDED")
SUM = Style(radius=15, font_size=16)
LINE = {"width": 1.2}


def diagram() -> Diagram:
    with Diagram("Pre-norm decoder block", theme="paper") as diag:

        def layer(label: str, y: float, style: Style = LAYER, h: float = 50):
            return diag.shape(label, 230, h, style=style).at(CX, y, anchor="center")

        def note(body: str, y: float, x: float = NOTE_X):
            return diag.text(body, size=12).at(x, y, anchor="left_center")

        def plus(y: float):
            return diag.shape("+", 30, 30, style=SUM).at(CX, y, anchor="center")

        block = diag.shape(
            "", 320, 545, z=-1, obstacle=False, style=Style(fill="#F8F8F8", radius=10, dash="6,4"),
        ).at(CX - 5, 352, anchor="center")

        add2 = plus(110)
        ffn = layer("**SwiGLU feed-forward**\n$W_2(\\mathrm{SiLU}(x W_1) \\odot x W_3)$", 190, h=56)
        norm2 = layer("RMSNorm", 275, NORM, 36)
        add1 = plus(365)
        attn = layer("**Causal self-attention**\nGQA, RoPE on $Q, K$", 450, h=56)
        norm1 = layer("RMSNorm", 535, NORM, 36)
        embed = layer("Token embedding $E$", 650)
        tokens = diag.text("Token ids $(B, n)$", size=13, padding=3).at(CX, 735, anchor="center")
        out = diag.text("to block $l + 1$", size=13, padding=3).at(CX, 35, anchor="center")

        tokens >> diag.edge(**LINE) >> embed.anchor("bottom", 0.5)
        embed.anchor("top", 0.5) >> diag.edge(**LINE) >> norm1.anchor("bottom", 0.5)
        norm1.anchor("top", 0.5) >> diag.edge(**LINE) >> attn.anchor("bottom", 0.5)
        attn.anchor("top", 0.5) >> diag.edge(**LINE) >> add1.anchor("bottom", 0.5)
        add1.anchor("top", 0.5) >> diag.edge(**LINE) >> norm2.anchor("bottom", 0.5)
        norm2.anchor("top", 0.5) >> diag.edge(**LINE) >> ffn.anchor("bottom", 0.5)
        ffn.anchor("top", 0.5) >> diag.edge(**LINE) >> add2.anchor("bottom", 0.5)
        add2.anchor("top", 0.5) >> diag.edge(**LINE) >> out

        # Residual stream: tapped before the norm, added after the sub-layer.
        for tap_y, target, y in ((595, add1, 365), (320, add2, 110)):
            tap = diag.point(CX, tap_y, dot=True)
            diag.connect(tap, target.anchor("left", 0.5), corner_radius=8,
                         via=[(SKIP_X, tap_y), (SKIP_X, y)], **LINE)
        diag.text("$x$", size=13).at(SKIP_X - 10, 470, anchor="right_center")

        diag.bracket("$L \\times$", side="left", font_size=15).spanning(block, block, gap=10)

        note("$(B, n, d_{model})$", 58, CX + 12)
        note("residual stream $x$ carried unchanged", 595, CX + 12)
        note("$x_{l+1} = x' + \\mathrm{FFN}(\\mathrm{RMSNorm}(x'))$", 190)
        note("$d_{model} \\to d_{ff} \\to d_{model}$, $d_{ff} \\approx \\frac{8}{3} d_{model}$", 225)
        note("$x' = x + \\mathrm{Attn}(\\mathrm{RMSNorm}(x))$", 365)
        note("$\\mathrm{softmax}(QK^T / \\sqrt{d_k} + M)\\, V$", 440)
        note("$M_{ij} = -\\infty$ for $j > i$ (causal mask)", 472)
        note("$h_q$ query heads share $h_{kv}$ key/value heads", 504)
        note("$\\mathrm{RMSNorm}(x) = g \\odot x / \\sqrt{\\mathrm{mean}(x^2) + \\epsilon}$", 535)
        note("$E \\in \\mathbf{R}^{|V| \\times d_{model}}$", 650)

        diag.caption(
            "**Figure 1:** Pre-norm decoder block; the residual stream bypasses both sub-layers",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "01_decoder_block")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
