"""Spec-driven development loop with an AI coding agent.

The written specification, not the chat, is the source of truth: it is refined
into a technical plan, split into small tasks, implemented one task at a time,
and verified against the spec's acceptance criteria. Failed checks go back to
the implementation, and a gap in the spec itself goes back to the spec
(the flow used by toolkits such as GitHub Spec Kit and Kiro).
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Spec-Driven Development Loop", theme="pastel_light") as diag:
        def put(shape, col: int, row: int):
            return shape.at(120 + col * 250, 110 + row * 200, anchor="center")

        intent = put(diag.shape("Intent\nuser story, constraints", icon="user", width=160, height=80), 0, 0)
        spec = put(diag.shape("Spec\nrequirements +\nacceptance criteria", icon="document", width=160, height=90), 1, 0)
        plan = put(diag.shape("Plan\narchitecture, stack,\ninterfaces", icon="workflow", width=160, height=90), 2, 0)
        tasks = put(diag.shape("Tasks\nsmall, ordered,\ntestable", icon="queue", width=160, height=90), 3, 0)
        merge = put(diag.shape("Merge", icon="shield_check"), 0, 1)
        verify = put(diag.shape("Verify\ntests + criteria met?", kind="diamond", width=210, height=120), 1, 1)
        impl = put(diag.shape("Implement\nagent edits code,\none task at a time", icon="agent", width=170, height=90), 3, 1)

        intent >> diag.edge("clarify") >> spec
        spec >> diag.edge("design") >> plan
        plan >> diag.edge("decompose") >> tasks
        tasks >> diag.edge("next task") >> impl
        impl >> diag.edge("diff + tests") >> verify
        verify >> diag.edge("pass") >> merge
        verify >> diag.edge("fail: fix code", style="dashed", source_port="south", target_port="south") >> impl
        verify >> diag.edge("spec gap: amend", style="dashed", source_port="north", target_port="south") >> spec

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "09_spec_driven_development_loop")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
