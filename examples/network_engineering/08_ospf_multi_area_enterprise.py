"""Example architecture: OSPF Multi-Area Enterprise Routing (NETWORK_ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/network_engineering") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "08_ospf_multi_area_enterprise.svg"
    png_file = out / "08_ospf_multi_area_enterprise.png"
    readme_file = out / "08_ospf_multi_area_enterprise_README.md"

    with Diagram("OSPF Multi-Area Enterprise Routing", theme="monochrome") as diag:
        with diag.group("Area 0 Backbone") as g_1:
            bb_rtr1 = diag.add(Shape("bb_rtr1", "Backbone Router A", icon="core_router", role="Backbone Router"))
            bb_rtr2 = diag.add(Shape("bb_rtr2", "Backbone Router B", icon="core_router", role="Backbone Router"))
            bb_rtr2.below(bb_rtr1, margin=30)

        with diag.group("Area 10 Campus Spoke") as g_2:
            abr_campus = diag.add(Shape("abr_campus", "Area 10 ABR", icon="core_router", lsa="Type 3 Summary LSA"))
            campus_sw = diag.add(Shape("campus_sw", "Campus Distribution", icon="switch", area="Totally Stubby"))
            campus_sw.below(abr_campus, margin=30)

        with diag.group("Area 20 Datacenter") as g_3:
            asbr_dc = diag.add(Shape("asbr_dc", "Datacenter ASBR", icon="core_router", redist="BGP External -> Type 5 LSA"))

        with diag.group("External Autonomous System") as g_4:
            bgp_peer = diag.add(Shape("bgp_peer", "External BGP Peer", icon="bgp", asn="AS 65100"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        bb_rtr1 >> diag.edge("Area 0 Mesh", style="solid") >> bb_rtr2
        bb_rtr1 >> diag.edge("Area 0 Trunk", style="solid") >> abr_campus
        abr_campus >> diag.edge("Area 10 Internal", style="solid") >> campus_sw
        bb_rtr2 >> diag.edge("Area 0 Trunk", style="solid") >> asbr_dc
        asbr_dc >> diag.edge("eBGP Redistribution", style="solid") >> bgp_peer

        diag.render_svg(svg_file)
        diag.render_png(png_file)
        diag.generate_readme("08_ospf_multi_area_enterprise.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/network_engineering")
    build_diagram(dest)
