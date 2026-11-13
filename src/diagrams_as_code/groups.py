from __future__ import annotations

from typing import Any, Literal, Optional, Sequence, Union
from diagrams_as_code.elements import (
    AbsoluteConstraint,
    AlignConstraint,
    Element,
    RelativeConstraint,
)
from diagrams_as_code.geometry import Anchor, Rect
from diagrams_as_code.style import Style

_LAYOUT_ENGINES: dict[str, type] = {}


def register_group_layout(name: str, engine_cls: type) -> None:
    """Register a layout engine class by mode name."""
    _LAYOUT_ENGINES[name] = engine_cls


def get_group_layout_engine(name: str, **kwargs: Any) -> Any:
    """Retrieve and instantiate a registered layout engine."""
    if name not in _LAYOUT_ENGINES:
        import importlib

        try:
            importlib.import_module("diagrams_as_code.layout.flow")
        except ImportError:
            pass
    engine_cls = _LAYOUT_ENGINES.get(name)
    if engine_cls is None:
        raise ValueError(f"Unknown group layout mode: {name!r}")
    return engine_cls(**kwargs)


class Group(Element):
    """Hierarchical container element with auto-bounding and flow placement."""

    def __init__(
        self,
        id: str,
        label: str,
        padding: float = 25.0,
        header_height: float = 35.0,
        metadata: Optional[dict[str, Any]] = None,
        style: Optional[Style] = None,
        child_style: Optional[Style] = None,
    ) -> None:
        super().__init__(id, label, width=120.0, height=60.0, metadata=metadata, style=style)
        #: Style given to every node inside this group, over the theme.
        self.child_style: Optional[Style] = child_style
        self.children: list[Element] = []
        self.padding = float(padding)
        self.header_height = float(header_height)
        self.is_auto_sized = True
        self.layout_mode: Optional[str] = None
        self.layout_margin: float = 20.0
        self.layout_align: str = "left"
        self.grid_columns: int = 2
        self.grid_margin_x: float = 20.0
        self.grid_margin_y: float = 20.0
        self._flow_engine: Optional[Any] = None

    def add(self, *elements: Union[Element, Sequence[Element]]) -> Group:
        """Add child elements to this group."""
        for item in elements:
            if isinstance(item, (list, tuple)):
                for el in item:
                    self._add_child(el)
            elif isinstance(item, Element):
                self._add_child(item)
            else:
                raise TypeError(
                    f"Expected Element or sequence of Elements, got {type(item).__name__}"
                )
        if self.layout_mode is not None:
            self._apply_layout()
        return self

    def _add_child(self, el: Element) -> None:
        if not isinstance(el, Element):
            raise TypeError(f"Expected Element, got {type(el).__name__}")
        if el is self:
            raise ValueError(f"Cannot add group '{self.id}' to itself")
        curr = self.parent
        while curr is not None:
            if curr is el:
                raise ValueError(
                    f"Cyclic group hierarchy detected: '{el.id}' is an ancestor of '{self.id}'"
                )
            curr = curr.parent

        if (
            el.parent is not None
            and el.parent is not self
            and isinstance(el.parent, Group)
        ):
            if el in el.parent.children:
                el.parent.children.remove(el)

        el.parent = self
        if el not in self.children:
            self.children.append(el)

    def calculate_bounds(self) -> Rect:
        """Calculate and update bounding box enclosing all children with padding and header room."""
        if not self.is_auto_sized or not self.children:
            return self.bounds

        union_rect = self.children[0].bounds
        for child in self.children[1:]:
            union_rect = union_rect.union(child.bounds)

        b = Rect(
            x=union_rect.x - self.padding,
            y=union_rect.y - self.padding - self.header_height,
            width=union_rect.width + (self.padding * 2.0),
            height=union_rect.height + (self.padding * 2.0) + self.header_height,
        )
        self.bounds = b
        self.width = b.width
        self.height = b.height
        return b

    def auto_bounds(self) -> Rect:
        """Alias for calculate_bounds."""
        return self.calculate_bounds()

    def translate(self, dx: float, dy: float) -> None:
        """Translate this group and all its children by delta (dx, dy)."""
        super().translate(dx, dy)
        for child in self.children:
            child.translate(dx, dy)

    def at(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> Group:
        """Position group absolutely with an anchor point."""
        self.constraints.append(
            AbsoluteConstraint(x=float(x), y=float(y), anchor=anchor)
        )
        if isinstance(anchor, str):
            try:
                anchor_enum = Anchor(anchor)
            except ValueError:
                anchor_enum = Anchor(anchor.lower())
        else:
            anchor_enum = anchor
        offset = Rect(0.0, 0.0, self.bounds.width, self.bounds.height).get_anchor(
            anchor_enum
        )
        target_x = float(x) - offset.x
        target_y = float(y) - offset.y
        dx = target_x - self.bounds.x
        dy = target_y - self.bounds.y
        self.translate(dx, dy)
        return self

    def move_to(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> Group:
        """Clear existing constraints and relocate group absolutely."""
        self.clear_constraints()
        return self.at(x, y, anchor=anchor)

    def right_of(
        self,
        other: Element,
        margin: float = 50.0,
        align: Literal["center", "top", "bottom"] = "top",
    ) -> Group:
        """Position group to the right of another element."""
        self.constraints.append(
            RelativeConstraint(
                target=other,
                direction="right",
                margin=float(margin),
                align=align,
            )
        )
        return self

    def left_of(
        self,
        other: Element,
        margin: float = 50.0,
        align: Literal["center", "top", "bottom"] = "top",
    ) -> Group:
        """Position group to the left of another element."""
        self.constraints.append(
            RelativeConstraint(
                target=other,
                direction="left",
                margin=float(margin),
                align=align,
            )
        )
        return self

    def below(
        self,
        other: Element,
        margin: float = 50.0,
        align: Literal["center", "left", "right"] = "left",
    ) -> Group:
        """Position group below another element."""
        self.constraints.append(
            RelativeConstraint(
                target=other,
                direction="below",
                margin=float(margin),
                align=align,
            )
        )
        return self

    def above(
        self,
        other: Element,
        margin: float = 50.0,
        align: Literal["center", "left", "right"] = "left",
    ) -> Group:
        """Position group above another element."""
        self.constraints.append(
            RelativeConstraint(
                target=other,
                direction="above",
                margin=float(margin),
                align=align,
            )
        )
        return self

    def align_with(
        self,
        other: Element,
        align: Literal["center", "left", "right", "top", "bottom"] = "center",
        axis: Literal["horizontal", "vertical", "both", "x", "y"] = "horizontal",
    ) -> Group:
        """Align group relative to another element."""
        self.constraints.append(
            AlignConstraint(
                target=other,
                align=align,
                axis=axis,
            )
        )
        return self

    def flow(self, engine: Any = "vertical", **kwargs: Any) -> Group:
        """Apply a flow layout engine or registered preset mode to child elements."""
        if isinstance(engine, str):
            self.layout_mode = engine
            self._flow_engine = get_group_layout_engine(engine, **kwargs)
        else:
            self._flow_engine = engine
            self.layout_mode = getattr(engine, "mode", "custom")
        self._apply_layout()
        return self

    def vertical_flow(
        self,
        margin: float = 20.0,
        align: Literal["center", "left", "right"] = "left",
    ) -> Group:
        """Apply vertical flow layout to child elements."""
        self.layout_mode = "vertical_flow"
        self.layout_margin = float(margin)
        self.layout_align = align
        self._flow_engine = get_group_layout_engine(
            "vertical_flow", margin=self.layout_margin, align=align
        )
        self._apply_layout()
        return self

    def horizontal_flow(
        self,
        margin: float = 20.0,
        align: Literal["center", "top", "bottom"] = "top",
    ) -> Group:
        """Apply horizontal flow layout to child elements."""
        self.layout_mode = "horizontal_flow"
        self.layout_margin = float(margin)
        self.layout_align = align
        self._flow_engine = get_group_layout_engine(
            "horizontal_flow", margin=self.layout_margin, align=align
        )
        self._apply_layout()
        return self

    def grid(
        self,
        columns: int = 2,
        margin_x: float = 20.0,
        margin_y: float = 20.0,
    ) -> Group:
        """Apply grid layout to child elements."""
        self.layout_mode = "grid"
        self.grid_columns = max(1, int(columns))
        self.grid_margin_x = float(margin_x)
        self.grid_margin_y = float(margin_y)
        self._flow_engine = get_group_layout_engine(
            "grid",
            columns=self.grid_columns,
            margin_x=self.grid_margin_x,
            margin_y=self.grid_margin_y,
        )
        self._apply_layout()
        return self

    def _apply_layout(self) -> None:
        """Generate relative placement constraints for children according to layout mode."""
        if not self.children:
            return

        if self._flow_engine is not None:
            self._flow_engine.apply(self)
        elif self.layout_mode is not None:
            if self.layout_mode == "grid":
                self._flow_engine = get_group_layout_engine(
                    "grid",
                    columns=self.grid_columns,
                    margin_x=self.grid_margin_x,
                    margin_y=self.grid_margin_y,
                )
            else:
                self._flow_engine = get_group_layout_engine(
                    self.layout_mode, margin=self.layout_margin, align=self.layout_align
                )
            self._flow_engine.apply(self)
