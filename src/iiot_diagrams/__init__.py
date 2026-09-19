"""IIoT Diagrams as Code framework."""
from iiot_diagrams.connections import Edge, Port, Routing
from iiot_diagrams.constraints import ConstraintSolver
from iiot_diagrams.elements import Element, Shape
from iiot_diagrams.geometry import Anchor, Point, Rect, Size, UnitBasis
from iiot_diagrams.groups import Group
from iiot_diagrams.router import OrthogonalRouter
from iiot_diagrams.shapes import ShapeLibrary, ShapeRenderer
from iiot_diagrams.theme import (
    BLUEPRINT,
    CYBER_SLATE,
    IIOT_DARK_GOLD,
    IIOT_LIGHT,
    THEMES,
    Theme,
    get_theme,
    register_theme,
    reset_themes,
)

__version__ = "0.1.0"
__all__ = [
    "Anchor",
    "BLUEPRINT",
    "CYBER_SLATE",
    "ConstraintSolver",
    "Edge",
    "Element",
    "Group",
    "IIOT_DARK_GOLD",
    "IIOT_LIGHT",
    "OrthogonalRouter",
    "Point",
    "Port",
    "Rect",
    "Routing",
    "Shape",
    "ShapeLibrary",
    "ShapeRenderer",
    "Size",
    "THEMES",
    "Theme",
    "UnitBasis",
    "get_theme",
    "register_theme",
    "reset_themes",
]
