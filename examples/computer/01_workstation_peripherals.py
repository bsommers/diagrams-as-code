"""Example architecture: Professional Workstation Hardware Topology (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "01_workstation_peripherals.svg"
    readme_file = out / "01_workstation_peripherals_README.md"

    with Diagram("Professional Workstation Hardware Topology", theme="iiot_light") as diag:
        with diag.group("Compute Core") as g_1:
            pc_host = diag.add(Shape("pc_host", "Workstation Host Tower", icon="laptop", cpu="AMD Ryzen 9 7950X", ram="64GB DDR5"))

        with diag.group("Display Peripherals") as g_2:
            display1 = diag.add(Shape("display1", "Primary 4K Monitor", icon="mobile", resolution="3840x2160 @ 144Hz"))
            display2 = diag.add(Shape("display2", "Secondary Vertical Display", icon="mobile", resolution="2160x3840 @ 60Hz"))
            display2.below(display1, margin=30)

        with diag.group("Input Devices") as g_3:
            keyboard = diag.add(Shape("keyboard", "Custom Mechanical Keyboard", icon="terminal", switch="Hot-Swap Mechanical"))

        with diag.group("Audio Hardware") as g_4:
            dac = diag.add(Shape("dac", "USB High-Res DAC Audio", icon="router", sample="32-bit / 384kHz"))

        with diag.group("Storage Expansion") as g_5:
            backup_ssd = diag.add(Shape("backup_ssd", "External NVMe RAID SSD", icon="storage", interface="Thunderbolt 4 40Gbps"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)

        # Establish inter-element connections with protocol annotations
        pc_host >> diag.edge("DisplayPort 2.1", style="solid") >> display1
        pc_host >> diag.edge("DisplayPort 1.4", style="solid") >> display2
        keyboard >> diag.edge("USB-C 2.0", style="solid") >> pc_host
        pc_host >> diag.edge("USB Audio Class 2", style="solid") >> dac
        pc_host >> diag.edge("Thunderbolt 4", style="solid") >> backup_ssd

        diag.render_svg(svg_file)
        diag.generate_readme("01_workstation_peripherals.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
