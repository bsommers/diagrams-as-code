"""A grassland food web and its energy pyramid.

Left: arrows point from the organism eaten to its eater, so they show the direction of energy flow, and
rows are trophic levels. Right: an illustrative pyramid in which each level keeps about 10% of the energy
of the level below (the "10% rule"); tier width is proportional to log10 of the energy, so each step is one
unit narrower. Values (kJ per square metre per year) are illustrative round numbers, not field data.
"""
import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

INK = "#1F2F57"
LEVELS = [  # name, fill, energy kJ/m2/yr, y
    ("Tertiary consumers", "#F0C4C4", 10, 140.0),
    ("Secondary consumers", "#F4D9A8", 100, 250.0),
    ("Primary consumers", "#FBF1B8", 1000, 360.0),
    ("Producers", "#CFE6C4", 10000, 470.0),
]
FILL = {name: fill for name, fill, _, _ in LEVELS}
ROW = {name: y for name, _, _, y in LEVELS}
# (label, level, x)
ORGANISMS = [
    ("Hawk", "Tertiary consumers", 175),
    ("Frog", "Secondary consumers", 100), ("Snake", "Secondary consumers", 250), ("Fox", "Secondary consumers", 400),
    ("Grasshopper", "Primary consumers", 100), ("Field mouse", "Primary consumers", 250), ("Rabbit", "Primary consumers", 400),
    ("Clover", "Producers", 100), ("Grass", "Producers", 250), ("Shrubs", "Producers", 400),
]
EATEN_BY = [  # (food, eater): energy flows food -> eater
    ("Clover", "Grasshopper"), ("Clover", "Field mouse"), ("Grass", "Grasshopper"), ("Grass", "Field mouse"),
    ("Grass", "Rabbit"), ("Shrubs", "Rabbit"),
    ("Grasshopper", "Frog"), ("Field mouse", "Snake"), ("Field mouse", "Fox"), ("Rabbit", "Fox"),
    ("Frog", "Hawk"), ("Snake", "Hawk"),
]
PX, PW = 800.0, 110.0   # pyramid centre x and width per log10 unit
H = 34.0


def diagram() -> Diagram:
    with Diagram("Food web and energy pyramid", theme="paper") as diag:
        diag.text("**Grassland food web**", size=15).at(250, 74, anchor="bottom_center")
        nodes = {}
        for name, level, x in ORGANISMS:
            nodes[name] = diag.shape(name, 112, H, style=Style(fill=FILL[level], stroke=INK, stroke_width=1.5, radius=17),
                                     fit_label=False).at(x, ROW[level], anchor="center")
        for food, eater in EATEN_BY:
            diag.connect(nodes[food], nodes[eater], routing="direct", width=1.6, color="#44506E", head="stealth")
        # Row labels between the web and the pyramid.
        for name, fill, energy, y in LEVELS:
            diag.text(name.replace(" ", "\n", 1) if len(name) > 12 else name, size=11, color="#555555").at(480, y, anchor="left_center")
        # Decomposers.
        diag.shape("Decomposers (fungi, bacteria) recycle the dead matter of every level", 440, 30,
                   style=Style(fill="#E6DCCB", stroke="#6B5A1E", stroke_width=1.4, radius=6, dash="5,3"),
                   fit_label=False).at(250, 548, anchor="center")

        # Energy pyramid.
        diag.text("**Energy pyramid** (kJ per m$^2$ per year)", size=15).at(PX, 74, anchor="bottom_center")
        import math
        for name, fill, energy, y in LEVELS:
            w = PW * math.log10(energy)
            diag.shape(f"**{name}**\n{energy:,} kJ", w, 84, style=Style(fill=fill, stroke=INK, stroke_width=1.6),
                       fit_label=False).at(PX, y, anchor="center")
        # The 10% transfer between tiers.
        for (n1, _, e1, y1), (n2, _, e2, y2) in zip(LEVELS[1:], LEVELS[:-1]):
            xr = PX + PW * math.log10(e1) / 2 + 40
            diag.connect((xr, y1 - 18), (xr, y2 + 24), routing="direct", width=1.8, color=INK, head="stealth")
            diag.text("~10% passed on", size=11).at(xr + 10, (y1 + y2) / 2 + 3, anchor="left_center")
        diag.text("The other ~90% of each level's energy is lost as heat from respiration, as waste, or stays uneaten,\n"
                  "so food chains rarely exceed four or five trophic levels.", size=12, color="#333333").at(PX - 220, 536, anchor="top_left")
        diag.caption(
            "**Figure 7:** A grassland food web (arrows run from food to eater) and its energy pyramid. Each tier holds about a tenth of the\n"
            "energy of the one below, so top predators are few; the numbers are illustrative",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/biology") -> Path:
    return render_all(diagram(), output_dir, "07_food_web_pyramid")["svg"]


if __name__ == "__main__":
    build_diagram(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/biology"))
