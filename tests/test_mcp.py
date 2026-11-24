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


def _tool(server, name, **args):
    return call(server, name, **args)


def test_symlinked_script_and_output_cannot_escape_root(tmp_path):
    outside = tmp_path / "outside"
    root = tmp_path / "root"
    outside.mkdir()
    root.mkdir()
    (outside / "evil.py").write_text(
        "from diagrams_as_code import Diagram, Shape\n"
        "def diagram():\n    open(%r, 'w').write('ran')\n    return Diagram('x')\n" % str(outside / "ran.txt"))
    (root / "evil.py").symlink_to(outside / "evil.py")
    res = _tool(Server(root), "render", path=".")
    assert res["isError"] and not (outside / "ran.txt").exists()

    (root / "ok.py").write_text((REPO / SCRIPT).read_text())
    (outside / "target.svg").write_text("keep")
    (root / "candlestick.svg").symlink_to(outside / "target.svg")
    (root / "ok.py").write_text(
        "from diagrams_as_code import Diagram\nOUTPUT_STEM = 'candlestick'\n"
        "def diagram():\n    return Diagram('x')\n")
    (root / "evil.py").unlink()
    res = _tool(Server(root), "render", path="ok.py")
    assert res["isError"] and (outside / "target.svg").read_text() == "keep"


def test_script_chosen_output_stem_must_be_plain(tmp_path):
    (tmp_path / "s.py").write_text(
        "from diagrams_as_code import Diagram\nOUTPUT_STEM = '../escaped'\n"
        "def diagram():\n    return Diagram('x')\n")
    res = _tool(Server(tmp_path), "render", path="s.py")
    assert res["isError"] and not (tmp_path.parent / "escaped.svg").exists()


def test_errors_do_not_leak_the_absolute_root(tmp_path):
    (tmp_path / "s.py").write_text("def diagram():\n    raise RuntimeError(%r)\n" % (str(tmp_path) + "/x"))
    res = _tool(Server(tmp_path), "render", path="s.py")
    assert res["isError"] and str(tmp_path) not in res["content"][0]["text"]


def test_malformed_messages_never_end_the_session():
    lines = ["[" * 100000, json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": "x"}),
             json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": []}}),
             json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                         "params": {"name": "list_themes", "arguments": "x"}}),
             json.dumps({"jsonrpc": "2.0", "id": 4, "method": "ping"}), ""]
    out = io.StringIO()
    assert serve(REPO, io.StringIO("\n".join(lines)), out) == 0
    replies = [json.loads(l) for l in out.getvalue().splitlines()]
    assert replies[-1]["id"] == 4 and replies[-1]["result"] == {}
    assert all("error" in r for r in replies[:-1])


def test_oversized_message_is_rejected_and_skipped(monkeypatch):
    from diagrams_as_code import mcp
    monkeypatch.setattr(mcp, "MAX_LINE", 64)
    big = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping", "pad": "x" * 500})
    ok = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"})
    out = io.StringIO()
    mcp.serve(REPO, io.StringIO(big + "\n" + ok + "\n"), out)
    replies = [json.loads(l) for l in out.getvalue().splitlines()]
    assert replies[0]["error"]["code"] == -32600 and replies[1]["id"] == 2


# --- sandbox: a script cannot hang, flood or corrupt the server --------------

def _script(tmp_path, body):
    (tmp_path / "s.py").write_text(
        "from diagrams_as_code import Diagram, Shape\n" + body +
        "\ndef diagram():\n    d = Diagram('t')\n    d.add(Shape('a', 'A'))\n    return d\n")


def test_script_that_never_returns_is_killed_at_the_timeout(tmp_path):
    import time
    from diagrams_as_code.sandbox import Limits
    _script(tmp_path, "while True:\n    pass")
    t0 = time.monotonic()
    res = call(Server(tmp_path, Limits(timeout=1.5, cpu=60)), "render", path="s.py")
    assert res["isError"] and "time limit" in res["content"][0]["text"]
    assert time.monotonic() - t0 < 10


def test_script_cannot_write_to_stdout_or_read_stdin(tmp_path):
    _script(tmp_path, "import os, sys\nos.write(1, b'{garbage}\\n')\nsys.stdin.read()")
    out = io.StringIO()
    req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                      "params": {"name": "lint", "arguments": {"path": "s.py"}}})
    serve(tmp_path, io.StringIO(req + "\n"), out)
    lines = out.getvalue().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["id"] == 1


def test_script_exit_or_crash_is_a_tool_error_not_a_server_crash(tmp_path):
    _script(tmp_path, "import sys\nsys.exit(3)")
    s = Server(tmp_path)
    assert call(s, "render", path="s.py")["isError"]
    assert call(s, "list_themes")["isError"] is False  # server still serving


def test_script_over_the_cpu_limit_is_stopped(tmp_path):
    import os
    import pytest
    if os.name != "posix":
        pytest.skip("rlimits are POSIX only")
    from diagrams_as_code.sandbox import Limits
    _script(tmp_path, "while True:\n    pass")
    res = call(Server(tmp_path, Limits(timeout=30, cpu=1)), "lint", path="s.py")
    assert res["structuredContent"]["failed"] and res["structuredContent"]["checked"] == 0


def test_script_over_the_memory_limit_fails_cleanly(tmp_path):
    import sys
    import pytest
    if sys.platform != "linux":
        pytest.skip("address-space limits are only enforced on Linux")
    from diagrams_as_code.sandbox import Limits
    _script(tmp_path, "x = bytearray(1 << 30)")
    res = call(Server(tmp_path, Limits(timeout=30, memory_mb=256)), "lint", path="s.py")
    assert res["structuredContent"]["failed"]


def test_cli_passes_limits_through(monkeypatch):
    seen = {}
    monkeypatch.setattr("diagrams_as_code.mcp.serve", lambda root, **kw: seen.update(kw) or 0)
    assert cli.main(["mcp", "--timeout", "5", "--memory-mb", "512"]) == 0
    assert seen == {"timeout": 5.0, "memory_mb": 512}
