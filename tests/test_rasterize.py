from __future__ import annotations

from pathlib import Path

import pytest

from diagrams_as_code import rasterize

SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"/>'


def test_backend_order_is_stable() -> None:
    assert [name for name, _ in rasterize.BACKENDS] == [
        "resvg-py",
        "cairosvg",
        "inkscape",
        "imagemagick",
    ]


def test_first_available_backend_wins(tmp_path: Path, monkeypatch) -> None:
    calls: list[str] = []

    def missing(svg: str, path: Path):
        calls.append("missing")
        return None

    def works(svg: str, path: Path):
        calls.append("works")
        path.write_bytes(b"PNG")
        return b"PNG"

    monkeypatch.setattr(rasterize, "BACKENDS", (("a", missing), ("b", works), ("c", missing)))
    assert rasterize.svg_to_png(SVG, tmp_path / "x.png") == b"PNG"
    assert calls == ["missing", "works"]


def test_no_backend_raises_with_install_hint(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(rasterize, "BACKENDS", (("a", lambda s, p: None),))
    with pytest.raises(RuntimeError, match="uv add --dev resvg-py"):
        rasterize.svg_to_png(SVG, tmp_path / "x.png")
