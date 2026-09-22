"""Command-line interface: ``diagrams-as-code render|layout export|themes|icons``."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import sys
import traceback
from pathlib import Path
from typing import Optional

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
    render.add_argument("--out", type=Path, default=Path("output"))
    render.add_argument("--format", type=_formats, default=_formats(DEFAULT_FORMATS))
    render.add_argument("--theme", choices=list_themes())
    _add_layout_flags(render)

    layout = sub.add_parser("layout", help="layout file tools")
    layout_sub = layout.add_subparsers(dest="layout_command", required=True, parser_class=_Parser)
    export = layout_sub.add_parser("export", help="write a script's positions to a layout file")
    export.add_argument("script", type=Path)
    export.add_argument("-o", "--output", type=Path)
    _add_layout_flags(export)

    sub.add_parser("themes", help="list built-in themes")
    icons = sub.add_parser("icons", help="list built-in icons")
    icons.add_argument("--domain")
    return parser


def _defines_diagram(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return False
    return any(isinstance(n, ast.FunctionDef) and n.name == "diagram" for n in tree.body)


def discover(paths: list[Path]) -> list[tuple[Path, Path]]:
    """Scripts to render, each with its output subdirectory."""
    found: list[tuple[Path, Path]] = []
    for path in paths:
        if path.is_dir():
            for script in sorted(path.rglob("*.py")):
                if _defines_diagram(script):
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
    spec.loader.exec_module(module)
    build = getattr(module, "diagram", None)
    if not callable(build):
        raise ValueError("defines no diagram() function")
    diag = build()
    if not isinstance(diag, Diagram):
        raise ValueError(f"diagram() returned {type(diag).__name__}, not Diagram")
    return diag, str(getattr(module, "OUTPUT_STEM", path.stem))


def _configure(diag: Diagram, args: argparse.Namespace, theme: Optional[str] = None) -> None:
    diag.configure(layout=args.layout, direction=args.direction, layout_file=args.layout_file, theme=theme)


def _report(path: Path, exc: Exception, debug: bool) -> None:
    if debug:
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
    print(f"error: {path}: {exc}", file=sys.stderr)


def _render(args: argparse.Namespace) -> int:
    status = 0
    for script, subdir in discover(args.paths):
        try:
            diag, stem = load_script(script)
            _configure(diag, args, theme=args.theme)
            for written in render_all(diag, args.out / subdir, stem, args.format).values():
                print(f"wrote {written}")
        except Exception as exc:  # report and continue with the next script
            _report(script, exc, args.debug)
            status = 1
    return status


def _layout_export(args: argparse.Namespace) -> int:
    try:
        diag, _stem = load_script(args.script)
        _configure(diag, args)
        target = args.output or args.script.with_suffix(".layout.json")
        print(f"wrote {export_layout(diag, target)}")
        return 0
    except Exception as exc:
        _report(args.script, exc, args.debug)
        return 1


def _icons(domain: Optional[str]) -> int:
    for name, (icon_domain, description) in sorted(ShapeLibrary._ICON_CATALOG.items()):
        if domain is None or icon_domain == domain:
            print(f"{name}\t{icon_domain}\t{description}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Run the CLI; returns the process exit code."""
    try:
        args = build_parser().parse_args(argv)
    except _UsageError:
        return 2
    except SystemExit as exc:  # --help
        return int(exc.code or 0)
    if args.command == "render":
        return _render(args)
    if args.command == "layout":
        return _layout_export(args)
    if args.command == "themes":
        print("\n".join(list_themes()))
        return 0
    return _icons(args.domain)
