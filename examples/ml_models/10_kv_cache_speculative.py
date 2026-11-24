"""The KV cache and a speculative-decoding timeline.

Top: during generation the keys and values of earlier tokens never change, so
they are cached and each step appends one row and attends over the cache.
Bottom: a small draft model proposes $\\gamma$ tokens cheaply; the large target
model scores all of them in a single forward pass, keeps the accepted prefix
and resamples at the first rejection, so several tokens cost one target pass.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

OLD = Style(font_size=12, fill="#E4E4E4", stroke="#777777")
NEW = Style(font_size=12, fill="#D9EAD3", stroke="#2E6B2E", stroke_width=1.8)
TARGET = Style(font_size=12, fill="#DCE6F2", stroke="#1F2F57")
DRAFT = Style(font_size=11, fill="#EFE3CF", stroke="#5A4520")
OK = Style(font_size=11, fill="#D9EAD3", stroke="#2E6B2E")
BAD = Style(font_size=11, fill="#F6D5C8", stroke="#9C3B1B", stroke_width=1.6)
LINE = {"width": 1.2}
T0 = 300.0  # where time zero sits on the lanes


def diagram() -> Diagram:
    with Diagram("KV cache and speculative decoding", theme="paper") as diag:
        # ---- KV cache ------------------------------------------------------------
        diag.text("**KV cache** at decoding step $t$", size=14).at(60, 30, anchor="left_center")
        for row, (name, sym, y) in enumerate((("$K$ cache", "k", 80), ("$V$ cache", "v", 135))):
            diag.text(f"**{name}**\n$(B, h_{{kv}}, t, d_k)$", size=12, align="left").at(60, y, anchor="left_center")
            for i in range(5):
                diag.shape(f"${sym}_{i + 1}$", 46, 36, style=OLD).at(T0 + i * 50, y, anchor="left_center")
            new = diag.shape(f"${sym}_t$", 46, 36, style=NEW).at(T0 + 5 * 50, y, anchor="left_center")
        diag.text("cached, reused", size=11, color="#555555").at(T0 + 120, 165, anchor="top_center")
        diag.text("appended", size=11, color="#2E6B2E").at(T0 + 273, 165, anchor="top_center")
        diag.text(
            "Only the new token's $q_t, k_t, v_t$ are computed.\n"
            "$\\mathrm{softmax}(q_t K_{1:t}^T / \\sqrt{d_k})\\, V_{1:t}$: $O(t)$ work per step, not $O(t^2)$.",
            size=12, align="left").at(670, 80, anchor="left_center")
        diag.text(
            "Memory: $2 \\cdot L \\cdot h_{kv} \\cdot d_k \\cdot t \\cdot b$ bytes per sequence\n"
            "(e.g. $L = 32$, $h_{kv} = 8$, $d_k = 128$, $t = 4096$, fp16: 0.5 GiB)",
            size=12, align="left").at(670, 135, anchor="left_center")

        # ---- Timeline ------------------------------------------------------------
        diag.text("**Decoding timeline** (one box = one forward pass; widths show relative cost)", size=14).at(
            60, 215, anchor="left_center")
        lanes = {"auto": 270, "draft": 350, "target": 430, "out": 510}
        names = {
            "auto": "**Target only**\n$M_p$, one token per pass",
            "draft": "**Draft** $M_q$\n~10x cheaper, $\\gamma = 4$",
            "target": "**Target** $M_p$\nverifies in parallel",
            "out": "**Tokens kept**\nspeculative step",
        }
        for key, y in lanes.items():
            diag.text(names[key], size=12, align="left").at(60, y, anchor="left_center")

        for i in range(4):
            diag.shape(f"$t_{i + 1}$", 90, 40, style=TARGET).at(T0 + i * 100, lanes["auto"], anchor="left_center")
        diag.text("4 tokens at $t = 400$", size=12).at(T0 + 410, lanes["auto"], anchor="left_center")

        for i in range(4):
            diag.shape(f"$d_{i + 1}$", 30, 34, style=DRAFT).at(T0 + i * 36, lanes["draft"], anchor="left_center")
        verify = diag.shape("verify 5 positions\n$(B, \\gamma + 1, |V|)$", 120, 44, style=TARGET).at(
            T0 + 150, lanes["target"], anchor="left_center")

        end = T0 + 270  # verification finishes
        marks = [("accept", OK), ("accept", OK), ("accept", OK), ("reject:\nresample", BAD)]
        for i, (lab, st) in enumerate(marks):
            diag.shape(f"$d_{i + 1}$\n{lab}" if i < 3 else f"$d_4 \\to d_4'$\n{lab}", 80, 44, style=st).at(
                end + 10 + i * 85, lanes["out"], anchor="left_center")
        diag.connect(verify.anchor("right", 0.5), diag.point(end + 10, lanes["out"] - 22), routing="direct",
                     style="dashed", width=1.0)
        diag.connect(diag.point(T0 + 4 * 36 - 6, lanes["draft"] + 17), verify.anchor("top", 0.2), style="dashed",
                     width=1.0, corner_radius=6)
        diag.connect((end, 328), (end, 535), routing="direct", style="dashed", width=1.0, color="#9C3B1B",
                     arrow_head=False)
        diag.text("4 tokens at $t = 270$", size=12, color="#9C3B1B").at(end + 10, lanes["draft"], anchor="left_center")

        # Time axis.
        diag.connect((T0 - 20, 590), (T0 + 760, 590), routing="direct", width=1.2)
        diag.text("time", size=12).at(T0 + 770, 590, anchor="left_center")
        diag.text(
            "Accept $d_i$ with probability $\\min(1, p(d_i) / q(d_i))$; on rejection resample from "
            "$\\mathrm{norm}(\\max(0, p - q))$. If all $\\gamma$ are accepted, a bonus token from $p$ is free.",
            size=12).at(60, 625, anchor="left_center")
        diag.text(
            "Expected tokens per target pass $= (1 - \\alpha^{\\gamma + 1}) / (1 - \\alpha)$, "
            "$\\alpha$ = mean acceptance rate; the output distribution equals the target's.",
            size=12).at(60, 650, anchor="left_center")
        diag.caption("**Figure 10:** A KV cache removes recomputation; speculative decoding spends one target pass on many tokens",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/ml_models") -> Path:
    return render_all(diagram(), output_dir, "10_kv_cache_speculative")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/ml_models"))
