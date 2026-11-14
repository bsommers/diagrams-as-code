"""Vector PDF export: file structure, drawing operators, text, and gallery coverage."""
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import warnings
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

import pytest

from diagrams_as_code import Diagram, PDFExportError, Style, svg_to_pdf
from diagrams_as_code.cli import main
from diagrams_as_code.output import DEFAULT_FORMATS, FORMATS, render_all
from diagrams_as_code.pdf import ATTRIBUTES, ELEMENTS, PX_TO_PT
from diagrams_as_code.text import text_width

REPO = Path(__file__).resolve().parent.parent
GALLERY = sorted((REPO / "output").rglob("*.svg"))
TECHNICAL = sorted((REPO / "output" / "technical").glob("*.svg"))


def _svg(body: str, width: float = 200, height: float = 100, defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}"><defs>{defs}</defs>{body}</svg>'
    )


def _objects(pdf: bytes) -> dict[int, bytes]:
    """Every indirect object, found through the cross-reference table."""
    start = int(re.search(rb"startxref\n(\d+)\n%%EOF\n$", pdf)[1])
    assert pdf[start:start + 5] == b"xref\n"
    lines = pdf[start:].split(b"\n")
    count = int(lines[1].split()[1])
    out = {}
    for number in range(1, count):
        offset = int(lines[2 + number][:10])
        head = f"{number} 0 obj\n".encode()
        assert pdf[offset:offset + len(head)] == head, f"object {number} is not at its xref offset"
        out[number] = pdf[offset + len(head):pdf.index(b"\nendobj\n", offset)]
    return out


def _stream(obj: bytes) -> bytes:
    head, _, rest = obj.partition(b"\nstream\n")
    data = rest[: -len(b"\nendstream")]
    assert int(re.search(rb"/Length (\d+)", head)[1]) == len(data)
    return zlib.decompress(data) if b"/FlateDecode" in head else data


def _content(pdf: bytes) -> str:
    objs = _objects(pdf)
    page = next(o for o in objs.values() if b"/Type /Page " in o)
    return _stream(objs[int(re.search(rb"/Contents (\d+) 0 R", page)[1])]).decode("ascii")


def _diag() -> Diagram:
    with Diagram("Demo") as d:
        a = d.shape("Alpha").at(60, 80)
        b = d.shape("Beta").right_of(a)
        a >> b
    return d


# ------------------------------------------------------------------ file layout

def test_file_structure_is_valid() -> None:
    pdf = _diag().render_pdf()
    assert pdf.startswith(b"%PDF-1.4\n")
    assert pdf.endswith(b"%%EOF\n")
    objs = _objects(pdf)
    trailer = pdf[pdf.rindex(b"trailer"):]
    assert int(re.search(rb"/Size (\d+)", trailer)[1]) == len(objs) + 1
    root = objs[int(re.search(rb"/Root (\d+) 0 R", trailer)[1])]
    assert b"/Type /Catalog" in root
    # every reference points at an object that exists
    for body in objs.values():
        head = body.partition(b"\nstream\n")[0]
        for ref in re.findall(rb"(\d+) 0 R", head):
            assert int(ref) in objs
    info = objs[int(re.search(rb"/Info (\d+) 0 R", trailer)[1])]
    assert b"/Title (Demo)" in info


def test_page_size_is_the_svg_size_in_points() -> None:
    d = _diag()
    pdf = d.render_pdf()
    svg = ET.fromstring(d.render_svg())
    box = re.search(rb"/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]", pdf)
    assert float(box[1]) == pytest.approx(float(svg.get("width")) * PX_TO_PT, abs=1e-3)
    assert float(box[2]) == pytest.approx(float(svg.get("height")) * PX_TO_PT, abs=1e-3)


def test_output_is_reproducible_and_has_no_timestamp() -> None:
    assert _diag().render_pdf() == _diag().render_pdf()
    assert b"CreationDate" not in _diag().render_pdf()


def test_uncompressed_stream_is_readable_text() -> None:
    pdf = svg_to_pdf(_svg('<rect x="1" y="2" width="30" height="40" fill="#FF0000"/>'), compress=False)
    assert b"/FlateDecode" not in pdf
    assert b"1 0 0 rg" in pdf


def test_non_ascii_title_is_written_as_utf16() -> None:
    pdf = svg_to_pdf(_svg(""), title="Größe")
    assert b"/Title <FEFF" in pdf


# ---------------------------------------------------------------------- shapes

def test_rect_fill_and_stroke() -> None:
    c = _content(svg_to_pdf(_svg('<rect x="10" y="20" width="30" height="40" fill="#FF0000" stroke="#0000FF" stroke-width="2"/>')))
    assert "1 0 0 rg" in c and "0 0 1 RG" in c and "2 w" in c
    assert "10 20 m\n40 20 l\n40 60 l\n10 60 l\nh\nB" in c


def test_fill_only_and_stroke_only_use_their_own_operators() -> None:
    c = _content(svg_to_pdf(_svg('<rect width="5" height="5" fill="#000000"/><line x1="0" y1="0" x2="9" y2="9" fill="none" stroke="#000000" stroke-width="1"/>')))
    assert "h\nf\n" in c
    assert "0 0 m\n9 9 l\nS\n" in c


def test_nothing_is_painted_without_fill_or_stroke() -> None:
    c = _content(svg_to_pdf(_svg('<rect width="5" height="5" fill="none"/>')))
    assert " m\n" not in c


def test_rounded_rect_uses_curves_and_clamps_the_radius() -> None:
    c = _content(svg_to_pdf(_svg('<rect x="0" y="0" width="20" height="10" rx="50" fill="#000000"/>')))
    assert c.count(" c\n") == 4
    assert "10 0 m" in c  # rx clamped to half the width, ry to half the height


def test_percent_size_fills_the_canvas() -> None:
    c = _content(svg_to_pdf(_svg('<rect width="100%" height="100%" fill="#FFFFFF"/>', 200, 100)))
    assert "0 0 m\n200 0 l\n200 100 l\n0 100 l\nh\nf" in c


def test_circle_ellipse_polyline_polygon() -> None:
    c = _content(svg_to_pdf(_svg(
        '<circle cx="50" cy="50" r="10" fill="#000000"/>'
        '<ellipse cx="50" cy="50" rx="20" ry="5" fill="#000000"/>'
        '<polyline points="0,0 5,5 10,0" fill="none" stroke="#000000" stroke-width="1"/>'
        '<polygon points="0,0 5,5 10,0" fill="#000000"/>'
    )))
    assert "60 50 m" in c and "70 50 m" in c
    assert "0 0 m\n5 5 l\n10 0 l\nS" in c
    assert "0 0 m\n5 5 l\n10 0 l\nh\nf" in c


def test_path_arcs_and_relative_commands_become_lines_and_curves() -> None:
    c = _content(svg_to_pdf(_svg('<path d="M 0 0 h 10 v 10 A 5 5 0 0 1 0 10 z" fill="#000000"/>')))
    assert "0 0 m\n10 0 l\n10 10 l" in c
    assert " c\n" in c and "h\nf" in c


def test_dash_cap_and_join() -> None:
    c = _content(svg_to_pdf(_svg(
        '<path d="M 0 0 L 9 9" fill="none" stroke="#000000" stroke-width="1" '
        'stroke-dasharray="6,4" stroke-linecap="round" stroke-linejoin="round"/>'
    )))
    assert "[6 4] 0 d" in c and "1 J" in c and "1 j" in c


def test_odd_dash_list_is_repeated() -> None:
    c = _content(svg_to_pdf(_svg('<path d="M 0 0 L 9 9" fill="none" stroke="#000000" stroke-dasharray="3"/>')))
    assert "[3 3] 0 d" in c


def test_fill_opacity_becomes_a_graphics_state() -> None:
    pdf = svg_to_pdf(_svg('<rect width="5" height="5" fill="#000000" fill-opacity="0.25"/>'))
    assert b"/ca 0.25" in pdf
    assert "/G1 gs" in _content(pdf)


def test_group_opacity_is_a_transparency_group() -> None:
    pdf = svg_to_pdf(_svg('<g opacity="0.5"><rect width="5" height="5" fill="#000000"/><rect x="2" width="5" height="5" fill="#000000"/></g>'))
    objs = _objects(pdf)
    form = next(o for o in objs.values() if b"/Subtype /Form" in o)
    assert b"/S /Transparency" in form
    assert _stream(form).count(b"\nf\n") == 2
    assert "/X1 Do" in _content(pdf)


def test_transform_is_applied_in_svg_order() -> None:
    c = _content(svg_to_pdf(_svg('<g transform="translate(10, 20) scale(2)"><rect width="5" height="5" fill="#000000"/></g>')))
    assert "2 0 0 2 10 20 cm" in c


def test_y_axis_is_flipped_onto_the_page() -> None:
    c = _content(svg_to_pdf(_svg("", 200, 100)))
    assert c.splitlines()[0] == "0.75 0 0 -0.75 0 75 cm"


# --------------------------------------------------------------------- markers

MARKER = (
    '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="9" markerHeight="9" '
    'orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#123456"/></marker>'
)


def test_marker_is_placed_scaled_and_rotated_at_the_path_end() -> None:
    c = _content(svg_to_pdf(_svg(
        '<path d="M 10 10 L 10 60" fill="none" stroke="#000000" stroke-width="2" marker-end="url(#arrow)"/>',
        defs=MARKER,
    )))
    # scale = 9/10 * stroke width; pointing down (+y); reference point on the path end
    assert "0 1.8 -1.8 0 19 45.6 cm" in c
    assert "0 0 10 10 re W n" in c
    assert "0.0706 0.2039 0.3373 rg" in c


def test_start_marker_points_backwards() -> None:
    c = _content(svg_to_pdf(_svg(
        '<path d="M 10 10 L 60 10" fill="none" stroke="#000000" stroke-width="1" marker-start="url(#arrow)"/>',
        defs=MARKER,
    )))
    assert "-0.9 0 0 -0.9 17.2 14.5 cm" in c


def test_marker_follows_a_curve_tangent() -> None:
    c = _content(svg_to_pdf(_svg(
        '<path d="M 0 0 C 50 0, 100 0, 100 50" fill="none" stroke="#000000" stroke-width="1" marker-end="url(#arrow)"/>',
        defs=MARKER,
    )))
    assert "0 0.9 -0.9 0 104.5 42.8 cm" in c


def test_undefined_marker_is_an_error() -> None:
    with pytest.raises(PDFExportError, match="not defined"):
        svg_to_pdf(_svg('<path d="M 0 0 L 9 9" stroke="#000000" marker-end="url(#nope)"/>'))


# ---------------------------------------------------------------------- shadow

SHADOW = '<filter id="shadow"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/></filter>'


def test_shadow_is_drawn_under_the_group_and_fades_outwards() -> None:
    pdf = svg_to_pdf(_svg('<g filter="url(#shadow)"><rect x="50" y="20" width="40" height="30" fill="#FFFFFF"/></g>', defs=SHADOW))
    c = _content(pdf)
    body = c.index("1 1 1 rg")
    rings = [float(w) for w in re.findall(r"gs ([\d.]+) w", c[:body])]
    assert rings == sorted(rings, reverse=True) and len(rings) == 6
    assert "50 24 m" in c[:body]  # offset by dy
    alphas = {tag: float(a) for tag, a in re.findall(rb"/(G\d+) << /Type /ExtGState /ca ([\d.]+)", pdf)}
    used = re.findall(r"/(G\d+) gs [\d.]+ w", c[:body])
    values = [alphas[t.encode()] for t in used]
    assert values == sorted(values)  # widest ring is the faintest
    assert all(0.0 < v < 0.4 for v in values)


def test_shadow_ignores_unfilled_outlines() -> None:
    c = _content(svg_to_pdf(_svg('<g filter="url(#shadow)"><rect width="9" height="9" fill="none" stroke="#000000"/></g>', defs=SHADOW)))
    assert "gs" not in c


# ------------------------------------------------------------------------ text

def test_text_is_upright_at_its_baseline() -> None:
    pdf = svg_to_pdf(_svg('<text x="10" y="30" fill="#000000" font-family="Helvetica, sans-serif" font-size="12">Hi (x)</text>'))
    c = _content(pdf)
    assert "/F1 12 Tf 1 0 0 -1 10 30 Tm (Hi \\(x\\)) Tj" in c
    assert b"/BaseFont /Helvetica " in pdf and b"/WinAnsiEncoding" in pdf


@pytest.mark.parametrize("attrs, name", [
    ('font-weight="700"', "Helvetica-Bold"),
    ('font-weight="500"', "Helvetica"),
    ('font-style="italic"', "Helvetica-Oblique"),
    ('font-weight="bold" font-style="italic"', "Helvetica-BoldOblique"),
    ("font-family=\"'STIX Two Text', Times, serif\"", "Times-Roman"),
    ("font-family=\"'STIX Two Text', Times, serif\" font-weight=\"700\"", "Times-Bold"),
    ("font-family=\"'STIX Two Text', Times, serif\" font-style=\"italic\"", "Times-Italic"),
    ('font-family="Menlo, monospace"', "Courier"),
])
def test_font_selection(attrs: str, name: str) -> None:
    pdf = svg_to_pdf(_svg(f'<text x="0" y="10" font-size="10" {attrs}>a</text>'))
    assert f"/BaseFont /{name} ".encode() in pdf


def test_middle_and_end_anchors_use_the_measured_width() -> None:
    width = text_width("Hello", 20)
    for anchor, shift in (("middle", width / 2), ("end", width)):
        c = _content(svg_to_pdf(_svg(f'<text x="100" y="50" font-size="20" text-anchor="{anchor}">Hello</text>')))
        x = float(re.search(r"1 0 0 -1 ([\d.]+) 50 Tm", c)[1])
        assert x == pytest.approx(100 - shift, abs=1e-3)


def test_font_widths_in_the_file_match_the_layout_metrics() -> None:
    pdf = svg_to_pdf(_svg('<text x="0" y="10" font-size="10">a</text>'))
    widths = [int(w) for w in re.search(rb"/FirstChar 32 /LastChar 255 /Widths \[([\d ]+)\]", pdf)[1].split()]
    assert len(widths) == 224
    assert widths[ord("A") - 32] == round(text_width("A", 1000))
    assert widths[ord(" ") - 32] == round(text_width(" ", 1000))


def test_text_length_stretches_the_run() -> None:
    natural = text_width("Hello", 20)
    c = _content(svg_to_pdf(_svg(
        f'<text x="5" y="50" font-size="20" xml:space="preserve" textLength="{natural * 1.25}" '
        'lengthAdjust="spacingAndGlyphs">Hello</text>'
    )))
    assert "125 Tz" in c


def test_serif_text_is_measured_with_serif_widths() -> None:
    c = _content(svg_to_pdf(_svg(
        '<text x="0" y="50" font-size="2048" font-family="Times, serif" textLength="1479">A</text>'
    )))
    assert "Tz" not in c  # Times "A" is 1479/2048 em (0.722) wide, so nothing to stretch
    c = _content(svg_to_pdf(_svg('<text x="0" y="50" font-size="2048" textLength="1479">A</text>')))
    assert "Tz" in c  # the sans "A" is narrower


def test_tspans_are_lines() -> None:
    c = _content(svg_to_pdf(_svg(
        '<text x="50" y="20" font-size="10" text-anchor="start"><tspan x="50" dy="0">one</tspan> <tspan x="50" dy="12">two</tspan></text>'
    )))
    assert "50 20 Tm (one) Tj" in c and "50 32 Tm (two) Tj" in c


def test_whitespace_is_collapsed_unless_preserved() -> None:
    plain = _content(svg_to_pdf(_svg('<text x="0" y="9" font-size="9">  a   b </text>')))
    kept = _content(svg_to_pdf(_svg('<text x="0" y="9" font-size="9" xml:space="preserve"> a  b</text>')))
    assert "(a b) Tj" in plain
    assert "( a  b) Tj" in kept


def test_latin1_and_symbol_characters() -> None:
    pdf = svg_to_pdf(_svg('<text x="0" y="20" font-size="10">5° a → b − π</text>'))
    c = _content(pdf)
    assert "(5\\260 a ) Tj" in c
    assert "(\\256) Tj" in c and "(-) Tj" in c and "(p) Tj" in c
    assert b"/BaseFont /Symbol" in pdf
    # the text after a symbol starts where the layout metrics put it
    x = float(re.search(r"1 0 0 -1 ([\d.]+) 20 Tm \( b \) Tj", c)[1])
    assert x == pytest.approx(text_width("5° a →", 10), abs=1e-3)


def test_character_no_standard_font_has_warns_and_draws_a_question_mark() -> None:
    with pytest.warns(UserWarning, match="漢"):
        pdf = svg_to_pdf(_svg('<text x="0" y="20" font-size="10">a漢</text>'))
    assert "(a?) Tj" in _content(pdf)


def test_text_with_no_fill_is_not_drawn() -> None:
    assert "BT" not in _content(svg_to_pdf(_svg('<text x="0" y="9" fill="none">a</text>')))


# ---------------------------------------------------------------------- errors

@pytest.mark.parametrize("body, match", [
    ("<image/>", "<image>"),
    ('<rect width="1" height="1" clip-path="url(#c)"/>', "clip-path"),
    ('<rect width="1" height="1" fill="url(#grad)"/>', "colour"),
    ('<g transform="skewX(3)"/>', "transform"),
    ('<path d="M 0 0 L 1 1" marker-end="arrow"/>', "marker-end"),
    ('<text x="0" y="0"><a>x</a></text>', "inside <text>"),
])
def test_unsupported_svg_is_an_error_not_a_silent_gap(body: str, match: str) -> None:
    with pytest.raises(PDFExportError, match=match):
        svg_to_pdf(_svg(body))


def test_malformed_input_is_an_error() -> None:
    with pytest.raises(PDFExportError, match="well-formed"):
        svg_to_pdf("<svg")
    with pytest.raises(PDFExportError, match="not an SVG"):
        svg_to_pdf("<html/>")


@pytest.mark.parametrize("colour, rgb", [
    ("#F80", "1 0.5333 0 rg"), ("rgb(255, 0, 0)", "1 0 0 rg"), ("navy", "0 0 0.502 rg"),
])
def test_colour_forms(colour: str, rgb: str) -> None:
    assert rgb in _content(svg_to_pdf(_svg(f'<rect width="1" height="1" fill="{colour}"/>')))


# ------------------------------------------------------------- diagram and CLI

def test_render_pdf_writes_the_file_and_returns_the_bytes(tmp_path: Path) -> None:
    target = tmp_path / "deep" / "demo.pdf"
    data = _diag().render_pdf(target)
    assert target.read_bytes() == data
    c = _content(data)
    assert "(Alpha) Tj" in c and "(Beta) Tj" in c


def test_render_pdf_leaves_out_the_interactive_overlay() -> None:
    d = _diag()
    d.interactive = True
    assert "<script" in d.render_svg()
    assert d.render_pdf().startswith(b"%PDF")


def test_styled_and_translucent_shapes_export() -> None:
    with Diagram("S", theme="paper") as d:
        a = d.shape("A", style=Style(fill="#DDEEFF", fill_opacity=0.5, dash="4,3")).at(40, 40)
        b = d.shape("$x_i^2 \\leq \\alpha$").right_of(a)
        a >> b
    pdf = d.render_pdf()
    assert b"/ca 0.5" in pdf
    assert "[4 3] 0 d" in _content(pdf)


def test_render_all_writes_pdf_only_when_asked(tmp_path: Path) -> None:
    assert "pdf" in FORMATS and "pdf" not in DEFAULT_FORMATS
    written = render_all(_diag(), tmp_path, "demo", formats=("svg", "pdf"))
    assert list(written) == ["svg", "pdf"]
    assert written["pdf"].read_bytes().startswith(b"%PDF-1.4")


def test_cli_format_pdf(tmp_path: Path) -> None:
    script = tmp_path / "demo.py"
    script.write_text(
        "from diagrams_as_code import Diagram\n\n\n"
        "def diagram() -> Diagram:\n"
        "    with Diagram('Demo') as d:\n"
        "        a, b = d.shape('A'), d.shape('B')\n"
        "        a >> b\n"
        "    return d\n",
        encoding="utf-8",
    )
    out = tmp_path / "out"
    assert main(["render", str(script), "--out", str(out), "--format", "pdf"]) == 0
    assert [p.suffix for p in out.rglob("*") if p.is_file()] == [".pdf"]


# --------------------------------------------------------------------- gallery

def test_gallery_exists() -> None:
    assert len(GALLERY) >= 100 and len(TECHNICAL) == 11


def test_the_writer_knows_every_element_and_attribute_the_renderer_writes() -> None:
    """A new SVG construct in the renderer must be taught to the PDF writer."""
    elements, attributes = set(), set()
    for path in GALLERY:
        for el in ET.parse(path).iter():
            elements.add(el.tag.rsplit("}", 1)[-1])
            attributes.update(k.rsplit("}", 1)[-1] for k in el.attrib)
    assert elements <= ELEMENTS, sorted(elements - ELEMENTS)
    assert attributes <= ATTRIBUTES, sorted(attributes - ATTRIBUTES)


@pytest.mark.parametrize("path", GALLERY, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_every_gallery_diagram_exports(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # every character has a glyph
        pdf = svg_to_pdf(svg)
    content = _content(pdf)
    _objects(pdf)
    # balanced state, and every piece of text in the SVG is text in the PDF
    lines = content.splitlines()
    assert lines.count("q") == lines.count("Q")
    assert content.count("BT\n") == content.count("ET\n")
    runs = sum(
        1
        for el in ET.fromstring(svg).iter()
        if el.tag.endswith("}text") or el.tag.endswith("}tspan")
        if (el.text or "").strip()
    )
    assert content.count("BT\n") == runs


# ------------------------------------------------- rendered check, when possible

BLOCK = 8  # px; pictures are compared block by block, so anti-aliasing does not count


def _decode_png(data: bytes) -> tuple[int, int, int, bytes]:
    name = "golden_images"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, REPO / "tools" / "golden_images.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name].decode_png(data)


def _blocks(png: bytes, width: int, height: int) -> list[float]:
    """Mean brightness of each ``BLOCK`` x ``BLOCK`` tile of the top-left ``width`` x ``height``."""
    w, _h, channels, pixels = _decode_png(png)
    stride = w * channels
    out = []
    for by in range(0, height - BLOCK + 1, BLOCK):
        rows = [pixels[(by + k) * stride:(by + k + 1) * stride] for k in range(BLOCK)]
        for bx in range(0, width - BLOCK + 1, BLOCK):
            lo, hi = bx * channels, (bx + BLOCK) * channels
            total = 0
            for row in rows:
                cell = row[lo:hi]
                # skip the alpha channel
                total += sum(cell) - (sum(cell[3::4]) if channels == 4 else 0)
            out.append(total / (BLOCK * BLOCK * 3.0))
    return out


def _rendered_difference(svg_path: Path, tmp_path: Path) -> float:
    """Share (%) of tiles that clearly differ between the SVG and its PDF, both rasterized."""
    resvg_py = pytest.importorskip("resvg_py")
    svg = svg_path.read_text(encoding="utf-8")
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(svg_to_pdf(svg))
    subprocess.run(["pdftoppm", "-r", "96", "-png", "-singlefile", str(pdf), str(tmp_path / "pdf")], check=True)
    from_svg = bytes(resvg_py.svg_to_bytes(svg_string=svg))
    from_pdf = (tmp_path / "pdf.png").read_bytes()
    (aw, ah), (bw, bh) = _decode_png(from_svg)[:2], _decode_png(from_pdf)[:2]
    assert abs(aw - bw) <= 1 and abs(ah - bh) <= 1
    w, h = min(aw, bw), min(ah, bh)
    a, b = _blocks(from_svg, w, h), _blocks(from_pdf, w, h)
    return sum(1 for p, q in zip(a, b) if abs(p - q) > 40.0) / len(a) * 100.0


@pytest.mark.skipif(shutil.which("pdftoppm") is None, reason="needs poppler's pdftoppm")
@pytest.mark.parametrize("path", TECHNICAL, ids=lambda p: p.stem)
def test_technical_figure_pdf_looks_like_its_svg(path: Path, tmp_path: Path) -> None:
    difference = _rendered_difference(path, tmp_path)
    print(f"{path.stem}: {difference:.3f}% of tiles differ")
    assert difference < 1.0


@pytest.mark.skipif(shutil.which("pdftoppm") is None, reason="needs poppler's pdftoppm")
def test_the_rendered_check_notices_a_missing_element(tmp_path: Path) -> None:
    """The comparison above is only worth having if it fails when the PDF is wrong."""
    resvg_py = pytest.importorskip("resvg_py")
    full = _svg('<rect width="100%" height="100%" fill="#FFFFFF"/><rect x="40" y="20" width="60" height="50" fill="#000000"/>')
    missing = _svg('<rect width="100%" height="100%" fill="#FFFFFF"/>')
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(svg_to_pdf(missing))
    subprocess.run(["pdftoppm", "-r", "96", "-png", "-singlefile", str(pdf), str(tmp_path / "pdf")], check=True)
    a = _blocks(bytes(resvg_py.svg_to_bytes(svg_string=full)), 200, 100)
    b = _blocks((tmp_path / "pdf.png").read_bytes(), 200, 100)
    assert sum(1 for p, q in zip(a, b) if abs(p - q) > 40.0) / len(a) * 100.0 > 10.0
