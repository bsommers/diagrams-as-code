"""A variational autoencoder: encoder, sampled latent, decoder and the two loss terms.

The encoder maps $x$ to the mean and log-variance of a Gaussian over the latent
$z$. Sampling is rewritten as $z = \\mu + \\sigma \\odot \\epsilon$ so gradients flow
through $\\mu$ and $\\sigma$. Training maximises the evidence lower bound: a
reconstruction term plus a KL term that pulls $q_\\phi(z \\mid x)$ towards the prior.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

DATA = Style(font_size=13, fill="#EFE3CF", stroke="#5A4520")
NET = Style(font_size=13, fill="#DCE6F2", stroke="#1F2F57")
DEC = Style(font_size=13, fill="#D9EAD3", stroke="#2E6B2E")
LAT = Style(font_size=13, fill="#F6E3E3", stroke="#8A2F2F")
LOSS = Style(font_size=13, fill="#FFFFFF", stroke="#555555", stroke_width=1.4)
LINE = {"width": 1.3}


def diagram() -> Diagram:
    with Diagram("Variational autoencoder", theme="paper") as diag:
        Y = 220.0
        x = diag.shape("**Input** $x$\n$(B, 3, 64, 64)$", 130, 64, style=DATA).at(80, Y, anchor="center")
        enc = diag.polygon([(0, 0), (170, 40), (170, 120), (0, 160)],
                           "**Encoder** $q_\\phi$\nconv $\\times 4$, stride 2\n$64 \\to 4$ px", style=NET).at(
            250, Y, anchor="center")
        mu = diag.shape("$\\mu$\n$(B, d_z)$", 100, 52, style=LAT).at(480, Y - 60, anchor="center")
        logvar = diag.shape("$\\log \\sigma^2$\n$(B, d_z)$", 100, 52, style=LAT).at(480, Y + 60, anchor="center")
        z = diag.shape("**$z$**\n$(B, d_z)$", 100, 64, style=LAT).at(680, Y, anchor="center")
        eps = diag.shape("$\\epsilon \\sim \\mathrm{N}(0, I)$", 130, 40, style=Style(font_size=13, dash="5,4")).at(
            680, Y + 130, anchor="center")
        dec = diag.polygon([(0, 40), (170, 0), (170, 160), (0, 120)],
                           "**Decoder** $p_\\theta$\ntransposed conv $\\times 4$\n$4 \\to 64$ px", style=DEC).at(
            900, Y, anchor="center")
        xhat = diag.shape("**Output** $x'$\n$(B, 3, 64, 64)$", 130, 64, style=DATA).at(1120, Y, anchor="center")

        x >> diag.edge(**LINE) >> enc
        enc.anchor("right", 0.3) >> diag.edge(corner_radius=6, **LINE) >> mu.anchor("left", 0.5)
        enc.anchor("right", 0.7) >> diag.edge(corner_radius=6, **LINE) >> logvar.anchor("left", 0.5)
        mu.anchor("right", 0.5) >> diag.edge(corner_radius=6, **LINE) >> z.anchor("left", 0.3)
        logvar.anchor("right", 0.5) >> diag.edge(label="$\\sigma = e^{\\log\\sigma^2 / 2}$", corner_radius=6, **LINE
                                                 ) >> z.anchor("left", 0.7)
        eps >> diag.edge(style="dashed", **LINE) >> z
        z >> diag.edge(**LINE) >> dec
        dec >> diag.edge(**LINE) >> xhat

        diag.text("$z = \\mu + \\sigma \\odot \\epsilon$  (reparameterisation)", size=13).at(680, Y - 70, anchor="bottom_center")

        # Losses.
        rec = diag.shape("**Reconstruction**\n$-\\log p_\\theta(x \\mid z) \\approx \\|x - x'\\|^2$", 330, 56,
                         style=LOSS).at(820, 460, anchor="center")
        kl = diag.shape(
            "**KL to prior**\n$D_{KL}(q_\\phi(z \\mid x) \\,\\|\\, \\mathrm{N}(0, I)) = "
            "-\\frac{1}{2} \\sum_j (1 + \\log\\sigma_j^2 - \\mu_j^2 - \\sigma_j^2)$", 470, 70, style=LOSS).at(
            330, 460, anchor="center")
        diag.connect(xhat.anchor("bottom", 0.5), rec.anchor("right", 0.5), style="dashed", corner_radius=8, **LINE)
        diag.connect(logvar.anchor("bottom", 0.5), kl.anchor("top", 0.8), label="$\\mu$, $\\log\\sigma^2$", style="dashed", corner_radius=8, **LINE)
        diag.text("$\\mathrm{ELBO} = \\mathrm{E}_{q_\\phi}[\\log p_\\theta(x \\mid z)] - D_{KL}(q_\\phi(z \\mid x) \\| p(z))$"
                  ",  loss $= -\\mathrm{ELBO}$", size=13).at(580, 530, anchor="top_center")
        diag.caption("**Figure 8:** VAE; the KL term keeps the latent space smooth enough to sample from",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "08_vae_latent_kl")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
