"""Example architecture: Predictive Maintenance Vibration Analysis (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Predictive Maintenance Vibration Analysis", theme="blueprint") as diag:
        with diag.group("Rotary Equipment") as g_1:
            sensor_x = diag.add(Shape("sensor_x", "3-Axis Accelerometer", icon="sensor", sampling="10kHz", axis="X/Y/Z"))
            temp_sensor = diag.add(Shape("temp_sensor", "Bearing Thermocouple", icon="sensor", range="-40..150C"))
            temp_sensor.below(sensor_x, margin=30)

        with diag.group("Edge Analytics") as g_2:
            edge_dsp = diag.add(Shape("edge_dsp", "DSP Anomaly Detector", icon="gateway", algorithm="FFT Peak Detection"))
            historian = diag.add(Shape("historian", "Plant Historian", icon="historian", retention="90 Days"))
            historian.below(edge_dsp, margin=30)

        with diag.group("Cloud ML Platform") as g_3:
            cloud_ml = diag.add(Shape("cloud_ml", "Predictive ML Model", icon="server", rul="Remaining Useful Life"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        sensor_x >> diag.edge("Analog 4-20mA", style="solid") >> edge_dsp
        temp_sensor >> diag.edge("Modbus RS-485", style="solid") >> edge_dsp
        edge_dsp >> diag.edge("OPC UA Stream", style="solid") >> historian
        edge_dsp >> diag.edge("MQTT TLS", style="solid") >> cloud_ml

    return diag


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    return render_all(diagram(), output_dir, "04_predictive_maintenance_vibration")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
