"""Example architecture: Auto-Laid-Out Workstation Stack (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram(
        "Auto-Laid-Out Workstation Stack", theme="solarized_light", layout="auto", direction="TB"
    ) as diag:
        applications = diag.shape("Applications", icon="laptop")
        runtime = diag.shape("Runtime", icon="server")
        kernel = diag.shape("Kernel", icon="chip")
        drivers = diag.shape("Drivers", icon="chip")
        hardware = diag.shape("Hardware", icon="server")

        applications >> diag.edge("syscalls") >> runtime
        runtime >> diag.edge("ABI") >> kernel
        kernel >> diag.edge("I/O") >> drivers
        drivers >> diag.edge("MMIO") >> hardware

    return diag


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    return render_all(diagram(), output_dir, "11_auto_workstation_stack")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
