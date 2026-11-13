"""Backend-neutral drawing items.

A primitive describes itself as a list of ``PathItem`` and ``TextItem``; a
renderer turns those into its own format. Paths are absolute ``M``/``L``/``C``/``Z``
commands only, so every backend needs just lines and cubic curves.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Optional, Sequence, Union

from diagrams_as_code.geometry import CubicBezier, Point, Rect
from diagrams_as_code.text import SANS_STACK, TextBlock

Command = tuple  # ("M", x, y) | ("L", x, y) | ("C", x1, y1, x2, y2, x, y) | ("Z",)
#: Control-point distance that makes a cubic follow a quarter circle.
KAPPA = 0.5522847498


@dataclass(frozen=True)
class PathItem:
    """A filled and/or stroked path."""

    commands: tuple[Command, ...]
    fill: Optional[str] = None
    stroke: Optional[str] = None
    stroke_width: float = 1.0
    dash: str = ""
    opacity: Optional[float] = None
    fill_opacity: Optional[float] = None
    linejoin: str = ""
    linecap: str = ""

    def bbox(self) -> Rect:
        return commands_bbox(self.commands)

    def to_svg(self, indent: str = "") -> str:
        attrs = [f'd="{svg_d(self.commands)}"', f'fill="{self.fill or "none"}"']
        if self.fill and self.fill_opacity is not None and self.fill_opacity < 1.0:
            attrs.append(f'fill-opacity="{self.fill_opacity}"')
        if self.stroke and self.stroke_width > 0.0:
            attrs.append(f'stroke="{self.stroke}" stroke-width="{self.stroke_width}"')
            if self.dash:
                attrs.append(f'stroke-dasharray="{self.dash}"')
            if self.linejoin:
                attrs.append(f'stroke-linejoin="{self.linejoin}"')
            if self.linecap:
                attrs.append(f'stroke-linecap="{self.linecap}"')
        if self.opacity is not None and self.opacity < 1.0:
            attrs.append(f'opacity="{self.opacity}"')
        return f'{indent}<path {" ".join(attrs)} />'


@dataclass(frozen=True)
class TextItem:
    """A laid-out block of text at a position."""

    block: TextBlock
    x: float
    y: float
    anchor: str = "middle"  # start | middle | end
    valign: str = "middle"  # top | middle | bottom
    fill: str = "#000000"
    font_family: str = SANS_STACK
    #: Pin every run's width to the layout, for fonts the metrics do not describe.
    precise: bool = False

    def bbox(self) -> Rect:
        left = self.x - {"start": 0.0, "middle": 0.5, "end": 1.0}[self.anchor] * self.block.width
        top = self.y - {"top": 0.0, "middle": 0.5, "bottom": 1.0}[self.valign] * self.block.height
        return Rect(left, top, self.block.width, self.block.height)

    def to_svg(self, indent: str = "") -> str:
        return self.block.to_svg(
            self.x, self.y, anchor=self.anchor, valign=self.valign, fill=self.fill,
            font_family=self.font_family, precise=self.precise, indent=indent,
        )


DrawItem = Union[PathItem, TextItem]


def items_svg(items: Sequence[DrawItem], indent: str = "") -> list[str]:
    return [item.to_svg(indent) for item in items]


def items_bbox(items: Sequence[DrawItem]) -> Optional[Rect]:
    boxes = [item.bbox() for item in items]
    if not boxes:
        return None
    out = boxes[0]
    for b in boxes[1:]:
        out = out.union(b)
    return out


# --------------------------------------------------------------------------- paths


def svg_d(commands: Sequence[Command]) -> str:
    return " ".join(
        c[0] if len(c) == 1 else f"{c[0]} " + " ".join(repr(float(v)) for v in c[1:]) for c in commands
    )


def polyline(points: Sequence[Union[Point, tuple[float, float]]], closed: bool = False) -> tuple[Command, ...]:
    pts = [_xy(p) for p in points]
    if not pts:
        return ()
    out: list[Command] = [("M", *pts[0])]
    out += [("L", *p) for p in pts[1:]]
    if closed:
        out.append(("Z",))
    return tuple(out)


def rect(x: float, y: float, w: float, h: float) -> tuple[Command, ...]:
    return polyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], closed=True)


def ellipse(cx: float, cy: float, rx: float, ry: Optional[float] = None) -> tuple[Command, ...]:
    ry = rx if ry is None else ry
    kx, ky = rx * KAPPA, ry * KAPPA
    return (
        ("M", cx + rx, cy),
        ("C", cx + rx, cy + ky, cx + kx, cy + ry, cx, cy + ry),
        ("C", cx - kx, cy + ry, cx - rx, cy + ky, cx - rx, cy),
        ("C", cx - rx, cy - ky, cx - kx, cy - ry, cx, cy - ry),
        ("C", cx + kx, cy - ry, cx + rx, cy - ky, cx + rx, cy),
        ("Z",),
    )


def translate(commands: Sequence[Command], dx: float, dy: float) -> tuple[Command, ...]:
    return transform(commands, 1.0, 1.0, dx, dy)


def transform(commands: Sequence[Command], sx: float, sy: float, dx: float, dy: float) -> tuple[Command, ...]:
    """Scale then translate every coordinate."""
    out: list[Command] = []
    for c in commands:
        vals = c[1:]
        out.append((c[0], *[v * (sx if i % 2 == 0 else sy) + (dx if i % 2 == 0 else dy) for i, v in enumerate(vals)]))
    return tuple(out)


def commands_bbox(commands: Sequence[Command]) -> Rect:
    xs: list[float] = []
    ys: list[float] = []
    cur = start = (0.0, 0.0)
    for c in commands:
        if c[0] == "M":
            cur = start = (c[1], c[2])
        elif c[0] == "L":
            cur = (c[1], c[2])
        elif c[0] == "C":
            b = CubicBezier(Point(*cur), Point(c[1], c[2]), Point(c[3], c[4]), Point(c[5], c[6])).bbox()
            xs += [b.left, b.right]
            ys += [b.top, b.bottom]
            cur = (c[5], c[6])
        elif c[0] == "Z":
            cur = start
        xs.append(cur[0])
        ys.append(cur[1])
    if not xs:
        return Rect(0.0, 0.0, 0.0, 0.0)
    return Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def _xy(p: Union[Point, Sequence[float]]) -> tuple[float, float]:
    if isinstance(p, Point):
        return (float(p.x), float(p.y))
    x, y = p
    return (float(x), float(y))


_TOKEN_RE = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}


def parse_path(d: str) -> tuple[Command, ...]:
    """SVG path data as absolute ``M``/``L``/``C``/``Z`` commands.

    Every SVG path command is accepted. Relative forms are made absolute;
    ``H``/``V`` become lines; quadratic curves and elliptical arcs become cubics.
    """
    tokens = _TOKEN_RE.findall(d)
    leftover = _TOKEN_RE.sub("", d).replace(",", "").strip()
    if leftover:
        raise ValueError(f"unexpected text in path data: {leftover[:20]!r}")
    out: list[Command] = []
    cur = start = (0.0, 0.0)
    last_ctrl: Optional[tuple[float, float]] = None
    last_cmd = ""
    i = 0
    cmd = ""
    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i]
            i += 1
        elif not cmd:
            raise ValueError("path data must start with a command")
        elif cmd in "Mm":
            # Coordinates after the first pair of a moveto are linetos.
            cmd = "L" if cmd == "M" else "l"
        upper = cmd.upper()
        n = _ARGS[upper]
        if i + n > len(tokens) or any(t.isalpha() for t in tokens[i : i + n]):
            raise ValueError(f"path command {cmd!r} needs {n} numbers")
        a = [float(t) for t in tokens[i : i + n]]
        i += n
        rel = cmd.islower()
        ox, oy = cur if rel else (0.0, 0.0)
        ctrl: Optional[tuple[float, float]] = None
        if upper == "M":
            cur = start = (a[0] + ox, a[1] + oy)
            out.append(("M", *cur))
        elif upper == "L":
            cur = (a[0] + ox, a[1] + oy)
            out.append(("L", *cur))
        elif upper == "H":
            cur = (a[0] + ox, cur[1])
            out.append(("L", *cur))
        elif upper == "V":
            cur = (cur[0], a[0] + oy)
            out.append(("L", *cur))
        elif upper in "CS":
            if upper == "C":
                c1 = (a[0] + ox, a[1] + oy)
                a = a[2:]
            else:
                c1 = _reflect(last_ctrl, cur) if last_cmd in "CS" else cur
            c2, end = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy)
            out.append(("C", *c1, *c2, *end))
            ctrl, cur = c2, end
        elif upper in "QT":
            if upper == "Q":
                q = (a[0] + ox, a[1] + oy)
                a = a[2:]
            else:
                q = _reflect(last_ctrl, cur) if last_cmd in "QT" else cur
            end = (a[0] + ox, a[1] + oy)
            c1 = (cur[0] + 2.0 / 3.0 * (q[0] - cur[0]), cur[1] + 2.0 / 3.0 * (q[1] - cur[1]))
            c2 = (end[0] + 2.0 / 3.0 * (q[0] - end[0]), end[1] + 2.0 / 3.0 * (q[1] - end[1]))
            out.append(("C", *c1, *c2, *end))
            ctrl, cur = q, end
        elif upper == "A":
            end = (a[5] + ox, a[6] + oy)
            out += arc_to_cubics(cur, a[0], a[1], a[2], bool(a[3]), bool(a[4]), end)
            cur = end
        else:  # Z
            out.append(("Z",))
            cur = start
        last_ctrl, last_cmd = ctrl, upper
    return tuple(out)


def _reflect(ctrl: Optional[tuple[float, float]], about: tuple[float, float]) -> tuple[float, float]:
    if ctrl is None:
        return about
    return (2.0 * about[0] - ctrl[0], 2.0 * about[1] - ctrl[1])


def arc_to_cubics(
    p0: tuple[float, float], rx: float, ry: float, rotation: float, large: bool, sweep: bool,
    p1: tuple[float, float],
) -> list[Command]:
    """An SVG elliptical arc from ``p0`` to ``p1`` as cubic curves (SVG 1.1, F.6.5)."""
    rx, ry = abs(rx), abs(ry)
    if p0 == p1:
        return []
    if rx == 0.0 or ry == 0.0:
        return [("L", *p1)]
    phi = math.radians(rotation)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    dx, dy = (p0[0] - p1[0]) / 2.0, (p0[1] - p1[1]) / 2.0
    x1, y1 = cos_p * dx + sin_p * dy, -sin_p * dx + cos_p * dy
    lam = (x1 * x1) / (rx * rx) + (y1 * y1) / (ry * ry)
    if lam > 1.0:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    coef = math.sqrt(max(0.0, num / den)) * (-1.0 if large == sweep else 1.0)
    cxp, cyp = coef * rx * y1 / ry, -coef * ry * x1 / rx
    cx = cos_p * cxp - sin_p * cyp + (p0[0] + p1[0]) / 2.0
    cy = sin_p * cxp + cos_p * cyp + (p0[1] + p1[1]) / 2.0
    theta = math.atan2((y1 - cyp) / ry, (x1 - cxp) / rx)
    delta = math.atan2((-y1 - cyp) / ry, (-x1 - cxp) / rx) - theta
    if sweep and delta < 0.0:
        delta += 2.0 * math.pi
    elif not sweep and delta > 0.0:
        delta -= 2.0 * math.pi
    pieces = max(1, int(math.ceil(abs(delta) / (math.pi / 2.0) - 1e-9)))
    step = delta / pieces
    k = 4.0 / 3.0 * math.tan(step / 4.0)

    def at(angle: float) -> tuple[float, float, float, float]:
        ca, sa = math.cos(angle), math.sin(angle)
        x, y = rx * ca, ry * sa
        tx, ty = -rx * sa, ry * ca
        return (
            cos_p * x - sin_p * y + cx, sin_p * x + cos_p * y + cy,
            cos_p * tx - sin_p * ty, sin_p * tx + cos_p * ty,
        )

    out: list[Command] = []
    for n in range(pieces):
        ax, ay, atx, aty = at(theta + n * step)
        bx, by, btx, bty = at(theta + (n + 1) * step)
        end = p1 if n == pieces - 1 else (bx, by)
        out.append(("C", ax + k * atx, ay + k * aty, bx - k * btx, by - k * bty, *end))
    return out


# --------------------------------------------------------------------------- arrowheads

ARROW_STYLES = ("triangle", "stealth", "open", "diamond", "circle", "bar", "none")


def arrow_length(stroke_width: float, size: float = 1.0) -> float:
    """Length of an arrowhead on a line of ``stroke_width``."""
    return 6.0 * max(float(stroke_width), 1.5) * float(size)


def arrow_trim(style: str, length: float) -> float:
    """How far the line stops short of the tip so it does not show through the head."""
    return {"triangle": 0.8, "stealth": 0.55, "diamond": 1.0, "circle": 0.7}.get(style, 0.0) * length


def arrowhead(
    tip: Point, direction: Point, style: str, length: float, color: str, stroke_width: float
) -> list[PathItem]:
    """An arrowhead whose point is at ``tip``, pointing along ``direction``."""
    if style == "none":
        return []
    if style not in ARROW_STYLES:
        raise ValueError(f"arrowhead must be one of {ARROW_STYLES}, got {style!r}")
    norm = math.hypot(direction.x, direction.y) or 1.0
    ux, uy = direction.x / norm, direction.y / norm
    half = 0.4 * length

    def at(back: float, side: float) -> tuple[float, float]:
        return (tip.x - ux * back - uy * side, tip.y - uy * back + ux * side)

    if style == "triangle":
        return [PathItem(polyline([at(0, 0), at(length, half), at(length, -half)], True), fill=color)]
    if style == "stealth":
        pts = [at(0, 0), at(length, half), at(0.65 * length, 0), at(length, -half)]
        return [PathItem(polyline(pts, True), fill=color)]
    if style == "diamond":
        pts = [at(0, 0), at(length / 2.0, half * 0.75), at(length, 0), at(length / 2.0, -half * 0.75)]
        return [PathItem(polyline(pts, True), fill=color)]
    if style == "circle":
        r = 0.35 * length
        cx, cy = at(r, 0)
        return [PathItem(ellipse(cx, cy, r), fill=color)]
    if style == "bar":
        return [PathItem(polyline([at(0, half), at(0, -half)]), stroke=color, stroke_width=stroke_width)]
    return [  # open
        PathItem(
            polyline([at(length, half), at(0, 0), at(length, -half)]),
            stroke=color, stroke_width=stroke_width, linejoin="miter", linecap="round",
        )
    ]
