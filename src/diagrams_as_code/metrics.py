"""Text metrics shared by layout and rendering, so spacing and drawing agree."""
from __future__ import annotations

#: Distance from a shape's bottom edge to the baseline of a label drawn below it.
LABEL_BELOW_OFFSET = 14.0

#: Room layout reserves under a shape whose label is drawn below it
#: (offset plus one line of 10-12px text).
LABEL_BELOW_EXTRA = LABEL_BELOW_OFFSET + 10.0
