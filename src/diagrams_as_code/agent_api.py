"""Machine-facing helpers shared by the CLI and the MCP server.

Pure functions that turn the library's facts into plain JSON-able data: a reference
of the public Python API built by introspection, the example gallery (domains,
titles, source), the capability manifest, structured lint findings and structured
errors. The CLI (``--json``, ``api``, ``examples``, ``source``) and the MCP tools
(``describe_api``, ``list_domains``, ``get_example``, ``capabilities``, ...) both
call these, so the two surfaces cannot drift apart.

Nothing here runs a diagram script or touches the network.
"""
from __future__ import annotations

import ast
import importlib
import inspect
import json
import os
import re
import traceback
from pathlib import Path
from typing import Any, Iterable, Optional

#: Stable machine-readable error codes. A client may switch on these.
ERROR_CODES: tuple[str, ...] = (
    "invalid_argument",    # a missing, mistyped or out-of-range argument
    "path_outside_root",   # a path resolves outside the server root
    "not_found",           # a named path, example or capability does not exist
    "no_scripts",          # a directory holds no diagram scripts
    "script_error",        # the script raised, exited or defined no diagram()
    "timeout",             # the script ran past the wall-clock limit
    "resource_limit",      # the script was killed for CPU or memory
    "sandbox_failure",     # the child process ended without a result
    "output_error",        # a file could not be written or an output name is unsafe
    "internal_error",      # a bug in the server, not in the request
)

MAX_SOURCE_CHARS = 200_000   # largest ``source`` accepted by render_source / lint_source
MAX_INLINE_CHARS = 100_000   # largest SVG/BOM/source text returned inline
MAX_API_CHARS = 60_000       # budget for one API reference document
MAX_MEMBERS = 80             # methods listed for one class

#: Kit modules documented beside the names in ``diagrams_as_code.__all__``.
KIT_MODULES: tuple[str, ...] = ("plot", "draft", "sequence", "gantt")

_PLAIN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-]*$")


# --- errors ------------------------------------------------------------------

def error_dict(code: str, message: str, line: Optional[int] = None) -> dict[str, Any]:
    """The one shape every machine-readable error takes."""
    err: dict[str, Any] = {"code": code, "message": message}
    if line is not None:
        err["line"] = line
    return err


def script_line(exc: BaseException, script: Any) -> Optional[int]:
    """The line in the user's ``script`` that raised ``exc``, from its traceback."""
    target = os.path.realpath(str(script))
    if isinstance(exc, SyntaxError) and exc.filename and os.path.realpath(exc.filename) == target:
        return exc.lineno
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if os.path.realpath(frame.filename) == target:
            line = frame.lineno  # the innermost frame inside the script
    return line


def scrub(text: str, names: dict[str, str]) -> str:
    """Replace each absolute path in ``names`` (path -> placeholder) in ``text``."""
    for path, placeholder in sorted(names.items(), key=lambda kv: -len(kv[0])):
        if path:
            text = text.replace(path, placeholder)
    return text


def plain_name(value: Any, what: str) -> str:
    """``value`` if it is a plain file stem or name, else ``ValueError``."""
    if not isinstance(value, str) or not _PLAIN.match(value) or ".." in value:
        raise ValueError(f"{what} {value!r} is not a plain name")
    return value


# --- lint findings -----------------------------------------------------------

def findings_json(findings: Iterable[Any], warnings: Iterable[Any] = ()) -> list[dict[str, Any]]:
    """Audit findings (and layout warnings) as ``{kind, detail, ids}`` dicts."""
    out = [{"kind": f.kind, "detail": f.detail, "ids": list(getattr(f, "ids", ()))}
           for f in findings]
    out += [{"kind": "layout_warning", "detail": str(w), "ids": []} for w in warnings]
    return out


# --- public API reference ----------------------------------------------------

def _is_callable_def(obj: Any) -> bool:
    return inspect.isclass(obj) or inspect.isroutine(obj)


def _summary(obj: Any) -> str:
    if _is_callable_def(obj) or inspect.ismodule(obj):
        doc = inspect.getdoc(obj)
        return doc.strip().splitlines()[0].strip() if doc else ""
    return f"{type(obj).__name__} instance"


class _Bare(str):
    """An annotation string that prints without quotes inside a signature."""

    def __repr__(self) -> str:
        return str(self)


def _signature(obj: Any) -> Optional[str]:
    if not _is_callable_def(obj):
        return None
    try:
        sig = inspect.signature(obj)
    except (TypeError, ValueError):
        return "(...)"
    # Postponed annotations are strings: show them bare, not as quoted literals.
    params = [p.replace(annotation=_Bare(p.annotation)) if isinstance(p.annotation, str) else p
              for p in sig.parameters.values()]
    ret = sig.return_annotation
    return str(sig.replace(parameters=params,
                           return_annotation=_Bare(ret) if isinstance(ret, str) else ret))


def _kind(obj: Any) -> str:
    if inspect.isclass(obj):
        return "class"
    if inspect.isroutine(obj):
        return "function"
    return "constant"


def _entry(name: str, obj: Any, module: str, members: bool = False) -> dict[str, Any]:
    entry: dict[str, Any] = {"name": name, "module": module, "kind": _kind(obj),
                             "signature": _signature(obj), "summary": _summary(obj)}
    if members and inspect.isclass(obj):
        found = []
        for mname, member in inspect.getmembers(obj):
            if mname.startswith("_"):
                continue
            if isinstance(member, property):
                found.append({"name": mname, "kind": "property", "signature": None,
                              "summary": _summary(member.fget) if member.fget else ""})
            elif inspect.isroutine(member) and getattr(member, "__module__", "").startswith(
                    "diagrams_as_code"):
                found.append({"name": mname, "kind": "method", "signature": _signature(member),
                              "summary": _summary(member)})
        entry["members"] = found[:MAX_MEMBERS]
    return entry


def _kit_names(mod: Any) -> list[str]:
    declared = getattr(mod, "__all__", None)
    if declared is not None:
        return sorted(declared)
    return sorted(n for n, o in vars(mod).items()
                  if not n.startswith("_") and (inspect.isclass(o) or inspect.isfunction(o))
                  and getattr(o, "__module__", None) == mod.__name__)


def api_names() -> list[tuple[str, str]]:
    """Every documented ``(module, name)``: ``__all__`` first, then the kit modules."""
    top = importlib.import_module("diagrams_as_code")
    names = [("diagrams_as_code", n) for n in top.__all__]
    for kit in KIT_MODULES:
        mod = importlib.import_module(f"diagrams_as_code.{kit}")
        names += [(f"diagrams_as_code.{kit}", n) for n in _kit_names(mod)]
    return names


def api_reference(name: Optional[str] = None, max_chars: int = MAX_API_CHARS) -> dict[str, Any]:
    """Structured reference of the public Python API.

    ``name`` filters: an exact (case-insensitive) name, else a kit module
    (``plot``, ``gantt``...), else a substring. A match of up to three names lists
    each class's public methods. The result is cut to ``max_chars`` of JSON
    (``truncated``).
    """
    pairs = api_names()
    if name:
        key = name.strip().lower().removeprefix("diagrams_as_code.")
        exact = [p for p in pairs if p[1].lower() == key]
        kit = [p for p in pairs if p[0].lower() == f"diagrams_as_code.{key}"]
        pairs = exact or kit or [p for p in pairs if key in p[1].lower()]
    detailed = bool(name) and len(pairs) <= 3
    entries = [_entry(n, getattr(importlib.import_module(m), n, None), m, members=detailed)
               for m, n in pairs]
    size, kept = 0, []
    for e in entries:
        size += len(json.dumps(e))
        if size > max_chars:
            break
        kept.append(e)
    return {"total": len(entries), "returned": len(kept), "truncated": len(kept) < len(entries),
            "entries": kept,
            "modules": ["diagrams_as_code", *(f"diagrams_as_code.{k}" for k in KIT_MODULES)]}


def format_api(ref: dict[str, Any]) -> str:
    """Human-readable lines for :func:`api_reference` (``api`` without ``--json``)."""
    lines = []
    for e in ref["entries"]:
        lines.append(f"{e['module']}.{e['name']}{e['signature'] or ''}  [{e['kind']}]")
        if e["summary"]:
            lines.append(f"    {e['summary']}")
        for m in e.get("members", ()):
            lines.append(f"    .{m['name']}{m['signature'] or ''}  {m['summary']}".rstrip())
    if ref["truncated"]:
        lines.append(f"... {ref['total'] - ref['returned']} more; pass a NAME to narrow")
    return "\n".join(lines)


# --- example gallery ---------------------------------------------------------

def find_examples_dir(root: Path) -> Optional[Path]:
    """``root/examples`` if present, else the examples beside a source checkout."""
    for cand in (root / "examples", Path(__file__).resolve().parents[2] / "examples"):
        if cand.is_dir():
            return cand
    return None


def _title(script: Path, tree: Optional[ast.Module]) -> str:
    doc = ast.get_docstring(tree) if tree is not None else None
    if doc:
        return doc.strip().splitlines()[0].strip()
    return re.sub(r"^\d+_", "", script.stem).replace("_", " ").capitalize()


def list_examples(examples: Path, domain: Optional[str] = None) -> list[dict[str, Any]]:
    """Every example script: ``{domain, name, title, script, svg}`` (paths relative to ``examples``)."""
    out = []
    for script in sorted(examples.rglob("*.py")):
        rel = script.relative_to(examples)
        dom = rel.parts[0] if len(rel.parts) > 1 else "root"
        if script.is_symlink() or (domain and dom != domain):
            continue
        try:
            tree = ast.parse(script.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        if not any(isinstance(n, ast.FunctionDef) and n.name == "diagram" for n in tree.body):
            continue
        name = "/".join(rel.parts[1:]) if len(rel.parts) > 1 else rel.name
        svg = script.with_suffix(".svg")
        out.append({"domain": dom, "name": name[:-3], "title": _title(script, tree),
                    "script": str(rel), "svg": str(svg.relative_to(examples)) if svg.exists() else None})
    return out


def domains(examples: Path) -> list[dict[str, Any]]:
    """``{domain, count, titles}`` for every example domain, sorted by name."""
    grouped: dict[str, list[str]] = {}
    for ex in list_examples(examples):
        grouped.setdefault(ex["domain"], []).append(ex["title"])
    return [{"domain": d, "count": len(t), "titles": t} for d, t in sorted(grouped.items())]


def _bare(name: str) -> str:
    return re.sub(r"^\d+_", "", name.rsplit("/", 1)[-1])


def read_example(examples: Path, domain: str, name: str,
                 limit: int = MAX_INLINE_CHARS) -> dict[str, Any]:
    """An example's source and committed SVG. ``LookupError`` if there is no match.

    ``name`` is the file stem (``01_candlestick_chart``); the numeric prefix may be
    left off if that is unambiguous. ``domain`` and ``name`` must be plain names
    (``ValueError`` otherwise), so neither can point outside ``examples``.
    """
    plain_name(domain, "domain")
    plain_name(name.replace("/", "_"), "name")
    items = list_examples(examples, domain)
    if not items:
        raise LookupError(f"no examples in domain {domain!r}")
    name = name.removesuffix(".py")
    hit = [e for e in items if e["name"] == name] or [e for e in items if _bare(e["name"]) == name]
    if len(hit) != 1:
        raise LookupError(f"{'ambiguous' if hit else 'no'} example {name!r} in domain {domain!r}")
    ex = hit[0]
    source = (examples / ex["script"]).read_text(encoding="utf-8")
    out: dict[str, Any] = {"domain": ex["domain"], "name": ex["name"], "title": ex["title"],
                           "script": ex["script"], "source": source[:limit],
                           "source_truncated": len(source) > limit}
    if ex["svg"]:
        svg = (examples / ex["svg"]).read_text(encoding="utf-8")
        out.update(svg=svg[:limit], svg_truncated=len(svg) > limit)
    return out


def resolve_example(examples: Path, ref: str, limit: int = MAX_INLINE_CHARS) -> dict[str, Any]:
    """Like :func:`read_example` for ``DOMAIN/NAME`` or a bare ``NAME`` unique in the gallery."""
    if "/" in ref:
        domain, _, name = ref.partition("/")
        return read_example(examples, domain, name, limit)
    hits = [e for e in list_examples(examples) if e["name"] == ref or _bare(e["name"]) == ref]
    if len(hits) != 1:
        raise LookupError(f"{'ambiguous' if hits else 'no'} example {ref!r}; use DOMAIN/NAME")
    return read_example(examples, hits[0]["domain"], hits[0]["name"], limit)


# --- capability manifest -----------------------------------------------------

def find_capabilities(root: Path) -> Optional[Path]:
    """``root/docs/capabilities.json`` if present, else the one beside a source checkout."""
    for cand in (root / "docs" / "capabilities.json",
                 Path(__file__).resolve().parents[2] / "docs" / "capabilities.json"):
        if cand.is_file():
            return cand
    return None


def capabilities_summary(path: Path, category: Optional[str] = None) -> dict[str, Any]:
    """``{version, total, categories, capabilities:[{id,title,category,status,verification}]}``."""
    data = json.loads(path.read_text(encoding="utf-8"))
    caps = [{"id": c["id"], "title": c.get("name", ""), "category": c.get("category", ""),
             "status": c.get("status", ""), "verification": c.get("verification", "")}
            for c in data.get("capabilities", [])]
    if category:
        caps = [c for c in caps if c["category"].lower() == category.lower()]
    return {"version": data.get("version", ""), "total": len(caps),
            "categories": data.get("summary", {}).get("categories", []), "capabilities": caps}
