from __future__ import annotations

from pathlib import Path

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def _diag() -> Diagram:
    with Diagram("T") as d:
        a = d.shape("A").at(60, 80)
        b = d.shape("B").right_of(a)
        a >> b
    return d


def test_writes_requested_formats_in_canonical_order(tmp_path: Path) -> None:
    written = render_all(_diag(), tmp_path / "out", "demo", formats=("bom", "svg"))
    assert list(written) == ["svg", "bom"]
    assert written["svg"] == tmp_path / "out" / "demo.svg"
    assert written["bom"] == tmp_path / "out" / "demo_README.md"
    assert "./demo.svg" in written["bom"].read_text(encoding="utf-8")


def test_readme_name_override(tmp_path: Path) -> None:
    written = render_all(_diag(), tmp_path, "main_architecture", formats=("svg", "bom"), readme_name="main_README.md")
    assert written["bom"].name == "main_README.md"


def test_unknown_format_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="gif"):
        render_all(_diag(), tmp_path, "x", formats=("svg", "gif"))
