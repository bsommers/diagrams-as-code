"""Text measurement from bundled advance-width tables."""
from __future__ import annotations

import unicodedata

from diagrams_as_code.text import _sans_metrics as _sans

_UPM = float(_sans.UNITS_PER_EM)

#: Fractions of the font size.
ASCENT = _sans.ASCENT / _UPM
DESCENT = _sans.DESCENT / _UPM
CAP_HEIGHT = _sans.CAP_HEIGHT / _UPM
X_HEIGHT = _sans.X_HEIGHT / _UPM

_FALLBACK = 0.556  # advance of an average lowercase letter
_ITALIC_FACTOR = 1.0  # Arimo italic shares the upright widths


def char_width(ch: str, bold: bool = False) -> float:
    """Advance of one character as a fraction of the font size."""
    table = _sans.BOLD if bold else _sans.REGULAR
    w = table.get(ord(ch))
    if w is not None:
        return w / _UPM
    if unicodedata.combining(ch):
        return 0.0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 1.0
    return _FALLBACK * (1.06 if bold else 1.0)


def text_width(text: str, size: float, bold: bool = False) -> float:
    """Width of ``text`` set in the sans font at ``size`` px."""
    return sum(char_width(ch, bold) for ch in text) * size
