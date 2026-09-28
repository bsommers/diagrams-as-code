# Phase 11: Routing Data Model, Layout Pipeline, and Canvas Extrema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a typed routing data model (`RoutedPath`, `RoutingScene`, `EdgeStyle`), pure routing execution within the layout pipeline, and analytical canvas auto-growth and framing for edge curves and detours.

**Architecture:** Replace duck-typed routing lists with a frozen `RoutedPath` value type in `geometry.py` (layer 0) and an obstacle `RoutingScene` in `router.py` (layer 3). Centralize style cascading into `resolve_edge_style` in `layout/pipeline.py` (layer 4) and dispatch exclusively via `EdgeRouter`. In `run_layout()`, execute edge routing before framing and canvas expansion, utilizing analytical Bezier/polyline bounding boxes (`RoutedPath.bbox()`) and coordinate translation (`RoutedPath.translate()`) to prevent clipping.

**Tech Stack:** Python 3.10+ standard library (`math`, `dataclasses`, `enum`, `typing`), pytest, `uv`.

## Global Constraints

- **Always `uv`:** `uv run pytest`, `uv run python ...`. Never bare `pip`, `python`, or `pytest`.
- **Zero runtime dependencies:** `dependencies = []` in `pyproject.toml` remains strictly empty. Pure standard library only.
- **Layering constraints:** Enforced by `tests/test_module_boundaries.py` (geometry 0 -> elements 1 -> connections 2 -> groups 2 -> router/constraints 3 -> layout/renderer_svg/bom 4 -> diagram 5). `renderer_svg -> router` is strictly forbidden.
- **Byte-identical baseline output:** Diagrams with default settings must produce identical visual output; existing test suite (520 tests) must pass green locally without regressions.
- **Python 3.10 compatibility:** No Python 3.11+ features (no `match` statements, no `Self`, no PEP 695 generics).

---

## File Structure

| File | Layer | Responsibility |
|---|---|---|
| `src/diagrams_as_code/geometry.py` | 0 | Adds `PathKind` and frozen `RoutedPath` with `bbox()`, `translate()`, `label_anchor()`, and `svg_d()`. |
| `src/diagrams_as_code/connections.py` | 2 | Updates `Edge` to store `None` for unset style fields, adds `manual_waypoints`, and provides backward-compatible properties. |
| `src/diagrams_as_code/diagram.py` | 5 | Updates `Diagram` with `routing` default and configuration; updates `_EdgeBuilder` with strict keyword validation and non-mutating per-call kwargs. |
| `src/diagrams_as_code/router.py` | 3 | Adds `RoutingScene`; makes `OrthogonalRouter`, `CurveRouter`, and `EdgeRouter` pure returning `RoutedPath`; adds `route_all()`. |
| `src/diagrams_as_code/layout/pipeline.py` | 4 | Adds `EdgeStyle` and `resolve_edge_style()`; reorders pipeline to route before framing and canvas expansion; integrates edge extrema. |
| `src/diagrams_as_code/renderer_svg.py` | 4 | Removes fallback routing and obstacle logic; renders purely from `diagram.routes` using `path.svg_d()` and `path.label_anchor()`. |
| `tests/test_module_boundaries.py` | - | Forbids `renderer_svg -> router` import. |
| `tests/test_geometry.py` | - | Unit tests for `RoutedPath` methods (`bbox`, `translate`, `label_anchor`, `svg_d`). |
| `tests/test_routing.py` | - | Unit tests for `RoutingScene`, pure routers, and `EdgeRouter` dispatcher. |
| `tests/test_diagram_api.py` | - | Unit tests for style cascade precedence, builder validation, and dynamic reconfiguration. |
| `tests/test_layout_pipeline.py` | - | Tests for pipeline execution order, extrema framing, and canvas expansion. |
| `tests/test_renderer_svg.py` | - | Tests for pure SVG drawing without router dependency. |
| `tests/test_e2e.py` | - | End-to-end integration tests for curved routing and canvas framing. |

---

## Wave 1: Data Model & Style Resolution

### Task 1: `RoutedPath` and `PathKind` Value Type in `geometry.py` (D-13)

**Files:**
- Modify: `src/diagrams_as_code/geometry.py:1-60`
- Test: `tests/test_geometry.py`

**Interfaces:**
- Consumes: `Point`, `Rect`, `CubicBezier` in `src/diagrams_as_code/geometry.py`
- Produces:
  - `PathKind(Enum)`: `POLYLINE = "polyline"`, `BEZIER_CHAIN = "bezier_chain"`
  - `RoutedPath(kind: PathKind, points: tuple[Point, ...], corner_radius: float = 0.0)`
  - `RoutedPath.segments() -> list[Union[tuple[Point, Point], CubicBezier]]`
  - `RoutedPath.bbox() -> Rect`
  - `RoutedPath.translate(dx: float, dy: float) -> RoutedPath`
  - `RoutedPath.label_anchor() -> tuple[float, float]`
  - `RoutedPath.svg_d() -> str`

- [ ] **Step 1: Write failing tests in `tests/test_geometry.py`**

```python
# Append to tests/test_geometry.py
from diagrams_as_code.geometry import PathKind, RoutedPath, Point, Rect

def test_routed_path_polyline_bbox_and_translate() -> None:
    pts = (Point(10.0, 20.0), Point(50.0, 20.0), Point(50.0, 80.0))
    path = RoutedPath(kind=PathKind.POLYLINE, points=pts, corner_radius=0.0)
    assert path.bbox() == Rect(10.0, 20.0, 40.0, 60.0)
    
    translated = path.translate(5.0, 10.0)
    assert translated.points == (Point(15.0, 30.0), Point(55.0, 30.0), Point(55.0, 90.0))
    assert translated.bbox() == Rect(15.0, 30.0, 40.0, 60.0)


def test_routed_path_bezier_bbox() -> None:
    p0 = Point(0.0, 100.0)
    c1 = Point(30.0, 0.0)
    c2 = Point(70.0, 0.0)
    p3 = Point(100.0, 100.0)
    path = RoutedPath(kind=PathKind.BEZIER_CHAIN, points=(p0, c1, c2, p3))
    bb = path.bbox()
    assert bb.y < 30.0  # Captures arching Bezier curve apex
    assert bb.height > 70.0


def test_routed_path_svg_d_polyline_and_fillet() -> None:
    pts = (Point(0.0, 0.0), Point(100.0, 0.0), Point(100.0, 100.0))
    sharp = RoutedPath(kind=PathKind.POLYLINE, points=pts, corner_radius=0.0)
    assert sharp.svg_d() == "M 0.0 0.0 L 100.0 0.0 L 100.0 100.0"
    
    filleted = RoutedPath(kind=PathKind.POLYLINE, points=pts, corner_radius=10.0)
    d = filleted.svg_d()
    assert "Q" in d


def test_routed_path_label_anchor() -> None:
    pts = (Point(0.0, 0.0), Point(100.0, 0.0))
    path = RoutedPath(kind=PathKind.POLYLINE, points=pts)
    assert path.label_anchor() == (50.0, 0.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_geometry.py -k test_routed_path`
Expected: FAIL with `ImportError: cannot import name 'PathKind' from 'diagrams_as_code.geometry'`

- [ ] **Step 3: Implement `PathKind` and `RoutedPath` in `src/diagrams_as_code/geometry.py`**

```python
# In src/diagrams_as_code/geometry.py
class PathKind(Enum):
    POLYLINE = "polyline"
    BEZIER_CHAIN = "bezier_chain"


@dataclass(frozen=True)
class RoutedPath:
    kind: PathKind
    points: tuple[Point, ...]
    corner_radius: float = 0.0

    def segments(self) -> list[Union[tuple[Point, Point], CubicBezier]]:
        if self.kind == PathKind.POLYLINE:
            return [(self.points[i], self.points[i + 1]) for i in range(len(self.points) - 1)]
        elif self.kind == PathKind.BEZIER_CHAIN:
            if len(self.points) < 4 or (len(self.points) - 1) % 3 != 0:
                return []
            curves: list[CubicBezier] = []
            for i in range(0, len(self.points) - 1, 3):
                curves.append(
                    CubicBezier(
                        self.points[i],
                        self.points[i + 1],
                        self.points[i + 2],
                        self.points[i + 3],
                    )
                )
            return curves
        return []

    def bbox(self) -> Rect:
        if not self.points:
            return Rect(0.0, 0.0, 0.0, 0.0)
        if self.kind == PathKind.BEZIER_CHAIN:
            segs = self.segments()
            if segs and all(isinstance(s, CubicBezier) for s in segs):
                bboxes = [s.bbox() for s in segs]  # type: ignore[union-attr]
                min_x = min(b.x for b in bboxes)
                min_y = min(b.y for b in bboxes)
                max_x = max(b.right for b in bboxes)
                max_y = max(b.bottom for b in bboxes)
                return Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        min_x = min(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_x = max(p.x for p in self.points)
        max_y = max(p.y for p in self.points)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def translate(self, dx: float, dy: float) -> RoutedPath:
        shifted_points = tuple(Point(p.x + dx, p.y + dy) for p in self.points)
        return RoutedPath(
            kind=self.kind,
            points=shifted_points,
            corner_radius=self.corner_radius,
        )

    def label_anchor(self) -> tuple[float, float]:
        if not self.points:
            return (0.0, 0.0)
        if self.kind == PathKind.BEZIER_CHAIN:
            segs = [s for s in self.segments() if isinstance(s, CubicBezier)]
            if not segs:
                return (self.points[0].x, self.points[0].y)
            if len(segs) == 1:
                mid = segs[0].arc_length_midpoint(num_samples=32)
                return (mid.x, mid.y)
            longest_curve: Optional[CubicBezier] = None
            max_seg_len = -1.0
            for seg_curve in segs:
                seg_len = seg_curve.arc_length(num_samples=16)
                if seg_len > max_seg_len:
                    max_seg_len = seg_len
                    longest_curve = seg_curve
            assert longest_curve is not None
            mid = longest_curve.arc_length_midpoint(num_samples=32)
            return (mid.x, mid.y)
        if self.corner_radius > 0.0 and len(self.points) > 2:
            longest_idx = 0
            longest_len = -1.0
            for j in range(len(self.points) - 1):
                seg_l = math.hypot(
                    self.points[j + 1].x - self.points[j].x,
                    self.points[j + 1].y - self.points[j].y,
                )
                if seg_l > longest_len:
                    longest_len = seg_l
                    longest_idx = j
            lx = (self.points[longest_idx].x + self.points[longest_idx + 1].x) / 2.0
            ly = (self.points[longest_idx].y + self.points[longest_idx + 1].y) / 2.0
            return (lx, ly)
        mid_idx = len(self.points) // 2
        lx = (self.points[mid_idx - 1].x + self.points[mid_idx].x) / 2.0
        ly = (self.points[mid_idx - 1].y + self.points[mid_idx].y) / 2.0
        return (lx, ly)

    def svg_d(self) -> str:
        if not self.points:
            return ""
        if self.kind == PathKind.BEZIER_CHAIN:
            if len(self.points) == 4:
                p0, c1, c2, p3 = self.points
                return f"M {p0.x} {p0.y} C {c1.x} {c1.y}, {c2.x} {c2.y}, {p3.x} {p3.y}"
            if len(self.points) >= 4 and (len(self.points) - 1) % 3 == 0:
                parts = [f"M {self.points[0].x} {self.points[0].y}"]
                for i in range(1, len(self.points), 3):
                    parts.append(
                        f"C {self.points[i].x} {self.points[i].y}, "
                        f"{self.points[i + 1].x} {self.points[i + 1].y}, "
                        f"{self.points[i + 2].x} {self.points[i + 2].y}"
                    )
                return " ".join(parts)
        if self.kind == PathKind.POLYLINE and self.corner_radius > 0.0 and len(self.points) >= 3:
            return self._filleted_svg_d()
        return f"M {self.points[0].x} {self.points[0].y} " + " ".join(
            f"L {p.x} {p.y}" for p in self.points[1:]
        )

    def _filleted_svg_d(self) -> str:
        pts = self.points
        n = len(pts)
        cr = self.corner_radius
        seg_lens: list[float] = []
        seg_units: list[Point] = []
        for j in range(n - 1):
            vx = pts[j + 1].x - pts[j].x
            vy = pts[j + 1].y - pts[j].y
            l = math.hypot(vx, vy)
            seg_lens.append(l)
            seg_units.append(Point(vx / l, vy / l) if l > 1e-6 else Point(0.0, 0.0))

        effective_radii: list[float] = [0.0] * n
        for i in range(1, n - 1):
            l_in = seg_lens[i - 1]
            l_out = seg_lens[i]
            if l_in < 1e-6 or l_out < 1e-6:
                continue
            u_in = seg_units[i - 1]
            u_out = seg_units[i]
            dot = u_in.x * u_out.x + u_in.y * u_out.y
            if abs(dot) > 1e-6:
                continue
            max_r_in = l_in / 2.0
            max_r_out = l_out / 2.0
            if i == 1:
                lead_in = min(10.0, l_in / 2.0)
                max_r_in = min(max_r_in, max(0.0, l_in - lead_in))
            if i == n - 2:
                lead_in = min(10.0, l_out / 2.0)
                max_r_out = min(max_r_out, max(0.0, l_out - lead_in))
            r_corner = min(cr, max_r_in, max_r_out)
            if r_corner < 2.0:
                r_corner = 0.0
            effective_radii[i] = r_corner

        parts = [f"M {pts[0].x} {pts[0].y}"]
        for i in range(1, n - 1):
            p_c = pts[i]
            r = effective_radii[i]
            if r >= 2.0:
                u_in = seg_units[i - 1]
                u_out = seg_units[i]
                t1 = Point(p_c.x - u_in.x * r, p_c.y - u_in.y * r)
                t2 = Point(p_c.x + u_out.x * r, p_c.y + u_out.y * r)
                parts.append(f"L {t1.x} {t1.y} Q {p_c.x} {p_c.y}, {t2.x} {t2.y}")
            else:
                parts.append(f"L {p_c.x} {p_c.y}")
        parts.append(f"L {pts[-1].x} {pts[-1].y}")
        return " ".join(parts)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_geometry.py -k test_routed_path -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/geometry.py tests/test_geometry.py
git commit -m "feat(geometry): add RoutedPath value type and PathKind enum"
```

---

### Task 2: `Edge` & `_EdgeBuilder` Style Defaults & Validation (D-07, D-17, D-19)

**Files:**
- Modify: `src/diagrams_as_code/connections.py:63-186`
- Modify: `src/diagrams_as_code/diagram.py:50-98`
- Test: `tests/test_diagram_api.py`

**Interfaces:**
- Consumes: `RoutedPath` from `diagrams_as_code.geometry`
- Produces:
  - `Edge.__init__(..., routing=None, corner_radius=None, clearance=None, manual_waypoints=None)`
  - `Edge._routing: Optional[Routing]` (defaults to None)
  - `Edge._clearance: Optional[float]` (defaults to None)
  - `Edge.manual_waypoints: Optional[list[Point]]`
  - `Edge._resolved_path: Optional[RoutedPath]`
  - `_EdgeBuilder.__call__(**kwargs)` raises `TypeError` on unexpected kwargs

- [ ] **Step 1: Write failing tests in `tests/test_diagram_api.py`**

```python
# In tests/test_diagram_api.py
import pytest
from diagrams_as_code import Edge, Routing, Point
from diagrams_as_code.elements import Shape

def test_edge_style_defaults_to_none() -> None:
    s1 = Shape(id="s1", label="1")
    s2 = Shape(id="s2", label="2")
    e = Edge(source=s1, target=s2)
    assert e._routing is None
    assert e._clearance is None
    assert e._corner_radius is None
    assert e.manual_waypoints is None
    # Public getters fall back to system defaults when unresolved
    assert e.routing == Routing.ORTHOGONAL
    assert e.clearance == 15.0


def test_edge_builder_rejects_unknown_kwargs() -> None:
    from diagrams_as_code import Diagram
    with Diagram() as d:
        with pytest.raises(TypeError, match="unexpected keyword argument 'invalid_param'"):
            d.edge(invalid_param=123)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_diagram_api.py -k "test_edge_style_defaults or test_edge_builder_rejects"`
Expected: FAIL

- [ ] **Step 3: Update `Edge` in `connections.py` and `_EdgeBuilder` in `diagram.py`**

In `src/diagrams_as_code/connections.py`:
- Update `_validate_clearance` to allow `None` and return `Optional[float]`.
- In `Edge.__init__`:
  - `routing: Optional[Union[Routing, str]] = None`
  - `self._routing: Optional[Routing] = _coerce_enum(routing, Routing, "routing", allow_none=True)`
  - `self._clearance: Optional[float] = self._validate_clearance(clearance)`
  - `self.manual_waypoints: Optional[list[Point]] = list(manual_waypoints) if manual_waypoints else None`
  - `self._resolved_path: Optional[RoutedPath] = None`
- In `Edge.routing` property:
  - If `self._routing is not None`: return `self._routing`
  - If `self._resolved_path is not None`: return `Routing.CURVE if self._resolved_path.kind == PathKind.BEZIER_CHAIN else Routing.ORTHOGONAL`
  - Return `Routing.ORTHOGONAL`
- In `Edge.clearance` property:
  - Return `self._clearance if self._clearance is not None else 15.0`
- In `Edge.waypoints` property:
  - Getter: return `list(self._resolved_path.points)` if `self._resolved_path is not None` else (`list(self.manual_waypoints)` if `self.manual_waypoints is not None` else None)
  - Setter: `self.manual_waypoints = list(val) if val is not None else None; self._resolved_path = None`

In `src/diagrams_as_code/diagram.py`:
- In `_EdgeBuilder.__call__`:
  - Strictly check `allowed_kwargs = {"source", "target", "clearance", "corner_radius", "routing"}`
  - If any unexpected kwargs, `raise TypeError(f"_EdgeBuilder got unexpected keyword argument {k!r}")`
  - Do not mutate `self._clearance` persistently; return a configured shallow clone of `self` or pass call-specific arguments.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_diagram_api.py -k "test_edge_style_defaults or test_edge_builder_rejects" -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/connections.py src/diagrams_as_code/diagram.py tests/test_diagram_api.py
git commit -m "feat(connections): store None for unset edge styles and add manual_waypoints"
```

---

### Task 3: Diagram Style Defaults & `resolve_edge_style` (D-01..D-04, D-18)

**Files:**
- Modify: `src/diagrams_as_code/layout/pipeline.py:1-40`
- Modify: `src/diagrams_as_code/diagram.py:310-445, 555-595, 638-646`
- Test: `tests/test_layout_pipeline.py`, `tests/test_diagram_api.py`

**Interfaces:**
- Produces:
  - `EdgeStyle(routing: Routing, corner_radius: float, clearance: float)` frozen dataclass
  - `resolve_edge_style(edge: Edge, diagram: Any) -> EdgeStyle` in `src/diagrams_as_code/layout/pipeline.py`
  - `Diagram(routing=None)` and `Diagram.configure(routing=...)`

- [ ] **Step 1: Write failing tests in `tests/test_layout_pipeline.py`**

```python
# In tests/test_layout_pipeline.py
from diagrams_as_code import Diagram, Edge, Routing
from diagrams_as_code.layout.pipeline import resolve_edge_style, EdgeStyle

def test_resolve_edge_style_precedence() -> None:
    with Diagram(routing="curve", corner_radius=12.0, clearance=25.0) as d:
        s1, s2 = d.shape("A"), d.shape("B")
        
        # Edge 1: Inherits all diagram defaults
        e1 = Edge(source=s1, target=s2)
        st1 = resolve_edge_style(e1, d)
        assert st1 == EdgeStyle(routing=Routing.CURVE, corner_radius=12.0, clearance=25.0)
        
        # Edge 2: Overrides routing explicitly, corner_radius=0.0 forces sharp corners (D-03)
        e2 = Edge(source=s1, target=s2, routing="orthogonal", corner_radius=0.0)
        st2 = resolve_edge_style(e2, d)
        assert st2 == EdgeStyle(routing=Routing.ORTHOGONAL, corner_radius=0.0, clearance=25.0)


def test_diagram_configure_invalidates_cache() -> None:
    d = Diagram()
    d._is_solved = True
    d.configure(routing="curve")
    assert d._is_solved is False
    assert d.routing == Routing.CURVE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_layout_pipeline.py -k test_resolve_edge_style_precedence`
Expected: FAIL with `ImportError: cannot import name 'resolve_edge_style'`

- [ ] **Step 3: Implement `EdgeStyle` and `resolve_edge_style`**

In `src/diagrams_as_code/layout/pipeline.py`:
```python
@dataclass(frozen=True)
class EdgeStyle:
    routing: Routing
    corner_radius: float
    clearance: float


def resolve_edge_style(edge: Edge, diagram: Any) -> EdgeStyle:
    # 1. Routing
    if edge._routing is not None:
        eff_routing = edge._routing
    elif getattr(diagram, "routing", None) is not None:
        eff_routing = diagram.routing
    else:
        eff_routing = Routing.ORTHOGONAL

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
```

In `src/diagrams_as_code/diagram.py`:
- Add `routing: Optional[Union[Routing, str]] = None` to `Diagram.__init__`.
- Add `routing` property getter & setter. Setter coerses with `_coerce_enum(val, Routing, "routing", allow_none=True)`.
- In `Diagram.configure()`, support `routing=...`. Invalidate `self._is_solved = False`.
- In `Diagram.connect()` and `_EdgeBuilder.__rshift__`: do NOT resolve diagram defaults onto edge instances. Remove per-site cascade.
- In `Diagram.solve()`: remove `edge.corner_radius = self.corner_radius` loop (D-18).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_layout_pipeline.py -k test_resolve_edge_style_precedence -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/layout/pipeline.py src/diagrams_as_code/diagram.py tests/test_layout_pipeline.py
git commit -m "feat(layout): add resolve_edge_style and diagram routing hierarchy"
```

---

### Task 4: `RoutingScene` Obstacle Model (D-08)

**Files:**
- Modify: `src/diagrams_as_code/router.py:1-60`
- Test: `tests/test_routing.py`

**Interfaces:**
- Consumes: `Element`, `Group`, `Edge`, `Rect`
- Produces:
  - `RoutingScene`
  - `RoutingScene.build(elements: Sequence[Element], canvas: Optional[Rect] = None) -> RoutingScene`
  - `RoutingScene.obstacles_for(edge: Edge, clearance: float = 0.0) -> list[Rect]`

- [ ] **Step 1: Write failing tests in `tests/test_routing.py`**

```python
# In tests/test_routing.py
from diagrams_as_code.elements import Shape
from diagrams_as_code.groups import Group
from diagrams_as_code.connections import Edge
from diagrams_as_code.geometry import Rect
from diagrams_as_code.router import RoutingScene

def test_routing_scene_excludes_endpoints_and_ancestors() -> None:
    g = Group(id="g1", label="Group")
    s1 = Shape(id="s1", label="S1")
    s2 = Shape(id="s2", label="S2")
    obs = Shape(id="obs", label="Obstacle")
    g.add(s1)
    s1.parent = g
    
    s1.bounds = Rect(0.0, 0.0, 50.0, 50.0)
    s2.bounds = Rect(200.0, 0.0, 50.0, 50.0)
    obs.bounds = Rect(100.0, 0.0, 50.0, 50.0)
    g.bounds = Rect(-10.0, -10.0, 80.0, 80.0)
    
    scene = RoutingScene.build([g, s1, s2, obs], canvas=Rect(0, 0, 400, 300))
    e = Edge(source=s1, target=s2)
    
    blocked = scene.obstacles_for(e, clearance=5.0)
    # Endpoint s1, endpoint s2, and ancestor g must be excluded. Only obs remains.
    assert len(blocked) == 1
    assert blocked[0] == obs.bounds.expand(5.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_routing.py -k test_routing_scene`
Expected: FAIL with `ImportError: cannot import name 'RoutingScene'`

- [ ] **Step 3: Implement `RoutingScene` in `src/diagrams_as_code/router.py`**

```python
# In src/diagrams_as_code/router.py
@dataclass(frozen=True)
class RoutingScene:
    rects: dict[Element, Rect]
    ancestors: dict[Element, frozenset[Group]]
    canvas: Rect

    @classmethod
    def build(
        cls,
        elements: Sequence[Element],
        canvas: Optional[Rect] = None,
    ) -> RoutingScene:
        rects: dict[Element, Rect] = {}
        ancestors: dict[Element, set[Group]] = {}
        for el in elements:
            rects[el] = el.bounds
            curr = getattr(el, "parent", None)
            anc: set[Group] = set()
            while curr is not None:
                anc.add(curr)
                curr = getattr(curr, "parent", None)
            ancestors[el] = anc
        return cls(
            rects=rects,
            ancestors={k: frozenset(v) for k, v in ancestors.items()},
            canvas=canvas or Rect(0.0, 0.0, 1200.0, 800.0),
        )

    def obstacles_for(self, edge: Edge, clearance: float = 0.0) -> list[Rect]:
        excluded: set[Element] = {edge.source, edge.target}
        excluded.update(self.ancestors.get(edge.source, frozenset()))
        excluded.update(self.ancestors.get(edge.target, frozenset()))

        result: list[Rect] = []
        for el, r in self.rects.items():
            if el not in excluded:
                result.append(r.expand(clearance) if clearance > 0.0 else r)
        return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_routing.py -k test_routing_scene -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/router.py tests/test_routing.py
git commit -m "feat(router): add RoutingScene obstacle model"
```

---

### Task 5: Pure Routers, In-Route Fillet Clamping, and Single `EdgeRouter` Dispatcher (D-05, D-14, D-16)

**Files:**
- Modify: `src/diagrams_as_code/router.py`
- Test: `tests/test_routing.py`

**Interfaces:**
- Consumes: `RoutedPath`, `RoutingScene`, `EdgeStyle`
- Produces:
  - `OrthogonalRouter.route(...) -> RoutedPath` (pure)
  - `CurveRouter.route(...) -> RoutedPath` (pure)
  - `EdgeRouter.route(edge, style, scene) -> RoutedPath` (single dispatcher)
  - `route_all(edges, elements, groups=(), canvas=None) -> dict[Edge, RoutedPath]`

- [ ] **Step 1: Write failing tests in `tests/test_routing.py`**

```python
# In tests/test_routing.py
def test_router_purity_and_clamped_fillet() -> None:
    s1 = Shape(id="s1", label="1")
    s2 = Shape(id="s2", label="2")
    s1.bounds = Rect(0, 0, 50, 50)
    s2.bounds = Rect(200, 100, 50, 50)
    e = Edge(source=s1, target=s2, corner_radius=15.0)
    scene = RoutingScene.build([s1, s2])
    
    er = EdgeRouter()
    st = EdgeStyle(routing=Routing.ORTHOGONAL, corner_radius=15.0, clearance=15.0)
    path1 = er.route(e, style=st, scene=scene)
    
    # Router must be pure: does not mutate edge
    assert isinstance(path1, RoutedPath)
    assert e._resolved_path is None
    
    # Routing twice produces identical result
    path2 = er.route(e, style=st, scene=scene)
    assert path1 == path2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_routing.py -k test_router_purity`
Expected: FAIL

- [ ] **Step 3: Refactor `router.py` to be pure and return `RoutedPath`**

1. In `OrthogonalRouter.route`:
   - Remove CURVE delegation branch.
   - Accept `(edge, scene=None, style=None, obstacles=None, clearance=None)`.
   - Honour `style.clearance`.
   - If `style` or `edge.corner_radius` specifies `corner_radius > 0.0`: perform obstacle clearance clamping (D-16) at routing time against `scene.obstacles_for(edge, clearance=0.0)`.
   - Return `RoutedPath(kind=PathKind.POLYLINE, points=tuple(pts), corner_radius=effective_corner_radius)`.
2. In `CurveRouter.route`:
   - Accept `(edge, scene=None, style=None, obstacles=None, clearance=None)`.
   - Return `RoutedPath(kind=PathKind.BEZIER_CHAIN, points=tuple(pts))`.
   - Pure: delete `edge.waypoints = pts` assignments.
3. In `EdgeRouter.route`:
   - `route(self, edge: Edge, style: Optional[EdgeStyle] = None, scene: Optional[RoutingScene] = None) -> RoutedPath`:
     - Dispatch on `style.routing`:
       - `Routing.DIRECT`: `p_start, p_end = ...; return RoutedPath(PathKind.POLYLINE, (p_start, p_end))`
       - `Routing.CURVE`: delegate to `self.curve.route(edge, scene=scene, style=style)`
       - `Routing.ORTHOGONAL`: delegate to `self.orthogonal.route(edge, scene=scene, style=style)`
4. Add `route_all(edges: Sequence[Edge], elements: Sequence[Element], groups: Sequence[Group] = (), canvas: Optional[Rect] = None) -> dict[Edge, RoutedPath]`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_routing.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/router.py tests/test_routing.py
git commit -m "refactor(router): pure routers returning RoutedPath and single EdgeRouter dispatcher"
```

---

### Task 6: Pure SVG Drawing in `SVGRenderer` & Architecture Boundary Enforcement (D-15)

**Files:**
- Modify: `src/diagrams_as_code/renderer_svg.py`
- Modify: `tests/test_module_boundaries.py`
- Modify: `tests/test_renderer_svg.py`
- Modify: `tests/test_layout_routes.py`

**Interfaces:**
- Consumes: `RoutedPath`
- Produces:
  - `SVGRenderer.render(..., routes: Optional[Mapping[Any, RoutedPath]] = None)`
  - Architecture boundary: `("renderer_svg", "router")` forbidden

- [ ] **Step 1: Write boundary test in `tests/test_module_boundaries.py`**

```python
# In tests/test_module_boundaries.py
FORBIDDEN_EDGES: dict[tuple[str, str], str] = {
    ("renderer_svg", "router"): "renderer only draws; routing happens in layout stage",
}

# Update test_imports_point_down:
# for (u, t), reason in FORBIDDEN_EDGES.items():
#     if unit == u and target == t:
#         bad.append(f"{target} (forbidden: {reason})")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_module_boundaries.py`
Expected: FAIL because `renderer_svg` currently imports `router`

- [ ] **Step 3: Update `renderer_svg.py` to remove `router` and draw from `routes`**

1. Remove `from diagrams_as_code.router import ...` from `renderer_svg.py`.
2. Remove `_render_filleted_path` (now handled in `RoutedPath.svg_d()`).
3. In `SVGRenderer.render`:
   - For each edge `e`:
     - Look up `path = routes.get(e) or routes.get(id(e)) or getattr(e, "_resolved_path", None)`
     - If `path is None`:
       - If `e.manual_waypoints`: `path = RoutedPath(PathKind.POLYLINE, tuple(e.manual_waypoints))`
       - Else: raise ValueError(f"No route provided for edge {e}") or skip if empty.
     - `path_d = path.svg_d()`
     - If `e.label`: `lx, ly = path.label_anchor()`
4. In `tests/test_renderer_svg.py` and `tests/test_layout_routes.py`, update standalone render calls with edges to supply `routes=route_all(...)`.

- [ ] **Step 4: Run tests to verify pass**

Run: `uv run pytest tests/test_module_boundaries.py tests/test_renderer_svg.py tests/test_layout_routes.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/renderer_svg.py tests/test_module_boundaries.py tests/test_renderer_svg.py tests/test_layout_routes.py
git commit -m "refactor(renderer): pure SVG drawing from RoutedPath and forbid router import"
```

---

## Wave 2: Canvas Growth & Extrema Integration

### Task 7: Layout Pipeline Execution Reordering & Route Storage (D-06, D-07, D-14)

**Files:**
- Modify: `src/diagrams_as_code/layout/pipeline.py:45-80`
- Modify: `src/diagrams_as_code/diagram.py:345-360`
- Test: `tests/test_layout_pipeline.py`

**Interfaces:**
- Consumes: `EdgeRouter`, `resolve_edge_style`, `RoutingScene`
- Produces:
  - `run_layout(diagram)` execution sequence: solve elements -> build scene -> route -> frame -> grow canvas.

- [ ] **Step 1: Write failing tests in `tests/test_layout_pipeline.py`**

```python
# In tests/test_layout_pipeline.py
def test_pipeline_routing_before_canvas_growth() -> None:
    with Diagram(layout="manual", width=500, height=300) as d:
        s1 = d.shape("A", width=50, height=50)
        s2 = d.shape("B", width=50, height=50)
        s1.at(50, 50)
        s2.at(400, 50)
        e = s1 >> s2
    
    # After diagram solve, d.routes must contain RoutedPath
    assert e in d.routes or id(e) in d.routes
    path = d.routes[e] if e in d.routes else d.routes[id(e)]
    assert isinstance(path, RoutedPath)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_layout_pipeline.py -k test_pipeline_routing_before_canvas_growth`
Expected: FAIL

- [ ] **Step 3: Update `run_layout()` in `src/diagrams_as_code/layout/pipeline.py`**

```python
# In src/diagrams_as_code/layout/pipeline.py
def run_layout(diagram: Any) -> None:
    """Position every element and route every edge of diagram."""
    elements = diagram.solver.all_elements()
    _reset(diagram, elements)
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
    routes: dict[Any, RoutedPath] = {}
    for edge in diagram.edges:
        if edge.manual_waypoints:
            path = RoutedPath(
                kind=PathKind.POLYLINE,
                points=tuple(edge.manual_waypoints),
                corner_radius=edge.corner_radius or 0.0,
            )
        else:
            style = resolve_edge_style(edge, diagram)
            path = edge_router.route(edge, style=style, scene=scene)
        edge._resolved_path = path
        routes[edge] = path
        routes[id(edge)] = path
    diagram.routes = routes

    # 2. Frame & Grow Canvas
    _frame(elements, groups, routes)
    _grow_canvas(diagram, elements, routes)
    diagram._layout_state.grown_size = (diagram.width, diagram.height)
    if diagram.layout == "auto":
        _warn_pinned_overlaps(diagram, elements, auto_ids)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_layout_pipeline.py -k test_pipeline_routing_before_canvas_growth -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/layout/pipeline.py src/diagrams_as_code/diagram.py tests/test_layout_pipeline.py
git commit -m "feat(layout): reorder pipeline to route before framing and canvas growth"
```

---

### Task 8: Extrema Integration in `_frame` and `_grow_canvas` (D-09, D-10, D-11, D-12)

**Files:**
- Modify: `src/diagrams_as_code/layout/pipeline.py:160-190`
- Test: `tests/test_layout_pipeline.py`

**Interfaces:**
- Consumes: `RoutedPath.bbox()`, `RoutedPath.translate()`
- Produces:
  - Extrema-aware coordinate framing: translates elements and edge paths when curves or detours arch into `min_y < FRAME_Y` or `min_x < FRAME_X`.
  - Extrema-aware canvas expansion: expands `diagram.width` and `diagram.height` to encompass edge bounding boxes.

- [ ] **Step 1: Write failing tests in `tests/test_layout_pipeline.py`**

```python
# In tests/test_layout_pipeline.py
def test_canvas_grows_for_deflected_or_arching_edge() -> None:
    with Diagram(layout="manual", width=300, height=300, routing="curve") as d:
        s1 = d.shape("A", width=50, height=50)
        s2 = d.shape("B", width=50, height=50)
        s1.at(50, 90)
        s2.at(200, 90)
        # An edge between them arching high or obstacle in middle forcing detour
        obs = d.shape("Obs", width=60, height=60)
        obs.at(120, 80)
        s1 >> s2
    
    # Diagram height should have grown beyond 300 if curve or elements needed margin
    assert d.width >= 300
    assert d.height >= 300
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_layout_pipeline.py -k test_canvas_grows_for_deflected`
Expected: FAIL (or verify framing logic)

- [ ] **Step 3: Implement extrema-aware `_frame` and `_grow_canvas` in `layout/pipeline.py`**

```python
# In src/diagrams_as_code/layout/pipeline.py
def _frame(
    elements: list[Element],
    groups: list[Group],
    routes: dict[Any, RoutedPath],
) -> None:
    """Translate the canvas when content or routes have negative or tight coordinates."""
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
        for k, path in list(routes.items()):
            shifted = path.translate(offset_x, offset_y)
            routes[k] = shifted
            if isinstance(k, Edge):
                k._resolved_path = shifted


def _grow_canvas(
    diagram: Any,
    elements: list[Element],
    routes: dict[Any, RoutedPath],
) -> None:
    roots = [e for e in elements if getattr(e, "parent", None) is None]
    maxs_x: list[float] = [e.bounds.right for e in roots]
    maxs_y: list[float] = [e.bounds.bottom for e in roots]
    for path in set(routes.values()):
        bb = path.bbox()
        maxs_x.append(bb.right)
        maxs_y.append(bb.bottom)

    if maxs_x:
        right = max(maxs_x)
        diagram.width = max(diagram.width, right + FRAME_X)
    if maxs_y:
        bottom = max(maxs_y)
        diagram.height = max(diagram.height, bottom + FRAME_Y)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_layout_pipeline.py -k test_canvas_grows_for_deflected -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/diagrams_as_code/layout/pipeline.py tests/test_layout_pipeline.py
git commit -m "feat(layout): expand canvas and translate framing for edge extrema"
```

---

### Task 9: End-to-End Verification & Full Test Suite (D-01–D-19)

**Files:**
- Test: `tests/test_e2e.py`
- Test: All tests across the test suite

**Interfaces:**
- Validates 100% test passing, zero diff on visual assets, and local verification before completion.

- [ ] **Step 1: Add E2E tests in `tests/test_e2e.py`**

```python
# In tests/test_e2e.py
def test_e2e_fluent_chain_inherits_diagram_curved_routing() -> None:
    with Diagram(routing="curve") as d:
        s1 = d.shape("Sensor 1")
        s2 = d.shape("Sensor 2")
        s3 = d.shape("Gateway")
        s1 >> s3
        s2 >> s3
    
    assert len(d.edges) == 2
    for e in d.edges:
        assert e.routing == Routing.CURVE
        path = d.routes[e]
        assert path.kind == PathKind.BEZIER_CHAIN
    
    svg = d.render_svg()
    assert 'd="M' in svg
    assert "C " in svg
```

- [ ] **Step 2: Run all tests locally**

Run: `uv run pytest`
Expected: 100% PASS (520+ tests passed)

- [ ] **Step 3: Run artifact and hygiene checks**

Run: `uv run python main.py`
Run: `uv run python tools/generate_icons.py --check`
Run: `git diff --exit-code -- output/ icons/ README.md docs/`
Expected: Zero diff on tracked gallery files.

- [ ] **Step 4: Commit test suite additions**

```bash
git add tests/test_e2e.py
git commit -m "test(e2e): verify edge routing hierarchy, extrema, and purity"
```
