"""Molecular orbital diagrams for H2 and O2, filled from the electron count.

Each molecule's occupancy is computed, not drawn by hand: the valence electrons are
poured into the molecular orbitals from the lowest level up, filling degenerate
orbitals singly with parallel spins first (Hund's rule) before pairing. The bond order
is $(n_{bonding} - n_{antibonding})/2$. For $\\ce{H2}$ two electrons fill
$\\sigma_{1s}$ (order 1, diamagnetic). For $\\ce{O2}$ the 12 valence electrons fill up to
$\\pi^*_{2p}$, leaving two unpaired electrons in the degenerate pair (order 2,
paramagnetic), which the simple Lewis structure cannot show. The 2s-2p mixing that
reorders $\\sigma_{2p}$ and $\\pi_{2p}$ in lighter molecules such as $\\ce{N2}$ is absent
for oxygen, so $\\sigma_{2p}$ lies below $\\pi_{2p}$.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK, RED, BLUE, GREY = "#111111", "#9C2F2F", "#1F2F57", "#999999"

# (label, y, number of degenerate orbitals, bonding?) from low energy up; y is pixels (down is low energy).
H2_MO = [("$\\sigma_{1s}$", 370, 1, True), ("$\\sigma^*_{1s}$", 230, 1, False)]
O2_MO = [("$\\sigma_{2s}$", 520, 1, True), ("$\\sigma^*_{2s}$", 440, 1, False),
         ("$\\sigma_{2p}$", 380, 1, True), ("$\\pi_{2p}$", 320, 2, True),
         ("$\\pi^*_{2p}$", 215, 2, False), ("$\\sigma^*_{2p}$", 150, 1, False)]


def fill(orbitals: list[tuple[str, float, int, bool]], electrons: int) -> list[list[list[str]]]:
    """Occupancy per level: a list (per level) of lists (per orbital) of spins.

    Degenerate orbitals take one electron each (spin up) before any is paired.
    """
    out: list[list[list[str]]] = []
    for _, _, n, _ in orbitals:
        slots: list[list[str]] = [[] for _ in range(n)]
        for s in slots:
            if electrons > 0:
                s.append("u")
                electrons -= 1
        for s in slots:
            if electrons > 0:
                s.append("d")
                electrons -= 1
        out.append(slots)
    return out


def arrow(diag, x, y, up, color=INK):
    y0, y1 = (y - 2, y - 24) if up else (y - 24, y - 2)
    diag.connect((x, y0), (x, y1), routing="direct", width=1.6, head="stealth", arrow_size=0.8, color=color)


def level(diag, cx, y, w=36, color=INK, width=2.2):
    diag.polyline([(cx - w / 2, y), (cx + w / 2, y)], style=Style(stroke=color, stroke_width=width))


def place_electrons(diag, cx, y, spins, color=INK):
    if len(spins) == 2:
        arrow(diag, cx - 5, y, True, color)
        arrow(diag, cx + 5, y, False, color)
    elif spins:
        arrow(diag, cx, y, spins[0] == "u", color)


def molecule(diag, cx, ao_dx, ao_levels, mo, occupancy, tag, label_dx=70):
    """Draw one diagram: atomic orbitals at cx -/+ ao_dx, molecular orbitals at cx."""
    spacing = 52
    mo_ends = []
    for (name, y, n, bonding), occ in zip(mo, occupancy):
        xs = [cx] if n == 1 else [cx - spacing / 2, cx + spacing / 2]
        for x, spins in zip(xs, occ):
            level(diag, x, y, color=BLUE if bonding else RED)
            place_electrons(diag, x, y, spins)
        mo_ends.append((y, xs))
        diag.text(name, size=14, color=BLUE if bonding else RED).at(cx, y + 8, anchor="top_center")
    # Atomic orbitals on both sides.
    for side in (-1, 1):
        ax = cx + side * ao_dx
        for (name, y, n_orb, electrons) in ao_levels:
            xs = [ax] if n_orb == 1 else [ax - 22, ax, ax + 22]
            width = 36 if n_orb == 1 else 16
            for j, x in enumerate(xs):
                level(diag, x, y, w=width)
            for j, spins in enumerate(fill([("", y, n_orb, True)], electrons)[0]):
                place_electrons(diag, xs[j], y, spins)
            diag.text(name, size=12).at(ax, y + 14, anchor="top_center")
    return mo_ends



def dashed(diag, a, b):
    diag.polyline([a, b], style=Style(stroke=GREY, stroke_width=1.0, dash="4,3"), obstacle=False)


def diagram() -> Diagram:
    with Diagram("Molecular orbitals of H2 and O2", theme="paper") as diag:
        # Energy axis.
        diag.connect((38, 580), (38, 95), routing="direct", width=1.4, head="stealth", color=INK)
        diag.text("energy", size=13).at(38, 85, anchor="bottom_center")

        # H2 ------------------------------------------------------------------
        cx = 190
        occ = fill(H2_MO, 2)
        molecule(diag, cx, 105, [("1s", 300, 1, 1)], H2_MO, occ, "H2")
        for y in (370, 230):
            dashed(diag, (cx - 105 + 18, 300), (cx - 18, y))
            dashed(diag, (cx + 105 - 18, 300), (cx + 18, y))
        diag.text("$\\ce{H}$", size=15).at(cx - 105, 572, anchor="center")
        diag.text("$\\ce{H2}$", size=15).at(cx, 572, anchor="center")
        diag.text("$\\ce{H}$", size=15).at(cx + 105, 572, anchor="center")

        # O2 ------------------------------------------------------------------
        cx = 640
        occ = fill(O2_MO, 12)
        molecule(diag, cx, 195, [("2s", 470, 1, 2), ("2p", 265, 3, 4)], O2_MO, occ, "O2")
        for y in (520, 440):
            dashed(diag, (cx - 195 + 18, 470), (cx - 18, y))
            dashed(diag, (cx + 195 - 18, 470), (cx + 18, y))
        for name, y, n, _ in O2_MO[2:]:
            left = cx - 26 - 18 if n == 2 else cx - 18
            right = cx + 26 + 18 if n == 2 else cx + 18
            dashed(diag, (cx - 195 + 22 + 8, 265), (left, y))
            dashed(diag, (cx + 195 - 22 - 8, 265), (right, y))
        diag.text("$\\ce{O}$", size=15).at(cx - 195, 572, anchor="center")
        diag.text("$\\ce{O2}$", size=15).at(cx, 572, anchor="center")
        diag.text("$\\ce{O}$", size=15).at(cx + 195, 572, anchor="center")

        # Bond order from the occupancy.
        def bond_order(mo, occ):
            bonding = sum(len(s) for lv, slots in zip(mo, occ) if lv[3] for s in slots)
            anti = sum(len(s) for lv, slots in zip(mo, occ) if not lv[3] for s in slots)
            return (bonding - anti) / 2, bonding, anti
        bo_h, b_h, a_h = bond_order(H2_MO, fill(H2_MO, 2))
        bo_o, b_o, a_o = bond_order(O2_MO, fill(O2_MO, 12))
        unpaired = sum(1 for slots in fill(O2_MO, 12) for s in slots if len(s) == 1)

        diag.text(
            f"**Bond order {bo_h:g}**\n"
            f"({b_h} bonding $-$ {a_h} antibonding) / 2\n"
            "no unpaired electrons: diamagnetic\n"
            "bond length 74 pm, 436 kJ/mol",
            size=13,
        ).at(190, 600, anchor="top_center")
        diag.text(
            f"**Bond order {bo_o:g}**:  ({b_o} bonding $-$ {a_o} antibonding) / 2\n"
            f"{unpaired} unpaired electrons in $\\pi^*_{{2p}}$: paramagnetic\n"
            "bond length 121 pm, 498 kJ/mol",
            size=13,
        ).at(640, 600, anchor="top_center")
        diag.caption("**Figure 9:** Molecular orbital diagrams of $\\ce{H2}$ (bond order 1) and $\\ce{O2}$ (bond order 2, two unpaired electrons)",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/chemistry") -> Path:
    return render_all(diagram(), output_dir, "09_molecular_orbitals_h2_o2")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/chemistry"))
