"""Drafting and anatomy primitives on a Diagram, in canvas pixels.

``Draft`` draws with the diagram's own paths, polygons and text, so its output is
ordinary figure content (lint, SVG and PDF output see it). Pure standard library.

    with Diagram("Bracket", theme="paper") as d:
        k = Draft(d)
        k.outline([(100, 100), (300, 100), (300, 180), (100, 180)])
        k.hatch([(100, 100), (300, 100), (300, 180), (100, 180)], angle=45, gap=7)
        k.dimension((100, 190), (300, 190), "$200$", offset=24)
        k.centerline((200, 80), (200, 200))

Engineering: ``dimension`` (extension lines, arrows, centred text; ``side`` picks
which way the offset runs), ``radius_dim`` (leader to a circle; ``diameter=True`` for a diameter),
``hatch`` (section lining clipped to any polygon, even-odd so holes work),
``centerline`` / ``hidden_line`` (chain and dashed linework), ``section_arrows``
(cutting-plane line with lettered arrows) and ``gdt_frame`` (feature-control frame).

Anatomy: ``smooth_closed`` / ``smooth_open`` (organic outlines through points,
Catmull-Rom), ``leader`` (label with a pointer line) and ``wave`` (a periodic
trace such as an ECG built from Gaussian beats).
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Sequence

from diagrams_as_code.diagram import Diagram
from diagrams_as_code.style import Style

Pt = tuple[float, float]

INK = "#1F2F57"
THIN = 0.9
THICK = 2.0


def _fmt(p: Pt) -> str:
    return f"{p[0]:.2f} {p[1]:.2f}"


def _unit(a: Pt, b: Pt) -> tuple[float, float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n, n


def catmull_rom(points: Sequence[Pt], closed: bool = False, tension: float = 1.0) -> str:
    """SVG path data of a cubic chain passing smoothly through ``points``."""
    pts = [(float(x), float(y)) for x, y in points]
    n = len(pts)
    if n < 2:
        return ""
    parts = [f"M {_fmt(pts[0])}"]
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 6.0, p1[1] + (p2[1] - p0[1]) * tension / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 6.0, p2[1] - (p3[1] - p1[1]) * tension / 6.0)
        parts.append(f"C {_fmt(c1)} {_fmt(c2)} {_fmt(p2)}")
    if closed:
        parts.append("Z")
    return " ".join(parts)


def hatch_segments(polygon: Sequence[Pt], angle: float = 45.0, gap: float = 6.0) -> list[tuple[Pt, Pt]]:
    """Parallel chords of ``polygon`` at ``angle`` degrees, ``gap`` pixels apart (even-odd)."""
    pts = [(float(x), float(y)) for x, y in polygon]
    if len(pts) < 3 or gap <= 0:
        return []
    th = math.radians(angle)
    ux, uy = math.cos(th), -math.sin(th)  # along the lines (screen y points down)
    nx, ny = -uy, ux  # across the lines
    along = [(x * ux + y * uy, x * nx + y * ny) for x, y in pts]
    lo = min(a[1] for a in along)
    hi = max(a[1] for a in along)
    out: list[tuple[Pt, Pt]] = []
    k = math.floor(lo / gap) + 1
    while k * gap < hi:
        c = k * gap
        xs: list[float] = []
        for i in range(len(along)):
            (s0, t0), (s1, t1) = along[i], along[(i + 1) % len(along)]
            if (t0 <= c < t1) or (t1 <= c < t0):
                xs.append(s0 + (c - t0) * (s1 - s0) / (t1 - t0))
        xs.sort()
        for a, b in zip(xs[0::2], xs[1::2]):
            if b - a > 0.5:
                out.append(((a * ux + c * nx, a * uy + c * ny), (b * ux + c * nx, b * uy + c * ny)))
        k += 1
    return out


class Draft:
    """Drafting and anatomy helpers bound to a Diagram."""

    def __init__(self, diagram: Diagram, ink: str = INK, size: float = 11) -> None:
        self.d = diagram
        self.ink = ink
        self.size = size

    # ------------------------------------------------------------ plumbing
    def _line(self, d: str, width: float = THIN, dash: str = "", fill: str = "none", z: float = 0) -> None:
        self.d.path(d, style=Style(fill=fill, stroke=self.ink, stroke_width=width, dash=dash), z=z)

    def _arrow(self, tip: Pt, toward: Pt, size: float = 7.0) -> str:
        ux, uy, _ = _unit(tip, toward)
        px, py = -uy, ux
        a = (tip[0] + ux * size + px * size * 0.28, tip[1] + uy * size + py * size * 0.28)
        b = (tip[0] + ux * size - px * size * 0.28, tip[1] + uy * size - py * size * 0.28)
        return f"M {_fmt(tip)} L {_fmt(a)} L {_fmt(b)} Z"

    def _tag(self, text: str, at: Pt, anchor: str = "center", size: Optional[float] = None, z: float = 0) -> None:
        self.d.text(text, size=size or self.size, z=z).at(at[0], at[1], anchor=anchor)

    # ------------------------------------------------------------ outlines
    def outline(self, points: Sequence[Pt], fill: str = "none", width: float = THICK, dash: str = "") -> None:
        """A closed object outline (thick visible line)."""
        pts = list(points)
        d = "M " + " L ".join(_fmt(p) for p in pts) + " Z"
        self._line(d, width=width, dash=dash, fill=fill)

    def smooth_closed(self, points: Sequence[Pt], fill: str = "none", stroke: Optional[str] = None,
                      width: float = 1.6, tension: float = 1.0, z: float = 0,
                      dash: str = "", fill_opacity: Optional[float] = None) -> None:
        """A smooth closed organic outline through ``points``."""
        self.d.path(catmull_rom(points, closed=True, tension=tension), style=Style(
            fill=fill, stroke=stroke or self.ink, stroke_width=width, dash=dash, fill_opacity=fill_opacity), z=z)

    def smooth_open(self, points: Sequence[Pt], stroke: Optional[str] = None, width: float = 1.6,
                    tension: float = 1.0, dash: str = "", z: float = 0) -> None:
        """A smooth open curve through ``points``."""
        self.d.path(catmull_rom(points, closed=False, tension=tension), style=Style(
            fill="none", stroke=stroke or self.ink, stroke_width=width, dash=dash), z=z)

    # ------------------------------------------------------------ linework
    def centerline(self, a: Pt, b: Pt, overshoot: float = 0.0, long: float = 14.0,
                   short: float = 3.0, gap: float = 3.0) -> None:
        """A chain line (long dash, gap, short dash, gap) from ``a`` to ``b``."""
        ux, uy, n = _unit(a, b)
        a = (a[0] - ux * overshoot, a[1] - uy * overshoot)
        total = n + 2 * overshoot
        pos, parts, on_long = 0.0, [], True
        while pos < total:
            seg = min(long if on_long else short, total - pos)
            p, q = pos, pos + seg
            parts.append(f"M {_fmt((a[0] + ux * p, a[1] + uy * p))} L {_fmt((a[0] + ux * q, a[1] + uy * q))}")
            pos = q + gap
            on_long = not on_long
        self._line(" ".join(parts), width=0.8)

    def hidden_line(self, points: Sequence[Pt], width: float = 1.1) -> None:
        """A dashed hidden-edge line."""
        self._line("M " + " L ".join(_fmt(p) for p in points), width=width, dash="5,3")

    def hatch(self, polygon: Sequence[Pt], angle: float = 45.0, gap: float = 6.0,
              width: float = 0.7, stroke: Optional[str] = None, holes: Sequence[Sequence[Pt]] = ()) -> None:
        """Section lining clipped to ``polygon``; each polygon in ``holes`` is left empty."""
        segs = hatch_segments([*polygon], angle, gap) if not holes else self._holed(polygon, holes, angle, gap)
        if not segs:
            return
        d = " ".join(f"M {_fmt(a)} L {_fmt(b)}" for a, b in segs)
        self.d.path(d, style=Style(fill="none", stroke=stroke or self.ink, stroke_width=width), z=-1)

    @staticmethod
    def _holed(polygon: Sequence[Pt], holes: Sequence[Sequence[Pt]], angle: float, gap: float) -> list[tuple[Pt, Pt]]:
        # Even-odd over one combined set of rings: run the scan with every ring's edges.
        th = math.radians(angle)
        ux, uy = math.cos(th), -math.sin(th)
        nx, ny = -uy, ux
        rings = [[(x * ux + y * uy, x * nx + y * ny) for x, y in ring] for ring in (polygon, *holes)]
        lo = min(t for r in rings[:1] for _, t in r)
        hi = max(t for r in rings[:1] for _, t in r)
        out: list[tuple[Pt, Pt]] = []
        k = math.floor(lo / gap) + 1
        while k * gap < hi:
            c = k * gap
            xs: list[float] = []
            for ring in rings:
                for i in range(len(ring)):
                    (s0, t0), (s1, t1) = ring[i], ring[(i + 1) % len(ring)]
                    if (t0 <= c < t1) or (t1 <= c < t0):
                        xs.append(s0 + (c - t0) * (s1 - s0) / (t1 - t0))
            xs.sort()
            for a, b in zip(xs[0::2], xs[1::2]):
                if b - a > 0.5:
                    out.append(((a * ux + c * nx, a * uy + c * ny), (b * ux + c * nx, b * uy + c * ny)))
            k += 1
        return out

    # ------------------------------------------------------------ dimensions
    def dimension(self, a: Pt, b: Pt, text: str, offset: float = 22.0, side: int = 1,
                  ext_gap: float = 3.0, ext_over: float = 4.0, arrow: float = 7.0,
                  text_size: Optional[float] = None) -> None:
        """A dimension between feature points ``a`` and ``b``.

        The dimension line runs parallel to a-b at ``offset`` pixels on the ``side``
        (+1 or -1) of the left-hand normal; extension lines reach it from the features.
        """
        ux, uy, n = _unit(a, b)
        nx, ny = -uy * side, ux * side
        a2 = (a[0] + nx * offset, a[1] + ny * offset)
        b2 = (b[0] + nx * offset, b[1] + ny * offset)
        ext = []
        for p, q in ((a, a2), (b, b2)):
            s = (p[0] + nx * ext_gap, p[1] + ny * ext_gap)
            e = (q[0] + nx * ext_over, q[1] + ny * ext_over)
            ext.append(f"M {_fmt(s)} L {_fmt(e)}")
        self._line(" ".join(ext), width=0.7)
        inside = n >= 2.6 * arrow + 6 * len(text) * 0.5
        if inside:
            self._line(f"M {_fmt(a2)} L {_fmt(b2)}", width=0.9)
            self._line(self._arrow(a2, b2, arrow) + " " + self._arrow(b2, a2, arrow), width=0.9, fill=self.ink)
        else:  # arrows outside, pointing in
            ea = (a2[0] - ux * (arrow + 6), a2[1] - uy * (arrow + 6))
            eb = (b2[0] + ux * (arrow + 6), b2[1] + uy * (arrow + 6))
            self._line(f"M {_fmt(ea)} L {_fmt(eb)}", width=0.9)
            self._line(self._arrow(a2, ea, arrow) + " " + self._arrow(b2, eb, arrow), width=0.9, fill=self.ink)
        mid = ((a2[0] + b2[0]) / 2 + nx * 8, (a2[1] + b2[1]) / 2 + ny * 8)
        self._tag(text, mid, size=text_size)

    def radius_dim(self, center: Pt, radius: float, angle: float, text: str = "",
                   diameter: bool = False, overshoot: float = 26.0) -> None:
        """A leader through a circle: ``R`` from the centre, or ``diameter`` across it."""
        th = math.radians(angle)
        ux, uy = math.cos(th), -math.sin(th)
        edge = (center[0] + ux * radius, center[1] + uy * radius)
        start = (center[0] - ux * radius, center[1] - uy * radius) if diameter else center
        far = (edge[0] + ux * overshoot, edge[1] + uy * overshoot)
        self._line(f"M {_fmt(start)} L {_fmt(far)}", width=0.9)
        self._line(self._arrow(edge, far, 7), width=0.9, fill=self.ink)
        if diameter:
            self._line(self._arrow(start, edge, 7), width=0.9, fill=self.ink)
        label = text or ("$\\emptyset$" if diameter else "$R$")
        self._tag(label, (far[0] + ux * 4, far[1] + uy * 4),
                  anchor="left_center" if ux >= 0 else "right_center")

    def section_arrows(self, a: Pt, b: Pt, label: str, direction: int = 1, length: float = 22.0) -> None:
        """A cutting-plane line a-b with lettered arrows at both ends (view side by ``direction``)."""
        ux, uy, _ = _unit(a, b)
        nx, ny = -uy * direction, ux * direction
        self._line(f"M {_fmt(a)} L {_fmt(b)}", width=1.6, dash="14,3,3,3")
        for p in (a, b):
            tip = (p[0] + nx * length, p[1] + ny * length)
            self._line(f"M {_fmt(p)} L {_fmt(tip)}", width=1.6)
            self._line(self._arrow(tip, p, 9), width=1.0, fill=self.ink)
            self._tag(label, (tip[0] + nx * 10, tip[1] + ny * 10), size=self.size + 2)

    def gdt_frame(self, at: Pt, cells: Sequence[str], height: float = 22.0, cell_w: float = 34.0,
                  widths: Optional[Sequence[float]] = None) -> tuple[float, float]:
        """A feature-control frame with ``cells`` left to right; returns its right-centre point."""
        widths = list(widths) if widths else [cell_w] * len(cells)
        x = at[0]
        for text, w in zip(cells, widths):
            self.d.polygon(
                [(x, at[1]), (x + w, at[1]), (x + w, at[1] + height), (x, at[1] + height)],
                style=Style(fill="#FFFFFF", stroke=self.ink, stroke_width=1.1), z=1)
            self._tag(text, (x + w / 2, at[1] + height / 2), size=self.size, z=2)
            x += w
        return (x, at[1] + height / 2)

    # ------------------------------------------------------------ annotation
    def leader(self, tip: Pt, label_at: Pt, text: str, anchor: str = "left_center", dot: bool = True) -> None:
        """A label with a thin pointer line ending in a dot on the feature."""
        self._line(f"M {_fmt(tip)} L {_fmt(label_at)}", width=0.8)
        if dot:
            self.d.path(
                f"M {tip[0] - 2.2:.2f} {tip[1]:.2f} a 2.2 2.2 0 1 0 4.4 0 a 2.2 2.2 0 1 0 -4.4 0",
                style=Style(fill=self.ink, stroke=self.ink, stroke_width=0.5), z=2)
        gap = 5 if anchor.startswith("left") else -5 if anchor.startswith("right") else 0
        self._tag(text, (label_at[0] + gap, label_at[1]), anchor=anchor)

    def wave(self, origin: Pt, width: float, amp: float, beat: Callable[[float], float],
             beats: int = 3, samples: int = 60, stroke: Optional[str] = None, line: float = 1.5) -> list[Pt]:
        """A periodic trace: ``beat(phase)`` for phase in [0, 1) repeated ``beats`` times.

        Positive values rise above ``origin`` (the baseline). Returns the sampled pixel points.
        """
        pts: list[Pt] = []
        total = max(beats * samples, 2)
        for i in range(total + 1):
            t = i / samples
            phase = t - math.floor(t)
            x = origin[0] + width * i / total
            pts.append((x, origin[1] - amp * beat(phase)))
        d = "M " + " L ".join(_fmt(p) for p in pts)
        self.d.path(d, style=Style(fill="none", stroke=stroke or self.ink, stroke_width=line), z=0)
        return pts


def ecg_beat(phase: float) -> float:
    """One ECG cardiac cycle on [0, 1): P wave, QRS complex, T wave (unit R peak)."""

    def g(mu: float, sigma: float, a: float) -> float:
        return a * math.exp(-((phase - mu) ** 2) / (2 * sigma * sigma))

    return g(0.16, 0.025, 0.12) - g(0.285, 0.008, 0.12) + g(0.31, 0.010, 1.0) - g(0.335, 0.010, 0.22) + g(0.55, 0.045, 0.28)
