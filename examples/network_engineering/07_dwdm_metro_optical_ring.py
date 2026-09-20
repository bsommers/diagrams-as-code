"""Example architecture: Metro DWDM Optical Transport Ring (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "07_dwdm_metro_optical_ring.svg"
    readme_file = out / "07_dwdm_metro_optical_ring_README.md"

    with Diagram("Metro DWDM Optical Transport Ring", theme="blueprint") as diag:
        with diag.group("West Datacenter Node") as g_1:
            roadm_w = diag.add(Shape("roadm_w", "ROADM Metro West", icon="fiber_optic", waves="96 C-Band Channels"))

        with diag.group("East Datacenter Node") as g_2:
            roadm_e = diag.add(Shape("roadm_e", "ROADM Metro East", icon="fiber_optic", waves="96 C-Band Channels"))

        with diag.group("South Aggregation Hub") as g_3:
            roadm_s = diag.add(Shape("roadm_s", "ROADM Metro South", icon="fiber_optic", amp="EDFA In-Line Amp"))
            patch_bay = diag.add(Shape("patch_bay", "Optical Patch Panel", icon="patch_panel", capacity="144-Fiber LC/APC"))
            patch_bay.below(roadm_s, margin=30)

        with diag.group("Client Framing Tier") as g_4:
            transponder = diag.add(Shape("transponder", "100G Muxponder", icon="switch", client="10x 10GbE into 100G OTU4"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        roadm_w >> diag.edge("Dark Fiber 45km", style="solid") >> roadm_e
        roadm_e >> diag.edge("Dark Fiber 60km", style="solid") >> roadm_s
        roadm_s >> diag.edge("Dark Fiber 38km", style="solid") >> roadm_w
        roadm_s >> diag.edge("Structured Patching", style="solid") >> patch_bay
        patch_bay >> diag.edge("Client Hand-off", style="solid") >> transponder

        diag.render_svg(svg_file)
        diag.generate_readme("07_dwdm_metro_optical_ring.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
