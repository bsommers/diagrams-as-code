"""Text metrics shared by layout and rendering, so spacing and drawing agree."""
from __future__ import annotations

#: Distance from a shape's bottom edge to the baseline of a label drawn below it.
LABEL_BELOW_OFFSET = 14.0

#: Room layout reserves under a shape whose label is drawn below it
#: (offset plus one line of 10-12px text).
LABEL_BELOW_EXTRA = LABEL_BELOW_OFFSET + 10.0

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
