"""The agent-facing documentation is generated, current, and points at real files."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import diagrams_as_code

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = "https://bsommers.github.io/diagrams-as-code/"
BLOB = "https://github.com/bsommers/diagrams-as-code/blob/master/"

sys.path.insert(0, str(ROOT / "tools"))
import build_agent_docs as gen  # noqa: E402


def test_generated_files_are_up_to_date():
    done = subprocess.run([sys.executable, str(ROOT / "tools" / "build_agent_docs.py"), "--check"],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


def test_generation_is_deterministic():
    assert gen.build() == gen.build()


def _links(text: str) -> list[str]:
    return re.findall(r"\]\((https?://[^)]+)\)", text)


def _to_repo_path(url: str) -> Path | None:
    if url.startswith(BLOB):
        return ROOT / url[len(BLOB):]
    if url.startswith(SITE):
        rest = url[len(SITE):].split("#", 1)[0]
        return DOCS / (rest or "index.html")
    return None


def test_llms_txt_follows_the_llmstxt_format():
    lines = (DOCS / "llms.txt").read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("# ") and not lines[0].startswith("##")
    assert lines[1] == "" and lines[2].startswith("> ")
    sections = [ln for ln in lines if ln.startswith("## ")]
    assert "## Docs" in sections and len(sections) >= 3
    assert sum(1 for ln in lines if ln.startswith("# ")) == 1


def test_llms_txt_links_are_absolute_and_resolve_to_repo_files():
    text = (DOCS / "llms.txt").read_text(encoding="utf-8")
    links = _links(text)
    assert links
    for url in links:
        target = _to_repo_path(url)
        assert target is not None, f"not a bsommers.github.io or github.com/bsommers URL: {url}"
        assert target.is_file(), f"{url} -> {target.relative_to(ROOT)} does not exist"
    assert not re.findall(r"\]\((?!https?://)", text), "relative link in llms.txt"


def test_llms_full_contains_every_part():
    text = (DOCS / "llms-full.txt").read_text(encoding="utf-8")
    for needle in ("Using diagrams-as-code from an AI agent", "# API reference", "## Command-line interface",
                   "## MCP server tools", "# Math markup reference", "## Examples index (compact)"):
        assert needle in text, needle


def test_llms_full_lists_the_live_mcp_tools_and_cli_commands():
    from diagrams_as_code.cli import build_parser
    from diagrams_as_code.mcp import TOOLS

    text = (DOCS / "llms-full.txt").read_text(encoding="utf-8")
    for name in TOOLS:
        assert f"### `{name}`" in text, name
    commands = build_parser()._subparsers._group_actions[0].choices  # type: ignore[union-attr]
    for name in commands:
        assert f"`diagrams-as-code {name}`" in text, name


def test_api_reference_mentions_every_public_name():
    text = (DOCS / "api-reference.md").read_text(encoding="utf-8")
    missing = [n for n in diagrams_as_code.__all__ if f"### `{n}`" not in text]
    assert not missing, missing
    for module in gen.KIT_MODULES:
        assert f"`{module}`" in text, module


def test_api_reference_carries_signatures_and_locations():
    text = (DOCS / "api-reference.md").read_text(encoding="utf-8")
    assert "`class Diagram(title: str" in text
    assert "`def render_all(" in text
    assert "Defined in `src/diagrams_as_code/diagram.py`" in text
    assert "0x" not in text


def test_examples_index_covers_every_example_script():
    index = json.loads((ROOT / "examples" / "index.json").read_text(encoding="utf-8"))
    scripts = sorted(p.relative_to(ROOT).as_posix()
                     for p in list((ROOT / "examples").glob("*/*.py")) + list((ROOT / "examples").glob("[0-9]*.py")))
    assert [r["path"] for r in index["examples"]] == scripts
    assert index["count"] == len(scripts)


def test_examples_index_records_are_complete_and_sane():
    index = json.loads((ROOT / "examples" / "index.json").read_text(encoding="utf-8"))
    keys = {"path", "domain", "number", "title", "description", "theme", "formats", "svg",
            "uses_plot", "uses_draft", "uses_sequence", "uses_gantt", "uses_math"}
    themes = set(diagrams_as_code.list_themes())
    for rec in index["examples"]:
        assert set(rec) == keys, rec["path"]
        assert rec["title"].strip() and "\n" not in rec["title"], rec["path"]
        assert rec["theme"] in themes, rec
        assert rec["formats"] and set(rec["formats"]) <= {"svg", "png", "pdf", "bom"}
        assert (ROOT / rec["path"]).is_file()
        for kit in ("plot", "draft", "sequence", "gantt", "math"):
            assert isinstance(rec[f"uses_{kit}"], bool)


def test_examples_index_flags_match_known_examples():
    by_path = {r["path"]: r for r in json.loads((ROOT / "examples" / "index.json").read_text())["examples"]}
    assert by_path["examples/sequence/03_mcp_tool_call.py"]["uses_sequence"] is True
    assert by_path["examples/sequence/03_mcp_tool_call.py"]["title"] == "MCP tool call"
    assert by_path["examples/calculus_math/02_riemann_sums.py"]["uses_plot"] is True
    assert by_path["examples/calculus_math/02_riemann_sums.py"]["uses_math"] is True
    assert by_path["examples/calculus_math/02_riemann_sums.py"]["theme"] == "paper"
    assert by_path["examples/project_management/01_gantt_critical_path.py"]["uses_gantt"] is True


def test_example_titles_are_deterministic():
    first = [gen.example_record(s)["title"] for s in gen.example_scripts()[:40]]
    second = [gen.example_record(s)["title"] for s in gen.example_scripts()[:40]]
    assert first == second
