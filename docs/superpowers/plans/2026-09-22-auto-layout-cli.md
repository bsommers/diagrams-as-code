# Auto-Layout, CLI, and Modularity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic layered auto-layout (mixable with manual placement and an editable JSON layout file), a `diagrams-as-code` CLI, and enforced module boundaries, without changing a single byte of existing rendered output.

**Architecture:** A new `diagrams_as_code/layout/` package holds a pure `LayeredLayout` engine, a graph builder, a layout-file module, and the solve pipeline that `Diagram.solve()` delegates to. Auto-layout and layout-file positions are expressed as tagged absolute constraints fed to the existing `ConstraintSolver`, so the solver itself does not change. Scripts gain a `diagram() -> Diagram` build function; a shared `output.render_all` writes files for both the examples and the CLI.

**Tech Stack:** Python 3.10+ standard library only (`argparse`, `ast`, `heapq`, `json`, `importlib`, `dataclasses`), pytest, `uv`.

**Spec:** `docs/superpowers/specs/2026-09-21-auto-layout-cli-design.md`

## Global Constraints

- **Always `uv`:** `uv run pytest`, `uv run python …`. Never bare `pip`/`python`/`pytest`.
- **Zero runtime dependencies:** `dependencies = []` in `pyproject.toml` stays empty.
- **Byte-identical output:** after every task, `uv run pytest -q` passes **and** `git status --porcelain -- output/ icons/ README.md docs/` shows no modified tracked files (the suite re-renders all diagrams in place; CI runs `git diff --exit-code` on these paths). Task 12 is the only task that adds files under `output/`, and it modifies none.
- `Diagram(layout=...)` defaults to `"manual"`; default ids `shape_N` / `group_N` are unchanged.
- `build_diagram(output_dir)` keeps its signature and return value in every example.
- Python 3.10 compatible syntax (no `match` on types needing 3.11, no `Self`, no PEP 695 generics).
- Commit messages end with `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- Match surrounding style: `from __future__ import annotations`, type hints, one-line docstrings on public functions.

## Decisions made while planning (not in the spec)

- The CLI's default `--format` is `svg,bom`. PNG needs an optional rasterizer (`resvg-py` is a dev dependency only), so a default that includes PNG would fail on a plain install. `--format svg,png,bom` reproduces today's gallery.
- The current `elements.py → diagram.py` function-level import (to find the active diagram) is replaced by a bottom-layer `context.py` module. The remaining function-level `elements → connections` import (a diagram-less `a >> b` builds a bare `Edge`) is allowlisted in the boundary test with that reason.
- A group counts as pinned if it has its own user constraint **or** any descendant has a user *absolute* constraint (`.at` / `.move_to`), because moving such a group would move the absolutely placed descendant.
- `ConstraintSolver.solve(strict=False)` resolves what it can and does not raise; the pipeline uses it only to estimate a group's size during auto-placement. The final global solve stays strict.
- Re-solving is made idempotent by restoring every element's pre-first-solve bounds and the base canvas size at the start of each pipeline run (first run: record only, so output is unchanged).
- `Diagram.render_png` now always returns the PNG bytes; with CairoSVG it previously returned `None`.
- From `docs/reviews/2026-09-22-architecture-boundaries.md`: label-below metrics move to `metrics.py` (Task 7), and edge routes are computed by the layout pipeline and handed to the renderer (new Task 9). Typed constraints are deferred.

## File Structure

| Path | Responsibility |
|---|---|
| `src/diagrams_as_code/context.py` (new) | Stack of diagrams whose `with` block is open |
| `src/diagrams_as_code/rasterize.py` (new) | Ordered PNG backends; `svg_to_png(svg, path)` |
| `src/diagrams_as_code/icon_glyphs.py` (new, generated once) | `GLYPHS: dict[str, GlyphFn]` icon bodies |
| `src/diagrams_as_code/metrics.py` (new) | Label metrics shared by layout and renderer |
| `src/diagrams_as_code/output.py` (new) | `render_all(diagram, out_dir, stem, formats, readme_name)` |
| `src/diagrams_as_code/layout/__init__.py` (new) | Public layout API |
| `src/diagrams_as_code/layout/base.py` (new) | `LayoutNode`, `LayoutEdge`, `LayoutGraph`, `LayoutEngine`, `LayoutWarning`, `SOURCE_KEY` |
| `src/diagrams_as_code/layout/layered.py` (new) | `LayeredLayout` engine (pure) |
| `src/diagrams_as_code/layout/graph.py` (new) | Scope children, edge lifting, pinned detection, `build_scope_graph` |
| `src/diagrams_as_code/layout/sidecar.py` (new) | Layout-file keys, load, apply, export |
| `src/diagrams_as_code/layout/pipeline.py` (new) | `run_layout(diagram)`: the ordered solve pipeline, including edge routing |
| `src/diagrams_as_code/cli.py`, `__main__.py` (new) | `argparse` CLI |
| `src/diagrams_as_code/diagram.py` | Uses context, rasterize, pipeline; gains layout options, `configure`, `all_elements` |
| `src/diagrams_as_code/elements.py` | Uses context; `explicit_id` attribute |
| `src/diagrams_as_code/shapes.py` | Dispatches icons through `GLYPHS` |
| `src/diagrams_as_code/constraints.py` | `all_elements()` public, `solve(strict=True)` |
| `src/diagrams_as_code/geometry.py` | `Rect.intersects` |
| `examples/**/*.py`, `main.py` | `diagram()` + `render_all` |
| `tests/test_module_boundaries.py`, `test_rasterize.py`, `test_icon_glyphs.py`, `test_output.py`, `test_layout_layered.py`, `test_layout_graph.py`, `test_layout_pipeline.py`, `test_layout_routes.py`, `test_layout_sidecar.py`, `test_cli.py` (new) | See tasks |

---

### Task 1: Active-diagram context module and module-boundary test

**Files:**
- Create: `src/diagrams_as_code/context.py`
- Create: `tests/test_module_boundaries.py`
- Modify: `src/diagrams_as_code/elements.py` (`_find_diagram`, lines 44-52)
- Modify: `src/diagrams_as_code/diagram.py` (`Diagram._active_stack`, `get_current`, `__enter__`, `__exit__`, lines 227-288)

**Interfaces:**
- Produces: `context.push(diagram) -> None`, `context.pop(diagram) -> None`, `context.current() -> Any | None`. `Diagram._active_stack` remains, and is the same list object as `context._ACTIVE`.
- Produces: `tests/test_module_boundaries.py::LAYERS` — every later task that adds a module adds its layer here.

- [ ] **Step 1: Write the failing boundary test**

`tests/test_module_boundaries.py`:

```python
"""Import direction inside ``diagrams_as_code``.

A module may import only modules on a strictly lower layer, or modules of
its own package (``layout`` imports ``layout``). Function-level imports
count: they are how the old ``elements -> diagram`` cycle hid. Imports under
``if TYPE_CHECKING:`` do not, because they never run.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parent.parent / "src" / "diagrams_as_code"

#: Lower number = lower layer. A new module must be classified here.
LAYERS: dict[str, int] = {
    "geometry": 0,
    "theme": 0,
    "context": 0,
    "icon_glyphs": 0,
    "rasterize": 0,
    "metrics": 0,
    "shapes": 1,
    "elements": 1,
    "connections": 2,
    "groups": 2,
    "constraints": 3,
    "router": 3,
    "renderer_svg": 4,
    "bom": 4,
    "layout": 4,
    "diagram": 5,
    "output": 6,
    "cli": 7,
    "__main__": 8,
    "__init__": 8,
}

#: Upward imports that are known and justified. Shrink it; do not grow it.
ALLOWED_UPWARD: dict[tuple[str, str], str] = {
    ("elements", "connections"): "a diagram-less `a >> b` builds a bare Edge",
}


def _unit(path: Path) -> str:
    rel = path.relative_to(PKG)
    return rel.parts[0] if len(rel.parts) > 1 else rel.stem


def _is_type_checking(node: ast.If) -> bool:
    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _imported_units(tree: ast.AST, own_unit: str) -> set[str]:
    found: set[str] = set()

    def visit(node: ast.AST) -> None:
        if isinstance(node, ast.If) and _is_type_checking(node):
            for child in node.orelse:
                visit(child)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == "diagrams_as_code" and len(parts) > 1:
                    found.add(parts[1])
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                found.add(own_unit)
            elif node.module == "diagrams_as_code":
                found.update(alias.name for alias in node.names)
            elif node.module and node.module.startswith("diagrams_as_code."):
                found.add(node.module.split(".")[1])
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return found


SOURCES = sorted(PKG.rglob("*.py"))


def test_every_module_is_classified() -> None:
    missing = sorted({_unit(p) for p in SOURCES} - set(LAYERS))
    assert not missing, f"add these modules to LAYERS: {missing}"


@pytest.mark.parametrize("path", SOURCES, ids=lambda p: str(p.relative_to(PKG)))
def test_imports_point_down(path: Path) -> None:
    unit = _unit(path)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    bad = []
    for target in sorted(_imported_units(tree, unit)):
        if target == unit or target not in LAYERS:
            continue
        if LAYERS[target] >= LAYERS[unit] and (unit, target) not in ALLOWED_UPWARD:
            bad.append(target)
    assert not bad, f"{unit} (layer {LAYERS.get(unit)}) imports higher/equal layers: {bad}"
```

Note: `from diagrams_as_code import X` where `X` is a class (e.g. `Diagram` in `__init__`) resolves to a name not in `LAYERS` and is skipped; only module names are checked.

- [ ] **Step 2: Run it to see the cycle fail**

Run: `uv run pytest tests/test_module_boundaries.py -q`
Expected: FAIL — `test_every_module_is_classified` lists `context` is absent only after Step 3; right now `test_imports_point_down[elements.py]` fails with `elements (layer 1) imports higher/equal layers: ['diagram']`.

- [ ] **Step 3: Create `context.py`**

```python
"""Stack of diagrams whose ``with`` block is currently open.

Elements look up the active diagram here instead of importing ``diagram``,
which sits above them.
"""
from __future__ import annotations

from typing import Any, Optional

_ACTIVE: list[Any] = []


def push(diagram: Any) -> None:
    """Make ``diagram`` the innermost active diagram."""
    _ACTIVE.append(diagram)


def pop(diagram: Any) -> None:
    """Remove ``diagram`` if it is the innermost active diagram."""
    if _ACTIVE and _ACTIVE[-1] is diagram:
        _ACTIVE.pop()


def current() -> Optional[Any]:
    """Return the innermost active diagram, or ``None``."""
    return _ACTIVE[-1] if _ACTIVE else None
```

- [ ] **Step 4: Use it from `elements.py`**

Add `from diagrams_as_code import context` after the `geometry` import, and replace the body of `_find_diagram`'s fallback:

```python
    def _find_diagram(self, other: Any = None) -> Optional[Any]:
        """Find the active Diagram instance for this element."""
        if self._diagram is not None:
            return self._diagram
        if other is not None and getattr(other, "_diagram", None) is not None:
            return other._diagram
        return context.current()
```

- [ ] **Step 5: Use it from `diagram.py`**

Add `from diagrams_as_code import context` to the imports. Replace the stack handling:

```python
class Diagram:
    """Fluent context manager and container for directed diagrams."""

    _active_stack: list[Diagram] = context._ACTIVE

    @classmethod
    def get_current(cls) -> Optional[Diagram]:
        """Get the innermost active Diagram from the context stack."""
        return context.current()
```

```python
    def __enter__(self) -> Diagram:
        context.push(self)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        context.pop(self)
        if exc_type is None:
            self.solve()
```

- [ ] **Step 6: Run the full suite and the output guard**

Run: `uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/`
Expected: all pass; the `git status` line prints nothing.

- [ ] **Step 7: Commit**

```bash
git add src/diagrams_as_code/context.py src/diagrams_as_code/elements.py src/diagrams_as_code/diagram.py tests/test_module_boundaries.py
git commit -m "refactor: break the elements -> diagram import cycle and enforce layering

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: PNG backends in `rasterize.py`

**Files:**
- Create: `src/diagrams_as_code/rasterize.py`
- Create: `tests/test_rasterize.py`
- Modify: `src/diagrams_as_code/diagram.py` (`render_png`, lines ~503-566)
- Modify: `tests/test_dependency_catalog.py:31-33` (fixture reads the new module)

**Interfaces:**
- Produces: `rasterize.BACKENDS: tuple[tuple[str, Backend], ...]` where `Backend = Callable[[str, Path], Optional[bytes]]` (returns `None` when the backend is unavailable), and `rasterize.svg_to_png(svg: str, path: Path) -> bytes`.

- [ ] **Step 1: Write the failing test**

`tests/test_rasterize.py`:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from diagrams_as_code import rasterize

SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"/>'


def test_backend_order_is_stable() -> None:
    assert [name for name, _ in rasterize.BACKENDS] == [
        "resvg-py",
        "cairosvg",
        "inkscape",
        "imagemagick",
    ]


def test_first_available_backend_wins(tmp_path: Path, monkeypatch) -> None:
    calls: list[str] = []

    def missing(svg: str, path: Path):
        calls.append("missing")
        return None

    def works(svg: str, path: Path):
        calls.append("works")
        path.write_bytes(b"PNG")
        return b"PNG"

    monkeypatch.setattr(rasterize, "BACKENDS", (("a", missing), ("b", works), ("c", missing)))
    assert rasterize.svg_to_png(SVG, tmp_path / "x.png") == b"PNG"
    assert calls == ["missing", "works"]


def test_no_backend_raises_with_install_hint(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(rasterize, "BACKENDS", (("a", lambda s, p: None),))
    with pytest.raises(RuntimeError, match="uv add --dev resvg-py"):
        rasterize.svg_to_png(SVG, tmp_path / "x.png")
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_rasterize.py -q`
Expected: FAIL — `ImportError: cannot import name 'rasterize'`.

- [ ] **Step 3: Create `rasterize.py`** (logic moved verbatim from `Diagram.render_png`)

```python
"""PNG rasterization backends, tried in order until one is available."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Callable, Optional

Backend = Callable[[str, Path], Optional[bytes]]


def _resvg(svg: str, path: Path) -> Optional[bytes]:
    try:
        import resvg_py  # type: ignore
    except ImportError:
        return None
    png: bytes = resvg_py.svg_to_bytes(svg)
    path.write_bytes(png)
    return png


def _cairosvg(svg: str, path: Path) -> Optional[bytes]:
    try:
        import cairosvg  # type: ignore
    except ImportError:
        return None
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(path))
    return path.read_bytes()


def _run_converter(argv_for: Callable[[Path], list[str]], svg: str, path: Path) -> Optional[bytes]:
    temp_svg = path.with_suffix(".temp.svg")
    try:
        temp_svg.write_text(svg, encoding="utf-8")
        res = subprocess.run(argv_for(temp_svg), capture_output=True)
        if res.returncode == 0 and path.exists():
            return path.read_bytes()
        return None
    finally:
        if temp_svg.exists():
            temp_svg.unlink()


def _inkscape(svg: str, path: Path) -> Optional[bytes]:
    inkscape_bin = shutil.which("inkscape")
    if not inkscape_bin:
        return None
    return _run_converter(lambda src: [inkscape_bin, str(src), "-o", str(path)], svg, path)


def _imagemagick(svg: str, path: Path) -> Optional[bytes]:
    magick_bin = shutil.which("magick") or shutil.which("convert")
    if not magick_bin:
        return None
    return _run_converter(lambda src: [magick_bin, str(src), str(path)], svg, path)


BACKENDS: tuple[tuple[str, Backend], ...] = (
    ("resvg-py", _resvg),
    ("cairosvg", _cairosvg),
    ("inkscape", _inkscape),
    ("imagemagick", _imagemagick),
)


def svg_to_png(svg: str, path: Path) -> bytes:
    """Rasterize ``svg`` to ``path`` with the first available backend."""
    for _name, backend in BACKENDS:
        png = backend(svg, path)
        if png is not None:
            return png
    raise RuntimeError(
        "PNG rendering requires 'resvg-py', 'cairosvg', or system utilities ('inkscape'/'magick'). "
        "Install with: uv add --dev resvg-py"
    )
```

- [ ] **Step 4: Delegate from `Diagram.render_png`**

Add `from diagrams_as_code import context, rasterize` (merge with Task 1's import). Replace the whole method body:

```python
    def render_png(self, path: Union[str, Path]) -> bytes:
        """Render diagram to PNG file using resvg-py, cairosvg, or system converters."""
        svg_content = self.render_svg()
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return rasterize.svg_to_png(svg_content, p)
```

- [ ] **Step 5: Point the dependency-catalog test at the module**

In `tests/test_dependency_catalog.py`, replace the fixture:

```python
@pytest.fixture(scope="module")
def render_png_source() -> str:
    from diagrams_as_code import rasterize

    return inspect.getsource(rasterize)
```

Its docstring/comments that say ``render_png`` stay accurate (the chain is what `render_png` reaches for).

- [ ] **Step 6: Add `rasterize` to `LAYERS`** — already present at layer 0 from Task 1. Run: `uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/`
Expected: all pass; no modified tracked output. `test_png_backend_chain_is_fully_catalogued` still passes (it detects `resvg_py`, `cairosvg`, `inkscape`, `magick`, `convert`).

- [ ] **Step 7: Commit**

```bash
git add src/diagrams_as_code/rasterize.py src/diagrams_as_code/diagram.py tests/test_rasterize.py tests/test_dependency_catalog.py
git commit -m "refactor: move PNG backends out of Diagram into rasterize.py

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Icon glyphs as a table in `icon_glyphs.py`

**Files:**
- Create: `src/diagrams_as_code/icon_glyphs.py` (generated once by the script in Step 3, then hand-maintained)
- Create: `tests/test_icon_glyphs.py`
- Modify: `src/diagrams_as_code/shapes.py` (`_render_icon_content`, lines 464-948)

**Interfaces:**
- Produces: `icon_glyphs.GlyphFn = Callable[[str, float], str]` and `icon_glyphs.GLYPHS: dict[str, GlyphFn]`, keyed by canonical icon name.

- [ ] **Step 1: Write the failing test**

`tests/test_icon_glyphs.py`:

```python
from __future__ import annotations

from diagrams_as_code.icon_glyphs import GLYPHS
from diagrams_as_code.shapes import ShapeLibrary


def test_every_catalog_icon_has_exactly_one_glyph() -> None:
    assert set(GLYPHS) == set(ShapeLibrary._ICON_CATALOG)


def test_glyphs_use_the_requested_color_and_stroke() -> None:
    for name, glyph in GLYPHS.items():
        body = glyph("#ABCDEF", 1.25)
        assert "#ABCDEF" in body, name
        assert body.strip(), name
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_icon_glyphs.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'diagrams_as_code.icon_glyphs'`.

- [ ] **Step 3: Generate `icon_glyphs.py` from the `if/elif` chain**

Run this one-off script (do not commit it). It fails loudly if any branch is not a plain `canonical == "<name>"` test with a single `return`:

```bash
uv run python - <<'EOF'
import ast, textwrap
from pathlib import Path

src_path = Path("src/diagrams_as_code/shapes.py")
src = src_path.read_text(encoding="utf-8")
lines = src.splitlines()
tree = ast.parse(src)
fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_render_icon_content")
chain = next(s for s in fn.body if isinstance(s, ast.If) and isinstance(s.test, ast.Compare)
             and isinstance(s.test.left, ast.Name) and s.test.left.id == "canonical"
             and isinstance(s.test.ops[0], ast.Eq))
out = ['"""SVG bodies for the built-in icons, drawn on a 24x24 grid.',
       '',
       'Each glyph takes the stroke/fill color and stroke width and returns the',
       'markup that ``ShapeLibrary.render_icon`` wraps in a positioned ``<g>``.',
       'Icon names, domains and descriptions live in ``ShapeLibrary._ICON_CATALOG``.',
       '"""',
       'from __future__ import annotations',
       '',
       'from typing import Callable',
       '',
       'GlyphFn = Callable[[str, float], str]',
       '']
names = []
node = chain
while node is not None:
    test = node.test
    assert isinstance(test, ast.Compare) and test.left.id == "canonical" and isinstance(test.ops[0], ast.Eq), ast.dump(test)
    name = test.comparators[0].value
    assert len(node.body) == 1 and isinstance(node.body[0], ast.Return), name
    ret = node.body[0]
    body = textwrap.dedent("\n".join(lines[ret.lineno - 1:ret.end_lineno]))
    out += ["", f"def _{name}(color: str, stroke_width: float) -> str:", textwrap.indent(body, "    "), ""]
    names.append(name)
    node = node.orelse[0] if node.orelse else None
    if node is not None:
        assert isinstance(node, ast.If), "unexpected else branch"
out += ["", "GLYPHS: dict[str, GlyphFn] = {"]
out += [f'    "{n}": _{n},' for n in names]
out += ["}", ""]
text = "\n".join(out)
while "\n\n\n\n" in text:
    text = text.replace("\n\n\n\n", "\n\n\n")
Path("src/diagrams_as_code/icon_glyphs.py").write_text(text, encoding="utf-8")
print(len(names), "glyphs; chain spans lines", chain.lineno, "to", chain.end_lineno)
EOF
```

Expected: `60 glyphs; chain spans lines 474 to 946` (line numbers may differ by a few).

- [ ] **Step 4: Replace the chain in `shapes.py`**

Add `from diagrams_as_code.icon_glyphs import GLYPHS` to the imports. Replace the entire body of `_render_icon_content` (from `# Core & IIoT icons` through `raise KeyError(...)`) so the method reads:

```python
    def _render_icon_content(
        self, canonical: str, color: str, stroke_width: float
    ) -> str:
        # Custom loaded icons
        if canonical in self._custom_icons:
            content = self._custom_icons[canonical]
            content = content.replace("currentColor", color)
            return content

        glyph = GLYPHS.get(canonical)
        if glyph is None:
            raise KeyError(f"Unhandled icon '{canonical}'")
        return glyph(color, stroke_width)
```

- [ ] **Step 5: Verify byte-identical icons and diagrams**

Run: `uv run pytest -q && uv run python tools/generate_icons.py --check && git status --porcelain -- output/ icons/ README.md docs/`
Expected: all pass, `--check` reports up to date, no modified tracked files. `wc -l src/diagrams_as_code/shapes.py` is now under 560.

- [ ] **Step 6: Commit**

```bash
git add src/diagrams_as_code/icon_glyphs.py src/diagrams_as_code/shapes.py tests/test_icon_glyphs.py
git commit -m "refactor: move the 60 icon glyphs out of a 486-line if/elif into a table

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Model prep — theme overrides, explicit ids, public element walk, lenient solve, `Rect.intersects`

**Files:**
- Modify: `src/diagrams_as_code/diagram.py` (`__init__` theme block lines ~244-262; `shape()` / `group()` id lines)
- Modify: `src/diagrams_as_code/elements.py` (`Element.__init__`)
- Modify: `src/diagrams_as_code/constraints.py` (`_collect_all_elements`, `solve`)
- Modify: `src/diagrams_as_code/geometry.py` (`Rect`)
- Test: `tests/test_model_prep.py` (create)

**Interfaces:**
- Produces: `Element.explicit_id: bool` (default `True`; `False` when `Diagram.shape`/`Diagram.group` generated the id).
- Produces: `ConstraintSolver.all_elements() -> list[Element]` (`_collect_all_elements` stays as an alias), `ConstraintSolver.solve(strict: bool = True) -> None`.
- Produces: `Rect.intersects(other: Rect) -> bool` — true only when interiors overlap (touching edges do not count).

- [ ] **Step 1: Write the failing tests**

`tests/test_model_prep.py`:

```python
from __future__ import annotations

import pytest

from diagrams_as_code import ConstraintSolver, Diagram, Rect, Shape


def test_theme_overrides_keep_every_other_field() -> None:
    base = Diagram(theme="nord").theme
    diag = Diagram(theme="nord", theme_overrides={"accent": "#123456"})
    assert diag.theme.accent == "#123456"
    assert diag.theme.name == "nord_custom"
    assert diag.theme.font_family == base.font_family
    assert diag.theme.background == base.background


def test_unknown_theme_override_is_rejected() -> None:
    with pytest.raises(TypeError):
        Diagram(theme_overrides={"no_such_field": "x"})


def test_explicit_id_is_recorded() -> None:
    diag = Diagram()
    assert diag.shape("A").explicit_id is False
    assert diag.shape("B", id="b").explicit_id is True
    with diag.group("G") as g:
        pass
    assert g.explicit_id is False
    assert Shape("s", "S").explicit_id is True


def test_all_elements_is_public_and_matches_alias() -> None:
    diag = Diagram()
    with diag.group("G"):
        diag.shape("A")
    assert diag.solver.all_elements() == diag.solver._collect_all_elements()
    assert [e.label for e in diag.solver.all_elements()] == ["G", "A"]


def test_lenient_solve_leaves_unresolvable_elements_alone() -> None:
    outside = Shape("out", "Out")
    inner = Shape("in", "In").right_of(outside)
    solver = ConstraintSolver()
    solver.add(inner)
    with pytest.raises(RuntimeError):
        solver.solve()
    solver.solve(strict=False)  # no raise


def test_rect_intersects_excludes_touching_edges() -> None:
    a = Rect(0, 0, 10, 10)
    assert a.intersects(Rect(5, 5, 10, 10))
    assert not a.intersects(Rect(10, 0, 10, 10))
    assert not a.intersects(Rect(0, 20, 10, 10))
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_model_prep.py -q`
Expected: FAIL — `AttributeError: 'Shape' object has no attribute 'explicit_id'`, `'ConstraintSolver' object has no attribute 'all_elements'`, `solve() got an unexpected keyword argument 'strict'`, `'Rect' object has no attribute 'intersects'`. (The two theme tests may already pass; they pin behavior for the refactor.)

- [ ] **Step 3: Implement**

`elements.py`, in `Element.__init__` after `self._diagram = None`:

```python
        self.explicit_id: bool = True
```

`diagram.py`, add `import dataclasses` at the top, and replace the theme block in `__init__`:

```python
        base_t = get_theme(theme)
        if theme_overrides:
            self.theme = dataclasses.replace(
                base_t, name=f"{base_t.name}_custom", **theme_overrides
            )
        else:
            self.theme = base_t
```

`diagram.py`, in `shape()` after `s._diagram = self`: `s.explicit_id = id is not None`; in `group()` after `g._diagram = self`: `g.explicit_id = id is not None`.

`constraints.py`: rename `_collect_all_elements` to `all_elements` (docstring: "Return every element, groups before their children, in declaration order."), then add below it:

```python
    _collect_all_elements = all_elements
```

Change the signature to `def solve(self, strict: bool = True) -> None:` and guard the final raise:

```python
        unsolved = [e.id for e in all_elements if e not in solved]
        if unsolved and strict:
            raise RuntimeError(f"Unresolved constraints for elements: {unsolved}")
```

and update the one call inside `solve` to `self.all_elements()`. In `diagram.py`, change `self.solver._collect_all_elements()` to `self.solver.all_elements()`.

`geometry.py`, in `Rect` after `union`:

```python
    def intersects(self, other: Rect) -> bool:
        """Return True when the two rectangles' interiors overlap."""
        return (
            self.left < other.right
            and other.left < self.right
            and self.top < other.bottom
            and other.top < self.bottom
        )
```

- [ ] **Step 4: Run tests and output guard**

Run: `uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/`
Expected: all pass; nothing modified.

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/diagram.py src/diagrams_as_code/elements.py src/diagrams_as_code/constraints.py src/diagrams_as_code/geometry.py tests/test_model_prep.py
git commit -m "refactor: prepare the model for layout (explicit ids, lenient solve, Rect.intersects)

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: `output.render_all` and the `diagram()` script contract

**Files:**
- Create: `src/diagrams_as_code/output.py`
- Create: `tests/test_output.py`
- Modify: all 80 `examples/<domain>/*.py` (scripted), `examples/01_mockup_slide.py`, `examples/02_high_availability.py`, `examples/03_sparkplug_pipeline.py`, `main.py` (by hand)

**Interfaces:**
- Produces: `output.FORMATS = ("svg", "png", "bom")`, `output.render_all(diag, out_dir: str | Path, stem: str, formats: Iterable[str] = FORMATS, readme_name: str | None = None) -> dict[str, Path]` — keys in `FORMATS` order, only for requested formats; creates `out_dir`; raises `ValueError` on an unknown format.
- Produces: every example and `main.py` defines `diagram() -> Diagram`; top-level examples and `main.py` define `OUTPUT_STEM`.

- [ ] **Step 1: Write the failing test**

`tests/test_output.py`:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def _diag() -> Diagram:
    with Diagram("T") as d:
        a = d.shape("A").at(60, 80)
        b = d.shape("B").right_of(a)
        a >> b
    return d


def test_writes_requested_formats_in_canonical_order(tmp_path: Path) -> None:
    written = render_all(_diag(), tmp_path / "out", "demo", formats=("bom", "svg"))
    assert list(written) == ["svg", "bom"]
    assert written["svg"] == tmp_path / "out" / "demo.svg"
    assert written["bom"] == tmp_path / "out" / "demo_README.md"
    assert "./demo.svg" in written["bom"].read_text(encoding="utf-8")


def test_readme_name_override(tmp_path: Path) -> None:
    written = render_all(_diag(), tmp_path, "main_architecture", formats=("svg", "bom"), readme_name="main_README.md")
    assert written["bom"].name == "main_README.md"


def test_unknown_format_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="gif"):
        render_all(_diag(), tmp_path, "x", formats=("svg", "gif"))
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_output.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'diagrams_as_code.output'`.

- [ ] **Step 3: Create `output.py`**

```python
"""Write a diagram's SVG, PNG and Bill of Materials to a directory."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Optional, Union

if TYPE_CHECKING:
    from diagrams_as_code.diagram import Diagram

FORMATS: tuple[str, ...] = ("svg", "png", "bom")


def render_all(
    diag: Diagram,
    out_dir: Union[str, Path],
    stem: str,
    formats: Iterable[str] = FORMATS,
    readme_name: Optional[str] = None,
) -> dict[str, Path]:
    """Render ``diag`` as ``<stem>.svg``, ``<stem>.png`` and a BOM README."""
    wanted = set(formats)
    unknown = sorted(wanted - set(FORMATS))
    if unknown:
        raise ValueError(f"unknown output format(s) {unknown}; choose from {list(FORMATS)}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_name = f"{stem}.svg"
    written: dict[str, Path] = {}
    for fmt in FORMATS:
        if fmt not in wanted:
            continue
        if fmt == "svg":
            path = out / svg_name
            diag.render_svg(path)
        elif fmt == "png":
            path = out / f"{stem}.png"
            diag.render_png(path)
        else:
            path = out / (readme_name or f"{stem}_README.md")
            diag.generate_readme(svg_name, path)
        written[fmt] = path
    return written
```

Run: `uv run pytest tests/test_output.py tests/test_module_boundaries.py -q` → PASS.

- [ ] **Step 4: Convert the 80 domain examples**

Every domain example has this shape (verified for all 80): a `build_diagram` that sets `out`, `svg_file`, `png_file`, `readme_file`, then a `with Diagram(...) as diag:` block, then `diag.render_svg(svg_file)`, `diag.render_png(png_file)`, `diag.generate_readme("<stem>.svg", readme_file)`, `return svg_file`. Run this one-off converter (do not commit it); it refuses any file that deviates:

```bash
uv run python - <<'EOF'
import re
from pathlib import Path

for path in sorted(Path("examples").glob("*/*.py")):
    src = path.read_text(encoding="utf-8")
    stem = path.stem
    m = re.search(
        r'^def build_diagram\((?P<sig>[^)]*)\) -> Path:\n'
        r'    out = Path\(output_dir\)\n'
        r'    out\.mkdir\(parents=True, exist_ok=True\)\n'
        rf'    svg_file = out / "{stem}\.svg"\n'
        rf'    png_file = out / "{stem}\.png"\n'
        rf'    readme_file = out / "{stem}_README\.md"\n'
        r'\n'
        r'(?P<body>    with Diagram\(.*?)\n'
        r'(?:    # [^\n]*\n)?'
        r'    diag\.render_svg\(svg_file\)\n'
        r'    diag\.render_png\(png_file\)\n'
        rf'    diag\.generate_readme\("{stem}\.svg", readme_file\)\n'
        r'\n'
        r'    return svg_file\n',
        src, re.S | re.M)
    assert m, f"unexpected structure: {path}"
    body = m.group("body").rstrip("\n")
    new = (
        "def diagram() -> Diagram:\n"
        f"{body}\n"
        "\n"
        "    return diag\n"
        "\n"
        "\n"
        f"def build_diagram({m.group('sig')}) -> Path:\n"
        f'    return render_all(diagram(), output_dir, "{stem}")["svg"]\n'
    )
    src = src[:m.start()] + new + src[m.end():]
    src = src.replace(
        "from diagrams_as_code import ",
        "from diagrams_as_code.output import render_all\nfrom diagrams_as_code import ",
        1,
    )
    path.write_text(src, encoding="utf-8")
print("converted")
EOF
```

Then fix import order to the file's style: `from diagrams_as_code import …` stays first, `from diagrams_as_code.output import render_all` right after it:

```bash
uv run python - <<'EOF'
from pathlib import Path
for path in sorted(Path("examples").glob("*/*.py")):
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    i = lines.index("from diagrams_as_code.output import render_all\n")
    lines[i], lines[i + 1] = lines[i + 1], lines[i]
    path.write_text("".join(lines), encoding="utf-8")
EOF
```

Verify one: `sed -n 1,20p examples/cloud/01_simple_vpc_web.py` shows `def diagram() -> Diagram:` followed by the `with Diagram(` block, and the file ends with `build_diagram` returning `render_all(...)["svg"]` and the unchanged `__main__` block.

- [ ] **Step 5: Convert the 3 top-level examples and `main.py` by hand**

Each has a function (`generate_mockup_slide`, `generate_high_availability`, `generate_sparkplug_pipeline`, `generate_main_architecture`) that builds a diagram, writes three files and prints `Generated: <path>` for each. For each file:

1. Add `OUTPUT_STEM = "<stem>"` below the imports: `mockup_slide`, `high_availability`, `sparkplug_pipeline`, `main_architecture`.
2. Add `from diagrams_as_code.output import render_all`.
3. Move the build code (everything in the function except the `out_dir = Path(...)`/`mkdir` lines and the path/render/print tail) into `def diagram() -> Diagram:` ending in `return diag`.
4. Replace the original function body with (for `main.py`, pass `readme_name="main_README.md"`):

```python
def generate_mockup_slide(output_dir: Path | str = "output") -> Diagram:
    diag = diagram()
    for path in render_all(diag, output_dir, OUTPUT_STEM).values():
        print(f"Generated: {path}")
    return diag
```

```python
def generate_main_architecture(output_dir: Path | str = "output") -> Diagram:
    diag = diagram()
    for path in render_all(diag, output_dir, OUTPUT_STEM, readme_name="main_README.md").values():
        print(f"Generated: {path}")
    return diag
```

Keep each file's `__main__`/`main()` block unchanged. Confirm the original README calls used `include_connections=True` (the default `render_all` relies on): `git show HEAD:main.py | grep -n include_connections`.

- [ ] **Step 6: Verify byte-identical output**

Run: `uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/ && git diff --stat -- examples main.py | tail -1`
Expected: all pass; `git status` prints nothing; the diff stat covers 84 files.

- [ ] **Step 7: Commit**

```bash
git add src/diagrams_as_code/output.py tests/test_output.py examples main.py
git commit -m "refactor: separate building a diagram from writing its files

Every example and main.py now defines diagram() -> Diagram; file writing
goes through output.render_all. Rendered output is byte-identical.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Layout graph model and the `LayeredLayout` engine

**Files:**
- Create: `src/diagrams_as_code/layout/__init__.py`, `layout/base.py`, `layout/layered.py`
- Create: `tests/test_layout_layered.py`

**Interfaces:**
- Produces (`layout/base.py`):
  - `SOURCE_KEY = "_layout_source"` — constraint dict key; values `"auto"` or `"file"`.
  - `@dataclass(frozen=True) LayoutNode(id: str, width: float, height: float, index: int)`
  - `@dataclass(frozen=True) LayoutEdge(source: str, target: str, weight: int = 1)`
  - `@dataclass(frozen=True) LayoutGraph(nodes: tuple[LayoutNode, ...], edges: tuple[LayoutEdge, ...])`
  - `class LayoutEngine(Protocol): def arrange(self, graph: LayoutGraph) -> dict[str, Point]`
  - `class LayoutWarning(UserWarning)`
- Produces (`layout/layered.py`): `DIRECTIONS = ("LR", "TB")`, `LayeredLayout(direction="LR", rank_gap=80.0, node_gap=40.0, sweeps=4)` with `.arrange(graph) -> dict[str, Point]` (top-left corners, scope origin at `(0, 0)`), and module function `crossings(layers: list[list[str]], edges: list[tuple[str, str, int]]) -> int` (exposed for tests).

- [ ] **Step 1: Write the failing tests**

`tests/test_layout_layered.py`:

```python
from __future__ import annotations

import pytest

from diagrams_as_code.geometry import Rect
from diagrams_as_code.layout.base import LayoutEdge, LayoutGraph, LayoutNode
from diagrams_as_code.layout.layered import LayeredLayout


def graph(nodes: list[tuple[str, float, float]], edges: list[tuple[str, str]]) -> LayoutGraph:
    return LayoutGraph(
        nodes=tuple(LayoutNode(n, w, h, i) for i, (n, w, h) in enumerate(nodes)),
        edges=tuple(LayoutEdge(s, t) for s, t in edges),
    )


def rects(g: LayoutGraph, pos) -> dict[str, Rect]:
    return {n.id: Rect(pos[n.id].x, pos[n.id].y, n.width, n.height) for n in g.nodes}


def test_empty_graph() -> None:
    assert LayeredLayout().arrange(LayoutGraph((), ())) == {}


def test_chain_left_to_right() -> None:
    g = graph([("a", 100, 50), ("b", 100, 50), ("c", 100, 50)], [("a", "b"), ("b", "c")])
    pos = LayeredLayout(rank_gap=80).arrange(g)
    assert [(pos[n].x, pos[n].y) for n in "abc"] == [(0, 0), (180, 0), (360, 0)]


def test_chain_top_to_bottom() -> None:
    g = graph([("a", 100, 50), ("b", 100, 50)], [("a", "b")])
    pos = LayeredLayout(direction="TB", rank_gap=80).arrange(g)
    assert (pos["a"].x, pos["a"].y, pos["b"].x, pos["b"].y) == (0, 0, 0, 130)


def test_diamond_stacks_the_middle_rank_and_centers_the_ends() -> None:
    g = graph([(n, 100, 50) for n in "abcd"], [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    pos = LayeredLayout(node_gap=40).arrange(g)
    assert pos["b"].x == pos["c"].x == 180
    assert pos["c"].y - pos["b"].y == 90
    assert pos["a"].y == pos["d"].y == 45  # centered on the 140-tall middle rank


def test_ordering_removes_an_avoidable_crossing() -> None:
    g = graph([("a", 50, 50), ("b", 50, 50), ("c", 50, 50), ("d", 50, 50)], [("a", "d"), ("b", "c")])
    pos = LayeredLayout().arrange(g)
    assert pos["d"].y < pos["c"].y


def test_cycle_is_ranked_in_declaration_order() -> None:
    g = graph([("a", 50, 50), ("b", 50, 50)], [("a", "b"), ("b", "a")])
    pos = LayeredLayout().arrange(g)
    assert pos["a"].x < pos["b"].x


def test_self_loops_and_unknown_endpoints_are_ignored() -> None:
    g = graph([("a", 50, 50)], [("a", "a"), ("a", "ghost")])
    assert LayeredLayout().arrange(g) == {"a": LayeredLayout().arrange(g)["a"]}


def _messy() -> LayoutGraph:
    names = [f"n{i}" for i in range(12)]
    sizes = [(n, 60 + 10 * (i % 4), 40 + 15 * (i % 3)) for i, n in enumerate(names)]
    edges = [(names[i], names[(i * 7 + 3) % 12]) for i in range(12)]
    return graph(sizes, edges)


@pytest.mark.parametrize("direction", ["LR", "TB"])
def test_no_two_nodes_overlap(direction: str) -> None:
    g = _messy()
    r = rects(g, LayeredLayout(direction=direction).arrange(g))
    ids = sorted(r)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            assert not r[a].intersects(r[b]), (a, b)


def test_arrange_is_deterministic() -> None:
    assert LayeredLayout().arrange(_messy()) == LayeredLayout().arrange(_messy())


def test_invalid_arguments() -> None:
    with pytest.raises(ValueError, match="direction"):
        LayeredLayout(direction="RL")
    with pytest.raises(ValueError, match="non-negative"):
        LayeredLayout(rank_gap=-1)
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_layout_layered.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'diagrams_as_code.layout'`.

- [ ] **Step 3: Create `layout/base.py`**

```python
"""Data model shared by layout engines, the graph builder and the pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from diagrams_as_code.geometry import Point

#: Key marking constraints the layout pipeline generated ("auto" or "file").
#: They are removed at the start of every pipeline run.
SOURCE_KEY = "_layout_source"


class LayoutWarning(UserWarning):
    """A layout result that is probably not what the author intended."""


@dataclass(frozen=True)
class LayoutNode:
    """One element to place: its size and declaration order."""

    id: str
    width: float
    height: float
    index: int


@dataclass(frozen=True)
class LayoutEdge:
    """A directed connection between two nodes of the same scope."""

    source: str
    target: str
    weight: int = 1


@dataclass(frozen=True)
class LayoutGraph:
    """The nodes and edges of one scope (the canvas or one group)."""

    nodes: tuple[LayoutNode, ...]
    edges: tuple[LayoutEdge, ...]


class LayoutEngine(Protocol):
    """Places every node of a graph; returns top-left corners from (0, 0)."""

    def arrange(self, graph: LayoutGraph) -> dict[str, Point]: ...
```

- [ ] **Step 4: Create `layout/layered.py`**

```python
"""Layered (Sugiyama-style) placement for one scope of a diagram.

Ranks follow edge direction, each rank is ordered to reduce crossings, and
ranks are spaced evenly. Everything is deterministic: ties break by the
node's declaration index, and no unordered set is ever iterated.
Only edges between adjacent ranks inform ordering; longer edges still set
ranks but get no dummy nodes (v1).
"""
from __future__ import annotations

import heapq

from diagrams_as_code.geometry import Point
from diagrams_as_code.layout.base import LayoutGraph, LayoutNode

DIRECTIONS = ("LR", "TB")

Edges = dict[tuple[str, str], int]


class LayeredLayout:
    """Rank nodes by edge direction and space the ranks along one axis."""

    def __init__(
        self,
        direction: str = "LR",
        rank_gap: float = 80.0,
        node_gap: float = 40.0,
        sweeps: int = 4,
    ) -> None:
        if direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, got {direction!r}")
        if rank_gap < 0 or node_gap < 0:
            raise ValueError("rank_gap and node_gap must be non-negative")
        self.direction = direction
        self.rank_gap = float(rank_gap)
        self.node_gap = float(node_gap)
        self.sweeps = int(sweeps)

    def arrange(self, graph: LayoutGraph) -> dict[str, Point]:
        """Return the top-left corner of every node in ``graph``."""
        if not graph.nodes:
            return {}
        index = {n.id: n.index for n in graph.nodes}
        dag = _acyclic_edges(graph, index)
        rank = _ranks(dag, index)
        layers = _order(rank, dag, index, self.sweeps)
        return self._coordinates(layers, {n.id: n for n in graph.nodes})

    def _coordinates(
        self, layers: list[list[str]], nodes: dict[str, LayoutNode]
    ) -> dict[str, Point]:
        lr = self.direction == "LR"

        def along(n: LayoutNode) -> float:
            return n.width if lr else n.height

        def across(n: LayoutNode) -> float:
            return n.height if lr else n.width

        extents = [max(along(nodes[i]) for i in layer) for layer in layers]
        spans = [
            sum(across(nodes[i]) for i in layer) + self.node_gap * (len(layer) - 1)
            for layer in layers
        ]
        widest = max(spans)
        out: dict[str, Point] = {}
        offset = 0.0
        for layer, extent, span in zip(layers, extents, spans):
            cursor = (widest - span) / 2.0
            for nid in layer:
                n = nodes[nid]
                a = offset + (extent - along(n)) / 2.0
                out[nid] = Point(a, cursor) if lr else Point(cursor, a)
                cursor += across(n) + self.node_gap
            offset += extent + self.rank_gap
        return out


def _acyclic_edges(graph: LayoutGraph, index: dict[str, int]) -> Edges:
    """Merge parallel edges, drop self-loops, reverse DFS back edges."""
    weights: Edges = {}
    for e in graph.edges:
        if e.source == e.target or e.source not in index or e.target not in index:
            continue
        key = (e.source, e.target)
        weights[key] = weights.get(key, 0) + e.weight

    succ: dict[str, list[str]] = {n: [] for n in index}
    for s, t in weights:
        succ[s].append(t)
    for targets in succ.values():
        targets.sort(key=index.__getitem__)

    state: dict[str, int] = {}  # 1 = on the DFS stack, 2 = finished
    back: set[tuple[str, str]] = set()
    for root in sorted(index, key=index.__getitem__):
        if root in state:
            continue
        state[root] = 1
        stack = [(root, iter(succ[root]))]
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
            elif state.get(nxt) == 1:
                back.add((node, nxt))
            elif nxt not in state:
                state[nxt] = 1
                stack.append((nxt, iter(succ[nxt])))

    dag: Edges = {}
    for (s, t), w in weights.items():
        if (s, t) in back:
            s, t = t, s
        dag[(s, t)] = dag.get((s, t), 0) + w
    return dag


def _ranks(dag: Edges, index: dict[str, int]) -> dict[str, int]:
    """Longest-path ranking; sources and isolated nodes get rank 0."""
    preds: dict[str, list[str]] = {n: [] for n in index}
    succ: dict[str, list[str]] = {n: [] for n in index}
    indeg = {n: 0 for n in index}
    for s, t in dag:
        succ[s].append(t)
        preds[t].append(s)
        indeg[t] += 1
    heap = [(index[n], n) for n in index if indeg[n] == 0]
    heapq.heapify(heap)
    rank: dict[str, int] = {}
    while heap:
        _, n = heapq.heappop(heap)
        rank[n] = max((rank[p] + 1 for p in preds[n]), default=0)
        for t in succ[n]:
            indeg[t] -= 1
            if indeg[t] == 0:
                heapq.heappush(heap, (index[t], t))
    return rank


def _order(
    rank: dict[str, int], dag: Edges, index: dict[str, int], sweeps: int
) -> list[list[str]]:
    """Barycenter sweeps; a sweep is kept only if it lowers crossings."""
    layers: list[list[str]] = [[] for _ in range(max(rank.values()) + 1)]
    for n in sorted(rank, key=index.__getitem__):
        layers[rank[n]].append(n)
    adjacent = [(s, t, w) for (s, t), w in dag.items() if rank[t] - rank[s] == 1]

    best = [list(layer) for layer in layers]
    best_cross = crossings(best, adjacent)
    current = [list(layer) for layer in best]
    for i in range(sweeps):
        _sweep(current, adjacent, downward=(i % 2 == 0))
        c = crossings(current, adjacent)
        if c < best_cross:
            best, best_cross = [list(layer) for layer in current], c
        else:
            current = [list(layer) for layer in best]
    return best


def _sweep(
    layers: list[list[str]], adjacent: list[tuple[str, str, int]], downward: bool
) -> None:
    ranks = range(1, len(layers)) if downward else range(len(layers) - 2, -1, -1)
    for r in ranks:
        ref = layers[r - 1] if downward else layers[r + 1]
        ref_pos = {n: i for i, n in enumerate(ref)}
        mine = layers[r]
        mine_pos = {n: i for i, n in enumerate(mine)}
        acc: dict[str, list[float]] = {}
        for s, t, w in adjacent:
            node, other = (t, s) if downward else (s, t)
            if node in mine_pos and other in ref_pos:
                a = acc.setdefault(node, [0.0, 0.0])
                a[0] += ref_pos[other] * w
                a[1] += w

        def key(n: str) -> tuple[float, int]:
            a = acc.get(n)
            return (a[0] / a[1] if a else float(mine_pos[n]), mine_pos[n])

        layers[r] = sorted(mine, key=key)


def crossings(layers: list[list[str]], edges: list[tuple[str, str, int]]) -> int:
    """Weighted count of crossing edge pairs between adjacent layers."""
    pos: dict[str, int] = {}
    layer_of: dict[str, int] = {}
    for r, layer in enumerate(layers):
        for i, n in enumerate(layer):
            pos[n] = i
            layer_of[n] = r
    total = 0
    for r in range(len(layers) - 1):
        spans = [(pos[s], pos[t], w) for s, t, w in edges if layer_of[s] == r]
        for i, a in enumerate(spans):
            for b in spans[i + 1:]:
                if (a[0] - b[0]) * (a[1] - b[1]) < 0:
                    total += a[2] * b[2]
    return total
```

- [ ] **Step 5: Create `layout/__init__.py`** (extended in Tasks 7–9)

```python
"""Automatic placement: engines, the layout graph, the layout file and the solve pipeline."""
from diagrams_as_code.layout.base import (
    LayoutEdge,
    LayoutEngine,
    LayoutGraph,
    LayoutNode,
    LayoutWarning,
)
from diagrams_as_code.layout.layered import LayeredLayout

__all__ = [
    "LayeredLayout",
    "LayoutEdge",
    "LayoutEngine",
    "LayoutGraph",
    "LayoutNode",
    "LayoutWarning",
]
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest tests/test_layout_layered.py tests/test_module_boundaries.py -q`
Expected: PASS. If `test_diamond_…` fails on `pos["a"].y`, recheck `_coordinates` centering: middle rank span = 50 + 40 + 50 = 140, end ranks span 50 → offset (140 − 50) / 2 = 45.

- [ ] **Step 7: Commit**

```bash
git add src/diagrams_as_code/layout tests/test_layout_layered.py
git commit -m "feat(layout): add a deterministic layered layout engine

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Building a scope's layout graph from a diagram

**Files:**
- Create: `src/diagrams_as_code/layout/graph.py`
- Create: `src/diagrams_as_code/metrics.py`
- Create: `tests/test_layout_graph.py`
- Modify: `src/diagrams_as_code/renderer_svg.py:296,315` (the two `b.y + b.height + 14.0` label-below offsets)

**Interfaces:**
- Consumes: `LayoutNode`, `LayoutEdge`, `LayoutGraph`, `SOURCE_KEY` (Task 6); `ConstraintSolver.all_elements()` (Task 4).
- Produces:
  - `metrics.LABEL_BELOW_OFFSET = 14.0` (baseline distance below the shape, used by the renderer) and `metrics.LABEL_BELOW_EXTRA = 24.0` (room layout reserves below the shape). `layout/graph.py` re-exports `LABEL_BELOW_EXTRA`.
  - `scope_children(diagram, group: Group | None) -> list[Element]` — root scope: elements with `parent is None` in `diagram.solver.elements` order; group scope: `group.children`.
  - `lift(element, group: Group | None) -> Element | None` — the ancestor-or-self of `element` that is a direct child of `group`, or `None`.
  - `is_user_pinned(element) -> bool` — has a constraint without `SOURCE_KEY`, or has a `SOURCE_KEY == "file"` constraint.
  - `pinned_ids(elements: list[Element]) -> set[str]` — user-pinned elements plus groups with an absolutely pinned descendant.
  - `node_size(element) -> tuple[float, float]`
  - `build_scope_graph(diagram, group: Group | None, pinned: set[str]) -> LayoutGraph`

- [ ] **Step 1: Write the failing tests**

`tests/test_layout_graph.py`:

```python
from __future__ import annotations

from diagrams_as_code import Diagram
from diagrams_as_code.layout.graph import (
    LABEL_BELOW_EXTRA,
    build_scope_graph,
    lift,
    node_size,
    pinned_ids,
    scope_children,
)


def _nested() -> tuple[Diagram, dict]:
    d = Diagram()
    with d.group("Outer") as outer:
        with d.group("Inner") as inner:
            a = d.shape("A")
        b = d.shape("B")
    c = d.shape("C")
    a >> c
    a >> c
    b >> a
    return d, {"outer": outer, "inner": inner, "a": a, "b": b, "c": c}


def test_scope_children_in_declaration_order() -> None:
    d, e = _nested()
    assert [x.label for x in scope_children(d, None)] == ["Outer", "C"]
    assert [x.label for x in scope_children(d, e["outer"])] == ["Inner", "B"]


def test_lift_finds_the_direct_child_of_the_scope() -> None:
    d, e = _nested()
    assert lift(e["a"], None) is e["outer"]
    assert lift(e["a"], e["outer"]) is e["inner"]
    assert lift(e["c"], e["outer"]) is None


def test_edges_are_lifted_and_parallel_edges_merge() -> None:
    d, e = _nested()
    root = build_scope_graph(d, None, pinned=set())
    assert [(x.source, x.target, x.weight) for x in root.edges] == [
        (e["outer"].id, e["c"].id, 2)
    ]
    outer = build_scope_graph(d, e["outer"], pinned=set())
    assert [(x.source, x.target, x.weight) for x in outer.edges] == [
        (e["b"].id, e["inner"].id, 1)
    ]


def test_pinned_nodes_and_their_edges_are_excluded() -> None:
    d, e = _nested()
    g = build_scope_graph(d, None, pinned={e["c"].id})
    assert [n.id for n in g.nodes] == [e["outer"].id]
    assert g.edges == ()


def test_pinned_ids_cover_user_constraints_and_absolute_descendants() -> None:
    d = Diagram()
    with d.group("G") as g:
        a = d.shape("A").at(10, 10)
        b = d.shape("B")
    c = d.shape("C").right_of(b)
    ids = pinned_ids(d.solver.all_elements())
    assert ids == {a.id, g.id, c.id}


def test_node_size_reserves_room_for_labels_below() -> None:
    d = Diagram()
    inside = d.shape("In", width=100, height=50)
    icon = d.shape("Icon", width=48, height=48, kind="icon")
    below = d.shape("Below", width=100, height=50, label_position="bottom")
    assert node_size(inside) == (100, 50)
    assert node_size(icon) == (48, 48 + LABEL_BELOW_EXTRA)
    assert node_size(below) == (100, 50 + LABEL_BELOW_EXTRA)
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_layout_graph.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'diagrams_as_code.layout.graph'`.

- [ ] **Step 3a: Create `metrics.py` and use it in the renderer**

```python
"""Text metrics shared by layout and rendering, so spacing and drawing agree."""
from __future__ import annotations

#: Distance from a shape's bottom edge to the baseline of a label drawn below it.
LABEL_BELOW_OFFSET = 14.0

#: Room layout reserves under a shape whose label is drawn below it
#: (offset plus one line of 10-12px text).
LABEL_BELOW_EXTRA = LABEL_BELOW_OFFSET + 10.0
```

In `renderer_svg.py` add `from diagrams_as_code.metrics import LABEL_BELOW_OFFSET` and change exactly the two lines `text_y = b.y + b.height + 14.0` (lines ~296 and ~315) to `text_y = b.y + b.height + LABEL_BELOW_OFFSET`. Leave `icon_y + icon_size + 14.0` (~352) alone: it places a label *inside* a tile. The offset is the same float, so output stays byte-identical.

- [ ] **Step 3: Create `layout/graph.py`**

```python
"""Turn one scope of a diagram (the canvas or a group) into a LayoutGraph.

The diagram is duck-typed: anything with ``solver.elements`` and ``edges``
works, so this module never imports ``diagram``.
"""
from __future__ import annotations

from typing import Any, Optional

from diagrams_as_code.elements import Element
from diagrams_as_code.groups import Group
from diagrams_as_code.layout.base import SOURCE_KEY, LayoutEdge, LayoutGraph, LayoutNode
from diagrams_as_code.metrics import LABEL_BELOW_EXTRA

__all__ = ["LABEL_BELOW_EXTRA", "build_scope_graph", "is_user_pinned", "lift", "node_size", "pinned_ids", "scope_children"]


def scope_children(diagram: Any, group: Optional[Group]) -> list[Element]:
    """Direct children of a scope, in declaration order."""
    if group is None:
        return [e for e in diagram.solver.elements if e.parent is None]
    return list(group.children)


def lift(element: Element, group: Optional[Group]) -> Optional[Element]:
    """The ancestor-or-self of ``element`` that is a direct child of ``group``."""
    current: Optional[Element] = element
    while current is not None:
        if current.parent is group:
            return current
        current = current.parent
    return None


def is_user_pinned(element: Element) -> bool:
    """True if the author (in code or the layout file) positioned ``element``."""
    return any(c.get(SOURCE_KEY) != "auto" for c in element.constraints)


def _has_absolute_descendant(group: Group) -> bool:
    for child in group.children:
        if any(c["type"] == "absolute" and c.get(SOURCE_KEY) != "auto" for c in child.constraints):
            return True
        if isinstance(child, Group) and _has_absolute_descendant(child):
            return True
    return False


def pinned_ids(elements: list[Element]) -> set[str]:
    """Ids that auto-layout must not move."""
    pinned = {e.id for e in elements if is_user_pinned(e)}
    pinned.update(
        e.id for e in elements if isinstance(e, Group) and _has_absolute_descendant(e)
    )
    return pinned


def node_size(element: Element) -> tuple[float, float]:
    """Width and height the element occupies, including a label drawn below it."""
    w, h = element.bounds.width, element.bounds.height
    label_below = getattr(element, "kind", None) == "icon" or getattr(
        element, "label_position", None
    ) in ("bottom", "below")
    return (w, h + LABEL_BELOW_EXTRA) if label_below else (w, h)


def build_scope_graph(diagram: Any, group: Optional[Group], pinned: set[str]) -> LayoutGraph:
    """Unpinned direct children of ``group`` and the edges lifted between them."""
    children = scope_children(diagram, group)
    nodes = tuple(
        LayoutNode(c.id, *node_size(c), index=i)
        for i, c in enumerate(children)
        if c.id not in pinned
    )
    free = {n.id for n in nodes}
    weights: dict[tuple[str, str], int] = {}
    for edge in diagram.edges:
        s, t = lift(edge.source, group), lift(edge.target, group)
        if s is None or t is None or s is t or s.id not in free or t.id not in free:
            continue
        key = (s.id, t.id)
        weights[key] = weights.get(key, 0) + 1
    edges = tuple(LayoutEdge(s, t, w) for (s, t), w in weights.items())
    return LayoutGraph(nodes=nodes, edges=edges)
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/`
Expected: PASS; nothing modified (the renderer change is byte-identical).

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/layout/graph.py src/diagrams_as_code/metrics.py src/diagrams_as_code/renderer_svg.py tests/test_layout_graph.py
git commit -m "feat(layout): build per-scope layout graphs with lifted edges and pins

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: The solve pipeline and `Diagram(layout=...)`

**Files:**
- Create: `src/diagrams_as_code/layout/pipeline.py`
- Create: `tests/test_layout_pipeline.py`
- Modify: `src/diagrams_as_code/diagram.py` (`__init__` signature and attributes, new `configure`, new `all_elements`, `solve` body)
- Modify: `src/diagrams_as_code/layout/__init__.py`

**Interfaces:**
- Consumes: Tasks 4, 6, 7.
- Produces:
  - `pipeline.FRAME_X = 60.0`, `pipeline.FRAME_Y = 80.0`
  - `pipeline.run_layout(diagram) -> None`
  - `Diagram(..., layout: str = "manual", direction: str = "LR", layout_file: str | Path | None = None, rank_gap: float = 80.0, node_gap: float = 40.0)`; attributes of the same names; `diagram.LAYOUT_MODES = ("manual", "auto")`.
  - `Diagram.configure(*, layout=None, direction=None, theme=None, layout_file=None, rank_gap=None, node_gap=None) -> Diagram` — validates; any non-theme argument marks the diagram unsolved so the next render re-solves.
  - `Diagram.all_elements() -> list[Element]`
  - Task 10 will fill `pipeline._apply_layout_file`; in this task it is a stub returning immediately when `diagram.layout_file is None` (it always is until Task 10 wires loading).

- [ ] **Step 1: Write the failing tests**

`tests/test_layout_pipeline.py`:

```python
from __future__ import annotations

import warnings

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.layout import LayoutWarning


def _bounds(d: Diagram) -> dict[str, tuple[float, float, float, float]]:
    return {e.id: (e.bounds.x, e.bounds.y, e.bounds.width, e.bounds.height) for e in d.all_elements()}


def test_manual_is_the_default_and_leaves_unplaced_shapes_alone() -> None:
    with Diagram() as d:
        a = d.shape("A")
    assert d.layout == "manual"
    assert (a.bounds.x, a.bounds.y) == (0.0, 0.0)


def test_auto_chain_flows_left_to_right_from_the_frame_margin() -> None:
    with Diagram(layout="auto") as d:
        a, b, c = d.shape("A"), d.shape("B"), d.shape("C")
        a >> b >> c
    assert (a.bounds.x, a.bounds.y) == (60.0, 80.0)
    assert a.bounds.right < b.bounds.x < b.bounds.right < c.bounds.x
    assert a.bounds.y == b.bounds.y == c.bounds.y


def test_auto_top_to_bottom() -> None:
    with Diagram(layout="auto", direction="TB") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    assert a.bounds.x == b.bounds.x
    assert a.bounds.bottom < b.bounds.y


def test_groups_are_laid_out_inside_then_placed_as_blocks() -> None:
    with Diagram(layout="auto") as d:
        with d.group("Left") as left:
            a1, a2 = d.shape("A1"), d.shape("A2")
            a1 >> a2
        with d.group("Right") as right:
            b1 = d.shape("B1")
        a2 >> b1
    assert left.bounds.right < right.bounds.x
    for child in (a1, a2):
        assert left.bounds.x < child.bounds.x and child.bounds.right < left.bounds.right
    assert a1.bounds.y > left.bounds.y + left.header_height


def test_pinned_shapes_stay_put_and_can_anchor_to_auto_ones() -> None:
    with Diagram(layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        p = d.shape("P").at(900, 600)
        c = d.shape("C").below(b, margin=30, align="left")
        a >> b
    assert (p.bounds.x, p.bounds.y) == (900.0, 600.0)
    assert (c.bounds.x, c.bounds.y) == (b.bounds.x, b.bounds.bottom + 30)


def test_overlap_between_pinned_and_auto_is_warned() -> None:
    with pytest.warns(LayoutWarning, match="'P'.*'A'"):
        with Diagram(layout="auto") as d:
            d.shape("A")
            d.shape("P").at(70, 90)


def test_no_warning_when_nothing_overlaps() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", LayoutWarning)
        with Diagram(layout="auto") as d:
            a, b = d.shape("A"), d.shape("B")
            a >> b


def test_canvas_grows_to_fit_but_never_shrinks() -> None:
    with Diagram(layout="auto", width=400, height=300) as d:
        shapes = [d.shape(f"S{i}") for i in range(8)]
        for s, t in zip(shapes, shapes[1:]):
            s >> t
    assert d.width == shapes[-1].bounds.right + 60.0
    assert d.height == 300.0


def test_solve_is_idempotent() -> None:
    with Diagram(layout="auto") as d:
        with d.group("G"):
            a, b = d.shape("A"), d.shape("B")
            a >> b
        c = d.shape("C").right_of(b)
    first = _bounds(d)
    d.solve()
    assert _bounds(d) == first


def test_configure_switches_layout_and_resolves_on_render() -> None:
    with Diagram() as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    d.configure(layout="auto")
    d.render_svg()
    assert a.bounds.right < b.bounds.x


def test_invalid_layout_options() -> None:
    with pytest.raises(ValueError, match="layout"):
        Diagram(layout="grid")
    with pytest.raises(ValueError, match="direction"):
        Diagram(direction="RL")
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_layout_pipeline.py -q`
Expected: FAIL — `TypeError: Diagram.__init__() got an unexpected keyword argument 'layout'`.

- [ ] **Step 3: Create `layout/pipeline.py`**

```python
"""The ordered steps ``Diagram.solve()`` runs.

1. Restore pre-layout bounds and drop constraints a previous run generated.
2. Apply layout-file entries (Task 10) as leading absolute constraints.
3. With ``layout="auto"``, place unpinned elements scope by scope, deepest
   groups first, as absolute constraints tagged ``SOURCE_KEY: "auto"``.
4. Run the constraint solver (strict).
5. Recompute group bounds bottom-up and frame negative coordinates.
6. With ``layout="auto"``, grow the canvas to fit and warn about pins that
   overlap auto-placed siblings.

With ``layout="manual"`` and no layout file this reproduces the original
``Diagram.solve()`` exactly.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any, Optional

from diagrams_as_code.constraints import ConstraintSolver
from diagrams_as_code.elements import Element
from diagrams_as_code.geometry import Anchor, Point, Rect
from diagrams_as_code.groups import Group
from diagrams_as_code.layout.base import SOURCE_KEY, LayoutWarning
from diagrams_as_code.layout.graph import build_scope_graph, pinned_ids, scope_children
from diagrams_as_code.layout.layered import LayeredLayout

FRAME_X = 60.0
FRAME_Y = 80.0


@dataclass
class _LayoutState:
    """What the first run saw, so later runs start from the same place."""

    bounds: dict[int, tuple[Element, Rect, float, float]] = field(default_factory=dict)
    base_size: tuple[float, float] = (0.0, 0.0)


def run_layout(diagram: Any) -> None:
    """Position every element of ``diagram``."""
    elements = diagram.solver.all_elements()
    _reset(diagram, elements)
    _apply_layout_file(diagram, elements)
    auto_ids: set[str] = set()
    if diagram.layout == "auto":
        auto_ids = _auto_place(diagram, elements)
    diagram.solver.solve()
    groups = _deepest_first(diagram.groups)
    _refresh_group_bounds(groups)
    _frame(elements, groups)
    if diagram.layout == "auto":
        _grow_canvas(diagram, elements)
        _warn_pinned_overlaps(diagram, elements, auto_ids)


def _reset(diagram: Any, elements: list[Element]) -> None:
    state: Optional[_LayoutState] = getattr(diagram, "_layout_state", None)
    if state is None:
        state = _LayoutState(base_size=(diagram.width, diagram.height))
        diagram._layout_state = state
    else:
        diagram.width, diagram.height = state.base_size
    for el in elements:
        saved = state.bounds.get(id(el))
        if saved is None:
            state.bounds[id(el)] = (el, el.bounds, el.width, el.height)
        else:
            _, el.bounds, el.width, el.height = saved
        el.constraints[:] = [c for c in el.constraints if SOURCE_KEY not in c]


def _apply_layout_file(diagram: Any, elements: list[Element]) -> None:
    """Replaced in Task 10."""
    return


def _deepest_first(groups: list[Group]) -> list[Group]:
    def depth(g: Group) -> int:
        d, cur = 0, g.parent
        while cur is not None:
            d, cur = d + 1, cur.parent
        return d

    return sorted(groups, key=depth, reverse=True)


def _auto_constraint(x: float, y: float) -> dict[str, Any]:
    return {"type": "absolute", "x": x, "y": y, "anchor": Anchor.TOP_LEFT, SOURCE_KEY: "auto"}


def _place(diagram: Any, group: Optional[Group], pinned: set[str], engine: LayeredLayout,
           origin: Point) -> set[str]:
    graph = build_scope_graph(diagram, group, pinned)
    positions = engine.arrange(graph)
    for child in scope_children(diagram, group):
        pos = positions.get(child.id)
        if pos is not None:
            child.constraints.append(_auto_constraint(origin.x + pos.x, origin.y + pos.y))
    return set(positions)


def _auto_place(diagram: Any, elements: list[Element]) -> set[str]:
    engine = LayeredLayout(diagram.direction, diagram.rank_gap, diagram.node_gap)
    pinned = pinned_ids(elements)
    placed: set[str] = set()
    for group in _deepest_first(diagram.groups):
        if not group.children:
            continue
        origin = Point(group.padding, group.padding + group.header_height)
        placed |= _place(diagram, group, pinned, engine, origin)
        # Estimate this group's size for its parent scope. The global solve
        # below is authoritative; this one may leave outside references unresolved.
        local = ConstraintSolver()
        local.add(group)
        local.solve(strict=False)
        group.calculate_bounds()
    placed |= _place(diagram, None, pinned, engine, Point(FRAME_X, FRAME_Y))
    return placed


def _refresh_group_bounds(groups: list[Group]) -> None:
    for g in groups:
        if g.is_auto_sized and g.children:
            g.calculate_bounds()


def _frame(elements: list[Element], groups: list[Group]) -> None:
    """Translate the canvas when content has negative coordinates."""
    if not elements:
        return
    roots = [e for e in elements if getattr(e, "parent", None) is None]
    if not roots:
        return
    min_x = min(e.bounds.x for e in roots)
    min_y = min(e.bounds.y for e in roots)
    if min_x < 0.0 or min_y < 0.0:
        offset_x = max(0.0, -min_x + FRAME_X) if min_x < 0.0 else 0.0
        offset_y = max(0.0, -min_y + FRAME_Y) if min_y < 0.0 else 0.0
        for r in roots:
            r.translate(offset_x, offset_y)
        _refresh_group_bounds(groups)


def _grow_canvas(diagram: Any, elements: list[Element]) -> None:
    roots = [e for e in elements if e.parent is None]
    if not roots:
        return
    right = max(e.bounds.right for e in roots)
    bottom = max(e.bounds.bottom for e in roots)
    diagram.width = max(diagram.width, right + FRAME_X)
    diagram.height = max(diagram.height, bottom + FRAME_X)


def _warn_pinned_overlaps(diagram: Any, elements: list[Element], auto_ids: set[str]) -> None:
    scopes: list[Optional[Group]] = [None, *[e for e in elements if isinstance(e, Group)]]
    for scope in scopes:
        siblings = scope_children(diagram, scope)
        auto = [s for s in siblings if s.id in auto_ids]
        fixed = [s for s in siblings if s.id not in auto_ids]
        for p in fixed:
            for a in auto:
                if p.bounds.intersects(a.bounds):
                    warnings.warn(
                        LayoutWarning(
                            f"pinned {p.label!r} overlaps auto-placed {a.label!r}; "
                            "move the pin or give both explicit positions"
                        ),
                        stacklevel=4,
                    )
```

Note: `_frame` is the original framing code from `Diagram.solve()`, moved unchanged apart from using `FRAME_X`/`FRAME_Y` (both equal the literals 60.0 and 80.0 it used).

- [ ] **Step 4: Wire `Diagram`**

In `diagram.py`: add `from diagrams_as_code.layout.layered import DIRECTIONS` and `from diagrams_as_code.layout.pipeline import run_layout`. Add a class attribute `LAYOUT_MODES = ("manual", "auto")`. Extend `__init__`'s signature after `label_position: str = "inside",`:

```python
        layout: str = "manual",
        direction: str = "LR",
        layout_file: Optional[Union[str, Path]] = None,
        rank_gap: float = 80.0,
        node_gap: float = 40.0,
```

and at the end of `__init__`:

```python
        self.layout = "manual"
        self.direction = "LR"
        self.layout_file: Optional[Path] = None
        self.rank_gap = 80.0
        self.node_gap = 40.0
        self.configure(
            layout=layout,
            direction=direction,
            layout_file=layout_file,
            rank_gap=rank_gap,
            node_gap=node_gap,
        )
```

Add methods:

```python
    def configure(
        self,
        *,
        layout: Optional[str] = None,
        direction: Optional[str] = None,
        theme: Optional[Union[Theme, str]] = None,
        layout_file: Optional[Union[str, Path]] = None,
        rank_gap: Optional[float] = None,
        node_gap: Optional[float] = None,
    ) -> Diagram:
        """Change layout or theme settings; layout changes re-solve on next render."""
        if layout is not None and layout not in self.LAYOUT_MODES:
            raise ValueError(f"layout must be one of {self.LAYOUT_MODES}, got {layout!r}")
        if direction is not None and direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, got {direction!r}")
        for name, gap in (("rank_gap", rank_gap), ("node_gap", node_gap)):
            if gap is not None and gap < 0:
                raise ValueError(f"{name} must be non-negative, got {gap}")
        if theme is not None:
            self.theme = get_theme(theme)
        changes = {
            "layout": layout,
            "direction": direction,
            "layout_file": Path(layout_file) if layout_file is not None else None,
            "rank_gap": float(rank_gap) if rank_gap is not None else None,
            "node_gap": float(node_gap) if node_gap is not None else None,
        }
        for name, value in changes.items():
            if value is not None:
                setattr(self, name, value)
                self._is_solved = False
        return self

    def all_elements(self) -> list[Element]:
        """Every shape and group, groups before their children, in declaration order."""
        return self.solver.all_elements()
```

Check `get_theme` accepts a `Theme` instance (`Diagram.__init__` already passes `theme: Union[Theme, str]` to it); if it does not, use `self.theme = theme if isinstance(theme, Theme) else get_theme(theme)`.

Replace the body of `solve` entirely:

```python
    def solve(self) -> None:
        """Place every element: auto-layout, layout file, constraints, framing."""
        run_layout(self)
        self._is_solved = True
```

- [ ] **Step 5: Export from `layout/__init__.py`**

Add `from diagrams_as_code.layout.pipeline import run_layout` and `"run_layout"` to `__all__`.

- [ ] **Step 6: Run everything and the output guard**

Run: `uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/`
Expected: all pass; nothing modified (manual path is byte-identical).

- [ ] **Step 7: Commit**

```bash
git add src/diagrams_as_code/layout src/diagrams_as_code/diagram.py tests/test_layout_pipeline.py
git commit -m "feat(layout): auto-layout option mixing with pinned and relative placement

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 9: Route edges in the layout stage

**Files:**
- Modify: `src/diagrams_as_code/layout/pipeline.py` (new last step)
- Modify: `src/diagrams_as_code/renderer_svg.py` (`render` signature; line ~165 `pts = self.router.route(e)`)
- Modify: `src/diagrams_as_code/diagram.py` (`__init__` attribute, `render_svg`)
- Test: `tests/test_layout_routes.py` (create)

**Interfaces:**
- Consumes: `run_layout` (Task 8), `OrthogonalRouter.route(edge) -> list[Point]`.
- Produces: `Diagram.routes: dict[int, list[Point]]` keyed by `id(edge)`, filled by `run_layout` for every edge in `diagram.edges`; `SVGRenderer.render(..., routes: Optional[Mapping[int, list[Point]]] = None)` — when given, the renderer draws those paths and never calls the router; when `None` (direct callers, existing tests) it routes as before.

- [ ] **Step 1: Write the failing tests**

`tests/test_layout_routes.py`:

```python
from __future__ import annotations

from diagrams_as_code import Diagram, SVGRenderer
from diagrams_as_code.router import OrthogonalRouter


def _diag() -> Diagram:
    with Diagram(layout="auto") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    return d


def test_solve_routes_every_edge() -> None:
    d = _diag()
    (edge,) = d.edges
    assert d.routes[id(edge)] == OrthogonalRouter().route(edge)


def test_renderer_uses_given_routes_without_calling_the_router(monkeypatch) -> None:
    d = _diag()

    def fail(self, edge):
        raise AssertionError("renderer must not route when routes are given")

    monkeypatch.setattr(OrthogonalRouter, "route", fail)
    svg = SVGRenderer(d.theme).render(
        elements=d.shapes, groups=d.groups, edges=d.edges,
        width=d.width, height=d.height, routes=d.routes,
    )
    assert "<path" in svg


def test_renderer_still_routes_when_no_routes_are_given() -> None:
    d = _diag()
    svg = SVGRenderer(d.theme).render(elements=d.shapes, groups=d.groups, edges=d.edges, width=d.width, height=d.height)
    assert "<path" in svg
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_layout_routes.py -q`
Expected: FAIL — `AttributeError: 'Diagram' object has no attribute 'routes'`.

- [ ] **Step 3: Implement**

`layout/pipeline.py`: add `from diagrams_as_code.router import OrthogonalRouter` (layer 3, below `layout`), and as the last statement of `run_layout`:

```python
    router = OrthogonalRouter()
    diagram.routes = {id(edge): router.route(edge) for edge in diagram.edges}
```

Add "7. Route every edge; the renderer draws these paths." to the module docstring's step list.

`diagram.py`, in `__init__` next to `self.edges`: `self.routes: dict[int, list[Point]] = {}` (import `Point` from `geometry`). In `render_svg`, pass `routes=self.routes` to `renderer.render(...)`.

`renderer_svg.py`: add `routes: Optional[Mapping[int, list[Point]]] = None` as the last parameter of `render` (import `Mapping` from `typing`, `Point` from `geometry`), and replace line ~165:

```python
            pts = routes[id(e)] if routes is not None and id(e) in routes else self.router.route(e)
```

- [ ] **Step 4: Verify**

Run: `uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/`
Expected: all pass; nothing modified (same router, same inputs, same paths).

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/layout/pipeline.py src/diagrams_as_code/renderer_svg.py src/diagrams_as_code/diagram.py tests/test_layout_routes.py
git commit -m "refactor: route edges in the layout stage; the renderer only draws

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 10: The layout file (sidecar)

**Files:**
- Create: `src/diagrams_as_code/layout/sidecar.py`
- Create: `tests/test_layout_sidecar.py`
- Modify: `src/diagrams_as_code/layout/pipeline.py` (`_apply_layout_file`)
- Modify: `src/diagrams_as_code/layout/__init__.py`

**Interfaces:**
- Consumes: `SOURCE_KEY`, `LayoutWarning` (Task 6); `Diagram.all_elements()`, `Diagram.layout_file`, `Diagram.solve()` (Task 8).
- Produces:
  - `LAYOUT_FILE_VERSION = 1`
  - `element_key(element) -> str`
  - `keyed_elements(elements) -> dict[str, list[Element]]`
  - `load_layout_file(path: str | Path) -> dict[str, tuple[float, float]]` (missing file → `{}`)
  - `apply_entries(elements, entries) -> None`
  - `export_layout(diagram, path: str | Path) -> Path`

- [ ] **Step 1: Write the failing tests**

`tests/test_layout_sidecar.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.layout import LayoutWarning, export_layout, load_layout_file
from diagrams_as_code.layout.sidecar import element_key


def _build(layout_file=None) -> Diagram:
    with Diagram(layout="auto", layout_file=layout_file) as d:
        with d.group("Cloud") as g:
            broker = d.shape("Broker")
            db = d.shape("DB", id="tsdb")
            broker >> db
        edge = d.shape("Edge")
        edge >> broker
    return d


def _positions(d: Diagram) -> dict[str, tuple[float, float]]:
    return {element_key(e): (e.bounds.x, e.bounds.y) for e in d.all_elements()}


def test_keys_are_label_paths_unless_the_id_was_explicit() -> None:
    d = _build()
    assert sorted(_positions(d)) == ["Cloud", "Cloud/Broker", "Edge", "tsdb"]


def test_export_format_is_stable(tmp_path: Path) -> None:
    path = export_layout(_build(), tmp_path / "x.layout.json")
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    assert data["version"] == 1
    assert list(data["positions"]) == sorted(data["positions"])
    assert text.endswith("}\n") and '\n  "positions"' in text


def test_round_trip_reproduces_every_position(tmp_path: Path) -> None:
    original = _build()
    path = export_layout(original, tmp_path / "l.json")
    assert _positions(_build(layout_file=path)) == _positions(original)


def test_editing_a_shape_entry_moves_that_shape(tmp_path: Path) -> None:
    path = export_layout(_build(), tmp_path / "l.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["positions"]["Edge"] = {"x": 700.0, "y": 500.0}
    path.write_text(json.dumps(data), encoding="utf-8")
    assert _positions(_build(layout_file=path))["Edge"] == (700.0, 500.0)


def test_editing_a_group_entry_moves_the_whole_group(tmp_path: Path) -> None:
    before = _positions(_build())
    path = export_layout(_build(), tmp_path / "l.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    gx, gy = before["Cloud"]
    data["positions"]["Cloud"] = {"x": gx + 100.0, "y": gy + 50.0}
    path.write_text(json.dumps(data), encoding="utf-8")
    after = _positions(_build(layout_file=path))
    for key in ("Cloud", "Cloud/Broker", "tsdb"):
        assert after[key] == (before[key][0] + 100.0, before[key][1] + 50.0)
    assert after["Edge"] == before["Edge"]


def test_missing_file_is_a_no_op(tmp_path: Path) -> None:
    assert load_layout_file(tmp_path / "absent.json") == {}
    assert _positions(_build(layout_file=tmp_path / "absent.json")) == _positions(_build())


def test_stale_entry_warns(tmp_path: Path) -> None:
    path = tmp_path / "l.json"
    path.write_text(json.dumps({"version": 1, "positions": {"Gone": {"x": 1, "y": 2}}}), encoding="utf-8")
    with pytest.warns(LayoutWarning, match="stale layout entry: 'Gone'"):
        _build(layout_file=path)


@pytest.mark.parametrize(
    "content, match",
    [
        ("{not json", "invalid JSON"),
        ('{"version": 2, "positions": {}}', "version"),
        ('{"version": 1, "positions": {"Edge": {"x": "a", "y": 1}}}', "Edge"),
    ],
)
def test_malformed_files_name_the_problem(tmp_path: Path, content: str, match: str) -> None:
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        load_layout_file(path)


def test_duplicate_keys_block_export(tmp_path: Path) -> None:
    with Diagram(layout="auto") as d:
        d.shape("Server")
        d.shape("Server")
    with pytest.raises(ValueError, match="'Server'.*id="):
        export_layout(d, tmp_path / "l.json")
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_layout_sidecar.py -q`
Expected: FAIL — `ImportError: cannot import name 'export_layout'`.

- [ ] **Step 3: Create `layout/sidecar.py`**

```python
"""The editable layout file: absolute positions keyed by a stable name.

A key is the element's explicit ``id=`` when one was given, else its label
path (ancestor group labels and its own label joined by ``/``). Counter ids
such as ``shape_3`` are never used: adding a shape would renumber them.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any, Union

from diagrams_as_code.elements import Element
from diagrams_as_code.geometry import Anchor
from diagrams_as_code.layout.base import SOURCE_KEY, LayoutWarning

LAYOUT_FILE_VERSION = 1


def element_key(element: Element) -> str:
    """The layout-file key for ``element``."""
    if element.explicit_id:
        return element.id
    parts: list[str] = []
    current: Any = element
    while current is not None:
        parts.append(current.label)
        current = current.parent
    return "/".join(reversed(parts))


def keyed_elements(elements: list[Element]) -> dict[str, list[Element]]:
    """Group elements by key; more than one element per key is ambiguous."""
    keyed: dict[str, list[Element]] = {}
    for el in elements:
        keyed.setdefault(element_key(el), []).append(el)
    return keyed


def load_layout_file(path: Union[str, Path]) -> dict[str, tuple[float, float]]:
    """Read a layout file; a missing file means no overrides."""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{p}: invalid JSON: {exc}") from exc
    version = data.get("version") if isinstance(data, dict) else None
    if version != LAYOUT_FILE_VERSION:
        raise ValueError(
            f"{p}: unsupported layout file version {version!r}; expected {LAYOUT_FILE_VERSION}"
        )
    positions = data.get("positions", {})
    if not isinstance(positions, dict):
        raise ValueError(f"{p}: 'positions' must be an object")
    entries: dict[str, tuple[float, float]] = {}
    for key, pos in positions.items():
        try:
            entries[key] = (float(pos["x"]), float(pos["y"]))
        except (TypeError, KeyError, ValueError) as exc:
            raise ValueError(f"{p}: entry {key!r} needs numeric 'x' and 'y'") from exc
    return entries


def apply_entries(elements: list[Element], entries: dict[str, tuple[float, float]]) -> None:
    """Put each entry first in its element's constraints so it wins."""
    keyed = keyed_elements(elements)
    for key in sorted(entries):
        matches = keyed.get(key, [])
        if not matches:
            warnings.warn(LayoutWarning(f"stale layout entry: {key!r} matches no element"), stacklevel=5)
            continue
        if len(matches) > 1:
            raise ValueError(
                f"layout entry {key!r} matches {len(matches)} elements; give them explicit id= values"
            )
        x, y = entries[key]
        matches[0].constraints.insert(
            0, {"type": "absolute", "x": x, "y": y, "anchor": Anchor.TOP_LEFT, SOURCE_KEY: "file"}
        )


def export_layout(diagram: Any, path: Union[str, Path]) -> Path:
    """Solve ``diagram`` and write every element's top-left corner to ``path``."""
    if not diagram._is_solved:
        diagram.solve()
    keyed = keyed_elements(diagram.all_elements())
    duplicates = {k: [e.id for e in v] for k, v in sorted(keyed.items()) if len(v) > 1}
    if duplicates:
        listed = "; ".join(f"{k!r} -> {ids}" for k, ids in duplicates.items())
        raise ValueError(f"layout keys are ambiguous: {listed}. Give these elements explicit id= values")
    positions = {
        key: {"x": els[0].bounds.x, "y": els[0].bounds.y} for key, els in sorted(keyed.items())
    }
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps({"version": LAYOUT_FILE_VERSION, "positions": positions}, indent=2, sort_keys=True)
    p.write_text(text + "\n", encoding="utf-8")
    return p
```

- [ ] **Step 4: Wire it into the pipeline**

In `layout/pipeline.py` add `from diagrams_as_code.layout.sidecar import apply_entries, load_layout_file` and replace the stub:

```python
def _apply_layout_file(diagram: Any, elements: list[Element]) -> None:
    if diagram.layout_file is not None:
        apply_entries(elements, load_layout_file(diagram.layout_file))
```

In `layout/__init__.py` add `from diagrams_as_code.layout.sidecar import export_layout, load_layout_file` and both names to `__all__`.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/`
Expected: all pass; nothing modified. If the stale-warning test's `match` fails because the warning is attributed elsewhere, the message text is what matters — do not loosen the regex, fix `stacklevel` only if pytest cannot capture it (it captures regardless of `stacklevel`).

- [ ] **Step 6: Commit**

```bash
git add src/diagrams_as_code/layout tests/test_layout_sidecar.py
git commit -m "feat(layout): editable layout file with stable keys and round-trip export

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 11: The `diagrams-as-code` CLI

**Files:**
- Create: `src/diagrams_as_code/cli.py`, `src/diagrams_as_code/__main__.py`
- Create: `tests/test_cli.py`
- Modify: `pyproject.toml` (add `[project.scripts]`)

**Interfaces:**
- Consumes: `output.render_all`, `output.FORMATS` (Task 5); `Diagram.configure` (Task 8); `export_layout` (Task 10); `list_themes`; `ShapeLibrary._ICON_CATALOG`.
- Produces: `cli.main(argv: list[str] | None = None) -> int`; `cli.load_script(path: Path) -> Diagram`; `cli.discover(paths: list[Path]) -> list[tuple[Path, Path]]` (script, output subdirectory relative to `--out`).

- [ ] **Step 1: Write the failing tests**

`tests/test_cli.py`:

```python
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from diagrams_as_code.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent

GOOD = '''
from diagrams_as_code import Diagram

OUTPUT_STEM = "{stem}"


def diagram() -> Diagram:
    with Diagram("Demo") as d:
        a, b = d.shape("A"), d.shape("B")
        a >> b
    return d
'''


def _script(path: Path, stem: str = "demo") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(GOOD.format(stem=stem), encoding="utf-8")
    return path


def test_render_one_script_defaults_to_svg_and_bom(tmp_path: Path, capsys) -> None:
    script = _script(tmp_path / "src" / "x.py")
    assert main(["render", str(script), "--out", str(tmp_path / "out")]) == 0
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["demo.svg", "demo_README.md"]
    assert "demo.svg" in capsys.readouterr().out


def test_flags_override_the_script(tmp_path: Path) -> None:
    script = _script(tmp_path / "x.py")
    out = tmp_path / "out"
    assert main(["render", str(script), "--out", str(out), "--layout", "auto", "--theme", "nord", "--format", "svg"]) == 0
    svg = (out / "demo.svg").read_text(encoding="utf-8")
    assert 'x="60.0" y="80.0"' in svg or 'x="60" y="80"' in svg


def test_directory_input_mirrors_subdirectories(tmp_path: Path) -> None:
    _script(tmp_path / "gallery" / "cloud" / "one.py", stem="one")
    (tmp_path / "gallery" / "helpers.py").write_text("X = 1\n", encoding="utf-8")
    assert main(["render", str(tmp_path / "gallery"), "--out", str(tmp_path / "out"), "--format", "svg"]) == 0
    assert (tmp_path / "out" / "cloud" / "one.svg").exists()
    assert not (tmp_path / "out" / "helpers.svg").exists()


def test_failing_script_returns_1_and_others_still_render(tmp_path: Path, capsys) -> None:
    bad = tmp_path / "a_bad.py"
    bad.write_text("def diagram():\n    raise RuntimeError('boom')\n", encoding="utf-8")
    good = _script(tmp_path / "b_good.py")
    assert main(["render", str(bad), str(good), "--out", str(tmp_path / "out"), "--format", "svg"]) == 1
    err = capsys.readouterr().err
    assert f"error: {bad}: boom" in err and "Traceback" not in err
    assert (tmp_path / "out" / "demo.svg").exists()


def test_debug_shows_the_traceback(tmp_path: Path, capsys) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def diagram():\n    raise RuntimeError('boom')\n", encoding="utf-8")
    assert main(["render", str(bad), "--out", str(tmp_path), "--debug"]) == 1
    assert "Traceback" in capsys.readouterr().err


def test_script_without_diagram_function(tmp_path: Path, capsys) -> None:
    s = tmp_path / "nothing.py"
    s.write_text("X = 1\n", encoding="utf-8")
    assert main(["render", str(s), "--out", str(tmp_path)]) == 1
    assert "defines no diagram() function" in capsys.readouterr().err


def test_usage_errors_return_2(capsys) -> None:
    assert main(["render"]) == 2
    assert main(["render", "x.py", "--layout", "grid"]) == 2
    assert main(["no-such-command"]) == 2


def test_layout_export(tmp_path: Path) -> None:
    script = _script(tmp_path / "x.py")
    assert main(["layout", "export", str(script), "--layout", "auto"]) == 0
    data = json.loads((tmp_path / "x.layout.json").read_text(encoding="utf-8"))
    assert sorted(data["positions"]) == ["A", "B"]


def test_themes_and_icons(capsys) -> None:
    assert main(["themes"]) == 0
    assert "nord" in capsys.readouterr().out.split()
    assert main(["icons", "--domain", "iiot"]) == 0
    out = capsys.readouterr().out
    assert "sensor" in out and "kubernetes" not in out


def test_module_entry_point_runs() -> None:
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
    res = subprocess.run([sys.executable, "-m", "diagrams_as_code", "themes"], capture_output=True, text=True, env=env)
    assert res.returncode == 0 and "nord" in res.stdout
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_cli.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'diagrams_as_code.cli'`.

- [ ] **Step 3: Create `cli.py`**

```python
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
```

Check the `_ICON_CATALOG` value shape before relying on it: `uv run python -c "from diagrams_as_code.shapes import ShapeLibrary as S; print(next(iter(S._ICON_CATALOG.items())))"` must print `(name, (domain, description))`. If the tuple order differs, swap the unpacking in `_icons`.

`__main__.py`:

```python
"""``python -m diagrams_as_code``."""
import sys

from diagrams_as_code.cli import main

sys.exit(main())
```

`pyproject.toml`, after the `dependencies = []` line:

```toml

[project.scripts]
diagrams-as-code = "diagrams_as_code.cli:main"
```

Then `uv sync` so the console script is installed.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_cli.py tests/test_module_boundaries.py -q && uv run diagrams-as-code themes | head -3`
Expected: PASS; three theme names printed.

- [ ] **Step 5: Reproduce the gallery through the CLI**

Run: `uv run diagrams-as-code render examples --out output --format svg,png,bom > /dev/null && git status --porcelain -- output/`
Expected: exit 0 and no modified tracked files — the CLI writes the same bytes the scripts do. (`main.py` is not under `examples/`; `uv run diagrams-as-code render main.py --out output --format svg,png` also leaves `output/` clean, but its BOM is named `main_architecture_README.md` via the CLI, so skip `bom` for it or delete that stray file.)

- [ ] **Step 6: Run the full suite and commit**

```bash
uv run pytest -q && git status --porcelain -- output/ icons/ README.md docs/
git add src/diagrams_as_code/cli.py src/diagrams_as_code/__main__.py tests/test_cli.py pyproject.toml uv.lock
git commit -m "feat(cli): add the diagrams-as-code command

render, layout export, themes and icons. Scripts provide diagram();
exit codes 0/1/2; errors go to stderr without a traceback unless --debug.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 12: Auto-layout gallery examples, docs and manifests

**Files:**
- Create: 8 files `examples/<domain>/11_auto_<name>.py`
- Create (generated by the test suite): `output/<domain>/11_auto_<name>.svg` and `_README.md` (PNGs are gitignored)
- Modify: `tests/test_domain_examples.py` (count 80→88, 10→11, docstring)
- Modify: `docs/how-to.md`, `docs/running.md`, `docs/architecture.md`, `README.md`, `docs/CHANGELOG.md`, `docs/CAPABILITIES.md`, `docs/capabilities.json`, `examples/README.md`, any doc stating "80" example diagrams

**Interfaces:**
- Consumes: everything above. Each new example follows the Task 5 contract (`diagram()` + `build_diagram(output_dir)`), and uses `layout="auto"` with **no** `.at()` / relative placement calls.

- [ ] **Step 1: Update the discovery test first (red)**

In `tests/test_domain_examples.py`: module docstring → `"""Test suite executing and verifying all 88 domain example diagram scripts across 8 domains."""`; `test_example_script_discovery` docstring → `"""Verify that exactly 88 example scripts exist across 8 domains."""`, `assert len(EXAMPLE_SCRIPTS) == 88`, and `assert count == 11, f"Domain {d} has {count} scripts, expected 11."`.

Run: `uv run pytest tests/test_domain_examples.py::test_example_script_discovery -q`
Expected: FAIL — `assert 80 == 88`.

- [ ] **Step 2: Write the 8 examples**

Every file uses this template; only the docstring, default output dir, `Diagram(...)` arguments and the body differ. Template (cloud):

```python
"""Example architecture: Auto-Laid-Out Serverless Pipeline (CLOUD domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Serverless Pipeline", theme="nord", layout="auto") as diag:
        with diag.group("Ingress") as ingress:
            client = diag.shape("Client", icon="mobile")
            gw = diag.shape("API Gateway", icon="api_gateway")
        with diag.group("Compute") as compute:
            fn_a = diag.shape("Order Function", icon="server")
            fn_b = diag.shape("Billing Function", icon="server")
        with diag.group("Data") as data:
            queue = diag.shape("Event Queue", icon="queue")
            db = diag.shape("Orders DB", icon="database")

        client >> diag.edge("HTTPS") >> gw
        gw >> diag.edge("invoke") >> fn_a
        gw >> diag.edge("invoke") >> fn_b
        fn_a >> diag.edge("publish") >> queue
        fn_b >> diag.edge("write") >> db
        queue >> diag.edge("consume") >> fn_b

    return diag


def build_diagram(output_dir: Path | str = "output/cloud") -> Path:
    return render_all(diagram(), output_dir, "11_auto_serverless_pipeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/cloud")
    build_diagram(dest)
```

The other seven — same template, with these values (file name → title, theme, direction; body):

1. `examples/ai/11_auto_training_pipeline.py` — "Auto-Laid-Out Training Pipeline", `theme="dracula"`, default LR. Groups: "Data" (`Raw Lake` icon `database`, `Feature Store` icon `database`), "Training" (`Trainer` icon `gpu`, `Experiment Tracker` icon `dashboard`), "Serving" (`Model Registry` icon `database`, `Inference API` icon `api_gateway`). Edges: Raw Lake→Feature Store "ETL", Feature Store→Trainer "features", Trainer→Experiment Tracker "metrics", Trainer→Model Registry "register", Model Registry→Inference API "deploy".
2. `examples/computer/11_auto_workstation_stack.py` — "Auto-Laid-Out Workstation Stack", `theme="solarized_light"`, `direction="TB"`. Ungrouped shapes: `Applications` icon `laptop`, `Runtime` icon `server`, `Kernel` icon `cpu`, `Drivers` icon `cpu`, `Hardware` icon `server`. Edges: Applications→Runtime "syscalls", Runtime→Kernel "ABI", Kernel→Drivers "I/O", Drivers→Hardware "MMIO".
3. `examples/datacenter/11_auto_spine_leaf.py` — "Auto-Laid-Out Spine-Leaf Fabric", `theme="blueprint"`, `direction="TB"`. Group "Spine" (`Spine 1`, `Spine 2`, icon `switch`); group "Leaf" (`Leaf 1`, `Leaf 2`, `Leaf 3`, icon `switch`); group "Racks" (`Rack A`, `Rack B`, `Rack C`, icon `server`). Edges: each spine → each leaf (label "40G"), Leaf n → Rack n ("10G").
4. `examples/business_process/11_auto_order_to_cash.py` — "Auto-Laid-Out Order to Cash", `theme="pastel_light"`, LR. Ungrouped: `Order Received`, `Credit Check` (kind `diamond`), `Fulfil Order`, `Invoice`, `Payment Received`, `Collections`. Edges: Order Received→Credit Check, Credit Check→Fulfil Order "approved", Credit Check→Collections "rejected", Fulfil Order→Invoice, Invoice→Payment Received, Invoice→Collections "overdue".
5. `examples/cybersecurity/11_auto_soc_pipeline.py` — "Auto-Laid-Out SOC Detection Pipeline", `theme="cyber_slate"`, LR. Groups: "Sources" (`Endpoints` icon `laptop`, `Firewalls` icon `firewall`), "SIEM" (`Log Collector` icon `server`, `Correlation Engine` icon `shield`), "Response" (`SOAR` icon `server`, `Analyst Console` icon `dashboard`). Edges: Endpoints→Log Collector "EDR", Firewalls→Log Collector "syslog", Log Collector→Correlation Engine "normalize", Correlation Engine→SOAR "alert", SOAR→Analyst Console "case".
6. `examples/network_engineering/11_auto_campus_core.py` — "Auto-Laid-Out Campus Core", `theme="emerald"`, `direction="TB"`. Ungrouped: `Internet` icon `cloud`, `Edge Router` icon `router`, `Core Switch` icon `switch`, `Distribution A` icon `switch`, `Distribution B` icon `switch`, `Access A` icon `switch`, `Access B` icon `switch`. Edges: Internet→Edge Router "BGP", Edge Router→Core Switch, Core Switch→Distribution A, Core Switch→Distribution B, Distribution A→Access A, Distribution B→Access B.
7. `examples/iiot/11_auto_uns_backbone.py` — "Auto-Laid-Out UNS Backbone", `theme="iiot_dark_gold"`, LR. Groups: "Plant Floor" (`PLC` icon `plc`, `Sensor Array` icon `sensor`), "Edge" (`Edge Gateway` icon `gateway`), "Enterprise" (`MQTT Broker` icon `broker`, `Historian` icon `database`, `Dashboard` icon `dashboard`). Edges: PLC→Edge Gateway "OPC UA", Sensor Array→Edge Gateway "Modbus", Edge Gateway→MQTT Broker "Sparkplug B", MQTT Broker→Historian "ingest", MQTT Broker→Dashboard "subscribe".

Before writing, confirm every icon name exists: `uv run diagrams-as-code icons | cut -f1 | grep -xE 'mobile|api_gateway|server|queue|database|gpu|dashboard|laptop|cpu|switch|firewall|shield|cloud|router|plc|sensor|gateway|broker'` must print all 18 names. Replace any missing one with the nearest listed icon from the same domain.

- [ ] **Step 3: Render and check for layout warnings**

Run: `for f in examples/*/11_auto_*.py; do uv run python -W error::UserWarning "$f" || echo "FAIL $f"; done`
Expected: no `FAIL` lines (auto-only diagrams have no pins, so no `LayoutWarning`). Open two SVGs and look at them (e.g. `xdg-open output/iiot/11_auto_uns_backbone.svg`); groups must not overlap and edges must connect the right shapes.

- [ ] **Step 4: Run the suite**

Run: `uv run pytest -q`
Expected: all pass, including `test_domain_theme_variety`. `git status --porcelain -- output/` shows only the 16 **new** (`??`) files — no `M` lines.

- [ ] **Step 5: Update the docs**

- `docs/running.md` §3.3: retitle to "Batch Regenerate the Gallery" and replace the Python one-liner with:

  ```bash
  uv run diagrams-as-code render examples --out output --format svg,png,bom
  ```

  Add a §3.4 "The `diagrams-as-code` Command" listing `render`, `layout export`, `themes`, `icons`, their flags, the default formats (`svg,bom`, and why), and exit codes 0/1/2.
- `docs/how-to.md`: add "Let the Engine Lay Out a Diagram" — a `layout="auto"` example, `direction`, pinning with `.at()` and anchoring with `.right_of()` to an auto-placed shape, the `LayoutWarning` on pinned overlap, and the layout file workflow: `diagrams-as-code layout export my_diagram.py`, edit `my_diagram.layout.json`, render with `--layout-file my_diagram.layout.json` or `Diagram(layout_file=...)`; how keys are formed and when to add `id=`; group entries move the whole group.
- `docs/architecture.md`: in §1's pipeline diagram insert a "Layout Pipeline (manual / auto / layout file)" box between the object model and the constraint solver; add §2.9 "Layout (`diagrams_as_code.layout`)" describing base/graph/layered/sidecar/pipeline; add `context.py`, `rasterize.py`, `icon_glyphs.py`, `output.py`, `cli.py`, `layout/` to the §4 source tree; add an invariant "Layered imports: enforced by `tests/test_module_boundaries.py`".
- `README.md`: add a quick-start snippet showing `layout="auto"` and `uv run diagrams-as-code render …`.
- Replace "80" example-count claims with "88" where they describe the gallery: `grep -rn "80 " README.md docs/*.md examples/README.md | grep -iE "diagram|example|architect"`; leave `CHANGELOG.md` released sections untouched. Add the 8 new examples to `examples/README.md`'s tables.
- `docs/CHANGELOG.md`: add at the top, above `## [v0.3.0]`:

  ```markdown
  ## [Unreleased]

  ### Added
  - **Auto-layout (`Diagram(layout="auto")`):** a deterministic layered engine places unpinned shapes and groups from the edge structure, left-to-right or top-to-bottom. Shapes placed with `.at()` or `.right_of()` stay pinned, relative placement can target auto-placed shapes, and a `LayoutWarning` names any pin that overlaps an auto-placed sibling.
  - **Layout file:** `diagrams-as-code layout export` writes every position to a JSON file keyed by label path or explicit `id=`; hand edits are applied as overrides on the next render, and a group entry moves the whole group.
  - **`diagrams-as-code` command:** `render`, `layout export`, `themes`, `icons`; also `python -m diagrams_as_code`.
  - **8 auto-layout gallery examples** (`examples/<domain>/11_auto_*.py`), bringing the gallery to 88.

  ### Changed
  - Scripts define `diagram() -> Diagram`; files are written by `output.render_all`. Existing `build_diagram()` functions keep working.
  - Internals split for modularity: PNG backends in `rasterize.py`, icon glyphs in `icon_glyphs.py`, the active-diagram stack in `context.py`, label metrics in `metrics.py`, and the solve pipeline in `layout/pipeline.py`, which now also routes edges so the renderer only draws. `tests/test_module_boundaries.py` enforces import direction. Rendered output of all existing diagrams is byte-identical.
  - `Diagram.render_png()` returns the PNG bytes for every backend (CairoSVG previously returned `None`).
  ```

- `docs/CAPABILITIES.md` and `docs/capabilities.json`: add `CAP-DIAG-LAYOUT` (Python API `diagrams_as_code.layout`, classes `LayeredLayout`, `LayoutWarning`; verification `uv run pytest tests/test_layout_layered.py tests/test_layout_graph.py tests/test_layout_pipeline.py tests/test_layout_sidecar.py`) and `CAP-DIAG-CLI` (entrypoint `diagrams-as-code`; verification `uv run pytest tests/test_cli.py`), both `OPERATIONAL`, target `v0.4.0`. In the JSON, bump `total_capabilities` 10→12 and `operational` 9→11, and update the domains entry to 88 diagrams. Add an "Is there auto-layout?" row to the quick-answers table.

- [ ] **Step 6: Final verification**

Run: `uv run pytest -q && uv run python tools/generate_icons.py --check && uv run python -c "import json; json.load(open('docs/capabilities.json'))" && git status --porcelain`
Expected: all pass; the only changes are this task's files.

- [ ] **Step 7: Commit**

```bash
git add examples tests/test_domain_examples.py output README.md docs
git commit -m "feat: auto-layout gallery examples, CLI and layout docs

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```
