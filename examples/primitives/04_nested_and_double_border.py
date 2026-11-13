"""Shapes nested in shapes, and double borders (PRIM-04)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Nesting and double borders", theme="paper") as diag:
        cpu = diag.shape("**Processor**", 330, 190, label_position="top", style=Style(fill="#F2F2F2")).at(60, 60)
        core0 = diag.shape("Core 0", 120, 110, label_position="top").inside(cpu, "top_left", 20, 50)
        core1 = diag.shape("Core 1", 120, 110, label_position="top").inside(cpu, "top_right", -20, 50)
        l1a = diag.shape("L1", 80, 34).inside(core0, "bottom_center", 0, -14)
        l1b = diag.shape("L1", 80, 34).inside(core1, "bottom_center", 0, -14)

        cache = diag.shape("Shared L3 cache", 330, 54, style=Style(double=4)).below(cpu, margin=50)
        vault = diag.shape("Secure\nenclave", 120, 80, style=Style(double=5, radius=10)).right_of(cpu, margin=70)

        # Straight down through the borders they are nested in.
        l1a >> diag.edge(width=1.0) >> cache.anchor("top", 80 / 330)
        l1b >> diag.edge(width=1.0) >> cache.anchor("top", 250 / 330)
        core1 >> diag.edge("attest") >> vault
        diag.caption("**Figure 4:** Boxes in boxes; a double border marks a trust boundary", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "04_nested_and_double_border")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
