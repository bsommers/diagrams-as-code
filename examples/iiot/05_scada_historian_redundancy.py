"""Example architecture: SCADA & Historian Dual Redundancy (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "05_scada_historian_redundancy.svg"
    png_file = out / "05_scada_historian_redundancy.png"
    readme_file = out / "05_scada_historian_redundancy_README.md"

    with Diagram("SCADA & Historian Dual Redundancy", theme="iiot_light") as diag:
        with diag.group("Control Network") as g_1:
            plc_main = diag.add(Shape("plc_main", "Plant Main PLC", icon="plc", cpu="Redundant Rack"))

        with diag.group("SCADA Server Pair") as g_2:
            scada_pri = diag.add(Shape("scada_pri", "Primary SCADA Server", icon="scada", state="Active Host"))
            scada_sec = diag.add(Shape("scada_sec", "Standby SCADA Server", icon="scada", state="Hot Standby"))
            scada_sec.below(scada_pri, margin=30)

        with diag.group("Historian Archive") as g_3:
            hist_pri = diag.add(Shape("hist_pri", "Primary Historian", icon="historian", storage="NVMe RAID"))
            hist_sec = diag.add(Shape("hist_sec", "Replica Historian", icon="historian", sync="Async Stream"))
            hist_sec.below(hist_pri, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        plc_main >> diag.edge("OPC UA :4840", style="solid") >> scada_pri
        plc_main >> diag.edge("OPC UA :4840", style="solid") >> scada_sec
        scada_pri >> diag.edge("Heartbeat Sync", style="dashed") >> scada_sec
        scada_pri >> diag.edge("Tag Ingest", style="solid") >> hist_pri
        hist_pri >> diag.edge("DB Replication", style="solid") >> hist_sec

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("05_scada_historian_redundancy.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
