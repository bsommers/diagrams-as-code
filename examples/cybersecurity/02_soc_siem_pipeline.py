"""Example architecture: SOC & SIEM Telemetry Analytics Pipeline (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "02_soc_siem_pipeline.svg"
    png_file = out / "02_soc_siem_pipeline.png"
    readme_file = out / "02_soc_siem_pipeline_README.md"

    with Diagram("SOC & SIEM Telemetry Analytics Pipeline", theme="crimson") as diag:
        with diag.group("Telemetry Sources") as g_1:
            edr = diag.add(Shape("edr", "Endpoint EDR Fleet", icon="malware_scan", agents="5000 Nodes"))
            net_fw = diag.add(Shape("net_fw", "Firewall Syslog", icon="firewall", protocol="Syslog/TLS"))
            net_fw.below(edr, margin=30)
            cloud_trail = diag.add(Shape("cloud_trail", "Cloud Audit Trail", icon="cloud", source="API Events"))
            cloud_trail.below(net_fw, margin=30)

        with diag.group("SIEM Analytics Core") as g_2:
            aggregator = diag.add(Shape("aggregator", "Log Aggregator", icon="server", throughput="100k EPS"))
            siem = diag.add(Shape("siem", "SIEM Correlation Engine", icon="siem", engine="Realtime ML"))
            siem.below(aggregator, margin=30)

        with diag.group("Incident Response") as g_3:
            soar = diag.add(Shape("soar", "SOAR Automated Playbook", icon="workflow", action="Auto-Containment"))
            soc = diag.add(Shape("soc", "SOC Analyst Console", icon="soc", tier="Tier 2 SOC"))
            soc.below(soar, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        edr >> diag.edge("gRPC Telemetry", style="solid") >> aggregator
        net_fw >> diag.edge("Syslog", style="solid") >> aggregator
        cloud_trail >> diag.edge("Event Bridge", style="solid") >> aggregator
        aggregator >> diag.edge("Enriched Stream", style="solid") >> siem
        siem >> diag.edge("High Priority Alert", style="solid") >> soar
        siem >> diag.edge("Case Escalation", style="solid") >> soc
        soar >> diag.edge("Status Report", style="dashed") >> soc

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("02_soc_siem_pipeline.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
