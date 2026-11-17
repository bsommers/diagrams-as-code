"""Example architecture: Core Systems Transition Roadmap with Plateaus (ENTERPRISE_ARCHITECTURE domain).

A TOGAF-style migration plan drawn as a paper figure. Each column is a
plateau, a stable state of the architecture; each row follows one domain from
the baseline to the target. Work packages between the columns carry the
architecture from one plateau to the next. Shaded blocks are new in that
plateau and dashed blocks are being retired.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

LANES = ("Customer", "Policy core", "Data", "Integration")
#: Each plateau: its name, and per lane (label, state) with state in {"kept", "new", "retiring"}.
PLATEAUS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Baseline 2025", (("Siebel CRM 8.1", "retiring"), ("Mainframe policy admin", "kept"),
                       ("Nightly ETL to EDW", "kept"), ("Point-to-point + ESB", "retiring"))),
    ("Plateau 1: 2026", (("Salesforce CRM", "new"), ("Mainframe policy admin", "retiring"),
                         ("EDW + cloud data lake", "new"), ("API gateway + ESB", "new"))),
    ("Plateau 2: 2027", (("Salesforce CRM", "kept"), ("Guidewire PolicyCenter", "new"),
                         ("Lakehouse (EDW retired)", "new"), ("Event streaming", "new"))),
    ("Target 2028", (("Salesforce + service AI", "new"), ("Guidewire Cloud", "new"),
                     ("Governed lakehouse + MDM", "new"), ("Event-driven APIs", "kept"))),
)
WORK_PACKAGES = (
    ("**WP1**\nCRM and API\nfoundation", "$4.2M, 9 months"),
    ("**WP2**\nPolicy core\nreplacement", "$11.8M, 14 months"),
    ("**WP3**\nDecommission\nand optimise", "$2.6M, 6 months"),
)

STATE = {
    "kept": Style(fill="#FFFFFF"),
    "new": Style(fill="#DADADA"),
    "retiring": Style(fill="#FFFFFF", dash="4,3"),
}
W, H = 190.0, 50.0
LANE_PITCH = 76.0
WP_W, WP_H = 124.0, 92.0
PAD = 22.0
GAP = WP_W + 2 * 40.0
X0, Y0 = 170.0, 110.0
PITCH = W + 2 * PAD + GAP


def diagram() -> Diagram:
    with Diagram("Core Systems Transition Roadmap: Baseline to Target", theme="paper") as diag:
        for lane, name in enumerate(LANES):
            diag.text(f"**{name}**", size=13).at(X0 - PAD - 18.0, Y0 + lane * LANE_PITCH + H / 2, anchor="right_center")

        plateaus = []
        for col, (title, blocks) in enumerate(PLATEAUS):
            x = X0 + col * PITCH
            with diag.group(title, padding=PAD, header_height=34.0) as plateau:
                for lane, (label, state) in enumerate(blocks):
                    diag.shape(label, W, H, style=STATE[state],
                               metadata={"plateau": title, "domain": LANES[lane], "state": state}).at(
                        x, Y0 + lane * LANE_PITCH)
            plateaus.append(plateau)

        # Level with the middle of the plateau frames, so the arrows run straight.
        mid_y = (Y0 - PAD - 34.0 + Y0 + 3 * LANE_PITCH + H + PAD) / 2
        for col, (label, cost) in enumerate(WORK_PACKAGES):
            x = X0 + col * PITCH + W + PAD + 40.0
            wp = diag.shape(label, WP_W, WP_H, style=Style(double=3.0),
                            metadata={"type": "Work Package", "budget": cost}).at(x, mid_y - WP_H / 2)
            plateaus[col] >> diag.edge(width=1.4) >> wp
            wp >> diag.edge(width=1.4) >> plateaus[col + 1]
            diag.text(f"*{cost}*", size=11).at(x + WP_W / 2, mid_y + WP_H / 2 + 8.0, anchor="top_center")

        legend_y = Y0 + 4 * LANE_PITCH + 30.0
        for i, (state, style) in enumerate(STATE.items()):
            diag.shape(state.capitalize(), 110.0, 30.0, style=style,
                       metadata={"legend": "state"}).at(X0 + i * 130.0, legend_y)

        diag.caption(
            "**Figure 2:** Plateaus are stable states; double-bordered work packages move between them",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "08_transition_roadmap")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/enterprise_architecture")
    build_diagram(dest)
