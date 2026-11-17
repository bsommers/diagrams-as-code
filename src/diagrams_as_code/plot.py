"""Data-space plotting on a Diagram: axes, curves, regions, fields and bars.

``Plot`` owns a mapping from data coordinates to canvas pixels and draws with the
diagram's own primitives (paths, polylines, polygons, text), so a plot is an
ordinary part of a figure and takes part in lint, SVG and PDF output like any
other element. Pure standard library.

    with Diagram("Area under a curve", theme="paper") as d:
        p = Plot(d, x=(0, 4), y=(0, 3), origin=(80, 300), size=(400, 240))
        p.grid()
        p.axes(xlabel="$x$", ylabel="$y$")
        p.area(lambda x: x**0.5, 1, 3, fill="#DCE6F2")
        p.function(lambda x: x**0.5, stroke="#1F2F57")
"""
from __future__ import annotations

import math
from typing import Callable, Iterable, Optional, Sequence

from diagrams_as_code.diagram import Diagram
from diagrams_as_code.style import Style

Pt = tuple[float, float]

INK = "#1F2F57"
GRID = "#D9DDE6"


def nice_step(span: float, target: int = 6) -> float:
    """A 1/2/5 x 10^n tick step giving roughly ``target`` ticks over ``span``."""
    if span <= 0:
        return 1.0
    raw = span / max(target, 1)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def ticks(lo: float, hi: float, step: Optional[float] = None) -> list[float]:
    """Tick positions inside [lo, hi] on multiples of ``step``."""
    step = step or nice_step(hi - lo)
    first = math.ceil(lo / step - 1e-9)
    last = math.floor(hi / step + 1e-9)
    return [round(i * step, 10) for i in range(first, last + 1)]


def _fmt(v: float) -> str:
    if abs(v) < 1e-12:
        return "0"
    return f"{v:.6g}".replace("-", "−")


class Plot:
    """A rectangular data window drawn onto ``diagram``.

    ``x`` and ``y`` are the data ranges, ``origin`` the pixel of the window's
    bottom-left corner and ``size`` its pixel width and height. ``xscale`` and
    ``yscale`` may be ``"log"`` for positive ranges.
    """

    def __init__(
        self, diagram: Diagram, x: tuple[float, float], y: tuple[float, float],
        origin: Pt = (80.0, 320.0), size: Pt = (400.0, 260.0),
        xscale: str = "linear", yscale: str = "linear",
    ) -> None:
        for name, (lo, hi), scale in (("x", x, xscale), ("y", y, yscale)):
            if not lo < hi:
                raise ValueError(f"{name} range must have lo < hi, got {(lo, hi)}")
            if scale not in ("linear", "log"):
                raise ValueError(f"{name}scale must be 'linear' or 'log'")
            if scale == "log" and lo <= 0:
                raise ValueError(f"a log {name} axis needs a positive range")
        self.d = diagram
        self.x, self.y = x, y
        self.ox, self.oy = origin
        self.w, self.h = size
        self.xscale, self.yscale = xscale, yscale

    # ------------------------------------------------------------------ mapping
    @staticmethod
    def _unit(v: float, lo: float, hi: float, scale: str) -> float:
        if scale == "log":
            return (math.log(v) - math.log(lo)) / (math.log(hi) - math.log(lo))
        return (v - lo) / (hi - lo)

    def px(self, x: float, y: float) -> Pt:
        """Pixel position of data point (x, y)."""
        return (
            self.ox + self._unit(x, *self.x, self.xscale) * self.w,
            self.oy - self._unit(y, *self.y, self.yscale) * self.h,
        )

    def inside(self, p: Pt) -> bool:
        return self.x[0] - 1e-9 <= p[0] <= self.x[1] + 1e-9 and self.y[0] - 1e-9 <= p[1] <= self.y[1] + 1e-9

    def _clip_segment(self, a: Pt, b: Pt) -> Optional[tuple[Pt, Pt]]:
        """Liang-Barsky clip of segment ab to the data window."""
        t0, t1 = 0.0, 1.0
        dx, dy = b[0] - a[0], b[1] - a[1]
        for p, q in (
            (-dx, a[0] - self.x[0]), (dx, self.x[1] - a[0]),
            (-dy, a[1] - self.y[0]), (dy, self.y[1] - a[1]),
        ):
            if abs(p) < 1e-15:
                if q < 0:
                    return None
                continue
            t = q / p
            if p < 0:
                if t > t1:
                    return None
                t0 = max(t0, t)
            else:
                if t < t0:
                    return None
                t1 = min(t1, t)
        return (a[0] + t0 * dx, a[1] + t0 * dy), (a[0] + t1 * dx, a[1] + t1 * dy)

    def _runs(self, pts: Sequence[Optional[Pt]]) -> list[list[Pt]]:
        """Split a sample list into connected runs clipped to the window.

        ``None`` (or a non-finite point) breaks the curve, as at an asymptote.
        """
        runs: list[list[Pt]] = []
        cur: list[Pt] = []
        prev: Optional[Pt] = None
        for p in pts:
            if p is None or not (math.isfinite(p[0]) and math.isfinite(p[1])):
                if len(cur) > 1:
                    runs.append(cur)
                cur, prev = [], None
                continue
            if prev is not None:
                seg = self._clip_segment(prev, p)
                if seg is None:
                    if len(cur) > 1:
                        runs.append(cur)
                    cur = []
                else:
                    a, b = seg
                    if not cur or cur[-1] != a:
                        if len(cur) > 1:
                            runs.append(cur)
                        cur = [a]
                    cur.append(b)
                    if b != p:  # left the window: end the run here
                        runs.append(cur)
                        cur = []
            prev = p
        if len(cur) > 1:
            runs.append(cur)
        return runs

    # ------------------------------------------------------------------ frame
    def grid(self, xstep: Optional[float] = None, ystep: Optional[float] = None, color: str = GRID) -> None:
        """Light grid lines at the tick positions."""
        style = Style(fill="none", stroke=color, stroke_width=0.6)
        parts = []
        for tx in ticks(*self.x, xstep):
            a, b = self.px(tx, self.y[0]), self.px(tx, self.y[1])
            parts.append(f"M {a[0]:.2f} {a[1]:.2f} L {b[0]:.2f} {b[1]:.2f}")
        for ty in ticks(*self.y, ystep):
            a, b = self.px(self.x[0], ty), self.px(self.x[1], ty)
            parts.append(f"M {a[0]:.2f} {a[1]:.2f} L {b[0]:.2f} {b[1]:.2f}")
        if parts:
            self.d.path(" ".join(parts), style=style, z=-3)

    def axes(
        self, xlabel: str = "", ylabel: str = "", xstep: Optional[float] = None,
        ystep: Optional[float] = None, through_zero: bool = True, labels: bool = True,
        arrows: bool = True, size: float = 11,
    ) -> None:
        """Axes with tick marks and numeric labels.

        With ``through_zero`` the axes cross at the data origin when it lies in
        the window; otherwise they run along the bottom and left edges.
        """
        zx = 0.0 if through_zero and self.x[0] <= 0 <= self.x[1] and self.xscale == "linear" else self.x[0]
        zy = 0.0 if through_zero and self.y[0] <= 0 <= self.y[1] and self.yscale == "linear" else self.y[0]
        ax0, ax1 = self.px(self.x[0], zy), self.px(self.x[1], zy)
        ay0, ay1 = self.px(zx, self.y[0]), self.px(zx, self.y[1])
        head = "stealth" if arrows else "none"
        opts = {"routing": "direct", "width": 1.2, "head": head}
        self.d.connect(ax0, (ax1[0] + 12, ax1[1]), **opts)
        self.d.connect(ay0, (ay1[0], ay1[1] - 12), **opts)
        tick_parts = []
        for tx in ticks(*self.x, xstep):
            p = self.px(tx, zy)
            tick_parts.append(f"M {p[0]:.2f} {p[1] - 3:.2f} v 6")
            if labels and not (abs(tx) < 1e-12 and zx == 0 and zy == 0):  # shared origin label drawn once, below
                self.d.text(_fmt(tx), size=size).at(p[0], p[1] + 6, anchor="top_center")
        for ty in ticks(*self.y, ystep):
            p = self.px(zx, ty)
            tick_parts.append(f"M {p[0] - 3:.2f} {p[1]:.2f} h 6")
            if labels:
                if abs(ty) < 1e-12 and zx == 0 and zy == 0:
                    continue
                self.d.text(_fmt(ty), size=size).at(p[0] - 7, p[1], anchor="right_center")
        if labels and zx == 0 and zy == 0 and self.xscale == "linear" and self.yscale == "linear":
            o = self.px(0, 0)
            self.d.text("0", size=size).at(o[0] - 6, o[1] + 4, anchor="top_right")
        if tick_parts:
            self.d.path(" ".join(tick_parts), style=Style(fill="none", stroke=INK, stroke_width=0.9))
        if xlabel:
            self.d.text(xlabel, size=size + 3).at(ax1[0] + 18, ax1[1], anchor="left_center")
        if ylabel:
            self.d.text(ylabel, size=size + 3).at(ay1[0], ay1[1] - 18, anchor="bottom_center")

    # ------------------------------------------------------------------ curves
    def _draw_runs(self, runs: list[list[Pt]], style: Style, z: int = 0) -> None:
        if not runs:
            return
        parts = []
        for run in runs:
            pts = [self.px(*p) for p in run]
            parts.append("M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts))
        self.d.path(" ".join(parts), style=style, z=z)

    def sample(self, f: Callable[[float], float], lo: Optional[float] = None, hi: Optional[float] = None,
               n: int = 400) -> list[Optional[Pt]]:
        """Evaluate ``f`` at ``n`` points; failures and non-finite values become breaks."""
        lo = self.x[0] if lo is None else lo
        hi = self.x[1] if hi is None else hi
        out: list[Optional[Pt]] = []
        for i in range(n + 1):
            t = i / n
            x = lo * (hi / lo) ** t if self.xscale == "log" else lo + (hi - lo) * t
            try:
                y = float(f(x))
            except (ZeroDivisionError, ValueError, OverflowError):
                out.append(None)
                continue
            out.append((x, y) if math.isfinite(y) else None)
        return out

    def function(
        self, f: Callable[[float], float], lo: Optional[float] = None, hi: Optional[float] = None,
        stroke: str = INK, width: float = 1.8, dash: str = "", n: int = 400,
        jump: Optional[float] = None,
    ) -> None:
        """Plot y = f(x), clipped to the window.

        Where consecutive samples differ by more than ``jump`` (data units of y)
        the curve is broken, so a tangent's asymptote is not joined across.
        """
        pts = self.sample(f, lo, hi, n)
        if jump is not None:
            broken: list[Optional[Pt]] = []
            prev: Optional[Pt] = None
            for p in pts:
                if p is not None and prev is not None and abs(p[1] - prev[1]) > jump:
                    broken.append(None)
                broken.append(p)
                prev = p
            pts = broken
        self._draw_runs(self._runs(pts), Style(fill="none", stroke=stroke, stroke_width=width, dash=dash), z=1)

    def parametric(
        self, fx: Callable[[float], float], fy: Callable[[float], float], t0: float, t1: float,
        stroke: str = INK, width: float = 1.8, dash: str = "", n: int = 400,
    ) -> list[Pt]:
        """Plot (fx(t), fy(t)) for t in [t0, t1]; returns the sampled points."""
        pts: list[Optional[Pt]] = []
        for i in range(n + 1):
            t = t0 + (t1 - t0) * i / n
            try:
                pts.append((float(fx(t)), float(fy(t))))
            except (ZeroDivisionError, ValueError, OverflowError):
                pts.append(None)
        self._draw_runs(self._runs(pts), Style(fill="none", stroke=stroke, stroke_width=width, dash=dash), z=1)
        return [p for p in pts if p is not None]

    def polyline(self, pts: Iterable[Pt], stroke: str = INK, width: float = 1.8, dash: str = "") -> None:
        """A line through data points, clipped to the window."""
        self._draw_runs(self._runs(list(pts)), Style(fill="none", stroke=stroke, stroke_width=width, dash=dash), z=1)

    def line(self, a: Pt, b: Pt, stroke: str = INK, width: float = 1.2, dash: str = "") -> None:
        self.polyline([a, b], stroke, width, dash)

    def hline(self, y: float, stroke: str = "#8A5A00", dash: str = "5,4", width: float = 1.0) -> None:
        self.line((self.x[0], y), (self.x[1], y), stroke, width, dash)

    def vline(self, x: float, stroke: str = "#8A5A00", dash: str = "5,4", width: float = 1.0) -> None:
        self.line((x, self.y[0]), (x, self.y[1]), stroke, width, dash)

    def tangent(self, f: Callable[[float], float], x0: float, half: float = 1.0, h: float = 1e-5, **kw) -> float:
        """Draw the tangent to f at x0 over x0 +- half; returns its slope."""
        slope = (f(x0 + h) - f(x0 - h)) / (2 * h)
        y0 = f(x0)
        kw.setdefault("stroke", "#8A5A00")
        kw.setdefault("width", 1.3)
        self.line((x0 - half, y0 - slope * half), (x0 + half, y0 + slope * half), **kw)
        return slope

    # ------------------------------------------------------------------ regions
    def area(
        self, f: Callable[[float], float], a: float, b: float,
        g: Optional[Callable[[float], float]] = None, fill: str = "#DCE6F2",
        opacity: float = 0.9, n: int = 200,
    ) -> None:
        """Shade between f and g (default the x-axis) from a to b, clipped to the window."""
        def clamp(v: float) -> float:
            return min(max(v, self.y[0]), self.y[1])

        xs = [a + (b - a) * i / n for i in range(n + 1)]
        top = [self.px(x, clamp(f(x))) for x in xs]
        base = [self.px(x, clamp(g(x) if g else 0.0)) for x in reversed(xs)]
        self.d.polygon(top + base, style=Style(fill=fill, stroke="none", opacity=opacity), z=-2)

    def bars(
        self, x0: float, x1: float, f: Callable[[float], float], n: int, rule: str = "left",
        fill: str = "#DCE6F2", stroke: str = INK, width: float = 0.9,
    ) -> float:
        """Riemann rectangles of f over [x0, x1]; ``rule`` is left, right, mid, lower or upper.

        Returns the sum of the rectangle areas.
        """
        dx = (x1 - x0) / n
        total = 0.0
        for i in range(n):
            lo, hi = x0 + i * dx, x0 + (i + 1) * dx
            if rule == "left":
                v = f(lo)
            elif rule == "right":
                v = f(hi)
            elif rule == "mid":
                v = f((lo + hi) / 2)
            else:
                samples = [f(lo + dx * k / 8) for k in range(9)]
                v = min(samples) if rule == "lower" else max(samples)
            total += v * dx
            pts = [self.px(lo, 0), self.px(lo, v), self.px(hi, v), self.px(hi, 0)]
            self.d.polygon(pts, style=Style(fill=fill, stroke=stroke, stroke_width=width), z=-1)
        return total

    def band(self, lo: Callable[[float], float], hi: Callable[[float], float], a: Optional[float] = None,
             b: Optional[float] = None, fill: str = "#E8E1F3", n: int = 200) -> None:
        """A shaded band between two curves, e.g. a confidence interval."""
        a = self.x[0] if a is None else a
        b = self.x[1] if b is None else b
        self.area(hi, a, b, g=lo, fill=fill, n=n)

    # ------------------------------------------------------------------ fields
    def slope_field(
        self, f: Callable[[float, float], float], nx: int = 14, ny: int = 10,
        length: float = 18.0, stroke: str = "#7C8AA8", width: float = 1.0,
    ) -> None:
        """Short line segments of slope f(x, y) on an nx by ny grid (a direction field)."""
        parts = []
        for i in range(nx):
            for j in range(ny):
                x = self.x[0] + (self.x[1] - self.x[0]) * (i + 0.5) / nx
                y = self.y[0] + (self.y[1] - self.y[0]) * (j + 0.5) / ny
                try:
                    m = float(f(x, y))
                except (ZeroDivisionError, ValueError, OverflowError):
                    continue
                if not math.isfinite(m):
                    continue
                # Slope is in data units; convert to the pixel direction.
                sx = self.w / (self.x[1] - self.x[0])
                sy = self.h / (self.y[1] - self.y[0])
                vx, vy = 1.0 * sx, m * sy
                norm = math.hypot(vx, vy)
                ux, uy = vx / norm * length / 2, vy / norm * length / 2
                cx, cy = self.px(x, y)
                parts.append(f"M {cx - ux:.2f} {cy + uy:.2f} L {cx + ux:.2f} {cy - uy:.2f}")
        if parts:
            self.d.path(" ".join(parts), style=Style(fill="none", stroke=stroke, stroke_width=width), z=-1)

    def vector_field(
        self, f: Callable[[float, float], Pt], nx: int = 12, ny: int = 9, length: float = 20.0,
        stroke: str = "#7C8AA8", width: float = 1.0, head: float = 4.0,
    ) -> None:
        """Arrows of direction f(x, y) on a grid; all have the same pixel length."""
        parts = []
        for i in range(nx):
            for j in range(ny):
                x = self.x[0] + (self.x[1] - self.x[0]) * (i + 0.5) / nx
                y = self.y[0] + (self.y[1] - self.y[0]) * (j + 0.5) / ny
                try:
                    u, v = f(x, y)
                except (ZeroDivisionError, ValueError, OverflowError):
                    continue
                n = math.hypot(u, v)
                if not math.isfinite(n) or n < 1e-12:
                    continue
                ux, uy = u / n, -v / n  # y grows downward on the canvas
                cx, cy = self.px(x, y)
                tx, ty = cx - ux * length / 2, cy - uy * length / 2
                hx, hy = cx + ux * length / 2, cy + uy * length / 2
                parts.append(f"M {tx:.2f} {ty:.2f} L {hx:.2f} {hy:.2f}")
                px_, py_ = -uy, ux
                parts.append(
                    f"M {hx - ux * head + px_ * head * 0.6:.2f} {hy - uy * head + py_ * head * 0.6:.2f} "
                    f"L {hx:.2f} {hy:.2f} "
                    f"L {hx - ux * head - px_ * head * 0.6:.2f} {hy - uy * head - py_ * head * 0.6:.2f}"
                )
        if parts:
            self.d.path(" ".join(parts), style=Style(fill="none", stroke=stroke, stroke_width=width), z=-1)

    def trajectory(
        self, f: Callable[[float, float], Pt], start: Pt, t_end: float = 10.0, steps: int = 600,
        stroke: str = INK, width: float = 1.6,
    ) -> list[Pt]:
        """Integrate x' = f(x, y) from ``start`` with fourth-order Runge-Kutta and draw it."""
        h = t_end / steps
        x, y = start
        pts: list[Pt] = [(x, y)]
        for _ in range(steps):
            k1 = f(x, y)
            k2 = f(x + h / 2 * k1[0], y + h / 2 * k1[1])
            k3 = f(x + h / 2 * k2[0], y + h / 2 * k2[1])
            k4 = f(x + h * k3[0], y + h * k3[1])
            x += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            y += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            if not (math.isfinite(x) and math.isfinite(y)):
                break
            pts.append((x, y))
        self.polyline(pts, stroke=stroke, width=width)
        return pts

    def solve_ode(
        self, f: Callable[[float, float], float], x0: float, y0: float, x1: Optional[float] = None,
        steps: int = 400, stroke: str = INK, width: float = 1.8, dash: str = "",
    ) -> list[Pt]:
        """Integrate y' = f(x, y) from (x0, y0) to x1 (RK4) and draw the solution curve."""
        x1 = self.x[1] if x1 is None else x1
        h = (x1 - x0) / steps
        x, y = x0, y0
        pts: list[Pt] = [(x, y)]
        for _ in range(steps):
            k1 = f(x, y)
            k2 = f(x + h / 2, y + h / 2 * k1)
            k3 = f(x + h / 2, y + h / 2 * k2)
            k4 = f(x + h, y + h * k3)
            y += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            x += h
            if not math.isfinite(y):
                break
            pts.append((x, y))
        self.polyline(pts, stroke=stroke, width=width, dash=dash)
        return pts

    # ------------------------------------------------------------------ marks
    def dot(self, x: float, y: float, radius: float = 3.5, label: str = "", size: float = 12,
            dx: float = 8, dy: float = -8, anchor: str = "bottom_left"):
        """A marked data point with an optional label."""
        p = self.px(x, y)
        mark = self.d.point(*p, dot=True, radius=radius)
        if label:
            self.d.text(label, size=size).at(p[0] + dx, p[1] + dy, anchor=anchor)
        return mark

    def label(self, x: float, y: float, text: str, size: float = 12, anchor: str = "left_center",
              dx: float = 0, dy: float = 0, color: Optional[str] = None) -> None:
        """Text at data position (x, y), nudged by (dx, dy) pixels."""
        p = self.px(x, y)
        kw = {"size": size}
        if color:
            kw["color"] = color
        self.d.text(text, **kw).at(p[0] + dx, p[1] + dy, anchor=anchor)

    def frame(self, stroke: str = INK, width: float = 1.0) -> None:
        """A rectangle around the data window."""
        pts = [self.px(self.x[0], self.y[0]), self.px(self.x[1], self.y[0]),
               self.px(self.x[1], self.y[1]), self.px(self.x[0], self.y[1])]
        self.d.polygon(pts, style=Style(fill="none", stroke=stroke, stroke_width=width), z=-1)

    def candles(
        self, data: Sequence[tuple[float, float, float, float, float]], width: float = 0.6,
        up: str = "#2E8B57", down: str = "#C0392B",
    ) -> None:
        """Candlesticks from (x, open, high, low, close); rising candles are filled ``up``."""
        for x, o, h, lo, c in data:
            colour = up if c >= o else down
            self.polyline([(x, lo), (x, h)], stroke=colour, width=1.2)
            half = width / 2
            pts = [self.px(x - half, o), self.px(x + half, o), self.px(x + half, c), self.px(x - half, c)]
            self.d.polygon(pts, style=Style(fill=colour, stroke=colour, stroke_width=1.0), z=1)

    def bar_chart(
        self, data: Sequence[tuple[float, float]], width: float = 0.7, fill: str = "#8FB3DE",
        stroke: str = INK,
    ) -> None:
        """Vertical bars from (x, value) pairs, rising from the x-axis."""
        base = max(self.y[0], 0.0)
        for x, v in data:
            pts = [self.px(x - width / 2, base), self.px(x - width / 2, v),
                   self.px(x + width / 2, v), self.px(x + width / 2, base)]
            self.d.polygon(pts, style=Style(fill=fill, stroke=stroke, stroke_width=0.9), z=0)
