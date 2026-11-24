"""The GitHub Pages landing page stays true: data in sync, links resolve, snippet runs."""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import diagrams_as_code

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGE = (DOCS / "index.html").read_text(encoding="utf-8")


def test_site_data_is_up_to_date():
    done = subprocess.run([sys.executable, str(ROOT / "tools" / "build_site.py"), "--check"],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


def test_site_data_matches_the_repository():
    data = json.loads((DOCS / "assets" / "site-data.json").read_text())
    assert data["version"] == diagrams_as_code.__version__
    assert data["diagrams"] == len(list((ROOT / "examples").glob("*/*.py"))) + len(list((ROOT / "examples").glob("*.py")))
    assert all((DOCS / i["image"]).is_file() for i in data["gallery"])
    assert {i["group"] for i in data["gallery"]} == set(data["groups"])


def test_pages_support_files_exist():
    assert (DOCS / ".nojekyll").is_file()
    assert (DOCS / "assets" / "logo.svg").is_file()


def test_every_relative_link_resolves():
    static = re.sub(r"<script>.*?</script>", "", PAGE, flags=re.S)  # JS builds some URLs at runtime
    refs = re.findall(r'(?:href|src)="([^"#:]+)"', static)
    missing = [r for r in refs if not (DOCS / r).exists()]
    assert not missing, missing


def test_doc_cards_point_at_real_docs():
    names = re.findall(r'blob/master/docs/([A-Za-z0-9_.-]+)"', PAGE)
    assert names and all((DOCS / n).is_file() for n in names), names


def test_quickstart_snippet_runs(tmp_path):
    block = re.search(r'<pre id="c1">(.*?)</pre>', PAGE, re.S).group(1)
    code = html.unescape(re.sub(r"<[^>]+>", "", block))
    script = tmp_path / "quickstart.py"
    script.write_text(code, encoding="utf-8")
    done = subprocess.run([sys.executable, str(script)], cwd=tmp_path, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert (tmp_path / "out" / "request_path.svg").is_file()


def test_page_has_metadata_and_no_absolute_docs_paths():
    assert 'rel="icon"' in PAGE and 'property="og:title"' in PAGE
    assert 'href="/docs/' not in PAGE and 'src="/docs/' not in PAGE


@pytest.mark.parametrize("cmd", ["render examples --out build", "lint examples", "mcp --root ."])
def test_cli_commands_shown_on_the_page_exist(cmd):
    assert f"diagrams-as-code {cmd}" in PAGE
