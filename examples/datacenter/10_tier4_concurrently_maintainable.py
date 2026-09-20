"""Example architecture: Tier IV Concurrently Maintainable Datacenter (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "10_tier4_concurrently_maintainable.svg"
    png_file = out / "10_tier4_concurrently_maintainable.png"
    readme_file = out / "10_tier4_concurrently_maintainable_README.md"

    with Diagram("Tier IV Concurrently Maintainable Datacenter", theme="blueprint") as diag:
        with diag.group("Utility Service") as g_1:
            grid_a = diag.add(Shape("grid_a", "Substation Grid Line A", icon="ups", feed="34.5kV Dedicated Feed"))
            grid_b = diag.add(Shape("grid_b", "Substation Grid Line B", icon="ups", feed="34.5kV Diverse Path"))
            grid_b.below(grid_a, margin=30)

        with diag.group("Power Path A") as g_2:
            ups_train_a = diag.add(Shape("ups_train_a", "UPS 2(N+1) Train A", icon="ups", efficiency="97% Double Conversion"))

        with diag.group("Power Path B") as g_3:
            ups_train_b = diag.add(Shape("ups_train_b", "UPS 2(N+1) Train B", icon="ups", efficiency="97% Double Conversion"))

        with diag.group("Cooling Path A") as g_4:
            crac_loop_a = diag.add(Shape("crac_loop_a", "Chilled Water Path A", icon="cooling", pumps="Variable Secondary"))

        with diag.group("Cooling Path B") as g_5:
            crac_loop_b = diag.add(Shape("crac_loop_b", "Chilled Water Path B", icon="cooling", pumps="Variable Secondary"))

        with diag.group("White Space Floor") as g_6:
            mission_rack = diag.add(Shape("mission_rack", "Mission-Critical Server Cabinets", icon="server_rack", sla="99.995% Availability"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)
        g_5.right_of(g_4, margin=80)
        g_6.right_of(g_5, margin=80)

        # Establish inter-element connections with protocol annotations
        grid_a >> diag.edge("Source Feed 1", style="solid") >> ups_train_a
        grid_b >> diag.edge("Source Feed 2", style="solid") >> ups_train_b
        ups_train_a >> diag.edge("Power Bus Duct A", style="solid") >> mission_rack
        ups_train_b >> diag.edge("Power Bus Duct B", style="dashed") >> mission_rack
        crac_loop_a >> diag.edge("Underfloor Supply A", style="solid") >> mission_rack
        crac_loop_b >> diag.edge("Underfloor Supply B", style="dashed") >> mission_rack

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("10_tier4_concurrently_maintainable.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
