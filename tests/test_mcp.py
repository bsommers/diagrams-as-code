"""The MCP server exposes the same operations as the CLI and the Python API."""
import io
import json
from pathlib import Path

from diagrams_as_code import cli
from diagrams_as_code.mcp import TOOLS, Server, serve

REPO = Path(__file__).resolve().parents[1]
SCRIPT = "examples/finance/01_candlestick_chart.py"


def call(server, name, **args):
    reply = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": name, "arguments": args}})
    return reply["result"]


def test_initialize_and_list_tools():
    s = Server(REPO)
    init = s.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert init["result"]["capabilities"] == {"tools": {}}
    names = {t["name"] for t in s.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]}
    assert names == set(TOOLS) >= {"render", "lint", "list_examples", "list_themes", "list_icons"}
    assert s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert s.handle({"jsonrpc": "2.0", "id": 3, "method": "nope"})["error"]["code"] == -32601


def test_render_to_out_dir(tmp_path):
    (tmp_path / "s.py").write_text((REPO / SCRIPT).read_text())
    res = call(Server(tmp_path), "render", path="s.py", out="build", formats=["svg"])
    assert not res["isError"], res
    assert (tmp_path / "build" / "s.svg").exists() or (tmp_path / "build" / "01_candlestick_chart.svg").exists()


def test_render_matches_committed_svg(tmp_path):
    root = tmp_path
    (root / "examples").mkdir()
    src = REPO / SCRIPT
    (root / "examples" / src.name).write_text(src.read_text())
    res = call(Server(root), "render", path="examples/" + src.name, formats=["svg"])
    assert not res["isError"], res
    assert (root / "examples" / "01_candlestick_chart.svg").read_text() == src.with_suffix(".svg").read_text()


def test_paths_are_confined_to_root():
    for bad in ("../outside.py", "/etc/passwd"):
        res = call(Server(REPO), "render", path=bad)
        assert res["isError"] and "outside" in res["content"][0]["text"]
    assert call(Server(REPO), "render", path=SCRIPT, out="../elsewhere")["isError"]


def test_lint_list_and_bad_arguments():
    s = Server(REPO)
    lint = call(s, "lint", path="examples/finance")
    assert lint["structuredContent"]["findings"] == [] and lint["structuredContent"]["checked"] >= 10
    assert call(s, "lint", path=SCRIPT, ignore=["nonsense"])["isError"]
    assert call(s, "render", path=SCRIPT, formats=["gif"])["isError"]
    ex = json.loads(call(s, "list_examples", domain="finance")["content"][0]["text"])
    assert len(ex) >= 10 and all(e["rendered"] for e in ex)
    assert json.loads(call(s, "list_themes")["content"][0]["text"]) == cli.list_themes()
    err = s.handle({"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "render"}})
    assert err["error"]["code"] == -32602


def test_stdio_loop_is_protocol_only():
    inp = io.StringIO("\n".join([
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}), "not json",
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}), ""]))
    out = io.StringIO()
    assert serve(REPO, inp, out) == 0
    lines = [json.loads(l) for l in out.getvalue().splitlines()]
    assert lines[0]["result"] == {} and lines[1]["error"]["code"] == -32700 and len(lines) == 2


def test_cli_exposes_mcp_subcommand(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}) + "\n"))
    assert cli.main(["mcp", "--root", str(REPO)]) == 0
    assert json.loads(capsys.readouterr().out)["id"] == 1
