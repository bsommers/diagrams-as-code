"""Model Context Protocol server: drive diagrams-as-code from an MCP client.

A stdlib-only JSON-RPC 2.0 server over stdio (newline-delimited, MCP revision
2025-06-18). Start it with ``diagrams-as-code mcp [--root DIR]``. It exposes the
same operations as the CLI and the Python API: ``list_examples``, ``render``,
``lint``, ``list_themes`` and ``list_icons``; and, so a client with no file-write
tool can still create a diagram, ``render_source`` and ``lint_source`` (script
text in, result out) plus the discovery tools ``get_example``, ``list_domains``,
``describe_api`` and ``capabilities``.

Rendering runs a diagram script, which is arbitrary Python (this includes the
``source`` text given to ``render_source`` / ``lint_source``), so every script and
output path is confined to ``--root`` (default: the current directory), and each
script runs in a resource-limited child process (see :mod:`.sandbox`): a wall-clock
timeout, CPU and memory caps, no stdin and no stdout.

Failures are structured: a tool error result carries ``{"error": {"code",
"message", "line"?}}`` as both its text and its ``structuredContent``. ``code`` is one
of :data:`diagrams_as_code.agent_api.ERROR_CODES`; ``line`` is the line of the
user's script that raised.
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
from importlib import metadata
from pathlib import Path
from typing import Any, Callable, Optional, TextIO

from diagrams_as_code import agent_api
from diagrams_as_code.audit import DEFECTS
from diagrams_as_code.cli import discover
from diagrams_as_code.output import FORMATS
from diagrams_as_code.sandbox import Limits, SandboxError
from diagrams_as_code.sandbox import run as run_sandboxed
from diagrams_as_code.shapes import ShapeLibrary
from diagrams_as_code.theme import list_themes

PROTOCOL_VERSION = "2025-06-18"
MAX_LINE = 1 << 20  # bytes of one JSON-RPC message
MAX_RESULT_CHARS = 200_000
try:
    _VERSION = metadata.version("diagrams-as-code")
except metadata.PackageNotFoundError:  # running from a bare checkout
    _VERSION = "unknown"
SERVER_INFO = {"name": "diagrams-as-code", "version": _VERSION}


class ToolError(Exception):
    """A failure the client should see as a tool result with ``isError`` set."""

    def __init__(self, message: str, code: str = "invalid_argument",
                 line: Optional[int] = None) -> None:
        super().__init__(message)
        self.code = code
        self.line = line


def _inside(root: Path, raw: Any, what: str) -> Path:
    if not isinstance(raw, str):
        raise ToolError(f"{what} must be a string")
    path = (root / raw).resolve()
    if path != root and root not in path.parents:
        raise ToolError(f"{what} {raw!r} is outside the server root", "path_outside_root")
    return path


def _from_sandbox(root: Path, exc: SandboxError) -> ToolError:
    return ToolError(_clean(root, str(exc)), exc.code, exc.line)


def _scripts(root: Path, raw: str) -> list[Path]:
    target = _inside(root, raw, "path")
    if not target.exists():
        raise ToolError(f"{raw!r} does not exist", "not_found")
    errors: list = []
    # A symlink inside root can point outside it: re-resolve every script found.
    found = [s for s, _ in discover([target], errors)
             if s.resolve() == root or root in s.resolve().parents]
    if not found:
        raise ToolError(f"no diagram scripts found in {raw!r}", "no_scripts")
    return found


def _check_outputs(root: Path, dest: Path, stem: str, formats: list) -> None:
    """Refuse a script-chosen stem or an existing symlink that would write outside root."""
    if not stem or "/" in stem or "\\" in stem or stem in (".", "..") or ".." in Path(stem).parts:
        raise ToolError(f"output name {stem!r} is not a plain file stem", "output_error")
    for suffix in {"svg": ".svg", "png": ".png", "pdf": ".pdf", "bom": "_README.md"}.values():
        target = dest / f"{stem}{suffix}"
        if target.is_symlink() or not (target.resolve().parent == root
                                       or root in target.resolve().parents):
            raise ToolError(f"refusing to write {_rel(root, target)}: it leaves the server root",
                            "output_error")


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return path.name  # never leak an absolute path outside the root


def _clean(root: Path, text: str) -> str:
    """Drop the server root's absolute path from a message sent to the client."""
    return agent_api.scrub(text, {str(root): ".", os.path.realpath(root): "."})


def tool_list_examples(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    base = _inside(root, args.get("path", "examples"), "path")
    if not base.is_dir():
        raise ToolError(f"{args.get('path', 'examples')!r} is not a directory", "not_found")
    domain = args.get("domain")
    out = []
    for script, sub in discover([base]):
        if domain and sub.parts[:1] != (domain,):
            continue
        svg = script.with_suffix(".svg")
        out.append({"script": _rel(root, script), "domain": str(sub) if str(sub) != "." else "",
                    "rendered": svg.exists() and _rel(root, svg) or None})
    return out


def tool_render(root: Path, args: dict, limits: Limits = Limits()) -> Any:
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
            result = run_sandboxed({"op": "render", "script": str(script),
                                    "formats": formats, "theme": theme}, limits)
            dest = out_dir or script.parent  # default: beside the script
            _check_outputs(root, dest, result["stem"], formats)
            dest.mkdir(parents=True, exist_ok=True)
            for fmt, (name, data) in result["files"].items():
                (dest / name).write_bytes(data)
                written.append({"format": fmt, "file": _rel(root, dest / name)})
        except (SandboxError, ToolError, OSError, ValueError) as exc:  # one bad script must not hide the others
            failed.append({"script": _rel(root, script), "error": _clean(root, str(exc)),
                           "code": getattr(exc, "code", "output_error"),
                           **({"line": exc.line} if getattr(exc, "line", None) else {})})
    if failed and not written:
        raise ToolError("; ".join(f"{f['script']}: {f['error']}" for f in failed),
                        failed[0]["code"], failed[0].get("line"))
    return {"written": written, "failed": failed}


def tool_lint(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    ignore = set(args.get("ignore") or [])
    bad = sorted(ignore - set(DEFECTS))
    if bad:
        raise ToolError(f"unknown defect kind {', '.join(bad)}")
    findings, failed, checked = [], [], 0
    for script in _scripts(root, args["path"]):
        rel = _rel(root, script)
        try:
            result = run_sandboxed({"op": "lint", "script": str(script),
                                    "ignore": sorted(ignore)}, limits)
        except SandboxError as exc:
            failed.append({"script": rel, "error": _clean(root, str(exc)), "code": exc.code,
                           **({"line": exc.line} if exc.line else {})})
            continue
        checked += 1
        findings += [{"script": rel, **f}
                     for f in result["findings"] + agent_api.findings_json((), result["warnings"])]
    return {"checked": checked, "findings": findings, "failed": failed}


def tool_list_themes(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    return list(list_themes())


def tool_list_icons(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    domain = args.get("domain")
    return [{"name": n, "domain": d, "description": desc}
            for n, (d, desc) in sorted(ShapeLibrary._ICON_CATALOG.items())
            if domain is None or d == domain]


# --- tools that take script text (no file needed) ----------------------------

def _clip(text: str) -> tuple[str, bool]:
    return text[:agent_api.MAX_INLINE_CHARS], len(text) > agent_api.MAX_INLINE_CHARS


def _source(args: dict) -> str:
    src = args["source"]
    if not isinstance(src, str) or not src.strip():
        raise ToolError("source must be a non-empty string")
    if len(src) > agent_api.MAX_SOURCE_CHARS:
        raise ToolError(f"source is {len(src)} characters; the limit is {agent_api.MAX_SOURCE_CHARS}")
    return src


def tool_render_source(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    src = _source(args)
    formats = args.get("formats") or ["svg"]
    bad = sorted(set(formats) - set(FORMATS))
    if bad:
        raise ToolError(f"unknown format {', '.join(bad)}; choose from {', '.join(FORMATS)}")
    theme = args.get("theme")
    if theme and theme not in list_themes():
        raise ToolError(f"unknown theme {theme!r}; choose from {', '.join(list_themes())}")
    out_dir = _inside(root, args["out"], "out") if args.get("out") else None
    inline = args.get("inline", out_dir is None)
    if out_dir is None and not inline:
        raise ToolError("nothing to return: set inline=true or give an out directory")
    if inline and not out_dir and set(formats) & {"png", "pdf"}:
        raise ToolError("png and pdf are binary; give an out directory to write them")
    name = args.get("name")
    if name is not None:
        try:
            agent_api.plain_name(name, "name")
        except ValueError as exc:
            raise ToolError(str(exc)) from None
    wanted = set(formats)
    needed = [f for f in FORMATS if f in wanted | ({"svg"} if inline else set())]
    try:
        result = run_sandboxed({"op": "render", "source": src, "formats": needed,
                                "theme": theme, "stem": name}, limits)
    except SandboxError as exc:
        raise _from_sandbox(root, exc) from None
    stem = result["stem"]
    out: dict = {"stem": stem, "written": []}
    if out_dir is not None:
        _check_outputs(root, out_dir, stem, formats)
        out_dir.mkdir(parents=True, exist_ok=True)
        for fmt in FORMATS:
            if fmt in wanted and fmt in result["files"]:
                fname, data = result["files"][fmt]
                (out_dir / fname).write_bytes(data)
                out["written"].append({"format": fmt, "file": _rel(root, out_dir / fname)})
    if inline:
        for fmt in ("svg", "bom"):
            if fmt in result["files"] and (fmt == "svg" or fmt in wanted):
                text = result["files"][fmt][1].decode("utf-8", "replace")
                out[fmt], out[f"{fmt}_truncated"] = _clip(text)
                out[f"{fmt}_chars"] = len(text)
    return out


def tool_lint_source(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    src = _source(args)
    ignore = set(args.get("ignore") or [])
    bad = sorted(ignore - set(DEFECTS))
    if bad:
        raise ToolError(f"unknown defect kind {', '.join(bad)}")
    try:
        result = run_sandboxed({"op": "lint", "source": src, "ignore": sorted(ignore)}, limits)
    except SandboxError as exc:
        raise _from_sandbox(root, exc) from None
    findings = result["findings"] + agent_api.findings_json((), result["warnings"])
    return {"checked": 1, "count": len(findings), "findings": findings}


# --- discovery tools ---------------------------------------------------------

def _examples_dir(root: Path) -> Path:
    found = agent_api.find_examples_dir(root)
    if found is None:
        raise ToolError("no examples directory is available", "not_found")
    return found


def tool_get_example(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    try:
        return agent_api.read_example(_examples_dir(root), args["domain"], args["name"])
    except LookupError as exc:
        raise ToolError(str(exc), "not_found") from None
    except ValueError as exc:
        raise ToolError(str(exc)) from None


def tool_list_domains(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    doms = agent_api.domains(_examples_dir(root))
    return {"total": sum(d["count"] for d in doms), "domains": doms}


def tool_describe_api(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    name = args.get("name")
    ref = agent_api.api_reference(name)
    if name and not ref["entries"]:
        raise ToolError(f"no public API name matches {name!r}", "not_found")
    return ref


def tool_capabilities(root: Path, args: dict, limits: Limits = Limits()) -> Any:
    path = agent_api.find_capabilities(root)
    if path is None:
        raise ToolError("docs/capabilities.json is not available in this installation", "not_found")
    return agent_api.capabilities_summary(path, args.get("category"))


def _schema(props: dict, required: tuple = ()) -> dict:
    return {"type": "object", "properties": props, "required": list(required),
            "additionalProperties": False}


def _out(props: dict) -> dict:
    """An outputSchema. Nothing is ``required`` so an error's ``{"error": ...}`` also fits."""
    return {"type": "object", "properties": {**props, "error": _ERROR}}


_STR = {"type": "string"}
_BOOL = {"type": "boolean"}
_ERROR = {"type": "object", "description": "Present only on failure.",
          "properties": {"code": {"enum": list(agent_api.ERROR_CODES)}, "message": _STR,
                         "line": {"type": "integer", "description": "line of the script that raised"}},
          "required": ["code", "message"]}
_FORMATS = {"type": "array", "items": {"enum": list(FORMATS)}, "uniqueItems": True,
            "description": "svg, png, pdf (binary: need out) and bom (a Markdown bill of materials)"}
_THEME = {"enum": list(list_themes()), "description": "overrides the script's own theme"}
_IGNORE = {"type": "array", "items": {"enum": list(DEFECTS)},
           "description": "defect kinds not to report"}
_SOURCE = {**_STR, "description": "Python text defining diagram() -> Diagram (see describe_api, "
           f"get_example); at most {agent_api.MAX_SOURCE_CHARS} characters. It RUNS as arbitrary "
           "Python in the resource-limited sandbox"}
_FINDING = {"type": "object", "properties": {
    "kind": {"enum": list(DEFECTS) + ["layout_warning"]}, "detail": _STR,
    "ids": {"type": "array", "items": _STR, "description": "ids of the elements involved, where known"}}}
_ENTRY = {"type": "object", "properties": {
    "name": _STR, "module": _STR, "kind": {"enum": ["class", "function", "constant"]},
    "signature": {"type": ["string", "null"]}, "summary": _STR,
    "members": {"type": "array", "items": {"type": "object"}}}}

ToolFn = Callable[[Path, dict, Limits], Any]
#: name -> (description, inputSchema, outputSchema or None, handler)
TOOLS: dict[str, tuple[str, dict, Optional[dict], ToolFn]] = {
    "list_examples": ("List diagram scripts under a directory, with the SVG rendered beside each.",
                      _schema({"path": {**_STR, "description": "directory, default 'examples'"},
                               "domain": {**_STR, "description": "e.g. finance, physics, cad"}}),
                      None, tool_list_examples),
    "render": ("Render a diagram script file (or every script in a directory) under the server "
               "root. Output goes beside the script unless 'out' is given. To render script text "
               "you have no file for, use render_source.",
               _schema({"path": {**_STR, "description": "script or directory, relative to the root"},
                        "out": {**_STR, "description": "output directory under the root"},
                        "formats": _FORMATS, "theme": _THEME}, ("path",)),
               _out({"written": {"type": "array", "items": {"type": "object", "properties": {
                         "format": _STR, "file": _STR}}},
                     "failed": {"type": "array", "items": {"type": "object"}}}),
               tool_render),
    "lint": ("Report visual defects (overlaps, clipped text, lines through nodes) in diagram "
             "script files. For script text, use lint_source.",
             _schema({"path": {**_STR, "description": "script or directory, relative to the root"},
                      "ignore": _IGNORE}, ("path",)),
             _out({"checked": {"type": "integer"},
                   "findings": {"type": "array", "items": {"type": "object"}},
                   "failed": {"type": "array", "items": {"type": "object"}}}),
             tool_lint),
    "render_source": (
        "Render diagram script TEXT (a program defining diagram() -> Diagram) without any file. "
        "Returns the SVG inline (default when 'out' is omitted; cut at "
        f"{agent_api.MAX_INLINE_CHARS} characters, see svg_truncated) and/or writes files "
        "under 'out' inside the server root. The source runs as arbitrary Python in the "
        "sandbox (timeout, CPU/memory caps, no stdin/stdout); it is not file or network "
        "isolation. Output is byte-identical to render of the same script.",
        _schema({"source": _SOURCE, "formats": _FORMATS, "theme": _THEME,
                 "inline": {**_BOOL, "description": "return the SVG (and bom) text; default "
                            "true when 'out' is omitted, false otherwise"},
                 "out": {**_STR, "description": "directory under the root to write files into"},
                 "name": {**_STR, "description": "output file stem; default the script's "
                          "OUTPUT_STEM or 'script'"}}, ("source",)),
        _out({"stem": _STR, "written": {"type": "array", "items": {"type": "object", "properties": {
                  "format": _STR, "file": _STR}}},
              "svg": _STR, "svg_truncated": _BOOL, "svg_chars": {"type": "integer"},
              "bom": _STR, "bom_truncated": _BOOL}),
        tool_render_source),
    "lint_source": (
        "Lay out diagram script TEXT and report visual defects as structured findings "
        "(kind, detail, element ids). Same sandbox and caveats as render_source. An empty "
        "findings list means no defect was detected.",
        _schema({"source": _SOURCE, "ignore": _IGNORE}, ("source",)),
        _out({"checked": {"type": "integer"}, "count": {"type": "integer"},
              "findings": {"type": "array", "items": _FINDING}}),
        tool_lint_source),
    "get_example": (
        "Return one gallery example's script text and its committed SVG: a working template to "
        "adapt for render_source. Find names with list_domains.",
        _schema({"domain": {**_STR, "description": "gallery domain, e.g. finance, cad, iiot "
                            "('root' for the top-level scripts)"},
                 "name": {**_STR, "description": "script stem, e.g. 01_candlestick_chart; the "
                          "numeric prefix may be omitted"}}, ("domain", "name")),
        _out({"domain": _STR, "name": _STR, "title": _STR, "script": _STR, "source": _STR,
              "source_truncated": _BOOL, "svg": _STR, "svg_truncated": _BOOL}),
        tool_get_example),
    "list_domains": ("List the example gallery's domains with the number and titles of the "
                     "examples in each.", _schema({}),
                     _out({"total": {"type": "integer"}, "domains": {"type": "array", "items": {
                         "type": "object", "properties": {"domain": _STR,
                         "count": {"type": "integer"}, "titles": {"type": "array", "items": _STR}}}}}),
                     tool_list_domains),
    "describe_api": (
        "Structured reference of the public Python API a diagram script can use: every name in "
        "diagrams_as_code.__all__ plus the kit modules plot, draft, sequence and gantt, each "
        "with kind, signature and a one-line summary, built by introspection. Pass 'name' (a "
        "class or function, a kit module such as 'gantt', or a substring) to narrow it; one or "
        "a few matching classes also list their methods.",
        _schema({"name": {**_STR, "description": "exact name, kit module or substring, "
                          "case-insensitive"}}),
        _out({"total": {"type": "integer"}, "returned": {"type": "integer"}, "truncated": _BOOL,
              "modules": {"type": "array", "items": _STR},
              "entries": {"type": "array", "items": _ENTRY}}),
        tool_describe_api),
    "capabilities": (
        "Summary of docs/capabilities.json, the project's verified capability manifest: ids, "
        "titles, categories, status and the command that verifies each.",
        _schema({"category": {**_STR, "description": "only this category"}}),
        _out({"version": _STR, "total": {"type": "integer"},
              "categories": {"type": "array", "items": _STR},
              "capabilities": {"type": "array", "items": {"type": "object", "properties": {
                  "id": _STR, "title": _STR, "category": _STR, "status": _STR,
                  "verification": _STR}}}}),
        tool_capabilities),
    "list_themes": ("List built-in themes.", _schema({}), None, tool_list_themes),
    "list_icons": ("List built-in icons, optionally for one domain.",
                   _schema({"domain": _STR}), None, tool_list_icons),
}

_JSON_TYPES = {"string": str, "boolean": bool, "array": list, "integer": int, "object": dict}


def _validate(args: dict, schema: dict) -> None:
    """Reject unknown keys, wrong types and values outside an enum, as ``invalid_argument``."""
    props = schema["properties"]
    for key, value in args.items():
        if key not in props:
            raise ToolError(f"unknown argument {key!r}; allowed: {', '.join(props) or 'none'}")
        spec = props[key]
        want = _JSON_TYPES.get(spec.get("type", ""))
        if want and (not isinstance(value, want) or (want is int and isinstance(value, bool))):
            raise ToolError(f"{key} must be a {spec['type']}")
        if "enum" in spec and value not in spec["enum"]:
            raise ToolError(f"{key} {value!r} is not one of: {', '.join(map(str, spec['enum']))}")
        if isinstance(value, list) and "enum" in spec.get("items", {}):
            bad = [v for v in value if v not in spec["items"]["enum"]]
            if bad:
                raise ToolError(f"{key} has unknown value(s) {bad}; choose from "
                                f"{', '.join(spec['items']['enum'])}")


class Server:
    def __init__(self, root: Path, limits: Limits = Limits()) -> None:
        self.root = root.resolve()
        self.limits = limits

    def handle(self, msg: dict) -> Optional[dict]:
        """Reply to one JSON-RPC message; ``None`` for notifications."""
        mid, method = msg.get("id"), msg.get("method")
        params = msg.get("params") or {}
        if mid is None:  # notification (e.g. notifications/initialized)
            return None
        if not isinstance(params, dict) or not isinstance(method, str):
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32600, "message": "invalid request"}}
        try:
            if method == "initialize":
                result: Any = {"protocolVersion": PROTOCOL_VERSION,
                               "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": [{"name": n, "description": d, "inputSchema": s,
                                     **({"outputSchema": o} if o else {})}
                                    for n, (d, s, o, _) in TOOLS.items()]}
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
        if not isinstance(name, str) or name not in TOOLS:
            raise KeyError(f"tool {name!r}")
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            raise KeyError("arguments (an object)")
        _, schema, _, fn = TOOLS[name]
        for required in schema["required"]:
            if required not in args:
                raise KeyError(required)
        error: Optional[dict] = None
        data: Any = None
        try:
            _validate(args, schema)
            with contextlib.redirect_stdout(sys.stderr):  # keep stdout protocol-only
                data = fn(self.root, args, self.limits)
        except ToolError as exc:
            error = agent_api.error_dict(exc.code, _clean(self.root, str(exc)), exc.line)
        except Exception as exc:
            error = agent_api.error_dict("internal_error",
                                         _clean(self.root, f"{type(exc).__name__}: {exc}"))
        if error is not None:
            data = {"error": error}
        text = data if isinstance(data, str) else json.dumps(data, indent=2)
        if len(text) > MAX_RESULT_CHARS:
            text = text[:MAX_RESULT_CHARS] + "\n... [truncated]"
        result: dict = {"content": [{"type": "text", "text": text}], "isError": error is not None}
        if isinstance(data, dict):
            result["structuredContent"] = data
        return result


def _error(code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": None, "error": {"code": code, "message": message}}


def serve(root: Path, stdin: Optional[TextIO] = None, stdout: Optional[TextIO] = None,
          timeout: float = Limits.timeout, memory_mb: int = Limits.memory_mb) -> int:
    server = Server(root, Limits(timeout=timeout, cpu=max(1, int(timeout)), memory_mb=memory_mb))
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    while True:
        line = stdin.readline(MAX_LINE + 1)
        if not line:
            return 0
        if len(line) > MAX_LINE and not line.endswith("\n"):
            while line and not line.endswith("\n"):  # discard the rest of the oversized message
                line = stdin.readline(MAX_LINE)
            reply: Optional[dict] = _error(-32600, "message too large")
        elif not line.strip():
            continue
        else:
            try:
                msg = json.loads(line)
                reply = server.handle(msg) if isinstance(msg, dict) else _error(-32600, "invalid request")
            except (json.JSONDecodeError, RecursionError):
                reply = _error(-32700, "parse error")
            except Exception:  # one bad message must never end the session
                reply = _error(-32603, "internal error")
        if reply is not None:
            stdout.write(json.dumps(reply) + "\n")
            stdout.flush()
