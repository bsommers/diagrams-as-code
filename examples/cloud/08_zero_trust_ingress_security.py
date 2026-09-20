"""Example architecture: Zero-Trust Perimeter & DMZ Security Ingress (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "08_zero_trust_ingress_security.svg"
    png_file = out / "08_zero_trust_ingress_security.png"
    readme_file = out / "08_zero_trust_ingress_security_README.md"

    with Diagram("Zero-Trust Perimeter & DMZ Security Ingress", theme="cyber_slate") as diag:
        with diag.group("Untrusted Zone") as g_1:
            internet = diag.add(Shape("internet", "External Traffic", icon="user", origin="Public Internet"))

        with diag.group("Perimeter Zone") as g_2:
            waf = diag.add(Shape("waf", "Edge Cloud WAF", icon="firewall", ddos="L3-L7 Defense"))

        with diag.group("DMZ Boundary") as g_3:
            fw_app = diag.add(Shape("fw_app", "Stateful NGFW Appliance", icon="firewall", ips="Snort Engine"))

        with diag.group("DMZ Zone") as g_4:
            dmz_proxy = diag.add(Shape("dmz_proxy", "DMZ Reverse Proxy", icon="api_gateway", tls="Terminate mTLS"))

        with diag.group("Identity Provider") as g_5:
            auth_idp = diag.add(Shape("auth_idp", "Enterprise IdP Okta", icon="shield", mfa="FIDO2"))

        with diag.group("Internal Trust Zone") as g_6:
            backend = diag.add(Shape("backend", "Private App Cluster", icon="server", subnet="10.0.10.0/24"))
            vault = diag.add(Shape("vault", "HashiCorp Vault", icon="storage", keys="Hardware HSM"))
            vault.below(backend, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)
        g_6.right_of(g_5, margin=50)

        # Establish inter-element connections with protocol annotations
        internet >> diag.edge("HTTPS Ingress", style="solid") >> waf
        waf >> diag.edge("Sanitized Packets", style="solid") >> fw_app
        fw_app >> diag.edge("Forward to DMZ", style="solid") >> dmz_proxy
        dmz_proxy >> diag.edge("Verify JWT", style="dashed") >> auth_idp
        dmz_proxy >> diag.edge("Internal mTLS", style="solid") >> backend
        backend >> diag.edge("Fetch Secret", style="dashed") >> vault

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("08_zero_trust_ingress_security.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
