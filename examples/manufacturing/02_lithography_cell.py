"""Example architecture: Lithography Cell with Overlay & CD Feedback (MANUFACTURING domain).

A coater/developer track is linked in-line to an exposure scanner. Wafers
arrive in a FOUP, are primed, coated and soft-baked on the track, exposed in
the scanner, then post-exposure baked and developed. Reticles come from a
stocker after a particle check. After develop, overlay and CD metrology feed a
run-to-run controller that sends per-lot dose, focus and alignment
corrections back to the scanner.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all

ROW = 130.0  # vertical gap between the rows of the cell


def diagram() -> Diagram:
    with Diagram("Lithography Cell with Overlay & CD Feedback", theme="blueprint") as diag:
        with diag.group("Coater / Developer Track") as g_track:
            load_port = diag.shape("FOUP Load Port", icon="queue", metadata={"carrier": "25-wafer FOUP"})
            coat = diag.shape("Prime, Spin Coat\n& Soft Bake", icon="robot", metadata={"modules": "HMDS / coat / bake"})
            develop = diag.shape("PEB & Develop", icon="robot", metadata={"modules": "PEB / develop / hard bake"})
            coat.below(load_port, margin=ROW)
            develop.below(coat, margin=ROW)

        with diag.group("Exposure Scanner") as g_scan:
            reticle_stage = diag.shape("Reticle Stage", icon="chip", metadata={"motion": "synchronous scan"})
            wafer_stage = diag.shape("Wafer Stage\nAlign, Level, Expose", icon="chip", metadata={"source": "ArF immersion or EUV"})
            wafer_stage.below(reticle_stage, margin=ROW)

        with diag.group("Reticle Handling") as g_ret:
            ret_inspect = diag.shape("Reticle Particle\nInspection", icon="vision", metadata={"check": "before load"})
            stocker = diag.shape("Reticle Stocker", icon="storage", metadata={"carrier": "reticle pod"})
            stocker.right_of(ret_inspect, margin=70)

        with diag.group("Litho APC") as g_apc:
            r2r = diag.shape("Run-to-Run\nController", 170, icon="workflow", metadata={"model": "EWMA per context"})
            mes = diag.shape("MES / Recipe\nManagement", icon="server", metadata={"role": "lot dispatch"})
            mes.right_of(r2r, margin=70)

        with diag.group("Litho Metrology") as g_metro:
            cd_sem = diag.shape("CD-SEM", icon="vision", metadata={"measures": "critical dimension"})
            overlay = diag.shape("Overlay Metrology", icon="vision", metadata={"method": "image or diffraction based"})
            overlay.right_of(cd_sem, margin=70)

        g_track.at(60.0, 80.0)
        g_scan.at(370.0, 80.0)
        g_ret.at(680.0, 80.0)
        g_apc.at(680.0, 80.0 + ROW + 60)
        g_metro.at(680.0, 80.0 + 2 * (ROW + 60))

        load_port >> diag.edge() >> coat
        coat >> diag.edge("interface") >> wafer_stage
        wafer_stage.anchor("bottom", 0.5) >> diag.edge("exposed") >> develop.anchor("right", 0.25)
        stocker >> diag.edge("pod") >> ret_inspect
        ret_inspect >> diag.edge("load") >> reticle_stage
        develop.anchor("right", 0.75) >> diag.edge("developed lot") >> cd_sem.anchor("left", 0.75)
        cd_sem >> diag.edge("sampled wafers") >> overlay
        cd_sem.anchor("top", 0.78) >> diag.edge("CD") >> r2r.anchor("bottom", 0.6)
        overlay.anchor("top", 0.2) >> diag.edge("overlay") >> r2r.anchor("bottom", 0.9)
        r2r >> diag.edge("dose, focus, alignment", style="dashed") >> wafer_stage
        mes >> diag.edge("lot context") >> r2r

    return diag


def build_diagram(output_dir: Path | str = "output/manufacturing") -> Path:
    return render_all(diagram(), output_dir, "02_lithography_cell")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/manufacturing")
    build_diagram(dest)
