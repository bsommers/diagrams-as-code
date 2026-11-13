"""``diagrams-as-code lint`` and the named findings behind it (VIS-02)."""
from __future__ import annotations

from pathlib import Path

from diagrams_as_code import Diagram, Shape
from diagrams_as_code.audit import DEFECTS, Finding, audit_diagram, audit_findings
from diagrams_as_code.cli import main

REPO = Path(__file__).resolve().parent.parent

CLEAN = '''
from diagrams_as_code import Diagram


def diagram() -> Diagram:
    with Diagram("Clean", layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    return d
'''

OVERLAPPING = '''
from diagrams_as_code import Diagram


def diagram() -> Diagram:
    with Diagram("Overlap") as d:
        d.shape("Left").at(100, 100)
        d.shape("Right").at(150, 110)
    return d
'''


def _write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _overlap() -> Diagram:
    with Diagram("t") as d:
        d.add(Shape("a", "Left")).at(100, 100)
        d.add(Shape("b", "Right")).at(150, 110)
    return d


def test_findings_name_the_elements_involved():
    findings = audit_findings(_overlap())
    assert findings == [Finding("node_overlap", "'Left' overlaps 'Right'")]
    assert str(findings[0]) == "node_overlap: 'Left' overlaps 'Right'"


def test_counts_are_the_findings_tallied():
    d = _overlap()
    assert audit_diagram(d) == {"node_overlap": 1}
    assert all(f.kind in DEFECTS for f in audit_findings(d))


def test_an_unlabelled_element_is_named_by_its_id():
    with Diagram("t") as d:
        d.add(Shape("first", "")).at(100, 100)
        d.add(Shape("second", "")).at(150, 110)
    assert audit_findings(d)[0].detail == "first overlaps second"


def test_a_line_to_a_point_set_on_a_shape_is_not_a_line_through_it():
    with Diagram("t", theme="paper") as d:
        box = d.shape("Target", 160, 100).at(300, 100)
        d.leader("a spot on the box", (360, 150), at=(60, 60))
    assert not audit_findings(d)
    # The same line carried on to the far side does cross the box.
    with Diagram("t", theme="paper") as d:
        box = d.shape("Target", 160, 100).at(300, 100)
        d.leader("past the box", (560, 180), at=(60, 100))
    assert [f.kind for f in audit_findings(d)] == ["edge_through_node"]
    assert "crosses 'Target'" in audit_findings(d)[0].detail


def test_a_bracket_beside_nested_shapes_does_not_overlap_their_container():
    with Diagram("t", theme="paper") as d:
        panel = d.shape("", 300, 200).at(100, 100)
        top = d.shape("One", 120, 40).inside(panel, "top_left", 20, 20)
        bottom = d.shape("Two", 120, 40).inside(panel, "top_left", 20, 120)
        d.bracket(side="right", shape="square").spanning(top, bottom)
    assert not audit_findings(d)


def test_lint_clean_script_exits_0(tmp_path: Path, capsys):
    assert main(["lint", str(_write(tmp_path / "clean.py", CLEAN))]) == 0
    assert capsys.readouterr().out.strip() == "1 diagram checked, 0 findings"


def test_lint_reports_each_finding_with_its_script_and_exits_1(tmp_path: Path, capsys):
    script = _write(tmp_path / "bad.py", OVERLAPPING)
    assert main(["lint", str(script)]) == 1
    out = capsys.readouterr().out.splitlines()
    assert out == [f"{script}: node_overlap: 'Left' overlaps 'Right'", "1 diagram checked, 1 finding"]


def test_lint_walks_directories_and_ignore_drops_a_kind(tmp_path: Path, capsys):
    _write(tmp_path / "a" / "clean.py", CLEAN)
    _write(tmp_path / "b" / "bad.py", OVERLAPPING)
    assert main(["lint", str(tmp_path)]) == 1
    assert "2 diagrams checked, 1 finding" in capsys.readouterr().out
    assert main(["lint", str(tmp_path), "--ignore", "node_overlap", "--quiet"]) == 0
    assert capsys.readouterr().out == ""


def test_lint_usage_and_script_errors(tmp_path: Path, capsys):
    assert main(["lint", str(tmp_path), "--ignore", "no_such_kind"]) == 2
    assert main(["lint", str(tmp_path)]) == 1  # nothing to check
    broken = _write(tmp_path / "broken.py", "def diagram():\n    raise RuntimeError('boom')\n")
    assert main(["lint", str(broken)]) == 1
    assert "boom" in capsys.readouterr().err


def test_lint_reports_layout_warnings(tmp_path: Path, capsys):
    script = _write(
        tmp_path / "warns.py",
        "import warnings\nfrom diagrams_as_code import Diagram\n\n\ndef diagram():\n"
        "    warnings.warn('something to look at')\n"
        "    with Diagram('W') as d:\n        d.shape('A')\n    return d\n",
    )
    assert main(["lint", str(script)]) == 1
    assert f"{script}: layout_warning: something to look at" in capsys.readouterr().out


def test_every_example_lints_clean(capsys):
    assert main(["lint", str(REPO / "examples"), "--quiet"]) == 0, capsys.readouterr().out
