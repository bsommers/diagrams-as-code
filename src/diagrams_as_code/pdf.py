"""Vector PDF export. Pure standard library.

The PDF is written from the SVG the renderer produces, so the two cannot drift:
``svg_to_pdf`` reads that SVG and draws each element with PDF operators. Only the
SVG vocabulary the engine itself writes is understood (``ELEMENTS`` and
``ATTRIBUTES`` below); anything else raises ``PDFExportError`` instead of being
dropped, and ``tests/test_pdf.py`` checks the whole gallery against the two sets.

What is not a one-to-one translation:

* Text uses the 14 standard PDF fonts (Helvetica, Times, Courier, Symbol), which
  every viewer supplies, so nothing is embedded. Advance widths come from the
  bundled metric-compatible tables. A character outside Windows-1252 and the
  Symbol font is drawn as ``?`` and reported with a warning.
* A drop shadow (``feDropShadow``) is a Gaussian blur in SVG; here it is a stack
  of translucent outlines that follows the same falloff.

One SVG px is 0.75 pt (96 px per inch).
"""
from __future__ import annotations

import hashlib
import math
import re
import warnings
import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence

from diagrams_as_code import drawing
from diagrams_as_code.text import _serif_metrics as _serif
from diagrams_as_code.text import metrics as _metrics

PX_TO_PT = 0.75

#: SVG elements the writer draws.
ELEMENTS = frozenset({
    "svg", "defs", "marker", "filter", "feDropShadow", "g", "path", "rect", "circle",
    "ellipse", "line", "polyline", "polygon", "text", "tspan", "title", "desc",
})

#: SVG attributes the writer acts on, or knows it may ignore.
ATTRIBUTES = frozenset({
    # structure
    "id", "class", "viewBox", "width", "height", "transform", "space",
    # geometry
    "d", "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "points", "dy",
    # paint
    "fill", "stroke", "stroke-width", "stroke-dasharray", "stroke-linecap", "stroke-linejoin",
    "opacity", "fill-opacity", "stroke-opacity",
    # text
    "font-family", "font-size", "font-weight", "font-style", "text-anchor", "textLength",
    "lengthAdjust",
    # markers and filters
    "marker-start", "marker-end", "refX", "refY", "markerWidth", "markerHeight", "orient",
    "filter", "dx", "stdDeviation", "flood-color", "flood-opacity",
})

_INHERITED = (
    "fill", "stroke", "stroke-width", "stroke-dasharray", "stroke-linecap", "stroke-linejoin",
    "fill-opacity", "stroke-opacity", "font-family", "font-size", "font-weight", "font-style",
    "text-anchor",
)
_DEFAULTS = {
    "fill": "#000000", "stroke": "none", "stroke-width": "1", "stroke-dasharray": "none",
    "stroke-linecap": "butt", "stroke-linejoin": "miter", "fill-opacity": "1",
    "stroke-opacity": "1", "font-family": "sans-serif", "font-size": "16",
    "font-weight": "400", "font-style": "normal", "text-anchor": "start",
}

_NAMED_COLORS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0), "green": (0, 128, 0),
    "blue": (0, 0, 255), "yellow": (255, 255, 0), "orange": (255, 165, 0),
    "purple": (128, 0, 128), "gray": (128, 128, 128), "grey": (128, 128, 128),
    "silver": (192, 192, 192), "maroon": (128, 0, 0), "navy": (0, 0, 128),
    "teal": (0, 128, 128), "olive": (128, 128, 0), "lime": (0, 255, 0),
    "aqua": (0, 255, 255), "cyan": (0, 255, 255), "fuchsia": (255, 0, 255),
    "magenta": (255, 0, 255), "brown": (165, 42, 42), "pink": (255, 192, 203),
}

#: Unicode -> code in the standard Symbol font, for characters Windows-1252 lacks.
_SYMBOL = {
    **{ord(c): 0x41 + i for i, c in enumerate("ΑΒΧΔΕΦΓΗΙϑΚΛΜΝΟΠΘΡΣΤΥςΩΞΨΖ")},
    **{ord(c): 0x61 + i for i, c in enumerate("αβχδεφγηιϕκλμνοπθρστυϖωξψζ")},
    0x2200: 0x22, 0x2203: 0x24, 0x220B: 0x27, 0x2217: 0x2A, 0x2212: 0x2D, 0x2245: 0x40,
    0x2234: 0x5C, 0x22A5: 0x5E, 0x223C: 0x7E, 0x2032: 0xA2, 0x2264: 0xA3, 0x2044: 0xA4,
    0x221E: 0xA5, 0x2663: 0xA7, 0x2666: 0xA8, 0x2665: 0xA9, 0x2660: 0xAA, 0x2194: 0xAB,
    0x2190: 0xAC, 0x2191: 0xAD, 0x2192: 0xAE, 0x2193: 0xAF, 0x2033: 0xB2, 0x2265: 0xB3,
    0x221D: 0xB5, 0x2202: 0xB6, 0x2260: 0xB9, 0x2261: 0xBA, 0x2248: 0xBB, 0x21B5: 0xBF,
    0x2135: 0xC0, 0x2111: 0xC1, 0x211C: 0xC2, 0x2118: 0xC3, 0x2297: 0xC4, 0x2295: 0xC5,
    0x2205: 0xC6, 0x2229: 0xC7, 0x222A: 0xC8, 0x2283: 0xC9, 0x2287: 0xCA, 0x2284: 0xCB,
    0x2282: 0xCC, 0x2286: 0xCD, 0x2208: 0xCE, 0x2209: 0xCF, 0x2220: 0xD0, 0x2207: 0xD1,
    0x220F: 0xD5, 0x221A: 0xD6, 0x22C5: 0xD7, 0x2227: 0xD9, 0x2228: 0xDA, 0x21D4: 0xDB,
    0x21D0: 0xDC, 0x21D1: 0xDD, 0x21D2: 0xDE, 0x21D3: 0xDF, 0x25CA: 0xE0, 0x2211: 0xE5,
    0x222B: 0xF2,
}

_FONT_NAMES = {
    # (family, bold, italic) -> PostScript name of a standard font
    ("sans", False, False): "Helvetica", ("sans", True, False): "Helvetica-Bold",
    ("sans", False, True): "Helvetica-Oblique", ("sans", True, True): "Helvetica-BoldOblique",
    ("serif", False, False): "Times-Roman", ("serif", True, False): "Times-Bold",
    ("serif", False, True): "Times-Italic", ("serif", True, True): "Times-BoldItalic",
    ("mono", False, False): "Courier", ("mono", True, False): "Courier-Bold",
    ("mono", False, True): "Courier-Oblique", ("mono", True, True): "Courier-BoldOblique",
}
_SERIF_TABLES = {
    (False, False): _serif.REGULAR, (True, False): _serif.BOLD,
    (False, True): _serif.ITALIC, (True, True): _serif.BOLD_ITALIC,
}

#: Shadow rings, as multiples of the blur's standard deviation.
_SHADOW_RINGS = (0.3, 0.6, 0.95, 1.35, 1.8, 2.4)

Matrix = tuple[float, float, float, float, float, float]
_IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


class PDFExportError(ValueError):
    """The SVG holds something the PDF writer does not draw."""


# ----------------------------------------------------------------------- helpers

def _fmt(value: float) -> str:
    """A number as PDF wants it: no exponent, no trailing zeros."""
    if not math.isfinite(value):
        raise PDFExportError(f"non-finite number {value!r}")
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _attrs(el: ET.Element) -> dict[str, str]:
    return {_local(k): v for k, v in el.attrib.items()}


def _float(value: str, what: str) -> float:
    try:
        return float(value.strip().removesuffix("px"))
    except ValueError:
        raise PDFExportError(f"cannot read {what} {value!r}") from None


def _color(value: str) -> Optional[tuple[float, float, float]]:
    """An SVG colour as RGB fractions, or None for ``none``."""
    v = value.strip().lower()
    if v in ("none", "transparent"):
        return None
    if re.fullmatch(r"#[0-9a-f]{6}", v):
        return (int(v[1:3], 16) / 255.0, int(v[3:5], 16) / 255.0, int(v[5:7], 16) / 255.0)
    if re.fullmatch(r"#[0-9a-f]{3}", v):
        return (int(v[1] * 2, 16) / 255.0, int(v[2] * 2, 16) / 255.0, int(v[3] * 2, 16) / 255.0)
    m = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", v)
    if m:
        return (min(int(m[1]), 255) / 255.0, min(int(m[2]), 255) / 255.0, min(int(m[3]), 255) / 255.0)
    if v in _NAMED_COLORS:
        r, g, b = _NAMED_COLORS[v]
        return (r / 255.0, g / 255.0, b / 255.0)
    raise PDFExportError(f"colour {value!r} is not supported in PDF export; use #RRGGBB")


def _multiply(inner: Matrix, outer: Matrix) -> Matrix:
    """The matrix that applies ``inner`` first, then ``outer``."""
    a1, b1, c1, d1, e1, f1 = inner
    a2, b2, c2, d2, e2, f2 = outer
    return (
        a1 * a2 + b1 * c2, a1 * b2 + b1 * d2,
        c1 * a2 + d1 * c2, c1 * b2 + d1 * d2,
        e1 * a2 + f1 * c2 + e2, e1 * b2 + f1 * d2 + f2,
    )


def _apply(m: Matrix, x: float, y: float) -> tuple[float, float]:
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


_TRANSFORM_RE = re.compile(r"(\w+)\s*\(([^)]*)\)")


def _parse_transform(value: str) -> Matrix:
    """An SVG ``transform`` attribute as one matrix."""
    result = _IDENTITY
    consumed = _TRANSFORM_RE.sub("", value).replace(",", "").strip()
    if consumed:
        raise PDFExportError(f"cannot read transform {value!r}")
    for name, body in _TRANSFORM_RE.findall(value):
        n = [_float(v, "transform") for v in re.split(r"[\s,]+", body.strip()) if v]
        if name == "translate" and len(n) in (1, 2):
            step: Matrix = (1.0, 0.0, 0.0, 1.0, n[0], n[1] if len(n) == 2 else 0.0)
        elif name == "scale" and len(n) in (1, 2):
            step = (n[0], 0.0, 0.0, n[1] if len(n) == 2 else n[0], 0.0, 0.0)
        elif name == "rotate" and len(n) in (1, 3):
            c, s = math.cos(math.radians(n[0])), math.sin(math.radians(n[0]))
            step = (c, s, -s, c, 0.0, 0.0)
            if len(n) == 3:
                step = _multiply(_multiply((1.0, 0.0, 0.0, 1.0, -n[1], -n[2]), step),
                                 (1.0, 0.0, 0.0, 1.0, n[1], n[2]))
        elif name == "matrix" and len(n) == 6:
            step = (n[0], n[1], n[2], n[3], n[4], n[5])
        else:
            raise PDFExportError(f"cannot read transform {value!r}")
        # The leftmost transform is the outermost one.
        result = _multiply(step, result)
    return result


def _transform_commands(commands: Sequence[drawing.Command], m: Matrix) -> list[drawing.Command]:
    out: list[drawing.Command] = []
    for c in commands:
        vals = c[1:]
        pts: list[float] = []
        for i in range(0, len(vals), 2):
            pts.extend(_apply(m, vals[i], vals[i + 1]))
        out.append((c[0], *pts))
    return out


def _rounded_rect(x: float, y: float, w: float, h: float, rx: float, ry: float) -> tuple[drawing.Command, ...]:
    rx, ry = min(max(rx, 0.0), w / 2.0), min(max(ry, 0.0), h / 2.0)
    if rx <= 0.0 or ry <= 0.0:
        return drawing.rect(x, y, w, h)
    kx, ky = rx * (1.0 - drawing.KAPPA), ry * (1.0 - drawing.KAPPA)
    r, b = x + w, y + h
    return (
        ("M", x + rx, y), ("L", r - rx, y), ("C", r - kx, y, r, y + ky, r, y + ry),
        ("L", r, b - ry), ("C", r, b - ky, r - kx, b, r - rx, b),
        ("L", x + rx, b), ("C", x + kx, b, x, b - ky, x, b - ry),
        ("L", x, y + ry), ("C", x, y + ky, x + kx, y, x + rx, y), ("Z",),
    )


def _points(value: str) -> list[tuple[float, float]]:
    n = [_float(v, "points") for v in re.split(r"[\s,]+", value.strip()) if v]
    if len(n) % 2:
        raise PDFExportError(f"odd number of coordinates in points {value[:30]!r}")
    return [(n[i], n[i + 1]) for i in range(0, len(n), 2)]


def _path_ops(commands: Iterable[drawing.Command]) -> list[str]:
    ops = []
    for c in commands:
        if c[0] == "M":
            ops.append(f"{_fmt(c[1])} {_fmt(c[2])} m")
        elif c[0] == "L":
            ops.append(f"{_fmt(c[1])} {_fmt(c[2])} l")
        elif c[0] == "C":
            ops.append(" ".join(_fmt(v) for v in c[1:]) + " c")
        else:
            ops.append("h")
    return ops


def _end_directions(commands: Sequence[drawing.Command]) -> Optional[tuple[tuple[float, float], float, tuple[float, float], float]]:
    """First point and outgoing angle, last point and incoming angle, of an open path."""
    pts: list[tuple[float, float]] = []
    for c in commands:
        vals = c[1:]
        pts.extend((vals[i], vals[i + 1]) for i in range(0, len(vals), 2))
    if len(pts) < 2:
        return None

    def angle(origin: tuple[float, float], others: Iterable[tuple[float, float]], flip: bool) -> float:
        for p in others:
            dx, dy = p[0] - origin[0], p[1] - origin[1]
            if abs(dx) > 1e-9 or abs(dy) > 1e-9:
                return math.atan2(-dy, -dx) if flip else math.atan2(dy, dx)
        return 0.0

    return pts[0], angle(pts[0], pts[1:], False), pts[-1], angle(pts[-1], reversed(pts[:-1]), True)


# ------------------------------------------------------------------------- text

def _font_key(style: dict[str, str]) -> tuple[str, bool, bool]:
    families = [f.strip().strip("'\"").lower() for f in style["font-family"].split(",")]
    generic = families[-1] if families else ""
    if generic == "serif" or (generic not in ("sans-serif", "monospace") and any("times" in f or f.endswith(" serif") for f in families)):
        family = "serif"
    elif generic == "monospace" or any("courier" in f or "mono" in f for f in families):
        family = "mono"
    else:
        family = "sans"
    weight = style["font-weight"].strip().lower()
    bold = weight in ("bold", "bolder") or (weight.isdigit() and int(weight) >= 600)
    italic = style["font-style"].strip().lower() in ("italic", "oblique")
    return family, bold, italic


def _char_width(ch: str, key: tuple[str, bool, bool]) -> float:
    """Advance of ``ch`` as a fraction of the font size."""
    family, bold, italic = key
    if family == "mono":
        return 0.6
    if family == "serif":
        w = _SERIF_TABLES[(bold, italic)].get(ord(ch))
        if w is not None:
            return w / float(_serif.UNITS_PER_EM)
    return _metrics.char_width(ch, bold)


def _pdf_string(data: bytes) -> str:
    out = []
    for byte in data:
        if byte in (0x28, 0x29, 0x5C):
            out.append("\\" + chr(byte))
        elif 0x20 <= byte < 0x7F:
            out.append(chr(byte))
        else:
            out.append(f"\\{byte:03o}")
    return "(" + "".join(out) + ")"


# ----------------------------------------------------------------------- writer

@dataclass
class _Marker:
    element: ET.Element
    view_box: tuple[float, float, float, float]
    ref: tuple[float, float]
    size: tuple[float, float]
    orient: str


@dataclass
class _Shadow:
    dx: float
    dy: float
    sigma: float
    color: tuple[float, float, float]
    opacity: float


@dataclass
class _Resources:
    fonts: dict[str, str] = field(default_factory=dict)  # PostScript name -> /F1
    states: dict[tuple[float, float], str] = field(default_factory=dict)  # (ca, CA) -> /G1
    forms: list[bytes] = field(default_factory=list)  # content of /X1, /X2, ...
    unsupported: set[str] = field(default_factory=set)

    def font(self, name: str) -> str:
        return self.fonts.setdefault(name, f"F{len(self.fonts) + 1}")

    def state(self, fill_alpha: float, stroke_alpha: float) -> str:
        key = (round(fill_alpha, 4), round(stroke_alpha, 4))
        return self.states.setdefault(key, f"G{len(self.states) + 1}")


class _Converter:
    def __init__(self, root: ET.Element) -> None:
        if _local(root.tag) != "svg":
            raise PDFExportError("not an SVG document")
        a = _attrs(root)
        box = [_float(v, "viewBox") for v in re.split(r"[\s,]+", a.get("viewBox", "").strip()) if v]
        if len(box) != 4:
            width, height = a.get("width"), a.get("height")
            if width is None or height is None:
                raise PDFExportError("the SVG needs a viewBox, or a width and a height")
            box = [0.0, 0.0, _float(width, "width"), _float(height, "height")]
        self.view_box = (box[0], box[1], box[2], box[3])
        self.width = _float(a["width"], "width") if "width" in a and not a["width"].endswith("%") else box[2]
        self.height = _float(a["height"], "height") if "height" in a and not a["height"].endswith("%") else box[3]
        if min(self.width, self.height, box[2], box[3]) <= 0.0:
            raise PDFExportError("the SVG has no area")
        self.root = root
        self.res = _Resources()
        self.markers: dict[str, _Marker] = {}
        self.shadows: dict[str, _Shadow] = {}
        for el in root.iter():
            name = _local(el.tag)
            if name == "marker":
                self._read_marker(el)
            elif name == "filter":
                self._read_filter(el)

    # -- definitions

    def _read_marker(self, el: ET.Element) -> None:
        a = _attrs(el)
        size = (_float(a.get("markerWidth", "3"), "markerWidth"), _float(a.get("markerHeight", "3"), "markerHeight"))
        vb = [_float(v, "viewBox") for v in re.split(r"[\s,]+", a.get("viewBox", "").strip()) if v]
        if len(vb) != 4:
            vb = [0.0, 0.0, size[0], size[1]]
        if "id" in a:
            self.markers[a["id"]] = _Marker(
                el, (vb[0], vb[1], vb[2], vb[3]),
                (_float(a.get("refX", "0"), "refX"), _float(a.get("refY", "0"), "refY")),
                size, a.get("orient", "0"),
            )

    def _read_filter(self, el: ET.Element) -> None:
        a = _attrs(el)
        children = list(el)
        if len(children) != 1 or _local(children[0].tag) != "feDropShadow":
            raise PDFExportError("only a single feDropShadow filter is supported in PDF export")
        s = _attrs(children[0])
        sigma = _float(s.get("stdDeviation", "2").split()[0], "stdDeviation")
        color = _color(s.get("flood-color", "#000000")) or (0.0, 0.0, 0.0)
        if "id" in a:
            self.shadows[a["id"]] = _Shadow(
                _float(s.get("dx", "2"), "dx"), _float(s.get("dy", "2"), "dy"), sigma, color,
                _float(s.get("flood-opacity", "1"), "flood-opacity"),
            )

    @staticmethod
    def _reference(value: str, what: str) -> str:
        m = re.fullmatch(r"url\(\s*['\"]?#([^)'\"]+)['\"]?\s*\)", value.strip())
        if not m:
            raise PDFExportError(f"cannot read {what} reference {value!r}")
        return m[1]

    # -- document

    def page(self) -> bytes:
        vx, vy, vw, vh = self.view_box
        sx, sy = self.width / vw, self.height / vh
        # px -> pt, flip the y axis, then map the viewBox onto the page.
        out = [
            f"{_fmt(PX_TO_PT * sx)} 0 0 {_fmt(-PX_TO_PT * sy)} "
            f"{_fmt(-vx * sx * PX_TO_PT)} {_fmt((self.height + vy * sy) * PX_TO_PT)} cm"
        ]
        style = dict(_DEFAULTS)
        for child in self.root:
            self._draw(child, style, out)
        return ("\n".join(out) + "\n").encode("ascii")

    def _style(self, a: dict[str, str], inherited: dict[str, str]) -> dict[str, str]:
        unknown = sorted(set(a) - ATTRIBUTES)
        if unknown:
            raise PDFExportError(f"SVG attribute(s) {', '.join(unknown)} are not supported in PDF export")
        style = dict(inherited)
        for name in _INHERITED:
            if name in a and a[name] != "inherit":
                style[name] = a[name]
        return style

    def _draw(self, el: ET.Element, inherited: dict[str, str], out: list[str]) -> None:
        name = _local(el.tag)
        if name not in ELEMENTS:
            raise PDFExportError(f"SVG element <{name}> is not supported in PDF export")
        if name in ("defs", "title", "desc", "marker", "filter"):
            return
        a = _attrs(el)
        style = self._style(a, inherited)
        opacity = _float(a["opacity"], "opacity") if "opacity" in a else 1.0
        if name in ("g", "svg"):
            self._group(el, a, style, opacity, out)
            return
        out.append("q")
        if "transform" in a:
            out.append(" ".join(_fmt(v) for v in _parse_transform(a["transform"])) + " cm")
        if name == "text":
            self._text(el, a, style, opacity, out)
        else:
            commands = self._outline(name, a)
            if commands:
                self._paint(commands, a, style, opacity, out)
        out.append("Q")

    def _group(self, el: ET.Element, a: dict[str, str], style: dict[str, str], opacity: float, out: list[str]) -> None:
        body: list[str] = []
        if "filter" in a and a["filter"] != "none":
            shadow = self.shadows.get(self._reference(a["filter"], "filter"))
            if shadow is None:
                raise PDFExportError(f"filter {a['filter']!r} is not defined")
            self._shadow(el, shadow, body)
        for child in el:
            self._draw(child, style, body)
        out.append("q")
        if "transform" in a:
            out.append(" ".join(_fmt(v) for v in _parse_transform(a["transform"])) + " cm")
        if opacity < 1.0:
            # A group fades as one image, so it is drawn as a transparency group.
            self.res.forms.append(("\n".join(body) + "\n").encode("ascii"))
            out.append(f"/{self.res.state(opacity, opacity)} gs")
            out.append(f"/X{len(self.res.forms)} Do")
        else:
            out.extend(body)
        out.append("Q")

    # -- shapes

    def _outline(self, name: str, a: dict[str, str]) -> tuple[drawing.Command, ...]:
        def num(key: str, default: float = 0.0) -> float:
            if key not in a:
                return default
            value = a[key]
            if value.endswith("%"):
                span = self.view_box[2] if key in ("x", "width", "x1", "x2", "cx", "rx") else self.view_box[3]
                return _float(value[:-1], key) / 100.0 * span
            return _float(value, key)

        if name == "path":
            try:
                return drawing.parse_path(a.get("d", ""))
            except ValueError as exc:
                raise PDFExportError(str(exc)) from None
        if name == "rect":
            w, h = num("width"), num("height")
            if w <= 0.0 or h <= 0.0:
                return ()
            rx = num("rx", num("ry", 0.0))
            return _rounded_rect(num("x"), num("y"), w, h, rx, num("ry", rx))
        if name == "circle":
            return drawing.ellipse(num("cx"), num("cy"), num("r")) if num("r") > 0.0 else ()
        if name == "ellipse":
            return drawing.ellipse(num("cx"), num("cy"), num("rx"), num("ry")) if num("rx") > 0.0 and num("ry") > 0.0 else ()
        if name == "line":
            return (("M", num("x1"), num("y1")), ("L", num("x2"), num("y2")))
        if name in ("polyline", "polygon"):
            return drawing.polyline(_points(a.get("points", "")), closed=name == "polygon")
        raise PDFExportError(f"SVG element <{name}> is not supported in PDF export")

    def _paint(
        self, commands: Sequence[drawing.Command], a: dict[str, str], style: dict[str, str],
        opacity: float, out: list[str],
    ) -> None:
        fill = _color(style["fill"])
        stroke = _color(style["stroke"])
        width = _float(style["stroke-width"], "stroke-width")
        if width <= 0.0:
            stroke = None
        fill_alpha = opacity * _float(style["fill-opacity"], "fill-opacity")
        stroke_alpha = opacity * _float(style["stroke-opacity"], "stroke-opacity")
        if fill is not None or stroke is not None:
            if fill_alpha < 1.0 or stroke_alpha < 1.0:
                out.append(f"/{self.res.state(fill_alpha, stroke_alpha)} gs")
            if fill is not None:
                out.append(" ".join(_fmt(v) for v in fill) + " rg")
            if stroke is not None:
                out.append(" ".join(_fmt(v) for v in stroke) + " RG")
                out.append(f"{_fmt(width)} w")
                cap = {"butt": 0, "round": 1, "square": 2}.get(style["stroke-linecap"], 0)
                join = {"miter": 0, "round": 1, "bevel": 2}.get(style["stroke-linejoin"], 0)
                if cap:
                    out.append(f"{cap} J")
                if join:
                    out.append(f"{join} j")
                else:
                    out.append("4 M")  # the SVG miter limit
                dash = style["stroke-dasharray"].strip()
                if dash and dash != "none":
                    lengths = [_float(v, "stroke-dasharray") for v in re.split(r"[\s,]+", dash) if v]
                    if len(lengths) % 2:
                        lengths *= 2
                    if any(v < 0.0 for v in lengths):
                        raise PDFExportError(f"negative length in stroke-dasharray {dash!r}")
                    if sum(lengths) > 0.0:
                        out.append("[" + " ".join(_fmt(v) for v in lengths) + "] 0 d")
            out.extend(_path_ops(commands))
            out.append("B" if fill is not None and stroke is not None else ("f" if fill is not None else "S"))
        ends = _end_directions(commands)
        for key in ("marker-start", "marker-end"):
            if key in a and a[key] != "none" and ends is not None:
                marker = self.markers.get(self._reference(a[key], key))
                if marker is None:
                    raise PDFExportError(f"marker {a[key]!r} is not defined")
                point, angle = (ends[0], ends[1]) if key == "marker-start" else (ends[2], ends[3])
                self._marker(marker, point, angle, key == "marker-start", width, out)

    def _marker(
        self, marker: _Marker, point: tuple[float, float], angle: float, at_start: bool,
        stroke_width: float, out: list[str],
    ) -> None:
        orient = marker.orient.strip()
        if orient == "auto-start-reverse":
            theta = angle + math.pi if at_start else angle
        elif orient == "auto":
            theta = angle
        else:
            theta = math.radians(_float(orient.removesuffix("deg"), "orient"))
        vx, vy, vw, vh = marker.view_box
        if vw <= 0.0 or vh <= 0.0:
            return
        # markerUnits is strokeWidth; the viewBox is fitted into the marker box.
        scale = min(marker.size[0] / vw, marker.size[1] / vh) * stroke_width
        c, s = math.cos(theta), math.sin(theta)
        m = _multiply((1.0, 0.0, 0.0, 1.0, -marker.ref[0], -marker.ref[1]), (scale, 0.0, 0.0, scale, 0.0, 0.0))
        m = _multiply(_multiply(m, (c, s, -s, c, 0.0, 0.0)), (1.0, 0.0, 0.0, 1.0, point[0], point[1]))
        out.append("q")
        out.append(" ".join(_fmt(v) for v in m) + " cm")
        out.append(f"{_fmt(vx)} {_fmt(vy)} {_fmt(vw)} {_fmt(vh)} re W n")
        style = dict(_DEFAULTS)
        for child in marker.element:
            self._draw(child, style, out)
        out.append("Q")

    # -- shadows

    def _silhouette(self, el: ET.Element, m: Matrix, inherited_fill: str, into: list[drawing.Command]) -> None:
        name = _local(el.tag)
        a = _attrs(el)
        if "transform" in a:
            m = _multiply(_parse_transform(a["transform"]), m)
        fill = a.get("fill", inherited_fill)
        if name == "g":
            for child in el:
                self._silhouette(child, m, fill, into)
        elif name in ("path", "rect", "circle", "ellipse", "polygon") and _color(fill) is not None:
            into.extend(_transform_commands(self._outline(name, a), m))

    def _shadow(self, group: ET.Element, shadow: _Shadow, out: list[str]) -> None:
        """Stand-in for a blurred drop shadow: the group's outline, in fading rings."""
        outline: list[drawing.Command] = []
        for child in group:
            self._silhouette(child, (1.0, 0.0, 0.0, 1.0, shadow.dx, shadow.dy), _DEFAULTS["fill"], outline)
        if not outline or shadow.opacity <= 0.0:
            return
        sigma = max(shadow.sigma, 0.0)

        def target(distance: float) -> float:
            """Opacity of a blurred edge ``distance`` outside it."""
            if sigma == 0.0:
                return shadow.opacity if distance <= 0.0 else 0.0
            return shadow.opacity * 0.5 * (1.0 - math.erf(distance / (sigma * math.sqrt(2.0))))

        # Band k lies between ring k-1 and ring k; every ring from k outward covers it.
        edges = [0.0] + [r * sigma for r in _SHADOW_RINGS] if sigma > 0.0 else [0.0]
        wanted = [target(-math.hypot(shadow.dx, shadow.dy) / 2.0)]
        wanted += [target((edges[k - 1] + edges[k]) / 2.0) for k in range(1, len(edges))]
        alphas = []
        outer = 0.0
        for t in reversed(wanted):
            alphas.append(max(0.0, 1.0 - (1.0 - t) / (1.0 - outer)))
            outer = t
        alphas.reverse()
        path = _path_ops(outline)
        out.append("q")
        out.append(" ".join(_fmt(v) for v in shadow.color) + " rg")
        out.append(" ".join(_fmt(v) for v in shadow.color) + " RG")
        out.append("1 j 1 J")
        for k in range(len(edges) - 1, 0, -1):
            out.append(f"/{self.res.state(alphas[k], alphas[k])} gs {_fmt(2.0 * edges[k])} w")
            out.extend(path)
            out.append("S")
        out.append(f"/{self.res.state(alphas[0], alphas[0])} gs")
        out.extend(path)
        out.append("f")
        out.append("Q")

    # -- text

    def _text(self, el: ET.Element, a: dict[str, str], style: dict[str, str], opacity: float, out: list[str]) -> None:
        preserve = a.get("space") == "preserve"
        pen = [_float(a.get("x", "0"), "x"), _float(a.get("y", "0"), "y")]

        def clean(text: Optional[str]) -> str:
            if not text:
                return ""
            return text if preserve else re.sub(r"\s+", " ", text).strip()

        self._chunk(clean(el.text), a, style, opacity, pen, out)
        for span in el:
            if _local(span.tag) != "tspan":
                raise PDFExportError(f"<{_local(span.tag)}> inside <text> is not supported in PDF export")
            if len(span):
                raise PDFExportError("nested <tspan> is not supported in PDF export")
            sa = _attrs(span)
            span_style = self._style(sa, style)
            if "x" in sa:
                pen[0] = _float(sa["x"], "x")
            if "y" in sa:
                pen[1] = _float(sa["y"], "y")
            pen[1] += _float(sa.get("dy", "0"), "dy")
            self._chunk(clean(span.text), sa, span_style, opacity, pen, out)
            self._chunk(clean(span.tail), {}, style, opacity, pen, out)

    def _chunk(
        self, text: str, a: dict[str, str], style: dict[str, str], opacity: float,
        pen: list[float], out: list[str],
    ) -> None:
        """Draw one run of text at the pen and move the pen past it."""
        if not text:
            return
        size = _float(style["font-size"], "font-size")
        fill = _color(style["fill"])
        key = _font_key(style)
        advances = [_char_width(ch, key) * size for ch in text]
        natural = sum(advances)
        stretch = 1.0
        if "textLength" in a and natural > 0.0:
            stretch = _float(a["textLength"], "textLength") / natural
        width = natural * stretch
        anchor = style["text-anchor"]
        x = pen[0] - (width / 2.0 if anchor == "middle" else width if anchor == "end" else 0.0)
        pen[0] = x + width
        if fill is None or size <= 0.0 or not text.strip():
            return
        base_font = self.res.font(_FONT_NAMES[key])
        # Split into runs of the text font and runs of the Symbol font.
        runs: list[tuple[str, float, bytearray]] = []
        cursor = x
        for ch, advance in zip(text, advances):
            try:
                code, font = ch.encode("cp1252")[0], base_font
            except UnicodeEncodeError:
                if ord(ch) in _SYMBOL:
                    code, font = _SYMBOL[ord(ch)], self.res.font("Symbol")
                else:
                    self.res.unsupported.add(ch)
                    code, font = 0x3F, base_font
            if not runs or runs[-1][0] != font:
                runs.append((font, cursor, bytearray()))
            runs[-1][2].append(code)
            cursor += advance * stretch
        alpha = opacity * _float(style["fill-opacity"], "fill-opacity")
        if alpha < 1.0:
            out.append(f"/{self.res.state(alpha, alpha)} gs")
        out.append(" ".join(_fmt(v) for v in fill) + " rg")
        out.append("BT")
        if abs(stretch - 1.0) > 1e-6:
            out.append(f"{_fmt(stretch * 100.0)} Tz")
        for font, start, data in runs:
            # The page is drawn y-down, so each run is flipped upright again.
            out.append(f"/{font} {_fmt(size)} Tf 1 0 0 -1 {_fmt(start)} {_fmt(pen[1])} Tm {_pdf_string(bytes(data))} Tj")
        out.append("ET")


# ------------------------------------------------------------------- file layout

#: family -> (ascent, descent, cap height, bounding box, stem, bold stem, italic angle)
_FONT_SHAPES = {
    "sans": (718, -207, 718, "-170 -228 1003 962", 88, 140, -12),
    "serif": (683, -217, 662, "-200 -218 1000 898", 84, 139, -15.5),
    "mono": (629, -157, 562, "-113 -250 749 801", 51, 106, -12),
}


def _font_object(name: str) -> str:
    """A standard font, with the widths and description a viewer needs to stand in for it."""
    if name == "Symbol":
        return "<< /Type /Font /Subtype /Type1 /BaseFont /Symbol >>"
    key = next(k for k, v in _FONT_NAMES.items() if v == name)
    family, bold, italic = key
    ascent, descent, cap, box, stem, bold_stem, angle = _FONT_SHAPES[family]
    widths = []
    for byte in range(32, 256):
        try:
            widths.append(round(_char_width(bytes([byte]).decode("cp1252"), key) * 1000))
        except UnicodeDecodeError:
            widths.append(0)
    flags = 32 | (1 if family == "mono" else 0) | (2 if family == "serif" else 0)
    flags |= (64 if italic else 0) | (262144 if bold else 0)
    descriptor = (
        f"<< /Type /FontDescriptor /FontName /{name} /Flags {flags} /FontBBox [{box}] "
        f"/ItalicAngle {_fmt(angle if italic else 0)} /Ascent {ascent} /Descent {descent} "
        f"/CapHeight {cap} /StemV {bold_stem if bold else stem} /FontWeight {700 if bold else 400} >>"
    )
    return (
        f"<< /Type /Font /Subtype /Type1 /BaseFont /{name} /Encoding /WinAnsiEncoding "
        f"/FirstChar 32 /LastChar 255 /Widths [{' '.join(str(w) for w in widths)}] "
        f"/FontDescriptor {descriptor} >>"
    )


def _assemble(conv: _Converter, content: bytes, title: Optional[str], producer: str, compress: bool) -> bytes:
    res = conv.res
    objects: list[bytes] = []

    def add(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    def stream(data: bytes, extra: str = "") -> bytes:
        flate = ""
        if compress:
            data = zlib.compress(data, 9)
            flate = " /Filter /FlateDecode"
        return f"<<{extra} /Length {len(data)}{flate} >>\nstream\n".encode("ascii") + data + b"\nendstream"

    def text_string(value: str) -> str:
        try:
            return _pdf_string(value.encode("ascii"))
        except UnicodeEncodeError:
            return "<" + ("﻿" + value).encode("utf-16-be").hex().upper() + ">"

    catalog = add(b"")
    pages = add(b"")
    page = add(b"")
    font_ids = {}
    for name, tag in res.fonts.items():
        font_ids[tag] = add(_font_object(name).encode("ascii"))
    resources = "<<"
    if font_ids:
        resources += " /Font << " + " ".join(f"/{tag} {num} 0 R" for tag, num in font_ids.items()) + " >>"
    if res.states:
        resources += " /ExtGState << " + " ".join(
            f"/{tag} << /Type /ExtGState /ca {_fmt(ca)} /CA {_fmt(CA)} >>" for (ca, CA), tag in res.states.items()
        ) + " >>"
    form_ids = [len(objects) + 1 + i for i in range(len(res.forms))]
    if form_ids:
        resources += " /XObject << " + " ".join(f"/X{i + 1} {num} 0 R" for i, num in enumerate(form_ids)) + " >>"
    resources += " >>"
    resources_id = len(objects) + len(res.forms) + 1
    big = 1_000_000
    for body in res.forms:
        add(stream(
            body,
            f" /Type /XObject /Subtype /Form /BBox [{-big} {-big} {big} {big}]"
            f" /Group << /S /Transparency /CS /DeviceRGB >> /Resources {resources_id} 0 R",
        ))
    assert add(resources.encode("ascii")) == resources_id
    contents = add(stream(content))
    info = f"<< /Producer {text_string(producer)}"
    if title:
        info += f" /Title {text_string(title)}"
    info_id = add((info + " >>").encode("ascii"))

    w, h = conv.width * PX_TO_PT, conv.height * PX_TO_PT
    objects[catalog - 1] = f"<< /Type /Catalog /Pages {pages} 0 R >>".encode("ascii")
    objects[pages - 1] = f"<< /Type /Pages /Kids [{page} 0 R] /Count 1 >>".encode("ascii")
    objects[page - 1] = (
        f"<< /Type /Page /Parent {pages} 0 R /MediaBox [0 0 {_fmt(w)} {_fmt(h)}] "
        f"/Resources {resources_id} 0 R /Contents {contents} 0 R "
        f"/Group << /S /Transparency /CS /DeviceRGB >> >>"
    ).encode("ascii")

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode("ascii") + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode("ascii")
    # The id is a digest of the content, so the same diagram gives the same file.
    digest = hashlib.md5(bytes(out)).hexdigest().upper()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog} 0 R /Info {info_id} 0 R "
        f"/ID [<{digest}> <{digest}>] >>\nstartxref\n{xref}\n%%EOF\n"
    ).encode("ascii")
    return bytes(out)


def svg_to_pdf(
    svg: str,
    *,
    title: Optional[str] = None,
    producer: str = "diagrams-as-code",
    compress: bool = True,
) -> bytes:
    """A one-page vector PDF of an SVG written by this package.

    The page is the SVG's size at 0.75 pt per px. The output has no timestamp:
    the same SVG always gives the same bytes on one machine (``compress=False``
    gives the same bytes on every machine, at several times the size).
    """
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        raise PDFExportError(f"the SVG is not well-formed: {exc}") from None
    conv = _Converter(root)
    content = conv.page()
    if conv.res.unsupported:
        shown = " ".join(sorted(conv.res.unsupported))
        warnings.warn(
            f"PDF export: no standard PDF font has the character(s) {shown}; drawn as '?'",
            stacklevel=2,
        )
    return _assemble(conv, content, title, producer, compress)


__all__ = ["ATTRIBUTES", "ELEMENTS", "PDFExportError", "PX_TO_PT", "svg_to_pdf"]
