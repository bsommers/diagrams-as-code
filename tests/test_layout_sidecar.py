from __future__ import annotations

import json
from pathlib import Path

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.layout import LayoutWarning, export_layout, load_layout_file
from diagrams_as_code.layout.sidecar import element_key


def _build(layout_file=None) -> Diagram:
    with Diagram(layout="auto", layout_file=layout_file) as d:
        with d.group("Cloud") as g:
            broker = d.shape("Broker")
            db = d.shape("DB", id="tsdb")
            broker >> db
        edge = d.shape("Edge")
        edge >> broker
    return d


def _positions(d: Diagram) -> dict[str, tuple[float, float]]:
    return {element_key(e): (e.bounds.x, e.bounds.y) for e in d.all_elements()}


def test_keys_are_label_paths_unless_the_id_was_explicit() -> None:
    d = _build()
    assert sorted(_positions(d)) == ["Cloud", "Cloud/Broker", "Edge", "tsdb"]


def test_export_format_is_stable(tmp_path: Path) -> None:
    path = export_layout(_build(), tmp_path / "x.layout.json")
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    assert data["version"] == 1
    assert list(data["positions"]) == sorted(data["positions"])
    assert text.endswith("}\n") and '\n  "positions"' in text


def test_round_trip_reproduces_every_position(tmp_path: Path) -> None:
    original = _build()
    path = export_layout(original, tmp_path / "l.json")
    assert _positions(_build(layout_file=path)) == _positions(original)


def test_editing_a_shape_entry_moves_that_shape(tmp_path: Path) -> None:
    path = export_layout(_build(), tmp_path / "l.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["positions"]["Edge"] = {"x": 700.0, "y": 500.0}
    path.write_text(json.dumps(data), encoding="utf-8")
    assert _positions(_build(layout_file=path))["Edge"] == (700.0, 500.0)


def test_editing_a_group_entry_moves_the_whole_group(tmp_path: Path) -> None:
    before = _positions(_build())
    path = export_layout(_build(), tmp_path / "l.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    gx, gy = before["Cloud"]
    data["positions"]["Cloud"] = {"x": gx + 100.0, "y": gy + 50.0}
    path.write_text(json.dumps(data), encoding="utf-8")
    after = _positions(_build(layout_file=path))
    for key in ("Cloud", "Cloud/Broker", "tsdb"):
        assert after[key] == (before[key][0] + 100.0, before[key][1] + 50.0)
    assert after["Edge"] == before["Edge"]


def test_missing_file_is_a_no_op(tmp_path: Path) -> None:
    assert load_layout_file(tmp_path / "absent.json") == {}
    assert _positions(_build(layout_file=tmp_path / "absent.json")) == _positions(_build())


def test_stale_entry_warns(tmp_path: Path) -> None:
    path = tmp_path / "l.json"
    path.write_text(json.dumps({"version": 1, "positions": {"Gone": {"x": 1, "y": 2}}}), encoding="utf-8")
    with pytest.warns(LayoutWarning, match="stale layout entry: 'Gone'"):
        _build(layout_file=path)


@pytest.mark.parametrize(
    "content, match",
    [
        ("{not json", "invalid JSON"),
        ('{"version": 2, "positions": {}}', "version"),
        ('{"version": 1, "positions": {"Edge": {"x": "a", "y": 1}}}', "Edge"),
    ],
)
def test_malformed_files_name_the_problem(tmp_path: Path, content: str, match: str) -> None:
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        load_layout_file(path)


def test_duplicate_keys_block_export(tmp_path: Path) -> None:
    with Diagram(layout="auto") as d:
        d.shape("Server")
        d.shape("Server")
    with pytest.raises(ValueError, match="'Server'.*id="):
        export_layout(d, tmp_path / "l.json")
