"""Example architecture: Auto-Laid-Out Campus Core (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram(
        "Auto-Laid-Out Campus Core", theme="emerald", layout="auto", direction="TB"
    ) as diag:
        internet = diag.shape("Internet", icon="cloud")
        edge_router = diag.shape("Edge Router", icon="router")
        core_switch = diag.shape("Core Switch", icon="switch")
        dist_a = diag.shape("Distribution A", icon="switch")
        dist_b = diag.shape("Distribution B", icon="switch")
        access_a = diag.shape("Access A", icon="switch")
        access_b = diag.shape("Access B", icon="switch")

        internet >> diag.edge("BGP") >> edge_router
        edge_router >> diag.edge() >> core_switch
        core_switch >> diag.edge() >> dist_a
        core_switch >> diag.edge() >> dist_b
        dist_a >> diag.edge() >> access_a
        dist_b >> diag.edge() >> access_b

    return diag


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    return render_all(diagram(), output_dir, "11_auto_campus_core")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
