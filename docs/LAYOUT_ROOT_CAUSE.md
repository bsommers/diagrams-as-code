# Root Cause Analysis & Resolution: Diagram Layout Stacking

## 1. Problem Description

When inspecting rendered architecture outputs across the domain gallery, diagrams appeared stacked or collapsed into the upper corner of the canvas. Visual components, shapes, and group bounding boxes were rendered on top of each other at coordinate origin `(0.0, 0.0)` rather than flowing horizontally and vertically according to the defined layout constraints.

---

## 2. Root Cause Analysis

Thorough tracing identified three interdependent root causes across the rendering pipeline and example script generation:

### Cause 1: Pre-Exit Rendering Inside Context Manager
In the example generation templates, diagram rendering calls were placed **inside** the `with Diagram(...) as diag:` context block:
```python
with Diagram("Architecture", theme="blueprint") as diag:
    # ... group and shape definitions ...
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("arch.svg", readme_file)
```
In Python context managers, `Diagram.__exit__()` is responsible for invoking `self.solve()`. Because `diag.render_svg()` was invoked *before* exiting the `with` block, `self.solve()` had not yet been called.

### Cause 2: Lack of Auto-Solve Guard in Render Pipeline
Neither `Diagram.render_svg()` nor `Diagram.render_png()` guarded against un-solved diagrams. They directly handed `self.shapes` and `self.groups` to `SVGRenderer`. Because all `Shape` instances default to `Rect(0.0, 0.0, width, height)` upon instantiation, every un-solved element was rendered verbatim at `(0.0, 0.0)`.

### Cause 3: Negative Coordinate Clipping on Unanchored Groups
When a group auto-calculates bounds around children at `(0.0, 0.0)`, padding (`25.0`) and header room (`35.0`) expand the group bounds into negative coordinate space:
$$\text{min\_x} = 0.0 - 25.0 = -25.0$$
$$\text{min\_y} = 0.0 - 25.0 - 35.0 = -60.0$$
In standard SVG viewing (`viewBox="0 0 1200 800"`), negative coordinates are clipped outside the viewport, obscuring group headers and shifting elements towards the canvas boundary.

---

## 3. Implemented Solution

A multi-layered architectural fix was applied:

### Fix 1: Engine-Level Auto-Solve & Dirty Flag Tracking
In `src/diagrams_as_code/diagram.py`:
1. Added `self._is_solved: bool = False` tracking.
2. In `Diagram.render_svg()`, `Diagram.render_png()`, and `Diagram.generate_readme()`, added an automated solve check:
   ```python
   if not self._is_solved:
       self.solve()
   ```
   Even if a user or script calls `render_svg` inside a `with` block, the engine guarantees constraints are solved before vector generation.

### Fix 2: Canvas Framing for Negative Bounds
In `Diagram.solve()`:
If root elements possess negative coordinates (which would clip outside the SVG viewport), the solver translates the layout into positive canvas space with comfortable padding:
```python
all_elements = self.solver._collect_all_elements()
if all_elements:
    roots = [e for e in all_elements if getattr(e, "parent", None) is None]
    if roots:
        min_x = min(e.bounds.x for e in roots)
        min_y = min(e.bounds.y for e in roots)
        if min_x < 0.0 or min_y < 0.0:
            offset_x = max(0.0, -min_x + 60.0) if min_x < 0.0 else 0.0
            offset_y = max(0.0, -min_y + 80.0) if min_y < 0.0 else 0.0
            for r in roots:
                r.translate(offset_x, offset_y)
            for g in sorted_groups:
                if g.is_auto_sized and g.children:
                    g.calculate_bounds()
```

### Fix 3: Clean Context Manager Lifecycle in Examples
Refactored all domain example scripts across 8 domains:
1. Anchored the primary entry group: `g_1.at(60.0, 80.0)`.
2. Chained subsequent groups horizontally: `g_2.right_of(g_1, margin=50.0)`.
3. Moved `render_svg`, `render_png`, and `generate_readme` outside the `with` block.

---

## 4. Verification & Results

- **Automated Anti-Stacking Test Gate:** Added validation to `tests/test_domain_examples.py` asserting that no diagram renders with all shapes at `(0, 0)`.
- **Full Gallery Verification:** 80 / 80 domain diagrams verified properly positioned and centered.
- **Unit & Integration Suite:** 223 / 223 automated tests passing in 9.54s.
