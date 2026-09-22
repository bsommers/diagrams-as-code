"""Example architecture: Water & Wastewater Remote RTU Mesh (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Water & Wastewater Remote RTU Mesh", theme="cyber_slate") as diag:
        with diag.group("Remote Lift Stations") as g_1:
            pump_sens = diag.add(Shape("pump_sens", "Well Level & Flow Sensor", icon="sensor", sensor="Submersible 4-20mA"))
            solar_rtu = diag.add(Shape("solar_rtu", "Solar Powered RTU", icon="plc", power="Solar / 24V Batt"))
            solar_rtu.below(pump_sens, margin=30)

        with diag.group("Cellular Network") as g_2:
            cell_tower = diag.add(Shape("cell_tower", "Cellular LTE-M Tower", icon="router", apn="Private Utility APN"))

        with diag.group("Central Utility SCADA") as g_3:
            scada_hub = diag.add(Shape("scada_hub", "Central Utility SCADA", icon="scada", protocol="DNP3 over IP"))
            alert_sys = diag.add(Shape("alert_sys", "Emergency Dialout System", icon="mobile", sms="SMS / Voice Alert"))
            alert_sys.below(scada_hub, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        pump_sens >> diag.edge("Analog Input", style="solid") >> solar_rtu
        solar_rtu >> diag.edge("DNP3 LTE-M", style="solid") >> cell_tower
        cell_tower >> diag.edge("IPSec VPN Tunnel", style="solid") >> scada_hub
        scada_hub >> diag.edge("High Alarm Trigger", style="solid") >> alert_sys

    return diag


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    return render_all(diagram(), output_dir, "10_water_wastewater_remote_rtu")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
