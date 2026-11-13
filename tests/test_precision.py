"""STYLE-04: fixed-precision coordinates and optional pixel snapping."""
from __future__ import annotations

import re

from diagrams_as_code import Diagram
from diagrams_as_code.renderer_svg import fix_precision


def test_lengths_are_rounded_and_trailing_zeros_dropped():
    out = fix_precision('<rect x="235.87451171875" y="68.0" width="100.50" height="-0.001" />')
    assert out == '<rect x="235.87" y="68" width="100.5" height="0" />'


def test_path_data_is_rounded():
    assert fix_precision('<path d="M 150.0 75.0 C 200.123456 75, 250 100.999, 300 100" />') == (
        '<path d="M 150 75 C 200.12 75, 250 101, 300 100" />'
    )


def test_text_and_names_are_left_alone():
    markup = '<text x="10.5" data-label="p < 0.00125" id="n1.23456">p &lt; 0.00125</text>'
    assert fix_precision(markup) == markup


def test_scale_factors_keep_their_precision():
    out = fix_precision('<path d="M0 0" transform="translate(285.6234567 114.4) scale(0.0131234567 -0.0131234567)" />')
    assert 'translate(285.62 114.4)' in out
    assert 'scale(0.013123 -0.013123)' in out


def test_precision_is_configurable():
    assert fix_precision('<rect x="1.23456" />', places=0) == '<rect x="1" />'
    assert fix_precision('<rect x="1.23456" />', places=4) == '<rect x="1.2346" />'


def _diagram(**kwargs) -> Diagram:
    with Diagram("t", theme="paper", **kwargs) as d:
        a = d.shape(r"Policy $\pi_\theta$", id="a", width=133.3, height=61.7).at(60.3, 80.7)
        b = d.shape("B", id="b", width=120, height=60).right_of(a, margin=111.1)
        d.connect(a, b, label="x")
    return d


def test_rendered_svg_has_no_long_decimals_outside_glyph_scales():
    svg = _diagram().render_svg()
    without_scales = re.sub(r"scale\([^)]*\)", "", svg)
    assert not re.search(r'="[^"]*\d\.\d{3,}', without_scales)


def test_math_glyphs_keep_their_size():
    svg = _diagram().render_svg()
    scales = {abs(float(m)) for m in re.findall(r"scale\((-?[\d.]+) ", svg)}
    # 13 px text and its 70% subscript, in units of a 1000-unit em.
    assert scales == {0.013, 0.0091}


def test_pixel_snap_puts_everything_on_whole_pixels():
    d = _diagram(pixel_snap=True)
    svg = d.render_svg()
    for shape in d.shapes:
        b = shape.bounds
        assert all(float(v).is_integer() for v in (b.x, b.y, b.width, b.height))
    for edge in d.edges:
        assert all(p.x.is_integer() and p.y.is_integer() for p in d.routes[edge].points)
    assert '<g transform="translate(0.5 0.5)">' in svg


def test_pixel_snap_is_off_by_default_and_only_shifts_odd_strokes():
    assert "translate(0.5 0.5)" not in _diagram().render_svg()
    with Diagram("t", theme="iiot_dark_gold", pixel_snap=True) as d:
        d.shape("A").at(60.4, 80.6)
    # 2 px strokes are already crisp on whole-pixel coordinates.
    assert "translate(0.5 0.5)" not in d.render_svg()
    assert d.shapes[0].bounds.x == 60 and d.shapes[0].bounds.y == 81
