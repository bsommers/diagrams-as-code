"""PNG rasterization backends, tried in order until one is available."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Callable, Optional

Backend = Callable[[str, Path], Optional[bytes]]


def _resvg(svg: str, path: Path) -> Optional[bytes]:
    try:
        import resvg_py  # type: ignore
    except ImportError:
        return None
    png: bytes = resvg_py.svg_to_bytes(svg)
    path.write_bytes(png)
    return png


def _cairosvg(svg: str, path: Path) -> Optional[bytes]:
    try:
        import cairosvg  # type: ignore
    except ImportError:
        return None
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(path))
    return path.read_bytes()


def _run_converter(argv_for: Callable[[Path], list[str]], svg: str, path: Path) -> Optional[bytes]:
    temp_svg = path.with_suffix(".temp.svg")
    try:
        temp_svg.write_text(svg, encoding="utf-8")
        res = subprocess.run(argv_for(temp_svg), capture_output=True)
        if res.returncode == 0 and path.exists():
            return path.read_bytes()
        return None
    finally:
        if temp_svg.exists():
            temp_svg.unlink()


def _inkscape(svg: str, path: Path) -> Optional[bytes]:
    inkscape_bin = shutil.which("inkscape")
    if not inkscape_bin:
        return None
    return _run_converter(lambda src: [inkscape_bin, str(src), "-o", str(path)], svg, path)


def _imagemagick(svg: str, path: Path) -> Optional[bytes]:
    magick_bin = shutil.which("magick") or shutil.which("convert")
    if not magick_bin:
        return None
    return _run_converter(lambda src: [magick_bin, str(src), str(path)], svg, path)


BACKENDS: tuple[tuple[str, Backend], ...] = (
    ("resvg-py", _resvg),
    ("cairosvg", _cairosvg),
    ("inkscape", _inkscape),
    ("imagemagick", _imagemagick),
)


def svg_to_png(svg: str, path: Path) -> bytes:
    """Rasterize ``svg`` to ``path`` with the first available backend."""
    for _name, backend in BACKENDS:
        png = backend(svg, path)
        if png is not None:
            return png
    raise RuntimeError(
        "PNG rendering requires 'resvg-py', 'cairosvg', or system utilities ('inkscape'/'magick'). "
        "Install with: uv add --dev resvg-py"
    )
