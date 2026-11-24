"""Multi-agent topologies: supervisor versus swarm (handoff).

In a supervisor design every message goes through a central agent that routes
work to specialists and collects their results, so control is easy to audit but
the supervisor is a bottleneck. In a swarm the specialists hand the
conversation directly to one another and the last active agent answers the
user, which saves hops at the cost of a harder-to-predict control path.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Multi-Agent Topologies: Supervisor vs Swarm", theme="cyber_slate") as diag:
        def put(shape, x: float, y: float):
            return shape.at(x, y, anchor="center")

        with diag.group("Supervisor: hub and spoke") as sup:
            u1 = put(diag.shape("User", icon="user"), 330, 150)
            boss = put(diag.shape("Supervisor Agent\nroutes and aggregates", icon="agent", width=190, height=70), 330, 330)
            r1 = put(diag.shape("Research Agent", icon="model"), 120, 540)
            c1 = put(diag.shape("Coding Agent", icon="model"), 330, 540)
            q1 = put(diag.shape("QA Agent", icon="model"), 540, 540)

        with diag.group("Swarm: peer handoff") as swarm:
            u2 = put(diag.shape("User", icon="user"), 840, 150)
            r2 = put(diag.shape("Research Agent\nfirst active", icon="model"), 1100, 150)
            c2 = put(diag.shape("Coding Agent", icon="model"), 1100, 400)
            q2 = put(diag.shape("QA Agent", icon="model"), 840, 400)

        u1 >> diag.edge("request") >> boss
        boss >> diag.edge("delegate / result", two_way=True) >> r1
        boss >> diag.edge("delegate / result", two_way=True) >> c1
        boss >> diag.edge("delegate / result", two_way=True) >> q1
        boss >> diag.edge("answer", style="dashed", source_port="west", target_port="west") >> u1

        u2 >> diag.edge("request") >> r2
        r2 >> diag.edge("handoff", two_way=True) >> c2
        c2 >> diag.edge("handoff", two_way=True) >> q2
        q2 >> diag.edge("answer", style="dashed") >> u2

    return diag


def build_diagram(output_dir: Path | str = "examples/agentic_dev") -> Path:
    return render_all(diagram(), output_dir, "06_supervisor_vs_swarm")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/agentic_dev")
    build_diagram(dest)
