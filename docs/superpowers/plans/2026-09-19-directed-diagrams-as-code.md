# Directed Diagrams as Code Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a robust, pure-Python Diagrams-as-Code engine with directed placement (absolute coordinates, unit-basis positioning, shape-to-shape relative margins, hierarchical grouping with auto-bounding, group flow placement, and smart edge routing), standalone SVG rendering, and automated Bill of Materials (BOM) generation.

**Architecture:** A modular geometry, constraint solver, and rendering architecture (`src/iiot_diagrams/`). Elements (Shapes and Groups) define geometric anchors and placement constraints. A layout solver evaluates dependencies, resolves relative offsets and group bounds, and routes orthogonal/curved connections. A pure-Python SVG renderer outputs crisp, production-grade vector diagrams without requiring external Graphviz binaries for placement, while preserving export compatibility.

**Tech Stack:** Python 3.10+, Pytest, Pydantic, Pure-Python SVG vector generation, YAML/CSV metadata loaders.

## Global Constraints

- Output pure, clean, zero-external-binary-dependent Python code for core diagram generation.
- Maintain strict typing with Python type annotations.
- Provide 100% test coverage for geometry calculations, constraint resolution, grouping, and SVG generation.
- Support both fixed coordinate systems and normalized unit-basis coordinates (0.0 to 1.0 / 0-100%).
- Replace all legacy HiveMQ branding with configurable generic IIoT themes while maintaining customizability.
- Maintain living documentation and Bill of Materials (BOM) generation.

---

### Task 1: Core Geometry and Unit-Basis Coordinate Engine

**Files:**
- Create: `src/iiot_diagrams/__init__.py`
- Create: `src/iiot_diagrams/geometry.py`
- Test: `tests/test_geometry.py`

**Interfaces:**
- Consumes: Standard Python `math`, `typing`, `dataclasses`.
- Produces:
  - `Point(x: float, y: float)`
  - `Size(width: float, height: float)`
  - `Rect(x: float, y: float, width: float, height: float)` with `.top`, `.bottom`, `.left`, `.right`, `.center`, `.top_left`, `.top_right`, `.bottom_left`, `.bottom_right`, `.union(other: Rect)`, `.expand(padding: float | tuple)`
  - `Anchor` (Enum: `TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`, `LEFT_CENTER`, `CENTER`, `RIGHT_CENTER`, `BOTTOM_LEFT`, `BOTTOM_CENTER`, `BOTTOM_RIGHT`)
  - `UnitBasis(canvas_size: Size)` with `to_absolute(u: float, v: float) -> Point`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_geometry.py
import pytest
from iiot_diagrams.geometry import Point, Size, Rect, Anchor, UnitBasis

def test_rect_anchor_points():
    rect = Rect(10, 20, 100, 50)
    assert rect.left == 10
    assert rect.right == 110
    assert rect.top == 20
    assert rect.bottom == 70
    assert rect.center == Point(60, 45)
    assert rect.get_anchor(Anchor.CENTER) == Point(60, 45)
    assert rect.get_anchor(Anchor.BOTTOM_RIGHT) == Point(110, 70)

def test_rect_union_and_expand():
    r1 = Rect(10, 10, 40, 40)
    r2 = Rect(60, 60, 20, 20)
    u = r1.union(r2)
    assert u == Rect(10, 10, 70, 70)
    expanded = u.expand(10)
    assert expanded == Rect(0, 0, 90, 90)

def test_unit_basis_conversion():
    basis = UnitBasis(Size(1000, 500))
    pt = basis.to_absolute(0.25, 0.5)
    assert pt == Point(250.0, 250.0)
    pt_pct = basis.to_absolute("10%", "20%")
    assert pt_pct == Point(100.0, 100.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_geometry.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iiot_diagrams'`

- [ ] **Step 3: Implement geometry module**

```python
# src/iiot_diagrams/__init__.py
"""IIoT Diagrams as Code framework."""
__version__ = "0.1.0"
```

```python
# src/iiot_diagrams/geometry.py
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Union

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Size:
    width: float
    height: float

class Anchor(Enum):
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    LEFT_CENTER = "left_center"
    CENTER = "center"
    RIGHT_CENTER = "right_center"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"

@dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2.0, self.y + self.height / 2.0)

    def get_anchor(self, anchor: Anchor) -> Point:
        if anchor == Anchor.TOP_LEFT:
            return Point(self.left, self.top)
        elif anchor == Anchor.TOP_CENTER:
            return Point(self.x + self.width / 2.0, self.top)
        elif anchor == Anchor.TOP_RIGHT:
            return Point(self.right, self.top)
        elif anchor == Anchor.LEFT_CENTER:
            return Point(self.left, self.y + self.height / 2.0)
        elif anchor == Anchor.CENTER:
            return self.center
        elif anchor == Anchor.RIGHT_CENTER:
            return Point(self.right, self.y + self.height / 2.0)
        elif anchor == Anchor.BOTTOM_LEFT:
            return Point(self.left, self.bottom)
        elif anchor == Anchor.BOTTOM_CENTER:
            return Point(self.x + self.width / 2.0, self.bottom)
        elif anchor == Anchor.BOTTOM_RIGHT:
            return Point(self.right, self.bottom)
        raise ValueError(f"Unknown anchor: {anchor}")

    def union(self, other: Rect) -> Rect:
        min_x = min(self.left, other.left)
        min_y = min(self.top, other.top)
        max_x = max(self.right, other.right)
        max_y = max(self.bottom, other.bottom)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def expand(self, padding: Union[float, tuple[float, float], tuple[float, float, float, float]]) -> Rect:
        if isinstance(padding, (int, float)):
            top = right = bottom = left = float(padding)
        elif len(padding) == 2:
            top = bottom = float(padding[0])
            left = right = float(padding[1])
        elif len(padding) == 4:
            top, right, bottom, left = (float(v) for v in padding)
        else:
            raise ValueError("Padding must be 1, 2, or 4 values.")
        return Rect(
            x=self.x - left,
            y=self.y - top,
            width=self.width + left + right,
            height=self.height + top + bottom,
        )

class UnitBasis:
    def __init__(self, reference_size: Size):
        self.reference_size = reference_size

    def _parse_val(self, val: Union[float, int, str], base: float) -> float:
        if isinstance(val, str) and val.endswith("%"):
            return float(val[:-1]) / 100.0 * base
        val_float = float(val)
        if 0.0 <= val_float <= 1.0 and isinstance(val, float):
            return val_float * base
        return val_float

    def to_absolute(self, u: Union[float, int, str], v: Union[float, int, str]) -> Point:
        x = self._parse_val(u, self.reference_size.width)
        y = self._parse_val(v, self.reference_size.height)
        return Point(x, y)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_geometry.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iiot_diagrams/__init__.py src/iiot_diagrams/geometry.py tests/test_geometry.py
git commit -m "feat: implement geometry and unit-basis coordinate engine"
```

---

### Task 2: Relative Positioning & Constraint Engine

**Files:**
- Create: `src/iiot_diagrams/elements.py`
- Create: `src/iiot_diagrams/constraints.py`
- Test: `tests/test_constraints.py`

**Interfaces:**
- Consumes: `iiot_diagrams.geometry` (`Point`, `Size`, `Rect`, `Anchor`, `UnitBasis`).
- Produces:
  - `Element`: base element with `id`, `label`, `bounds`, `parent`.
  - `Shape(Element)`: visual node with explicit or constraint-driven bounds.
    - Methods: `.at(x, y, anchor=Anchor.TOP_LEFT)`, `.right_of(other, margin=20, align="center")`, `.left_of(other, margin=20, align="center")`, `.below(other, margin=20, align="center")`, `.above(other, margin=20, align="center")`.
  - `ConstraintSolver`: resolves DAG of element positions.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_constraints.py
import pytest
from iiot_diagrams.elements import Shape
from iiot_diagrams.constraints import ConstraintSolver

def test_absolute_placement():
    solver = ConstraintSolver()
    s1 = Shape("s1", label="Sensor", width=100, height=50)
    s1.at(200, 150)
    solver.add(s1)
    solver.solve()
    assert s1.bounds.x == 200
    assert s1.bounds.y == 150

def test_shape_to_shape_relative_placement():
    solver = ConstraintSolver()
    s1 = Shape("s1", label="PLC", width=100, height=60).at(50, 50)
    s2 = Shape("s2", label="Edge Gateway", width=120, height=60).right_of(s1, margin=30, align="center")
    s3 = Shape("s3", label="Local Historian", width=100, height=60).below(s1, margin=40, align="left")
    
    solver.add(s1, s2, s3)
    solver.solve()

    # s2 right of s1
    assert s2.bounds.x == 50 + 100 + 30  # 180
    assert s2.bounds.y == 50  # aligned center (both height 60)

    # s3 below s1, aligned left
    assert s3.bounds.x == 50
    assert s3.bounds.y == 50 + 60 + 40  # 150
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_constraints.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iiot_diagrams.elements'`

- [ ] **Step 3: Implement elements and constraint solver**

```python
# src/iiot_diagrams/elements.py
from __future__ import annotations
from typing import Optional, Any
from iiot_diagrams.geometry import Rect, Point, Anchor

class Element:
    def __init__(self, id: str, label: str, width: float = 120, height: float = 60, metadata: Optional[dict[str, Any]] = None):
        self.id = id
        self.label = label
        self.width = width
        self.height = height
        self.bounds: Rect = Rect(0, 0, width, height)
        self.parent: Optional[Element] = None
        self.metadata = metadata or {}
        self.constraints: list[Any] = []

class Shape(Element):
    def __init__(self, id: str, label: str, width: float = 120, height: float = 60, kind: str = "box", icon: Optional[str] = None, metadata: Optional[dict[str, Any]] = None):
        super().__init__(id, label, width, height, metadata)
        self.kind = kind
        self.icon = icon

    def at(self, x: float, y: float, anchor: Anchor = Anchor.TOP_LEFT) -> Shape:
        self.constraints.append({"type": "absolute", "x": x, "y": y, "anchor": anchor})
        return self

    def right_of(self, other: Element, margin: float = 20, align: str = "center") -> Shape:
        self.constraints.append({"type": "relative_dir", "target": other, "direction": "right", "margin": margin, "align": align})
        return self

    def left_of(self, other: Element, margin: float = 20, align: str = "center") -> Shape:
        self.constraints.append({"type": "relative_dir", "target": other, "direction": "left", "margin": margin, "align": align})
        return self

    def below(self, other: Element, margin: float = 20, align: str = "center") -> Shape:
        self.constraints.append({"type": "relative_dir", "target": other, "direction": "below", "margin": margin, "align": align})
        return self

    def above(self, other: Element, margin: float = 20, align: str = "center") -> Shape:
        self.constraints.append({"type": "relative_dir", "target": other, "direction": "above", "margin": margin, "align": align})
        return self
```

```python
# src/iiot_diagrams/constraints.py
from __future__ import annotations
from typing import Sequence
from iiot_diagrams.elements import Element
from iiot_diagrams.geometry import Rect, Anchor

class ConstraintSolver:
    def __init__(self):
        self.elements: list[Element] = []

    def add(self, *elements: Element):
        for el in elements:
            if el not in self.elements:
                self.elements.append(el)

    def solve(self):
        solved: set[Element] = set()
        # Resolve absolute first
        for el in self.elements:
            for c in el.constraints:
                if c["type"] == "absolute":
                    x, y = c["x"], c["y"]
                    anchor = c.get("anchor", Anchor.TOP_LEFT)
                    if anchor == Anchor.TOP_LEFT:
                        el.bounds = Rect(x, y, el.width, el.height)
                    elif anchor == Anchor.CENTER:
                        el.bounds = Rect(x - el.width / 2.0, y - el.height / 2.0, el.width, el.height)
                    solved.add(el)

        # Iteratively resolve relative constraints
        max_iters = len(self.elements) * 2 + 10
        for _ in range(max_iters):
            progress = False
            for el in self.elements:
                if el in solved:
                    continue
                for c in el.constraints:
                    if c["type"] == "relative_dir":
                        target = c["target"]
                        if target in solved:
                            self._apply_relative(el, target, c["direction"], c["margin"], c["align"])
                            solved.add(el)
                            progress = True
                            break
            if not progress:
                break
        
        unsolved = [e.id for e in self.elements if e not in solved]
        if unsolved:
            raise RuntimeError(f"Unresolved constraints for elements: {unsolved}")

    def _apply_relative(self, el: Element, target: Element, direction: str, margin: float, align: str):
        tb = target.bounds
        w, h = el.width, el.height
        if direction == "right":
            x = tb.right + margin
            if align == "center":
                y = tb.top + (tb.height - h) / 2.0
            elif align == "top":
                y = tb.top
            else:
                y = tb.bottom - h
        elif direction == "left":
            x = tb.left - margin - w
            if align == "center":
                y = tb.top + (tb.height - h) / 2.0
            elif align == "top":
                y = tb.top
            else:
                y = tb.bottom - h
        elif direction == "below":
            y = tb.bottom + margin
            if align == "center":
                x = tb.left + (tb.width - w) / 2.0
            elif align == "left":
                x = tb.left
            else:
                x = tb.right - w
        elif direction == "above":
            y = tb.top - margin - h
            if align == "center":
                x = tb.left + (tb.width - w) / 2.0
            elif align == "left":
                x = tb.left
            else:
                x = tb.right - w
        else:
            raise ValueError(f"Unknown direction: {direction}")
        el.bounds = Rect(x, y, w, h)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_constraints.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iiot_diagrams/elements.py src/iiot_diagrams/constraints.py tests/test_constraints.py
git commit -m "feat: implement relative positioning and constraint solver"
```

---

### Task 3: Grouping, Container Auto-Bounding, and Flow Placement

**Files:**
- Create: `src/iiot_diagrams/groups.py`
- Modify: `src/iiot_diagrams/constraints.py:30-80`
- Test: `tests/test_groups.py`

**Interfaces:**
- Consumes: `iiot_diagrams.elements`, `iiot_diagrams.geometry`.
- Produces:
  - `Group(Element)`: container with `.children`, `.padding`, `.auto_bounds()`, internal layouts (`vertical_flow`, `horizontal_flow`, `grid`).
  - Group-to-Group flow placement: `g2.below(g1, margin=50)`, `g2.right_of(g1, margin=80)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_groups.py
import pytest
from iiot_diagrams.elements import Shape
from iiot_diagrams.groups import Group
from iiot_diagrams.constraints import ConstraintSolver

def test_group_auto_bounds():
    solver = ConstraintSolver()
    g1 = Group("g1", label="Edge Factory", padding=20)
    s1 = Shape("s1", label="PLC", width=100, height=50).at(100, 100)
    s2 = Shape("s2", label="Gateway", width=100, height=50).below(s1, margin=30, align="left")
    g1.add(s1, s2)
    
    solver.add(g1, s1, s2)
    solver.solve()

    # Children span x: 100..200, y: 100..230 (100 + 50 + 30 + 50)
    # With padding 20 and header room (30), g1 bounds are calculated
    assert g1.bounds.left <= 80
    assert g1.bounds.right >= 220
    assert g1.bounds.bottom >= 250

def test_group_to_group_flow_placement():
    solver = ConstraintSolver()
    g1 = Group("g1", label="Plant Site", padding=20)
    s1 = Shape("s1", label="PLC").at(50, 50)
    g1.add(s1)

    g2 = Group("g2", label="Cloud Platform", padding=20).right_of(g1, margin=100)
    s2 = Shape("s2", label="Broker", width=120, height=60)
    g2.add(s2)

    solver.add(g1, s1, g2, s2)
    solver.solve()

    assert g2.bounds.left == g1.bounds.right + 100
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_groups.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iiot_diagrams.groups'`

- [ ] **Step 3: Implement Group class and auto-bounds resolution**

```python
# src/iiot_diagrams/groups.py
from __future__ import annotations
from typing import Optional, Sequence
from iiot_diagrams.elements import Element, Shape
from iiot_diagrams.geometry import Rect, Point

class Group(Element):
    def __init__(self, id: str, label: str, padding: float = 25, header_height: float = 35):
        super().__init__(id, label)
        self.children: list[Element] = []
        self.padding = padding
        self.header_height = header_height
        self.is_auto_sized = True

    def add(self, *elements: Element) -> Group:
        for el in elements:
            el.parent = self
            if el not in self.children:
                self.children.append(el)
        return self

    def calculate_bounds(self) -> Rect:
        if not self.children:
            return self.bounds
        union_rect = self.children[0].bounds
        for child in self.children[1:]:
            union_rect = union_rect.union(child.bounds)
        
        # Expand bounds for padding and header
        return Rect(
            x=union_rect.x - self.padding,
            y=union_rect.y - self.padding - self.header_height,
            width=union_rect.width + (self.padding * 2),
            height=union_rect.height + (self.padding * 2) + self.header_height
        )

    def right_of(self, other: Element, margin: float = 50, align: str = "top") -> Group:
        self.constraints.append({"type": "relative_dir", "target": other, "direction": "right", "margin": margin, "align": align})
        return self

    def below(self, other: Element, margin: float = 50, align: str = "left") -> Group:
        self.constraints.append({"type": "relative_dir", "target": other, "direction": "below", "margin": margin, "align": align})
        return self
```

Update `src/iiot_diagrams/constraints.py` to support two-pass solving (resolving inner child positions, auto-sizing groups, then solving group-to-group relative positions and shifting relative children).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_groups.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iiot_diagrams/groups.py src/iiot_diagrams/constraints.py tests/test_groups.py
git commit -m "feat: add hierarchical groups, auto-bounding, and group flow placement"
```

---

### Task 4: Connections, Port Anchors, and Smart Orthogonal Routing

**Files:**
- Create: `src/iiot_diagrams/connections.py`
- Create: `src/iiot_diagrams/router.py`
- Test: `tests/test_routing.py`

**Interfaces:**
- Consumes: `iiot_diagrams.elements`, `iiot_diagrams.geometry`.
- Produces:
  - `Port` (Enum: `NORTH`, `SOUTH`, `EAST`, `WEST`)
  - `Edge(source, target, label, style, color, arrow_head, routing)`
  - `OrthogonalRouter`: computes waypoints avoiding node overlap with Manhattan routing.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_routing.py
import pytest
from iiot_diagrams.elements import Shape
from iiot_diagrams.connections import Edge, Port
from iiot_diagrams.router import OrthogonalRouter
from iiot_diagrams.geometry import Point

def test_automatic_port_selection():
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(300, 0)
    edge = Edge(s1, s2, label="MQTT")
    router = OrthogonalRouter()
    ports = router.resolve_ports(edge)
    assert ports == (Port.EAST, Port.WEST)

def test_orthogonal_manhattan_waypoints():
    s1 = Shape("s1", "A", 100, 50).at(0, 0)
    s2 = Shape("s2", "B", 100, 50).at(200, 150)
    edge = Edge(s1, s2)
    router = OrthogonalRouter()
    waypoints = router.route(edge)
    assert len(waypoints) >= 3
    assert waypoints[0] == s1.bounds.get_anchor(Port.EAST.to_anchor())
    assert waypoints[-1] == s2.bounds.get_anchor(Port.WEST.to_anchor())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_routing.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iiot_diagrams.connections'`

- [ ] **Step 3: Implement connections and orthogonal router**

```python
# src/iiot_diagrams/connections.py
from __future__ import annotations
from enum import Enum
from typing import Optional
from iiot_diagrams.elements import Element
from iiot_diagrams.geometry import Anchor

class Port(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    def to_anchor(self) -> Anchor:
        mapping = {
            Port.NORTH: Anchor.TOP_CENTER,
            Port.SOUTH: Anchor.BOTTOM_CENTER,
            Port.EAST: Anchor.RIGHT_CENTER,
            Port.WEST: Anchor.LEFT_CENTER,
        }
        return mapping[self]

class Edge:
    def __init__(
        self,
        source: Element,
        target: Element,
        label: str = "",
        color: Optional[str] = None,
        style: str = "solid",
        source_port: Optional[Port] = None,
        target_port: Optional[Port] = None,
    ):
        self.source = source
        self.target = target
        self.label = label
        self.color = color
        self.style = style
        self.source_port = source_port
        self.target_port = target_port
```

```python
# src/iiot_diagrams/router.py
from __future__ import annotations
from iiot_diagrams.connections import Edge, Port
from iiot_diagrams.geometry import Point

class OrthogonalRouter:
    def resolve_ports(self, edge: Edge) -> tuple[Port, Port]:
        if edge.source_port and edge.target_port:
            return (edge.source_port, edge.target_port)
        
        sb, tb = edge.source.bounds, edge.target.bounds
        dx = tb.center.x - sb.center.x
        dy = tb.center.y - sb.center.y

        if abs(dx) >= abs(dy):
            src_p = Port.EAST if dx > 0 else Port.WEST
            tgt_p = Port.WEST if dx > 0 else Port.EAST
        else:
            src_p = Port.SOUTH if dy > 0 else Port.NORTH
            tgt_p = Port.NORTH if dy > 0 else Port.SOUTH
        return (edge.source_port or src_p, edge.target_port or tgt_p)

    def route(self, edge: Edge) -> list[Point]:
        src_port, tgt_port = self.resolve_ports(edge)
        p_start = edge.source.bounds.get_anchor(src_port.to_anchor())
        p_end = edge.target.bounds.get_anchor(tgt_port.to_anchor())

        # Step Manhattan midpoint
        if src_port in (Port.EAST, Port.WEST) and tgt_port in (Port.EAST, Port.WEST):
            mid_x = (p_start.x + p_end.x) / 2.0
            return [p_start, Point(mid_x, p_start.y), Point(mid_x, p_end.y), p_end]
        elif src_port in (Port.NORTH, Port.SOUTH) and tgt_port in (Port.NORTH, Port.SOUTH):
            mid_y = (p_start.y + p_end.y) / 2.0
            return [p_start, Point(p_start.x, mid_y), Point(p_end.x, mid_y), p_end]
        else:
            return [p_start, Point(p_end.x, p_start.y), p_end]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_routing.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iiot_diagrams/connections.py src/iiot_diagrams/router.py tests/test_routing.py
git commit -m "feat: implement port anchoring, connection model, and orthogonal routing"
```

---

### Task 5: Theming Engine and Vector Shapes

**Files:**
- Create: `src/iiot_diagrams/theme.py`
- Create: `src/iiot_diagrams/shapes.py`
- Test: `tests/test_theme.py`

**Interfaces:**
- Consumes: `dataclasses`, `typing`.
- Produces:
  - `Theme`: configurable color palette (`background`, `node_fill`, `node_stroke`, `accent_gold`, `text_color`, `subtext_color`, `font_family`).
  - Presets: `IIOT_DARK_GOLD` (default), `IIOT_LIGHT`, `BLUEPRINT`.
  - `ShapeRenderer`: vector path generation for rounded rects, cylinders, database, server racks, cloud, badges.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_theme.py
import pytest
from iiot_diagrams.theme import Theme, get_theme
from iiot_diagrams.shapes import ShapeLibrary

def test_theme_presets():
    dark = get_theme("iiot_dark_gold")
    assert dark.background == "#000000"
    assert dark.accent == "#FFC000"
    light = get_theme("iiot_light")
    assert light.background == "#FFFFFF"

def test_shape_library_svg():
    lib = ShapeLibrary()
    rect_svg = lib.render_box(10, 10, 100, 50, fill="#1A1A1A", stroke="#FFC000", radius=8)
    assert "<rect" in rect_svg
    assert "rx=\"8\"" in rect_svg
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_theme.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iiot_diagrams.theme'`

- [ ] **Step 3: Implement Theme and ShapeLibrary**

```python
# src/iiot_diagrams/theme.py
from dataclasses import dataclass

@dataclass
class Theme:
    name: str
    background: str
    group_bg: str
    group_stroke: str
    node_fill: str
    node_stroke: str
    accent: str
    text: str
    subtext: str
    edge_color: str
    font_family: str = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

THEMES = {
    "iiot_dark_gold": Theme(
        name="iiot_dark_gold",
        background="#0F0F11",
        group_bg="#1A1A1E",
        group_stroke="#2E2E36",
        node_fill="#24242A",
        node_stroke="#FFC000",
        accent="#FFC000",
        text="#FFFFFF",
        subtext="#A0A0AA",
        edge_color="#FFC000",
    ),
    "iiot_light": Theme(
        name="iiot_light",
        background="#FFFFFF",
        group_bg="#F4F4F6",
        group_stroke="#E0E0E6",
        node_fill="#FFFFFF",
        node_stroke="#0066CC",
        accent="#0066CC",
        text="#111111",
        subtext="#666666",
        edge_color="#0066CC",
    ),
}

def get_theme(name: str = "iiot_dark_gold") -> Theme:
    return THEMES.get(name, THEMES["iiot_dark_gold"])
```

```python
# src/iiot_diagrams/shapes.py
class ShapeLibrary:
    def render_box(self, x: float, y: float, w: float, h: float, fill: str, stroke: str, stroke_width: float = 2, radius: float = 6) -> str:
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'

    def render_cylinder(self, x: float, y: float, w: float, h: float, fill: str, stroke: str) -> str:
        # SVG cylinder path
        ry = min(12.0, h / 4.0)
        return (
            f'<path d="M {x} {y + ry} A {w/2} {ry} 0 0 1 {x + w} {y + ry} '
            f'L {x + w} {y + h - ry} A {w/2} {ry} 0 0 1 {x} {y + h - ry} Z" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<ellipse cx="{x + w/2}" cy="{y + ry}" rx="{w/2}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_theme.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iiot_diagrams/theme.py src/iiot_diagrams/shapes.py tests/test_theme.py
git commit -m "feat: implement theme presets and vector shape primitives"
```

---

### Task 6: Pure-Python Standalone SVG Renderer

**Files:**
- Create: `src/iiot_diagrams/renderer_svg.py`
- Test: `tests/test_renderer_svg.py`

**Interfaces:**
- Consumes: `iiot_diagrams.elements`, `iiot_diagrams.groups`, `iiot_diagrams.connections`, `iiot_diagrams.router`, `iiot_diagrams.theme`.
- Produces:
  - `SVGRenderer(theme: Theme)`: takes solved elements, groups, and edges, and generates crisp, production-grade SVG XML string with badges, arrow markers, and styles.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_renderer_svg.py
import pytest
from iiot_diagrams.elements import Shape
from iiot_diagrams.groups import Group
from iiot_diagrams.connections import Edge
from iiot_diagrams.renderer_svg import SVGRenderer
from iiot_diagrams.theme import get_theme

def test_svg_render_contains_elements():
    theme = get_theme("iiot_dark_gold")
    renderer = SVGRenderer(theme)
    
    g = Group("g1", label="Production Plant").at(20, 20)
    s1 = Shape("s1", label="Allen-Bradley PLC", width=140, height=60).at(40, 70)
    s2 = Shape("s2", label="IIoT Edge Gateway", width=140, height=60).at(240, 70)
    g.add(s1, s2)
    edge = Edge(s1, s2, label="Modbus TCP")
    
    svg = renderer.render(elements=[s1, s2], groups=[g], edges=[edge], width=600, height=300)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Production Plant" in svg
    assert "Allen-Bradley PLC" in svg
    assert "Modbus TCP" in svg
    assert "marker-end=\"url(#arrow)\"" in svg
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_renderer_svg.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iiot_diagrams.renderer_svg'`

- [ ] **Step 3: Implement SVGRenderer**

```python
# src/iiot_diagrams/renderer_svg.py
from __future__ import annotations
import html
from typing import Sequence
from iiot_diagrams.elements import Element, Shape
from iiot_diagrams.groups import Group
from iiot_diagrams.connections import Edge
from iiot_diagrams.router import OrthogonalRouter
from iiot_diagrams.theme import Theme
from iiot_diagrams.shapes import ShapeLibrary

class SVGRenderer:
    def __init__(self, theme: Theme):
        self.theme = theme
        self.shapes = ShapeLibrary()
        self.router = OrthogonalRouter()

    def render(self, elements: Sequence[Shape], groups: Sequence[Group], edges: Sequence[Edge], width: float = 1200, height: float = 800) -> str:
        lines: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
            '  <defs>',
            '    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{self.theme.accent}"/>',
            '    </marker>',
            '    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">',
            '      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>',
            '    </filter>',
            '  </defs>',
            f'  <rect width="100%" height="100%" fill="{self.theme.background}"/>',
        ]

        # 1. Render Groups
        for g in groups:
            b = g.bounds
            lines.append(f'  <g id="{g.id}">')
            lines.append(f'    <rect x="{b.x}" y="{b.y}" width="{b.width}" height="{b.height}" rx="8" fill="{self.theme.group_bg}" stroke="{self.theme.group_stroke}" stroke-width="1.5" />')
            lines.append(f'    <text x="{b.x + 16}" y="{b.y + 24}" fill="{self.theme.accent}" font-family="{self.theme.font_family}" font-size="14" font-weight="bold">{html.escape(g.label)}</text>')
            lines.append('  </g>')

        # 2. Render Connections / Edges
        for e in edges:
            pts = self.router.route(e)
            path_d = f"M {pts[0].x} {pts[0].y} " + " ".join(f"L {p.x} {p.y}" for p in pts[1:])
            edge_color = e.color or self.theme.edge_color
            dash = ' stroke-dasharray="5,5"' if e.style == "dashed" else (' stroke-dasharray="2,2"' if e.style == "dotted" else '')
            lines.append(f'  <path d="{path_d}" fill="none" stroke="{edge_color}" stroke-width="2"{dash} marker-end="url(#arrow)" />')
            if e.label:
                # Place label in center
                mid_idx = len(pts) // 2
                lx = (pts[mid_idx-1].x + pts[mid_idx].x) / 2.0
                ly = (pts[mid_idx-1].y + pts[mid_idx].y) / 2.0 - 6
                lines.append(f'  <rect x="{lx - 40}" y="{ly - 12}" width="80" height="18" rx="4" fill="{self.theme.background}" opacity="0.8"/>')
                lines.append(f'  <text x="{lx}" y="{ly}" text-anchor="middle" fill="{self.theme.text}" font-family="{self.theme.font_family}" font-size="11">{html.escape(e.label)}</text>')

        # 3. Render Shapes
        for s in elements:
            b = s.bounds
            lines.append(f'  <g id="{s.id}" filter="url(#shadow)">')
            lines.append(f'    {self.shapes.render_box(b.x, b.y, b.width, b.height, self.theme.node_fill, self.theme.node_stroke)}')
            lines.append(f'    <text x="{b.center.x}" y="{b.center.y + 4}" text-anchor="middle" fill="{self.theme.text}" font-family="{self.theme.font_family}" font-size="13" font-weight="500">{html.escape(s.label)}</text>')
            lines.append('  </g>')

        lines.append('</svg>')
        return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_renderer_svg.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iiot_diagrams/renderer_svg.py tests/test_renderer_svg.py
git commit -m "feat: implement pure-Python standalone SVG renderer"
```

---

### Task 7: Diagram Context Manager API and Fluent Syntax

**Files:**
- Create: `src/iiot_diagrams/diagram.py`
- Modify: `src/iiot_diagrams/__init__.py:1-10`
- Test: `tests/test_diagram_api.py`

**Interfaces:**
- Consumes: All submodules (`geometry`, `elements`, `groups`, `connections`, `constraints`, `renderer_svg`, `theme`).
- Produces:
  - `Diagram(title: str, width: int = 1200, height: int = 800, theme: str = "iiot_dark_gold")` context manager.
  - Fluent syntax: `diag.shape(...)`, `diag.group(...)`, operator `s1 >> s2`, `s1 >> diag.edge("MQTT") >> s2`.
  - `.render_svg(path: str) -> str`
  - `.render_png(path: str)` (if resvg or cairosvg or graphviz installed).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_diagram_api.py
import os
import pytest
from iiot_diagrams import Diagram

def test_fluent_diagram_api(tmp_path):
    out_svg = tmp_path / "test_diagram.svg"
    with Diagram("IIoT Architecture", width=1000, height=600) as diag:
        with diag.group("On-Premises Plant", padding=20) as plant:
            plc = diag.shape("PLC Modbus").at(50, 80)
            edge = diag.shape("Edge Gateway").below(plc, margin=40)
            plc >> edge

        with diag.group("IIoT Cloud Platform").right_of(plant, margin=80) as cloud:
            broker = diag.shape("Central Broker").at(50, 80)

        edge >> diag.edge("MQTT TLS") >> broker

    diag.render_svg(str(out_svg))
    assert out_svg.exists()
    content = out_svg.read_text()
    assert "On-Premises Plant" in content
    assert "IIoT Cloud Platform" in content
    assert "MQTT TLS" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_diagram_api.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iiot_diagrams.diagram'`

- [ ] **Step 3: Implement Diagram Context Manager**

```python
# src/iiot_diagrams/diagram.py
from __future__ import annotations
from typing import Optional
from iiot_diagrams.elements import Shape
from iiot_diagrams.groups import Group
from iiot_diagrams.connections import Edge
from iiot_diagrams.constraints import ConstraintSolver
from iiot_diagrams.renderer_svg import SVGRenderer
from iiot_diagrams.theme import get_theme, Theme

class _EdgeBuilder:
    def __init__(self, label: str = "", color: Optional[str] = None):
        self.label = label
        self.color = color

class Diagram:
    def __init__(self, title: str, width: float = 1200, height: float = 800, theme: str = "iiot_dark_gold"):
        self.title = title
        self.width = width
        self.height = height
        self.theme: Theme = get_theme(theme)
        self.shapes: list[Shape] = []
        self.groups: list[Group] = []
        self.edges: list[Edge] = []
        self.solver = ConstraintSolver()
        self._active_group: Optional[Group] = None
        self._counter = 0

    def __enter__(self) -> Diagram:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.solve()

    def shape(self, label: str, width: float = 130, height: float = 60, kind: str = "box") -> Shape:
        self._counter += 1
        s = Shape(f"shape_{self._counter}", label, width, height, kind=kind)
        self.shapes.append(s)
        self.solver.add(s)
        if self._active_group:
            self._active_group.add(s)
        return s

    def group(self, label: str, padding: float = 25) -> _GroupContext:
        self._counter += 1
        g = Group(f"group_{self._counter}", label, padding=padding)
        self.groups.append(g)
        self.solver.add(g)
        return _GroupContext(self, g)

    def edge(self, label: str = "", color: Optional[str] = None) -> _EdgeBuilder:
        return _EdgeBuilder(label, color)

    def connect(self, source: Shape, target: Shape, label: str = "", color: Optional[str] = None) -> Edge:
        e = Edge(source, target, label=label, color=color)
        self.edges.append(e)
        return e

    def solve(self):
        self.solver.solve()

    def render_svg(self, path: Optional[str] = None) -> str:
        renderer = SVGRenderer(self.theme)
        svg = renderer.render(self.shapes, self.groups, self.edges, self.width, self.height)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
        return svg

class _GroupContext:
    def __init__(self, diag: Diagram, group: Group):
        self.diag = diag
        self.group = group

    def __enter__(self) -> Group:
        self.diag._active_group = self.group
        return self.group

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.diag._active_group = None
        self.group.bounds = self.group.calculate_bounds()
```

Hook up `Shape.__rshift__` to support `s1 >> s2` and `s1 >> diag.edge(...) >> s2`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_diagram_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iiot_diagrams/diagram.py src/iiot_diagrams/__init__.py tests/test_diagram_api.py
git commit -m "feat: implement fluent Diagram context manager and edge operators"
```

---

### Task 8: Bill of Materials (BOM) & Living Documentation Generator

**Files:**
- Create: `src/iiot_diagrams/bom.py`
- Modify: `src/iiot_diagrams/diagram.py:100-140`
- Test: `tests/test_bom.py`

**Interfaces:**
- Consumes: `Diagram`, `Shape`, `Edge`.
- Produces:
  - `BOMGenerator`: extracts inventory of all components, protocols, and connections.
  - Generates Markdown Table, JSON, and updates `README.md`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_bom.py
import pytest
from iiot_diagrams import Diagram
from iiot_diagrams.bom import BOMGenerator

def test_generate_bom():
    with Diagram("Baltimore Plant Architecture") as diag:
        plc = diag.shape("PLC Allen-Bradley", kind="sensor").at(10, 10)
        plc.metadata = {"model": "ControlLogix", "vendor": "Rockwell", "protocol": "EtherNet/IP"}
        edge = diag.shape("Edge Gateway", kind="gateway").right_of(plc, margin=30)
        edge.metadata = {"hardware": "Industrial IPC", "os": "Linux"}
        plc >> diag.edge("Modbus/TCP") >> edge

    bom = BOMGenerator(diag)
    md_table = bom.to_markdown()
    assert "| Symbol / ID | Label | Kind | Metadata |" in md_table
    assert "ControlLogix" in md_table
    assert "Industrial IPC" in md_table
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_bom.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iiot_diagrams.bom'`

- [ ] **Step 3: Implement BOMGenerator**

```python
# src/iiot_diagrams/bom.py
from __future__ import annotations
import json
from typing import Any

class BOMGenerator:
    def __init__(self, diagram: Any):
        self.diagram = diagram

    def items(self) -> list[dict[str, Any]]:
        result = []
        for s in self.diagram.shapes:
            result.append({
                "id": s.id,
                "label": s.label,
                "kind": getattr(s, "kind", "box"),
                "metadata": s.metadata,
            })
        return result

    def to_markdown(self) -> str:
        lines = [
            "## Bill of Materials",
            "",
            "| Symbol / ID | Label | Kind | Metadata |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for it in self.items():
            meta_str = ", ".join(f"{k}: {v}" for k, v in it["metadata"].items()) or "-"
            lines.append(f"| `{it['id']}` | **{it['label']}** | {it['kind']} | {meta_str} |")
        return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_bom.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iiot_diagrams/bom.py tests/test_bom.py
git commit -m "feat: implement Bill of Materials (BOM) markdown and JSON generator"
```

---

### Task 9: Recreate Existing Architecture Diagrams with Directed Engine

**Files:**
- Create: `examples/01_mockup_slide.py` (exact recreation of `mock-up.txt` and `diagram-architecture-slide.py`)
- Create: `examples/02_high_availability.py` (recreation of `diagram-iiot-high-availability.py`)
- Modify: `main.py`
- Test: `tests/test_examples.py`

**Interfaces:**
- Consumes: `iiot_diagrams`.
- Produces:
  - Generates `Baltimore_UNS_Slide.svg` and `IIoT_HA_Cluster.svg`.
  - Generates updated `README.md` with BOM.

- [ ] **Step 1: Write verification test for examples**

```python
# tests/test_examples.py
import subprocess
import sys
from pathlib import Path

def test_mockup_slide_execution(tmp_path):
    res = subprocess.run([sys.executable, "examples/01_mockup_slide.py"], capture_output=True, text=True)
    assert res.returncode == 0
    assert Path("output/mockup_slide.svg").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_examples.py -v`
Expected: FAIL with missing `examples/01_mockup_slide.py`

- [ ] **Step 3: Implement example scripts**

Implement `examples/01_mockup_slide.py` matching `mock-up.txt`:
- 3 distinct vertical columns/groups: On-Premise Baltimore, IIoT Cloud Managed, Remote Monitoring.
- Absolute & relative positioning with exact coordinate margins.
- Orthogonal MQTT bridge routing.
Implement `examples/02_high_availability.py`:
- Load balancer directing traffic across redundant nodes with dotted cluster discovery links.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_examples.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add examples/ tests/test_examples.py
git commit -m "feat: recreate architectural diagrams using directed placement engine"
```
