"""Example architecture: Datacenter Power Distribution & 2N UPS (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Datacenter Power Distribution & 2N UPS", theme="cyber_slate") as diag:
        with diag.group("Utility Ingress") as g_1:
            utility = diag.add(Shape("utility", "Utility Grid Feeder (13.8kV)", icon="ups", capacity="2.5 MVA"))

        with diag.group("Backup Power") as g_2:
            gen_ats = diag.add(Shape("gen_ats", "Diesel Generator + ATS", icon="ups", rating="2000 kW Standby"))

        with diag.group("UPS Train A") as g_3:
            ups_a = diag.add(Shape("ups_a", "Static Online UPS System A", icon="ups", runtime="15 min Lithium-Ion"))

        with diag.group("UPS Train B") as g_4:
            ups_b = diag.add(Shape("ups_b", "Static Online UPS System B", icon="ups", runtime="15 min Lithium-Ion"))

        with diag.group("Distribution A") as g_5:
            pdu_a = diag.add(Shape("pdu_a", "Floor PDU A (480V to 208V)", icon="ups", breakers="42 Circuits"))

        with diag.group("Distribution B") as g_6:
            pdu_b = diag.add(Shape("pdu_b", "Floor PDU B (480V to 208V)", icon="ups", breakers="42 Circuits"))

        with diag.group("Server Floor") as g_7:
            rack_feed = diag.add(Shape("rack_feed", "Dual-Corded Server Racks", icon="server_rack", power="2x 30A 208V Feeds"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)
        g_5.right_of(g_4, margin=80)
        g_6.right_of(g_5, margin=80)
        g_7.right_of(g_6, margin=80)

        # Establish inter-element connections with protocol annotations
        utility >> diag.edge("Normal Power Feed", style="solid") >> gen_ats
        gen_ats >> diag.edge("Conditioned Power", style="solid") >> ups_a
        gen_ats >> diag.edge("Conditioned Power", style="solid") >> ups_b
        ups_a >> diag.edge("Isolated Feed A", style="solid") >> pdu_a
        ups_b >> diag.edge("Isolated Feed B", style="solid") >> pdu_b
        pdu_a >> diag.edge("PDU Whip A", style="solid") >> rack_feed
        pdu_b >> diag.edge("PDU Whip B", style="dashed") >> rack_feed

    return diag


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    return render_all(diagram(), output_dir, "04_power_distribution_ups")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
