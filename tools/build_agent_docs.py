#!/usr/bin/env python3
"""Regenerate the agent-facing documentation from the code, so it cannot drift.

Writes four files:

* ``docs/api-reference.md``  every public name, with signature, docstring and location
* ``docs/llms.txt``         the llmstxt.org index (absolute URLs)
* ``docs/llms-full.txt``    the guide, API, CLI, MCP tools, math markup and examples in one file
* ``examples/index.json``   one record per example script

The CLI section is read from ``cli.build_parser()`` and the MCP section from ``mcp.TOOLS``
when this runs, so a new flag or tool shows up the next time it is regenerated.

    uv run python tools/build_agent_docs.py          # rewrite
    uv run python tools/build_agent_docs.py --check  # exit 1 if a committed file is stale
"""
from __future__ import annotations

import argparse
import ast
import importlib
import inspect
import json
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import diagrams_as_code  # noqa: E402

SITE = "https://bsommers.github.io/diagrams-as-code/"
BLOB = "https://github.com/bsommers/diagrams-as-code/blob/master/"

OUT_API = ROOT / "docs" / "api-reference.md"
OUT_LLMS = ROOT / "docs" / "llms.txt"
OUT_FULL = ROOT / "docs" / "llms-full.txt"
OUT_INDEX = ROOT / "examples" / "index.json"

#: Modules documented beyond ``diagrams_as_code.__all__``.
KIT_MODULES = [
    "diagrams_as_code.plot",
    "diagrams_as_code.draft",
    "diagrams_as_code.sequence",
    "diagrams_as_code.gantt",
    "diagrams_as_code.text.math",
]

#: (file under docs/, one-line description) for the llms.txt "Docs" section.
DOCS = [
    ("for-agents.md", "Start here: choose an interface, quickstart, API cheat sheet, lint loop, pitfalls"),
    ("api-reference.md", "Signature and docstring of every public name, generated from the code"),
    ("user-guide.md", "Task-oriented guide to writing and rendering diagrams"),
    ("how-to.md", "Recipes for layout, routing, themes and output"),
    ("math-markup.md", "The TeX-like math subset accepted between dollar signs in any label"),
    ("sequence-diagrams.md", "UML sequence diagrams: participants, messages, frames"),
    ("gantt-timelines.md", "Gantt charts, critical path and timelines"),
    ("technical-figures.md", "Paper-style technical figures: plots, drafting, solids"),
    ("architecture.md", "Layers, modules and data flow of the engine"),
    ("CAPABILITIES.md", "What the library can and cannot do, with verification commands"),
    ("capabilities.json", "The same capabilities as machine-readable JSON"),
    ("running.md", "Installing and running: uv, Docker, CLI, MCP"),
    ("CHANGELOG.md", "Release history"),
]


def link(path: str) -> str:
    """Absolute URL a repo file is served at (Pages for ``docs/``, GitHub for the rest)."""
    if path.startswith("docs/"):
        return SITE + path[len("docs/"):]
    return BLOB + path


# ----------------------------------------------------------------- examples index
def example_scripts() -> list[Path]:
    """Every example script, in the order the audit and the site use."""
    return sorted(set(ROOT.glob("examples/*/*.py")) | set(ROOT.glob("examples/[0-9]*.py")))


def _call_name(node: ast.Call) -> str | None:
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None


def _flat(value: ast.AST) -> str | None:
    """Text of a string literal or f-string (each expression stands in as ``0``)."""
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value
    if isinstance(value, ast.JoinedStr):
        return "".join(p.value if isinstance(p, ast.Constant) else "0" for p in value.values)
    return None


def _one_line(text: str) -> str:
    return " ".join(text.split())


def _sentence(doc: str | None) -> str:
    if not doc:
        return ""
    first = _one_line(doc.strip().split("\n\n")[0])
    sentence = re.split(r"(?<=[.!?])\s", first, maxsplit=1)[0]
    return sentence if len(sentence) <= 200 else sentence[:197].rstrip() + "..."


def _uses_math(tree: ast.AST) -> bool:
    from diagrams_as_code.text import parse_markup

    for node in ast.walk(tree):
        text = _flat(node) if isinstance(node, (ast.Constant, ast.JoinedStr)) else None
        if text and "$" in text:
            try:
                if any(sp.kind == "math" for line in parse_markup(text) for sp in line):
                    return True
            except Exception:  # not valid markup is not "uses math"
                continue
    return False


def example_record(script: Path) -> dict[str, Any]:
    """The index record for one example script, from its source and sibling files."""
    source = script.read_text(encoding="utf-8")
    tree = ast.parse(source)
    rel = script.relative_to(ROOT)
    domain = rel.parent.name if len(rel.parts) > 2 else None
    stem = script.stem
    number = int(m.group(1)) if (m := re.match(r"(\d+)_", stem)) else None

    calls = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call) and _call_name(n) in
                    {"Diagram", "SequenceDiagram", "GanttChart"}), key=lambda n: (n.lineno, n.col_offset))
    title = theme = None
    for call in calls:
        first = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == "title"), None)
        text = _flat(first) if first is not None else None
        if text:
            title = _one_line(text)
            for kw in call.keywords:
                if kw.arg == "theme" and isinstance(kw.value, ast.Constant):
                    theme = kw.value.value
            break
    doc = ast.get_docstring(tree)
    if not title:
        title = _sentence(doc).rstrip(".") or stem.split("_", 1)[-1].replace("_", " ")

    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
            modules.update(f"{node.module}.{a.name}" for a in node.names)
        elif isinstance(node, ast.Import):
            modules.update(a.name for a in node.names)

    def uses(name: str) -> bool:
        return f"diagrams_as_code.{name}" in modules

    out_stem = stem
    for node in tree.body:
        if (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "OUTPUT_STEM" for t in node.targets)
                and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            out_stem = node.value.value
    base = script.with_name(out_stem)
    # Only committed outputs count. PNG and PDF are gitignored, so whether they exist depends
    # on the machine and would make this file differ between checkouts.
    formats = [fmt for fmt, suffix in (("svg", ".svg"), ("bom", "_README.md"))
               if Path(f"{base}{suffix}").is_file()]
    return {
        "path": rel.as_posix(),
        "domain": domain,
        "number": number,
        "title": title,
        "description": _sentence(doc),
        "theme": theme or "iiot_dark_gold",
        "formats": formats,
        "svg": script.with_name(f"{out_stem}.svg").relative_to(ROOT).as_posix() if "svg" in formats else None,
        "uses_plot": uses("plot"),
        "uses_draft": uses("draft"),
        "uses_sequence": uses("sequence"),
        "uses_gantt": uses("gantt"),
        "uses_math": _uses_math(tree),
    }


def build_index() -> str:
    records = [example_record(s) for s in example_scripts()]
    data = {
        "version": diagrams_as_code.__version__,
        "note": "Generated by tools/build_agent_docs.py. Each script defines diagram() and renders beside itself.",
        "count": len(records),
        "examples": records,
    }
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


# ------------------------------------------------------------------ API reference
class _Raw(str):
    """A string annotation that prints without quotes."""

    __repr__ = str.__str__


def _signature(obj: Any) -> str:
    try:
        sig = inspect.signature(obj)
    except (TypeError, ValueError):
        return "(...)"
    def raw(a: Any) -> Any:
        return _Raw(a) if isinstance(a, str) else a
    params = [p.replace(annotation=raw(p.annotation)) for p in sig.parameters.values()]
    return str(sig.replace(parameters=params, return_annotation=raw(sig.return_annotation)))


def _doc(obj: Any) -> str:
    return inspect.getdoc(obj) or ""


def _home(obj: Any) -> str:
    """Repo-relative source path of the module that defines ``obj``."""
    module = inspect.getmodule(obj)
    file = getattr(module, "__file__", None)
    try:
        return Path(file).resolve().relative_to(ROOT).as_posix() if file else "?"
    except ValueError:
        return "?"


def _public_members(cls: type) -> list[tuple[str, Any]]:
    out = []
    for name, value in vars(cls).items():
        if name.startswith("_") or not (inspect.isfunction(value) or isinstance(value, (property, classmethod, staticmethod))):
            continue
        out.append((name, value))
    return out


def _describe_member(name: str, value: Any) -> str:
    if isinstance(value, property):
        kind, doc, sig = "property", _doc(value.fget), ""
    elif isinstance(value, (classmethod, staticmethod)):
        fn = value.__func__
        kind = "classmethod" if isinstance(value, classmethod) else "staticmethod"
        doc, sig = _doc(fn), _signature(fn)
    else:
        kind, doc, sig = "method", _doc(value), _signature(value)
    first = _one_line(doc.split("\n\n")[0]) if doc else ""
    head = f"- `{name}{sig}`" if sig else f"- `{name}`"
    tag = "" if kind == "method" else f" ({kind})"
    return f"{head}{tag}: {first}" if first else f"{head}{tag}"


def _entry(name: str, obj: Any, module_name: str) -> str:
    where = _home(obj)
    lines = [f"### `{name}`", ""]
    if inspect.isclass(obj):
        if issubclass(obj, Enum):
            lines.append(f"`class {name}(Enum)` members: " + ", ".join(f"`{m}`" for m in obj.__members__))
        else:
            bases = ", ".join(b.__name__ for b in obj.__bases__ if b is not object)
            sig = "" if issubclass(obj, BaseException) and "__init__" not in vars(obj) else _signature(obj)
            lines.append(f"`class {name}{sig}`" + (f" extends `{bases}`" if bases else ""))
    elif inspect.isfunction(obj):
        lines.append(f"`def {name}{_signature(obj)}`")
    else:
        lines.append(f"`{name}`: {type(obj).__name__} constant")
    lines += ["", f"Defined in `{where}`; import with `from {module_name} import {name}`."]
    doc = _doc(obj) if (inspect.isclass(obj) or inspect.isfunction(obj)) else ""
    if not doc and not (inspect.isclass(obj) or inspect.isfunction(obj)):
        doc = f"Value of type `{type(obj).__name__}`."
        if hasattr(obj, "name") and isinstance(getattr(obj, "name"), str):
            doc = f"A built-in theme, `Theme.name` = `{obj.name}`."
    if doc:
        lines += ["", doc]
    if inspect.isclass(obj) and not issubclass(obj, Enum):
        members = _public_members(obj)
        if members:
            lines += ["", "Public members:", ""] + [_describe_member(n, v) for n, v in members]
    return "\n".join(lines)


def _kit_names(mod: Any) -> list[str]:
    declared = getattr(mod, "__all__", None)
    if declared:
        return list(declared)
    return sorted(n for n, v in vars(mod).items()
                  if not n.startswith("_") and (inspect.isclass(v) or inspect.isfunction(v))
                  and getattr(v, "__module__", None) == mod.__name__)


def build_api_reference() -> str:
    out = [
        "# API reference",
        "",
        "Generated by `tools/build_agent_docs.py` from the code and its docstrings; do not edit by hand. "
        "Parameters are in pixels unless a docstring says otherwise. For a task-oriented introduction read "
        "[for-agents.md](for-agents.md).",
        "",
        f"Version {diagrams_as_code.__version__}. Two parts: the top-level package (`from diagrams_as_code import ...`, "
        f"{len(diagrams_as_code.__all__)} names) and the kit modules that are imported by path "
        f"({', '.join('`' + m + '`' for m in KIT_MODULES)}).",
        "",
        "## Top-level package: `diagrams_as_code`",
        "",
    ]
    for name in diagrams_as_code.__all__:
        out += [_entry(name, getattr(diagrams_as_code, name), "diagrams_as_code"), ""]
    for module_name in KIT_MODULES:
        mod = importlib.import_module(module_name)
        out += [f"## Kit module: `{module_name}`", "", f"Source: `{_home(mod)}`.", ""]
        mdoc = _doc(mod)
        if mdoc:
            out += [mdoc, ""]
        for name in _kit_names(mod):
            out += [_entry(name, getattr(mod, name), module_name), ""]
    text = "\n".join(out).rstrip() + "\n"
    if re.search(r"0x[0-9a-f]{6,}", text):
        raise SystemExit("api-reference would contain a memory address (non-deterministic default repr)")
    return text


# ------------------------------------------------------------------- CLI and MCP
def _argument(action: argparse.Action) -> str:
    flags = ", ".join(action.option_strings) if action.option_strings else (action.metavar or action.dest)
    if action.option_strings and action.nargs != 0:
        flags += f" {action.metavar or action.dest.upper()}"
    if action.choices is not None and not action.option_strings:
        flags += f" {{{','.join(map(str, action.choices))}}}"
    notes = []
    if action.option_strings and action.choices is not None:
        notes.append("one of " + ", ".join(map(str, action.choices)))
    if action.required and action.option_strings:
        notes.append("required")
    if not action.option_strings and action.nargs in ("+", "*"):
        notes.append("one or more" if action.nargs == "+" else "zero or more")
    default = action.default
    help_text = (action.help or "").replace("%(default)s", str(default))
    if (default not in (None, argparse.SUPPRESS, False, ()) and action.option_strings
            and not isinstance(default, bool) and "default" not in help_text):
        notes.append(f"default {default}")
    parts = [help_text] if help_text else []
    return f"- `{flags}`" + (": " + "; ".join(parts + notes) if (parts or notes) else "")


def _describe_parser(parser: argparse.ArgumentParser, name: str, depth: int = 0) -> list[str]:
    out = [f"{'#' * (3 + depth)} `{name}`", ""]
    if parser.description:
        out += [_one_line(parser.description), ""]
    subs = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    for action in parser._actions:
        if isinstance(action, (argparse._HelpAction, argparse._SubParsersAction)):
            continue
        out.append(_argument(action))
    if any(not isinstance(a, (argparse._HelpAction, argparse._SubParsersAction)) for a in parser._actions):
        out.append("")
    for sub in subs:
        helps = {ca.dest: ca.help for ca in sub._choices_actions}
        for cmd, subparser in sub.choices.items():
            summary = helps.get(cmd)
            block = _describe_parser(subparser, f"{name} {cmd}", depth + 1)
            if summary and not subparser.description:
                block.insert(2, _one_line(summary) + ".")
                block.insert(3, "")
            out += block
    return out


def build_cli_section() -> str:
    from diagrams_as_code.cli import build_parser

    parser = build_parser()
    body = _describe_parser(parser, "diagrams-as-code")
    contract = (
        "Exit codes: 0 success; 1 a script failed, lint found defects, or no diagram script was found; "
        "2 usage error. Failures print `error: <path>: <message>` on stderr; `render` prints `wrote <path>` on stdout."
    )
    return "\n".join(["## Command-line interface", "", contract, ""] + body).rstrip() + "\n"


def _tool_parts(name: str, entry: Any) -> tuple[str, Any]:
    """``(description, input schema)`` from a ``TOOLS`` entry, whatever shape it has."""
    if isinstance(entry, (tuple, list)):
        return str(entry[0]), entry[1]
    if isinstance(entry, dict):
        return str(entry.get("description", "")), entry.get("inputSchema", entry.get("schema", {}))
    return str(getattr(entry, "description", "")), getattr(entry, "input_schema", getattr(entry, "schema", {}))


def mcp_tools() -> list[tuple[str, str, Any]]:
    from diagrams_as_code.mcp import TOOLS

    return [(name, *_tool_parts(name, entry)) for name, entry in TOOLS.items()]


def build_mcp_section() -> str:
    out = [
        "## MCP server tools",
        "",
        "Start with `diagrams-as-code mcp --root DIR`. JSON-RPC 2.0 over stdio. Script and output paths are "
        "confined to `DIR`; each script runs in a resource-limited child process (no file or network isolation).",
        "",
    ]
    for name, description, schema in mcp_tools():
        out += [f"### `{name}`", "", description, "", "Input schema:", "", "```json",
                json.dumps(schema, indent=2), "```", ""]
    return "\n".join(out).rstrip() + "\n"


# ----------------------------------------------------------- llms.txt / llms-full
def examples_compact(index: dict[str, Any]) -> str:
    out = ["## Examples index (compact)", "",
           "Full records, including description, theme and formats, are in `examples/index.json`. "
           "Format: `path - title [kits used]`.", ""]
    for rec in index["examples"]:
        kits = [k for k in ("plot", "draft", "sequence", "gantt", "math") if rec[f"uses_{k}"]]
        out.append(f"- {rec['path']} - {rec['title']}" + (f" [{', '.join(kits)}]" if kits else ""))
    return "\n".join(out) + "\n"


def build_llms(index: dict[str, Any]) -> str:
    domains = sorted({r["domain"] for r in index["examples"] if r["domain"]})
    lines = [
        "# diagrams-as-code",
        "",
        "> Pure-Python diagrams as code: describe a diagram in a script, get deterministic SVG, PNG, PDF and a "
        "bill of materials with zero runtime dependencies. Drive it from the Python API, the `diagrams-as-code` "
        "CLI or an MCP server; a visual linter finds overlaps, clipped labels and lines through nodes.",
        "",
        f"Version {diagrams_as_code.__version__}. Requires Python 3.10+; install with `uv sync`. "
        f"{index['count']} example scripts across {len(domains)} domains. The API is "
        "`d = Diagram(title)`, `d.shape(label)` or `d.add(Shape(id, label))`, and `a >> d.edge(label) >> b`; "
        "there is no `add_node` or `add_edge`.",
        "",
        "## Start here",
        "",
        f"- [Using diagrams-as-code from an AI agent]({link('docs/for-agents.md')}): interfaces, verified quickstart, "
        "cheat sheet, lint loop, pitfalls",
        f"- [llms-full.txt]({link('docs/llms-full.txt')}): this documentation in one file (guide, API, CLI, MCP tools, "
        "math markup, examples)",
        "",
        "## Docs",
        "",
    ]
    for name, text in DOCS:
        lines.append(f"- [{name}]({link('docs/' + name)}): {text}")
    lines += [
        "",
        "## Machine-readable",
        "",
        f"- [examples/index.json]({link('examples/index.json')}): one record per example script "
        "(path, domain, title, description, theme, formats, kits used)",
        f"- [docs/capabilities.json]({link('docs/capabilities.json')}): capabilities with their Python API and tests",
        "",
        "## Source",
        "",
        f"- [src/diagrams_as_code/__init__.py]({link('src/diagrams_as_code/__init__.py')}): the public names (`__all__`)",
        f"- [src/diagrams_as_code/diagram.py]({link('src/diagrams_as_code/diagram.py')}): `Diagram`",
        f"- [src/diagrams_as_code/cli.py]({link('src/diagrams_as_code/cli.py')}): the command-line interface",
        f"- [src/diagrams_as_code/mcp.py]({link('src/diagrams_as_code/mcp.py')}): the MCP server and its tool table",
        f"- [AGENTS.md]({link('AGENTS.md')}): rules for contributing and for using the library as an agent",
        "",
        "## Optional",
        "",
        f"- [README.md]({link('README.md')}): overview and gallery",
        f"- [CONTRIBUTING.md]({link('CONTRIBUTING.md')}): how to contribute",
        f"- [Landing page]({SITE}): the gallery as a website",
    ]
    return "\n".join(lines) + "\n"


def build_llms_full(index: dict[str, Any], api: str) -> str:
    def read(name: str) -> str:
        return (ROOT / "docs" / name).read_text(encoding="utf-8").rstrip() + "\n"

    parts = [
        "# diagrams-as-code: full documentation for agents",
        "",
        f"> Everything an AI agent or program needs in one file. Version {diagrams_as_code.__version__}. "
        f"Index: {link('docs/llms.txt')}",
        "",
        "Sections: 1 guide for agents; 2 API reference; 3 command-line interface; 4 MCP tools; "
        "5 math markup reference; 6 examples index.",
        "",
        "---",
        "",
        read("for-agents.md"),
        "---",
        "",
        api.rstrip() + "\n",
        "---",
        "",
        build_cli_section(),
        "---",
        "",
        build_mcp_section(),
        "---",
        "",
        read("math-markup.md"),
        "---",
        "",
        examples_compact(index),
    ]
    return "\n".join(parts)


def build() -> dict[Path, str]:
    """Every generated file and its content."""
    index_text = build_index()
    index = json.loads(index_text)
    api = build_api_reference()
    return {
        OUT_INDEX: index_text,
        OUT_API: api,
        OUT_LLMS: build_llms(index),
        OUT_FULL: build_llms_full(index, api),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if a committed file is stale")
    args = parser.parse_args(argv)
    files = build()
    if args.check:
        stale = [p.relative_to(ROOT).as_posix() for p, text in files.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print("stale: " + ", ".join(stale) + " - run tools/build_agent_docs.py")
            return 1
        print(f"agent docs up to date ({len(files)} files)")
        return 0
    for path, text in files.items():
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
