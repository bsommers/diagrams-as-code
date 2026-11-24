"""Multi-head scaled dot-product attention, with tensor shapes on every arrow.

The input is projected into queries, keys and values, split into $h$ heads of
width $d_k = d_{model} / h$, and each head computes
$\\mathrm{softmax}(QK^T / \\sqrt{d_k})\\,V$. The heads are concatenated and mixed
by an output projection.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style

from diagrams_as_code.output import render_all

PROJ = Style(font_size=13, fill="#DCE6F2", stroke="#1F2F57")
OP = Style(font_size=13)
DATA = Style(font_size=13, fill="#EFE3CF", stroke="#5A4520")
LINE = {"width": 1.2}
SHAPE = {"size": 12}

# The attention weights of one head: a row-stochastic matrix, darker is larger.
WEIGHTS = [
    ["#2F5799", "#C9D3E6", "#E9EDF5", "#E9EDF5"],
    ["#7F99C4", "#2F5799", "#E9EDF5", "#C9D3E6"],
    ["#C9D3E6", "#7F99C4", "#2F5799", "#E9EDF5"],
    ["#7F99C4", "#C9D3E6", "#7F99C4", "#2F5799"],
]

def diagram() -> Diagram:
    with Diagram("Multi-head scaled dot-product attention", theme="paper") as diag:
        Y = 250.0

        def box(label: str, x: float, y: float, w: float = 130, h: float = 56, style: Style = OP):
            return diag.shape(label, w, h, style=style).at(x, y, anchor="center")

        def note(body: str, x: float, y: float, anchor: str = "top_center"):
            return diag.text(body, align="center", **SHAPE).at(x, y, anchor=anchor)

        x_in = box("**Input** $X$\n$(B, n, d_{model})$", 90, Y, 140, 60, DATA)
        q = box("$Q = X W^Q$\n$(B, h, n, d_k)$", 290, 130, style=PROJ)
        k = box("$K = X W^K$\n$(B, h, n, d_k)$", 290, Y, style=PROJ)
        v = box("$V = X W^V$\n$(B, h, n, d_k)$", 290, 500, style=PROJ)
        diag.fan_out(x_in, [q, k, v], trunk=40, **LINE)

        score = box("**MatMul**\n$S = QK^T$", 500, Y)
        scale = box("**Scale**\n$S / \\sqrt{d_k}$", 650, Y, 120)
        mask = box("**Mask**\n$S + M$ (optional)", 800, Y, 130)
        soft = box("**Softmax**\n$\\mathrm{softmax}_j$", 950, Y, 120)
        wv = box("**MatMul**\n$A V$", 1110, Y, 110)
        cat = box("**Concat** heads\n$(B, n, h \\cdot d_k)$", 1290, Y, 150)
        wo = box("**Linear** $W^O$\n$(d_{model}, d_{model})$", 1290, 370, 150, style=PROJ)
        out = box("**Output**\n$(B, n, d_{model})$", 1290, 490, 150, 60, DATA)

        q.anchor("right", 0.5) >> diag.edge(corner_radius=8, **LINE) >> score.anchor("top", 0.5)
        k >> diag.edge(**LINE) >> score
        score >> diag.edge(**LINE) >> scale
        scale >> diag.edge(**LINE) >> mask
        mask >> diag.edge(**LINE) >> soft
        soft >> diag.edge(**LINE) >> wv
        v.anchor("right", 0.5) >> diag.edge(corner_radius=8, via=[(1110, 500)], **LINE) >> wv.anchor("bottom", 0.5)
        wv >> diag.edge(**LINE) >> cat
        cat >> diag.edge(**LINE) >> wo
        wo >> diag.edge(**LINE) >> out

        note("$(B, h, n, n)$", 575, Y - 36, "bottom_center")
        note("one score per\nquery-key pair", 650, Y + 45)
        note("$M_{ij} = -\\infty$, $j > i$", 810, Y + 45)

        # The weights of one head, drawn as a heat map under the softmax.
        cell = 22
        gx, gy = 950 - 2 * cell, 325
        for r, row in enumerate(WEIGHTS):
            for c, colour in enumerate(row):
                diag.shape("", cell, cell, style=Style(fill=colour, stroke="#FFFFFF", stroke_width=1)).at(
                    gx + c * cell, gy + r * cell
                )
        note("$A$: $(n, n)$ per head,\nrows sum to 1", 950, gy + 4 * cell + 6)

        # Every head runs the same computation on its own slice of $d_{model}$.
        diag.text(
            "$\\mathrm{head}_i = \\mathrm{softmax}\\!\\left(Q_i K_i^T / \\sqrt{d_k}\\right) V_i$,  "
            "$\\mathrm{MHA}(X) = \\mathrm{Concat}(\\mathrm{head}_1, \\ldots, \\mathrm{head}_h)\\, W^O$,  "
            "$d_k = d_{model} / h$",
            size=13,
        ).at(60, 40, anchor="top_left")
        diag.caption(
            "**Figure 2:** Multi-head attention; each head attends over all $n$ positions in a $d_k$-wide subspace",
            small_caps=True,
        )
    return diag

def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "02_multi_head_attention")["svg"]

if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
