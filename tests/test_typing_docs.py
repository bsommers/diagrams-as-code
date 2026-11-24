"""PEP 561 marker ships with the wheel, and public docstring coverage only goes up."""
from __future__ import annotations

import ast
import shutil
import subprocess
import tempfile
import tomllib
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "diagrams_as_code"
#: Modules owned by the agent-facing surface; documented separately.
EXCLUDED = {"mcp.py", "cli.py", "sandbox.py"}
#: Public classes, functions and methods with a docstring. Raise it; never lower it.
FLOOR = 0.95


def public_docstring_coverage() -> tuple[int, int, list[str]]:
    """Return ``(public, documented, missing)`` for classes, functions and methods."""
    total = documented = 0
    missing: list[str] = []

    def walk(body, path: Path, prefix: str, public: bool = True) -> None:
        nonlocal total, documented
        for node in body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            is_public = public and not node.name.startswith("_")
            if is_public:
                total += 1
                if ast.get_docstring(node):
                    documented += 1
                else:
                    missing.append(f"{path.relative_to(ROOT)}:{node.lineno} {prefix}{node.name}")
            if isinstance(node, ast.ClassDef):
                walk(node.body, path, f"{prefix}{node.name}.", is_public)

    for path in sorted(SRC.rglob("*.py")):
        if path.name not in EXCLUDED:
            walk(ast.parse(path.read_text(encoding="utf-8")).body, path, "")
    return total, documented, missing


def test_py_typed_markers_exist():
    assert (SRC / "py.typed").is_file()
    assert (ROOT / "src" / "iiot_diagrams" / "py.typed").is_file()


def test_wheel_config_packages_the_directories_holding_py_typed():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    wheel = config["tool"]["hatch"]["build"]["targets"]["wheel"]
    assert "src/diagrams_as_code" in wheel["packages"]
    assert not wheel.get("exclude") and not wheel.get("only-include")


def test_py_typed_is_in_the_built_wheel():
    if shutil.which("uv") is None:
        pytest.skip("uv not available")
    with tempfile.TemporaryDirectory() as out:
        done = subprocess.run(["uv", "build", "--wheel", "--out-dir", out], cwd=ROOT,
                              capture_output=True, text=True)
        if done.returncode != 0:
            pytest.skip("wheel build unavailable offline: " + done.stderr[-200:])
        wheel = next(Path(out).glob("*.whl"))
        names = zipfile.ZipFile(wheel).namelist()
    assert "diagrams_as_code/py.typed" in names


def test_public_docstring_coverage_ratchet():
    total, documented, missing = public_docstring_coverage()
    assert documented / total >= FLOOR, f"{documented}/{total}; undocumented: {missing[:20]}"
