"""A time-scaled phylogeny of the primates, drawn from nested data with a scale bar.

The tree is a nested tuple structure: ``leaf(name, common, length)`` and ``node(key, length, *children)``,
each with the branch length in million years (My). Because ages are consistent, all tips line up at the
present (an ultrametric tree) and a node's x position is its age. Layout is a rectangular phylogram:
leaves take consecutive rows and an internal node sits at the mean row of its children. Divergence
times are approximate published estimates (illustrative, in Mya): Homo-Pan 6.5, Pan-Gorilla 9,
Pongo 15.7, Hylobatidae 20, Cercopithecidae 29, New World monkeys 43; chimpanzee and bonobo 1.9.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"
RED = "#B03A3A"
GREY = "#8A93A8"
PX_PER_MY = 14.0
X_ROOT, Y0, DY = 110.0, 110.0, 46.0


def leaf(name, common, length):
    return ("leaf", name, common, length)


def node(key, length, *children):
    return ("node", key, length, children)


TREE = node("A", 0.0,
            leaf("Callithrix jacchus", "marmoset", 43.0),
            node("B", 14.0,
                 leaf("Macaca mulatta", "rhesus macaque", 29.0),
                 node("C", 9.0,
                      leaf("Hylobates lar", "lar gibbon", 20.0),
                      node("D", 4.3,
                           leaf("Pongo pygmaeus", "orangutan", 15.7),
                           node("E", 6.7,
                                leaf("Gorilla gorilla", "gorilla", 9.0),
                                node("F", 2.5,
                                     leaf("Homo sapiens", "human", 6.5),
                                     node("G", 4.6,
                                          leaf("Pan troglodytes", "chimpanzee", 1.9),
                                          leaf("Pan paniscus", "bonobo", 1.9))))))))
CLADES = {
    "A": ("Anthropoidea", 43.0),
    "B": ("Catarrhini", 29.0),
    "C": ("Hominoidea (apes)", 20.0),
    "D": ("Hominidae (great apes)", 15.7),
    "E": ("Homininae", 9.0),
    "F": ("Hominini", 6.5),
    "G": ("Pan", 1.9),
}


def layout(tree):
    """Return (segments, nodes, tips): drawing data from the nested tuples."""
    rows = [0]
    segs, nodes, tips = [], [], []

    def walk(t, x_parent, on_human):
        kind = t[0]
        length = t[3] if kind == "leaf" else t[2]
        x = x_parent + length * PX_PER_MY
        if kind == "leaf":
            y = Y0 + rows[0] * DY
            rows[0] += 1
            human = t[1] == "Homo sapiens"
            segs.append(((x_parent, y), (x, y), human))
            tips.append((x, y, t[1], t[2], human))
            return y, human
        ys, flags = [], []
        for ch in t[3]:
            y_ch, h = walk(ch, x, False)
            ys.append(y_ch)
            flags.append(h)
        y = sum(ys) / len(ys)
        has_human = any(flags)
        segs.append(((x, min(ys)), (x, max(ys)), has_human and False))
        # Highlight the vertical stretch that leads to the human branch.
        for y_ch, h in zip(ys, flags):
            if h:
                segs.append(((x, y), (x, y_ch), True))
        segs.append(((x_parent, y), (x, y), has_human))
        nodes.append((x, y, t[1]))
        return y, has_human

    walk(tree, X_ROOT, False)
    return segs, nodes, tips


def diagram() -> Diagram:
    segs, nodes, tips = layout(TREE)
    x_tip = X_ROOT + 43.0 * PX_PER_MY
    y_last = tips[-1][1]
    axis_y = y_last + 48
    with Diagram("Primate phylogenetic tree", theme="paper") as diag:
        # Faint time gridlines and the time axis (Mya), 0 at the tips.
        for t in range(0, 44, 10):
            x = x_tip - t * PX_PER_MY
            diag.polyline([(x, Y0 - 22), (x, axis_y)], style=Style(stroke="#E1E5EE", stroke_width=1.0), z=-3)
            diag.polyline([(x, axis_y), (x, axis_y + 6)], style=Style(stroke=INK, stroke_width=1.2))
            diag.text(str(t), size=11).at(x, axis_y + 9, anchor="top_center")
        diag.polyline([(X_ROOT, axis_y), (x_tip, axis_y)], style=Style(stroke=INK, stroke_width=1.2))
        diag.text("Mya (million years ago)", size=12).at((X_ROOT + x_tip) / 2 + 60, axis_y + 28, anchor="top_center")

        # Branches.
        diag.polyline([(X_ROOT - 28, nodes[-1][1]), (X_ROOT, nodes[-1][1])], style=Style(stroke=INK, stroke_width=2.0))
        for (a, b, human) in segs:
            if a != b:
                diag.polyline([a, b], style=Style(stroke=RED if human else INK, stroke_width=3.0 if human else 2.0), z=1 if human else 0)
        for x, y, key in nodes:
            diag.point(x, y, dot=True, radius=3.2)
            diag.text(f"**{key}**", size=12, color=INK).at(x - 10, y - 11, anchor="center")
        for x, y, name, common, human in tips:
            diag.point(x, y, dot=True, radius=3.0)
            diag.text(f"*{name}*  ({common})", size=13, color=RED if human else INK).at(x + 12, y, anchor="left_center")

        # Scale bar: 10 My.
        sy = axis_y + 70
        diag.polyline([(X_ROOT, sy), (X_ROOT + 10 * PX_PER_MY, sy)], style=Style(stroke=INK, stroke_width=2.4))
        diag.polyline([(X_ROOT, sy - 5), (X_ROOT, sy + 5)], style=Style(stroke=INK, stroke_width=1.6))
        diag.polyline([(X_ROOT + 10 * PX_PER_MY, sy - 5), (X_ROOT + 10 * PX_PER_MY, sy + 5)], style=Style(stroke=INK, stroke_width=1.6))
        diag.text("10 million years", size=12).at(X_ROOT + 10 * PX_PER_MY + 12, sy, anchor="left_center")

        # Key to the lettered clades, in the empty lower-left of the tree.
        ky = Y0 + 5 * DY + 10
        diag.text("**Clades** (approx. divergence, Mya)", size=12).at(X_ROOT, ky, anchor="top_left")
        for i, (key, (name, age)) in enumerate(CLADES.items()):
            col, row = divmod(i, 4)
            diag.text(f"**{key}**   {name}   ~{age:g}", size=12).at(X_ROOT + 6 + col * 215, ky + 20 + row * 17, anchor="top_left")
        diag.caption(
            "**Figure 6:** Time-scaled phylogeny of eight primates built from nested (name, branch length) data. Node x-position is divergence time;\n"
            "the lineage to humans is red, and the chimpanzee and bonobo are our closest living relatives",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "06_phylogenetic_tree")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
