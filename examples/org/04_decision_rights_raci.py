"""Example: Decision rights (RACI by role) (ORGANISATION domain).

A RACI matrix for six recurring engineering decisions. Every row has exactly one
Accountable role (checked when the diagram is built) and at least one Responsible.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

ROLES = ("Product\nOwner", "Eng\nManager", "Tech\nLead", "Architect", "Security")
#: decision -> one letter per role: R responsible, A accountable, C consulted, I informed, - none.
DECISIONS = (
    ("Prioritise the quarterly roadmap", "ACCCI"),
    ("Approve a new third-party dependency", "-ARCC"),
    ("Choose the service architecture", "ICRAC"),
    ("Hire into the team", "CARII"),
    ("Release to production", "ICAIC"),
    ("Accept a security exception", "IIC-A"),
)
LOOK = {
    "R": ("Responsible", Style(fill="#D9E3F5", stroke="#2F4B86")),
    "A": ("Accountable", Style(fill="#F6D9CC", stroke="#B0502E", stroke_width=2.5)),
    "C": ("Consulted", Style(fill="#FBF0C8", stroke="#B8860B")),
    "I": ("Informed", Style(fill="#EEF0F3", stroke="#6B7280")),
    "-": ("", Style(fill="#FFFFFF", stroke="#D5D9DE")),
}
LABEL_W, CW, CH, GAP = 300.0, 82.0, 48.0, 8.0
X0, Y0 = 60.0, 130.0


def check() -> None:
    for name, row in DECISIONS:
        assert len(row) == len(ROLES), name
        assert row.count("A") == 1, f"{name}: needs exactly one Accountable"
        assert "R" in row or "A" in row, name


def diagram() -> Diagram:
    check()
    with Diagram("Decision rights: RACI by role", theme="paper") as diag:
        for j, role in enumerate(ROLES):
            diag.shape(role, CW, 50, style=Style(fill="#2F4B86", stroke="#2F4B86", text_color="#FFFFFF")).at(
                X0 + LABEL_W + GAP + j * (CW + GAP), Y0 - 62)
        for i, (name, row) in enumerate(DECISIONS):
            y = Y0 + i * (CH + GAP)
            diag.shape(name, LABEL_W, CH, style=Style(fill="#F4F6F9", stroke="#6B7280")).at(X0, y)
            for j, letter in enumerate(row):
                diag.shape("" if letter == "-" else letter, CW, CH, style=LOOK[letter][1]).at(
                    X0 + LABEL_W + GAP + j * (CW + GAP), y)
        # Legend row.
        ly = Y0 + len(DECISIONS) * (CH + GAP) + 24
        for k, letter in enumerate("RACI"):
            word, style = LOOK[letter]
            diag.shape(f"{letter}  {word}", 150, 36, style=style).at(X0 + k * 164, ly)
        diag.text("Rule: exactly one A per decision; the A may also do the work (shown as A).",
                  size=12).at(X0, ly + 54)
    return diag


def build_diagram(output_dir: Path | str = "examples/org") -> Path:
    return render_all(diagram(), output_dir, "04_decision_rights_raci")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/org"))
