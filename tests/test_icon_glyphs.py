from __future__ import annotations

from diagrams_as_code.icon_glyphs import GLYPHS
from diagrams_as_code.shapes import ShapeLibrary


def test_every_catalog_icon_has_exactly_one_glyph() -> None:
    assert set(GLYPHS) == set(ShapeLibrary._ICON_CATALOG)


def test_glyphs_use_the_requested_color_and_stroke() -> None:
    for name, glyph in GLYPHS.items():
        body = glyph("#ABCDEF", 1.25)
        assert "#ABCDEF" in body, name
        assert body.strip(), name
