"""IIoT Diagrams as Code framework."""
from iiot_diagrams.bom import BOMGenerator
from iiot_diagrams.connections import Edge, Port, Routing
from iiot_diagrams.constraints import ConstraintSolver
from iiot_diagrams.diagram import Diagram
from iiot_diagrams.elements import Element, Shape
from iiot_diagrams.geometry import Anchor, Point, Rect, Size, UnitBasis
from iiot_diagrams.groups import Group
from iiot_diagrams.renderer_svg import SVGRenderer
from iiot_diagrams.router import OrthogonalRouter
from iiot_diagrams.shapes import ShapeLibrary, ShapeRenderer
from iiot_diagrams.theme import (
    BLUEPRINT,
    CRIMSON,
    CYBER_SLATE,
    EMERALD,
    IIOT_DARK_GOLD,
    IIOT_LIGHT,
    MONOCHROME,
    NORD,
    THEMES,
    Theme,
    get_theme,
    register_theme,
    reset_themes,
)

__version__ = "0.2.0"
__all__ = [
    "Anchor",
    "BLUEPRINT",
    "BOMGenerator",
    "CRIMSON",
    "CYBER_SLATE",
    "ConstraintSolver",
    "Diagram",
    "EMERALD",
    "Edge",
    "Element",
    "Group",
    "IIOT_DARK_GOLD",
    "IIOT_LIGHT",
    "MONOCHROME",
    "NORD",
    "OrthogonalRouter",
    "Point",
    "Port",
    "Rect",
    "Routing",
    "SVGRenderer",
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
