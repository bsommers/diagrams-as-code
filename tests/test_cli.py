from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from diagrams_as_code.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent

GOOD = '''
from diagrams_as_code import Diagram

OUTPUT_STEM = "{stem}"


def diagram() -> Diagram:
    with Diagram("Demo") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    return d
'''


def _script(path: Path, stem: str = "demo") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(GOOD.format(stem=stem), encoding="utf-8")
    return path


def test_render_one_script_defaults_to_svg_and_bom(tmp_path: Path, capsys) -> None:
    script = _script(tmp_path / "src" / "x.py")
    assert main(["render", str(script), "--out", str(tmp_path / "out")]) == 0
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["demo.svg", "demo_README.md"]
    assert "demo.svg" in capsys.readouterr().out


def test_flags_override_the_script(tmp_path: Path) -> None:
    script = _script(tmp_path / "x.py")
    out = tmp_path / "out"
    assert main(["render", str(script), "--out", str(out), "--layout", "auto", "--theme", "nord", "--format", "svg"]) == 0
    svg = (out / "demo.svg").read_text(encoding="utf-8")
    assert 'x="60.0" y="80.0"' in svg or 'x="60" y="80"' in svg


def test_directory_input_mirrors_subdirectories(tmp_path: Path) -> None:
    _script(tmp_path / "gallery" / "cloud" / "one.py", stem="one")
    (tmp_path / "gallery" / "helpers.py").write_text("X = 1\n", encoding="utf-8")
    assert main(["render", str(tmp_path / "gallery"), "--out", str(tmp_path / "out"), "--format", "svg"]) == 0
    assert (tmp_path / "out" / "cloud" / "one.svg").exists()
    assert not (tmp_path / "out" / "helpers.svg").exists()


def test_failing_script_returns_1_and_others_still_render(tmp_path: Path, capsys) -> None:
    bad = tmp_path / "a_bad.py"
    bad.write_text("def diagram():\n    raise RuntimeError('boom')\n", encoding="utf-8")
    good = _script(tmp_path / "b_good.py")
    assert main(["render", str(bad), str(good), "--out", str(tmp_path / "out"), "--format", "svg"]) == 1
    err = capsys.readouterr().err
    assert f"error: {bad}: boom" in err and "Traceback" not in err
    assert (tmp_path / "out" / "demo.svg").exists()


def test_debug_shows_the_traceback(tmp_path: Path, capsys) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def diagram():\n    raise RuntimeError('boom')\n", encoding="utf-8")
    assert main(["render", str(bad), "--out", str(tmp_path), "--debug"]) == 1
    assert "Traceback" in capsys.readouterr().err


def test_script_without_diagram_function(tmp_path: Path, capsys) -> None:
    s = tmp_path / "nothing.py"
    s.write_text("X = 1\n", encoding="utf-8")
    assert main(["render", str(s), "--out", str(tmp_path)]) == 1
    assert "defines no diagram() function" in capsys.readouterr().err


def test_usage_errors_return_2(capsys) -> None:
    assert main(["render"]) == 2
    assert main(["render", "x.py", "--layout", "grid"]) == 2
    assert main(["no-such-command"]) == 2


def test_layout_export(tmp_path: Path) -> None:
    script = _script(tmp_path / "x.py")
    assert main(["layout", "export", str(script), "--layout", "auto"]) == 0
    data = json.loads((tmp_path / "x.layout.json").read_text(encoding="utf-8"))
    assert sorted(data["positions"]) == ["A", "B"]


def test_themes_and_icons(capsys) -> None:
    assert main(["themes"]) == 0
    assert "nord" in capsys.readouterr().out.split()
    assert main(["icons", "--domain", "iiot"]) == 0
    out = capsys.readouterr().out
    assert "sensor" in out and "kubernetes" not in out


def test_module_entry_point_runs() -> None:
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
    res = subprocess.run([sys.executable, "-m", "diagrams_as_code", "themes"], capture_output=True, text=True, env=env)
    assert res.returncode == 0 and "nord" in res.stdout
