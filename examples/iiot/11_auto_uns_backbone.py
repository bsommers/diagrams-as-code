"""Example architecture: Auto-Laid-Out UNS Backbone (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram(
        "Auto-Laid-Out UNS Backbone", theme="iiot_dark_gold", layout="auto"
    ) as diag:
        with diag.group("Plant Floor") as plant_floor:
            plc = diag.shape("PLC", icon="plc")
            sensor_array = diag.shape("Sensor Array", icon="sensor")
        with diag.group("Edge") as edge:
            edge_gateway = diag.shape("Edge Gateway", icon="gateway")
        with diag.group("Enterprise") as enterprise:
            mqtt_broker = diag.shape("MQTT Broker", icon="broker")
            historian = diag.shape("Historian", icon="database")
            dashboard = diag.shape("Dashboard", icon="dashboard")

        plc >> diag.edge("OPC UA") >> edge_gateway
        sensor_array >> diag.edge("Modbus") >> edge_gateway
        edge_gateway >> diag.edge("Sparkplug B") >> mqtt_broker
        mqtt_broker >> diag.edge("ingest") >> historian
        mqtt_broker >> diag.edge("subscribe") >> dashboard

    return diag


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    return render_all(diagram(), output_dir, "11_auto_uns_backbone")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
