"""IIoT Diagrams as Code framework."""
from diagrams_as_code.bom import BOMGenerator
from diagrams_as_code.connections import Edge, Port, Routing
from diagrams_as_code.constraints import ConstraintSolver
from diagrams_as_code.diagram import Diagram
from diagrams_as_code.elements import Element, Shape
from diagrams_as_code.geometry import Anchor, Point, Rect, Size, UnitBasis
from diagrams_as_code.groups import Group
from diagrams_as_code.renderer_svg import SVGRenderer
from diagrams_as_code.router import OrthogonalRouter
from diagrams_as_code.shapes import ShapeLibrary, ShapeRenderer
from diagrams_as_code.theme import (
    BLUEPRINT,
    CRIMSON,
    CYBER_SLATE,
    DRACULA,
    EMERALD,
    HIGH_CONTRAST,
    IIOT_DARK_GOLD,
    IIOT_LIGHT,
    MONOCHROME,
    NORD,
    PASTEL_LIGHT,
    SOLARIZED_LIGHT,
    SYNTHWAVE,
    THEMES,
    Theme,
    create_theme,
    get_dark_themes,
    get_light_themes,
    get_theme,
    list_themes,
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
    "DRACULA",
    "Diagram",
    "EMERALD",
    "Edge",
    "Element",
    "Group",
    "HIGH_CONTRAST",
    "IIOT_DARK_GOLD",
    "IIOT_LIGHT",
    "MONOCHROME",
    "NORD",
    "OrthogonalRouter",
    "PASTEL_LIGHT",
    "Point",
    "Port",
    "Rect",
    "Routing",
    "SOLARIZED_LIGHT",
    "SVGRenderer",
    "SYNTHWAVE",
    "Shape",
    "ShapeLibrary",
    "ShapeRenderer",
    "Size",
    "THEMES",
    "Theme",
    "UnitBasis",
    "create_theme",
    "get_dark_themes",
    "get_light_themes",
    "get_theme",
    "list_themes",
    "register_theme",
    "reset_themes",
]

