"""Every snippet in docs/for-agents.md runs, and the guide's claims are checked, not hoped.

Fenced ``python`` and ``bash`` blocks must carry the word ``runnable`` in their info string:

    ```python runnable              executed with the repository's interpreter
    ```python runnable file=x.py    written to x.py, then imported; ``diagram()`` must return a Diagram
    ```bash runnable exit=1         each line is a ``diagrams-as-code ...`` command; expected exit code

Blocks run in document order inside one temporary directory, so a later block can use a
script an earlier one wrote. Use ``text`` or ``json`` fences for anything that is not executed.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "for-agents.md"
FENCE = re.compile(r"^```(\w+)([^\n]*)\n(.*?)^```", re.S | re.M)
CODE_LANGS = {"python", "py", "bash", "sh", "shell", "console"}


def blocks() -> list[tuple[str, dict[str, str], str, int]]:
    """``(language, attributes, body, line number)`` for every fenced code block."""
    text = GUIDE.read_text(encoding="utf-8")
    out = []
    for m in FENCE.finditer(text):
        words = m.group(2).split()
        attrs = {w.split("=", 1)[0]: (w.split("=", 1)[1] if "=" in w else "") for w in words}
        out.append((m.group(1), attrs, m.group(3), text[: m.start()].count("\n") + 1))
    return out


def test_every_code_block_is_marked_runnable():
    loose = [f"line {line}: {lang}" for lang, attrs, _body, line in blocks()
             if lang in CODE_LANGS and "runnable" not in attrs]
    assert not loose, f"unexecuted code blocks in docs/for-agents.md (mark runnable or use ```text): {loose}"


def test_guide_has_the_required_sections():
    text = GUIDE.read_text(encoding="utf-8")
    for heading in ("Choose an interface", "minimal verified quickstart", "cheat sheet", "feedback loop",
                    "Pitfalls", "Determinism guarantees", "determinism and sandbox limits", "Finding examples"):
        assert re.search(rf"^## .*{re.escape(heading)}", text, re.M | re.I), heading


def test_cheat_sheet_lists_fifteen_calls():
    text = GUIDE.read_text(encoding="utf-8")
    section = text.split("## 3.", 1)[1].split("## 4.", 1)[0]
    rows = re.findall(r"^\| (\d+) \|", section, re.M)
    assert [int(r) for r in rows] == list(range(1, 16))


def test_relative_links_resolve():
    text = GUIDE.read_text(encoding="utf-8")
    for target in re.findall(r"\]\((?!https?://|#)([^)#]+)", text):
        assert (GUIDE.parent / target).exists(), target


def test_snippets_run(tmp_path):
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), DAC_REPO=str(ROOT), PYTHONHASHSEED="0")
    ran = 0
    for lang, attrs, body, line in blocks():
        if "runnable" not in attrs:
            continue
        where = f"docs/for-agents.md:{line}"
        if lang in {"python", "py"}:
            if "file" in attrs:
                (tmp_path / attrs["file"]).write_text(body, encoding="utf-8")
                probe = ("import importlib.util as u, sys;"
                         f"s=u.spec_from_file_location('m', {attrs['file']!r}); m=u.module_from_spec(s);"
                         "s.loader.exec_module(m);"
                         "from diagrams_as_code import Diagram;"
                         "assert isinstance(m.diagram(), Diagram)")
                cmd = [sys.executable, "-c", probe]
            else:
                script = tmp_path / f"_block_{line}.py"
                script.write_text(body, encoding="utf-8")
                cmd = [sys.executable, str(script)]
            expected = 0
        else:
            expected = int(attrs.get("exit", "0"))
            for raw in body.strip().splitlines():
                tokens = shlex.split(raw)
                assert tokens and tokens[0] == "diagrams-as-code", f"{where}: only diagrams-as-code commands: {raw!r}"
                done = subprocess.run([sys.executable, "-m", "diagrams_as_code", *tokens[1:]], cwd=tmp_path,
                                      env=env, capture_output=True, text=True, timeout=300)
                assert done.returncode == expected, f"{where}: {raw!r} exited {done.returncode}\n{done.stdout}{done.stderr}"
                ran += 1
            continue
        done = subprocess.run(cmd, cwd=tmp_path, env=env, capture_output=True, text=True, timeout=300)
        assert done.returncode == expected, f"{where}\n{done.stdout}{done.stderr}"
        ran += 1
    assert ran >= 15


def test_cli_commands_named_in_the_guide_exist():
    from diagrams_as_code.cli import build_parser

    commands = set(build_parser()._subparsers._group_actions[0].choices)  # type: ignore[union-attr]
    text = GUIDE.read_text(encoding="utf-8")
    named = set(re.findall(r"`diagrams-as-code (\w+)", text))
    assert named <= commands | {"mcp"}, named - commands
