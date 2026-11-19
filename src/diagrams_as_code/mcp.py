"""Model Context Protocol server: drive diagrams-as-code from an MCP client.

A stdlib-only JSON-RPC 2.0 server over stdio (newline-delimited, MCP revision
2025-06-18). Start it with ``diagrams-as-code mcp [--root DIR]``. It exposes the
same operations as the CLI and the Python API: ``list_examples``, ``render``,
``lint``, ``list_themes`` and ``list_icons``.

Rendering runs a diagram script, which is arbitrary Python, so every script and
output path is confined to ``--root`` (default: the current directory).
"""
from __future__ import annotations

import contextlib
import json
import sys
import warnings
from importlib import metadata
from pathlib import Path
from typing import Any, Callable, Optional, TextIO

from diagrams_as_code.audit import DEFECTS, audit_findings
from diagrams_as_code.cli import discover, load_script
from diagrams_as_code.output import FORMATS, render_all
from diagrams_as_code.shapes import ShapeLibrary
from diagrams_as_code.theme import list_themes

PROTOCOL_VERSION = "2025-06-18"
try:
    _VERSION = metadata.version("diagrams-as-code")
except metadata.PackageNotFoundError:  # running from a bare checkout
    _VERSION = "unknown"
SERVER_INFO = {"name": "diagrams-as-code", "version": _VERSION}


class ToolError(Exception):
    """A failure the client should see as a tool result with ``isError`` set."""


def _inside(root: Path, raw: str, what: str) -> Path:
    path = (root / raw).resolve()
    if path != root and root not in path.parents:
        raise ToolError(f"{what} {raw!r} is outside the server root {root}")
    return path


def _scripts(root: Path, raw: str) -> list[Path]:
    target = _inside(root, raw, "path")
    if not target.exists():
        raise ToolError(f"{raw!r} does not exist")
    errors: list = []
    found = [s for s, _ in discover([target], errors)]
    if not found:
        raise ToolError(f"no diagram scripts found in {raw!r}")
    return found


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def tool_list_examples(root: Path, args: dict) -> Any:
    base = _inside(root, args.get("path", "examples"), "path")
    if not base.is_dir():
        raise ToolError(f"{args.get('path', 'examples')!r} is not a directory")
    domain = args.get("domain")
    out = []
    for script, sub in discover([base]):
        if domain and sub.parts[:1] != (domain,):
            continue
        svg = script.with_suffix(".svg")
        out.append({"script": _rel(root, script), "domain": str(sub) if str(sub) != "." else "",
                    "rendered": svg.exists() and _rel(root, svg) or None})
    return out


def tool_render(root: Path, args: dict) -> Any:
    formats = args.get("formats") or ["svg", "bom"]
    bad = sorted(set(formats) - set(FORMATS))
    if bad:
        raise ToolError(f"unknown format {', '.join(bad)}; choose from {', '.join(FORMATS)}")
    theme = args.get("theme")
    if theme and theme not in list_themes():
        raise ToolError(f"unknown theme {theme!r}; choose from {', '.join(list_themes())}")
    out_dir = _inside(root, args["out"], "out") if args.get("out") else None
    written, failed = [], []
    for script in _scripts(root, args["path"]):
        try:
            diag, stem = load_script(script)
            if theme:
                diag.configure(theme=theme)
            dest = out_dir or script.parent  # default: beside the script
            for fmt, p in render_all(diag, dest, stem, formats).items():
                written.append({"format": fmt, "file": _rel(root, p)})
        except Exception as exc:  # one bad script must not hide the others
            failed.append({"script": _rel(root, script), "error": str(exc)})
    if failed and not written:
        raise ToolError("; ".join(f"{f['script']}: {f['error']}" for f in failed))
    return {"written": written, "failed": failed}


def tool_lint(root: Path, args: dict) -> Any:
    ignore = set(args.get("ignore") or [])
    bad = sorted(ignore - set(DEFECTS))
    if bad:
        raise ToolError(f"unknown defect kind {', '.join(bad)}")
    findings, failed, checked = [], [], 0
    for script in _scripts(root, args["path"]):
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                diag, _ = load_script(script)
                found = [f for f in audit_findings(diag) if f.kind not in ignore]
            checked += 1
        except Exception as exc:
            failed.append({"script": _rel(root, script), "error": str(exc)})
            continue
        findings += [{"script": _rel(root, script), "kind": f.kind, "detail": f.detail} for f in found]
        findings += [{"script": _rel(root, script), "kind": "layout_warning", "detail": str(w.message)}
                     for w in caught]
    return {"checked": checked, "findings": findings, "failed": failed}


def tool_list_themes(root: Path, args: dict) -> Any:
    return list(list_themes())


def tool_list_icons(root: Path, args: dict) -> Any:
    domain = args.get("domain")
    return [{"name": n, "domain": d, "description": desc}
            for n, (d, desc) in sorted(ShapeLibrary._ICON_CATALOG.items())
            if domain is None or d == domain]


def _schema(props: dict, required: tuple = ()) -> dict:
    return {"type": "object", "properties": props, "required": list(required),
            "additionalProperties": False}


_STR = {"type": "string"}
TOOLS: dict[str, tuple[str, dict, Callable[[Path, dict], Any]]] = {
    "list_examples": ("List diagram scripts under a directory, with the SVG rendered beside each.",
                      _schema({"path": {**_STR, "description": "directory, default 'examples'"},
                               "domain": {**_STR, "description": "e.g. finance, physics, cad"}}),
                      tool_list_examples),
    "render": ("Render a diagram script, or every script in a directory. Output goes beside "
               "the script unless 'out' is given.",
               _schema({"path": _STR, "out": _STR,
                        "formats": {"type": "array", "items": {"enum": list(FORMATS)}},
                        "theme": {"enum": list(list_themes())}}, ("path",)),
               tool_render),
    "lint": ("Report visual defects (overlaps, clipped text, lines through nodes) in diagram scripts.",
             _schema({"path": _STR,
                      "ignore": {"type": "array", "items": {"enum": list(DEFECTS)}}}, ("path",)),
             tool_lint),
    "list_themes": ("List built-in themes.", _schema({}), tool_list_themes),
    "list_icons": ("List built-in icons, optionally for one domain.",
                   _schema({"domain": _STR}), tool_list_icons),
}


class Server:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def handle(self, msg: dict) -> Optional[dict]:
        """Reply to one JSON-RPC message; ``None`` for notifications."""
        mid, method = msg.get("id"), msg.get("method")
        params = msg.get("params") or {}
        if mid is None:  # notification (e.g. notifications/initialized)
            return None
        try:
            if method == "initialize":
                result: Any = {"protocolVersion": PROTOCOL_VERSION,
                               "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": [{"name": n, "description": d, "inputSchema": s}
                                    for n, (d, s, _) in TOOLS.items()]}
            elif method == "tools/call":
                result = self._call(params)
            else:
                return {"jsonrpc": "2.0", "id": mid,
                        "error": {"code": -32601, "message": f"method not found: {method}"}}
        except KeyError as exc:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"invalid params: missing {exc}"}}
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def _call(self, params: dict) -> dict:
        name = params["name"]
        if name not in TOOLS:
            raise KeyError(f"tool {name!r}")
        args = params.get("arguments") or {}
        if "path" in TOOLS[name][1]["required"] and "path" not in args:
            raise KeyError("path")
        try:
            with contextlib.redirect_stdout(sys.stderr):  # keep stdout protocol-only
                data = TOOLS[name][2](self.root, args)
            error = False
        except ToolError as exc:
            data, error = str(exc), True
        except Exception as exc:
            data, error = f"{type(exc).__name__}: {exc}", True
        text = data if isinstance(data, str) else json.dumps(data, indent=2)
        result: dict = {"content": [{"type": "text", "text": text}], "isError": error}
        if not error and isinstance(data, dict):
            result["structuredContent"] = data
        return result


def serve(root: Path, stdin: Optional[TextIO] = None, stdout: Optional[TextIO] = None) -> int:
    server = Server(root)
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    for line in stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
            reply = server.handle(msg) if isinstance(msg, dict) else None
            if reply is None and not isinstance(msg, dict):
                reply = {"jsonrpc": "2.0", "id": None,
                         "error": {"code": -32600, "message": "invalid request"}}
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        if reply is not None:
            stdout.write(json.dumps(reply) + "\n")
            stdout.flush()
    return 0
