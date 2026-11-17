"""From the regular expression $(a|b)^*abb$ to an NFA, and from the NFA to a DFA.

The NFA guesses where the final $abb$ starts: state 0 loops on both letters,
then reads $a$, $b$, $b$. The subset construction turns it into a DFA whose
states are sets of NFA states; the table on the right is that construction,
computed in the script, and the lower automaton draws it. A double border
marks an accepting state.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

# NFA: (state, letter) -> set of next states.
NFA = {(0, "a"): {0, 1}, (0, "b"): {0}, (1, "b"): {2}, (2, "b"): {3}}
NFA_FINAL = {3}
ALPHABET = ("a", "b")
D = 52.0
STATE = Style(radius=D / 2, font_size=14)
FINAL = Style(radius=D / 2, font_size=14, double=4)
LINE = {"width": 1.2}
LABEL = {"size": 13, "padding": 2}
CELL_H = 30.0
HEAD = Style(radius=0, shadow=False, fill="#E4E4E8", font_size=12)
PLAIN = Style(radius=0, shadow=False, fill="#FFFFFF", font_size=13)


def subset_construction():
    """DFA states as frozensets in discovery order, and the DFA transition table."""
    start = frozenset({0})
    order, table, todo = [start], {}, [start]
    while todo:
        current = todo.pop(0)
        for letter in ALPHABET:
            nxt = frozenset(t for s in current for t in NFA.get((s, letter), ()))
            table[(current, letter)] = nxt
            if nxt not in order:
                order.append(nxt)
                todo.append(nxt)
    return order, table


def diagram() -> Diagram:
    order, table = subset_construction()
    names = {subset: "ABCD"[i] for i, subset in enumerate(order)}
    with Diagram("Regular expression to NFA and DFA", theme="monochrome") as diag:

        def state(name: str, x: float, y: float, final: bool = False):
            return diag.shape(name, D, D, style=FINAL if final else STATE).at(x, y, anchor="center")

        def label(body: str, x: float, y: float, anchor: str = "bottom_center"):
            return diag.text(body, **LABEL).at(x, y, anchor=anchor)

        def loop(node, x: float, y: float, up: bool = True):
            side, dy = ("top", -1) if up else ("bottom", 1)
            diag.connect(node.anchor(side, 0.25), node.anchor(side, 0.75), routing="spline",
                         via=[(x - 22, y + dy * 52), (x, y + dy * 64), (x + 22, y + dy * 52)], **LINE)

        def straight(a, b):
            a.anchor("right", 0.5) >> diag.edge(**LINE) >> b.anchor("left", 0.5)

        # (a) The NFA.
        ny, nx = 170.0, (150.0, 310.0, 470.0, 630.0)
        diag.text("**(a)** NFA for $(a \\mid b)^* a b b$", size=14).at(60, 50)
        nfa = [state(str(i), x, ny, i in NFA_FINAL) for i, x in enumerate(nx)]
        diag.connect((70, ny), nfa[0].anchor("left", 0.5), routing="direct", **LINE)
        loop(nfa[0], nx[0], ny)
        label("$a, b$", nx[0], ny - 66)
        for i, letter in enumerate("abb"):
            straight(nfa[i], nfa[i + 1])
            label(f"${letter}$", (nx[i] + nx[i + 1]) / 2, ny - 6)

        # (b) The DFA from the subset construction.
        dy, dx = 440.0, (150.0, 330.0, 510.0, 690.0)
        diag.text("**(b)** DFA by subset construction", size=14).at(60, 270)
        dfa = {}
        for subset, x in zip(order, dx):
            dfa[subset] = state(names[subset], x, dy, bool(subset & NFA_FINAL))
        diag.connect((70, dy), dfa[order[0]].anchor("left", 0.5), routing="direct", **LINE)
        A, B, C, Dd = (dfa[s] for s in order)
        straight(A, B)
        straight(B, C)
        straight(C, Dd)
        label("$a$", (dx[0] + dx[1]) / 2, dy - 6)
        label("$b$", (dx[1] + dx[2]) / 2, dy - 6)
        label("$b$", (dx[2] + dx[3]) / 2, dy - 6)
        loop(A, dx[0], dy)
        label("$b$", dx[0], dy - 66)
        loop(B, dx[1], dy, up=False)
        label("$a$", dx[1], dy + 66, "top_center")
        # Back arcs: C -a-> B and D -a-> B above, D -b-> A below.
        diag.connect(C.anchor("top", 0.3), B.anchor("top", 0.7), routing="spline",
                     via=[(dx[2] - 24, dy - 58), (dx[1] + 24, dy - 58)], **LINE)
        label("$a$", (dx[1] + dx[2]) / 2, dy - 66)
        diag.connect(Dd.anchor("top", 0.5), B.anchor("top", 0.4), routing="spline",
                     via=[(dx[3] - 14, dy - 96), (dx[2], dy - 116), (dx[1] + 14, dy - 96)], **LINE)
        label("$a$", dx[2], dy - 124)
        diag.connect(Dd.anchor("bottom", 0.5), A.anchor("bottom", 0.5), routing="spline",
                     via=[(dx[3] - 24, dy + 96), (dx[2], dy + 116), (dx[1], dy + 116), (dx[0] + 24, dy + 96)], **LINE)
        label("$b$", (dx[1] + dx[2]) / 2, dy + 124, "top_center")

        # The construction itself.
        x0, y0 = 840.0, 120.0
        widths = (70.0, 100.0, 70.0, 70.0)
        diag.text("**Subset construction**", size=13).at(x0, y0 - 10, anchor="bottom_left")

        def row(cells, y, style):
            x = x0
            for text, w in zip(cells, widths):
                diag.shape(text, w, CELL_H, style=style, fit_label=False).at(x, y)
                x += w

        def name_set(subset):
            return "$\\{" + ", ".join(str(s) for s in sorted(subset)) + "\\}$"

        row(["DFA", "NFA states", "on $a$", "on $b$"], y0, HEAD)
        for i, subset in enumerate(order, start=1):
            mark = names[subset] + (" *(acc.)*" if subset & NFA_FINAL else "")
            row([mark, name_set(subset), names[table[(subset, 'a')]], names[table[(subset, 'b')]]],
                y0 + i * CELL_H, PLAIN)
        diag.text(
            "A DFA state accepts when its set\ncontains an accepting NFA state.\n"
            "$D$ = $\\{0, 3\\}$ means the input\nso far ends in $abb$.\n\n"
            "In the worst case an $n$-state NFA\nneeds $2^n$ DFA states; here 4 suffice.",
            size=12, font="serif", italic=True,
        ).at(x0, y0 + 5 * CELL_H + 24)
        diag.caption("**Figure 5:** A four-state NFA for $(a \\mid b)^* abb$ and the equivalent DFA "
                     "from the subset construction", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/computer_science") -> Path:
    return render_all(diagram(), output_dir, "05_regex_nfa_to_dfa")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer_science")
    build_diagram(dest)
