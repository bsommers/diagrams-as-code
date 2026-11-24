"""Machine interfaces: the MCP source/discovery tools and the CLI's ``--json`` output."""
import io
import json
import re
import time
from pathlib import Path

import pytest

import diagrams_as_code
from diagrams_as_code import agent_api, cli
from diagrams_as_code.mcp import MAX_RESULT_CHARS, TOOLS, Server, serve
from diagrams_as_code.sandbox import Limits

REPO = Path(__file__).resolve().parents[1]
SCRIPT = "examples/finance/01_candlestick_chart.py"
GOOD = (REPO / SCRIPT).read_text()
TINY = ("from diagrams_as_code import Diagram\n"
        "def diagram():\n    d = Diagram('t')\n    d.shape('A', id='a')\n    return d\n")
OVERLAP = ("from diagrams_as_code import Diagram, Shape\n"
           "def diagram():\n"
           "    with Diagram('t', theme='monochrome', width=520, height=260) as d:\n"
           "        d.add(Shape('a', 'A')).at(100, 100)\n"
           "        d.add(Shape('b', 'B')).at(110, 110)\n"
           "    return d\n")


def call(server, _tool, **args):
    reply = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": _tool, "arguments": args}})
    return reply["result"]


def err(res):
    assert res["isError"], res
    assert res["structuredContent"]["error"] == json.loads(res["content"][0]["text"])["error"]
    return res["structuredContent"]["error"]


# --- tools/list ---------------------------------------------------------------

def test_new_tools_are_listed_with_schemas():
    tools = {t["name"]: t for t in Server(REPO).handle(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]}
    for name in ("render_source", "lint_source", "get_example", "list_domains",
                 "describe_api", "capabilities"):
        assert name in tools and tools[name]["inputSchema"]["type"] == "object"
        assert tools[name]["outputSchema"]["type"] == "object"
    props = tools["render_source"]["inputSchema"]["properties"]
    assert props["formats"]["items"]["enum"] == ["svg", "png", "pdf", "bom"]
    assert "enum" in props["theme"] and tools["render_source"]["inputSchema"]["required"] == ["source"]
    assert all(p.get("description") for p in props.values())
    assert set(TOOLS) >= set(tools)


# --- render_source ------------------------------------------------------------

def test_render_source_inline_is_byte_identical_to_render(tmp_path):
    (tmp_path / "s.py").write_text(GOOD)
    s = Server(tmp_path)
    assert not call(s, "render", path="s.py", out="b", formats=["svg"])["isError"]
    res = call(s, "render_source", source=GOOD)
    assert not res["isError"], res
    sc = res["structuredContent"]
    assert sc["svg"] == (tmp_path / "b" / "s.svg").read_text()
    assert sc["svg"] == (REPO / SCRIPT).with_suffix(".svg").read_text()
    assert sc["svg_truncated"] is False and sc["stem"] == "script"


def test_render_source_writes_files_under_out_only(tmp_path):
    s = Server(tmp_path)
    res = call(s, "render_source", source=TINY, formats=["svg", "bom"], out="build", name="mine")
    files = {w["format"]: w["file"] for w in res["structuredContent"]["written"]}
    assert files == {"svg": "build/mine.svg", "bom": "build/mine_README.md"}
    assert (tmp_path / "build" / "mine.svg").read_text().startswith("<svg")
    assert "svg" not in res["structuredContent"]  # out given: not inline unless asked
    both = call(s, "render_source", source=TINY, out="build", inline=True)["structuredContent"]
    assert both["svg"] and both["written"]
    assert call(s, "render_source", source=TINY, out="../x")["structuredContent"]["error"]["code"] \
        == "path_outside_root"
    assert err(call(s, "render_source", source=TINY, name="../evil", out="o"))["code"] == "invalid_argument"
    assert not (tmp_path.parent / "evil.svg").exists()


def test_render_source_argument_errors():
    s = Server(REPO)
    assert err(call(s, "render_source", source=TINY, formats=["png"]))["code"] == "invalid_argument"
    assert err(call(s, "render_source", source=TINY, inline=False))["code"] == "invalid_argument"
    assert err(call(s, "render_source", source=TINY, formats=["gif"]))["code"] == "invalid_argument"
    assert err(call(s, "render_source", source=TINY, theme="nope"))["code"] == "invalid_argument"
    assert err(call(s, "render_source", source=""))["code"] == "invalid_argument"
    assert err(call(s, "render_source", source=5))["code"] == "invalid_argument"
    assert err(call(s, "render_source", source=TINY, bogus=1))["code"] == "invalid_argument"
    big = "#" * (agent_api.MAX_SOURCE_CHARS + 1)
    assert err(call(s, "render_source", source=big))["code"] == "invalid_argument"
    missing = s.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                        "params": {"name": "render_source", "arguments": {}}})
    assert missing["error"]["code"] == -32602


def test_render_source_inline_svg_is_bounded(monkeypatch):
    monkeypatch.setattr(agent_api, "MAX_INLINE_CHARS", 500)
    sc = call(Server(REPO), "render_source", source=TINY)["structuredContent"]
    assert len(sc["svg"]) == 500 and sc["svg_truncated"] is True and sc["svg_chars"] > 500


def test_result_text_is_cut_at_max_result_chars(monkeypatch):
    from diagrams_as_code import mcp
    monkeypatch.setattr(mcp, "MAX_RESULT_CHARS", 300)
    res = call(Server(REPO), "describe_api")
    assert len(res["content"][0]["text"]) <= 300 + len("\n... [truncated]")
    assert MAX_RESULT_CHARS == 200_000


def test_render_source_error_has_code_and_user_line():
    src = "from diagrams_as_code import Diagram\n\ndef helper():\n    raise ValueError('boom')\n\n" \
          "def diagram():\n    d = Diagram('t')\n    helper()\n    return d\n"
    e = err(call(Server(REPO), "render_source", source=src))
    assert e["code"] == "script_error" and e["line"] == 4 and "ValueError: boom" in e["message"]
    syn = err(call(Server(REPO), "render_source", source="def diagram(:\n"))
    assert syn["code"] == "script_error" and syn["line"] == 1
    nod = err(call(Server(REPO), "render_source", source="x = 1\n"))
    assert nod["code"] == "script_error" and "diagram()" in nod["message"]


def test_render_source_is_sandboxed(tmp_path):
    loop = TINY.replace("def diagram", "while True:\n    pass\ndef diagram")
    t0 = time.monotonic()
    e = err(call(Server(tmp_path, Limits(timeout=1.5, cpu=60)), "render_source", source=loop))
    assert e["code"] == "timeout" and time.monotonic() - t0 < 10
    assert err(call(Server(tmp_path), "render_source",
                    source="import sys\nsys.exit(3)\n" + TINY))["code"] == "script_error"
    noisy = "import os, sys\nos.write(1, b'{garbage}\\n')\nprint('hi')\nsys.stdin.read()\n" + TINY
    out = io.StringIO()
    req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                      "params": {"name": "render_source", "arguments": {"source": noisy}}})
    serve(tmp_path, io.StringIO(req + "\n"), out)
    lines = out.getvalue().splitlines()
    assert len(lines) == 1 and not json.loads(lines[0])["result"]["isError"]


def test_no_absolute_path_leaks(tmp_path):
    leak = f"import os\nraise RuntimeError({str(tmp_path / 'secret')!r})\n" + TINY
    s = Server(tmp_path)
    for res in (call(s, "render_source", source=leak),
                call(s, "lint_source", source=leak),
                call(s, "render_source", source=TINY, out="../escape"),
                call(s, "get_example", domain="..", name="x")):
        text = res["content"][0]["text"]
        assert res["isError"] and str(tmp_path) not in text
    ok = call(s, "render_source", source=TINY, out="o")
    assert str(tmp_path) not in ok["content"][0]["text"]
    # an error raised from the sandbox scratch directory is scrubbed too
    where = call(s, "render_source", source="import os\nraise RuntimeError(os.getcwd())\n" + TINY)
    assert "dac-sandbox" not in where["content"][0]["text"]


# --- lint_source --------------------------------------------------------------

def test_lint_source_findings_are_structured():
    clean = call(Server(REPO), "lint_source", source=GOOD)["structuredContent"]
    assert clean == {"checked": 1, "count": 0, "findings": []}
    overlap = OVERLAP
    sc = call(Server(REPO), "lint_source", source=overlap)["structuredContent"]
    hit = [f for f in sc["findings"] if f["kind"] == "node_overlap"]
    assert hit and hit[0]["ids"] == ["a", "b"] and hit[0]["detail"]
    assert sc["count"] == len(sc["findings"])
    assert err(call(Server(REPO), "lint_source", source=TINY, ignore=["nope"]))["code"] == "invalid_argument"
    ignored = call(Server(REPO), "lint_source", source=overlap, ignore=["node_overlap"])
    assert not [f for f in ignored["structuredContent"]["findings"] if f["kind"] == "node_overlap"]


# --- discovery tools ----------------------------------------------------------

def test_list_domains_and_get_example():
    s = Server(REPO)
    doms = call(s, "list_domains")["structuredContent"]
    fin = next(d for d in doms["domains"] if d["domain"] == "finance")
    assert fin["count"] == len(fin["titles"]) >= 10 and doms["total"] >= 300
    ex = call(s, "get_example", domain="finance", name="01_candlestick_chart")["structuredContent"]
    assert ex["source"] == GOOD and ex["svg"] == (REPO / SCRIPT).with_suffix(".svg").read_text()
    short = call(s, "get_example", domain="finance", name="candlestick_chart")["structuredContent"]
    assert short["name"] == ex["name"]
    assert err(call(s, "get_example", domain="finance", name="zzz"))["code"] == "not_found"
    assert err(call(s, "get_example", domain="nodomain", name="x"))["code"] == "not_found"
    for bad in ("..", "a/b", "/etc"):
        assert err(call(s, "get_example", domain=bad, name="x"))["code"] == "invalid_argument"
    assert err(call(s, "get_example", domain="finance", name="../../pyproject"))["code"] == "invalid_argument"


def test_describe_api_covers_all_and_the_kits():
    ref = call(Server(REPO), "describe_api")["structuredContent"]
    names = {(e["module"], e["name"]) for e in ref["entries"]}
    for n in diagrams_as_code.__all__:
        assert ("diagrams_as_code", n) in names, n
    assert any(m == "diagrams_as_code.gantt" for m, _ in names)
    assert any(m == "diagrams_as_code.plot" for m, _ in names)
    assert any(m == "diagrams_as_code.sequence" for m, _ in names)
    assert any(m == "diagrams_as_code.draft" for m, _ in names)
    assert not ref["truncated"] and len(json.dumps(ref)) <= agent_api.MAX_API_CHARS + 2000
    d = next(e for e in ref["entries"] if e["name"] == "Diagram")
    assert d["kind"] == "class" and d["signature"].startswith("(title: str") and d["summary"]


def test_describe_api_name_filter_and_bounds():
    s = Server(REPO)
    one = call(s, "describe_api", name="diagram")["structuredContent"]
    assert one["entries"][0]["name"] == "Diagram"
    assert any(m["name"] == "shape" for m in one["entries"][0]["members"])
    kit = call(s, "describe_api", name="gantt")["structuredContent"]
    assert kit["entries"] and all(e["module"] == "diagrams_as_code.gantt" for e in kit["entries"])
    assert err(call(s, "describe_api", name="zzz_nothing"))["code"] == "not_found"
    small = agent_api.api_reference(max_chars=2000)
    assert small["truncated"] and small["returned"] < small["total"]


def test_capabilities_tool():
    sc = call(Server(REPO), "capabilities")["structuredContent"]
    ids = {c["id"] for c in sc["capabilities"]}
    assert "CAP-MCP-SERVER" in ids and sc["total"] == len(sc["capabilities"])
    mcp_cap = next(c for c in sc["capabilities"] if c["id"] == "CAP-MCP-SERVER")
    assert mcp_cap["verification"].startswith("uv run")
    only = call(Server(REPO), "capabilities", category="Model Context Protocol Server")["structuredContent"]
    assert 0 < only["total"] < sc["total"]


def test_every_capability_verification_command_names_an_existing_test():
    for c in agent_api.capabilities_summary(REPO / "docs" / "capabilities.json")["capabilities"]:
        for path in re.findall(r"tests/[\w/]+\.py", c["verification"]):
            assert (REPO / path).exists(), (c["id"], path)


# --- structured errors on the older tools ------------------------------------

def test_existing_tools_report_codes(tmp_path):
    s = Server(tmp_path)
    assert err(call(s, "render", path="../x.py"))["code"] == "path_outside_root"
    assert err(call(s, "render", path="missing.py"))["code"] == "not_found"
    (tmp_path / "d").mkdir()
    assert err(call(s, "lint", path="d"))["code"] == "no_scripts"
    (tmp_path / "bad.py").write_text("def diagram():\n    raise KeyError('k')\n")
    e = err(call(s, "render", path="bad.py"))
    assert e["code"] == "script_error" and e["line"] == 2
    assert err(call(s, "render", path="bad.py", formats=["gif"]))["code"] == "invalid_argument"


# --- CLI ----------------------------------------------------------------------

def run_cli(capsys, *argv):
    code = cli.main(list(argv))
    out = capsys.readouterr()
    return code, out.out, out.err


def test_cli_themes_and_icons_json(capsys):
    code, out, _ = run_cli(capsys, "themes", "--json")
    assert code == 0 and json.loads(out)["themes"] == list(cli.list_themes())
    code, out, _ = run_cli(capsys, "icons", "--json", "--domain", "iiot")
    doc = json.loads(out)
    assert code == 0 and doc["icons"] and all(i["domain"] == "iiot" for i in doc["icons"])
    code, out, _ = run_cli(capsys, "themes")  # human text unchanged
    assert out.splitlines() == list(cli.list_themes())
    code, out, _ = run_cli(capsys, "icons")
    assert "\t" in out.splitlines()[0]


def test_cli_lint_json(capsys, tmp_path):
    code, out, err_ = run_cli(capsys, "lint", "--json", str(REPO / SCRIPT))
    assert code == 0 and json.loads(out) == {"checked": 1, "findings": [], "failed": []}
    (tmp_path / "ov.py").write_text(OVERLAP)
    (tmp_path / "boom.py").write_text("def diagram():\n    x = 1\n    raise RuntimeError('no')\n")
    code, out, err_ = run_cli(capsys, "lint", "--json", str(tmp_path / "ov.py"), str(tmp_path / "boom.py"))
    doc = json.loads(out)
    assert code == 1
    f = next(f for f in doc["findings"] if f["kind"] == "node_overlap")
    assert f["file"].endswith("ov.py") and f["ids"] == ["a", "b"] and f["detail"]
    assert doc["failed"][0]["code"] == "script_error" and doc["failed"][0]["line"] == 3
    assert "boom.py" in err_  # diagnostics on stderr


def test_cli_lint_json_keeps_script_prints_off_stdout(capsys, tmp_path):
    (tmp_path / "p.py").write_text("print('chatter')\n" + TINY)
    code, out, err_ = run_cli(capsys, "lint", "--json", str(tmp_path / "p.py"))
    assert code == 0 and json.loads(out)["checked"] == 1 and "chatter" in err_


def test_cli_render_json(capsys, tmp_path):
    (tmp_path / "s.py").write_text(TINY)
    code, out, _ = run_cli(capsys, "render", "--json", "--format", "svg", "--out", str(tmp_path / "o"),
                           str(tmp_path / "s.py"))
    doc = json.loads(out)
    assert code == 0 and doc["failed"] == []
    assert doc["written"] == [{"script": str(tmp_path / "s.py"), "format": "svg",
                               "file": str(tmp_path / "o" / "s.svg")}]
    code, out, _ = run_cli(capsys, "render", str(tmp_path / "s.py"), "--out", str(tmp_path / "o"))
    assert out.startswith("wrote ")  # human output unchanged
    (tmp_path / "bad.py").write_text("def diagram():\n    raise ValueError('v')\n")
    code, out, err_ = run_cli(capsys, "render", "--json", "--out", str(tmp_path / "o2"), str(tmp_path / "bad.py"))
    doc = json.loads(out)
    assert code == 1 and doc["written"] == [] and doc["failed"][0]["line"] == 2
    (tmp_path / "empty").mkdir()
    code, out, _ = run_cli(capsys, "render", "--json", str(tmp_path / "empty"))
    assert code == 1 and json.loads(out)["failed"][0]["code"] == "no_scripts"
    assert run_cli(capsys, "render", "--bogus")[0] == 2


def test_cli_render_matches_render_source_bytes(capsys, tmp_path):
    (tmp_path / "s.py").write_text(GOOD)
    run_cli(capsys, "render", "--json", "--format", "svg", "--out", str(tmp_path / "o"), str(tmp_path / "s.py"))
    svg = (tmp_path / "o" / "s.svg").read_text()
    assert call(Server(tmp_path), "render_source", source=GOOD)["structuredContent"]["svg"] == svg


def test_cli_api(capsys):
    code, out, _ = run_cli(capsys, "api", "--json")
    names = {e["name"] for e in json.loads(out)["entries"]}
    assert code == 0 and set(diagrams_as_code.__all__) <= names
    assert json.loads(run_cli(capsys, "api", "--json", "Diagram")[1]) == \
        call(Server(REPO), "describe_api", name="Diagram")["structuredContent"]
    code, out, _ = run_cli(capsys, "api", "gantt")
    assert code == 0 and "GanttChart" in out
    code, out, err_ = run_cli(capsys, "api", "zzz_nothing")
    assert code == 1 and out == "" and "zzz_nothing" in err_
    assert run_cli(capsys, "api", "--json", "zzz_nothing")[0] == 1


def test_cli_examples_and_source(capsys):
    code, out, _ = run_cli(capsys, "examples", "--json")
    doc = json.loads(out)
    assert code == 0 and any(d["domain"] == "finance" for d in doc["domains"])
    assert doc == call(Server(REPO), "list_domains")["structuredContent"]
    code, out, _ = run_cli(capsys, "examples", "--domain", "finance", "--json")
    items = json.loads(out)["examples"]
    assert code == 0 and len(items) >= 10 and items[0]["domain"] == "finance"
    code, out, _ = run_cli(capsys, "examples", "--domain", "finance")
    assert out.splitlines()[0].startswith("finance/")
    assert run_cli(capsys, "examples", "--domain", "nope")[0] == 1
    code, out, _ = run_cli(capsys, "source", "finance/01_candlestick_chart")
    assert code == 0 and out == GOOD
    assert run_cli(capsys, "source", "finance/nope")[0] == 1
    assert run_cli(capsys, "source", "../../etc/passwd")[0] == 1
    assert run_cli(capsys, "source")[0] == 2


def test_cli_subprocess_stdout_is_only_json():
    import subprocess
    import sys
    p = subprocess.run([sys.executable, "-m", "diagrams_as_code", "lint", "--json", SCRIPT],
                       cwd=REPO, capture_output=True, text=True)
    assert p.returncode == 0 and json.loads(p.stdout)["checked"] == 1


@pytest.mark.parametrize("code", agent_api.ERROR_CODES)
def test_error_codes_are_documented(code):
    text = (REPO / "docs" / "running.md").read_text()
    assert f"`{code}`" in text
