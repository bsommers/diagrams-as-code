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

import dataclasses
import math
import warnings
from dataclasses import dataclass, field
from typing import Any, Optional

from diagrams_as_code.connections import Edge, EdgeStyle, Routing
from diagrams_as_code.constraints import ConstraintSolver
from diagrams_as_code.elements import AbsoluteConstraint, Element
from diagrams_as_code.geometry import Anchor, PathKind, Point, Rect, RoutedPath
from diagrams_as_code.groups import Group
from diagrams_as_code.layout.badges import place_badges
from diagrams_as_code.layout.base import SOURCE_KEY, LayoutWarning
from diagrams_as_code.layout.graph import (
    build_scope_graph,
    lift,
    node_inset,
    pinned_ids,
    scope_children,
)
from diagrams_as_code.labels import (
    GROUP_TITLE_INSET,
    badge_size,
    edge_badge_rect,
    group_title_rect,
    node_label,
)
from diagrams_as_code.layout.lanes import separate_lanes
from diagrams_as_code.layout.layered import LayeredLayout
from diagrams_as_code.layout.sidecar import apply_entries, load_layout_file
from diagrams_as_code.router import EdgeRouter, RoutingScene, path_collides

FRAME_X = 60.0
FRAME_Y = 80.0
#: Smallest trailing margin a fitted canvas keeps, however close content starts to the origin.
FIT_MARGIN_MIN = 24.0
#: Clear space kept on each side of an edge badge between two ranks.
BADGE_MARGIN = 12.0


def resolve_edge_style(edge: Edge, diagram: Any) -> EdgeStyle:
    # 1. Routing
    if edge._routing is not None:
        eff_routing = edge._routing
    elif getattr(diagram, "routing", None) is not None:
        eff_routing = diagram.routing
    else:
        eff_routing = Routing.ORTHOGONAL
    if isinstance(eff_routing, str):
        eff_routing = Routing(eff_routing)

    # 2. Corner radius (None = inherit, 0.0 = explicit sharp)
    if edge._corner_radius is not None:
        eff_cr = edge._corner_radius
    elif getattr(diagram, "corner_radius", None) is not None:
        eff_cr = diagram.corner_radius
    else:
        eff_cr = 0.0

    # 3. Clearance (None = inherit)
    if edge._clearance is not None:
        eff_clearance = edge._clearance
    elif getattr(diagram, "clearance", None) is not None:
        eff_clearance = diagram.clearance
    else:
        eff_clearance = 15.0

    return EdgeStyle(
        routing=eff_routing,
        corner_radius=float(eff_cr),
        clearance=float(eff_clearance),
    )


@dataclass
class _LayoutState:
    """What the first run saw, so later runs start from the same place."""

    bounds: dict[int, tuple[Element, Rect, float, float]] = field(default_factory=dict)
    #: (width, height) each element had when the previous run finished.
    solved: dict[int, tuple[float, float]] = field(default_factory=dict)
    base_size: tuple[float, float] = (0.0, 0.0)
    #: (width, height) the pipeline itself left the canvas at after the previous
    #: run. Used to tell "the pipeline grew the canvas" apart from "the user
    #: changed width/height between solves" (see ``_reset``).
    grown_size: tuple[float, float] = (0.0, 0.0)


def run_layout(diagram: Any) -> None:
    """Position every element and route every edge of diagram."""
    elements = diagram.solver.all_elements()
    _reset(diagram, elements)
    _grow_to_fit_labels(elements, getattr(diagram, "fit_labels", True))
    _apply_layout_file(diagram, elements)
    auto_ids: set[str] = set()
    if diagram.layout == "auto":
        auto_ids = _auto_place(diagram, elements)
    diagram.solver.solve()
    groups = _deepest_first(diagram.groups)
    _refresh_group_bounds(groups)

    # 1. Build Scene & Route Edges
    scene = RoutingScene.build(
        elements,
        canvas=Rect(0.0, 0.0, diagram.width, diagram.height),
    )
    edge_router = EdgeRouter()
    styles = {edge: resolve_edge_style(edge, diagram) for edge in diagram.edges}
    scene = scene.with_anchor_offsets(_spread_ports(diagram.edges, styles, edge_router, scene))
    routes: dict[Any, RoutedPath] = {}
    for edge in diagram.edges:
        style = styles[edge]
        if edge.manual_waypoints:
            path = RoutedPath(
                kind=PathKind.POLYLINE,
                points=tuple(edge.manual_waypoints),
                corner_radius=style.corner_radius,
            )
        else:
            path = edge_router.route(edge, scene=scene, style=style)
            if style.routing != Routing.DIRECT and path_collides(edge, path, scene):
                warnings.warn(
                    LayoutWarning(
                        f"edge {edge.source.label!r} -> {edge.target.label!r} could not be "
                        "routed clear of other elements; move them apart or set ports"
                    ),
                    stacklevel=4,
                )
        edge._resolved_path = path
        edge._resolved_style = style
        routes[edge] = path
        routes[id(edge)] = path
    separate_lanes(diagram.edges, routes, [s.bounds for s in diagram.shapes])
    diagram.routes = routes

    # 2. Frame & Grow Canvas
    _frame(elements, groups, routes)
    if getattr(diagram, "pixel_snap", False):
        _snap_to_pixels(elements, diagram.edges, routes)
    keep_clear = [s.bounds for s in diagram.shapes]
    keep_clear += [t for t in (group_title_rect(g) for g in diagram.groups) if t is not None]
    place_badges(diagram.edges, routes, keep_clear)
    _grow_canvas(diagram, elements, routes)
    diagram._layout_state.grown_size = (diagram.width, diagram.height)
    diagram._layout_state.solved = {id(el): (el.width, el.height) for el in elements}
    if diagram.layout == "auto":
        _warn_pinned_overlaps(diagram, elements, auto_ids)


def _grow_to_fit_labels(elements: list[Element], default: bool = True) -> None:
    """Enlarge shapes whose inside label cannot fit even at the smallest size.

    A label must never spill out of its box. Growing happens before placement,
    so relative constraints and auto-layout see the final size.
    """
    for el in elements:
        if isinstance(el, Group) or not getattr(el, "label", None):
            continue
        wanted = getattr(el, "fit_label", None)
        if not (default if wanted is None else wanted):
            continue
        label = node_label(el)
        if label.fits:
            continue
        b = el.bounds
        w, h = max(b.width, label.needed_width), max(b.height, label.needed_height)
        # Widening changes how the text wraps; settle the height for the new width.
        el.bounds = Rect(b.x, b.y, w, h)
        again = node_label(el)
        h = max(h, again.needed_height) if not again.fits else h
        el.bounds = Rect(b.x, b.y, w, h)
        el.width, el.height = w, h


def _spread_ports(
    edges: list[Edge],
    styles: dict[Edge, EdgeStyle],
    router: EdgeRouter,
    scene: RoutingScene,
) -> dict[Edge, tuple[float, float]]:
    """Shift port anchors so incoming and outgoing edges on one side do not overlap.

    Edges leaving a side keep sharing one anchor (a fan-out trunk reads well),
    and so do edges arriving at it. When a side carries both, the two sets are
    moved to a third and two thirds of the way along it, ordered by where their
    other ends lie so the lines do not cross.
    """
    # (element, port) -> role -> [(edge index, edge, other end's centre)]
    sides: dict[tuple[Element, Any], dict[str, list[tuple[int, Edge, Point]]]] = {}
    ports: dict[Edge, tuple[Any, Any]] = {}
    for idx, edge in enumerate(edges):
        if edge.manual_waypoints or edge.source is edge.target:
            continue
        obstacles = scene.obstacles_for(edge, clearance=0.0)
        sp, tp = router.resolve_ports(edge, obstacles=obstacles, style=styles[edge])
        ports[edge] = (sp, tp)
        sides.setdefault((edge.source, sp), {}).setdefault("out", []).append(
            (idx, edge, edge.target.bounds.center)
        )
        sides.setdefault((edge.target, tp), {}).setdefault("in", []).append(
            (idx, edge, edge.source.bounds.center)
        )

    offsets: dict[Edge, list[float]] = {}
    for (element, port), roles in sides.items():
        if len(roles) < 2:
            continue
        horizontal_side = port.value in ("north", "south")
        length = element.bounds.width if horizontal_side else element.bounds.height

        def far_end(role: str, edge: Edge, centre: Point) -> float:
            """Where the edge's other end sits along this side's axis.

            Counts a shift already given to that end, so the two ends of an
            edge are moved the same way and the edge stays straight.
            """
            other_port = ports[edge][1 if role == "out" else 0]
            along = centre.x if horizontal_side else centre.y
            if (other_port.value in ("north", "south")) == horizontal_side:
                along += offsets.get(edge, [0.0, 0.0])[1 if role == "out" else 0]
            return along

        def sort_key(role: str) -> tuple[float, int]:
            members = roles[role]
            along = [far_end(role, e, c) for _, e, c in members]
            return (round(sum(along) / len(along), 6), min(i for i, _, _ in members))

        for slot, role in enumerate(sorted(roles, key=sort_key)):
            shift = (-1.0 if slot == 0 else 1.0) * length / 6.0
            for _, edge, _ in roles[role]:
                offsets.setdefault(edge, [0.0, 0.0])[0 if role == "out" else 1] = shift
    return {e: (v[0], v[1]) for e, v in offsets.items()}


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
            # The user set width/height since the last solve; treat that as new,
            # and stop fitting an axis they have now sized themselves.
            if current[0] != state.grown_size[0]:
                diagram._fit_width = False
            if current[1] != state.grown_size[1]:
                diagram._fit_height = False
            state.base_size = current
    for el in elements:
        saved = state.bounds.get(id(el))
        if saved is None:
            state.bounds[id(el)] = (el, el.bounds, el.width, el.height)
        else:
            _, base, width, height = saved
            left = state.solved.get(id(el))
            if (
                left is not None
                and not isinstance(el, Group)
                and (el.width, el.height) != left
            ):
                # The user resized the element since the last solve; keep that.
                width, height = el.width, el.height
                base = Rect(base.x, base.y, width, height)
                state.bounds[id(el)] = (el, base, width, height)
            el.bounds, el.width, el.height = base, width, height
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
    if diagram.direction == "LR":
        # A badge sits in the gap between two ranks; make the gap wide enough.
        free = {n.id for n in graph.nodes}
        widest = 0.0
        for edge in diagram.edges:
            if not edge.label:
                continue
            s, t = lift(edge.source, group), lift(edge.target, group)
            if s is not None and t is not None and s is not t and s.id in free and t.id in free:
                widest = max(widest, badge_size(edge.label)[0])
        if widest + BADGE_MARGIN * 2.0 > engine.rank_gap:
            engine = LayeredLayout(
                engine.direction, widest + BADGE_MARGIN * 2.0, engine.node_gap, engine.sweeps
            )
    positions = engine.arrange(graph)
    for child in scope_children(diagram, group):
        pos = positions.get(child.id)
        if pos is not None:
            child.constraints.append(
                _auto_constraint(origin.x + pos.x + node_inset(child), origin.y + pos.y)
            )
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
    """Recompute auto-sized groups, deepest first, widening any too narrow for its title."""
    for g in groups:
        if g.is_auto_sized and g.children:
            b = g.calculate_bounds()
            title = group_title_rect(g)
            if title is not None and getattr(g, "fit_title", True):
                extra = title.width + 2.0 * GROUP_TITLE_INSET - b.width
                if extra > 0.0:
                    g.bounds = Rect(b.x - extra / 2.0, b.y, b.width + extra, b.height)
                    g.width = g.bounds.width


def _frame(
    elements: list[Element],
    groups: list[Group],
    routes: Optional[dict[Any, RoutedPath]] = None,
) -> None:
    """Translate the canvas when content or routes have negative or tight coordinates."""
    if routes is None:
        routes = {}
    roots = [e for e in elements if getattr(e, "parent", None) is None]
    if not roots and not routes:
        return

    # Check minimum coordinates across elements and routes
    mins_x: list[float] = [e.bounds.x for e in roots]
    mins_y: list[float] = [e.bounds.y for e in roots]
    for path in set(routes.values()):
        bb = path.bbox()
        mins_x.append(bb.x)
        mins_y.append(bb.y)

    min_x = min(mins_x) if mins_x else 0.0
    min_y = min(mins_y) if mins_y else 0.0

    offset_x = max(0.0, -min_x + FRAME_X) if min_x < 0.0 else 0.0
    offset_y = max(0.0, -min_y + FRAME_Y) if min_y < 0.0 else 0.0

    if offset_x > 0.0 or offset_y > 0.0:
        for r in roots:
            r.translate(offset_x, offset_y)
        _refresh_group_bounds(groups)
        translated_paths: dict[int, RoutedPath] = {}
        for p in routes.values():
            if id(p) not in translated_paths:
                translated_paths[id(p)] = p.translate(offset_x, offset_y)
        for k, path in list(routes.items()):
            shifted = translated_paths[id(path)]
            routes[k] = shifted
            if isinstance(k, Edge):
                k._resolved_path = shifted


def _snap_to_pixels(elements: list[Element], edges: list[Edge], routes: dict[Any, RoutedPath]) -> None:
    """Round every bound and route point to a whole pixel."""
    def px(value: float) -> float:
        return float(math.floor(value + 0.5))

    for el in elements:
        b = el.bounds
        left, top = px(b.x), px(b.y)
        el.bounds = Rect(left, top, px(b.right) - left, px(b.bottom) - top)
    for edge in edges:
        path = routes.get(edge)
        if path is None:
            continue
        snapped = dataclasses.replace(path, points=tuple(Point(px(p.x), px(p.y)) for p in path.points))
        routes[edge] = routes[id(edge)] = snapped
        edge._resolved_path = snapped


def _grow_canvas(
    diagram: Any,
    elements: list[Element],
    routes: Optional[dict[Any, RoutedPath]] = None,
) -> None:
    """Size the canvas to the content.

    An axis the user sized is a minimum: it grows when content would be clipped
    and is otherwise left alone. An axis left unset is fitted, with a trailing
    margin that mirrors the leading one so the content sits evenly in the frame.
    """
    if routes is None:
        routes = {}
    roots = [e for e in elements if getattr(e, "parent", None) is None]
    boxes: list[Rect] = [e.bounds for e in roots]
    for key, path in routes.items():
        if not isinstance(key, Edge):
            continue
        boxes.append(path.bbox())
        badge = edge_badge_rect(key, path)
        if badge is not None:
            boxes.append(badge)
    if not boxes:
        return

    left, top = min(b.x for b in boxes), min(b.y for b in boxes)
    right, bottom = max(b.right for b in boxes), max(b.bottom for b in boxes)
    if getattr(diagram, "_fit_width", False):
        diagram.width = math.ceil(right + min(max(left, FIT_MARGIN_MIN), FRAME_X))
    else:
        diagram.width = max(diagram.width, right + FRAME_X)
    if getattr(diagram, "_fit_height", False):
        diagram.height = math.ceil(bottom + min(max(top, FIT_MARGIN_MIN), FRAME_Y))
    else:
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
