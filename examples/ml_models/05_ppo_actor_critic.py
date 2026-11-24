"""The reinforcement-learning loop with a PPO actor-critic agent.

Acting: the agent encodes the state, samples an action from its policy and the
environment answers with the next state and a reward. Learning: transitions
fill a rollout buffer, generalised advantage estimation turns them into
advantages, and PPO maximises a clipped surrogate objective for several epochs.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

NET = Style(font_size=13, fill="#DCE6F2", stroke="#1F2F57")
ACT = Style(font_size=13, fill="#D9EAD3", stroke="#2E6B2E")
ENV = Style(font_size=13, fill="#EFE3CF", stroke="#5A4520")
STEP = Style(font_size=12, fill="#F2F2F2")
LINE = {"width": 1.3}


def diagram() -> Diagram:
    with Diagram("PPO actor-critic agent-environment loop", theme="paper") as diag:
        diag.shape("", 590, 270, z=-1, obstacle=False,
                   style=Style(fill="#F8F8F8", radius=10, dash="6,4")).at(330, 210, anchor="center")
        diag.text("**Agent** (acting)", size=14).at(60, 95, anchor="left_center")

        enc = diag.shape("**Shared encoder**\n$s_t \\to h_t$\n$(B, d_{obs}) \\to (B, d_h)$", 170, 70,
                         style=NET).at(160, 210, anchor="center")
        actor = diag.shape("**Actor** $\\pi_\\theta(a \\mid s)$\nlogits $(B, |A|)$", 170, 60, style=NET).at(
            400, 150, anchor="center")
        critic = diag.shape("**Critic** $V_\\phi(s)$\nvalue $(B, 1)$", 170, 60, style=NET).at(
            400, 290, anchor="center")
        sample = diag.shape("**Sample**\n$a_t \\sim \\pi_\\theta$", 110, 56, style=ACT).at(
            600, 150, anchor="center")
        env = diag.shape("**Environment**\n$s_{t+1}, r_t = \\mathrm{step}(s_t, a_t)$", 210, 90, style=ENV).at(
            960, 210, anchor="center")

        enc.anchor("right", 0.25) >> diag.edge(corner_radius=6, **LINE) >> actor.anchor("left", 0.5)
        enc.anchor("right", 0.75) >> diag.edge(corner_radius=6, **LINE) >> critic.anchor("left", 0.5)
        actor >> diag.edge(**LINE) >> sample
        sample.anchor("right", 0.5) >> diag.edge(label="action $a_t$", corner_radius=8, **LINE) >> env.anchor("left", 0.2)
        env.anchor("top", 0.5) >> diag.edge(
            label="state $s_{t+1}$, reward $r_t$", corner_radius=8, via=[(960, 45), (160, 45)], **LINE
        ) >> enc.anchor("top", 0.5)

        # Learning: transitions flow right to left along the bottom row.
        Y = 470
        buffer = diag.shape(
            "**Rollout buffer**\n$(s_t, a_t, r_t, \\log\\pi_{old}, V_t)$\n$T$ steps $\\times$ $N$ envs",
            210, 70, style=STEP).at(960, Y, anchor="center")
        gae = diag.shape(
            "**GAE**\n$A_t = \\sum_l (\\gamma\\lambda)^l \\delta_{t+l}$", 210, 70, style=STEP).at(
            690, Y, anchor="center")
        loss = diag.shape(
            "**PPO loss**\n$L = -L^{CLIP} + c_1 L^{V} - c_2 H[\\pi]$", 250, 70, style=STEP).at(
            410, Y, anchor="center")
        update = diag.shape("**Update**\nAdam, $K$ epochs\nminibatches", 140, 70, style=ACT).at(
            160, Y, anchor="center")
        env.anchor("bottom", 0.5) >> diag.edge(label="transitions", **LINE) >> buffer
        buffer >> diag.edge(**LINE) >> gae
        gae >> diag.edge(**LINE) >> loss
        loss >> diag.edge(**LINE) >> update
        update.anchor("top", 0.5) >> diag.edge(label="new $\\theta, \\phi$", **LINE) >> enc.anchor("bottom", 0.5)

        diag.text("$\\delta_t = r_t + \\gamma V(s_{t+1}) - V(s_t)$", size=12).at(690, Y + 50, anchor="top_center")
        diag.text("$L^{CLIP} = \\mathrm{E}_t\\,[\\min(\\rho_t A_t,\\ \\mathrm{clip}(\\rho_t, 1 - \\epsilon, 1 + \\epsilon)\\,A_t)]$",
                  size=12).at(410, Y + 50, anchor="top_center")
        diag.text("$\\rho_t = \\pi_\\theta(a_t \\mid s_t) / \\pi_{old}(a_t \\mid s_t)$", size=12).at(
            410, Y + 80, anchor="top_center")
        diag.text("$L^{V} = (V_\\phi(s_t) - R_t)^2$", size=12).at(160, Y + 50, anchor="top_center")
        diag.caption("**Figure 5:** PPO actor-critic; acting fills the buffer, learning updates the same network",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "05_ppo_actor_critic")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
