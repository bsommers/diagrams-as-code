"""Example architecture: Endpoint Detection & Threat Hunting Grid (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "05_edr_threat_hunting.svg"
    png_file = out / "05_edr_threat_hunting.png"
    readme_file = out / "05_edr_threat_hunting_README.md"

    with Diagram("Endpoint Detection & Threat Hunting Grid", theme="crimson") as diag:
        with diag.group("Managed Endpoints") as g_1:
            win_host = diag.add(Shape("win_host", "Finance Desktop", icon="laptop", os="Windows 11"))
            linux_srv = diag.add(Shape("linux_srv", "Production Server", icon="server", os="RHEL 9"))
            linux_srv.below(win_host, margin=30)
            mac_host = diag.add(Shape("mac_host", "Executive Laptop", icon="laptop", os="macOS Sonoma"))
            mac_host.below(linux_srv, margin=30)

        with diag.group("Threat Analytics Engine") as g_2:
            sensor_hub = diag.add(Shape("sensor_hub", "Telemetry Ingestion", icon="malware_scan", protocol="gRPC Streaming"))
            mitre_engine = diag.add(Shape("mitre_engine", "ATT&CK Correlator", icon="siem", rules="Behavioral Heuristics"))
            mitre_engine.below(sensor_hub, margin=30)

        with diag.group("Security Operations") as g_3:
            analyst_ws = diag.add(Shape("analyst_ws", "Threat Hunter Console", icon="soc", role="Lead Investigator"))
            quarantine = diag.add(Shape("quarantine", "Host Isolation Action", icon="lock", status="Isolated at NIC"))
            quarantine.below(analyst_ws, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        win_host >> diag.edge("Process Events", style="solid") >> sensor_hub
        linux_srv >> diag.edge("Auditd Telemetry", style="solid") >> sensor_hub
        mac_host >> diag.edge("Endpoint Events", style="solid") >> sensor_hub
        sensor_hub >> diag.edge("Structured Events", style="solid") >> mitre_engine
        mitre_engine >> diag.edge("TTP Incident", style="solid") >> analyst_ws
        analyst_ws >> diag.edge("Execute Containment", style="solid") >> quarantine
        quarantine >> diag.edge("Isolate NIC", style="dashed") >> win_host

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("05_edr_threat_hunting.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
