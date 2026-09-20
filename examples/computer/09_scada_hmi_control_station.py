"""Example architecture: SCADA Dual-Console Operator Control Station (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "09_scada_hmi_control_station.svg"
    png_file = out / "09_scada_hmi_control_station.png"
    readme_file = out / "09_scada_hmi_control_station_README.md"

    with Diagram("SCADA Dual-Console Operator Control Station", theme="iiot_dark_gold") as diag:
        with diag.group("Control Room") as g_1:
            hmi_left = diag.add(Shape("hmi_left", "Primary Operator Touchscreen", icon="dashboard", display="32-inch Industrial Touch"))
            hmi_right = diag.add(Shape("hmi_right", "Secondary Alarm Monitor", icon="dashboard", display="32-inch High Contrast"))
            hmi_right.below(hmi_left, margin=30)

        with diag.group("Server Room") as g_2:
            scada_pri = diag.add(Shape("scada_pri", "SCADA Server Primary", icon="server_rack", redundancy="Active Hot Standby"))
            scada_sec = diag.add(Shape("scada_sec", "SCADA Server Secondary", icon="server_rack", redundancy="Warm Standby"))
            scada_sec.below(scada_pri, margin=30)

        with diag.group("Substation Field") as g_3:
            field_rtu = diag.add(Shape("field_rtu", "Remote Terminal Units (RTUs)", icon="plc", protocol="DNP3 / IEC 60870-5"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        hmi_left >> diag.edge("OPC UA Graphics", style="solid") >> scada_pri
        hmi_right >> diag.edge("Live Alarm Feed", style="solid") >> scada_pri
        scada_pri >> diag.edge("Heartbeat Sync", style="dotted") >> scada_sec
        scada_pri >> diag.edge("Serial DNP3 Over IP", style="solid") >> field_rtu

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("09_scada_hmi_control_station.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
