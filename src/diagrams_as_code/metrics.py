"""Text metrics shared by layout and rendering, so spacing and drawing agree."""
from __future__ import annotations

#: Distance from a shape's bottom edge to the baseline of a label drawn below it.
LABEL_BELOW_OFFSET = 14.0

#: Room layout reserves under a shape whose label is drawn below it
#: (offset plus one line of 10-12px text).
LABEL_BELOW_EXTRA = LABEL_BELOW_OFFSET + 10.0

#: Average glyph advance as a fraction of the font size. A stopgap shared by
#: layout and rendering until real font metrics land (Phase 13).
AVG_CHAR_EM = 0.62


def wrap_text(text: str, max_chars: int = 15) -> list[str]:
    """Break label text into lines of at most ``max_chars`` at word boundaries."""
    words = text.split() if text else []
    lines: list[str] = []
    curr: list[str] = []
    curr_len = 0
    for w in words:
        addition = len(w) + (1 if curr else 0)
        if curr_len + addition <= max_chars:
            curr.append(w)
            curr_len += addition
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
    if curr:
        lines.append(" ".join(curr))
    return lines


def badge_width(label: str, font_size: float = 10.0, padding_x: float = 8.0) -> float:
    """Width of an edge label badge."""
    return max(len(label) * font_size * AVG_CHAR_EM + 2.0 * padding_x, 24.0)


def below_label_budget(width: float) -> int:
    """Characters per line for a label drawn below a shape of ``width``."""
    return max(14, int(max(width, 100.0) / 7.0))


def below_label_extent(label: str, width: float) -> tuple[float, int]:
    """(width, line count) of a label drawn below a shape of ``width``."""
    lines = wrap_text(label, below_label_budget(width))
    if not lines:
        return (0.0, 0)
    font_size = 12.0 if len(lines) == 1 else 11.0
    return (max(len(line) for line in lines) * font_size * AVG_CHAR_EM, len(lines))
