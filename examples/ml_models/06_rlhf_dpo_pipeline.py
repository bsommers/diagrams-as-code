"""Preference tuning two ways: RLHF with a reward model, and DPO without one.

Both start from a supervised fine-tuned model and a dataset of preference pairs
$(x, y_w, y_l)$. RLHF fits a reward model with the Bradley-Terry loss and then
optimises the policy with PPO under a KL penalty to a frozen reference. DPO
folds the reward into the policy's log-ratios and trains on the pairs directly.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

DATA = Style(font_size=13, fill="#EFE3CF", stroke="#5A4520")
MODEL = Style(font_size=13, fill="#DCE6F2", stroke="#1F2F57")
FROZEN = Style(font_size=13, fill="#F2F2F2", stroke="#777777", dash="5,4")
LOSS = Style(font_size=12, fill="#FFFFFF", stroke="#2E6B2E", stroke_width=1.6)
OUT = Style(font_size=13, fill="#D9EAD3", stroke="#2E6B2E", stroke_width=1.8)
LINE = {"width": 1.3}


def diagram() -> Diagram:
    with Diagram("RLHF and DPO preference-tuning pipelines", theme="paper") as diag:
        for y, name in ((135, "RLHF: reward model, then PPO"), (465, "DPO: direct preference optimisation")):
            diag.shape("", 780, 215, z=-1, obstacle=False,
                       style=Style(fill="#F8F8F8", radius=10, dash="6,4")).at(880, y, anchor="center")
            diag.text(f"**{name}**", size=14).at(510, y - 92, anchor="left_center")

        base = diag.shape("**Base LM**\npre-trained\n$(B, n) \\to (B, n, |V|)$", 140, 76, style=MODEL).at(
            70, 300, anchor="center")
        sft = diag.shape("**SFT model**\n$\\pi_{SFT}$\ninstruction data", 130, 76, style=MODEL).at(
            275, 300, anchor="center")
        prefs = diag.shape(
            "**Preference pairs**\n$(x, y_w, y_l)$\nsampled completions,\n$y_w \\succ y_l$ by human or AI label", 200, 96, style=DATA).at(
            500, 300, anchor="center")
        ref = diag.shape("**Reference** $\\pi_{ref}$\nfrozen copy of $\\pi_{SFT}$", 190, 60, style=FROZEN).at(
            880, 300, anchor="center")

        rm = diag.shape("**Reward model** $r_\\phi(x, y)$\nscalar head, $(B, n) \\to (B, 1)$", 210, 70,
                        style=MODEL).at(660, 135, anchor="center")
        ppo = diag.shape("**PPO** on $\\pi_\\theta$\nreward $r_\\phi - \\beta\\,\\mathrm{KL}(\\pi_\\theta \\| \\pi_{ref})$",
                         250, 70, style=MODEL).at(1000, 135, anchor="center")
        rm_loss = diag.shape("$L_{RM} = -\\log \\sigma(r_\\phi(x, y_w) - r_\\phi(x, y_l))$", 270, 36, style=LOSS).at(
            660, 195, anchor="center")
        dpo = diag.shape("**DPO step** on $\\pi_\\theta$\nno reward model, no sampling", 230, 70,
                         style=MODEL).at(760, 440, anchor="center")
        dpo_loss = diag.shape(
            "$L_{DPO} = -\\log \\sigma\\left(\\beta \\log \\frac{\\pi_\\theta(y_w \\mid x)}{\\pi_{ref}(y_w \\mid x)}"
            " - \\beta \\log \\frac{\\pi_\\theta(y_l \\mid x)}{\\pi_{ref}(y_l \\mid x)}\\right)$",
            470, 60, style=LOSS).at(770, 530, anchor="center")
        out = diag.shape("**Aligned policy**\n$\\pi_\\theta$\n$(B, n, |V|)$", 140, 76, style=OUT).at(
            1330, 300, anchor="center")

        base >> diag.edge(**LINE) >> sft
        sft >> diag.edge(**LINE) >> prefs
        prefs.anchor("top", 0.5) >> diag.edge(corner_radius=8, **LINE) >> rm.anchor("left", 0.5)
        prefs.anchor("bottom", 0.5) >> diag.edge(corner_radius=8, **LINE) >> dpo.anchor("left", 0.5)
        rm >> diag.edge("reward", **LINE) >> ppo
        ref.anchor("top", 0.8) >> diag.edge(style="dashed", corner_radius=8, **LINE) >> ppo.anchor("bottom", 0.5)
        ref.anchor("bottom", 0.5) >> diag.edge(style="dashed", corner_radius=8, **LINE) >> dpo_loss.anchor("top", 0.9)
        dpo >> diag.edge(**LINE) >> dpo_loss.anchor("top", 0.5)
        ppo.anchor("right", 0.5) >> diag.edge(corner_radius=8, **LINE) >> out.anchor("top", 0.5)
        dpo_loss.anchor("right", 0.5) >> diag.edge(corner_radius=8, **LINE) >> out.anchor("bottom", 0.5)
        diag.text("$\\pi_\\theta$ initialised from $\\pi_{SFT}$", size=12).at(1100, 300, anchor="center")
        diag.caption(
            "**Figure 6:** RLHF learns an explicit reward; DPO optimises the same KL-regularised objective in closed form",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "06_rlhf_dpo_pipeline")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
