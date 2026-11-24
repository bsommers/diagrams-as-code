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


@pytest.mark.parametrize("bad", [r"\acute{a}", r"\sqrt[3{x}", "a_", "{a", "a}", r"\nosuchthing"])
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


# function names, bars and radicals ------------------------------------------------


def _extent(box):
    """(x_min, x_max, y_min, y_max) of the glyph origins, y down."""
    xs = [g.x for g in box.glyphs]
    ys = [g.y for g in box.glyphs]
    return min(xs), max(xs), min(ys), max(ys)


def test_superscript_on_a_function_name_sits_beside_it():
    plain = typeset(r"\cos", 10)
    box = typeset(r"\cos^2", 10)
    # The exponent follows the name (to its right), instead of floating over its middle.
    exponent = box.glyphs[-1]
    assert exponent.x >= plain.width - 1e-9
    assert exponent.y < 0  # raised


def test_inverse_function_exponent_is_beside_the_name():
    box = typeset(r"\sin^{-1}", 10)
    assert min(g.x for g in box.glyphs[3:]) >= typeset(r"\sin", 10).width - 1e-9


def test_limit_functions_keep_their_limits_below():
    box = typeset(r"\lim_{x}", 10)
    sub = box.glyphs[-1]
    assert sub.y > 0 and sub.x < typeset(r"\lim", 10).width  # under the name, not after it


@pytest.mark.parametrize("name", ["arcsin", "arccos", "arctan", "sinh", "cosh", "tanh", "cot", "sec", "csc"])
def test_more_function_names_are_upright(name):
    assert [g.cp for g in typeset("\\" + name, 10).glyphs] == [ord(c) for c in name]


@pytest.mark.parametrize("src", [r"\bar x", r"\bar{x}", r"\overline{xy}"])
def test_overline_adds_a_bar_above_the_body(src):
    body = typeset(src.replace(r"\overline", "").replace(r"\bar", "").replace("{", "").replace("}", ""), 10)
    box = typeset(src, 10)
    assert box.height > body.height
    assert abs(box.width - body.width) < 1e-6
    assert any(g.cp == 0x2212 for g in box.glyphs)


def test_sqrt_has_a_radical_and_a_bar_over_the_body():
    box = typeset(r"\sqrt{a^2+b^2}", 10)
    cps = [g.cp for g in box.glyphs]
    assert 0x221A in cps and 0x2212 in cps
    body = typeset("a^2+b^2", 10)
    assert box.width > body.width and box.height > body.height


def test_sqrt_index_sits_up_and_left_of_the_radical():
    plain, boxed = typeset(r"\sqrt{x}", 10), typeset(r"\sqrt[3]{x}", 10)
    assert boxed.width > plain.width and boxed.height >= plain.height
    three = [g for g in boxed.glyphs if g.cp == ord("3")][0]
    sign = [g for g in boxed.glyphs if g.cp == 0x221A][0]
    assert three.size < 10 and three.x < sign.x + 10 * 0.5 and three.y < 0
    assert typeset(r"\sqrt[n]{x+1}", 10).width > typeset(r"\sqrt{x+1}", 10).width


def test_binom_stacks_two_entries_in_parentheses_without_a_rule():
    box = typeset(r"\binom{n}{k}", 10)
    cps = [g.cp for g in box.glyphs]
    assert cps.count(0x28) == 1 and cps.count(0x29) == 1 and 0x2212 not in cps
    n = [g for g in box.glyphs if g.cp == 0x1D45B][0]
    k = [g for g in box.glyphs if g.cp == 0x1D458][0]
    assert n.y < 0 < k.y
    paren = [g for g in box.glyphs if g.cp == 0x28][0]
    assert paren.size > 10  # grown to fit the stack
    with pytest.raises(MathError):
        typeset(r"\binom{n}", 10)


@pytest.mark.parametrize("cmd,cp,count", [("hat", 0x5E, 1), ("tilde", 0x7E, 1), ("dot", 0x2E, 1),
                                          ("ddot", 0x2E, 2), ("vec", 0x2192, 1), ("grave", 0x60, 1)])
def test_accents_sit_centred_above_the_argument(cmd, cp, count):
    body = typeset("x", 10)
    box = typeset(rf"\{cmd}{{x}}", 10)
    marks = [g for g in box.glyphs if g.cp == cp]
    assert len(marks) == count
    from diagrams_as_code.text import _math_glyphs as mg
    for g in marks:  # ink bottom clears the top of the letter
        assert -g.y + mg.GLYPHS[cp][1] * g.size / mg.UNITS_PER_EM > body.height
    assert box.height > body.height and box.depth == body.depth
    assert box.width >= body.width


def test_accent_wider_than_its_argument_centres_the_argument():
    box = typeset(r"\vec{i}", 10)
    letter = [g for g in box.glyphs if g.cp == 0x1D456][0]
    assert letter.x > 0  # pushed right so the arrow overhangs both sides evenly
    assert typeset(r"\hat x", 10).glyphs == typeset(r"\hat{x}", 10).glyphs


@pytest.mark.parametrize("bad", [r"\hat", r"\vec", r"\binom", r"\sqrt[3]"])
def test_new_commands_need_their_arguments(bad):
    with pytest.raises(MathError):
        typeset(bad, 10)


@pytest.mark.parametrize("bad", [r"\bar", r"\sqrt", r"\frac", r"\frac{a}"])
def test_bar_and_sqrt_need_an_argument(bad):
    with pytest.raises(MathError):
        typeset(bad, 10)


def test_frac_stacks_numerator_over_denominator_about_a_rule():
    box = typeset(r"\frac{a+b}{c}", 10)
    num, den = typeset("a+b", 10.0 * 0.85), typeset("c", 10.0 * 0.85)
    assert box.width >= num.width
    assert box.height > num.height and box.depth > den.depth
    ys = {g.cp: g.y for g in box.glyphs}
    assert ys[typeset("c", 10).glyphs[0].cp] > 0  # denominator hangs below the baseline
    assert any(g.cp == 0x2212 and g.y < 0 for g in box.glyphs)  # the rule sits on the axis


def test_nested_frac_shrinks_and_dfrac_matches_frac():
    assert typeset(r"\dfrac{1}{2}", 10).glyphs == typeset(r"\frac{1}{2}", 10).glyphs
    inner = typeset(r"\frac{1}{2}", 10)
    nested = typeset(r"\frac{\frac{1}{2}}{3}", 10)
    assert nested.height > inner.height


def test_rightleftharpoons_stacks_a_right_arrow_over_a_left_arrow():
    box = typeset(r"A \rightleftharpoons B", 10)
    right = [g for g in box.glyphs if g.cp == 0x2192][0]
    left = [g for g in box.glyphs if g.cp == 0x2190][0]
    assert right.y < left.y and right.x == left.x
    assert [g.cp for g in typeset(r"\rightleftarrows", 10).glyphs] == [0x2192, 0x2190]


def test_ce_sets_species_upright_with_subscripts_and_charges():
    box = typeset(r"\ce{H2O}", 10)
    cps = [g.cp for g in box.glyphs]
    assert cps == [ord("H"), ord("2"), ord("O")]
    h, two = box.glyphs[0], box.glyphs[1]
    assert two.size < h.size and two.y > h.y
    ion = typeset(r"\ce{NH4+}", 10)
    plus = [g for g in ion.glyphs if g.cp == ord("+")][0]
    assert plus.size < 10 and plus.y < 0
    so4 = typeset(r"\ce{SO4^2-}", 10)
    two = [g for g in so4.glyphs if g.cp == ord("2")][0]
    assert two.y < 0 and any(g.cp == 0x2212 for g in so4.glyphs)
    reaction = typeset(r"\ce{2H2 + O2 <=> 2H2O}", 10)
    cps = [g.cp for g in reaction.glyphs]
    assert 0x2192 in cps and 0x2190 in cps and cps.count(ord("+")) == 1
    assert typeset(r"\ce{Ca(OH)2}", 10).glyphs[-1].cp == ord("2")
