"""UML sequence diagrams, laid out deterministically and drawn on a Diagram.

``SequenceDiagram`` records participants and events in time order, then lays
them out: one column per participant (in declaration order), one row per event
(in call order). Every label is measured with the engine's own text metrics, so
columns grow until no label clips or overlaps. The result is ordinary diagram
content (shapes, text, paths and edges), so themes, lint, SVG, PNG, PDF, the
CLI and the MCP server treat it like any other figure. Pure standard library.

    seq = SequenceDiagram("Checkout", theme="iiot_light")
    web = seq.participant("Web")
    api = seq.participant("API")
    db = seq.participant("Orders DB", kind="database")
    seq.message(web, api, "POST /orders", activate=True)
    with seq.loop("until committed"):
        seq.message(api, db, "INSERT order")
        seq.reply(db, api, "ok")
    with seq.alt("paid") as alt:
        seq.reply(api, web, "201 Created")
        alt.branch("declined")
        seq.reply(api, web, "402 Payment Required")
    seq.note(api, "idempotent on the order key")
    diag = seq.build()          # a Diagram: render_svg(), render_all(), lint ...

Messages: ``message`` (``style`` "solid", "dashed" or "async"), ``reply``
(dashed, open head; ends the sender's activation), self-calls (``message(a,
a, ...)``). Activations: ``activate=True`` / ``deactivate=True`` on a message,
or ``activate(p)`` / ``deactivate(p)``; nested bars step right. Notes: ``note(p,
text, side="right"|"left"|"over")``, or over a pair ``note([a, b], text)``.
Frames: ``loop``, ``opt``, ``alt`` (``branch()`` starts the next operand),
``par``, ``critical``, ``break_`` and the general ``frame(kind, guard)``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Sequence, Union

from diagrams_as_code.diagram import Diagram
from diagrams_as_code.elements import Shape
from diagrams_as_code.labels import node_label
from diagrams_as_code.style import Style
from diagrams_as_code.text.rich import TextStyle, measure

__all__ = ["Frame", "Participant", "SequenceDiagram", "SequenceLayout"]

#: Participant header kinds.
KINDS = ("participant", "actor", "database")
#: Message line styles: solid with a filled head, dashed (a return), async (open head).
MESSAGE_STYLES = ("solid", "dashed", "async")
NOTE_SIDES = ("right", "left", "over")
#: Combined-fragment operators; only ``alt`` and ``par`` have more than one operand.
FRAME_KINDS = ("loop", "alt", "opt", "par", "critical", "break")
_BRANCHING = ("alt", "par")

# Geometry, in pixels.
MESSAGE_SIZE = 12.0  # message label font size
NOTE_SIZE = 12.0
FRAME_SIZE = 11.0  # frame tag and guard font size
HEADER_MIN_W = 96.0
HEADER_H = 44.0
DATABASE_H = 68.0
HEADER_GAP_X = 28.0  # between neighbouring header boxes
FIRST_GAP = 26.0  # header bottom to the first row
LABEL_GAP = 4.0  # message label bottom to its line
LABEL_MARGIN = 12.0  # message label to either end of its line
MIN_ARROW = 48.0
ROW_GAP = 14.0  # between rows
SELF_W = 30.0  # self-call loop width
SELF_H = 22.0  # self-call loop height
BAR_W = 10.0  # activation bar width
BAR_STEP = 5.0  # nested bars step right by this much
MIN_BAR = 12.0
NOTE_PAD = 7.0
NOTE_FOLD = 9.0
NOTE_GAP = 8.0  # note to the lifeline it hangs off
NOTE_WIDTH = 240.0  # notes wrap at this width unless told otherwise
FRAME_PAD = 12.0  # frame edge to its contents
FRAME_HEAD_GAP = 10.0  # under a frame's tag row and a branch guard
LIFELINE_CLEAR = 3.0  # lifelines stop this far short of text they would cross
ACTOR_H = 40.0  # stick figure height
MARGIN = 40.0  # canvas margin around a built diagram
LINE_W = 1.4  # message stroke width

Pt = tuple[float, float]


@dataclass(frozen=True)
class Box:
    """An axis-aligned rectangle in canvas pixels (left, top, right, bottom)."""

    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    def moved(self, dx: float, dy: float) -> Box:
        return Box(self.left + dx, self.top + dy, self.right + dx, self.bottom + dy)

    def overlaps(self, other: Box) -> bool:
        return (self.left < other.right and other.left < self.right
                and self.top < other.bottom and other.top < self.bottom)


def _measure(text: str, size: float, bold: bool = False, max_width: Optional[float] = None) -> tuple[float, float]:
    if not text:
        return (0.0, 0.0)
    return measure(text, TextStyle(size=size, bold=bold), max_width)


@dataclass(eq=False)
class Participant:
    """One column of a sequence diagram: a header and a lifeline."""

    name: str
    kind: str
    index: int
    icon: Optional[str] = None
    _owner: Any = field(default=None, repr=False)


# ------------------------------------------------------------------ events
@dataclass
class _Message:
    src: int
    dst: int
    label: str
    style: str
    activate: bool = False
    deactivate: bool = False


@dataclass
class _Activation:
    p: int
    on: bool


@dataclass
class _Note:
    parts: tuple[int, ...]
    text: str
    side: str
    width: float


@dataclass
class _FrameOpen:
    frame: Frame


@dataclass
class _FrameBranch:
    frame: Frame
    guard: str


@dataclass
class _FrameClose:
    frame: Frame


@dataclass
class _Space:
    height: float


class Frame:
    """A combined fragment (``loop``, ``alt`` ...) used as a ``with`` block."""

    def __init__(self, seq: SequenceDiagram, kind: str, guards: Sequence[str]) -> None:
        self._seq = seq
        self.kind = kind
        self.guard = guards[0] if guards else ""
        self._pending = list(guards[1:])
        self._state = "new"

    def __enter__(self) -> Frame:
        if self._state != "new":
            raise RuntimeError(f"a {self.kind} frame can be entered only once")
        self._seq._push_frame(self)
        self._state = "open"
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self._seq._pop_frame(self, failed=exc_type is not None)
        self._state = "closed"

    def branch(self, guard: Optional[str] = None) -> None:
        """Start the next operand of an ``alt`` or ``par`` frame (a dashed divider).

        With no ``guard``, the next guard given when the frame was made is used.
        """
        if self.kind not in _BRANCHING:
            raise ValueError(f"only alt and par frames have branches, not {self.kind}")
        if self._state != "open":
            raise RuntimeError("branch() must be called inside the frame's with block")
        if not self._seq._frames or self._seq._frames[-1] is not self:
            raise RuntimeError("branch() belongs to the innermost open frame; close inner frames first")
        if guard is None:
            guard = self._pending.pop(0) if self._pending else ""
        self._seq._events.append(_FrameBranch(self, str(guard)))

    #: ``alt.else_("error")`` reads like the UML it draws.
    else_ = branch


# ------------------------------------------------------------------ layout result
@dataclass(frozen=True)
class MessageGeometry:
    """Where one message was drawn: its line's points and its label's box."""

    src: str
    dst: str
    label: str
    style: str
    points: tuple[Pt, ...]
    label_box: Optional[Box]


@dataclass(frozen=True)
class SequenceLayout:
    """The geometry ``SequenceDiagram.layout()`` computed, in local pixels."""

    columns: tuple[float, ...]
    headers: tuple[Box, ...]
    footers: tuple[Box, ...]
    messages: tuple[MessageGeometry, ...]
    bars: tuple[tuple[int, Box], ...]
    notes: tuple[Box, ...]
    frames: tuple[tuple[str, Box], ...]
    texts: tuple[tuple[str, Box], ...]
    lifelines: tuple[tuple[float, float, float], ...]
    bounds: Box


@dataclass
class _Text:
    text: str
    box: Box
    size: float
    bold: bool = False
    italic: bool = False
    align: str = "center"
    max_width: Optional[float] = None


@dataclass
class _OpenFrame:
    frame: Frame
    top: float
    head_w: float
    tag: Box
    tag_text: _Text
    guard_text: Optional[_Text]
    xmin: float = float("inf")
    xmax: float = float("-inf")
    branches: list[tuple[float, Optional[_Text]]] = field(default_factory=list)


@dataclass
class _Plan:
    """Everything to draw, in local coordinates."""

    columns: list[float]
    headers: list[Box]
    footers: list[Box]
    texts: list[_Text] = field(default_factory=list)
    messages: list[tuple[_Message, tuple[Pt, ...], Optional[_Text]]] = field(default_factory=list)
    bars: list[tuple[int, int, Box]] = field(default_factory=list)  # (participant, depth, box)
    notes: list[tuple[Box, _Text]] = field(default_factory=list)
    frames: list[tuple[str, Box, Box, list[float]]] = field(default_factory=list)  # kind, box, tag, dividers
    lifelines: list[tuple[float, float, float]] = field(default_factory=list)  # (x, y0, y1) segments
    header_labels: list[Optional[_Text]] = field(default_factory=list)  # actor names
    footer_labels: list[Optional[_Text]] = field(default_factory=list)


class SequenceDiagram:
    """A UML sequence diagram: participants, messages, activations, notes and frames.

    ``build()`` returns a :class:`Diagram`; ``draw(diagram, origin)`` adds the
    same content to an existing one. ``mirror=True`` repeats the headers under
    the lifelines; ``autonumber=True`` numbers the messages.
    """

    def __init__(self, title: str = "Sequence diagram", *, theme: str = "iiot_light",
                 mirror: bool = False, autonumber: bool = False, **diagram_options: Any) -> None:
        self.title = title
        self.theme = theme
        self.mirror = bool(mirror)
        self.autonumber = bool(autonumber)
        self.diagram_options = dict(diagram_options)
        self.participants: list[Participant] = []
        self._events: list[Any] = []
        self._frames: list[Frame] = []
        self._depth: list[int] = []  # activation depth while recording, for validation

    # ------------------------------------------------------------ recording
    def participant(self, name: str, kind: str = "participant", icon: Optional[str] = None) -> Participant:
        """Add a column. ``kind`` is "participant" (a box), "actor" (a stick figure) or "database"."""
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {KINDS}, got {kind!r}")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("a participant needs a non-empty name")
        if any(p.name == name for p in self.participants):
            raise ValueError(f"participant {name!r} already exists")
        p = Participant(name, kind, len(self.participants), icon, self)
        self.participants.append(p)
        self._depth.append(0)
        return p

    def actor(self, name: str) -> Participant:
        """A participant drawn as a stick figure."""
        return self.participant(name, kind="actor")

    def _index(self, p: Union[Participant, str]) -> int:
        if isinstance(p, Participant):
            if p._owner is not self:
                raise ValueError(f"participant {p.name!r} belongs to another sequence diagram")
            return p.index
        if isinstance(p, str):
            for q in self.participants:
                if q.name == p:
                    return q.index
            raise ValueError(f"no participant named {p!r}")
        raise TypeError(f"expected a Participant or its name, got {type(p).__name__}")

    def message(self, src: Union[Participant, str], dst: Union[Participant, str], label: str = "",
                style: str = "solid", activate: bool = False, deactivate: bool = False) -> None:
        """A message from ``src`` to ``dst`` (the same participant for a self-call).

        ``activate`` starts an activation bar on ``dst`` where the message arrives;
        ``deactivate`` ends ``src``'s innermost bar where it leaves.
        """
        if style not in MESSAGE_STYLES:
            raise ValueError(f"style must be one of {MESSAGE_STYLES}, got {style!r}")
        s, d = self._index(src), self._index(dst)
        if deactivate and self._depth[s] == 0:
            raise ValueError(f"{self.participants[s].name!r} is not active, so it cannot be deactivated")
        if deactivate:
            self._depth[s] -= 1
        if activate:
            self._depth[d] += 1
        self._events.append(_Message(s, d, str(label), style, bool(activate), bool(deactivate)))

    def reply(self, src: Union[Participant, str], dst: Union[Participant, str], label: str = "",
              deactivate: Optional[bool] = None) -> None:
        """A return message (dashed, open head). It ends ``src``'s activation if it has one."""
        s = self._index(src)
        if deactivate is None:
            deactivate = self._depth[s] > 0
        self.message(src, dst, label, style="dashed", deactivate=deactivate)

    def activate(self, p: Union[Participant, str]) -> None:
        """Start an activation bar on ``p`` (at the message that just reached it, if any)."""
        i = self._index(p)
        self._depth[i] += 1
        last = self._events[-1] if self._events else None
        if isinstance(last, _Message) and last.dst == i and not last.activate and not (last.deactivate and last.src == i):
            last.activate = True
        else:
            self._events.append(_Activation(i, True))

    def deactivate(self, p: Union[Participant, str]) -> None:
        """End ``p``'s innermost activation bar (at the message that just left it, if any)."""
        i = self._index(p)
        if self._depth[i] == 0:
            raise ValueError(f"{self.participants[i].name!r} is not active, so it cannot be deactivated")
        self._depth[i] -= 1
        last = self._events[-1] if self._events else None
        if isinstance(last, _Message) and last.src == i and not last.deactivate and not (last.activate and last.dst == i):
            last.deactivate = True
        else:
            self._events.append(_Activation(i, False))

    def note(self, over: Union[Participant, str, Sequence[Union[Participant, str]]], text: str,
             side: str = "right", width: float = NOTE_WIDTH) -> None:
        """A note beside one lifeline (``side`` right or left), over it, or over a pair."""
        if side not in NOTE_SIDES:
            raise ValueError(f"side must be one of {NOTE_SIDES}, got {side!r}")
        if not text:
            raise ValueError("a note needs text")
        if not width > 0:
            raise ValueError(f"width must be positive, got {width!r}")
        targets = list(over) if isinstance(over, (list, tuple)) else [over]
        if not 1 <= len(targets) <= 2:
            raise ValueError("a note goes on one participant or spans two")
        parts = tuple(sorted(self._index(t) for t in targets))
        if len(parts) == 2:
            if side != "right" and side != "over":
                raise ValueError("a note spanning two participants is drawn over them")
            side = "over"
        self._events.append(_Note(parts, str(text), side, float(width)))

    def space(self, height: float = 20.0) -> None:
        """Extra empty time between rows."""
        if not height >= 0:
            raise ValueError(f"height must be >= 0, got {height!r}")
        self._events.append(_Space(float(height)))

    def frame(self, kind: str, *guards: str) -> Frame:
        """A combined fragment: ``with seq.frame("loop", "every 5 s"): ...``."""
        if kind not in FRAME_KINDS:
            raise ValueError(f"kind must be one of {FRAME_KINDS}, got {kind!r}")
        if len(guards) > 1 and kind not in _BRANCHING:
            raise ValueError(f"a {kind} frame has one guard, got {len(guards)}")
        return Frame(self, kind, [str(g) for g in guards])

    def loop(self, guard: str = "") -> Frame:
        return self.frame("loop", guard)

    def opt(self, guard: str = "") -> Frame:
        return self.frame("opt", guard)

    def alt(self, *guards: str) -> Frame:
        """Alternatives. ``branch()`` inside the block starts the next one."""
        return self.frame("alt", *guards)

    def par(self, *guards: str) -> Frame:
        return self.frame("par", *guards)

    def critical(self, guard: str = "") -> Frame:
        return self.frame("critical", guard)

    def break_(self, guard: str = "") -> Frame:
        return self.frame("break", guard)

    def _push_frame(self, frame: Frame) -> None:
        self._frames.append(frame)
        self._events.append(_FrameOpen(frame))

    def _pop_frame(self, frame: Frame, failed: bool = False) -> None:
        if not self._frames or self._frames[-1] is not frame:
            raise RuntimeError("frames must close in the order they were opened")
        self._frames.pop()
        self._events.append(_FrameClose(frame))

    # ------------------------------------------------------------ layout
    def _check(self) -> None:
        if not self.participants:
            raise ValueError("a sequence diagram needs at least one participant")
        if self._frames:
            raise RuntimeError(f"the {self._frames[-1].kind} frame is still open")

    def _header_size(self, p: Participant) -> tuple[float, float]:
        if p.kind == "actor":
            w, h = _measure(p.name, 13.0)
            return (max(40.0, w), ACTOR_H + 4.0 + h)
        kind = "database" if p.kind == "database" else "box"
        tw, _ = _measure(p.name, 13.0, bold=True)
        w = max(HEADER_MIN_W, tw + 28.0)
        h = DATABASE_H if kind == "database" else HEADER_H
        if kind == "database":
            w += 16.0
        for _ in range(8):
            probe = Shape("probe", p.name, width=w, height=h, kind=kind, icon=p.icon, label_position="inside")
            nl = node_label(probe)
            if nl.fits:
                break
            w, h = max(w, nl.needed_width) + 4.0, max(h, nl.needed_height) + 4.0
        return (round(w, 2), round(h, 2))

    def _label(self, index: int, label: str) -> str:
        return f"{index}. {label}" if self.autonumber and label else (f"{index}." if self.autonumber else label)

    def _plan(self) -> _Plan:
        self._check()
        n = len(self.participants)
        sizes = [self._header_size(p) for p in self.participants]

        # ---- pass 1: activation depths at each message, from the events alone
        depth = [0] * n
        msg_depths: list[tuple[int, int, int]] = []  # (src depth, dst depth at arrival, depth after self-call)
        for ev in self._events:
            if isinstance(ev, _Message):
                ds = depth[ev.src]
                if ev.src == ev.dst:
                    after = ds + (1 if ev.activate else 0)
                    msg_depths.append((ds, after, after))
                    depth[ev.src] = after - (1 if ev.deactivate else 0)
                    continue
                dd = depth[ev.dst] + (1 if ev.activate else 0)
                msg_depths.append((ds, dd, dd))
                depth[ev.dst] = dd
                if ev.deactivate:
                    depth[ev.src] -= 1
            elif isinstance(ev, _Activation):
                depth[ev.p] = depth[ev.p] + 1 if ev.on else max(0, depth[ev.p] - 1)

        def right_off(d: int) -> float:
            return 0.0 if d <= 0 else (d - 1) * BAR_STEP + BAR_W / 2

        def left_off(d: int) -> float:
            return 0.0 if d <= 0 else (d - 1) * BAR_STEP - BAR_W / 2

        # ---- pass 2: column gaps from header widths and label widths
        need: list[tuple[int, int, float]] = []
        for i in range(n - 1):
            need.append((i, i + 1, sizes[i][0] / 2 + sizes[i + 1][0] / 2 + HEADER_GAP_X))
        k = 0
        number = 0
        depth = [0] * n
        right_edge = 0.0  # room needed right of the last lifeline
        left_edge = 0.0  # room needed left of the first lifeline
        for ev in self._events:
            if isinstance(ev, _Message):
                number += 1
                ds, dd, _ = msg_depths[k]
                k += 1
                lw, _ = _measure(self._label(number, ev.label), MESSAGE_SIZE)
                if ev.src == ev.dst:
                    reach = max(right_off(ds), right_off(dd)) + SELF_W + 6.0 + lw + LABEL_MARGIN
                    if ev.src < n - 1:
                        need.append((ev.src, ev.src + 1, reach + BAR_W))
                    else:
                        right_edge = max(right_edge, reach)
                    depth[ev.src] = dd - (1 if ev.deactivate else 0)
                    continue
                lo, hi = sorted((ev.src, ev.dst))
                d_lo, d_hi = (ds, dd) if ev.src < ev.dst else (dd, ds)
                span = lw + 2 * LABEL_MARGIN if lw else MIN_ARROW
                need.append((lo, hi, max(MIN_ARROW, span) + right_off(d_lo) - left_off(d_hi)))
                depth[ev.dst] = dd
                if ev.deactivate:
                    depth[ev.src] -= 1
            elif isinstance(ev, _Activation):
                depth[ev.p] = depth[ev.p] + 1 if ev.on else max(0, depth[ev.p] - 1)
            elif isinstance(ev, _Note) and len(ev.parts) == 1:
                nw = _measure(ev.text, NOTE_SIZE, max_width=ev.width)[0] + 2 * NOTE_PAD + NOTE_FOLD
                i = ev.parts[0]
                if ev.side == "right":
                    reach = right_off(depth[i]) + NOTE_GAP + nw + LABEL_MARGIN
                    if i < n - 1:
                        need.append((i, i + 1, reach + BAR_W))
                    else:
                        right_edge = max(right_edge, reach)
                elif ev.side == "left":
                    reach = -left_off(depth[i]) + NOTE_GAP + nw + LABEL_MARGIN
                    if i > 0:
                        need.append((i - 1, i, reach + BAR_W))
                    else:
                        left_edge = max(left_edge, reach)
        gaps = [0.0] * max(n - 1, 0)
        for lo, hi, want in sorted(need, key=lambda c: (c[1] - c[0], c[0], c[1])):
            have = sum(gaps[lo:hi])
            if have < want:
                extra = (want - have) / (hi - lo)
                for g in range(lo, hi):
                    gaps[g] += extra
        xs = [0.0]
        for g in gaps:
            xs.append(round(xs[-1] + g, 2))

        # ---- pass 3: rows
        band = max(h for _, h in sizes)
        headers = [Box(x - w / 2, band - h, x + w / 2, band) for x, (w, h) in zip(xs, sizes)]
        plan = _Plan(columns=xs, headers=headers, footers=[])
        plan.header_labels = [self._actor_label(p, b) for p, b in zip(self.participants, headers)]
        cursor = band + FIRST_GAP
        depth = [0] * n
        open_bars: list[list[float]] = [[] for _ in range(n)]
        frames: list[_OpenFrame] = []
        number = 0
        k = 0

        def edge_x(i: int, d: int, toward_right: bool) -> float:
            if d <= 0:
                return xs[i]
            return xs[i] + (right_off(d) if toward_right else left_off(d))

        def touch(left: float, right: float) -> None:
            for f in frames:
                f.xmin, f.xmax = min(f.xmin, left), max(f.xmax, right)

        def touch_bars(i: int) -> None:
            if depth[i] > 0:
                touch(xs[i] - BAR_W / 2, xs[i] + right_off(depth[i]))

        def text(body: str, box: Box, size: float, **kw: Any) -> _Text:
            t = _Text(body, box, size, **kw)
            plan.texts.append(t)
            touch(box.left, box.right)
            return t

        def open_bar(i: int, y: float) -> None:
            open_bars[i].append(y)
            depth[i] += 1

        def close_bar(i: int, y: float) -> None:
            if not open_bars[i]:
                return
            d = depth[i]
            y0 = open_bars[i].pop()
            depth[i] -= 1
            cx = xs[i] + (d - 1) * BAR_STEP
            box = Box(cx - BAR_W / 2, y0, cx + BAR_W / 2, max(y, y0 + MIN_BAR))
            plan.bars.append((i, d, box))
            touch(box.left, box.right)

        last_y = cursor
        for ev in self._events:
            if isinstance(ev, _Message):
                number += 1
                ds, dd, _ = msg_depths[k]
                k += 1
                body = self._label(number, ev.label)
                lw, lh = _measure(body, MESSAGE_SIZE)
                if ev.src == ev.dst:
                    i = ev.src
                    x0 = edge_x(i, ds, True)
                    y1 = cursor + max(0.0, (lh - SELF_H) / 2)
                    y2 = y1 + SELF_H
                    x_back = edge_x(i, dd, True)
                    x_out = max(x0, x_back) + SELF_W
                    pts: tuple[Pt, ...] = ((x0, y1), (x_out, y1), (x_out, y2), (x_back, y2))
                    touch(min(x0, x_back), x_out)
                    touch_bars(i)
                    label = None
                    if body:
                        mid = (y1 + y2) / 2
                        label = text(body, Box(x_out + 6.0, mid - lh / 2, x_out + 6.0 + lw, mid + lh / 2),
                                     MESSAGE_SIZE, align="left")
                    if ev.activate:
                        open_bar(i, y2)
                    if ev.deactivate:
                        close_bar(i, y2)
                    plan.messages.append((ev, pts, label))
                    last_y = y2
                    cursor = max(y2, label.box.bottom if label else y2) + ROW_GAP
                    continue
                y = cursor + (lh + LABEL_GAP if body else 6.0)
                toward = ev.dst > ev.src
                xa = edge_x(ev.src, ds, toward)
                if ev.activate:
                    open_bar(ev.dst, y)
                xb = edge_x(ev.dst, depth[ev.dst], not toward)
                label = None
                if body:
                    mid = (xa + xb) / 2
                    label = text(body, Box(mid - lw / 2, y - LABEL_GAP - lh, mid + lw / 2, y - LABEL_GAP),
                                 MESSAGE_SIZE)
                touch(min(xa, xb), max(xa, xb))
                touch_bars(ev.src)
                touch_bars(ev.dst)
                if ev.deactivate:
                    close_bar(ev.src, y)
                plan.messages.append((ev, ((xa, y), (xb, y)), label))
                last_y = y
                cursor = y + ROW_GAP
            elif isinstance(ev, _Activation):
                if ev.on:
                    open_bar(ev.p, cursor)
                    touch(xs[ev.p] - BAR_W, xs[ev.p] + BAR_W)
                else:
                    close_bar(ev.p, last_y)
            elif isinstance(ev, _Note):
                tw, th = _measure(ev.text, NOTE_SIZE, max_width=ev.width)
                w, h = tw + 2 * NOTE_PAD + NOTE_FOLD, th + 2 * NOTE_PAD
                i = ev.parts[0]
                if len(ev.parts) == 2:
                    lo_x, hi_x = xs[ev.parts[0]] - 24.0, xs[ev.parts[1]] + 24.0
                    w = max(w, hi_x - lo_x)
                    left = (lo_x + hi_x) / 2 - w / 2
                elif ev.side == "right":
                    left = edge_x(i, depth[i], True) + NOTE_GAP
                elif ev.side == "left":
                    left = edge_x(i, depth[i], False) - NOTE_GAP - w
                else:
                    w = max(w, 60.0)
                    left = xs[i] - w / 2
                box = Box(left, cursor, left + w, cursor + h)
                t = _Text(ev.text, Box(left + NOTE_PAD, cursor + NOTE_PAD, left + NOTE_PAD + tw,
                                       cursor + NOTE_PAD + th), NOTE_SIZE, align="left", max_width=ev.width)
                plan.texts.append(t)
                plan.notes.append((box, t))
                touch(box.left, box.right)
                cursor = box.bottom + ROW_GAP
            elif isinstance(ev, _Space):
                cursor += ev.height
            elif isinstance(ev, _FrameOpen):
                kw, kh = _measure(ev.frame.kind, FRAME_SIZE, bold=True)
                tag = Box(0.0, cursor, kw + 2 * 6.0 + 6.0, cursor + kh + 6.0)  # x set on close
                tag_text = _Text(ev.frame.kind, Box(6.0, cursor + 3.0, 6.0 + kw, cursor + 3.0 + kh),
                                 FRAME_SIZE, bold=True, align="left")
                guard_text = None
                head_w = tag.width
                if ev.frame.guard:
                    gw, gh = _measure(f"[{ev.frame.guard}]", FRAME_SIZE)
                    gy = cursor + (tag.height - gh) / 2
                    guard_text = _Text(f"[{ev.frame.guard}]", Box(tag.right + 8.0, gy, tag.right + 8.0 + gw, gy + gh),
                                       FRAME_SIZE, align="left")
                    head_w = tag.right + 8.0 + gw + 8.0
                frames.append(_OpenFrame(ev.frame, cursor, head_w, tag, tag_text, guard_text))
                cursor = tag.bottom + FRAME_HEAD_GAP
            elif isinstance(ev, _FrameBranch):
                f = frames[-1]
                sep = cursor - 4.0
                guard = None
                if ev.guard:
                    gw, gh = _measure(f"[{ev.guard}]", FRAME_SIZE)
                    guard = _Text(f"[{ev.guard}]", Box(8.0, sep + 4.0, 8.0 + gw, sep + 4.0 + gh), FRAME_SIZE,
                                  align="left")
                    cursor = guard.box.bottom + FRAME_HEAD_GAP
                else:
                    cursor = sep + FRAME_HEAD_GAP
                f.branches.append((sep, guard))
            elif isinstance(ev, _FrameClose):
                f = frames.pop()
                if f.xmin > f.xmax:  # an empty frame spans every lifeline
                    f.xmin, f.xmax = xs[0] - 20.0, xs[-1] + 20.0
                left = f.xmin - FRAME_PAD
                widest = max([f.head_w] + [g.box.right + 8.0 for _, g in f.branches if g is not None])
                right = max(f.xmax + FRAME_PAD, left + widest)
                bottom = cursor - ROW_GAP + 10.0
                box = Box(left, f.top, right, bottom)
                tag = f.tag.moved(left, 0.0)
                plan.texts.append(_moved(f.tag_text, left))
                if f.guard_text is not None:
                    plan.texts.append(_moved(f.guard_text, left))
                for _, g in f.branches:
                    if g is not None:
                        plan.texts.append(_moved(g, left))
                plan.frames.append((f.frame.kind, box, tag, [s for s, _ in f.branches]))
                touch(box.left, box.right)
                cursor = bottom + ROW_GAP
        end = cursor + 6.0
        for i in range(n):
            while open_bars[i]:
                close_bar(i, end - 6.0)

        # ---- footers and lifelines
        if self.mirror:
            plan.footers = [Box(b.left, end, b.right, end + b.height) for b in headers]
            plan.footer_labels = [self._actor_label(p, b) for p, b in zip(self.participants, plan.footers)]
        blockers = [t.box for t in plan.texts] + [b for b, _ in plan.notes] + [f[2] for f in plan.frames]
        for i, x in enumerate(xs):
            top = headers[i].bottom
            plan.lifelines.extend((x, a, b) for a, b in _gaps(x, top, end, blockers))
        return plan

    @staticmethod
    def _actor_label(p: Participant, header: Box) -> Optional[_Text]:
        if p.kind != "actor":
            return None
        w, h = _measure(p.name, 13.0)
        cx = (header.left + header.right) / 2
        return _Text(p.name, Box(cx - w / 2, header.bottom - h, cx + w / 2, header.bottom), 13.0)

    def layout(self) -> SequenceLayout:
        """The geometry the diagram will be drawn with, in local pixels (top-left near 0, 0)."""
        plan = self._plan()
        names = [p.name for p in self.participants]
        boxes = _all_boxes(plan)
        return SequenceLayout(
            columns=tuple(plan.columns),
            headers=tuple(plan.headers),
            footers=tuple(plan.footers),
            messages=tuple(
                MessageGeometry(names[m.src], names[m.dst], m.label, m.style, pts, t.box if t else None)
                for m, pts, t in plan.messages
            ),
            bars=tuple((i, b) for i, _, b in plan.bars),
            notes=tuple(b for b, _ in plan.notes),
            frames=tuple((k, b) for k, b, _, _ in plan.frames),
            texts=tuple((t.text, t.box) for t in plan.texts),
            lifelines=tuple(plan.lifelines),
            bounds=Box(min(b.left for b in boxes), min(b.top for b in boxes),
                       max(b.right for b in boxes), max(b.bottom for b in boxes)),
        )

    # ------------------------------------------------------------ drawing
    def build(self) -> Diagram:
        """A new Diagram holding this sequence diagram, with a margin around it."""
        diag = Diagram(self.title, theme=self.theme, **self.diagram_options)
        self.draw(diag, (MARGIN, MARGIN))
        return diag

    def draw(self, diag: Diagram, origin: Pt = (MARGIN, MARGIN)) -> Box:
        """Add the diagram to ``diag`` with its top-left at ``origin``; returns the box it fills."""
        plan = self._plan()
        boxes = _all_boxes(plan)
        dx = float(origin[0]) - min(b.left for b in boxes)
        dy = float(origin[1]) - min(b.top for b in boxes)

        def pt(p: Pt) -> Pt:
            return (round(p[0] + dx, 2), round(p[1] + dy, 2))

        def mv(b: Box) -> Box:
            return b.moved(dx, dy)

        line = Style(fill="none", stroke_width=1.0, dash="5,4")
        for x, a, b in plan.lifelines:
            diag.polyline([pt((x, a)), pt((x, b))], style=line, z=-3, obstacle=False)
        for kind, box, tag, dividers in plan.frames:
            fb, tb = mv(box), mv(tag)
            diag.polyline(_ring(fb), style=Style(fill="none", stroke_width=1.2), z=-2, obstacle=False)
            notch = 6.0
            diag.polygon([(tb.left, tb.top), (tb.right, tb.top), (tb.right, tb.bottom - notch),
                          (tb.right - notch, tb.bottom), (tb.left, tb.bottom)],
                         style=Style(stroke_width=1.2), z=-0.5, obstacle=False)
            for y in dividers:
                yy = round(y + dy, 2)
                diag.polyline([(fb.left, yy), (fb.right, yy)], style=Style(fill="none", stroke_width=1.0, dash="6,4"),
                              z=-2, obstacle=False)
        for box, _ in plan.notes:
            b = mv(box)
            f = NOTE_FOLD
            diag.polygon([(b.left, b.top), (b.right - f, b.top), (b.right, b.top + f), (b.right, b.bottom),
                          (b.left, b.bottom)], style=Style(stroke_width=1.0), z=-1, obstacle=False)
            diag.polyline([(b.right - f, b.top), (b.right - f, b.top + f), (b.right, b.top + f)],
                          style=Style(fill="none", stroke_width=1.0), z=-1, obstacle=False)
        for _, _, box in sorted(plan.bars, key=lambda t: (t[1], t[0], t[2].top)):
            b = mv(box)
            diag.polygon([(b.left, b.top), (b.right, b.top), (b.right, b.bottom), (b.left, b.bottom)],
                         style=Style(stroke_width=1.2), z=-1, obstacle=False)
        for row in (plan.headers, plan.footers):
            labels = plan.header_labels if row is plan.headers else plan.footer_labels
            for p, box, label in zip(self.participants, row, labels):
                self._draw_header(diag, p, mv(box), label, dx, dy)
        for m, pts, _ in plan.messages:
            dashed = m.style == "dashed"
            head = "open" if m.style in ("async", "dashed") else "triangle"
            ends = [pt(p) for p in pts]
            opts: dict[str, Any] = {"routing": "direct", "width": LINE_W, "head": head, "arrow_size": 0.9}
            if len(ends) > 2:
                opts["via"] = ends[1:-1]
                opts["corner_radius"] = 0.0
            diag.connect(ends[0], ends[-1], style="dashed" if dashed else "solid", **opts)
        bar_boxes = [b for _, _, b in plan.bars]
        for t in plan.texts:
            b = mv(t.box)
            if any(t.box.overlaps(bar) for bar in bar_boxes):
                # A plate keeps the text readable where it crosses an activation bar.
                diag.polygon(_ring(Box(b.left - 3, b.top - 2, b.right + 3, b.bottom + 2))[:-1],
                             style=Style(stroke="none"), z=-0.5, obstacle=False)
            el = diag.text(t.text, size=t.size, bold=t.bold, italic=t.italic, align=t.align,
                           max_width=t.max_width)
            el.at(round(b.left, 2), round(b.top, 2))
        out = [mv(b) for b in boxes]
        return Box(min(b.left for b in out), min(b.top for b in out),
                   max(b.right for b in out), max(b.bottom for b in out))

    @staticmethod
    def _draw_header(diag: Diagram, p: Participant, box: Box, label: Optional[_Text], dx: float, dy: float) -> None:
        if p.kind == "actor":
            cx, top = (box.left + box.right) / 2, box.top
            r = 7.0
            head = (f"M {cx - r:.2f} {top + r:.2f} a {r} {r} 0 1 0 {2 * r} 0 a {r} {r} 0 1 0 {-2 * r} 0 "
                    f"M {cx:.2f} {top + 2 * r:.2f} L {cx:.2f} {top + 28:.2f} "
                    f"M {cx - 12:.2f} {top + 19:.2f} L {cx + 12:.2f} {top + 19:.2f} "
                    f"M {cx:.2f} {top + 28:.2f} L {cx - 10:.2f} {top + ACTOR_H:.2f} "
                    f"M {cx:.2f} {top + 28:.2f} L {cx + 10:.2f} {top + ACTOR_H:.2f}")
            diag.path(head, style=Style(fill="none", stroke_width=1.6), obstacle=False)
            if label is not None:
                b = label.box.moved(dx, dy)
                diag.text(label.text, size=label.size, align="center").at(round(b.left, 2), round(b.top, 2))
            return
        kind = "database" if p.kind == "database" else "box"
        diag.shape(p.name, box.width, box.height, kind=kind, icon=p.icon, label_position="inside").at(
            round(box.left, 2), round(box.top, 2))


def _moved(t: _Text, dx: float) -> _Text:
    return _Text(t.text, t.box.moved(dx, 0.0), t.size, t.bold, t.italic, t.align, t.max_width)


def _ring(b: Box) -> list[Pt]:
    return [(b.left, b.top), (b.right, b.top), (b.right, b.bottom), (b.left, b.bottom), (b.left, b.top)]


def _gaps(x: float, top: float, bottom: float, blockers: Sequence[Box]) -> list[tuple[float, float]]:
    """The runs of a vertical line at ``x`` from ``top`` to ``bottom`` that miss every blocker."""
    cuts = sorted(
        (b.top - LIFELINE_CLEAR, b.bottom + LIFELINE_CLEAR)
        for b in blockers
        if b.left - LIFELINE_CLEAR < x < b.right + LIFELINE_CLEAR
    )
    runs: list[tuple[float, float]] = []
    y = top
    for a, b in cuts:
        if a > y + 1.0:
            runs.append((y, min(a, bottom)))
        y = max(y, b)
        if y >= bottom:
            break
    if y < bottom - 1.0:
        runs.append((y, bottom))
    return [(a, b) for a, b in runs if b - a > 1.0]


def _all_boxes(plan: _Plan) -> list[Box]:
    boxes = list(plan.headers) + list(plan.footers)
    boxes += [t.box for t in plan.texts]
    boxes += [b for b, _ in plan.notes] + [b for _, b, _, _ in plan.frames] + [b for _, _, b in plan.bars]
    for _, pts, _ in plan.messages:
        boxes += [Box(x, y, x, y) for x, y in pts]
    boxes += [Box(x, a, x, b) for x, a, b in plan.lifelines]
    return boxes
