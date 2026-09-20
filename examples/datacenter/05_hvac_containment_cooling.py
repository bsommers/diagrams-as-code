"""Example architecture: Datacenter In-Row CRAC & Cooling Loops (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "05_hvac_containment_cooling.svg"
    readme_file = out / "05_hvac_containment_cooling_README.md"

    with Diagram("Datacenter In-Row CRAC & Cooling Loops", theme="nord") as diag:
        with diag.group("Containment Zone") as g_1:
            hot_aisle = diag.add(Shape("hot_aisle", "Hot Aisle Enclosure (38°C)", icon="cooling", exhaust="Encapsulated Airflow"))

        with diag.group("Cooling Units") as g_2:
            crac1 = diag.add(Shape("crac1", "In-Row CRAC Unit 01", icon="cooling", fan="Variable Speed EC Fans"))
            crac2 = diag.add(Shape("crac2", "In-Row CRAC Unit 02", icon="cooling", fan="Variable Speed EC Fans"))
            crac2.below(crac1, margin=30)

        with diag.group("Central Plant") as g_3:
            water_loop = diag.add(Shape("water_loop", "Chilled Water Primary Loop", icon="cooling", temperature="7°C Supply / 14°C Return"))
            chiller = diag.add(Shape("chiller", "Variable Speed Centrifugal Chiller", icon="cooling", cop="6.2 COP Efficiency"))
            chiller.below(water_loop, margin=30)

        with diag.group("External Plant") as g_4:
            towers = diag.add(Shape("towers", "Rooftop Evaporative Cooling Towers", icon="cooling", wet_bulb="24°C Design"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        hot_aisle >> diag.edge("Duct Intake", style="solid") >> crac1
        hot_aisle >> diag.edge("Duct Intake", style="solid") >> crac2
        crac1 >> diag.edge("Heat Exchange", style="solid") >> water_loop
        crac2 >> diag.edge("Heat Exchange", style="solid") >> water_loop
        water_loop >> diag.edge("Chilled Water Feed", style="solid") >> chiller
        chiller >> diag.edge("Condenser Water Loop", style="solid") >> towers

        diag.render_svg(svg_file)
        diag.generate_readme("05_hvac_containment_cooling.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
