r"""A small TeX-like math typesetter that produces positioned glyph outlines.

Supported inside ``$...$``: letters (set in math italic), digits, sub/superscripts
with ``_`` and ``^``, ``{}`` grouping, Greek letters, the operators and relations
in ``SYMBOLS``, ``\mathrm{}`` / ``\text{}`` / ``\mathbf{}``, limits under big
operators, and the spaces ``\\,`` ``\;`` ``\\quad``. This is not TeX: no
fractions, radicals or matrices.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from diagrams_as_code.text import _math_glyphs as _mg

EM = float(_mg.UNITS_PER_EM)
SCRIPT_SCALE = _mg.SCRIPT_PERCENT / 100.0
AXIS = _mg.AXIS_HEIGHT / EM
SUB_DROP = _mg.SUBSCRIPT_SHIFT_DOWN / EM
SUP_RISE = _mg.SUPERSCRIPT_SHIFT_UP / EM

THIN, MEDIUM, THICK = 3 / 18, 4 / 18, 5 / 18
BIG_OP_SCALE = 1.25

ORD, BIN, REL, OPEN, CLOSE, PUNCT, OP = "ord", "bin", "rel", "open", "close", "punct", "op"

_GREEK_LOWER = (
    "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron "
    "pi rho varsigma sigma tau upsilon phi chi psi omega"
).split()
_GREEK_UPPER = {
    "Gamma": 0x393, "Delta": 0x394, "Theta": 0x398, "Lambda": 0x39B, "Xi": 0x39E,
    "Pi": 0x3A0, "Sigma": 0x3A3, "Upsilon": 0x3A5, "Phi": 0x3A6, "Psi": 0x3A8, "Omega": 0x3A9,
}

#: command -> (codepoint, class)
SYMBOLS: dict[str, tuple[int, str]] = {
    **{name: (0x1D6FC + i, ORD) for i, name in enumerate(_GREEK_LOWER)},
    **{name: (cp, ORD) for name, cp in _GREEK_UPPER.items()},
    "partial": (0x1D715, ORD), "varepsilon": (0x1D716, ORD), "vartheta": (0x1D717, ORD),
    "varphi": (0x1D719, ORD), "varrho": (0x1D71A, ORD), "varpi": (0x1D71B, ORD),
    "forall": (0x2200, ORD), "exists": (0x2203, ORD), "nexists": (0x2204, ORD),
    "emptyset": (0x2205, ORD), "nabla": (0x2207, ORD), "infty": (0x221E, ORD),
    "ell": (0x2113, ORD), "hbar": (0x210F, ORD), "top": (0x22A4, ORD), "bot": (0x22A5, ORD),
    "neg": (0xAC, ORD), "lnot": (0xAC, ORD), "angle": (0x2220, ORD), "prime": (0x2032, ORD),
    "ldots": (0x2026, ORD), "dots": (0x2026, ORD), "cdots": (0x22EF, ORD), "vdots": (0x22EE, ORD),
    "mathbbR": (0x211D, ORD), "mathbbN": (0x2115, ORD), "mathbbZ": (0x2124, ORD),
    "mathbbQ": (0x211A, ORD), "mathbbC": (0x2102, ORD),
    "pm": (0xB1, BIN), "mp": (0x2213, BIN), "times": (0xD7, BIN), "div": (0xF7, BIN),
    "cdot": (0x22C5, BIN), "ast": (0x2217, BIN), "circ": (0x2218, BIN), "bullet": (0x2219, BIN),
    "land": (0x2227, BIN), "wedge": (0x2227, BIN), "lor": (0x2228, BIN), "vee": (0x2228, BIN),
    "cap": (0x2229, BIN), "cup": (0x222A, BIN), "setminus": (0x2216, BIN),
    "oplus": (0x2295, BIN), "ominus": (0x2296, BIN), "otimes": (0x2297, BIN), "odot": (0x2299, BIN),
    "sqcap": (0x2293, BIN), "sqcup": (0x2294, BIN), "uplus": (0x228E, BIN), "diamond": (0x22C4, BIN),
    "leq": (0x2264, REL), "le": (0x2264, REL), "geq": (0x2265, REL), "ge": (0x2265, REL),
    "neq": (0x2260, REL), "ne": (0x2260, REL), "equiv": (0x2261, REL), "approx": (0x2248, REL),
    "sim": (0x223C, REL), "simeq": (0x2243, REL), "cong": (0x2245, REL), "propto": (0x221D, REL),
    "ll": (0x226A, REL), "gg": (0x226B, REL), "prec": (0x227A, REL), "succ": (0x227B, REL),
    "preceq": (0x227C, REL), "succeq": (0x227D, REL), "triangleq": (0x225C, REL),
    "coloneqq": (0x2254, REL), "in": (0x2208, REL), "notin": (0x2209, REL), "ni": (0x220B, REL),
    "subset": (0x2282, REL), "supset": (0x2283, REL), "subseteq": (0x2286, REL),
    "supseteq": (0x2287, REL), "subsetneq": (0x228A, REL), "supsetneq": (0x228B, REL),
    "sqsubseteq": (0x2291, REL), "sqsupseteq": (0x2292, REL),
    "mid": (0x2223, REL), "parallel": (0x2225, REL), "perp": (0x27C2, REL),
    "vdash": (0x22A2, REL), "dashv": (0x22A3, REL), "models": (0x22A8, REL),
    "to": (0x2192, REL), "rightarrow": (0x2192, REL), "leftarrow": (0x2190, REL),
    "gets": (0x2190, REL), "leftrightarrow": (0x2194, REL), "uparrow": (0x2191, REL),
    "downarrow": (0x2193, REL), "mapsto": (0x21A6, REL), "Rightarrow": (0x21D2, REL),
    "Leftarrow": (0x21D0, REL), "Leftrightarrow": (0x21D4, REL), "implies": (0x27F9, REL),
    "iff": (0x27FA, REL), "longrightarrow": (0x27F6, REL), "longleftarrow": (0x27F5, REL),
    "leadsto": (0x21DD, REL), "rightsquigarrow": (0x21DD, REL), "rightwavearrow": (0x219D, REL),
    "sum": (0x2211, OP), "prod": (0x220F, OP), "coprod": (0x2210, OP), "int": (0x222B, OP),
    "oint": (0x222E, OP), "bigcap": (0x22C2, OP), "bigcup": (0x22C3, OP),
    "bigwedge": (0x22C0, OP), "bigvee": (0x22C1, OP),
    "langle": (0x27E8, OPEN), "rangle": (0x27E9, CLOSE), "lceil": (0x2308, OPEN),
    "rceil": (0x2309, CLOSE), "lfloor": (0x230A, OPEN), "rfloor": (0x230B, CLOSE),
    "lbrace": (0x7B, OPEN), "rbrace": (0x7D, CLOSE), "vert": (0x7C, ORD), "Vert": (0x2016, ORD),
    "colon": (0x3A, PUNCT),
}

#: Function names set upright, e.g. ``\\min``.
FUNCTIONS = (
    "min max sup inf lim arg argmin argmax log ln exp sin cos tan det dim ker Pr gcd deg".split()
)

_SPACES = {",": THIN, ":": MEDIUM, ";": THICK, "!": -THIN, " ": 0.333, "quad": 1.0, "qquad": 2.0}

_CHAR_CLASS = {
    "+": BIN, "-": BIN, "*": BIN, "/": ORD, "=": REL, "<": REL, ">": REL, ":": REL,
    ",": PUNCT, ";": PUNCT, "(": OPEN, "[": OPEN, ")": CLOSE, "]": CLOSE, "|": ORD,
    ".": ORD, "!": CLOSE, "?": CLOSE, "'": ORD,
}
_UNICODE_CLASS = {cp: cls for cp, cls in SYMBOLS.values()}


@dataclass(frozen=True)
class Glyph:
    """One outline to draw: codepoint, pen position (px, y down) and font size."""

    cp: int
    x: float
    y: float
    size: float


@dataclass(frozen=True)
class MathBox:
    """A typeset formula: its extent around the baseline and its glyphs."""

    width: float
    height: float  # above the baseline
    depth: float  # below the baseline
    glyphs: tuple[Glyph, ...]

    def shifted(self, dx: float, dy: float) -> MathBox:
        return MathBox(
            self.width, self.height - dy, self.depth + dy,
            tuple(Glyph(g.cp, g.x + dx, g.y + dy, g.size) for g in self.glyphs),
        )


class MathError(ValueError):
    """The formula uses something this typesetter does not support."""


# --- parsing -----------------------------------------------------------------

@dataclass
class _Node:
    kind: str  # sym | group | text | space | script
    cls: str = ORD
    cp: int = 0
    children: Optional[list["_Node"]] = None
    text: str = ""
    bold: bool = False
    width: float = 0.0
    base: Optional["_Node"] = None
    sub: Optional["_Node"] = None
    sup: Optional["_Node"] = None
    limits: bool = False
    force: Optional[bool] = None


def _math_italic(ch: str) -> int:
    if ch == "h":
        return 0x210E
    if "A" <= ch <= "Z":
        return 0x1D434 + ord(ch) - 65
    return 0x1D44E + ord(ch) - 97


def _math_bold(ch: str) -> int:
    if "A" <= ch <= "Z":
        return 0x1D400 + ord(ch) - 65
    if "a" <= ch <= "z":
        return 0x1D41A + ord(ch) - 97
    return ord(ch)


class _Parser:
    def __init__(self, src: str) -> None:
        self.src = src
        self.i = 0

    def parse(self) -> list[_Node]:
        nodes = self._sequence(top=True)
        if self.i < len(self.src):
            raise MathError(f"unexpected '}}' at position {self.i} in ${self.src}$")
        return nodes

    def _sequence(self, top: bool = False) -> list[_Node]:
        out: list[_Node] = []
        while self.i < len(self.src):
            ch = self.src[self.i]
            if ch == "}":
                if top:
                    break
                return out
            if ch in "_^":
                self.i += 1
                arg = self._atom()
                if arg is None:
                    raise MathError(f"missing argument after '{ch}' in ${self.src}$")
                base = out.pop() if out and out[-1].kind != "space" else _Node("group", children=[])
                if base.kind != "script":
                    limits = base.force if base.force is not None else base.cls == OP
                    base = _Node("script", cls=base.cls, base=base, limits=limits)
                if ch == "_":
                    base.sub = arg
                else:
                    base.sup = arg
                out.append(base)
                continue
            node = self._atom()
            if node is None:
                continue
            if node.kind == "space" and node.text in ("limits", "nolimits"):
                if out:
                    out[-1].force = node.text == "limits"
                continue
            out.append(node)
        return out

    def _atom(self) -> Optional[_Node]:
        while self.i < len(self.src) and self.src[self.i].isspace():
            self.i += 1
        if self.i >= len(self.src):
            return None
        ch = self.src[self.i]
        if ch == "{":
            self.i += 1
            children = self._sequence()
            if self.i >= len(self.src) or self.src[self.i] != "}":
                raise MathError(f"unbalanced '{{' in ${self.src}$")
            self.i += 1
            return _Node("group", children=children)
        if ch == "\\":
            return self._command()
        self.i += 1
        if ch == "~":
            return _Node("space", width=0.333)
        if ch.isascii() and ch.isalpha():
            return _Node("sym", cp=_math_italic(ch))
        if ch == "-":
            return _Node("sym", cls=BIN, cp=0x2212)
        if ch == "'":
            return _Node("sym", cp=0x2032)
        cp = ord(ch)
        if 0x3B1 <= cp <= 0x3C9:  # Greek lowercase typed directly -> math italic
            return _Node("sym", cp=0x1D6FC + cp - 0x3B1)
        return _Node("sym", cls=_CHAR_CLASS.get(ch, _UNICODE_CLASS.get(cp, ORD)), cp=cp)

    def _command(self) -> _Node:
        self.i += 1
        if self.i >= len(self.src):
            raise MathError(f"dangling backslash in ${self.src}$")
        ch = self.src[self.i]
        if not ch.isalpha():
            self.i += 1
            if ch in _SPACES:
                return _Node("space", width=_SPACES[ch])
            if ch in "{}":
                return _Node("sym", cls=OPEN if ch == "{" else CLOSE, cp=ord(ch))
            if ch == "|":
                return _Node("sym", cp=0x2016)
            return _Node("sym", cp=ord(ch))
        j = self.i
        while j < len(self.src) and self.src[j].isalpha():
            j += 1
        name = self.src[self.i : j]
        self.i = j
        if name in ("quad", "qquad"):
            return _Node("space", width=_SPACES[name])
        if name in ("mathrm", "text", "textrm", "operatorname", "mathbf", "textbf", "mathit"):
            body = self._braced_text(name)
            if name == "mathit":
                return _Node("group", children=[_Node("sym", cp=_math_italic(c)) if c.isalpha() and c.isascii()
                                                else _Node("sym", cp=ord(c)) for c in body])
            return _Node("text", text=body, bold=name in ("mathbf", "textbf"),
                         cls=OP if name == "operatorname" else ORD)
        if name == "mathbb":
            body = self._braced_text(name)
            key = f"mathbb{body}"
            if key not in SYMBOLS:
                raise MathError(f"\\mathbb{{{body}}} is not available")
            return _Node("sym", cp=SYMBOLS[key][0])
        if name in ("limits", "nolimits"):
            return _Node("space", width=0.0, text=name)
        if name in ("left", "right", "displaystyle", "textstyle"):
            return _Node("space", width=0.0)
        if name in FUNCTIONS:
            return _Node("text", text=name, cls=OP)
        if name in SYMBOLS:
            cp, cls = SYMBOLS[name]
            return _Node("sym", cls=cls, cp=cp)
        raise MathError(f"unsupported command \\{name} in ${self.src}$")

    def _braced_text(self, name: str) -> str:
        if self.i >= len(self.src) or self.src[self.i] != "{":
            raise MathError(f"\\{name} needs a {{...}} argument in ${self.src}$")
        depth, j = 0, self.i
        while j < len(self.src):
            if self.src[j] == "{":
                depth += 1
            elif self.src[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            raise MathError(f"unbalanced '{{' in ${self.src}$")
        body = self.src[self.i + 1 : j]
        self.i = j + 1
        return body.replace("\\_", "_").replace("\\ ", " ")


# --- layout ------------------------------------------------------------------

def glyph_available(cp: int) -> bool:
    return cp in _mg.GLYPHS


def _glyph_box(cp: int, size: float) -> MathBox:
    data = _mg.GLYPHS.get(cp)
    if data is None:
        raise MathError(f"no outline for U+{cp:04X} ({chr(cp)!r})")
    adv, ymin, ymax, _ = data
    s = size / EM
    return MathBox(adv * s, max(ymax, 0) * s, max(-ymin, 0) * s, (Glyph(cp, 0.0, 0.0, size),))


def _hcat(boxes: list[MathBox]) -> MathBox:
    x = 0.0
    glyphs: list[Glyph] = []
    height = depth = 0.0
    for b in boxes:
        glyphs.extend(Glyph(g.cp, g.x + x, g.y, g.size) for g in b.glyphs)
        x += b.width
        height, depth = max(height, b.height), max(depth, b.depth)
    return MathBox(x, height, depth, tuple(glyphs))


def _space(width: float) -> MathBox:
    return MathBox(width, 0.0, 0.0, ())


def _gap(left: str, right: str) -> float:
    """Space, in em, TeX puts between two adjacent atom classes."""
    if BIN in (left, right):
        if left in (ORD, CLOSE) and right == BIN or left == BIN and right in (ORD, OPEN, OP):
            return MEDIUM
        return 0.0
    if REL in (left, right):
        return 0.0 if left == right or OPEN == left or right in (CLOSE, PUNCT) else THICK
    if left == PUNCT:
        return THIN
    if OP in (left, right):
        if left == OP and right in (ORD, OP) or left in (ORD, CLOSE) and right == OP:
            return THIN
    return 0.0


def _layout_seq(nodes: list[_Node], size: float, level: int) -> MathBox:
    # Decide which binary operators are really unary (start, or after an operator).
    classes: list[str] = []
    prev = None
    for n in nodes:
        if n.kind == "space":
            classes.append("space")
            continue
        cls = n.cls
        if cls == BIN and prev in (None, BIN, REL, OPEN, PUNCT, OP):
            cls = ORD
        classes.append(cls)
        prev = cls
    boxes: list[MathBox] = []
    prev_cls: Optional[str] = None
    for node, cls in zip(nodes, classes):
        if cls == "space":
            boxes.append(_space(node.width * size))
            continue
        if prev_cls is not None and level == 0:
            boxes.append(_space(_gap(prev_cls, cls) * size))
        boxes.append(_layout(node, size, level))
        prev_cls = cls
    return _hcat(boxes)


def _layout(node: _Node, size: float, level: int) -> MathBox:
    if node.kind == "sym":
        if node.cls == OP:
            big = size * BIG_OP_SCALE
            box = _glyph_box(node.cp, big)
            # Centre the enlarged operator on the math axis.
            centre = (box.height - box.depth) / 2.0
            return box.shifted(0.0, centre - AXIS * size)
        return _glyph_box(node.cp, size)
    if node.kind == "group":
        return _layout_seq(node.children or [], size, level)
    if node.kind == "text":
        return _hcat([
            _glyph_box(_math_bold(c) if node.bold else ord(c), size) if c != " "
            else _space(0.25 * size)
            for c in node.text
        ])
    if node.kind == "space":
        return _space(node.width * size)
    if node.kind == "script":
        return _layout_script(node, size, level)
    raise MathError(f"cannot lay out {node.kind}")


def _layout_script(node: _Node, size: float, level: int) -> MathBox:
    assert node.base is not None
    base = _layout(node.base, size, level)
    s_size = size * (SCRIPT_SCALE if level == 0 else 0.8)
    sub = _layout(node.sub, s_size, level + 1) if node.sub is not None else None
    sup = _layout(node.sup, s_size, level + 1) if node.sup is not None else None
    if node.limits:
        width = max(base.width, sub.width if sub else 0.0, sup.width if sup else 0.0)
        parts = [base.shifted((width - base.width) / 2.0, 0.0)]
        height, depth = base.height, base.depth
        gap = 0.12 * size
        if sub is not None:
            dy = base.depth + gap + sub.height
            parts.append(sub.shifted((width - sub.width) / 2.0, dy))
            depth = dy + sub.depth
        if sup is not None:
            dy = -(base.height + gap + sup.depth)
            parts.append(sup.shifted((width - sup.width) / 2.0, dy))
            height = -dy + sup.height
        glyphs = tuple(g for p in parts for g in p.glyphs)
        return MathBox(width, height, depth, glyphs)
    parts = [base]
    height, depth = base.height, base.depth
    x = base.width + 0.03 * size
    width = base.width
    if sub is not None:
        dy = max(SUB_DROP * size, base.depth + 0.08 * size)
        if sup is not None:
            dy = max(dy, 0.25 * size)
        parts.append(sub.shifted(x, dy))
        depth = max(depth, dy + sub.depth)
        width = max(width, x + sub.width)
    if sup is not None:
        dy = -max(SUP_RISE * size, base.height - 0.30 * size)
        parts.append(sup.shifted(x, dy))
        height = max(height, -dy + sup.height)
        width = max(width, x + sup.width)
    glyphs = tuple(g for p in parts for g in p.glyphs)
    return MathBox(width + 0.04 * size, height, depth, glyphs)


def typeset(source: str, size: float) -> MathBox:
    """Typeset the formula ``source`` (without the ``$`` delimiters) at ``size`` px."""
    return _layout_seq(_Parser(source).parse(), float(size), 0)


def glyph_path(cp: int) -> str:
    """SVG path data of a glyph in font units, y axis pointing up."""
    return _mg.GLYPHS[cp][3]


def glyph_advance(cp: int, size: float) -> float:
    return _mg.GLYPHS[cp][0] * size / EM
