"""Diffusion: a fixed forward noising chain and a learned reverse chain.

The forward process adds Gaussian noise until $x_T$ is pure noise; it has a
closed form, so training picks a random $t$ and regresses the noise. The reverse
process removes noise one step at a time, using a U-Net $\\epsilon_\\theta(x_t, t)$
whose encoder halves the resolution, whose decoder restores it, and whose skip
connections carry fine detail across.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

LINE = {"width": 1.3}
SKIP = {"width": 1.0, "style": "dashed", "color": "#5A7DB4"}
DOWN = Style(font_size=12, fill="#DCE6F2", stroke="#1F2F57")
UP = Style(font_size=12, fill="#D9EAD3", stroke="#2E6B2E")
MID = Style(font_size=12, fill="#EFE3CF", stroke="#5A4520")
NOISE = ["#FFFFFF", "#ECECEC", "#CFCFCF", "#9A9A9A"]


def diagram() -> Diagram:
    with Diagram("Diffusion forward and reverse process", theme="paper") as diag:
        xs = [140, 400, 660, 920]
        labels = ["$x_0$\ndata", "$x_1$", "$x_t$", "$x_T \\approx \\mathrm{N}(0, I)$"]

        def chain(y: float, order, tag: str):
            nodes = []
            for x, lab, fill in zip(xs, labels, NOISE):
                nodes.append(diag.shape(lab, 150, 54, style=Style(font_size=13, fill=fill)).at(x, y, anchor="center"))
            seq = nodes if order == 1 else nodes[::-1]
            for a, b in zip(seq, seq[1:]):
                a >> diag.edge(**LINE) >> b
            return nodes

        # Forward process, left to right.
        fwd = chain(60, 1, "q")
        diag.text("**Forward** $q(x_t \\mid x_{t-1}) = \\mathrm{N}(\\sqrt{1 - \\beta_t}\\, x_{t-1},\\, \\beta_t I)$",
                  size=13).at(60, 8, anchor="left_center")
        diag.text("$x_t = \\sqrt{\\bar\\alpha_t}\\, x_0 + \\sqrt{1 - \\bar\\alpha_t}\\, \\epsilon$,  "
                  "$\\epsilon \\sim \\mathrm{N}(0, I)$", size=12).at(530, 108, anchor="top_center")

        # The U-Net.
        diag.shape("", 1010, 300, z=-1, obstacle=False,
                   style=Style(fill="#F8F8F8", radius=10, dash="6,4")).at(530, 330, anchor="center")
        diag.text("**U-Net** $\\epsilon_\\theta(x_t, t)$", size=14).at(50, 195, anchor="left_center")

        enc_x, dec_x, ys = [160, 280, 400], [660, 790, 920], [235, 305, 375]
        sizes = ["$(B, 128, 64, 64)$", "$(B, 256, 32, 32)$", "$(B, 512, 16, 16)$"]
        enc = [diag.shape(f"**Down {i + 1}**\n{s}", 120, 46, style=DOWN).at(x, y, anchor="center")
               for i, (x, y, s) in enumerate(zip(enc_x, ys, sizes))]
        dec = [diag.shape(f"**Up {i + 1}**\n{sz}", 120, 46, style=UP).at(dec_x[2 - i], ys[i], anchor="center")
               for i, sz in enumerate(sizes)]
        bott = diag.shape("**Bottleneck**\n$(B, 1024, 8, 8)$", 130, 46, style=MID).at(530, 440, anchor="center")

        for a, b in zip(enc, enc[1:]):
            a.anchor("bottom", 0.5) >> diag.edge(corner_radius=6, **LINE) >> b.anchor("left", 0.5)
        enc[2].anchor("bottom", 0.5) >> diag.edge(corner_radius=6, **LINE) >> bott.anchor("left", 0.5)
        bott.anchor("right", 0.5) >> diag.edge(corner_radius=6, **LINE) >> dec[2].anchor("bottom", 0.5)
        dec[2].anchor("right", 0.5) >> diag.edge(corner_radius=6, **LINE) >> dec[1].anchor("bottom", 0.5)
        dec[1].anchor("right", 0.5) >> diag.edge(corner_radius=6, **LINE) >> dec[0].anchor("bottom", 0.5)
        for e, d in zip(enc, dec):
            e.anchor("right", 0.5) >> diag.edge(**SKIP) >> d.anchor("left", 0.5)
        diag.text("skip connections: concatenate encoder features", size=11, color="#5A7DB4").at(
            530, 285, anchor="center")

        diag.text("input $x_t$, $t$\n$(B, 3, 64, 64)$", size=12, align="center").at(
            60, 250, anchor="top_center")
        diag.connect(diag.point(60, 235), enc[0].anchor("left", 0.5), routing="direct", arrow_head=True, width=1.3)
        diag.text("**$t$ embedding:** sinusoidal + MLP,\nadded in every block", size=12, align="center").at(
            160, 440, anchor="center")
        pred = diag.text("predicted noise\n$(B, 3, 64, 64)$", size=12, align="center").at(
            1010, 235, anchor="left_center")
        diag.connect(dec[0].anchor("right", 0.5), diag.point(1005, 235), routing="direct", **LINE)

        diag.text("**Training loss** $L = \\mathrm{E}_{t, x_0, \\epsilon}\\,\\|\\epsilon - \\epsilon_\\theta(x_t, t)\\|^2$",
                  size=13).at(330, 195, anchor="left_center")

        # Reverse process, right to left, calling the U-Net at each step.
        rev = chain(590, -1, "p")
        diag.text("**Reverse** $x_{t-1} = \\frac{1}{\\sqrt{\\alpha_t}}\\left(x_t - \\frac{\\beta_t}{\\sqrt{1 - \\bar\\alpha_t}}\\,"
                  "\\epsilon_\\theta(x_t, t)\\right) + \\sigma_t z$", size=13).at(60, 535, anchor="left_center")
        diag.connect(rev[2].anchor("top", 0.5), diag.point(660, 480), routing="direct", style="dashed", width=1.0)
        diag.caption("**Figure 4:** Forward noising, the denoising U-Net and ancestral sampling", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "04_diffusion_unet")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
