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
