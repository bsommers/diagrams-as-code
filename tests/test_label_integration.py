"""Labels drawn through the text engine: markup, math, fitting."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from diagrams_as_code import Diagram, Shape
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.labels import badge_size, node_label

NS = {"svg": "http://www.w3.org/2000/svg"}
REPO = Path(__file__).resolve().parent.parent


def _render(d: Diagram) -> ET.Element:
    return ET.fromstring(d.render_svg())


def test_math_in_node_group_and_edge_labels_renders_as_outlines():
    with Diagram("t", theme="monochrome", width=640, height=280) as d:
        with d.group("Layer $\\Omega$"):
            a = d.add(Shape("a", "Intent ($I$)", width=160, height=60)).at(80, 120)
            b = d.add(Shape("b", "$E_{t+1}$", width=120, height=60)).right_of(a, margin=160)
        d.connect(a, b, label="$g_k \\leq 0$")
    root = _render(d)
    for element_id in ("a", "b"):
        node = root.find(f".//svg:g[@id='{element_id}']", NS)
        assert node is not None and node.findall("svg:path", NS), element_id
    badge = root.find(".//svg:g[@class='badge']", NS)
    assert badge is not None and len(badge.findall("svg:path", NS)) >= 4
    assert "$" not in "".join(root.itertext())
    assert audit_diagram(d) == {}


def test_explicit_line_breaks_are_kept():
    with Diagram("t", theme="monochrome") as d:
        d.add(Shape("a", "one\ntwo\nthree", width=140, height=80)).at(50, 50)
    root = _render(d)
    spans = root.findall(".//svg:g[@id='a']//svg:tspan", NS)
    assert [s.text for s in spans] == ["one", "two", "three"]


def test_label_and_layout_agree_on_size():
    s = Shape("a", "A fairly long label that wraps", width=110, height=70).at(0, 0)
    label = node_label(s)
    assert label.fits
    assert label.block.width <= 110 - 12 and label.block.height <= 70 - 6


def test_pinned_font_size_is_respected_and_the_shape_grows_for_it():
    with Diagram("t", theme="monochrome") as d:
        s = d.add(Shape("a", "Sized label text", width=60, height=30, font_size=16)).at(50, 50)
    d.solve()
    label = node_label(s)
    assert label.block.style.size == 16 and label.fits
    assert s.bounds.height > 30


def test_fit_label_can_be_turned_off_per_shape_and_per_diagram():
    with Diagram("t", theme="monochrome", fit_labels=False) as d:
        a = d.add(Shape("a", "This label is far too long for the box", width=60, height=24)).at(50, 50)
        b = d.add(Shape("b", "This label is far too long for the box", width=60, height=24, fit_label=True)).at(50, 150)
    d.solve()
    assert (a.bounds.width, a.bounds.height) == (60, 24)
    assert b.bounds.height > 24


def test_badge_size_matches_what_is_drawn():
    with Diagram("t", theme="monochrome") as d:
        a = d.add(Shape("a", "A")).at(50, 50)
        b = d.add(Shape("b", "B")).at(450, 50)
        d.connect(a, b, label="Protocol label")
    root = _render(d)
    rect = root.find(".//svg:g[@class='badge']/svg:rect", NS)
    w, h = badge_size("Protocol label")
    # Drawn at the measured size, to the two decimals the SVG keeps.
    assert float(rect.attrib["width"]) == round(w, 2) and float(rect.attrib["height"]) == round(h, 2)


def test_no_module_guesses_text_width_from_character_counts():
    offenders = []
    for path in (REPO / "src" / "diagrams_as_code").rglob("*.py"):
        if path.name.startswith("_") or "text" in path.parts:
            continue
        src = path.read_text(encoding="utf-8")
        if "* 0.62" in src or "AVG_CHAR_EM" in src and path.name != "metrics.py":
            offenders.append(path.name)
    assert offenders == []


def test_font_licence_ships_with_the_package():
    text = (REPO / "src" / "diagrams_as_code" / "text" / "OFL-STIX.txt").read_text(encoding="utf-8")
    assert "SIL Open Font License" in text
