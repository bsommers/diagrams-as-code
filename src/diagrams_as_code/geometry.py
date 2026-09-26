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
