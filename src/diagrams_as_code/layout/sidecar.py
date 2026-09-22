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
