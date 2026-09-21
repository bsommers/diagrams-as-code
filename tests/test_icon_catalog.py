"""Bind the icon catalog, the generated ``icons/`` tree, and the docs together.

``ShapeLibrary._ICON_CATALOG`` is the single source of truth for icons. These
tests fail if the tree on disk, the manifests, or the counts quoted in the
documentation drift away from it, which is what allowed the tree to fall three
symbols behind the engine before it was generated.
"""

from __future__ import annotations

import csv
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from diagrams_as_code.shapes import ShapeLibrary

REPO_ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = REPO_ROOT / "icons"
GENERATOR = REPO_ROOT / "tools" / "generate_icons.py"

SVG_NS = "http://www.w3.org/2000/svg"


@pytest.fixture(scope="module")
def library() -> ShapeLibrary:
    return ShapeLibrary()


@pytest.fixture(scope="module")
def catalog(library: ShapeLibrary) -> dict[str, tuple[str, str]]:
    return library._ICON_CATALOG


def test_generator_check_passes() -> None:
    """The committed tree matches what the generator would emit right now.

    This is the gate: it fails on a hand-edited icon, a catalog entry added
    without regenerating, and a stale manifest alike.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"icons/ is out of date with ShapeLibrary._ICON_CATALOG.\n"
        f"{result.stdout}{result.stderr}"
    )


def test_every_canonical_icon_has_a_file(catalog, library: ShapeLibrary) -> None:
    """Every name the engine accepts resolves to a file a reader can open."""
    assert set(catalog) == set(library._CANONICAL_ICONS)
    missing = [
        f"{domain}/{name}.svg"
        for name, (domain, _description) in catalog.items()
        if not (ICONS_DIR / domain / f"{name}.svg").is_file()
    ]
    assert not missing, f"canonical icons with no SVG file: {missing}"


def test_no_orphan_svg_files(catalog) -> None:
    """No file in the tree claims to be an icon the engine cannot render."""
    expected = {
        ICONS_DIR / domain / f"{name}.svg"
        for name, (domain, _description) in catalog.items()
    }
    assert set(ICONS_DIR.rglob("*.svg")) == expected


def test_each_icon_lives_in_exactly_one_domain(catalog) -> None:
    """One home per icon: the duplicate plc/sensor files must not come back."""
    stems = [path.stem for path in ICONS_DIR.rglob("*.svg")]
    duplicates = sorted({stem for stem in stems if stems.count(stem) > 1})
    assert not duplicates, f"icons present in more than one domain: {duplicates}"
    assert len(stems) == len(catalog)


@pytest.mark.parametrize("path", sorted(ICONS_DIR.rglob("*.svg")), ids=lambda p: p.name)
def test_icon_file_is_well_formed_svg(path: Path) -> None:
    """Downstream check: every file parses as XML and is a 24x24 SVG root."""
    root = ET.parse(path).getroot()
    assert root.tag == f"{{{SVG_NS}}}svg"
    assert root.get("viewBox") == "0 0 24 24"
    assert len(list(root)) > 0, "icon has no drawable content"


def test_icon_file_matches_the_rendered_glyph(catalog, library: ShapeLibrary) -> None:
    """A file's artwork is the same markup ``render_icon`` puts in a diagram."""
    for name, (domain, _description) in sorted(catalog.items()):
        body = library._render_icon_content(name, "currentColor", 2)
        on_disk = (ICONS_DIR / domain / f"{name}.svg").read_text(encoding="utf-8")
        assert body in on_disk, f"{domain}/{name}.svg is not the engine's glyph"


def test_csv_manifest_matches_catalog(catalog) -> None:
    with (ICONS_DIR / "icons.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["symbol"] for row in rows] == sorted(catalog)
    for row in rows:
        domain, description = catalog[row["symbol"]]
        assert row["domain"] == domain
        assert row["notes"] == description
        assert row["path"] == f"./icons/{domain}/{row['symbol']}.svg"
        assert (REPO_ROOT / row["path"].lstrip("./")).is_file()


def test_yaml_manifest_lists_every_icon(catalog) -> None:
    """Parsed without PyYAML: the engine has no third-party runtime deps."""
    text = (ICONS_DIR / "icons.yaml").read_text(encoding="utf-8")
    symbols = [
        line.split(":", 1)[1].strip()
        for line in text.splitlines()
        if line.startswith("- symbol:")
    ]
    assert sorted(symbols) == sorted(catalog)
    for name, (domain, _description) in catalog.items():
        assert f"  path: ./icons/{domain}/{name}.svg" in text


def test_every_alias_resolves_to_a_canonical_icon(library: ShapeLibrary) -> None:
    """Aliases are part of the public API, so they must not dangle."""
    unresolved = {
        alias: target
        for alias, target in library._ICON_ALIASES.items()
        if target not in library._ICON_CATALOG
    }
    assert not unresolved, f"aliases pointing at unknown icons: {unresolved}"


def test_aliases_are_documented(library: ShapeLibrary) -> None:
    """Issue #12: the vendor-named aliases must be discoverable from the docs."""
    readme = (ICONS_DIR / "README.md").read_text(encoding="utf-8")
    undocumented = [
        alias for alias in library._ICON_ALIASES if f"| `{alias}` |" not in readme
    ]
    assert not undocumented, f"aliases missing from icons/README.md: {undocumented}"


#: Every place a hand-maintained document advertises the size of the icon
#: library, as a format string taking the real total. All of these said 59
#: while the engine exposed 60, in a badge, in prose, and inside two ASCII
#: architecture boxes. ``icons/README.md`` is absent because it is generated,
#: and ``docs/CHANGELOG.md`` because released entries record the count at the
#: time. Rewording a sentence here means updating the phrase here too, which is
#: the point: the count stops being something a writer can quietly get wrong.
DOC_ICON_CLAIMS: dict[str, list[str]] = {
    "README.md": [
        "badge/icons-{n}%20SVG",
        "library of {n} handcrafted 24x24 open-source vector icons",
    ],
    "docs/README.md": ["- {n} Built-in Vector Icons"],
    "docs/sources.md": ["provides {n} handcrafted, resolution-independent vector icons"],
    "docs/purpose.md": ["{n} custom SVG vector icons"],
    "docs/architecture.md": [
        "library of {n} handcrafted 24x24 open-source vector icons",
        "Standalone Vector Icons ({n})",
    ],
    "examples/README.md": ["{n} custom open-source SVG vector icons"],
}


@pytest.mark.parametrize("doc", sorted(DOC_ICON_CLAIMS), ids=str)
def test_hand_written_docs_quote_the_real_icon_total(doc: str, catalog) -> None:
    """Guard the specific drift that shipped: a hard-coded library total."""
    text = (REPO_ROOT / doc).read_text(encoding="utf-8")
    missing = [
        phrase.format(n=len(catalog))
        for phrase in DOC_ICON_CLAIMS[doc]
        if phrase.format(n=len(catalog)) not in text
    ]
    assert not missing, (
        f"{doc} does not state the real icon total ({len(catalog)}).\n"
        f"Expected to find: {missing}\n"
        "Either the count is stale, or the sentence was reworded and "
        "DOC_ICON_CLAIMS needs updating."
    )
