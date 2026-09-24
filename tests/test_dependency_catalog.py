"""Bind ``docs/sources.md`` to the code and the image it claims to describe.

The provenance document answers "what am I redistributing or invoking?". It
fell behind once already: ``render_png`` reaches for four rasterizers and the
container installs a font, and the catalog listed only the first rasterizer.
These tests read the real fallback chain and the real ``Dockerfile`` so a new
backend or a new ``apt`` package cannot be added without cataloging it.
"""

from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES = REPO_ROOT / "docs" / "sources.md"
DOCKERFILE = REPO_ROOT / "Dockerfile"


@pytest.fixture(scope="module")
def sources_text() -> str:
    return SOURCES.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def render_png_source() -> str:
    from diagrams_as_code import rasterize

    return inspect.getsource(rasterize)


#: Every third-party name ``render_png`` can reach for, mapped to the phrase
#: that must appear in the catalog. Adding a backend means adding a row and an
#: entry here; the test below fails until both exist.
BACKEND_CATALOG_PHRASES = {
    "resvg_py": "resvg-py",
    "cairosvg": "CairoSVG",
    "inkscape": "Inkscape",
    "magick": "ImageMagick",
    "convert": "ImageMagick",
}


def _png_backends(source: str) -> set[str]:
    """Third-party modules imported and binaries looked up on ``PATH``."""
    imported = {
        name
        for name in re.findall(r"^\s*import\s+(\w+)", source, re.MULTILINE)
        if name not in sys.stdlib_module_names
    }
    external = set(re.findall(r'shutil\.which\(\s*"([^"]+)"\s*\)', source))
    return imported | external


def _apt_packages(dockerfile: str) -> set[str]:
    """Packages installed by ``apt-get install`` across line continuations."""
    joined = dockerfile.replace("\\\n", " ")
    packages: set[str] = set()
    for line in joined.splitlines():
        if "apt-get install" not in line:
            continue
        tail = line.split("apt-get install", 1)[1]
        tail = tail.split("&&", 1)[0]
        packages.update(
            token
            for token in tail.split()
            if not token.startswith("-") and token not in {"y"}
        )
    return packages


def test_png_backend_chain_is_fully_catalogued(render_png_source, sources_text) -> None:
    """Issue #6: three of the four rasterizers were missing from the catalog."""
    detected = _png_backends(render_png_source)
    assert detected, "no PNG backends detected; the parser is out of date"

    unmapped = sorted(detected - set(BACKEND_CATALOG_PHRASES))
    assert not unmapped, (
        f"render_png() reaches for {unmapped}, which BACKEND_CATALOG_PHRASES "
        "does not know about. Add a row to docs/sources.md and an entry here."
    )

    missing = sorted(
        {
            BACKEND_CATALOG_PHRASES[name]
            for name in detected
            if BACKEND_CATALOG_PHRASES[name] not in sources_text
        }
    )
    assert not missing, f"docs/sources.md does not catalog: {missing}"


def test_copyleft_backends_are_flagged_as_such(sources_text) -> None:
    """CairoSVG is LGPL and Inkscape is GPL; 'permissive' must not cover them."""
    for phrase in ("LGPL-3.0", "GPL-3.0"):
        assert phrase in sources_text, f"{phrase} license not stated"
    assert "not uniformly permissive" in sources_text, (
        "docs/sources.md must not imply every catalogued component is permissive"
    )


def test_docker_base_image_is_catalogued(sources_text) -> None:
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    images = re.findall(r"^FROM\s+(\S+)", dockerfile, re.MULTILINE)
    assert images, "no FROM line found in Dockerfile"
    missing = [image for image in images if image not in sources_text]
    assert not missing, f"docs/sources.md does not catalog base image(s): {missing}"


def test_apt_installed_packages_are_catalogued(sources_text) -> None:
    """The image ships these binaries and font outlines; the doc must say so."""
    packages = _apt_packages(DOCKERFILE.read_text(encoding="utf-8"))
    assert packages, "no apt packages detected; the parser is out of date"
    missing = sorted(pkg for pkg in packages if f"`{pkg}`" not in sources_text)
    assert not missing, (
        f"Dockerfile installs {missing}, which docs/sources.md does not list."
    )
