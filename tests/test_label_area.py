"""LAYOUT-04: an inside label stays clear of its shape's own artwork."""
from __future__ import annotations

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.labels import PLATE_KINDS, label_area, node_label

KINDS = ["box", "cylinder", "database", "server_rack", "cloud", "diamond"]


def _one(kind: str, label: str = "Primary Store", icon: str | None = "database"):
    with Diagram("t", theme="monochrome") as d:
        shape = d.shape(label, kind=kind, icon=icon, width=140, height=70).at(60, 80)
    d.solve()
    return d, shape


@pytest.mark.parametrize("kind", KINDS)
def test_label_and_icon_fit_inside_the_label_area(kind):
    d, shape = _one(kind)
    label, area = node_label(shape), label_area(shape)
    assert label.fits
    assert label.block.width <= area.width and label.content_height <= area.height
    assert "label_overflow" not in audit_diagram(d)


@pytest.mark.parametrize("kind", KINDS)
def test_label_area_is_inside_the_shape(kind):
    _, shape = _one(kind)
    area, b = label_area(shape), shape.bounds
    assert b.left <= area.left and area.right <= b.right
    assert b.top <= area.top and area.bottom <= b.bottom


def test_cylinder_label_area_starts_below_the_rim():
    _, shape = _one("cylinder")
    assert label_area(shape).top >= shape.bounds.top + 2 * min(12.0, shape.bounds.height / 4.0)


def test_diamond_label_area_is_inscribed():
    _, shape = _one("diamond", icon=None)
    area, b = label_area(shape), shape.bounds
    assert area.width / b.width + area.height / b.height <= 1.0 + 1e-9


@pytest.mark.parametrize("kind", KINDS)
def test_plate_is_drawn_only_where_artwork_fills_the_body(kind):
    d, _ = _one(kind)
    assert ('class="label-plate"' in d.render_svg()) == (kind in PLATE_KINDS)


def test_shape_grows_rather_than_let_the_label_touch_the_artwork():
    _, shape = _one("cloud", label="A fairly long cloud region name")
    assert shape.bounds.width > 140 or shape.bounds.height > 70
    assert node_label(shape).fits


def test_fit_label_off_keeps_the_size():
    with Diagram("t", theme="monochrome") as d:
        shape = d.shape("Tank", kind="cylinder", icon="database", width=140, height=70, fit_label=False).at(60, 80)
    d.solve()
    assert (shape.bounds.width, shape.bounds.height) == (140, 70)
