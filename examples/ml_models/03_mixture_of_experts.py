"""A sparse mixture-of-experts layer with a top-$k$ router.

A linear router scores every token against $N$ experts, keeps the $k$ largest
scores and renormalises them with a softmax. Only those $k$ expert networks run
for the token; their outputs are combined with the gate weights. Parameters grow
with $N$ while the compute per token grows only with $k$.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

DATA = Style(font_size=13, fill="#EFE3CF", stroke="#5A4520")
ROUTER = Style(font_size=13, fill="#DCE6F2", stroke="#1F2F57")
ACTIVE = Style(font_size=13, fill="#D9EAD3", stroke="#2E6B2E", stroke_width=1.8)
IDLE = Style(font_size=13, fill="#F2F2F2", stroke="#999999", dash="5,4", text_color="#777777")
SUM = Style(radius=18, font_size=18)
LINE = {"width": 1.3}

# (expert index, gate weight or None when the router did not pick it)
EXPERTS = [(1, None), (2, 0.62), (3, None), (4, 0.38)]


def diagram() -> Diagram:
    with Diagram("Mixture-of-experts layer", theme="paper") as diag:
        Y = 280.0
        x_in = diag.shape("**Tokens** $x$\n$(T, d_{model})$", 140, 60, style=DATA).at(90, Y, anchor="center")
        router = diag.shape("**Router**\n$z = x W_r$\n$(T, N)$", 130, 80, style=ROUTER).at(310, Y, anchor="center")
        topk = diag.shape(
            "**Top-$k$ + softmax**\n$g = \\mathrm{softmax}(\\mathrm{top}_k(z))$", 190, 70, style=ROUTER
        ).at(540, Y, anchor="center")

        experts = []
        for i, (idx, gate) in enumerate(EXPERTS):
            y = 90 + i * 130
            style = ACTIVE if gate else IDLE
            tag = f"$E_{{{idx}}}$"
            body = "FFN" if gate else "FFN, idle"
            experts.append(
                diag.shape(f"**Expert** {tag}\n{body}\n$d_{{model}} \\to d_{{ff}} \\to d_{{model}}$", 170, 66, style=style)
                .at(800, y, anchor="center")
            )
        diag.text("$\\vdots$", size=20).at(800, 90 + 4 * 130 - 60, anchor="center")
        diag.text("$N = 8$ experts, $k = 2$ active", size=12).at(800, 20, anchor="center")

        total = diag.shape("$\\Sigma$", 38, 38, style=SUM).at(1040, Y, anchor="center")
        out = diag.shape("**Output** $y$\n$(T, d_{model})$", 140, 60, style=DATA).at(1210, Y, anchor="center")

        x_in >> diag.edge(**LINE) >> router
        router >> diag.edge(**LINE) >> topk
        for (idx, gate), e in zip(EXPERTS, experts):
            if gate:
                diag.connect(topk, e, label=f"$g_{idx} = {gate}$", corner_radius=8, **LINE)
                diag.connect(e, total, corner_radius=8, **LINE)
            else:
                diag.connect(topk, e, style="dashed", color="#999999", width=0.9, corner_radius=8)
        total >> diag.edge(**LINE) >> out

        # The token also bypasses the router, as the layer sits inside a residual block.
        diag.text("$y = \\sum_{i \\in \\mathrm{TopK}} g_i\\, E_i(x)$", size=14).at(1040, Y - 70, anchor="bottom_center")
        diag.text("$(T, N)$ scores,\n$k$ non-zero per row", size=12, align="center").at(
            540, Y + 50, anchor="top_center"
        )
        diag.text(
            "Load balance: $L_{aux} = \\alpha N \\sum_{i=1}^{N} f_i P_i$, "
            "$f_i$ = share of tokens sent to $E_i$, $P_i$ = mean router probability",
            size=12,
        ).at(60, 575, anchor="left_center")
        diag.text(
            "Per-expert tokens $T_i \\approx k T / N$, capped at a capacity factor; overflow tokens skip the layer",
            size=12,
        ).at(60, 600, anchor="left_center")
        diag.caption(
            "**Figure 3:** A top-$k$ routed mixture-of-experts layer; unselected experts do no work for the token",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "03_mixture_of_experts")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
