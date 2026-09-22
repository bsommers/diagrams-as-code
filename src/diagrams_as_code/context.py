"""Stack of diagrams whose ``with`` block is currently open.

Elements look up the active diagram here instead of importing ``diagram``,
which sits above them.
"""
from __future__ import annotations

from typing import Any, Optional

_ACTIVE: list[Any] = []


def push(diagram: Any) -> None:
    """Make ``diagram`` the innermost active diagram."""
    _ACTIVE.append(diagram)


def pop(diagram: Any) -> None:
    """Remove ``diagram`` if it is the innermost active diagram."""
    if _ACTIVE and _ACTIVE[-1] is diagram:
        _ACTIVE.pop()


def current() -> Optional[Any]:
    """Return the innermost active diagram, or ``None``."""
    return _ACTIVE[-1] if _ACTIVE else None
