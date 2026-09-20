"""Example architecture: OPC UA TSN Edge Aggregator (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "06_opc_ua_edge_aggregation.svg"
    png_file = out / "06_opc_ua_edge_aggregation.png"
    readme_file = out / "06_opc_ua_edge_aggregation_README.md"

    with Diagram("OPC UA TSN Edge Aggregator", theme="iiot_light") as diag:
        with diag.group("Cell Devices") as g_1:
            plc_cell1 = diag.add(Shape("plc_cell1", "Assembly Cell PLC", icon="plc", vendor="Siemens"))
            plc_cell2 = diag.add(Shape("plc_cell2", "Packaging Cell PLC", icon="plc", vendor="Rockwell"))
            plc_cell2.below(plc_cell1, margin=30)
            robot_cell = diag.add(Shape("robot_cell", "Welding Robot Controller", icon="robot", protocol="Profinet"))
            robot_cell.below(plc_cell2, margin=30)

        with diag.group("Aggregation Layer") as g_2:
            agg_gw = diag.add(Shape("agg_gw", "OPC UA Edge Aggregator", icon="gateway", model="Unified Node-RED"))

        with diag.group("MES & UNS") as g_3:
            mes = diag.add(Shape("mes", "Manufacturing Exec System", icon="server", tier="ISA-95 Level 3"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        plc_cell1 >> diag.edge("OPC UA Client", style="solid") >> agg_gw
        plc_cell2 >> diag.edge("EtherNet/IP", style="solid") >> agg_gw
        robot_cell >> diag.edge("Profinet IO", style="solid") >> agg_gw
        agg_gw >> diag.edge("MQTT Sparkplug", style="solid") >> mes

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("06_opc_ua_edge_aggregation.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
