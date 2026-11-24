"""Prompt chaining with a programmatic gate, after Anthropic's "Building effective agents".

A task is split into fixed steps. Each LLM call consumes the previous call's
output, and a plain-code gate between steps checks the intermediate result
before the next call is paid for. A failed gate exits early instead of passing
bad output down the chain.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Prompt Chaining with a Gate", theme="paper", layout="auto", direction="LR") as diag:
        inp = diag.shape("Input", icon="user")
        call1 = diag.shape("LLM Call 1\nOutline", icon="model")
        gate = diag.shape("Gate\nprogrammatic check", kind="diamond", width=170, height=100)
        call2 = diag.shape("LLM Call 2\nDraft from outline", icon="model")
        call3 = diag.shape("LLM Call 3\nTranslate / polish", icon="model")
        out = diag.shape("Output", icon="document")
        fail = diag.shape("Exit early\nreturn error", icon="shield")

        inp >> diag.edge("task") >> call1
        call1 >> diag.edge("outline") >> gate
        gate >> diag.edge("pass") >> call2
        call2 >> diag.edge("draft") >> call3
        call3 >> diag.edge("final text") >> out
        gate >> diag.edge("fail", style="dashed") >> fail

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "01_prompt_chaining_gate")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
