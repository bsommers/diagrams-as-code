"""Example architecture: Public Key Infrastructure (PKI) Certificate Hierarchy (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "04_pki_ca_hierarchy.svg"
    png_file = out / "04_pki_ca_hierarchy.png"
    readme_file = out / "04_pki_ca_hierarchy_README.md"

    with Diagram("Public Key Infrastructure (PKI) Certificate Hierarchy", theme="blueprint") as diag:
        with diag.group("Tier 0 Root Trust") as g_1:
            root_ca = diag.add(Shape("root_ca", "Offline Root CA", icon="vault", key="RSA 4096 / HSM", state="Air-Gapped"))

        with diag.group("Tier 1 Issuing Sub-CAs") as g_2:
            tls_ca = diag.add(Shape("tls_ca", "TLS Issuing CA", icon="key", validity="3 Years"))
            code_ca = diag.add(Shape("code_ca", "Code Signing CA", icon="key", validity="2 Years"))
            code_ca.below(tls_ca, margin=30)

        with diag.group("Revocation Services") as g_3:
            ocsp = diag.add(Shape("ocsp", "OCSP Responder", icon="server", protocol="OCSP / RFC 6960"))

        with diag.group("Tier 2 End Entities") as g_4:
            web_svr = diag.add(Shape("web_svr", "Production Web Host", icon="server", cert="Leaf TLS"))
            dev_ws = diag.add(Shape("dev_ws", "Developer Workstation", icon="laptop", cert="Developer Identity"))
            dev_ws.below(web_svr, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        root_ca >> diag.edge("Signs Sub-CA", style="solid") >> tls_ca
        root_ca >> diag.edge("Signs Sub-CA", style="solid") >> code_ca
        tls_ca >> diag.edge("Publishes CRL", style="solid") >> ocsp
        tls_ca >> diag.edge("Issues TLS Cert", style="solid") >> web_svr
        code_ca >> diag.edge("Issues Signing Cert", style="solid") >> dev_ws

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("04_pki_ca_hierarchy.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
