#!/usr/bin/env python3
"""Golden images: a stored picture of every technical figure, compared on each test run.

    uv run python tools/golden_images.py            # compare, print a table
    uv run python tools/golden_images.py --check    # the same, exit 1 on a difference
    uv run python tools/golden_images.py --update   # store the current pictures

A change to the engine that moves a line or a label shows up here as a changed
picture, which a reviewer can look at in the pull request. After a deliberate
visual change, look at the new pictures, then run ``--update`` and commit them.

Pictures are rendered with ``resvg-py`` (a development dependency) at a fixed
width, using only the fonts in ``tests/fixtures/fonts``, so they come out the
same on every machine. The comparison allows for anti-aliasing noise: a pixel
counts as changed when a channel differs by more than ``CHANNEL_TOLERANCE``,
and a picture as changed when more than ``PIXEL_TOLERANCE`` of its pixels do.
"""
from __future__ import annotations

import argparse
import importlib.util
import struct
import sys
import warnings
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

GOLDEN_DIR = REPO / "tests" / "golden"
FONT_DIR = REPO / "tests" / "fixtures" / "fonts"
#: Example folders whose figures have a golden image.
FOLDERS = ("technical",)

WIDTH = 800
CHANNEL_TOLERANCE = 48
PIXEL_TOLERANCE = 0.0005

_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def scripts() -> list[Path]:
    return sorted(p for folder in FOLDERS for p in (REPO / "examples" / folder).glob("*.py"))


def golden_path(script: Path) -> Path:
    return GOLDEN_DIR / script.parent.name / f"{script.stem}.png"


def render(script: Path) -> bytes:
    """The picture of ``script``'s diagram, as PNG bytes."""
    import resvg_py  # type: ignore

    spec = importlib.util.spec_from_file_location(f"_golden_{script.stem}", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        svg = module.diagram().render_svg()
    return bytes(
        resvg_py.svg_to_bytes(
            svg_string=svg,
            width=WIDTH,
            background="#ffffff",
            skip_system_fonts=True,
            font_files=sorted(str(p) for p in FONT_DIR.glob("*.ttf")),
            font_family="Arimo",
            sans_serif_family="Arimo",
            serif_family="Arimo",
        )
    )


def decode_png(data: bytes) -> tuple[int, int, int, bytes]:
    """``(width, height, channels, pixels)`` of an 8-bit, non-interlaced PNG."""
    if data[:8] != _SIGNATURE:
        raise ValueError("not a PNG file")
    pos, idat = 8, bytearray()
    width = height = channels = 0
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos : pos + 8])
        body = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or interlace or colour not in (0, 2, 4, 6):
                raise ValueError("only 8-bit, non-interlaced, non-palette PNGs are supported")
            channels = {0: 1, 2: 3, 4: 2, 6: 4}[colour]
        elif kind == b"IDAT":
            idat += body
        elif kind == b"IEND":
            break
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    out = bytearray(height * stride)
    previous = bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        kind, row = raw[start], bytearray(raw[start + 1 : start + 1 + stride])
        if kind == 1:
            for i in range(channels, stride):
                row[i] = (row[i] + row[i - channels]) & 255
        elif kind == 2:
            for i in range(stride):
                row[i] = (row[i] + previous[i]) & 255
        elif kind == 3:
            for i in range(stride):
                left = row[i - channels] if i >= channels else 0
                row[i] = (row[i] + ((left + previous[i]) >> 1)) & 255
        elif kind == 4:
            for i in range(stride):
                a = row[i - channels] if i >= channels else 0
                b = previous[i]
                c = previous[i - channels] if i >= channels else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                row[i] = (row[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        elif kind != 0:
            raise ValueError(f"unknown PNG filter {kind}")
        out[y * stride : (y + 1) * stride] = row
        previous = row
    return width, height, channels, bytes(out)


@dataclass(frozen=True)
class Comparison:
    """How a rendered picture differs from its golden image."""

    same: bool
    reason: str
    changed: float = 0.0  # share of pixels that differ

    def __str__(self) -> str:
        return self.reason


def compare(actual: bytes, golden: bytes) -> Comparison:
    """Compare two PNGs, allowing for anti-aliasing noise."""
    if actual == golden:
        return Comparison(True, "identical")
    aw, ah, ac, a = decode_png(actual)
    gw, gh, gc, g = decode_png(golden)
    if (aw, ah, ac) != (gw, gh, gc):
        return Comparison(False, f"size changed: {gw} x {gh} -> {aw} x {ah}", 1.0)
    if a == g:
        return Comparison(True, "identical pixels")
    stride = aw * ac
    differing = 0
    for y in range(ah):
        ra, rg = a[y * stride : (y + 1) * stride], g[y * stride : (y + 1) * stride]
        if ra == rg:
            continue
        far = [i // ac for i, (p, q) in enumerate(zip(ra, rg)) if abs(p - q) > CHANNEL_TOLERANCE]
        differing += len(set(far))
    share = differing / float(aw * ah)
    if share > PIXEL_TOLERANCE:
        return Comparison(False, f"{differing} pixels differ ({share:.2%} of the picture)", share)
    return Comparison(True, f"within tolerance ({differing} pixels differ)", share)


def check(script: Path, actual: Optional[bytes] = None) -> Comparison:
    """Compare ``script``'s picture with its golden image."""
    golden = golden_path(script)
    if not golden.exists():
        return Comparison(False, "no golden image; run tools/golden_images.py --update", 1.0)
    return compare(actual if actual is not None else render(script), golden.read_bytes())


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if any picture changed")
    parser.add_argument("--update", action="store_true", help="store the current pictures as golden")
    args = parser.parse_args(argv)

    failed = 0
    for script in scripts():
        actual = render(script)
        golden = golden_path(script)
        name = str(golden.relative_to(REPO))
        if args.update:
            if golden.exists() and compare(actual, golden.read_bytes()).same:
                print(f"unchanged  {name}")
                continue
            golden.parent.mkdir(parents=True, exist_ok=True)
            golden.write_bytes(actual)
            print(f"written    {name}")
            continue
        result = check(script, actual)
        print(f"{'ok' if result.same else 'CHANGED':10s} {name}: {result}")
        failed += not result.same
    if not args.update:
        # A golden image whose script is gone would otherwise sit there for ever.
        wanted = {golden_path(s) for s in scripts()}
        for stray in sorted(set(GOLDEN_DIR.glob("*/*.png")) - wanted):
            print(f"STRAY      {stray.relative_to(REPO)}: no script renders this")
            failed += 1
    return 1 if (args.check and failed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
