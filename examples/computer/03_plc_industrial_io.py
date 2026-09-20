"""Example architecture: Industrial PLC Hardware & IO Subsystem (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "03_plc_industrial_io.svg"
    png_file = out / "03_plc_industrial_io.png"
    readme_file = out / "03_plc_industrial_io_README.md"

    with Diagram("Industrial PLC Hardware & IO Subsystem", theme="blueprint") as diag:
        with diag.group("Control CPU") as g_1:
            plc_cpu = diag.add(Shape("plc_cpu", "Siemens S7-1500 PLC", icon="plc", firmware="v3.1", cycle="2ms Scan"))

        with diag.group("Signal Modules") as g_2:
            di_module = diag.add(Shape("di_module", "16-Channel Digital Input", icon="sensor", voltage="24V DC Optical Isolation"))
            ai_module = diag.add(Shape("ai_module", "8-Channel Analog Input", icon="sensor", signal="4-20mA / 0-10V"))
            ai_module.below(di_module, margin=30)

        with diag.group("Actuator Modules") as g_3:
            relay_out = diag.add(Shape("relay_out", "Relay Output Driver", icon="terminal", rating="250V AC 5A"))
            stepper = diag.add(Shape("stepper", "Stepper Motor Drive Module", icon="chip", protocol="Pulse / Direction 200kHz"))
            stepper.below(relay_out, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        di_module >> diag.edge("Backplane Bus", style="solid") >> plc_cpu
        ai_module >> diag.edge("Backplane Bus", style="solid") >> plc_cpu
        plc_cpu >> diag.edge("Control Signals", style="solid") >> relay_out
        plc_cpu >> diag.edge("PTO Motion Pulses", style="solid") >> stepper

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("03_plc_industrial_io.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
