"""Chiplet SoC package floorplan with UCIe die-to-die links (SEMICONDUCTOR domain).

Two compute chiplets and an I/O chiplet are joined by UCIe die-to-die links; four HBM
stacks sit beside the compute chiplets on the same package. The compute and I/O dies
can come from different process nodes, which is the point of the split: the I/O die and
the memory PHYs do not need the leading-edge logic node. Block sizes and the number
of tiles are illustrative, not any shipping product; the HBM interface is a wide
parallel bus, not UCIe.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"


def diagram() -> Diagram:
    with Diagram("Chiplet SoC floorplan with UCIe links (schematic, not to scale)", theme="paper") as diag:
        # package / interposer outline
        diag.polygon([(40, 70), (900, 70), (900, 600), (40, 600)],
                     style=Style(fill="#F6F6F2", stroke=INK, stroke_width=1.6, dash="8,4"), z=-6)
        diag.text("Package substrate / interposer", size=12, color="#555555").at(54, 80, anchor="top_left")

        def block(label, x, y, w, h, fill, icon=None):
            s = diag.shape(label, w, h, icon=icon, style=Style(fill=fill, stroke=INK, stroke_width=1.4)).at(x, y)
            return s

        hbm = [block("HBM", 70, 130, 100, 100, "#DCE8C8"), block("HBM", 70, 250, 100, 100, "#DCE8C8"),
               block("HBM", 770, 130, 100, 100, "#DCE8C8"), block("HBM", 770, 250, 100, 100, "#DCE8C8")]
        a = block("Compute chiplet A\nCPU cores + cache\n(leading-edge node)", 230, 120, 190, 230, "#C9D9F0", icon="chip")
        b = block("Compute chiplet B\nCPU cores + cache\n(leading-edge node)", 500, 120, 190, 230, "#C9D9F0", icon="chip")
        io = block("I/O chiplet\nPCIe / CXL, DDR, Ethernet\n(mature node)", 320, 440, 280, 110, "#F2DDB8", icon="gateway")

        # HBM interface (wide parallel bus, not UCIe)
        hbm[0] >> diag.edge("HBM PHY", width=2.5, two_way=True) >> a.anchor("left", 0.261)
        hbm[1] >> diag.edge(width=2.5, two_way=True) >> a.anchor("left", 0.783)
        b.anchor("right", 0.261) >> diag.edge("HBM PHY", width=2.5, two_way=True) >> hbm[2]
        b.anchor("right", 0.783) >> diag.edge(width=2.5, two_way=True) >> hbm[3]
        # UCIe die-to-die links
        a >> diag.edge("UCIe", width=4, two_way=True, color="#B03060") >> b
        a.anchor("bottom", 0.7) >> diag.edge("UCIe", width=4, two_way=True, color="#B03060") >> io.anchor("top", 0.25)
        b.anchor("bottom", 0.3) >> diag.edge("UCIe", width=4, two_way=True, color="#B03060") >> io.anchor("top", 0.75)
        # off-package I/O
        out = diag.point(460, 640)
        io.anchor("bottom", 0.5) >> diag.edge("PCIe / CXL / DDR / Ethernet", width=2.5, two_way=True) >> out
        diag.text("UCIe: die-to-die link (advanced or standard package); HBM: stacked DRAM on a wide parallel interface",
                  size=11.5, color="#444444").at(470, 665, anchor="top_center")
        diag.caption("**Figure 9:** Chiplet SoC floorplan. Illustrative partitioning and not to scale.", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/semiconductor") -> Path:
    return render_all(diagram(), output_dir, "09_chiplet_soc_floorplan")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/semiconductor")
    build_diagram(dest)
