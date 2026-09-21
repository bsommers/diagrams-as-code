"""Keep the icon provenance statement honest.

Issue #1: ``docs/sources.md`` credited the bundled icons to six third-party
design systems they are not derived from, and named two licenses that do not
exist. The glyphs are original geometry emitted by ``ShapeLibrary``. These
tests fail if an attribution claim comes back without the license text that
claim would oblige the project to ship.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES = REPO_ROOT / "docs" / "sources.md"
ICONS_README = REPO_ROOT / "icons" / "README.md"
LICENSES_DIR = REPO_ROOT / "icons" / "licenses"

#: Licenses invented by an earlier revision of docs/sources.md. None of these
#: is a real license; Cisco's and AWS's icon programs are conditional
#: brand-asset terms. They must never reappear as a license claim.
FABRICATED_LICENSES = [
    "Public Domain / Open Stencil Use",
    "Permissive Architectural Diagramming Use",
    "Open Architectural Diagramming Use",
]

#: Third-party icon sets whose names may legitimately appear as a *convention*
#: reference. Naming one on the same line as a license is an attribution
#: claim, and an attribution claim has to ship the upstream license text.
UPSTREAM_ICON_SETS = [
    "Lucide",
    "Feather",
    "Tabler",
    "CNCF",
    "Cisco",
    "AWS Architecture Icons",
]

LICENSE_TOKEN = re.compile(
    r"\b(ISC|MIT|Apache-2\.0|CC-BY-[\d.]+|GPL-[\d.]+|LGPL-[\d.]+|BSD-[\d-]+\w*)\b"
)


@pytest.fixture(scope="module")
def sources_text() -> str:
    return SOURCES.read_text(encoding="utf-8")


def _icon_section(text: str) -> str:
    """Section 1 only: the dependency tables legitimately name licenses."""
    start = text.index("## 1.")
    end = text.index("## 2.")
    return text[start:end]


@pytest.mark.parametrize("phrase", FABRICATED_LICENSES)
def test_no_fabricated_license_names(phrase: str) -> None:
    """These name no real license and must not be asserted anywhere.

    Quoting one inside a blockquote is allowed: that is how the retraction in
    ``docs/sources.md`` names what it retracts. Stating one on an ordinary
    line is an assertion, and fails.
    """
    offenders = []
    for path in REPO_ROOT.rglob("*.md"):
        if {".venv", ".issues", ".claude"} & set(path.parts):
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if phrase in line and not line.lstrip().startswith(">"):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}")
    assert not offenders, f"invented license {phrase!r} asserted at: {offenders}"


def test_attribution_claims_ship_their_license_text(sources_text: str) -> None:
    """Acceptance criterion: a claimed license must exist under icons/licenses/.

    Naming an upstream icon set next to a license is a derivation claim. ISC
    and MIT both require retaining the upstream copyright notice, so such a
    claim obliges this repo to ship that notice. If the icons ever do adapt an
    upstream glyph, add the license file and this test goes quiet.
    """
    claims = [
        line.strip()
        for line in _icon_section(sources_text).splitlines()
        if any(name in line for name in UPSTREAM_ICON_SETS)
        and LICENSE_TOKEN.search(line)
        # The retraction note names the old sources; it asserts nothing.
        and not line.lstrip().startswith(">")
    ]
    missing = [
        claim
        for claim in claims
        if not LICENSES_DIR.is_dir() or not any(LICENSES_DIR.iterdir())
    ]
    assert not missing, (
        "docs/sources.md section 1 attributes icons to a third party under a "
        f"named license, but {LICENSES_DIR.relative_to(REPO_ROOT)} ships no "
        f"license text for it:\n  " + "\n  ".join(missing)
    )


def test_sources_and_icon_readme_agree_on_authorship(sources_text: str) -> None:
    """Acceptance criterion: the two documents must not contradict."""
    claim = "original geometry written for this project"
    assert claim in sources_text, f"docs/sources.md no longer states: {claim!r}"
    assert claim in ICONS_README.read_text(encoding="utf-8"), (
        f"icons/README.md no longer states: {claim!r}. It is generated — fix "
        "render_readme() in tools/generate_icons.py and regenerate."
    )


def test_no_vendor_artwork_is_bundled() -> None:
    """The aliases are names, not logos; nothing here embeds a vendor mark."""
    trademarked = ("grafana", "kafka", "docker", "kubernetes")
    for path in (REPO_ROOT / "icons").rglob("*.svg"):
        text = path.read_text(encoding="utf-8").lower()
        for mark in trademarked:
            assert f"{mark} logo" not in text and "<image" not in text, (
                f"{path.relative_to(REPO_ROOT)} appears to embed vendor artwork"
            )
