"""Example architecture: Embedded Real-Time Operating System (RTOS) (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "07_embedded_rtos_system.svg"
    png_file = out / "07_embedded_rtos_system.png"
    readme_file = out / "07_embedded_rtos_system_README.md"

    with Diagram("Embedded Real-Time Operating System (RTOS)", theme="monochrome") as diag:
        with diag.group("Silicon Core") as g_1:
            arm_mcu = diag.add(Shape("arm_mcu", "ARM Cortex-M4 Microcontroller", icon="chip", clock="168 MHz", flash="1MB"))
            crypto = diag.add(Shape("crypto", "Hardware Security Enclave", icon="shield", features="Secure Boot / True RNG"))
            crypto.below(arm_mcu, margin=30)

        with diag.group("System Software") as g_2:
            freertos = diag.add(Shape("freertos", "FreeRTOS Preemptive Kernel", icon="workflow", tick="1ms SysTick"))

        with diag.group("RTOS Tasks") as g_3:
            task_sensor = diag.add(Shape("task_sensor", "Sensor Acquisition Task", icon="sensor", priority="High (Level 3)"))
            task_comms = diag.add(Shape("task_comms", "CAN Bus Protocol Task", icon="router", priority="Medium (Level 2)"))
            task_comms.below(task_sensor, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)

        # Establish inter-element connections with protocol annotations
        arm_mcu >> diag.edge("Initialize OS", style="solid") >> freertos
        freertos >> diag.edge("Schedule Task", style="solid") >> task_sensor
        freertos >> diag.edge("Schedule Task", style="solid") >> task_comms
        task_comms >> diag.edge("Sign Outgoing Packet", style="dashed") >> crypto

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("07_embedded_rtos_system.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
