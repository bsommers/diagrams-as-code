"""Example architecture: Auto-Laid-Out Spine-Leaf Fabric (DATACENTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram(
        "Auto-Laid-Out Spine-Leaf Fabric", theme="blueprint", layout="auto", direction="TB"
    ) as diag:
        with diag.group("Spine") as spine:
            spine_1 = diag.shape("Spine 1", icon="switch")
            spine_2 = diag.shape("Spine 2", icon="switch")
        with diag.group("Leaf") as leaf:
            leaf_1 = diag.shape("Leaf 1", icon="switch")
            leaf_2 = diag.shape("Leaf 2", icon="switch")
            leaf_3 = diag.shape("Leaf 3", icon="switch")
        with diag.group("Racks") as racks:
            rack_a = diag.shape("Rack A", icon="server")
            rack_b = diag.shape("Rack B", icon="server")
            rack_c = diag.shape("Rack C", icon="server")

        for spine_node in (spine_1, spine_2):
            for leaf_node in (leaf_1, leaf_2, leaf_3):
                spine_node >> diag.edge("40G") >> leaf_node

        leaf_1 >> diag.edge("10G") >> rack_a
        leaf_2 >> diag.edge("10G") >> rack_b
        leaf_3 >> diag.edge("10G") >> rack_c

    return diag


def build_diagram(output_dir: Path | str = "output/datacenter") -> Path:
    return render_all(diagram(), output_dir, "11_auto_spine_leaf")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/datacenter")
    build_diagram(dest)
