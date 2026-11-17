"""Example architecture: Application Portfolio TIME Rationalisation (ENTERPRISE_ARCHITECTURE domain).

Gartner's TIME model on a two-by-two grid: business value rises upward and
technical fit rises to the right. Each application is placed in Tolerate,
Invest, Migrate or Eliminate, and the arrows show where a migrating or retiring
application's function and data go.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

W, H = 200.0, 58.0
ROW = 82.0
LEFT_X, RIGHT_A, RIGHT_B = 110.0, 490.0, 720.0
TOP_Y, BOTTOM_Y = 150.0, 520.0

QUADRANT = {
    "migrate": Style(fill="#FDF0D5", stroke="#B58900"),
    "invest": Style(fill="#E3F1DA", stroke="#5F8F2F"),
    "eliminate": Style(fill="#F9DEDC", stroke="#C0392B"),
    "tolerate": Style(fill="#E4ECF5", stroke="#268BD2"),
}


def app(diag: Diagram, label: str, x: float, y: float, lifecycle: str, **meta: str):
    """One application box, carrying its portfolio facts for the BOM."""
    return diag.shape(
        label, W, H, icon="server" if lifecycle != "eliminate" else "document",
        metadata={"lifecycle": lifecycle.capitalize(), **meta},
    ).at(x, y)


def diagram() -> Diagram:
    with Diagram("Application Portfolio Rationalisation (TIME Model)", theme="solarized_light") as diag:
        with diag.group("MIGRATE: high value, poor fit", child_style=QUADRANT["migrate"]):
            siebel = app(diag, "**Siebel CRM 8.1**\nend of support 2026", LEFT_X, TOP_Y, "migrate", owner="Sales", cost="$1.4M/yr")
            as400 = app(diag, "**AS/400 Order Entry**\nRPG, 2 SMEs left", LEFT_X, TOP_Y + ROW, "migrate", owner="Operations", cost="$0.9M/yr")
            notes = app(diag, "**Lotus Notes Workflows**\n140 databases", LEFT_X, TOP_Y + 2 * ROW, "migrate", owner="Shared Services", cost="$0.3M/yr")

        with diag.group("INVEST: high value, good fit", child_style=QUADRANT["invest"]):
            sfdc = app(diag, "**Salesforce Sales Cloud**", RIGHT_A, TOP_Y, "invest", owner="Sales", cost="$2.1M/yr")
            s4 = app(diag, "**SAP S/4HANA**", RIGHT_A, TOP_Y + ROW, "invest", owner="Finance", cost="$3.8M/yr")
            snow = app(diag, "**ServiceNow Platform**", RIGHT_A, TOP_Y + 2 * ROW, "invest", owner="IT", cost="$1.2M/yr")
            app(diag, "**Snowflake Data Cloud**", RIGHT_B, TOP_Y, "invest", owner="Data Office", cost="$0.8M/yr")
            app(diag, "**Workday HCM**", RIGHT_B, TOP_Y + ROW, "invest", owner="HR", cost="$1.0M/yr")

        with diag.group("ELIMINATE: low value, poor fit", child_style=QUADRANT["eliminate"]):
            access = app(diag, "**Access Pricing Tool**\nshadow IT", LEFT_X, BOTTOM_Y, "eliminate", owner="Marketing", cost="$0.05M/yr")
            crystal = app(diag, "**Crystal Reports Server**\n2,300 reports", LEFT_X, BOTTOM_Y + ROW, "eliminate", owner="Finance", cost="$0.2M/yr")
            app(diag, "**Custom FTP Gateway**\nunpatched", LEFT_X, BOTTOM_Y + 2 * ROW, "eliminate", owner="IT", cost="$0.1M/yr")

        with diag.group("TOLERATE: low value, good fit", child_style=QUADRANT["tolerate"]):
            cpq = app(diag, "**Pricing Rules Engine**", RIGHT_A, BOTTOM_Y, "tolerate", owner="Marketing", cost="$0.2M/yr")
            archive = app(diag, "**OpenText Archive**", RIGHT_A, BOTTOM_Y + ROW, "tolerate", owner="Records", cost="$0.4M/yr")
            app(diag, "**SharePoint 2019**", RIGHT_A, BOTTOM_Y + 2 * ROW, "tolerate", owner="Workplace", cost="$0.3M/yr")
            app(diag, "**Kronos Timekeeping**", RIGHT_B, BOTTOM_Y, "tolerate", owner="HR", cost="$0.2M/yr")

        siebel >> diag.edge("replace") >> sfdc
        as400 >> diag.edge("re-platform") >> s4
        notes >> diag.edge("rebuild") >> snow
        access >> diag.edge("absorb", style="dashed") >> cpq
        crystal >> diag.edge("archive", style="dashed") >> archive

        diag.text("**Business value**  higher ↑", size=13).at(LEFT_X - 25, TOP_Y - 95)
        diag.text("**Technical fit**  better →", size=13).at(RIGHT_B + W + 25, BOTTOM_Y + 2 * ROW + H + 50, anchor="top_right")
    return diag


def build_diagram(output_dir: Path | str = "output/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "03_application_portfolio_time")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/enterprise_architecture")
    build_diagram(dest)
