"""Text engine: metrics, markup, layout and math typesetting."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from diagrams_as_code.text import (
    MathError,
    MathRun,
    TextRun,
    TextStyle,
    has_markup,
    layout,
    measure,
    parse_markup,
    text_width,
    typeset,
)
from diagrams_as_code.text import _math_glyphs, _sans_metrics
from diagrams_as_code.text.math import SYMBOLS, glyph_available


# metrics ----------------------------------------------------------------
def test_text_width_uses_real_advances_not_a_flat_average():
    assert text_width("iiii", 20) < text_width("mmmm", 20) / 3
    assert text_width("Hello", 10) * 2 == pytest.approx(text_width("Hello", 20))
    assert text_width("Hello", 20, bold=True) > text_width("Hello", 20)


def test_text_width_matches_known_arial_advances():
    # Arial/Helvetica-compatible: 'a' = 0.556 em, space = 0.278 em, 'W' = 0.944 em.
    assert text_width("a", 1000) == pytest.approx(556, abs=1)
    assert text_width(" ", 1000) == pytest.approx(278, abs=1)
    assert text_width("W", 1000) == pytest.approx(944, abs=1)


def test_unknown_characters_still_measure():
    assert text_width("漢字", 10) == pytest.approx(20)
    assert text_width("́", 10) == 0


def test_generated_data_is_plain_and_covers_ascii():
    assert all(cp in _sans_metrics.REGULAR for cp in range(0x20, 0x7F))
    assert all(cp in _math_glyphs.GLYPHS for cp in range(0x21, 0x7F))
    assert "SIL Open Font License" in _math_glyphs.__doc__


def test_every_math_command_has_an_outline():
    missing = [name for name, (cp, _) in SYMBOLS.items() if not glyph_available(cp)]
    assert missing == []


# markup -----------------------------------------------------------------
def test_markup_parsing():
    (line,) = parse_markup("a **b** *c* $x_i$ d")
    assert [(s.kind, s.text, s.bold, s.italic) for s in line] == [
        ("text", "a ", False, False),
        ("text", "b", True, False),
        ("text", " ", False, False),
        ("text", "c", False, True),
        ("text", " ", False, False),
        ("math", "x_i", False, False),
        ("text", " d", False, False),
    ]


@pytest.mark.parametrize(
    "plain",
    ["Under $50k Budget", "costs $5 and $10", "2 * 3 * 4", "a * b", "C**", "snake_case_name", "100%", "A & B < C"],
)
def test_ordinary_labels_are_not_treated_as_markup(plain):
    assert not has_markup(plain)
    (line,) = parse_markup(plain)
    assert "".join(s.text for s in line) == plain


def test_escapes_and_line_breaks():
    assert [[s.text for s in ln] for ln in parse_markup(r"a\nb" + "\nc")] == [["a"], ["b"], ["c"]]
    (line,) = parse_markup(r"\$x\$ and \*y\*")
    assert "".join(s.text for s in line) == "$x$ and *y*"


# layout -----------------------------------------------------------------
def test_layout_wraps_at_max_width_and_never_exceeds_it():
    text = "The quick brown fox jumps over the lazy dog near the river bank"
    block = layout(text, TextStyle(size=12), max_width=120)
    assert len(block.lines) > 2
    assert all(ln.width <= 120 for ln in block.lines)
    assert " ".join(r.text for ln in block.lines for r in ln.runs) == text


def test_a_word_wider_than_max_width_gets_its_own_line():
    block = layout("a Supercalifragilistic b", TextStyle(size=12), max_width=40)
    assert [ln.runs[0].text for ln in block.lines] == ["a", "Supercalifragilistic", "b"]


def test_block_size_and_measure_agree():
    block = layout("one\ntwo lines", TextStyle(size=10))
    assert measure("one\ntwo lines", TextStyle(size=10)) == (block.width, block.height)
    assert block.height == pytest.approx(2 * 12.5)
    assert block.width == pytest.approx(text_width("two lines", 10))


def test_mixed_line_has_text_and_math_runs():
    block = layout("Valid($a_i, I$) holds", TextStyle(size=16))
    kinds = [type(r) for r in block.lines[0].runs]
    assert kinds == [TextRun, MathRun, TextRun]
    assert block.lines[0].width == pytest.approx(sum(r.width for r in block.lines[0].runs))


def test_tall_math_opens_the_line_and_stays_inside_the_block():
    plain = layout("x", TextStyle(size=16))
    tall = layout(r"$\bigcap_{k} \Omega_k$", TextStyle(size=16))
    assert tall.height > plain.height
    (base,) = tall.baselines(0.0)
    ln = tall.lines[0]
    assert base - ln.ascent >= -1e-6 and base + ln.depth <= tall.height + 1e-6


# math -------------------------------------------------------------------
def test_letters_are_italic_digits_upright():
    box = typeset("x2", 10)
    assert [g.cp for g in box.glyphs] == [0x1D465, ord("2")]


def test_subscript_is_smaller_and_lower_superscript_higher():
    box = typeset("a_i^2", 20)
    base, sub, sup = box.glyphs
    assert sub.size == pytest.approx(14) and sup.size == pytest.approx(14)
    assert sub.y > base.y > sup.y
    assert sub.x == sup.x > base.x


def test_relations_and_binary_operators_get_space_but_unary_minus_does_not():
    tight, spaced = typeset("ab", 20), typeset("a=b", 20)
    eq = typeset("=", 20).width
    assert spaced.width > tight.width + eq + 5
    assert typeset("-a", 20).width == pytest.approx(typeset("-", 20).width + typeset("a", 20).width)
    assert typeset("b-a", 20).width > typeset("-a", 20).width + typeset("b", 20).width + 5


def test_scripts_are_not_spaced():
    inner = typeset("t+1", 14)
    box = typeset("E_{t+1}", 20)
    assert box.width < typeset("E", 20).width + inner.width + 2


def test_big_operator_limits_go_underneath_and_can_be_turned_off():
    under = typeset(r"\bigcap_{k}", 20)
    side = typeset(r"\bigcap\nolimits_{k}", 20)
    assert under.width < side.width
    assert under.depth > side.depth


def test_mathrm_is_upright_and_greek_resolves():
    assert [g.cp for g in typeset(r"\mathrm{ab}", 10).glyphs] == [ord("a"), ord("b")]
    assert typeset(r"\Omega", 10).glyphs[0].cp == 0x3A9
    assert typeset(r"\alpha", 10).glyphs[0].cp == 0x1D6FC
    assert typeset("α", 10).glyphs[0].cp == 0x1D6FC


@pytest.mark.parametrize("bad", [r"\frac{a}{b}", "a_", "{a", "a}", r"\nosuchthing"])
def test_unsupported_math_raises_a_clear_error(bad):
    with pytest.raises(MathError):
        typeset(bad, 10)


# svg --------------------------------------------------------------------
def _parse(svg_fragment: str) -> ET.Element:
    return ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{svg_fragment}</svg>')


def test_plain_single_line_is_one_centred_text_element():
    svg = layout("Hello & <world>", TextStyle(size=12)).to_svg(100, 50, fill="#123456")
    root = _parse(svg)
    (el,) = list(root)
    assert el.attrib["text-anchor"] == "middle" and el.attrib["x"] == "100"
    assert el.text == "Hello & <world>" and "textLength" not in el.attrib


def test_mixed_line_pins_text_widths_and_draws_math_as_paths():
    block = layout("Valid($a_i$) ok", TextStyle(size=16))
    root = _parse(block.to_svg(200, 50))
    tags = [el.tag.split("}")[1] for el in root]
    assert tags == ["text", "path", "path", "text"]
    texts = [el for el in root if el.tag.endswith("text")]
    assert all("textLength" in el.attrib for el in texts)
    xs = [float(el.attrib["x"]) for el in texts]
    assert xs[0] == pytest.approx(200 - block.width / 2, abs=0.01)
    for el in root:
        if el.tag.endswith("path"):
            assert re.fullmatch(r"translate\([-\d.]+ [-\d.]+\) scale\([\d.]+ -[\d.]+\)", el.attrib["transform"])


def test_bold_and_italic_runs_carry_their_style():
    root = _parse(layout("a **b** *c*", TextStyle(size=12)).to_svg(0, 0, anchor="start"))
    styles = [(el.attrib.get("font-weight"), el.attrib.get("font-style")) for el in root]
    assert styles == [(None, None), ("700", None), (None, None), (None, "italic")]


def test_output_coordinates_have_at_most_two_decimals():
    svg = layout("x $a_i$ y", TextStyle(size=13.37)).to_svg(101.123456, 55.987654)
    for attr in re.findall(r'(?: x| y|textLength)="([^"]+)"', svg):
        assert len(attr.split(".")[-1]) <= 2 or "." not in attr


def test_wrapping_balances_lines_instead_of_leaving_an_orphan():
    block = layout("Hardware Security Key", TextStyle(size=12, weight=600), max_width=100)
    assert [ln.runs[0].text for ln in block.lines] == ["Hardware", "Security Key"]
    assert all(ln.width <= 100 for ln in block.lines)


def test_backslash_n_inside_math_is_a_command_not_a_line_break():
    # \nabla, \neq, \nu and \nolimits all begin with a backslash and an n.
    for formula in (r"$\nabla_\theta L$", r"$a \neq b$", r"$\nu$", r"$\sum\nolimits_i x_i$"):
        block = layout(formula, TextStyle(size=13))
        assert len(block.lines) == 1, formula
    # Outside math a typed backslash-n still breaks the line, as a real newline does.
    assert len(layout(r"one\ntwo", TextStyle(size=13)).lines) == 2
    assert len(layout(r"$\nu$ first\n$\neq$ second", TextStyle(size=13)).lines) == 2
