"""A natural-deduction proof tree for hypothetical syllogism.

The theorem is ((P implies Q) and (Q implies R)) implies (P implies R). Premises sit above
a horizontal bar and the conclusion below it, each bar is labelled with its
rule, and an assumption in brackets carries the number of the rule that
discharges it. The tree is stored as data; the script measures each formula,
lays the sub-proofs out left to right so that nothing overlaps, and centres each
conclusion under its premises.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.text import TextStyle, layout

SIZE = 15
RULE_SIZE = 12
GAP = 46.0  # between sibling premises
STEP = 54.0  # vertical distance between a conclusion and its premises
H = r"(P \to Q) \land (Q \to R)"


def width(text: str, size: float) -> float:
    return layout(text, TextStyle(size=size)).width


class Proof:
    """A conclusion, the rule that yields it, and the sub-proofs of its premises."""

    def __init__(self, conclusion: str, rule: str = "", premises: list[Proof] | None = None) -> None:
        self.conclusion, self.rule, self.premises = conclusion, rule, premises or []
        self.x = self.lo = self.hi = self.text_lo = self.text_hi = 0.0  # centre and extents, set by place()
        self.bar_lo = self.bar_hi = 0.0

    def place(self, left: float) -> None:
        """Lay this sub-proof out with its left edge at ``left``."""
        tw = width(self.conclusion, SIZE)
        if not self.premises:
            self.x, self.lo, self.hi = left + tw / 2, left, left + tw
            self.text_lo, self.text_hi = self.lo, self.hi
            return
        cursor = left
        for p in self.premises:
            p.place(cursor)
            cursor = p.hi + GAP
        span_lo, span_hi = self.premises[0].text_lo, self.premises[-1].text_hi
        self.x = (span_lo + span_hi) / 2
        if self.x - tw / 2 < left:  # a wide conclusion pushes its premises right
            self.shift(left - (self.x - tw / 2))
            span_lo, span_hi = self.premises[0].text_lo, self.premises[-1].text_hi
        self.text_lo, self.text_hi = self.x - tw / 2, self.x + tw / 2
        self.bar_lo, self.bar_hi = min(span_lo, self.text_lo), max(span_hi, self.text_hi)
        self.hi = max(self.premises[-1].hi, self.bar_hi + 8 + width(self.rule, RULE_SIZE))
        self.lo = min(left, self.bar_lo)

    def shift(self, dx: float) -> None:
        self.x += dx
        self.lo += dx
        self.hi += dx
        self.text_lo += dx
        self.text_hi += dx
        self.bar_lo += dx
        self.bar_hi += dx
        for p in self.premises:
            p.shift(dx)

    def depth(self) -> int:
        return 1 + max((p.depth() for p in self.premises), default=-1) if self.premises else 0

    def draw(self, diag: Diagram, y: float) -> None:
        """Draw with the conclusion's text centred on ``y``."""
        diag.text(self.conclusion, size=SIZE).at(self.x, y, anchor="center")
        if self.premises:
            bar = y - 17
            diag.polyline([(self.bar_lo, bar), (self.bar_hi, bar)], style=Style(stroke="#111111", stroke_width=1.3),
                          obstacle=False)
            diag.text(self.rule, size=RULE_SIZE).at(self.bar_hi + 8, bar, anchor="left_center")
            for p in self.premises:
                p.draw(diag, y - STEP)


def tree() -> Proof:
    hyp = lambda: Proof(rf"$[{H}]^{{1}}$")
    p_to_q = Proof(r"$P \to Q$", r"$\land\mathrm{E}_1$", [hyp()])
    q_to_r = Proof(r"$Q \to R$", r"$\land\mathrm{E}_2$", [hyp()])
    q = Proof(r"$Q$", r"$\to\mathrm{E}$", [p_to_q, Proof(r"$[P]^{2}$")])
    r = Proof(r"$R$", r"$\to\mathrm{E}$", [q, q_to_r])
    p_to_r = Proof(r"$P \to R$", r"$\to\mathrm{I}^{2}$", [r])
    return Proof(rf"$({H}) \to (P \to R)$", r"$\to\mathrm{I}^{1}$", [p_to_r])


def diagram() -> Diagram:
    root = tree()
    root.place(60.0)
    levels = root.depth()
    y_root = 70 + levels * STEP
    with Diagram("Natural deduction proof tree", theme="paper") as diag:
        root.draw(diag, y_root)
        ly = y_root + 70
        diag.text("**Rules used**", size=13).at(60, ly, anchor="top_left")
        notes = [
            r"$\land\mathrm{E}_1,\ \land\mathrm{E}_2$: from $A \land B$ infer $A$, or infer $B$.",
            r"$\to\mathrm{E}$ (modus ponens): from $A \to B$ and $A$ infer $B$.",
            r"$\to\mathrm{I}^{n}$: from a proof of $B$ that assumes $[A]^{n}$, infer $A \to B$ and discharge the assumption.",
        ]
        diag.text("\n".join(notes), size=12, font="serif").at(60, ly + 24, anchor="top_left")
        diag.caption(
            "**Figure 8:** A natural-deduction proof of hypothetical syllogism",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/logic") -> Path:
    return render_all(diagram(), output_dir, "08_proof_tree")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/logic")
    build_diagram(dest)
