"""The ordered steps ``Diagram.solve()`` runs.

1. Restore pre-layout bounds and drop constraints a previous run generated.
2. Apply layout-file entries (Task 10) as leading absolute constraints.
3. With ``layout="auto"``, place unpinned elements scope by scope, deepest
   groups first, as absolute constraints tagged ``SOURCE_KEY: "auto"``.
4. Run the constraint solver (strict).
5. Recompute group bounds bottom-up and frame negative coordinates.
6. Grow the canvas to fit when auto-layout ran or a layout file supplied a
   position, and with ``layout="auto"`` warn about pins that overlap
   auto-placed siblings.
7. Route every edge; the renderer draws these paths.

With ``layout="manual"`` and no layout file this reproduces the original
``Diagram.solve()`` exactly.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any, Optional

from diagrams_as_code.constraints import ConstraintSolver
from diagrams_as_code.elements import AbsoluteConstraint, Element
from diagrams_as_code.geometry import Anchor, Point, Rect
from diagrams_as_code.groups import Group
from diagrams_as_code.layout.base import SOURCE_KEY, LayoutWarning
from diagrams_as_code.layout.graph import build_scope_graph, pinned_ids, scope_children
from diagrams_as_code.layout.layered import LayeredLayout
from diagrams_as_code.layout.sidecar import apply_entries, load_layout_file
from diagrams_as_code.router import OrthogonalRouter

FRAME_X = 60.0
FRAME_Y = 80.0


@dataclass
class _LayoutState:
    """What the first run saw, so later runs start from the same place."""

    bounds: dict[int, tuple[Element, Rect, float, float]] = field(default_factory=dict)
    base_size: tuple[float, float] = (0.0, 0.0)
    #: (width, height) the pipeline itself left the canvas at after the previous
    #: run. Used to tell "the pipeline grew the canvas" apart from "the user
    #: changed width/height between solves" (see ``_reset``).
    grown_size: tuple[float, float] = (0.0, 0.0)


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
    _grow_canvas(diagram, elements)
    diagram._layout_state.grown_size = (diagram.width, diagram.height)
    if diagram.layout == "auto":
        _warn_pinned_overlaps(diagram, elements, auto_ids)
    router = OrthogonalRouter()
    routes: dict[int, list[Point]] = {}
    for edge in diagram.edges:
        waypoints = router.route(edge, obstacles=elements)
        edge.waypoints = waypoints
        routes[id(edge)] = waypoints
    diagram.routes = routes


def _reset(diagram: Any, elements: list[Element]) -> None:
    state: Optional[_LayoutState] = getattr(diagram, "_layout_state", None)
    if state is None:
        size = (diagram.width, diagram.height)
        state = _LayoutState(base_size=size, grown_size=size)
        diagram._layout_state = state
    else:
        current = (diagram.width, diagram.height)
        if current == state.grown_size:
            # Nothing but the pipeline's own last growth changed the size; undo it.
            diagram.width, diagram.height = state.base_size
        else:
            # The user set width/height since the last solve; treat that as new.
            state.base_size = current
    for el in elements:
        saved = state.bounds.get(id(el))
        if saved is None:
            state.bounds[id(el)] = (el, el.bounds, el.width, el.height)
        else:
            _, el.bounds, el.width, el.height = saved
        el.constraints[:] = [c for c in el.constraints if SOURCE_KEY not in c]


def _apply_layout_file(diagram: Any, elements: list[Element]) -> bool:
    """Apply the layout file, if any; True when at least one entry matched."""
    if diagram.layout_file is None:
        return False
    return apply_entries(elements, load_layout_file(diagram.layout_file)) > 0


def _deepest_first(groups: list[Group]) -> list[Group]:
    def depth(g: Group) -> int:
        d, cur = 0, g.parent
        while cur is not None:
            d, cur = d + 1, cur.parent
        return d

    return sorted(groups, key=depth, reverse=True)


def _auto_constraint(x: float, y: float) -> AbsoluteConstraint:
    return AbsoluteConstraint(
        x=x, y=y, anchor=Anchor.TOP_LEFT, _layout_source="auto"
    )


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
        if group.id in pinned:
            # A pinned group is not a node in its parent's graph, so no size
            # estimate is needed -- and its descendants may reference elements
            # outside it, which a group-local solve cannot resolve.
            continue
        # Estimate this group's size for its parent scope. Every constraint in
        # an unpinned group resolves within it, so the estimate is complete;
        # the global solve below stays authoritative.
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
    diagram.height = max(diagram.height, bottom + FRAME_Y)


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
