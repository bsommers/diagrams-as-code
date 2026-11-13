"""Every technical figure is compared with a stored picture of itself (VIS-01).

A failure here means the picture changed. Look at the new render (written to
the path the failure names), and if the change is intended run
``uv run python tools/golden_images.py --update`` and commit the new images.
"""
from __future__ import annotations

import importlib.util
import struct
import sys
import zlib
from pathlib import Path

import pytest

pytest.importorskip("resvg_py")

REPO = Path(__file__).resolve().parent.parent


def _tool():
    name = "golden_images"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, REPO / "tools" / "golden_images.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


golden = _tool()
SCRIPTS = golden.scripts()


def _png(width: int, height: int, pixel: tuple[int, int, int, int], changed: int = 0, filter_type: int = 0) -> bytes:
    """A flat RGBA picture with the first ``changed`` pixels inverted."""
    rows = bytearray()
    left = changed
    for _ in range(height):
        row = bytearray()
        for _ in range(width):
            row += bytes(255 - v for v in pixel) if left > 0 else bytes(pixel)
            left -= 1
        if filter_type == 1:  # Sub: each byte less the one a pixel to its left
            row = bytearray((row[i] - (row[i - 4] if i >= 4 else 0)) & 255 for i in range(len(row)))
        rows += bytes([filter_type]) + row

    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b"")


def test_decoder_reads_pixels_whatever_the_row_filter():
    plain = golden.decode_png(_png(5, 3, (10, 20, 30, 255), changed=2))
    filtered = golden.decode_png(_png(5, 3, (10, 20, 30, 255), changed=2, filter_type=1))
    assert plain == filtered
    width, height, channels, pixels = plain
    assert (width, height, channels) == (5, 3, 4)
    assert pixels[:4] == bytes((245, 235, 225, 0)) and pixels[8:12] == bytes((10, 20, 30, 255))


def test_identical_pictures_compare_equal_even_when_encoded_differently():
    a, b = _png(40, 40, (200, 200, 200, 255)), _png(40, 40, (200, 200, 200, 255), filter_type=1)
    assert a != b
    assert golden.compare(a, b).same


def test_faint_noise_is_tolerated_but_a_visible_change_is_not():
    base = _png(100, 100, (200, 200, 200, 255))
    faint = _png(100, 100, (210, 190, 205, 255))  # every pixel a little off: anti-aliasing noise
    assert golden.compare(faint, base).same
    few = _png(100, 100, (200, 200, 200, 255), changed=5)  # 0.05% of the picture
    assert golden.compare(few, base).same
    many = _png(100, 100, (200, 200, 200, 255), changed=50)
    result = golden.compare(many, base)
    assert not result.same and "50 pixels differ" in str(result)


def test_a_size_change_is_reported():
    result = golden.compare(_png(10, 12, (0, 0, 0, 255)), _png(10, 10, (0, 0, 0, 255)))
    assert not result.same and "size changed: 10 x 10 -> 10 x 12" in str(result)


def test_every_technical_figure_has_a_golden_image_and_no_strays():
    assert len(SCRIPTS) >= 11
    wanted = {golden.golden_path(s) for s in SCRIPTS}
    assert wanted == set(golden.GOLDEN_DIR.glob("*/*.png"))


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_figure_matches_its_golden_image(script: Path, tmp_path: Path):
    actual = golden.render(script)
    result = golden.check(script, actual)
    if not result.same:
        out = tmp_path / f"{script.stem}.actual.png"
        out.write_bytes(actual)
        pytest.fail(
            f"{script.relative_to(REPO)} no longer matches {golden.golden_path(script).relative_to(REPO)}: "
            f"{result}. New render: {out}. If the change is intended, run "
            "`uv run python tools/golden_images.py --update` and commit the result."
        )
