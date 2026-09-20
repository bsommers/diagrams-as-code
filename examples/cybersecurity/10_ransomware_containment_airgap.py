"""Example architecture: Ransomware Defense & Optical Air-Gapped Vault (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "10_ransomware_containment_airgap.svg"
    readme_file = out / "10_ransomware_containment_airgap_README.md"

    with Diagram("Ransomware Defense & Optical Air-Gapped Vault", theme="crimson") as diag:
        with diag.group("Primary Datacenter") as g_1:
            prod_san = diag.add(Shape("prod_san", "Production SAN Volume", icon="storage_array", storage="NVMe-oF"))
            backup_mgr = diag.add(Shape("backup_mgr", "Backup Master Node", icon="server", job="Continuous Snapshot"))
            backup_mgr.below(prod_san, margin=30)

        with diag.group("Air-Gap Boundary") as g_2:
            diode = diag.add(Shape("diode", "Optical Data Diode", icon="lock", physics="Transmit Only (Tx)"))

        with diag.group("Isolated Recovery Vault") as g_3:
            immutable_vault = diag.add(Shape("immutable_vault", "Immutable WORM Vault", icon="vault", retention="Object Lock Hardened"))
            clean_vm = diag.add(Shape("clean_vm", "Cleanroom Analysis VM", icon="malware_scan", scan="YARA Malware Heuristics"))
            clean_vm.below(immutable_vault, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        prod_san >> diag.edge("Snapshot Export", style="solid") >> backup_mgr
        backup_mgr >> diag.edge("Unidirectional Tx", style="solid") >> diode
        diode >> diag.edge("Zero-ACK Pulse", style="solid") >> immutable_vault
        immutable_vault >> diag.edge("Read-Only Mount", style="solid") >> clean_vm

        diag.render_svg(svg_file)
        diag.generate_readme("10_ransomware_containment_airgap.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
