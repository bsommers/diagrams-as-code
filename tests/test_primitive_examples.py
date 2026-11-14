"""Every primitive has a focused example; each one builds and is free of visual defects."""
from __future__ import annotations

import importlib.util
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from diagrams_as_code.audit import audit_diagram

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = sorted((REPO / "examples" / "primitives").glob("*.py"))

#: Requirement -> the example that shows it.
REQUIREMENTS = {
    "PRIM-01": "01_text_caption_bracket",
    "PRIM-02": "02_polygon_polyline_path",
    "PRIM-03": "03_layer_bands",
    "PRIM-04": "04_nested_and_double_border",
    "PRIM-05": "05_edge_weights_and_arrowheads",
    "PRIM-06": "06_anchors_leaders_splines",
    "PRIM-07": "07_projected_solids",
    "PRIM-08": "08_z_order",
    "PRIM-09": "09_align_distribute_units",
}


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"_primitive_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_requirement_has_its_example():
    assert sorted(p.stem for p in SCRIPTS) == sorted(REQUIREMENTS.values())


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_example_builds_cleanly(script: Path, tmp_path: Path):
    module = _load(script)
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # no layout warnings in a showcase
        diagram = module.diagram()
        svg_path = module.build_diagram(tmp_path)
    root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
    assert root.tag.endswith("svg")
    assert (tmp_path / f"{script.stem}.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert not audit_diagram(diagram), dict(audit_diagram(diagram))
    assert diagram.theme.name == "paper"


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_committed_output_matches_the_script(script: Path):
    committed = REPO / "output" / "primitives" / f"{script.stem}.svg"
    assert committed.exists(), f"run `uv run python {script.relative_to(REPO)}`"
    assert committed.read_text(encoding="utf-8") == _load(script).diagram().render_svg()
