"""Command-line interface.

``diagrams-as-code render|lint|layout export|mcp|themes|icons|api|examples|source``.

Exit codes: 0 success; 1 findings or failures (a script failed, lint found a defect,
a named example does not exist); 2 usage error. With ``--json`` (``render``, ``lint``,
``themes``, ``icons``, ``api``, ``examples``) stdout is exactly one JSON document and
nothing else; diagnostics always go to stderr.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import importlib.util
import json
import sys
import traceback
import warnings
from pathlib import Path
from typing import Optional, TextIO

from diagrams_as_code import agent_api
from diagrams_as_code.audit import DEFECTS, audit_findings
from diagrams_as_code.diagram import Diagram
from diagrams_as_code.layout.layered import DIRECTIONS
from diagrams_as_code.layout.sidecar import export_layout
from diagrams_as_code.output import FORMATS, render_all
from diagrams_as_code.shapes import ShapeLibrary
from diagrams_as_code.theme import list_themes

DEFAULT_FORMATS = "svg,bom"


class _Parser(argparse.ArgumentParser):
    """ArgumentParser that raises instead of exiting, so main() returns 2."""

    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise _UsageError


class _UsageError(Exception):
    pass


def _formats(value: str) -> tuple[str, ...]:
    chosen = tuple(v.strip() for v in value.split(",") if v.strip())
    unknown = sorted(set(chosen) - set(FORMATS))
    if unknown or not chosen:
        raise argparse.ArgumentTypeError(f"choose from {','.join(FORMATS)}; got {value!r}")
    return chosen


def _defects(value: str) -> tuple[str, ...]:
    chosen = tuple(v.strip() for v in value.split(",") if v.strip())
    unknown = sorted(set(chosen) - set(DEFECTS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown defect kind {', '.join(unknown)}")
    return chosen


def _add_json_flag(p: argparse.ArgumentParser) -> None:
    p.add_argument("--json", action="store_true",
                   help="print one JSON document on stdout and nothing else (diagnostics on stderr)")


_STDOUT: Optional[TextIO] = None  # the real stdout, while a script may be printing to stderr instead


def _emit(doc: object) -> None:
    print(json.dumps(doc, indent=2), file=_STDOUT or sys.stdout)


def _add_layout_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--layout", choices=Diagram.LAYOUT_MODES)
    p.add_argument("--direction", choices=DIRECTIONS)
    p.add_argument("--layout-file", type=Path)
    p.add_argument("--debug", action="store_true", help="show tracebacks")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="diagrams-as-code", description="Render diagrams-as-code scripts.")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)

    render = sub.add_parser("render", help="render scripts or directories of scripts")
    render.add_argument("paths", nargs="+", type=Path, metavar="PATH")
    render.add_argument(
        "--out", type=Path, default=None,
        help="output directory (default: beside each script)",
    )
    render.add_argument(
        "--format",
        type=_formats,
        default=_formats(DEFAULT_FORMATS),
        help=f"comma-separated list from {','.join(FORMATS)} (default: {DEFAULT_FORMATS})",
    )
    render.add_argument("--theme", choices=list_themes())
    render.add_argument(
        "--interactive",
        dest="interactive",
        action="store_true",
        default=None,
        help="emit interactive pan/zoom-enabled SVG output",
    )
    render.add_argument(
        "--no-interactive",
        dest="interactive",
        action="store_false",
        help="disable interactive SVG output",
    )
    _add_layout_flags(render)
    _add_json_flag(render)

    lint = sub.add_parser(
        "lint",
        help="report visual defects in scripts or directories of scripts",
        description="Lay out each diagram and report what a reader would see as a defect: "
        "a line through a node, labels on top of each other, text spilling out of its box. "
        "Exits 1 if anything is found.",
    )
    lint.add_argument("paths", nargs="+", type=Path, metavar="PATH")
    lint.add_argument(
        "--ignore", type=_defects, default=(), metavar="KIND[,KIND]",
        help="defect kinds not to report; choose from " + ", ".join(DEFECTS),
    )
    lint.add_argument("--quiet", action="store_true", help="print findings only, no summary")
    _add_layout_flags(lint)
    _add_json_flag(lint)

    layout = sub.add_parser("layout", help="layout file tools")
    layout_sub = layout.add_subparsers(dest="layout_command", required=True, parser_class=_Parser)
    export = layout_sub.add_parser("export", help="write a script's positions to a layout file")
    export.add_argument("script", type=Path)
    export.add_argument("-o", "--output", type=Path)
    _add_layout_flags(export)

    mcp = sub.add_parser("mcp", help="serve render/lint/list tools over MCP (stdio)")
    mcp.add_argument("--root", type=Path, default=Path("."),
                     help="directory scripts and outputs are confined to (default: .)")
    mcp.add_argument("--timeout", type=float, default=60.0, metavar="SECONDS",
                     help="wall-clock limit for one script (default: 60)")
    mcp.add_argument("--memory-mb", type=int, default=2048, metavar="MB",
                     help="memory limit for one script, POSIX (default: 2048)")

    _add_json_flag(sub.add_parser("themes", help="list built-in themes"))
    icons = sub.add_parser("icons", help="list built-in icons")
    icons.add_argument("--domain")
    _add_json_flag(icons)

    api = sub.add_parser(
        "api", help="reference of the public Python API (names, signatures, summaries)",
        description="List every name in diagrams_as_code.__all__ and the plot, draft, sequence "
        "and gantt kits with kind, signature and a one-line summary. NAME narrows it "
        "(a class, function, kit module or substring); a class also lists its methods. "
        "Exits 1 if NAME matches nothing.")
    api.add_argument("name", nargs="?", metavar="NAME")
    _add_json_flag(api)

    examples = sub.add_parser(
        "examples", help="list the example gallery, or its domains",
        description="List example scripts as DOMAIN/NAME with a title. Without --domain, "
        "list domains with their counts instead.")
    examples.add_argument("--domain", help="only this domain (e.g. finance, cad)")
    examples.add_argument("--dir", type=Path, default=None,
                          help="examples directory (default: ./examples, else the checkout's)")
    _add_json_flag(examples)

    source = sub.add_parser(
        "source", help="print an example's script",
        description="Print the script of an example, DOMAIN/NAME (the numeric prefix of NAME "
        "is optional) or a NAME unique in the gallery. Exits 1 if there is no such example.")
    source.add_argument("example", metavar="EXAMPLE")
    source.add_argument("--dir", type=Path, default=None,
                        help="examples directory (default: ./examples, else the checkout's)")
    return parser


def _scan(path: Path) -> tuple[bool, Optional[Exception]]:
    """``(has_diagram, error)`` for a candidate script found while scanning a directory.

    ``error`` is set when the file could not even be parsed, as distinct from a file
    that parses cleanly but simply defines no ``diagram()`` (a helper module).
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return False, exc
    has_diagram = any(isinstance(n, ast.FunctionDef) and n.name == "diagram" for n in tree.body)
    return has_diagram, None


def discover(
    paths: list[Path], errors: Optional[list[tuple[Path, Exception]]] = None
) -> list[tuple[Path, Path]]:
    """Scripts to render, each with its output subdirectory.

    A directly named path is always included, unchecked (a syntax error there
    surfaces through the normal load path). When scanning a directory, a ``*.py``
    file that cannot be parsed is appended to ``errors`` as ``(path, exception)``
    instead of being silently dropped; a file that parses but defines no
    ``diagram()`` is skipped without error, since that's how helper modules are
    excluded.
    """
    found: list[tuple[Path, Path]] = []
    for path in paths:
        if path.is_dir():
            for script in sorted(path.rglob("*.py")):
                has_diagram, exc = _scan(script)
                if exc is not None:
                    if errors is not None:
                        errors.append((script, exc))
                    continue
                if has_diagram:
                    found.append((script, script.parent.relative_to(path)))
        else:
            found.append((path, Path(".")))
    return found


_loaded = 0


def load_script(path: Path) -> tuple[Diagram, str]:
    """Run a script and return ``(diagram(), output stem)``."""
    global _loaded
    _loaded += 1
    spec = importlib.util.spec_from_file_location(f"_dac_script_{_loaded}_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot be loaded as a Python module")
    module = importlib.util.module_from_spec(spec)
    # Let the script import helper modules that sit beside it.
    script_dir = str(path.resolve().parent)
    sys.path.insert(0, script_dir)
    try:
        try:
            spec.loader.exec_module(module)
            build = getattr(module, "diagram", None)
            if not callable(build):
                raise ValueError("defines no diagram() function")
            diag = build()
        except SystemExit as exc:
            raise RuntimeError(f"script called sys.exit({exc.code!r}) while loading") from exc
    finally:
        try:
            sys.path.remove(script_dir)
        except ValueError:
            pass
    if not isinstance(diag, Diagram):
        raise ValueError(f"diagram() returned {type(diag).__name__}, not Diagram")
    return diag, str(getattr(module, "OUTPUT_STEM", path.stem))


def _configure(diag: Diagram, args: argparse.Namespace, theme: Optional[str] = None) -> None:
    diag.configure(
        layout=args.layout,
        direction=args.direction,
        layout_file=args.layout_file,
        theme=theme,
        interactive=getattr(args, "interactive", None),
    )


def _report(path: Path, exc: Exception, debug: bool) -> None:
    if debug:
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
    print(f"error: {path}: {exc}", file=sys.stderr)


def _failure(path: Path, exc: Exception, code: str = "script_error") -> dict:
    """The ``--json`` record of a script that could not be loaded or run."""
    return {"file": str(path), **agent_api.error_dict(code, str(exc), agent_api.script_line(exc, path))}


def _missing_layout_file(args: argparse.Namespace) -> bool:
    """Report a ``--layout-file`` that was named but does not exist."""
    layout_file = getattr(args, "layout_file", None)
    if layout_file is not None and not Path(layout_file).is_file():
        print(f"error: --layout-file: {layout_file} does not exist", file=sys.stderr)
        return True
    return False


def _render(args: argparse.Namespace) -> int:
    if args.out is not None and args.out.is_file():
        print(f"error: --out: {args.out} is an existing file, not a directory", file=sys.stderr)
        return 2
    if _missing_layout_file(args):
        return 2
    status = 0
    written_json: list[dict] = []
    failed_json: list[dict] = []
    errors: list[tuple[Path, Exception]] = []
    scripts = discover(args.paths, errors)
    for script, exc in errors:
        _report(script, exc, args.debug)
        failed_json.append(_failure(script, exc))
        status = 1
    if not scripts and not errors:
        listed = ", ".join(str(p) for p in args.paths)
        print(f"error: no diagram scripts found in {listed}", file=sys.stderr)
        if args.json:
            _emit({"written": [], "failed": [{"file": listed, **agent_api.error_dict(
                "no_scripts", f"no diagram scripts found in {listed}")}]})
        return 1
    written_by: dict[Path, Path] = {}
    for script, subdir in scripts:
        try:
            diag, stem = load_script(script)
            out_dir = script.parent if args.out is None else args.out / subdir
            target = out_dir / stem
            if target in written_by:
                raise ValueError(
                    f"output {target}.* was already written by {written_by[target]}; "
                    "rename one script or set OUTPUT_STEM"
                )
            written_by[target] = script
            _configure(diag, args, theme=args.theme)
            for fmt, written in render_all(diag, out_dir, stem, args.format).items():
                if args.json:
                    written_json.append({"script": str(script), "format": fmt, "file": str(written)})
                else:
                    print(f"wrote {written}")
        except Exception as exc:  # report and continue with the next script
            _report(script, exc, args.debug)
            failed_json.append(_failure(script, exc))
            status = 1
    if args.json:
        _emit({"written": written_json, "failed": failed_json})
    return status


def _lint(args: argparse.Namespace) -> int:
    """Report visual defects; 0 if clean, 1 if any were found or a script failed."""
    if _missing_layout_file(args):
        return 2
    errors: list[tuple[Path, Exception]] = []
    scripts = discover(args.paths, errors)
    failed = len(errors)
    failed_json = [_failure(script, exc) for script, exc in errors]
    findings_out: list[dict] = []
    for script, exc in errors:
        _report(script, exc, args.debug)
    if not scripts and not errors:
        listed = ", ".join(str(p) for p in args.paths)
        print(f"error: no diagram scripts found in {listed}", file=sys.stderr)
        if args.json:
            _emit({"checked": 0, "findings": [], "failed": [{"file": listed, **agent_api.error_dict(
                "no_scripts", f"no diagram scripts found in {listed}")}]})
        return 1
    total = 0
    for script, _subdir in scripts:
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                diag, _stem = load_script(script)
                _configure(diag, args)
                findings = [f for f in audit_findings(diag) if f.kind not in args.ignore]
        except Exception as exc:
            _report(script, exc, args.debug)
            failed_json.append(_failure(script, exc))
            failed += 1
            continue
        if args.json:
            findings_out += [{"file": str(script), **f}
                             for f in agent_api.findings_json(findings, [w.message for w in caught])]
        else:
            for finding in findings:
                print(f"{script}: {finding}")
            for warning in caught:
                print(f"{script}: layout_warning: {warning.message}")
        total += len(findings) + len(caught)
    if args.json:
        _emit({"checked": len(scripts) - (failed - len(errors)), "findings": findings_out,
               "failed": failed_json})
    elif not args.quiet:
        checked = len(scripts) - (failed - len(errors))
        print(f"{checked} diagram{'s' if checked != 1 else ''} checked, "
              f"{total} finding{'s' if total != 1 else ''}")
    return 1 if (total or failed) else 0


def _layout_export(args: argparse.Namespace) -> int:
    if _missing_layout_file(args):
        return 2
    target = args.output or args.script.with_suffix(".layout.json")
    if Path(target).is_dir():
        print(f"error: --output: {target} is a directory, not a file", file=sys.stderr)
        return 2
    try:
        diag, _stem = load_script(args.script)
        _configure(diag, args)
        print(f"wrote {export_layout(diag, target)}")
        return 0
    except Exception as exc:
        _report(args.script, exc, args.debug)
        return 1


def _icons(domain: Optional[str], as_json: bool = False) -> int:
    rows = [(name, icon_domain, description)
            for name, (icon_domain, description) in sorted(ShapeLibrary._ICON_CATALOG.items())
            if domain is None or icon_domain == domain]
    if as_json:
        _emit({"icons": [{"name": n, "domain": d, "description": t} for n, d, t in rows]})
    else:
        for row in rows:
            print("\t".join(row))
    return 0


def _api(args: argparse.Namespace) -> int:
    ref = agent_api.api_reference(args.name)
    if args.json:
        _emit(ref)
    elif ref["entries"]:
        print(agent_api.format_api(ref))
    if not ref["entries"]:
        print(f"error: no public API name matches {args.name!r}", file=sys.stderr)
        return 1
    return 0


def _examples_dir(args: argparse.Namespace) -> Optional[Path]:
    found = args.dir if args.dir is not None else agent_api.find_examples_dir(Path("."))
    if found is None or not found.is_dir():
        print("error: no examples directory found; pass --dir", file=sys.stderr)
        return None
    return found


def _examples(args: argparse.Namespace) -> int:
    base = _examples_dir(args)
    if base is None:
        return 1
    if args.domain:
        items = agent_api.list_examples(base, args.domain)
        if args.json:
            _emit({"domain": args.domain, "count": len(items), "examples": items})
        else:
            for ex in items:
                print(f"{ex['domain']}/{ex['name']}\t{ex['title']}")
        if not items:
            print(f"error: no examples in domain {args.domain!r}", file=sys.stderr)
        return 0 if items else 1
    doms = agent_api.domains(base)
    if args.json:
        _emit({"total": sum(d["count"] for d in doms), "domains": doms})
    else:
        for d in doms:
            print(f"{d['domain']}\t{d['count']}")
    return 0


def _source(args: argparse.Namespace) -> int:
    base = _examples_dir(args)
    if base is None:
        return 1
    try:
        found = agent_api.resolve_example(base, args.example, 10**9)
    except (LookupError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(found["source"])
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Run the CLI; returns the process exit code."""
    try:
        args = build_parser().parse_args(argv)
    except _UsageError:
        return 2
    except SystemExit as exc:  # --help
        return int(exc.code or 0)
    if args.command in ("render", "lint"):
        global _STDOUT
        _STDOUT = sys.stdout
        # A script may print while it loads: under --json that must not reach stdout.
        quiet = contextlib.redirect_stdout(sys.stderr) if args.json else contextlib.nullcontext()
        try:
            with quiet:
                return _render(args) if args.command == "render" else _lint(args)
        finally:
            _STDOUT = None
    if args.command == "layout":
        return _layout_export(args)
    if args.command == "mcp":
        from diagrams_as_code.mcp import serve  # late: mcp imports this module

        return serve(args.root, timeout=args.timeout, memory_mb=args.memory_mb)
    if args.command == "themes":
        if args.json:
            _emit({"themes": list(list_themes())})
        else:
            print("\n".join(list_themes()))
        return 0
    if args.command == "api":
        return _api(args)
    if args.command == "examples":
        return _examples(args)
    if args.command == "source":
        return _source(args)
    return _icons(args.domain, args.json)
