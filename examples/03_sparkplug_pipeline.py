#!/usr/bin/env python3
"""Example 03: Sparkplug B IIoT Pipeline Architecture.

Recreates diagram-sparklplug.py using the new directed placement engine
with hierarchical nested groups, protocol badges, and multi-consumer fanout.
"""
from __future__ import annotations

from pathlib import Path
import sys
from iiot_diagrams import Diagram, Port


def generate_sparkplug_pipeline(output_dir: Path | str = "output") -> Diagram:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    diag = Diagram(
        "IIoT Unified Namespace (UNS) with Sparkplug B",
        width=1300,
        height=750,
        theme="iiot_dark_gold",
    )

    with diag:
        # Group 1: Manufacturing Cell / Edge of Network (EoN)
        with diag.group(
            "Manufacturing Cell", padding=30.0, header_height=40.0
        ) as mfg:
            plc = diag.shape(
                "Sensors & PLCs",
                width=140.0,
                height=60.0,
                kind="box",
                icon="sensor",
                metadata={"data": "Raw Field Telemetry", "bus": "Modbus / OPC UA"},
            ).at(60.0, 100.0)

            eon = diag.shape(
                "IIoT Edge",
                width=140.0,
                height=60.0,
                kind="box",
                icon="gateway",
                metadata={"role": "Sparkplug B Host / EoN", "format": "Protobuf spBv1.0"},
            ).below(plc, margin=60.0)

            # OT link between PLC and EoN Edge gateway
            plc >> diag.edge(
                label="Modbus/OPC UA",
                source_port=Port.SOUTH,
                target_port=Port.NORTH,
            ) >> eon

        # Group 2: Enterprise UNS (Central IIoT Platform)
        with diag.group(
            "Enterprise UNS (Central IIoT)", padding=30.0, header_height=40.0
        ) as central:
            broker = diag.shape(
                "IIoT Broker",
                width=150.0,
                height=65.0,
                kind="server_rack",
                icon="broker",
                metadata={"role": "State Provider", "namespace": "spBv1.0/Plant1"},
            )

            # Nested Group: State Consumers
            with diag.group(
                "State Consumers", padding=20.0, header_height=30.0
            ) as consumers:
                kafka = diag.shape(
                    "Kafka",
                    width=150.0,
                    height=55.0,
                    kind="box",
                    icon="queue",
                    metadata={"system": "Event Streaming Data Lake"},
                )
                influx = diag.shape(
                    "InfluxDB",
                    width=150.0,
                    height=55.0,
                    kind="cylinder",
                    icon="database",
                    metadata={"system": "Time-Series Historian"},
                ).below(kafka, margin=25.0)
                scada = diag.shape(
                    "Ignition SCADA",
                    width=150.0,
                    height=55.0,
                    kind="box",
                    icon="dashboard",
                    metadata={"system": "Primary Operational HMI/SCADA"},
                ).below(influx, margin=25.0)

            consumers.right_of(broker, margin=80.0, align="center")

        central.right_of(mfg, margin=80.0, align="top")

        # Edge to Central Broker Sparkplug B communication
        eon >> diag.edge(
            label="spBv1.0 Payload",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> broker

        # Decoupled consumption via extensions and subscriptions
        broker >> diag.edge(
            label="Extension",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> kafka

        broker >> diag.edge(
            label="Extension",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> influx

        broker >> diag.edge(
            label="MQTT Subscription",
            source_port=Port.EAST,
            target_port=Port.WEST,
        ) >> scada

    svg_path = out_dir / "sparkplug_pipeline.svg"
    readme_path = out_dir / "sparkplug_pipeline_README.md"

    diag.render_svg(svg_path)
    diag.generate_readme(
        image_file="sparkplug_pipeline.svg",
        output_path=readme_path,
        include_connections=True,
    )

    print(f"Generated: {svg_path}")
    print(f"Generated: {readme_path}")
    return diag


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    generate_sparkplug_pipeline(out_dir)
