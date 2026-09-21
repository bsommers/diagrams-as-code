"""Guards against duplicated files in the repository tree.

Two documents once shared the path ``docs/architecture.md`` apart from letter
case, and ``RUNNING.md`` and ``docker_compose.yml`` were stale copies of other
tracked files. A root file that mirrors one under ``docs/`` is a symlink, so
the copies cannot drift apart.
"""

from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Byte-identical files that predate this guard. Shrink it; do not grow it.
KNOWN_IDENTICAL: set[frozenset[str]] = {
    frozenset({"legacy/enhanced_iiot_themed_main.py", "legacy/old2_iiot_theme.py"}),
}


def _tracked() -> list[tuple[str, str, str]]:
    """Return ``(mode, blob_sha, path)`` for every tracked file."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-s"],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        pytest.skip(f"not a git checkout: {exc}")
    rows = []
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        mode, sha, _stage = meta.split()
        rows.append((mode, sha, path))
    return rows


def test_no_paths_differ_only_by_case() -> None:
    by_folded: dict[str, list[str]] = defaultdict(list)
    for _mode, _sha, path in _tracked():
        by_folded[path.lower()].append(path)
    clashes = [paths for paths in by_folded.values() if len(paths) > 1]
    assert not clashes, f"paths collide on case-insensitive filesystems: {clashes}"


def test_no_tracked_file_is_a_copy_of_another() -> None:
    by_sha: dict[str, list[str]] = defaultdict(list)
    for mode, sha, path in _tracked():
        # Symlinks are the sanctioned way to expose one file at two paths;
        # empty files (``__init__.py``) and generated output are expected
        # to repeat.
        if mode == "120000" or path.startswith("output/"):
            continue
        if (REPO_ROOT / path).stat().st_size == 0:
            continue
        by_sha[sha].append(path)
    copies = [
        sorted(paths) for paths in by_sha.values()
        if len(paths) > 1 and frozenset(paths) not in KNOWN_IDENTICAL
    ]
    assert not copies, (
        f"identical tracked files: {copies}\n"
        "Delete the copy, or replace it with a symlink to the original."
    )
