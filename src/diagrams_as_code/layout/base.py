"""Data model shared by layout engines, the graph builder and the pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from diagrams_as_code.geometry import Point

#: Key marking constraints the layout pipeline generated ("auto" or "file").
#: They are removed at the start of every pipeline run.
SOURCE_KEY = "_layout_source"


class LayoutWarning(UserWarning):
    """A layout result that is probably not what the author intended."""


@dataclass(frozen=True)
class LayoutNode:
    """One element to place: its size and declaration order."""

    id: str
    width: float
    height: float
    index: int


@dataclass(frozen=True)
class LayoutEdge:
    """A directed connection between two nodes of the same scope."""

    source: str
    target: str
    weight: int = 1


@dataclass(frozen=True)
class LayoutGraph:
    """The nodes and edges of one scope (the canvas or one group)."""

    nodes: tuple[LayoutNode, ...]
    edges: tuple[LayoutEdge, ...]


class LayoutEngine(Protocol):
    """Places every node of a graph; returns top-left corners from (0, 0)."""

    def arrange(self, graph: LayoutGraph) -> dict[str, Point]: ...
