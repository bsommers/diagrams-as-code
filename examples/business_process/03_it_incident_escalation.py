"""Example architecture: ITSM Major Incident Escalation & Response (BUSINESS_PROCESS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/business_process") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "03_it_incident_escalation.svg"
    png_file = out / "03_it_incident_escalation.png"
    readme_file = out / "03_it_incident_escalation_README.md"

    with Diagram("ITSM Major Incident Escalation & Response", theme="solarized_light") as diag:
        with diag.group("Monitoring") as g_1:
            alert_source = diag.add(Shape("alert_source", "Prometheus / Datadog Alert", icon="message", threshold="API Error Rate > 5%"))

        with diag.group("Incident Response") as g_2:
            l1_triage = diag.add(Shape("l1_triage", "L1 Operations NOC", icon="user", sla="5 min Response"))
            decision_gate = diag.add(Shape("decision_gate", "Severity 1 Assessment", icon="decision", criteria="Revenue Impacting"))
            decision_gate.below(l1_triage, margin=30)

        with diag.group("Swarm Engineering") as g_3:
            war_room = diag.add(Shape("war_room", "SRE Major Incident Bridge", icon="workflow", bridge="Zoom Incident Command"))

        with diag.group("Stakeholder Comms") as g_4:
            status_page = diag.add(Shape("status_page", "Public Status Page Update", icon="document", comms="status.company.com"))

        with diag.group("Post-Incident") as g_5:
            postmortem = diag.add(Shape("postmortem", "Blameless RCA Postmortem", icon="document", template="Corrective Action Plan"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)
        g_5.right_of(g_4, margin=80)

        # Establish inter-element connections with protocol annotations
        alert_source >> diag.edge("PagerDuty Trigger", style="solid") >> l1_triage
        l1_triage >> diag.edge("Evaluate Outage", style="solid") >> decision_gate
        decision_gate >> diag.edge("Escalate to Sev-1", style="solid") >> war_room
        war_room >> diag.edge("Publish Degradation", style="dashed") >> status_page
        war_room >> diag.edge("Resolve & File RCA", style="solid") >> postmortem

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("03_it_incident_escalation.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/business_process")
    build_diagram(dest)
