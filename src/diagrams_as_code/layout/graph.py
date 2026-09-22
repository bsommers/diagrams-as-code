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
