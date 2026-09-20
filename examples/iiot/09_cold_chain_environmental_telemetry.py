"""Example architecture: Cold Chain Environmental Monitoring (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "09_cold_chain_environmental_telemetry.svg"
    png_file = out / "09_cold_chain_environmental_telemetry.png"
    readme_file = out / "09_cold_chain_environmental_telemetry_README.md"

    with Diagram("Cold Chain Environmental Monitoring", theme="cyber_slate") as diag:
        with diag.group("Refrigerated Zones") as g_1:
            temp_probe1 = diag.add(Shape("temp_probe1", "Freezer Probe (-30C)", icon="sensor", accuracy="+-0.1C"))
            temp_probe2 = diag.add(Shape("temp_probe2", "Chiller Probe (+4C)", icon="sensor", accuracy="+-0.2C"))
            temp_probe2.below(temp_probe1, margin=30)
            hum_probe = diag.add(Shape("hum_probe", "Humidity Sensor", icon="sensor", range="10-90% RH"))
            hum_probe.below(temp_probe2, margin=30)

        with diag.group("Telemetry Gateway") as g_2:
            lora_gw = diag.add(Shape("lora_gw", "LoRaWAN Gateway", icon="gateway", freq="915 MHz"))

        with diag.group("Cold Chain Compliance") as g_3:
            audit_db = diag.add(Shape("audit_db", "21 CFR Part 11 Audit DB", icon="database", audit="Immutable Log"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        temp_probe1 >> diag.edge("LoRa Wireless", style="solid") >> lora_gw
        temp_probe2 >> diag.edge("LoRa Wireless", style="solid") >> lora_gw
        hum_probe >> diag.edge("LoRa Wireless", style="solid") >> lora_gw
        lora_gw >> diag.edge("HTTPS Ingest", style="solid") >> audit_db

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("09_cold_chain_environmental_telemetry.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
