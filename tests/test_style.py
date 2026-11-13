"""STYLE-01 / STYLE-02: the style cascade and the paper theme."""
from __future__ import annotations

import re

import pytest

from diagrams_as_code import Diagram, Style, get_theme
from diagrams_as_code.audit import audit_diagram
from diagrams_as_code.style import resolve_group_style, resolve_node_style


def _node_svg(svg: str, shape_id: str) -> str:
    return svg[svg.index(f'<g id="{shape_id}"'):].split("</g>", 1)[0]


def test_merged_keeps_unset_fields():
    base = Style(fill="#111", stroke="#222", radius=6)
    out = base.merged(Style(stroke="#333"))
    assert (out.fill, out.stroke, out.radius) == ("#111", "#333", 6)
    assert base.merged(None) is base


@pytest.mark.parametrize("kwargs", [{"stroke_width": -1}, {"radius": float("nan")}, {"opacity": 1.5}])
def test_invalid_values_are_rejected(kwargs):
    with pytest.raises(ValueError):
        Style(**kwargs)


def test_cascade_theme_then_group_then_element_then_metadata():
    theme = get_theme("paper")
    with Diagram("t", theme="paper") as d:
        with d.group("Outer", child_style=Style(fill="#EEEEEE", stroke_width=3)):
            with d.group("Inner", child_style=Style(stroke_width=4)):
                plain = d.shape("Plain").at(100, 150)
                own = d.shape("Own", style=Style(fill="#DDDDDD")).right_of(plain, margin=40)
                legacy = d.shape("Legacy", style=Style(fill="#DDDDDD"), fill="#CCCCCC").right_of(own, margin=40)
        outside = d.shape("Outside").at(100, 400)
    assert resolve_node_style(theme, outside).fill == theme.node_fill
    assert (resolve_node_style(theme, plain).fill, resolve_node_style(theme, plain).stroke_width) == ("#EEEEEE", 4)
    assert resolve_node_style(theme, own).fill == "#DDDDDD"
    assert resolve_node_style(theme, legacy).fill == "#CCCCCC"


def test_group_frame_style_and_child_style_are_separate():
    theme = get_theme("paper")
    with Diagram("t", theme="paper") as d:
        with d.group("G", style=Style(dash="", stroke_width=2), child_style=Style(fill="#EEEEEE")) as g:
            d.shape("A").at(100, 150)
    frame = resolve_group_style(theme, g)
    assert (frame.dash, frame.stroke_width, frame.fill) == ("", 2, theme.group_bg)


def test_paper_theme_has_no_shadows_hairlines_and_square_corners():
    with Diagram("t", theme="paper") as d:
        with d.group("Layer"):
            a = d.shape("A", id="a").at(100, 150)
            b = d.shape("B", id="b").right_of(a, margin=120)
        d.connect(a, b, label="x")
    svg = d.render_svg()
    assert 'filter="url(#shadow)"' not in svg
    node = _node_svg(svg, "a")
    assert 'rx="0"' in node and 'stroke-width="1"' in node and 'stroke="#000000"' in node
    group = _node_svg(svg, d.groups[0].id)
    assert 'rx="0"' in group and 'stroke-dasharray="6,4"' in group and 'stroke-width="1"' in group
    assert re.search(r'<path d="[^"]+" fill="none" stroke="#000000" stroke-width="1"', svg)
    assert not audit_diagram(d)


def test_existing_themes_keep_their_look():
    with Diagram("t", theme="iiot_dark_gold") as d:
        with d.group("G"):
            a = d.shape("A", id="a").at(100, 150)
            b = d.shape("B", id="b").right_of(a, margin=120)
        d.connect(a, b)
    svg = d.render_svg()
    node = _node_svg(svg, "a")
    assert 'filter="url(#shadow)"' in svg and 'rx="6"' in node and 'stroke-width="2"' in node
    group = _node_svg(svg, d.groups[0].id)
    assert 'rx="8"' in group and 'stroke-width="1.5"' in group and "stroke-dasharray" not in group
    assert 'markerWidth="6"' in svg


def test_style_reaches_the_svg():
    with Diagram("t", theme="paper") as d:
        d.shape("A", id="a", style=Style(fill="#ABCDEF", stroke_width=2.5, radius=4, dash="2,2", opacity=0.5)).at(100, 100)
    node = _node_svg(d.render_svg(), "a")
    for expected in ('fill="#ABCDEF"', 'stroke-width="2.5"', 'rx="4"', 'stroke-dasharray="2,2"', 'opacity="0.5"'):
        assert expected in node


def test_style_font_size_pins_the_label_size():
    with Diagram("t", theme="paper") as d:
        with d.group("G", child_style=Style(font_size=10)):
            d.shape("Inherited", id="a").at(100, 150)
            d.shape("Own", id="b", style=Style(font_size=16)).at(300, 150)
    svg = d.render_svg()
    assert 'font-size="10"' in _node_svg(svg, "a")
    assert 'font-size="16"' in _node_svg(svg, "b")


def test_clone_keeps_style():
    from diagrams_as_code import Shape
    s = Shape("s", "S", style=Style(fill="#123456"))
    assert s.clone("t").style == Style(fill="#123456")
