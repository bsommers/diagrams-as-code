"""The ``project_management`` icon domain: catalogued, generated and drawn inside the grid."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from diagrams_as_code.shapes import ShapeLibrary

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "project_management"
NAMES = [
    "backlog", "baseline", "deliverable", "dependency", "epic", "gate", "kanban_card",
    "milestone", "resource", "risk", "sprint", "task", "timebox",
]
LIB = ShapeLibrary()


def test_domain_holds_exactly_the_thirteen_icons() -> None:
    in_domain = sorted(n for n, (d, _) in LIB._ICON_CATALOG.items() if d == DOMAIN)
    assert in_domain == NAMES


@pytest.mark.parametrize("name", NAMES)
def test_icon_is_catalogued_generated_and_described(name: str) -> None:
    domain, description = LIB._ICON_CATALOG[name]
    assert domain == DOMAIN
    assert description.strip()
    assert (REPO_ROOT / "icons" / DOMAIN / f"{name}.svg").is_file()
    assert name not in LIB._ICON_ALIASES, "a canonical name must not also be an alias"


@pytest.mark.parametrize("name", NAMES)
def test_icon_renders_well_formed_markup_without_text(name: str) -> None:
    svg = LIB.render_icon(name, 0, 0, size=24, color="#123456")
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>')
    assert f"icon-{name}" in svg
    assert "#123456" in svg
    assert not list(root.iter("{http://www.w3.org/2000/svg}text")), "icons carry no text"


def _coords(content: str) -> list[float]:
    """Every number that is a geometry coordinate, ignoring paint attributes."""
    values: list[float] = []
    for el in ET.fromstring(f"<g>{content}</g>").iter():
        if el.tag in ("g",):
            continue
        for attr in ("x1", "x2", "y1", "y2", "cx", "cy", "x", "y"):
            if attr in el.attrib:
                values.append(float(el.attrib[attr]))
        if el.tag == "rect":
            values.append(float(el.attrib["x"]) + float(el.attrib["width"]))
            values.append(float(el.attrib["y"]) + float(el.attrib["height"]))
        if el.tag == "circle":
            r = float(el.attrib["r"])
            values += [float(el.attrib["cx"]) - r, float(el.attrib["cx"]) + r,
                       float(el.attrib["cy"]) - r, float(el.attrib["cy"]) + r]
        if "d" in el.attrib:
            values += [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", re.sub(r"[A-Za-z]", " ", el.attrib["d"]))]
    return values


@pytest.mark.parametrize("name", NAMES)
def test_icon_fits_the_24_grid(name: str) -> None:
    content = LIB._render_icon_content(name, "currentColor", 2)
    coords = _coords(content)
    assert coords
    # Arc radii appear in path data, so only the lower bound and a loose upper
    # bound are checked here; the file test below pins the viewBox itself.
    assert min(coords) >= 0.0 and max(coords) <= 24.0
    root = ET.parse(REPO_ROOT / "icons" / DOMAIN / f"{name}.svg").getroot()
    assert root.get("viewBox") == "0 0 24 24"
