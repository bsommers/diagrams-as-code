"""Example architecture: Automated Secrets Vault & Credential Rotation (CYBERSECURITY domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/cybersecurity") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "06_secrets_vault_rotation.svg"
    png_file = out / "06_secrets_vault_rotation.png"
    readme_file = out / "06_secrets_vault_rotation_README.md"

    with Diagram("Automated Secrets Vault & Credential Rotation", theme="emerald") as diag:
        with diag.group("Workload Layer") as g_1:
            k8s_app = diag.add(Shape("k8s_app", "Kubernetes Workload", icon="container", identity="SPIFFE / JWT"))

        with diag.group("Secrets Management Enclave") as g_2:
            vault_srv = diag.add(Shape("vault_srv", "HashiCorp Vault", icon="vault", storage="Integrated Raft"))
            hsm = diag.add(Shape("hsm", "FIPS 140-2 Level 3 HSM", icon="chip", function="Root Key Auto-Unwrap"))
            hsm.below(vault_srv, margin=30)

        with diag.group("Credential Lifecycle") as g_3:
            rotator = diag.add(Shape("rotator", "Rotation Controller", icon="key", cron="Every 24 Hours"))

        with diag.group("Protected Datastores") as g_4:
            prod_db = diag.add(Shape("prod_db", "Production Postgres", icon="database", ssl="Enforced TLS 1.3"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        k8s_app >> diag.edge("Authenticate Pod", style="solid") >> vault_srv
        vault_srv >> diag.edge("Master Key Unwrap", style="solid") >> hsm
        vault_srv >> diag.edge("Dynamic Lease Token", style="solid") >> k8s_app
        rotator >> diag.edge("Rotate Password", style="solid") >> prod_db
        rotator >> diag.edge("Commit New Secret", style="solid") >> vault_srv

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("06_secrets_vault_rotation.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cybersecurity")
    build_diagram(dest)
