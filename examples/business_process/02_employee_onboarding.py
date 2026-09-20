"""Example architecture: Corporate Employee Onboarding Lifecycle (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "02_employee_onboarding.svg"
    png_file = out / "02_employee_onboarding.png"
    readme_file = out / "02_employee_onboarding_README.md"

    with Diagram("Corporate Employee Onboarding Lifecycle", theme="nord") as diag:
        with diag.group("Talent Acquisition") as g_1:
            candidate = diag.add(Shape("candidate", "New Hire Employee", icon="user", role="Software Engineer"))

        with diag.group("Human Resources") as g_2:
            hr_intake = diag.add(Shape("hr_intake", "HR Workday System", icon="document", record="Employee ID Creation"))

        with diag.group("IT Operations") as g_3:
            it_provision = diag.add(Shape("it_provision", "IT Asset Provisioning", icon="laptop", device="MacBook Pro + YubiKey"))
            iam_setup = diag.add(Shape("iam_setup", "Okta Identity & Groups", icon="shield", rbac="Engineering Team Role"))
            iam_setup.below(it_provision, margin=30)

        with diag.group("Physical Security") as g_4:
            badge_access = diag.add(Shape("badge_access", "Facilities Physical Badge", icon="sensor", zones="HQ Access Granted"))

        with diag.group("Finance & Payroll") as g_5:
            payroll = diag.add(Shape("payroll", "ADP Payroll Enrolment", icon="storage", direct_deposit="Active"))

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)
        g_5.right_of(g_4, margin=50)

        # Establish inter-element connections with protocol annotations
        candidate >> diag.edge("Signed Offer Letter", style="solid") >> hr_intake
        hr_intake >> diag.edge("Trigger Equipment Dispatch", style="solid") >> it_provision
        hr_intake >> diag.edge("Create Cloud Account", style="solid") >> iam_setup
        hr_intake >> diag.edge("Issue Security Card", style="solid") >> badge_access
        hr_intake >> diag.edge("Enroll Benefits", style="solid") >> payroll
        it_provision >> diag.edge("Deliver Workstation", style="dashed") >> candidate

        diag.render_svg(svg_file)
        diag.render_png(png_file)
        diag.generate_readme("02_employee_onboarding.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
