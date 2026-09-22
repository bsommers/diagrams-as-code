"""Example architecture: Auto-Laid-Out SOC Detection Pipeline (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram(
        "Auto-Laid-Out SOC Detection Pipeline", theme="cyber_slate", layout="auto"
    ) as diag:
        with diag.group("Sources") as sources:
            endpoints = diag.shape("Endpoints", icon="laptop")
            firewalls = diag.shape("Firewalls", icon="firewall")
        with diag.group("SIEM") as siem:
            log_collector = diag.shape("Log Collector", icon="server")
            correlation_engine = diag.shape("Correlation Engine", icon="shield")
        with diag.group("Response") as response:
            soar = diag.shape("SOAR", icon="server")
            analyst_console = diag.shape("Analyst Console", icon="dashboard")

        endpoints >> diag.edge("EDR") >> log_collector
        firewalls >> diag.edge("syslog") >> log_collector
        log_collector >> diag.edge("normalize") >> correlation_engine
        correlation_engine >> diag.edge("alert") >> soar
        soar >> diag.edge("case") >> analyst_console

    return diag


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    return render_all(diagram(), output_dir, "11_auto_soc_pipeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
