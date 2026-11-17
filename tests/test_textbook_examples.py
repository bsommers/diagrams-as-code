"""The textbook galleries: calculus_math, differential_equations, physics, finance, logic."""
from __future__ import annotations

import importlib.util
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from diagrams_as_code.audit import audit_findings

REPO = Path(__file__).resolve().parent.parent
DOMAINS = ("calculus_math", "differential_equations", "physics", "finance", "logic")
SCRIPTS = sorted(p for d in DOMAINS for p in (REPO / "examples" / d).glob("*.py"))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"_textbook_{path.parent.name}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("domain", DOMAINS)
def test_each_gallery_has_ten_figures(domain: str):
    stems = [p.stem for p in SCRIPTS if p.parent.name == domain]
    assert len(stems) == 10
    assert [s[:2] for s in stems] == [f"{i:02d}" for i in range(1, 11)]


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_figure_builds_cleanly(script: Path, tmp_path: Path):
    module = _load(script)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        diagram = module.diagram()
        svg_path = module.build_diagram(tmp_path)
    assert ET.fromstring(svg_path.read_text(encoding="utf-8")).tag.endswith("svg")
    assert not audit_findings(diagram), [str(f) for f in audit_findings(diagram)]
    assert diagram.theme.name == "paper"
    assert any(s.kind == "caption" for s in diagram.shapes), "a figure needs a caption"


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_committed_output_matches_the_script(script: Path):
    committed = REPO / "output" / script.parent.name / f"{script.stem}.svg"
    assert committed.exists(), f"run `uv run python {script.relative_to(REPO)} output/{script.parent.name}`"
    assert committed.read_text(encoding="utf-8") == _load(script).diagram().render_svg()
