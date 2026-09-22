"""Example architecture: Metro Disaster Recovery Datacenter Pair (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Metro Disaster Recovery Datacenter Pair", theme="crimson") as diag:
        with diag.group("East Datacenter (Active)") as g_1:
            dc_east_compute = diag.add(Shape("dc_east_compute", "Primary DC Compute Farm", icon="cluster", vms="2,500 Production VMs"))
            dc_east_san = diag.add(Shape("dc_east_san", "Primary All-Flash Array", icon="storage_array", rpo="Zero Data Loss"))
            dc_east_san.below(dc_east_compute, margin=30)

        with diag.group("Inter-DC Transport") as g_2:
            dwdm = diag.add(Shape("dwdm", "Dark Fiber DWDM Metro Link", icon="router", latency="0.8ms Round-Trip"))

        with diag.group("West Datacenter (Standby)") as g_3:
            dc_west_san = diag.add(Shape("dc_west_san", "Standby Array Replica", icon="storage_array", sync="Synchronous Mirror"))
            dc_west_compute = diag.add(Shape("dc_west_compute", "Standby Recovery Compute", icon="cluster", hosts="Cold Standby Farm"))
            dc_west_compute.below(dc_west_san, margin=30)

        with diag.group("DR Automation") as g_4:
            dr_orchestrator = diag.add(Shape("dr_orchestrator", "Disaster Recovery Orchestrator", icon="workflow", failover="1-Click Runbook"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)

        # Establish inter-element connections with protocol annotations
        dc_east_compute >> diag.edge("SAN Fiber Channel", style="solid") >> dc_east_san
        dc_east_san >> diag.edge("Synchronous Replication", style="solid") >> dwdm
        dwdm >> diag.edge("DWDM Wavelength", style="solid") >> dc_west_san
        dr_orchestrator >> diag.edge("Automated Power On", style="dashed") >> dc_west_compute
        dr_orchestrator >> diag.edge("Promote LUNs", style="dashed") >> dc_west_san

    return diag


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    return render_all(diagram(), output_dir, "07_disaster_recovery_datacenter_pair")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
