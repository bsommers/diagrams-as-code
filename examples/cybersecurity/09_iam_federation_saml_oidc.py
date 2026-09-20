"""Example architecture: Enterprise IAM Federation & SSO Pipeline (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "09_iam_federation_saml_oidc.svg"
    png_file = out / "09_iam_federation_saml_oidc.png"
    readme_file = out / "09_iam_federation_saml_oidc_README.md"

    with Diagram("Enterprise IAM Federation & SSO Pipeline", theme="monochrome") as diag:
        with diag.group("User Principal") as g_1:
            user_node = diag.add(Shape("user_node", "Corporate User", icon="user", browser="Chrome / Edge"))
            fido_mfa = diag.add(Shape("fido_mfa", "Hardware Security Key", icon="mobile", standard="FIDO2 / WebAuthn"))
            fido_mfa.below(user_node, margin=30)

        with diag.group("Identity Provider Tier") as g_2:
            idp_cloud = diag.add(Shape("idp_cloud", "Cloud IdP (Okta/Entra)", icon="key", standards="SAML 2.0 & OIDC"))
            directory = diag.add(Shape("directory", "Enterprise LDAP/AD", icon="database", sync="SCIM Provisioning"))
            directory.below(idp_cloud, margin=30)

        with diag.group("Service Providers") as g_3:
            saas_app = diag.add(Shape("saas_app", "SaaS Business App", icon="cloud", auth="SAML Assertion"))
            portal_app = diag.add(Shape("portal_app", "Internal Microservice", icon="server", auth="OAuth2 / OIDC JWT"))
            portal_app.below(saas_app, margin=30)

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        user_node >> diag.edge("SSO Login Request", style="solid") >> idp_cloud
        idp_cloud >> diag.edge("Challenge MFA", style="solid") >> fido_mfa
        fido_mfa >> diag.edge("FIDO Attestation", style="solid") >> idp_cloud
        idp_cloud >> diag.edge("Verify Group Membership", style="solid") >> directory
        idp_cloud >> diag.edge("SAML Assertion Post", style="solid") >> saas_app
        idp_cloud >> diag.edge("ID Token / PKCE", style="solid") >> portal_app

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("09_iam_federation_saml_oidc.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
