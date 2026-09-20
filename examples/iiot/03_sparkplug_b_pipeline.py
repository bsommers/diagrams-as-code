"""Example architecture: Sparkplug B Unified Namespace (IIOT domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/iiot") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "03_sparkplug_b_pipeline.svg"
    png_file = out / "03_sparkplug_b_pipeline.png"
    readme_file = out / "03_sparkplug_b_pipeline_README.md"

    with Diagram("Sparkplug B Unified Namespace", theme="blueprint") as diag:
        with diag.group("Field Sensors") as g_1:
            sensors = diag.add(Shape("sensors", "Sensors & PLCs", icon="sensor", io="4-20mA / Modbus"))

        with diag.group("Edge Node") as g_2:
            eon = diag.add(Shape("eon", "Sparkplug B Edge Node", icon="gateway", compression="Gzip", payload="Protobuf"))

        with diag.group("Unified Namespace") as g_3:
            broker = diag.add(Shape("broker", "UNS Central Broker", icon="broker", namespace="spBv1.0/Plant1"))

        with diag.group("Consumer Applications") as g_4:
            scada = diag.add(Shape("scada", "Host SCADA Application", icon="scada", role="Primary Application"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)

        # Establish inter-element connections with protocol annotations
        sensors >> diag.edge("Modbus RTU", style="solid") >> eon
        eon >> diag.edge("NBIRTH / NDATA", style="solid") >> broker
        broker >> diag.edge("MQTT Subscription", style="solid") >> scada

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("03_sparkplug_b_pipeline.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/iiot")
    build_diagram(dest)
