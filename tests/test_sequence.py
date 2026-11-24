"""UML sequence diagrams (sequence.py): layout geometry, drawing, outputs and errors."""
from __future__ import annotations

import importlib.util
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.audit import audit_findings
from diagrams_as_code.output import render_all
from diagrams_as_code.sequence import SequenceDiagram
from diagrams_as_code.text.rich import TextStyle, measure

REPO = Path(__file__).resolve().parent.parent
EXAMPLES = sorted((REPO / "examples" / "sequence").glob("*.py"))


def _rich() -> SequenceDiagram:
    """A diagram that uses every feature."""
    seq = SequenceDiagram("rich", theme="iiot_light")
    user = seq.actor("User")
    web = seq.participant("Web")
    api = seq.participant("API")
    db = seq.participant("DB", kind="database")
    seq.message(user, web, "open page")
    seq.message(web, api, "GET /items with a long label so columns must widen", activate=True)
    seq.message(api, api, "validate $x^2 + y^2$", activate=True)
    seq.deactivate(api)
    with seq.loop("for each page"):
        seq.message(api, db, "SELECT", activate=True)
        seq.reply(db, api, "rows")
    with seq.alt("found", "missing") as alt:
        seq.reply(api, web, "200", deactivate=False)
        alt.branch()
        seq.reply(api, web, "404", deactivate=False)
    seq.deactivate(api)
    seq.note(web, "cached for 60 s", side="left")
    seq.note([api, db], "spanning note")
    seq.note(db, "over the database", side="over")
    seq.message(web, db, "async audit", style="async")
    seq.space(10)
    seq.reply(web, user, "rendered page")
    return seq


def _overlap(a, b) -> bool:
    return a.left < b.right and b.left < a.right and a.top < b.bottom and b.top < a.bottom


# ------------------------------------------------------------------ geometry
def test_columns_follow_participant_order():
    lay = _rich().layout()
    assert list(lay.columns) == sorted(lay.columns)
    assert len(set(lay.columns)) == 4


def test_rows_follow_event_order():
    lay = _rich().layout()
    tops = [min(y for _, y in m.points) for m in lay.messages]
    assert tops == sorted(tops) and len(set(tops)) == len(tops)
    assert all(m.points[0][1] > max(h.bottom for h in lay.headers) for m in lay.messages)


def test_message_ends_sit_on_their_lifelines_or_bars():
    lay = _rich().layout()
    col = dict(zip(["User", "Web", "API", "DB"], lay.columns))
    for m in lay.messages:
        (xa, _), (xb, _) = m.points[0], m.points[-1]
        assert abs(xa - col[m.src]) <= 15 and abs(xb - col[m.dst]) <= 15
        if m.src != m.dst:
            assert (xb > xa) == (col[m.dst] > col[m.src])
            assert len({y for _, y in m.points}) == 1  # horizontal


def test_self_call_is_a_loop_right_of_the_lifeline():
    lay = _rich().layout()
    m = next(m for m in lay.messages if m.src == m.dst)
    assert len(m.points) == 4
    xs = [x for x, _ in m.points]
    assert max(xs) > xs[0] and m.points[-1][1] > m.points[0][1]
    assert m.label_box.left > max(xs)


def test_labels_fit_between_the_ends_of_their_message():
    lay = _rich().layout()
    for m in lay.messages:
        if m.src == m.dst or m.label_box is None:
            continue
        lo, hi = sorted((m.points[0][0], m.points[-1][0]))
        assert lo < m.label_box.left and m.label_box.right < hi
        assert m.label_box.bottom <= m.points[0][1]


def test_label_width_matches_the_text_metrics():
    lay = _rich().layout()
    m = lay.messages[1]
    w, h = measure(m.label, TextStyle(size=12.0))
    assert m.label_box.width == pytest.approx(w) and m.label_box.height == pytest.approx(h)


def test_no_two_texts_overlap_and_none_cover_a_header():
    lay = _rich().layout()
    boxes = [b for _, b in lay.texts]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert not _overlap(a, b), (a, b)
        for h in lay.headers:
            assert not _overlap(a, h)


def test_lifelines_break_around_text():
    lay = _rich().layout()
    for x, top, bottom in lay.lifelines:
        for _, b in lay.texts:
            if b.left - 1 < x < b.right + 1:
                assert bottom <= b.top or top >= b.bottom, (x, top, bottom, b)


def test_nested_activation_steps_right():
    lay = _rich().layout()
    api = [b for i, b in lay.bars if i == 2]
    assert len(api) >= 2
    lefts = sorted({round(b.left, 2) for b in api})
    assert len(lefts) == 2 and lefts[1] - lefts[0] == pytest.approx(5.0)


def test_frames_enclose_their_messages_and_nest():
    seq = SequenceDiagram("frames")
    a, b, c = (seq.participant(n) for n in "ABC")
    with seq.loop("outer"):
        seq.message(a, b, "one")
        with seq.opt("inner"):
            seq.message(b, c, "two")
    lay = seq.layout()
    (k1, inner), (k2, outer) = lay.frames
    assert (k1, k2) == ("opt", "loop")
    assert outer.left < inner.left and inner.right < outer.right
    assert outer.top < inner.top and inner.bottom < outer.bottom
    two = lay.messages[1]
    assert inner.left < two.points[0][0] and two.points[-1][0] < inner.right
    assert inner.top < two.label_box.top and two.points[0][1] < inner.bottom


def test_long_label_widens_its_column_only_enough():
    short, long_ = SequenceDiagram("s"), SequenceDiagram("l")
    for seq, label in ((short, "x"), (long_, "a much longer label " * 4)):
        a, b = seq.participant("A"), seq.participant("B")
        seq.message(a, b, label)
    gap_short = short.layout().columns[1]
    gap_long = long_.layout().columns[1]
    w, _ = measure("a much longer label " * 4, TextStyle(size=12.0))
    assert gap_long > gap_short
    assert w < gap_long < w + 40


def test_math_labels_are_measured():
    seq = SequenceDiagram("m")
    a, b = seq.participant("A"), seq.participant("B")
    seq.message(a, b, "$\\frac{a}{b} + \\sqrt{x}$")
    m = seq.layout().messages[0]
    assert m.label_box.height > 15  # a fraction is taller than one text line


def test_autonumber_prefixes_labels():
    seq = SequenceDiagram("n", autonumber=True)
    a, b = seq.participant("A"), seq.participant("B")
    seq.message(a, b, "hello")
    seq.reply(b, a, "hi")
    texts = [t for t, _ in seq.layout().texts]
    assert texts[:2] == ["1. hello", "2. hi"]


def test_mirror_repeats_headers_below():
    seq = SequenceDiagram("m", mirror=True)
    a, b = seq.participant("A"), seq.participant("B")
    seq.message(a, b, "x")
    lay = seq.layout()
    assert len(lay.footers) == 2
    assert all(f.top > m.points[0][1] for f in lay.footers for m in lay.messages)
    assert sum(1 for s in seq.build().shapes if s.label == "A") == 2


def test_standalone_activation_and_unclosed_bars_are_drawn():
    seq = SequenceDiagram("a")
    a, b = seq.participant("A"), seq.participant("B")
    seq.activate(a)
    seq.message(a, b, "x", activate=True)
    lay = seq.layout()
    assert len(lay.bars) == 2
    assert all(b.height >= 12 for _, b in lay.bars)


# ------------------------------------------------------------------ drawing and outputs
def test_build_is_clean_under_the_audit():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        diag = _rich().build()
        assert not audit_findings(diag), [str(f) for f in audit_findings(diag)]


def test_svg_is_byte_stable():
    assert _rich().build().render_svg() == _rich().build().render_svg()
    seq = _rich()
    assert seq.build().render_svg() == seq.build().render_svg()


def test_build_contains_edges_text_and_headers():
    diag = _rich().build()
    assert isinstance(diag, Diagram)
    assert len(diag.edges) == 9
    assert any(s.kind == "database" and s.label == "DB" for s in diag.shapes)
    root = ET.fromstring(diag.render_svg())
    assert root.tag.endswith("svg")


def test_message_styles_map_to_edge_styles():
    seq = SequenceDiagram("s")
    a, b = seq.participant("A"), seq.participant("B")
    seq.message(a, b, "sync")
    seq.message(a, b, "async", style="async")
    seq.reply(b, a, "back")
    e1, e2, e3 = seq.build().edges
    assert (e1.style, e1.head) == ("solid", "triangle")
    assert (e2.style, e2.head) == ("solid", "open")
    assert (e3.style, e3.head) == ("dashed", "open")


def test_draw_into_an_existing_diagram_at_an_origin():
    seq = SequenceDiagram("s")
    a, b = seq.participant("A"), seq.participant("B")
    seq.message(a, b, "x")
    with Diagram("host", theme="paper") as d:
        box = seq.draw(d, origin=(300, 200))
    assert box.left == pytest.approx(300) and box.top == pytest.approx(200)
    assert min(s.bounds.x for s in d.shapes) >= 299.9


@pytest.mark.parametrize("theme", ["paper", "nord", "high_contrast"])
def test_renders_in_any_theme(theme: str):
    seq = _rich()
    seq.theme = theme
    diag = seq.build()
    assert diag.theme.name == theme
    assert not audit_findings(diag)


def test_render_all_writes_svg_pdf_and_png(tmp_path: Path):
    written = render_all(_rich().build(), tmp_path, "seq", formats=("svg", "pdf", "png", "bom"))
    assert written["svg"].read_text(encoding="utf-8").lstrip().startswith("<")
    assert written["pdf"].read_bytes().startswith(b"%PDF")
    png = written["png"]
    assert png.exists() and png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


# ------------------------------------------------------------------ errors
def test_errors():
    seq = SequenceDiagram("e")
    a = seq.participant("A")
    with pytest.raises(ValueError, match="already exists"):
        seq.participant("A")
    with pytest.raises(ValueError, match="kind"):
        seq.participant("X", kind="robot")
    with pytest.raises(ValueError, match="non-empty"):
        seq.participant("  ")
    b = seq.participant("B")
    with pytest.raises(ValueError, match="style"):
        seq.message(a, b, "x", style="wavy")
    with pytest.raises(ValueError, match="no participant"):
        seq.message("A", "Nobody", "x")
    with pytest.raises(TypeError):
        seq.message(a, 3, "x")  # type: ignore[arg-type]
    other = SequenceDiagram("o").participant("A")
    with pytest.raises(ValueError, match="another sequence"):
        seq.message(other, b, "x")
    with pytest.raises(ValueError, match="not active"):
        seq.deactivate(b)
    with pytest.raises(ValueError, match="not active"):
        seq.message(a, b, "x", deactivate=True)
    with pytest.raises(ValueError, match="side"):
        seq.note(a, "n", side="under")
    with pytest.raises(ValueError, match="needs text"):
        seq.note(a, "")
    with pytest.raises(ValueError, match="spanning"):
        seq.note([a, b], "n", side="left")
    with pytest.raises(ValueError, match="kind"):
        seq.frame("switch")
    with pytest.raises(ValueError, match="one guard"):
        seq.frame("loop", "a", "b")
    with pytest.raises(ValueError, match="height"):
        seq.space(-1)


def test_frame_errors():
    seq = SequenceDiagram("f")
    a, b = seq.participant("A"), seq.participant("B")
    with seq.loop("x") as loop:
        with pytest.raises(ValueError, match="only alt and par"):
            loop.branch("no")
    alt = seq.alt("a")
    with pytest.raises(RuntimeError, match="inside the frame"):
        alt.branch("b")
    with alt:
        with seq.opt("inner"):
            with pytest.raises(RuntimeError, match="innermost"):
                alt.branch("b")
    with pytest.raises(RuntimeError, match="only once"):
        with alt:
            pass
    open_frame = seq.opt("left open")
    open_frame.__enter__()
    with pytest.raises(RuntimeError, match="still open"):
        seq.build()


def test_empty_diagram_is_rejected():
    with pytest.raises(ValueError, match="at least one participant"):
        SequenceDiagram("empty").build()


def test_single_participant_and_empty_frame_work():
    seq = SequenceDiagram("one")
    a = seq.participant("Solo")
    seq.message(a, a, "think")
    with seq.opt("nothing"):
        pass
    seq.note(a, "alone", side="over")
    assert not audit_findings(seq.build())


# ------------------------------------------------------------------ the gallery
def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"_sequence_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gallery_has_three_examples():
    assert [p.stem[:2] for p in EXAMPLES] == ["01", "02", "03"]


@pytest.mark.parametrize("script", EXAMPLES, ids=lambda p: p.stem)
def test_example_builds_cleanly_and_matches_committed_svg(script: Path):
    module = _load(script)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        diag = module.diagram()
    assert not audit_findings(diag), [str(f) for f in audit_findings(diag)]
    committed = script.with_suffix(".svg")
    assert committed.exists(), f"run `uv run python {script.relative_to(REPO)}`"
    assert committed.read_text(encoding="utf-8") == module.diagram().render_svg()
