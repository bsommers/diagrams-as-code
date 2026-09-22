"""Example architecture: AI Safety Guardrails & Jailbreak Defense (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("AI Safety Guardrails & Jailbreak Defense", theme="pastel_light") as diag:
        with diag.group("Ingress Gate") as g_1:
            user_input = diag.add(Shape("user_input", "Untrusted User Prompt", icon="user", risk="Potential Jailbreak"))

        with diag.group("Security Filter") as g_2:
            guard_in = diag.add(Shape("guard_in", "NeMo Input Guardrail", icon="firewall", check="Prompt Injection / Jailbreak"))
            pii_mask = diag.add(Shape("pii_mask", "PII Redaction Engine", icon="shield", compliance="HIPAA / GDPR"))
            pii_mask.below(guard_in, margin=30)

        with diag.group("Model Execution") as g_3:
            llm_core = diag.add(Shape("llm_core", "Core Reasoning LLM", icon="model", temperature="0.2"))

        with diag.group("Egress Filter") as g_4:
            guard_out = diag.add(Shape("guard_out", "Toxicity & Hallucination Filter", icon="shield", metric="Faithfulness Score"))

        with diag.group("Compliance Store") as g_5:
            audit_log = diag.add(Shape("audit_log", "Security Audit Log", icon="storage", retention="7 Years Immutable"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=80)
        g_3.right_of(g_2, margin=80)
        g_4.right_of(g_3, margin=80)
        g_5.right_of(g_4, margin=80)

        # Establish inter-element connections with protocol annotations
        user_input >> diag.edge("Raw Prompt", style="solid") >> guard_in
        guard_in >> diag.edge("Sanitized Input", style="solid") >> pii_mask
        pii_mask >> diag.edge("Anonymized Prompt", style="solid") >> llm_core
        llm_core >> diag.edge("Draft Response", style="solid") >> guard_out
        guard_out >> diag.edge("Log Prompt & Evaluation", style="dashed") >> audit_log
        guard_out >> diag.edge("Verified Safe Response", style="solid") >> user_input

    return diag


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    return render_all(diagram(), output_dir, "08_ai_guardrails_safety_eval")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
