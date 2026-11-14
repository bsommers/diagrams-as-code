"""Rich text: parse label markup, lay it out, and emit SVG.

Markup
    ``**bold**``, ``*italic*``, ``$math$`` (see ``text.math``), and ``\\n`` or a
    real newline for a line break. A backslash escapes ``*`` and ``$``.

Ordinary text stays SVG text, measured from bundled metrics. Math is drawn as
glyph outlines, so it looks the same in every viewer.
"""
from __future__ import annotations

import html
from dataclasses import dataclass, replace
from typing import Optional, Sequence, Union

from diagrams_as_code.text import math as _math
from diagrams_as_code.text import metrics as _metrics

SANS_STACK = "Helvetica, Arial, 'Liberation Sans', Arimo, sans-serif"


@dataclass(frozen=True)
class TextStyle:
    """How a block of text is set."""

    size: float = 13.0
    bold: bool = False
    italic: bool = False
    line_height: float = 1.25  # multiple of size
    weight: Optional[int] = None  # explicit CSS weight; wins over ``bold`` when drawing
    small_caps: bool = False

    def scaled(self, size: float) -> TextStyle:
        return replace(self, size=float(size))


@dataclass(frozen=True)
class TextRun:
    text: str
    width: float
    size: float
    bold: bool = False
    italic: bool = False


@dataclass(frozen=True)
class MathRun:
    box: _math.MathBox

    @property
    def width(self) -> float:
        return self.box.width


Run = Union[TextRun, MathRun]


@dataclass(frozen=True)
class Line:
    runs: tuple[Run, ...]
    width: float
    ascent: float  # tallest ink above the baseline
    depth: float  # deepest math below the baseline (text descenders excluded)
    height: float  # advance to the next line


@dataclass(frozen=True)
class TextBlock:
    """Laid-out text: lines of runs, with the block's overall size."""

    lines: tuple[Line, ...]
    width: float
    height: float
    style: TextStyle

    @property
    def is_plain(self) -> bool:
        """True when every line is a single unstyled text run."""
        return all(
            len(ln.runs) == 1
            and isinstance(ln.runs[0], TextRun)
            and ln.runs[0].bold == self.style.bold
            and ln.runs[0].italic == self.style.italic
            for ln in self.lines
        )

    def baselines(self, top: float) -> list[float]:
        """Baseline y of each line for a block whose top edge is at ``top``.

        Each line's text is centred in its line box by cap height, which is how
        the eye judges vertical centring of Latin text.
        """
        out: list[float] = []
        y = top
        for ln in self.lines:
            cap = _metrics.CAP_HEIGHT * self.style.size
            base = y + (ln.height + cap) / 2.0
            # Tall math must stay inside its line box: nudge only as far as needed.
            base = min(base, y + ln.height - ln.depth)
            base = max(base, y + ln.ascent)
            out.append(base)
            y += ln.height
        return out

    def to_svg(
        self,
        x: float,
        y: float,
        *,
        anchor: str = "middle",
        valign: str = "middle",
        fill: str = "#000000",
        font_family: str = SANS_STACK,
        precise: bool = False,
        indent: str = "",
    ) -> str:
        """SVG for this block.

        ``x`` is the left edge, centre or right edge according to ``anchor``
        (start/middle/end); ``y`` is the top, middle or bottom according to
        ``valign`` (top/middle/bottom). With ``precise`` every text run carries
        ``textLength`` so its width matches the layout in any font.
        """
        top = y if valign == "top" else (y - self.height if valign == "bottom" else y - self.height / 2.0)
        family = html.escape(font_family, quote=False).replace('"', "&quot;")
        out: list[str] = []
        if self.is_plain and not precise and len(self.lines) > 1:
            # Plain wrapped text: one <text> with a <tspan> per line.
            bases = self.baselines(top)
            attrs = [f'text-anchor="{anchor}"', f'fill="{fill}"', f'font-family="{family}"',
                     f'font-size="{_n(self.style.size)}"']
            weight = self.style.weight or (700 if self.style.bold else None)
            if weight:
                attrs.append(f'font-weight="{weight}"')
            if self.style.italic:
                attrs.append('font-style="italic"')
            spans = " ".join(
                f'<tspan x="{_n(x)}" dy="{_n(0 if i == 0 else bases[i] - bases[i - 1])}">'
                f"{html.escape(ln.runs[0].text)}</tspan>"  # type: ignore[union-attr]
                for i, ln in enumerate(self.lines)
            )
            return f'{indent}<text x="{_n(x)}" y="{_n(bases[0])}" {" ".join(attrs)}>{spans}</text>'
        for ln, base in zip(self.lines, self.baselines(top)):
            if anchor == "middle":
                cx = x - ln.width / 2.0
            elif anchor == "end":
                cx = x - ln.width
            else:
                cx = x
            single = len(ln.runs) == 1 and isinstance(ln.runs[0], TextRun)
            for run in ln.runs:
                if isinstance(run, MathRun):
                    out.append(_math_svg(run.box, cx, base, fill, indent))
                    cx += run.width
                    continue
                if not run.text:
                    continue
                attrs = [f'fill="{fill}"', f'font-family="{family}"', f'font-size="{_n(run.size)}"']
                weight = self.style.weight if (self.style.weight and run.bold == self.style.bold) else (700 if run.bold else None)
                if weight:
                    attrs.append(f'font-weight="{weight}"')
                if run.italic:
                    attrs.append('font-style="italic"')
                if single and not precise:
                    # Let the viewer centre the run itself: exact even if its font differs.
                    ax = {"middle": x, "end": x, "start": x}[anchor]
                    attrs.append(f'text-anchor="{anchor}"')
                    out.append(f'{indent}<text x="{_n(ax)}" y="{_n(base)}" {" ".join(attrs)}>{html.escape(run.text)}</text>')
                else:
                    stripped = run.text
                    attrs.append(f'textLength="{_n(run.width)}" lengthAdjust="spacingAndGlyphs"')
                    out.append(
                        f'{indent}<text x="{_n(cx)}" y="{_n(base)}" xml:space="preserve" {" ".join(attrs)}>'
                        f"{html.escape(stripped)}</text>"
                    )
                cx += run.width
        return "\n".join(out)


def _n(v: float) -> str:
    """Compact fixed-precision number."""
    r = round(float(v), 2)
    return str(int(r)) if r == int(r) else f"{r:.2f}".rstrip("0")


def _math_svg(box: _math.MathBox, x: float, baseline: float, fill: str, indent: str = "") -> str:
    parts = []
    for g in box.glyphs:
        d = _math.glyph_path(g.cp)
        if not d:
            continue
        s = g.size / _math.EM
        parts.append(
            f'{indent}<path d="{d}" transform="translate({_n(x + g.x)} {_n(baseline + g.y)}) '
            f'scale({s:.5f} {-s:.5f})" fill="{fill}"/>'
        )
    return "\n".join(parts)


# --- parsing -----------------------------------------------------------------

@dataclass(frozen=True)
class _Span:
    kind: str  # text | math
    text: str
    bold: bool = False
    italic: bool = False


def _find_math_end(s: str, start: int) -> int:
    """Index of the ``$`` closing the math opened at ``start`` or -1."""
    if start + 1 >= len(s) or s[start + 1].isspace():
        return -1
    j = start + 1
    while j < len(s):
        if s[j] == "\\":
            j += 2
            continue
        if s[j] == "\n":
            return -1
        if s[j] == "$":
            return j if not s[j - 1].isspace() else -1
        j += 1
    return -1


def parse_markup(source: str) -> list[list[_Span]]:
    """Split ``source`` into lines of styled spans."""
    lines: list[list[_Span]] = [[]]
    buf: list[str] = []
    bold = italic = False

    def flush() -> None:
        if buf:
            lines[-1].append(_Span("text", "".join(buf), bold, italic))
            buf.clear()

    s = source
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] in "*$\\":
            buf.append(s[i + 1])
            i += 2
        elif ch == "\n" or s.startswith("\\n", i):
            # A typed backslash-n breaks the line too, but only out here: inside
            # math it starts a command (\nabla, \neq, \nu).
            i += 0 if ch == "\n" else 1
            flush()
            lines.append([])
            i += 1
        elif ch == "$":
            end = _find_math_end(s, i)
            if end < 0:
                buf.append(ch)
                i += 1
            else:
                flush()
                lines[-1].append(_Span("math", s[i + 1 : end]))
                i = end + 1
        elif s.startswith("**", i) and _toggles(s, i, 2, bold):
            flush()
            bold = not bold
            i += 2
        elif ch == "*" and _toggles(s, i, 1, italic):
            flush()
            italic = not italic
            i += 1
        else:
            buf.append(ch)
            i += 1
    flush()
    return lines


def _toggles(s: str, i: int, n: int, is_open: bool) -> bool:
    """Whether the marker at ``i`` opens or closes emphasis (rather than being literal)."""
    marker = s[i : i + n]
    if is_open:
        return i > 0 and not s[i - 1].isspace()
    after = s[i + n : i + n + 1]
    if not after or after.isspace() or after == "*":
        return False
    close = s.find(marker, i + n)
    while close != -1:
        if not s[close - 1].isspace() and "\n" not in s[i:close]:
            return True
        close = s.find(marker, close + 1)
    return False


def has_markup(source: str) -> bool:
    """True if ``source`` contains anything beyond a single plain line."""
    if not source:
        return False
    lines = parse_markup(source)
    return len(lines) > 1 or any(sp.kind == "math" or sp.bold or sp.italic for ln in lines for sp in ln)


# --- layout ------------------------------------------------------------------

def _measure_span(span: _Span, style: TextStyle) -> list[Run]:
    if span.kind == "math":
        return [MathRun(_math.typeset(span.text, style.size))]
    bold = style.bold or span.bold
    italic = style.italic != span.italic if span.italic else style.italic
    text = span.text.upper() if style.small_caps else span.text
    return [TextRun(text, _metrics.text_width(text, style.size, bold), style.size, bold, italic)]


def _split_words(runs: Sequence[Run]) -> list[Run]:
    """Break text runs at spaces so a line can wrap between words."""
    out: list[Run] = []
    for run in runs:
        if isinstance(run, MathRun):
            out.append(run)
            continue
        word = ""
        for ch in run.text:
            if ch == " ":
                if word:
                    out.append(replace(run, text=word, width=_metrics.text_width(word, run.size, run.bold)))
                    word = ""
                out.append(replace(run, text=" ", width=_metrics.text_width(" ", run.size, run.bold)))
            else:
                word += ch
        if word:
            out.append(replace(run, text=word, width=_metrics.text_width(word, run.size, run.bold)))
    return out


def _merge(runs: Sequence[Run]) -> tuple[Run, ...]:
    """Join adjacent text runs that share a style."""
    out: list[Run] = []
    for run in runs:
        prev = out[-1] if out else None
        if (
            isinstance(run, TextRun)
            and isinstance(prev, TextRun)
            and (prev.bold, prev.italic, prev.size) == (run.bold, run.italic, run.size)
        ):
            text = prev.text + run.text
            out[-1] = replace(prev, text=text, width=_metrics.text_width(text, run.size, run.bold))
        else:
            out.append(run)
    return tuple(out)


def _strip(runs: list[Run]) -> list[Run]:
    while runs and isinstance(runs[0], TextRun) and runs[0].text == " ":
        runs.pop(0)
    while runs and isinstance(runs[-1], TextRun) and runs[-1].text == " ":
        runs.pop()
    return runs


def _make_line(runs: Sequence[Run], style: TextStyle) -> Line:
    merged = _merge(runs)
    width = sum(r.width for r in merged)
    ascent = _metrics.CAP_HEIGHT * style.size
    depth = 0.0
    for r in merged:
        if isinstance(r, MathRun):
            ascent, depth = max(ascent, r.box.height), max(depth, r.box.depth)
    natural = style.line_height * style.size
    # Tall math (limits, stacked scripts) opens the line up instead of colliding.
    height = max(natural, ascent + depth + 0.2 * style.size)
    return Line(merged, width, ascent, depth, height)


def _wrap(words: Sequence[Run], limit: float) -> list[list[Run]]:
    """Greedy word wrap: each line takes as many words as fit in ``limit``."""
    lines: list[list[Run]] = []
    current: list[Run] = []
    width = 0.0
    for word in words:
        is_space = isinstance(word, TextRun) and word.text == " "
        if current and not is_space and width + word.width > limit:
            lines.append(_strip(current))
            current, width = [], 0.0
        if is_space and not current:
            continue
        current.append(word)
        width += word.width
    if _strip(current):
        lines.append(current)
    return lines


def _wrap_balanced(runs: Sequence[Run], max_width: float) -> list[list[Run]]:
    """Wrap into as few lines as ``max_width`` allows, then even the lines out.

    Greedy wrapping alone leaves a short last line ("Hardware Security" / "Key").
    Narrowing the limit as far as the line count allows gives lines of similar
    length without ever exceeding ``max_width``.
    """
    words = _split_words(runs)
    lines = _wrap(words, max_width)
    if len(lines) <= 1:
        return lines
    target = len(lines)
    lo = sum(r.width for r in runs) / target
    hi = max_width
    for _ in range(12):
        mid = (lo + hi) / 2.0
        if len(_wrap(words, mid)) <= target:
            hi = mid
        else:
            lo = mid
    return _wrap(words, hi)


def layout(source: str, style: Optional[TextStyle] = None, max_width: Optional[float] = None) -> TextBlock:
    """Lay out ``source`` (plain text or markup), wrapping at ``max_width`` if given."""
    style = style or TextStyle()
    lines: list[Line] = []
    for spans in parse_markup(source or ""):
        runs: list[Run] = [r for sp in spans for r in _measure_span(sp, style)]
        if max_width is None or sum(r.width for r in runs) <= max_width:
            lines.append(_make_line(runs, style))
        else:
            lines.extend(_make_line(ln, style) for ln in _wrap_balanced(runs, max_width))
    if not lines:
        lines = [_make_line([], style)]
    return TextBlock(
        tuple(lines), max(ln.width for ln in lines), sum(ln.height for ln in lines), style
    )


def measure(source: str, style: Optional[TextStyle] = None, max_width: Optional[float] = None) -> tuple[float, float]:
    """(width, height) of ``source`` once laid out."""
    block = layout(source, style, max_width)
    return (block.width, block.height)
