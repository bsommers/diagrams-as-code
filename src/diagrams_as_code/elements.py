from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Literal, Optional, Union
from diagrams_as_code.geometry import Anchor, Rect
from diagrams_as_code import context


class Constraint(MutableMapping):
    """Base class for element positioning constraints with dictionary duck-typing."""

    type: str = ""
    _layout_source: Optional[str] = None
    _auto_layout: bool = False

    def __init__(
        self,
        type: str = "",
        _layout_source: Optional[str] = None,
        _auto_layout: bool = False,
        **kwargs: Any,
    ) -> None:
        self.type = type
        self._layout_source = _layout_source
        self._auto_layout = _auto_layout
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def _source(self) -> Optional[str]:
        return self._layout_source

    @_source.setter
    def _source(self, val: Optional[str]) -> None:
        self._layout_source = val

    def _present_fields(self) -> set[str]:
        res = set()
        if is_dataclass(self):
            for f in fields(self):
                if f.name in ("_layout_source", "_auto_layout"):
                    continue
                val = getattr(self, f.name, None)
                if val is not None:
                    res.add(f.name)
        for k, v in self.__dict__.items():
            if k in ("_layout_source", "_auto_layout"):
                continue
            if v is not None:
                res.add(k)
        if self._layout_source is not None:
            res.add("_layout_source")
            res.add("_source")
        if self._auto_layout:
            res.add("_auto_layout")
        return res

    def __getitem__(self, key: str) -> Any:
        if key not in self._present_fields():
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in ("_source", "_layout_source"):
            self._layout_source = value
        elif key == "_auto_layout":
            self._auto_layout = bool(value)
        else:
            setattr(self, key, value)

    def __delitem__(self, key: str) -> None:
        if key in self._present_fields():
            if key in ("_source", "_layout_source"):
                self._layout_source = None
            elif key == "_auto_layout":
                self._auto_layout = False
            else:
                setattr(self, key, None)
        else:
            raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        return key in self._present_fields()

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self._present_fields():
            return default
        return getattr(self, key)

    def __iter__(self):
        return iter(sorted(self._present_fields()))

    def __len__(self) -> int:
        return len(self._present_fields())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            d_other = dict(other)
            d_self = {
                k: self[k]
                for k in self
                if k != "_source" or "_layout_source" not in d_other
            }
            return d_self == d_other
        return False

    def copy(self) -> Constraint:
        import copy

        return copy.copy(self)

    def to_dict(self) -> dict[str, Any]:
        return {k: self[k] for k in self}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Constraint:
        ctype = data.get("type")
        source = data.get("_layout_source") or data.get("_source")
        auto = bool(data.get("_auto_layout", False))
        if ctype == "absolute":
            return AbsoluteConstraint(
                x=float(data["x"]),
                y=float(data["y"]),
                anchor=data.get("anchor", Anchor.TOP_LEFT),
                type="absolute",
                _layout_source=source,
                _auto_layout=auto,
            )
        elif ctype == "relative_dir":
            return RelativeConstraint(
                target=data["target"],
                direction=data["direction"],
                margin=float(data.get("margin", 20.0)),
                align=data.get("align", "center"),
                type="relative_dir",
                _layout_source=source,
                _auto_layout=auto,
            )
        elif ctype == "align":
            return AlignConstraint(
                target=data["target"],
                align=data.get("align", "center"),
                axis=data.get("axis", "horizontal"),
                type="align",
                _layout_source=source,
                _auto_layout=auto,
            )
        c = Constraint(type=ctype or "unknown", _layout_source=source, _auto_layout=auto)
        for k, v in data.items():
            if k not in ("type", "_layout_source", "_source", "_auto_layout"):
                setattr(c, k, v)
        return c


@dataclass(eq=False)
class AbsoluteConstraint(Constraint):
    """Position element absolutely with an anchor point."""

    x: float = 0.0
    y: float = 0.0
    anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    type: str = "absolute"
    _layout_source: Optional[str] = None
    _auto_layout: bool = False


@dataclass(eq=False)
class RelativeConstraint(Constraint):
    """Position element relative to a target element in a specified direction."""

    target: Any = None
    direction: str = "right"
    margin: float = 20.0
    align: str = "center"
    type: str = "relative_dir"
    _layout_source: Optional[str] = None
    _auto_layout: bool = False


@dataclass(eq=False)
class AlignConstraint(Constraint):
    """Align element relative to a target element along an axis."""

    target: Any = None
    align: str = "center"
    axis: str = "horizontal"
    type: str = "align"
    _layout_source: Optional[str] = None
    _auto_layout: bool = False


def to_constraint(c: Union[Constraint, dict[str, Any]]) -> Constraint:
    """Coerce a constraint dict or object into a typed Constraint."""
    if isinstance(c, Constraint):
        return c
    if isinstance(c, dict):
        return Constraint.from_dict(c)
    raise TypeError(f"Expected Constraint or dict, got {type(c).__name__}")


class Element:
    """Base class for all diagram elements."""

    def __init__(
        self,
        id: str,
        label: str,
        width: float = 120.0,
        height: float = 60.0,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.label = label
        self.width = float(width)
        self.height = float(height)
        self.bounds: Rect = Rect(0.0, 0.0, self.width, self.height)
        self.parent: Optional[Element] = None
        self.metadata: dict[str, Any] = dict(metadata) if metadata is not None else {}
        self.metadata.update(kwargs)
        self.constraints: list[Any] = []
        self._diagram: Optional[Any] = None
        self.explicit_id: bool = True

    def translate(self, dx: float, dy: float) -> None:
        """Translate element bounds by delta (dx, dy)."""
        self.bounds = Rect(
            self.bounds.x + float(dx),
            self.bounds.y + float(dy),
            self.bounds.width,
            self.bounds.height,
        )

    def clear_constraints(self) -> Element:
        """Clear all positioning constraints from this element."""
        self.constraints.clear()
        return self

    def _find_diagram(self, other: Any = None) -> Optional[Any]:
        """Find the active Diagram instance for this element."""
        if self._diagram is not None:
            return self._diagram
        if other is not None and getattr(other, "_diagram", None) is not None:
            return other._diagram
        return context.current()

    def __rshift__(self, other: Any) -> Any:
        """Connect this element to target using >> operator."""
        if hasattr(other, "_is_edge_builder") and other._is_edge_builder:
            other.source = self
            return other

        diag = self._find_diagram(other)
        if isinstance(other, Element):
            if diag is not None:
                diag.connect(self, other)
            else:
                from diagrams_as_code.connections import Edge

                Edge(self, other)
            return other
        elif isinstance(other, (list, tuple)):
            # Atomically validate all targets before initiating connections
            for target in other:
                if not isinstance(target, Element):
                    raise TypeError(
                        f"Target must be Element, got {type(target).__name__}"
                    )
            for target in other:
                if diag is not None:
                    diag.connect(self, target)
                else:
                    from diagrams_as_code.connections import Edge

                    Edge(self, target)
            return other
        return NotImplemented

    def __rrshift__(self, other: Any) -> Any:
        """Support list fan-in: [s1, s2] >> self."""
        if isinstance(other, (list, tuple)):
            # Atomically validate all sources before initiating connections
            for source in other:
                if not isinstance(source, Element):
                    raise TypeError(
                        f"Source must be Element, got {type(source).__name__}"
                    )
            for source in other:
                diag = self._find_diagram(source)
                if diag is not None:
                    diag.connect(source, self)
                else:
                    from diagrams_as_code.connections import Edge

                    Edge(source, self)
            return self
        elif isinstance(other, Element):
            diag = self._find_diagram(other)
            if diag is not None:
                diag.connect(other, self)
            else:
                from diagrams_as_code.connections import Edge

                Edge(other, self)
            return self
        return NotImplemented


class Shape(Element):
    """Visual shape element with absolute or relative positioning constraints."""

    def __init__(
        self,
        id: str,
        label: str,
        width: float = 120.0,
        height: float = 60.0,
        kind: str = "box",
        icon: Optional[str] = None,
        label_position: str = "auto",
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            id,
            label,
            width=width,
            height=height,
            metadata=metadata,
            **kwargs,
        )
        self.kind = kind
        self.icon = icon
        self.label_position = label_position


    def at(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> Shape:
        """Position element absolutely with an anchor point."""
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
        self.bounds = Rect(
            float(x) - offset.x,
            float(y) - offset.y,
            self.bounds.width,
            self.bounds.height,
        )
        return self

    def right_of(
        self,
        other: Element,
        margin: float = 20.0,
        align: Literal["center", "top", "bottom"] = "center",
    ) -> Shape:
        """Position element to the right of another element."""
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
        margin: float = 20.0,
        align: Literal["center", "top", "bottom"] = "center",
    ) -> Shape:
        """Position element to the left of another element."""
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
        margin: float = 20.0,
        align: Literal["center", "left", "right"] = "center",
    ) -> Shape:
        """Position element below another element."""
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
        margin: float = 20.0,
        align: Literal["center", "left", "right"] = "center",
    ) -> Shape:
        """Position element above another element."""
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
    ) -> Shape:
        """Align element relative to another element."""
        self.constraints.append(
            AlignConstraint(
                target=other,
                align=align,
                axis=axis,
            )
        )
        return self

    def move_to(
        self, x: float, y: float, anchor: Union[Anchor, str] = Anchor.TOP_LEFT
    ) -> Shape:
        """Clear existing constraints and relocate element absolutely."""
        self.clear_constraints()
        return self.at(x, y, anchor=anchor)

    def clone(self, new_id: Optional[str] = None, **overrides: Any) -> Shape:
        """Stamp out an independent copy of this shape from a template."""
        clone_id = new_id or overrides.pop("id", None) or f"{self.id}_clone"
        label = overrides.pop("label", self.label)
        width = overrides.pop("width", self.width)
        height = overrides.pop("height", self.height)
        kind = overrides.pop("kind", self.kind)
        icon = overrides.pop("icon", self.icon)
        metadata = dict(self.metadata)
        if "metadata" in overrides:
            metadata.update(overrides.pop("metadata"))
        cloned = Shape(
            id=clone_id,
            label=label,
            width=width,
            height=height,
            kind=kind,
            icon=icon,
            metadata=metadata,
            **overrides,
        )
        return cloned
