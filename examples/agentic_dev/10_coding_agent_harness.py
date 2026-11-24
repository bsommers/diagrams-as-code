"""Anatomy of a coding-agent harness.

The model only emits text and tool calls; the harness around it builds the
context window each turn, checks every tool call against a permission policy,
runs approved calls in a sandbox, and feeds the result back into the next
turn. Persistent memory (project instruction files, saved notes) is loaded
into the context at the start of a session.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Coding-Agent Harness", theme="high_contrast") as diag:
        def put(shape, x: float, y: float):
            return shape.at(x, y, anchor="center")

        user = put(diag.shape("Developer\nprompt and approvals", icon="user", width=170), 480, 90)

        with diag.group("Harness: agent loop") as harness:
            mem = put(diag.shape("Memory\ninstruction files,\nsaved notes", icon="storage", width=160, height=80), 130, 330)
            ctx = put(diag.shape("Context Window\nsystem prompt, history,\ntool results", icon="document", width=180, height=80), 400, 330)
            llm = put(diag.shape("LLM\nnext message or\ntool call", icon="model", width=160, height=80), 670, 330)
            perm = put(diag.shape("Permission Policy\nallow / ask / deny", icon="shield_check", width=170, height=80), 930, 330)

        with diag.group("Sandbox: execution boundary") as sandbox:
            shell = put(diag.shape("Shell\ntests, build", icon="terminal", width=150), 1230, 230)
            fs = put(diag.shape("File Edits\nworking tree", icon="storage", width=150), 1230, 350)
            mcp = put(diag.shape("MCP Servers\nexternal tools", icon="server", width=150), 1230, 470)

        user >> diag.edge("task", source_port="south", target_port="north") >> ctx
        perm >> diag.edge("ask", style="dashed", source_port="north", target_port="east") >> user
        mem >> diag.edge("load at start", style="dashed") >> ctx
        ctx >> diag.edge("prompt") >> llm
        llm >> diag.edge("tool call") >> perm
        perm >> diag.edge("approved") >> sandbox
        sandbox >> diag.edge("tool results", style="dashed", source_port="south", target_port="south") >> ctx

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "10_coding_agent_harness")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
