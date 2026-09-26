from __future__ import annotations
import bisect
from dataclasses import dataclass
from enum import Enum
import math
from typing import Union

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __add__(self, other: Point) -> Point:
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Point:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Point(self.x * float(scalar), self.y * float(scalar))

    def __rmul__(self, scalar: float) -> Point:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Point(self.x * float(scalar), self.y * float(scalar))

    def __truediv__(self, scalar: float) -> Point:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Point(self.x / float(scalar), self.y / float(scalar))

    def distance_to(self, other: Point) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

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

    @property
    def top_left(self) -> Point:
        return Point(self.left, self.top)

    @property
    def top_right(self) -> Point:
        return Point(self.right, self.top)

    @property
    def bottom_left(self) -> Point:
        return Point(self.left, self.bottom)

    @property
    def bottom_right(self) -> Point:
        return Point(self.right, self.bottom)

    def get_anchor(self, anchor: Anchor) -> Point:
        if anchor == Anchor.TOP_LEFT:
            return self.top_left
        elif anchor == Anchor.TOP_CENTER:
            return Point(self.x + self.width / 2.0, self.top)
        elif anchor == Anchor.TOP_RIGHT:
            return self.top_right
        elif anchor == Anchor.LEFT_CENTER:
            return Point(self.left, self.y + self.height / 2.0)
        elif anchor == Anchor.CENTER:
            return self.center
        elif anchor == Anchor.RIGHT_CENTER:
            return Point(self.right, self.y + self.height / 2.0)
        elif anchor == Anchor.BOTTOM_LEFT:
            return self.bottom_left
        elif anchor == Anchor.BOTTOM_CENTER:
            return Point(self.x + self.width / 2.0, self.bottom)
        elif anchor == Anchor.BOTTOM_RIGHT:
            return self.bottom_right
        raise ValueError(f"Unknown anchor: {anchor}")

    def union(self, other: Rect) -> Rect:
        min_x = min(self.left, other.left)
        min_y = min(self.top, other.top)
        max_x = max(self.right, other.right)
        max_y = max(self.bottom, other.bottom)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def intersects(self, other: Rect) -> bool:
        """Return True when the two rectangles' interiors overlap."""
        return (
            self.left < other.right
            and other.left < self.right
            and self.top < other.bottom
            and other.top < self.bottom
        )

    def expand(
        self,
        padding: Union[float, int, tuple[float, ...], list[float]],
    ) -> Rect:
        if isinstance(padding, (int, float)):
            top = right = bottom = left = float(padding)
        elif isinstance(padding, (tuple, list)):
            if len(padding) == 2:
                top = bottom = float(padding[0])
                left = right = float(padding[1])
            elif len(padding) == 4:
                top, right, bottom, left = (float(v) for v in padding)
            else:
                raise ValueError("Padding must be 1, 2, or 4 values.")
        else:
            raise TypeError(f"Unsupported padding type: {type(padding).__name__}")
        return Rect(
            x=self.x - left,
            y=self.y - top,
            width=self.width + left + right,
            height=self.height + top + bottom,
        )

class UnitBasis:
    def __init__(
        self,
        reference_size: Size | None = None,
        *,
        canvas_size: Size | None = None,
    ) -> None:
        size = canvas_size if canvas_size is not None else reference_size
        if size is None:
            raise ValueError("A Size reference or canvas_size must be provided.")
        self.reference_size = size

    @property
    def canvas_size(self) -> Size:
        return self.reference_size

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


@dataclass(frozen=True)
class CubicBezier:
    p0: Point
    c1: Point
    c2: Point
    p3: Point

    def point_at(self, t: float) -> Point:
        """Evaluate point on cubic Bezier curve at parameter t in [0.0, 1.0]."""
        it = 1.0 - t
        it2 = it * it
        t2 = t * t
        x = (
            it2 * it * self.p0.x
            + 3.0 * it2 * t * self.c1.x
            + 3.0 * it * t2 * self.c2.x
            + t2 * t * self.p3.x
        )
        y = (
            it2 * it * self.p0.y
            + 3.0 * it2 * t * self.c1.y
            + 3.0 * it * t2 * self.c2.y
            + t2 * t * self.p3.y
        )
        return Point(x, y)

    def tangent_at(self, t: float) -> Point:
        """Evaluate first derivative velocity vector B'(t)."""
        it = 1.0 - t
        c_p0 = 3.0 * it * it
        c_c1 = 6.0 * it * t
        c_c2 = 3.0 * t * t
        vx = (
            c_p0 * (self.c1.x - self.p0.x)
            + c_c1 * (self.c2.x - self.c1.x)
            + c_c2 * (self.p3.x - self.c2.x)
        )
        vy = (
            c_p0 * (self.c1.y - self.p0.y)
            + c_c1 * (self.c2.y - self.c1.y)
            + c_c2 * (self.p3.y - self.c2.y)
        )
        return Point(vx, vy)

    def sample(self, n: int = 16) -> list[Point]:
        """Uniform parameter sampling at t = i / (n - 1) for i in [0, n-1]."""
        if n < 2:
            return [self.p0, self.p3]
        return [self.point_at(i / (n - 1)) for i in range(n)]

    def bbox(self) -> Rect:
        """Compute exact tight axis-aligned bounding box using derivative roots."""
        def solve_quadratic(a: float, b: float, c: float) -> list[float]:
            if abs(a) < 1e-9:
                if abs(b) < 1e-9:
                    return []
                return [-c / b]
            disc = b * b - 4.0 * a * c
            if disc < 0.0:
                return []
            if abs(disc) < 1e-9:
                return [-b / (2.0 * a)]
            s = math.sqrt(disc)
            return [(-b - s) / (2.0 * a), (-b + s) / (2.0 * a)]

        ax = 3.0 * (-self.p0.x + 3.0 * self.c1.x - 3.0 * self.c2.x + self.p3.x)
        bx = 6.0 * (self.p0.x - 2.0 * self.c1.x + self.c2.x)
        cx = 3.0 * (self.c1.x - self.p0.x)

        ay = 3.0 * (-self.p0.y + 3.0 * self.c1.y - 3.0 * self.c2.y + self.p3.y)
        by = 6.0 * (self.p0.y - 2.0 * self.c1.y + self.c2.y)
        cy = 3.0 * (self.c1.y - self.p0.y)

        candidates = [0.0, 1.0]
        for t in solve_quadratic(ax, bx, cx):
            if 0.0 < t < 1.0:
                candidates.append(t)
        for t in solve_quadratic(ay, by, cy):
            if 0.0 < t < 1.0:
                candidates.append(t)

        pts = [self.point_at(t) for t in candidates]
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def arc_length(self, num_samples: int = 32) -> float:
        """Compute approximate curve arc length via piecewise chord lengths."""
        num_samples = max(1, num_samples)
        pts = self.sample(num_samples + 1)
        return sum(pts[i].distance_to(pts[i + 1]) for i in range(len(pts) - 1))

    def arc_length_midpoint(self, num_samples: int = 32) -> Point:
        """Find the physical midpoint s = L / 2 using chord parameterization."""
        num_samples = max(1, num_samples)
        pts = self.sample(num_samples + 1)
        dists = [0.0]
        for i in range(len(pts) - 1):
            dists.append(dists[-1] + pts[i].distance_to(pts[i + 1]))

        total_len = dists[-1]
        if total_len < 1e-6:
            return self.p0

        half_len = total_len / 2.0
        idx = bisect.bisect_right(dists, half_len) - 1
        idx = max(0, min(idx, num_samples - 1))

        segment_len = dists[idx + 1] - dists[idx]
        alpha = (half_len - dists[idx]) / segment_len if segment_len > 1e-9 else 0.0
        t_mid = (idx + alpha) / num_samples
        return self.point_at(t_mid)


@dataclass(frozen=True)
class QuadraticBezier:
    p0: Point
    p1: Point
    p2: Point

    def point_at(self, t: float) -> Point:
        """Evaluate point on quadratic Bezier curve at parameter t in [0.0, 1.0]."""
        it = 1.0 - t
        it2 = it * it
        t2 = t * t
        two_it_t = 2.0 * it * t
        x = it2 * self.p0.x + two_it_t * self.p1.x + t2 * self.p2.x
        y = it2 * self.p0.y + two_it_t * self.p1.y + t2 * self.p2.y
        return Point(x, y)

    def tangent_at(self, t: float) -> Point:
        """Evaluate first derivative velocity vector B'(t)."""
        it = 1.0 - t
        vx = 2.0 * it * (self.p1.x - self.p0.x) + 2.0 * t * (self.p2.x - self.p1.x)
        vy = 2.0 * it * (self.p1.y - self.p0.y) + 2.0 * t * (self.p2.y - self.p1.y)
        return Point(vx, vy)

    def sample(self, n: int = 16) -> list[Point]:
        """Uniform parameter sampling at t = i / (n - 1) for i in [0, n - 1]."""
        if n < 2:
            return [self.p0, self.p2]
        return [self.point_at(i / (n - 1)) for i in range(n)]

    def bbox(self) -> Rect:
        """Compute exact tight axis-aligned bounding box from analytical linear roots of first derivative."""
        candidates = [0.0, 1.0]

        denom_x = self.p0.x - 2.0 * self.p1.x + self.p2.x
        if abs(denom_x) > 1e-9:
            tx = (self.p0.x - self.p1.x) / denom_x
            if 0.0 < tx < 1.0:
                candidates.append(tx)

        denom_y = self.p0.y - 2.0 * self.p1.y + self.p2.y
        if abs(denom_y) > 1e-9:
            ty = (self.p0.y - self.p1.y) / denom_y
            if 0.0 < ty < 1.0:
                candidates.append(ty)

        pts = [self.point_at(t) for t in candidates]
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def arc_length(self, num_samples: int = 16) -> float:
        """Compute approximate curve arc length via piecewise chord lengths."""
        num_samples = max(1, num_samples)
        pts = self.sample(num_samples + 1)
        return sum(pts[i].distance_to(pts[i + 1]) for i in range(len(pts) - 1))

