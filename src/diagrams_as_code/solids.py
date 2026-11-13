"""Convex solids drawn in parallel projection.

A ``Solid`` is a set of 3D vertices and the faces that join them. A
``Projection`` flattens it; ``project()`` returns the faces back to front and
every edge marked visible or hidden, so a figure can dash the hidden ones.

Model axes: x to the right, y up, z away from the viewer.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

from diagrams_as_code.geometry import Point

Vec3 = tuple[float, float, float]
EPS = 1e-7


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _unit(a: Vec3) -> Vec3:
    n = math.sqrt(_dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n) if n > EPS else (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class Projection:
    """A parallel projection: screen x and y as linear functions of model x, y, z.

    ``view`` points from the solid towards the viewer; a face is seen when its
    outward normal has a positive component along it.
    """

    name: str
    x_axis: Vec3  # screen x = x_axis . p
    y_axis: Vec3  # screen y = y_axis . p   (screen y grows downwards)
    view: Vec3

    def point(self, p: Vec3) -> Point:
        return Point(_dot(self.x_axis, p), _dot(self.y_axis, p))

    def depth(self, p: Vec3) -> float:
        """Larger is nearer the viewer."""
        return _dot(self.view, p)


def oblique(angle: float = 45.0, depth_scale: float = 0.5) -> Projection:
    """Front face drawn true; depth recedes up and to the right at ``angle`` degrees.

    ``depth_scale`` 0.5 is a cabinet projection, 1.0 a cavalier one.
    """
    a = math.radians(angle)
    kx, ky = depth_scale * math.cos(a), depth_scale * math.sin(a)
    return Projection("oblique", (1.0, 0.0, kx), (0.0, -1.0, -ky), (kx, ky, -1.0))


def isometric() -> Projection:
    """The three axes drawn 120 degrees apart, equally foreshortened; the top is seen.

    Here z comes towards the viewer's left and x towards the right.
    """
    c, s = math.cos(math.radians(30.0)), math.sin(math.radians(30.0))
    return Projection("isometric", (c, 0.0, -c), (s, -1.0, s), (1.0, 1.0, 1.0))


@dataclass(frozen=True)
class ProjectedFace:
    points: tuple[Point, ...]
    front: bool  # faces the viewer
    depth: float
    index: int  # position in ``Solid.faces``


@dataclass(frozen=True)
class ProjectedEdge:
    a: Point
    b: Point
    visible: bool


@dataclass(frozen=True)
class Solid:
    """A convex polyhedron: vertices, and faces as loops of vertex indices."""

    vertices: tuple[Vec3, ...]
    faces: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "vertices", tuple(tuple(float(c) for c in v) for v in self.vertices))
        object.__setattr__(self, "faces", tuple(tuple(int(i) for i in f) for f in self.faces))
        for face in self.faces:
            if len(face) < 3 or any(not 0 <= i < len(self.vertices) for i in face):
                raise ValueError(f"face {face!r} needs at least three valid vertex indices")

    # ---------------------------------------------------------------- constructors

    @classmethod
    def box(cls, width: float, height: float, depth: float) -> Solid:
        """A cuboid with one corner at the origin."""
        w, h, d = float(width), float(height), float(depth)
        v = [(0, 0, 0), (w, 0, 0), (w, h, 0), (0, h, 0), (0, 0, d), (w, 0, d), (w, h, d), (0, h, d)]
        f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (3, 2, 6, 7), (0, 3, 7, 4), (1, 2, 6, 5)]
        return cls(tuple(v), tuple(f))

    @classmethod
    def prism(cls, base: Sequence[tuple[float, float]], depth: float) -> Solid:
        """A convex polygon in the x-y plane, extruded ``depth`` along z."""
        n = len(base)
        if n < 3:
            raise ValueError("a prism needs a base of at least three points")
        v = [(x, y, 0.0) for x, y in base] + [(x, y, float(depth)) for x, y in base]
        f = [tuple(range(n)), tuple(range(n, 2 * n))]
        f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        return cls(tuple(v), tuple(f))

    @classmethod
    def pyramid(cls, base: Sequence[tuple[float, float]], apex: Vec3) -> Solid:
        """A convex polygon in the x-z plane (the floor) joined to ``apex``."""
        n = len(base)
        if n < 3:
            raise ValueError("a pyramid needs a base of at least three points")
        v = [(x, 0.0, z) for x, z in base] + [tuple(apex)]
        f = [tuple(range(n))] + [(i, (i + 1) % n, n) for i in range(n)]
        return cls(tuple(v), tuple(f))

    @classmethod
    def hull(cls, points: Sequence[Vec3]) -> Solid:
        """The convex hull of ``points``. Meant for the few dozen points of a figure."""
        pts: list[Vec3] = []
        for p in points:
            q = (float(p[0]), float(p[1]), float(p[2]))
            if all(max(abs(q[i] - o[i]) for i in range(3)) > EPS for o in pts):
                pts.append(q)
        n = len(pts)
        scale = max((abs(c) for p in pts for c in p), default=1.0) or 1.0
        tol = 1e-9 * scale * scale * scale + 1e-9
        faces: dict[frozenset[int], tuple[int, ...]] = {}
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    normal = _cross(_sub(pts[j], pts[i]), _sub(pts[k], pts[i]))
                    if _dot(normal, normal) < tol * tol:
                        continue
                    sides = [_dot(normal, _sub(p, pts[i])) for p in pts]
                    if any(s > tol for s in sides) and any(s < -tol for s in sides):
                        continue
                    on = frozenset(m for m, s in enumerate(sides) if abs(s) <= tol)
                    if on not in faces:
                        faces[on] = _ordered(pts, sorted(on), _unit(normal))
        if len(faces) < 4:
            raise ValueError("points do not span a solid (need four that are not coplanar)")
        used = sorted({i for f in faces.values() for i in f})
        remap = {old: new for new, old in enumerate(used)}
        return cls(
            tuple(pts[i] for i in used),
            tuple(tuple(remap[i] for i in f) for f in sorted(faces.values())),
        )

    # ------------------------------------------------------------------- geometry

    @property
    def centroid(self) -> Vec3:
        n = float(len(self.vertices))
        return (
            sum(v[0] for v in self.vertices) / n,
            sum(v[1] for v in self.vertices) / n,
            sum(v[2] for v in self.vertices) / n,
        )

    def normal(self, face_index: int) -> Vec3:
        """Outward unit normal of a face, whichever way its loop is wound."""
        face = self.faces[face_index]
        a = self.vertices[face[0]]
        normal = (0.0, 0.0, 0.0)
        for i in range(1, len(face) - 1):
            part = _cross(_sub(self.vertices[face[i]], a), _sub(self.vertices[face[i + 1]], a))
            normal = (normal[0] + part[0], normal[1] + part[1], normal[2] + part[2])
        normal = _unit(normal)
        if _dot(normal, _sub(a, self.centroid)) < 0.0:
            normal = (-normal[0], -normal[1], -normal[2])
        return normal

    def edges(self) -> dict[tuple[int, int], list[int]]:
        """Each edge as a sorted vertex pair, with the faces that meet along it."""
        out: dict[tuple[int, int], list[int]] = {}
        for fi, face in enumerate(self.faces):
            for a, b in zip(face, face[1:] + face[:1]):
                out.setdefault((min(a, b), max(a, b)), []).append(fi)
        return out

    def translated(self, dx: float, dy: float, dz: float) -> Solid:
        return Solid(tuple((x + dx, y + dy, z + dz) for x, y, z in self.vertices), self.faces)

    def section(self, point: Vec3, normal: Vec3) -> list[Vec3]:
        """The polygon where the plane through ``point`` with ``normal`` cuts the solid."""
        n = _unit(normal)
        hits: list[Vec3] = []
        for a, b in self.edges():
            pa, pb = self.vertices[a], self.vertices[b]
            da, db = _dot(n, _sub(pa, point)), _dot(n, _sub(pb, point))
            if abs(da) <= EPS:
                hits.append(pa)
            if abs(db) <= EPS:
                hits.append(pb)
            if da * db < -EPS * EPS and abs(da) > EPS and abs(db) > EPS:
                t = da / (da - db)
                hits.append((pa[0] + t * (pb[0] - pa[0]), pa[1] + t * (pb[1] - pa[1]), pa[2] + t * (pb[2] - pa[2])))
        unique: list[Vec3] = []
        for h in hits:
            if all(max(abs(h[i] - u[i]) for i in range(3)) > 1e-6 for u in unique):
                unique.append(h)
        if len(unique) < 3:
            return []
        order = _ordered(unique, list(range(len(unique))), n)
        return [unique[i] for i in order]

    def clipped(self, point: Vec3, normal: Vec3) -> Solid:
        """The part of the solid behind the plane (the side ``normal`` points away from)."""
        n = _unit(normal)
        keep = [v for v in self.vertices if _dot(n, _sub(v, point)) <= EPS]
        return Solid.hull(keep + self.section(point, normal))

    # ----------------------------------------------------------------- projection

    def project(
        self, projection: Projection, scale: float = 1.0
    ) -> tuple[list[ProjectedFace], list[ProjectedEdge]]:
        """Faces sorted back to front, and every edge marked visible or hidden."""
        pts = [projection.point(v) * scale for v in self.vertices]
        front = [_dot(self.normal(i), projection.view) > EPS for i in range(len(self.faces))]
        faces = [
            ProjectedFace(
                tuple(pts[i] for i in face),
                front[fi],
                sum(projection.depth(self.vertices[i]) for i in face) / len(face),
                fi,
            )
            for fi, face in enumerate(self.faces)
        ]
        # Back faces first, then by distance, so nearer faces are painted over farther ones.
        faces.sort(key=lambda f: (f.front, f.depth, f.index))
        edges = [
            ProjectedEdge(pts[a], pts[b], any(front[fi] for fi in meeting))
            for (a, b), meeting in sorted(self.edges().items())
        ]
        return faces, edges


def _ordered(pts: Sequence[Vec3], indices: list[int], normal: Vec3) -> tuple[int, ...]:
    """``indices`` sorted around their centroid, in the plane with ``normal``."""
    n = float(len(indices))
    c = (
        sum(pts[i][0] for i in indices) / n,
        sum(pts[i][1] for i in indices) / n,
        sum(pts[i][2] for i in indices) / n,
    )
    u = _unit(_sub(pts[indices[0]], c))
    v = _cross(normal, u)

    def angle(i: int) -> float:
        d = _sub(pts[i], c)
        return math.atan2(_dot(d, v), _dot(d, u))

    return tuple(sorted(indices, key=angle))


def section_points(
    solid: Solid, point: Vec3, normal: Vec3, projection: Projection, scale: float = 1.0
) -> list[Point]:
    """The cut polygon of ``Solid.section``, projected."""
    return [projection.point(p) * scale for p in solid.section(point, normal)]


def plane_points(
    point: Vec3, normal: Vec3, half_size: float, projection: Projection, scale: float = 1.0,
    up: Optional[Vec3] = None,
) -> list[Point]:
    """A square patch of the plane through ``point``, projected, for drawing a cutting plane."""
    n = _unit(normal)
    ref = up or ((0.0, 1.0, 0.0) if abs(n[1]) < 0.9 else (1.0, 0.0, 0.0))
    u = _unit(_cross(ref, n))
    v = _cross(n, u)
    out = []
    for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        p = tuple(point[i] + half_size * (su * u[i] + sv * v[i]) for i in range(3))
        out.append(projection.point(p) * scale)  # type: ignore[arg-type]
    return out
