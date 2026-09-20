"""Example architecture: Enterprise DMZ Perimeter Defense (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "01_perimeter_defense_dmz.svg"
    png_file = out / "01_perimeter_defense_dmz.png"
    readme_file = out / "01_perimeter_defense_dmz_README.md"

    with Diagram("Enterprise DMZ Perimeter Defense", theme="crimson") as diag:
        with diag.group("Untrusted External") as g_1:
            client = diag.add(Shape("client", "Web Client", icon="laptop", origin="Internet"))

        with diag.group("DMZ Perimeter") as g_2:
            ext_fw = diag.add(Shape("ext_fw", "External Firewall", icon="firewall", policy="Drop Default"))
            proxy = diag.add(Shape("proxy", "Reverse Proxy", icon="server", port="443/TLS"))
            proxy.below(ext_fw, margin=30)
            waf = diag.add(Shape("waf", "WAF Inspector", icon="shield_check", rules="OWASP Core"))
            waf.below(proxy, margin=30)

        with diag.group("Trusted Corporate Core") as g_3:
            int_fw = diag.add(Shape("int_fw", "Internal Firewall", icon="lock", policy="Strict mTLS"))
            app = diag.add(Shape("app", "Application Cluster", icon="server", env="Production"))
            app.below(int_fw, margin=30)

        with diag.group("Protected Datastore") as g_4:
            db = diag.add(Shape("db", "Encrypted Database", icon="database", data="AES-256 at Rest"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        client >> diag.edge("HTTPS :443", style="solid") >> ext_fw
        ext_fw >> diag.edge("Clean Traffic", style="solid") >> proxy
        proxy >> diag.edge("Deep Inspect", style="solid") >> waf
        waf >> diag.edge("Sanitized Forward", style="solid") >> int_fw
        int_fw >> diag.edge("mTLS :8443", style="solid") >> app
        app >> diag.edge("TCP TLS :5432", style="solid") >> db

        diag.render_svg(svg_file)
        diag.render_png(png_file)
        diag.generate_readme("01_perimeter_defense_dmz.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
