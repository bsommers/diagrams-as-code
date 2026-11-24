"""Gantt charts and timelines on a Diagram: date axes, task bars, dependencies.

``GanttChart`` schedules tasks from their durations and finish-to-start
dependencies, finds the critical path, and draws a two-tier date header,
gridlines, bars with percent complete, milestones, phases, dependency arrows and
a "today" line. ``Timeline`` puts dated events on a ruler with stacked labels
that never overlap, for incident timelines and release trains. Both draw with
the diagram's own text, polygons, paths and edges, so the result takes part in
lint, the visual audit, SVG, PNG and PDF output like any other figure. Pure
standard library; dates are ``datetime.date`` (a ``Timeline`` also takes naive
``datetime.datetime``); there is no timezone logic.

    with Diagram("Plan", theme="pastel_light") as d:
        g = GanttChart(d, today=date(2026, 3, 11))
        with g.phase("Build"):
            g.task("api", "API", start=date(2026, 3, 2), duration=5, progress=1.0)
            g.task("ui", "UI", after="api", duration=8, progress=0.4)
        g.milestone("ship", "Ship", after="ui")
        g.draw()

Scheduling semantics: ``start`` is the first day of work, ``duration`` counts
calendar days, and a task's ``finish`` is the day after its last day (an
exclusive end), so a successor starts on its predecessor's ``finish``. ``end``
is an inclusive alternative to ``duration``. An explicit ``start`` on a task
with dependencies is a start-no-earlier-than constraint.

Critical path: a forward pass (earliest start = the latest predecessor finish
plus lag, or the start constraint) and a backward pass (latest finish = the
earliest successor latest start minus its lag, or the project finish) over a
topological order; slack is latest start minus earliest start, and the critical
tasks are those with zero slack. With no start constraints these are exactly the
tasks on a longest path through the dependency graph; every tied longest path is
critical. Integer day arithmetic, so ties are exact. See docs/gantt-timelines.md.
"""
from __future__ import annotations

import datetime as _dt
import heapq
import math
import re
import warnings
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from typing import Iterator, Optional, Sequence, Union

from diagrams_as_code.diagram import Diagram
from diagrams_as_code.geometry import Point
from diagrams_as_code.style import Style
from diagrams_as_code.text import TextStyle, measure

When = Union[_dt.date, _dt.datetime]
Box = tuple[float, float, float, float]  # left, top, right, bottom
Pt = tuple[float, float]

DAY = 86400
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

#: Tick steps tried for each scale, finest first.
STEPS: dict[str, tuple[int, ...]] = {
    "minutes": (1, 5, 10, 15, 30),
    "hours": (1, 2, 3, 6, 12),
    "days": (1,),
    "weeks": (1, 2),
    "months": (1, 2, 3, 6),
    "years": (1, 2, 5, 10, 25, 50, 100),
}
SCALES: tuple[str, ...] = tuple(STEPS)
#: Scales available to a GanttChart, whose dates are whole days.
DATE_SCALES: tuple[str, ...] = ("days", "weeks", "months", "years")


class ScheduleError(ValueError):
    """A task set that cannot be scheduled: a cycle, an unknown dependency, no start."""


# ---------------------------------------------------------------------- time


def to_seconds(when: When) -> int:
    """Seconds since the proleptic Gregorian origin; a date is its midnight."""
    if isinstance(when, _dt.datetime):
        if when.tzinfo is not None and when.utcoffset() is not None:
            raise ValueError("timezone-aware datetimes are not supported; pass naive ones")
        return when.toordinal() * DAY + when.hour * 3600 + when.minute * 60 + when.second
    if isinstance(when, _dt.date):
        return when.toordinal() * DAY
    raise TypeError(f"expected a datetime.date or datetime.datetime, got {type(when).__name__}")


def from_seconds(s: int) -> _dt.datetime:
    """Convert seconds since the proleptic Gregorian ordinal epoch back to a ``datetime``."""
    return _dt.datetime.fromordinal(s // DAY) + _dt.timedelta(seconds=s % DAY)


def _ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def _month_index(d: _dt.date) -> int:
    return d.year * 12 + d.month - 1


def _month_start(index: int) -> _dt.date:
    return _dt.date(index // 12, index % 12 + 1, 1)


def _ticks_s(lo: int, hi: int, scale: str, step: int = 1) -> list[int]:
    """Tick positions (seconds) in [lo, hi] for ``scale`` every ``step`` units."""
    if scale not in STEPS:
        raise ValueError(f"scale must be one of {list(SCALES)}, got {scale!r}")
    if step < 1:
        raise ValueError("step must be a positive integer")
    if scale in ("minutes", "hours", "days"):
        unit = {"minutes": 60, "hours": 3600, "days": DAY}[scale] * step
        return list(range(_ceil_div(lo, unit) * unit, hi + 1, unit))
    first_day = _ceil_div(lo, DAY)
    last_day = hi // DAY
    if scale == "weeks":
        # Ordinal 1 (0001-01-01) is a Monday; a 2-week step keeps an absolute parity.
        d = first_day
        while d % 7 != 1 or ((d - 1) // 7) % step:
            d += 1
        return [k * DAY for k in range(d, last_day + 1, 7 * step)]
    out = []
    if scale == "months":
        m = _month_index(_dt.date.fromordinal(first_day))
        while True:
            start = _month_start(m)
            if start.toordinal() < first_day or m % step:
                m += 1
                continue
            if start.toordinal() > last_day:
                break
            out.append(start.toordinal() * DAY)
            m += step
        return out
    year = _dt.date.fromordinal(first_day).year
    while True:
        start = _dt.date(year, 1, 1)
        if start.toordinal() >= first_day and year % step == 0:
            if start.toordinal() > last_day:
                break
            out.append(start.toordinal() * DAY)
        elif start.toordinal() > last_day:
            break
        year += 1
    return out


def date_ticks(lo: When, hi: When, scale: str, step: int = 1) -> list[When]:
    """Tick dates in [lo, hi]: midnights for days, Mondays for weeks, the 1st for
    months, 1 January for years, whole minutes or hours for the time scales.

    Day-and-coarser ticks come back as ``date``; minute and hour ticks as ``datetime``.
    """
    out = _ticks_s(to_seconds(lo), to_seconds(hi), scale, step)
    if scale in ("minutes", "hours"):
        return [from_seconds(s) for s in out]
    return [_dt.date.fromordinal(s // DAY) for s in out]


def tick_label(s: int, scale: str, long: bool = False) -> str:
    """The text of a tick at ``s`` seconds. ``long`` adds the month (or date)."""
    t = from_seconds(s)
    if scale in ("minutes", "hours"):
        if long and s % DAY == 0:
            return f"{_MONTHS[t.month - 1]} {t.day}"
        return f"{t.hour:02d}:{t.minute:02d}"
    if scale in ("days", "weeks"):
        return f"{_MONTHS[t.month - 1]} {t.day}" if long else str(t.day)
    if scale == "months":
        return f"{_MONTHS[t.month - 1]} {t.year}" if long else _MONTHS[t.month - 1]
    return str(t.year)


def _upper_scale(scale: str) -> Optional[str]:
    return {"minutes": "days", "hours": "days", "days": "months", "weeks": "months",
            "months": "years"}.get(scale)


def _upper_label(s: int, scale: str) -> str:
    t = from_seconds(s)
    if scale == "days":
        return f"{_MONTHS[t.month - 1]} {t.day}, {t.year}"
    if scale == "months":
        return f"{_MONTHS[t.month - 1]} {t.year}"
    return str(t.year)


def _period_floor(s: int, scale: str) -> int:
    d = _dt.date.fromordinal(s // DAY)
    if scale == "weeks":
        return (d.toordinal() - (d.toordinal() - 1) % 7) * DAY
    if scale == "months":
        return d.replace(day=1).toordinal() * DAY
    if scale == "years":
        return _dt.date(d.year, 1, 1).toordinal() * DAY
    return (s // DAY) * DAY


def _period_ceil(s: int, scale: str) -> int:
    f = _period_floor(s, scale)
    if f == s:
        return s
    d = _dt.date.fromordinal(f // DAY)
    if scale == "weeks":
        return f + 7 * DAY
    if scale == "months":
        return _month_start(_month_index(d) + 1).toordinal() * DAY
    if scale == "years":
        return _dt.date(d.year + 1, 1, 1).toordinal() * DAY
    return f + DAY


# ---------------------------------------------------------------------- scheduling


@dataclass
class Task:
    """One schedulable item: a task (``duration`` >= 1 day) or a milestone (0)."""

    id: str
    label: str
    duration: int
    start: Optional[_dt.date] = None
    after: tuple[str, ...] = ()
    lag: int = 0
    progress: Optional[float] = None
    milestone: bool = False
    phase: Optional[int] = None
    color: Optional[str] = None
    index: int = 0


@dataclass(frozen=True)
class Scheduled:
    """A task's computed dates. ``finish`` is exclusive (the day after the last day)."""

    id: str
    start: _dt.date
    finish: _dt.date
    latest_start: _dt.date
    latest_finish: _dt.date
    slack: int
    critical: bool

    @property
    def duration(self) -> int:
        """Length of the task in whole days (finish minus start)."""
        return (self.finish - self.start).days


@dataclass(frozen=True)
class Schedule:
    """The result of :func:`schedule`: per-task dates, project bounds, critical links."""

    tasks: dict[str, Scheduled]
    start: _dt.date
    finish: _dt.date
    #: (predecessor, successor) pairs that drive the successor's start and are both critical.
    critical_links: tuple[tuple[str, str], ...]
    order: tuple[str, ...]

    @property
    def critical(self) -> list[str]:
        """Critical task ids in declaration order."""
        return [t for t in self.order if self.tasks[t].critical]

    def paths(self, limit: int = 1000) -> list[list[str]]:
        """Every critical chain from a critical task with no critical predecessor to
        one finishing on the project finish, in declaration order (at most ``limit``)."""
        succ: dict[str, list[str]] = {t: [] for t in self.order}
        has_pred: set[str] = set()
        for p, s in self.critical_links:
            succ[p].append(s)
            has_pred.add(s)
        pos = {t: i for i, t in enumerate(self.order)}
        for v in succ.values():
            v.sort(key=pos.__getitem__)
        out: list[list[str]] = []

        def walk(node: str, trail: list[str]) -> None:
            if len(out) >= limit:
                return
            trail = trail + [node]
            if not succ[node]:
                if self.tasks[node].finish == self.finish:
                    out.append(trail)
                return
            for nxt in succ[node]:
                walk(nxt, trail)

        for t in self.critical:
            if t not in has_pred:
                walk(t, [])
        return out

    @property
    def critical_path(self) -> list[str]:
        """The first critical chain (declaration order breaks ties); [] if none."""
        paths = self.paths(limit=1)
        return paths[0] if paths else []


def _find_cycle(nodes: Sequence[str], preds: dict[str, tuple[str, ...]]) -> list[str]:
    """A dependency cycle among ``nodes`` (all of which lie on or lead into one)."""
    remaining = set(nodes)
    for start in nodes:
        trail: list[str] = []
        seen: dict[str, int] = {}
        node = start
        while node not in seen:
            seen[node] = len(trail)
            trail.append(node)
            node = next(p for p in preds[node] if p in remaining)
        return trail[seen[node]:] + [node]
    return []


def schedule(tasks: Sequence[Task], project_start: Optional[_dt.date] = None) -> Schedule:
    """Compute earliest and latest dates, slack and the critical tasks (CPM).

    Raises :class:`ScheduleError` for a duplicate id, an unknown dependency, a
    cycle, or a task with neither a start date nor dependencies (when no
    ``project_start`` is given).
    """
    if not tasks:
        raise ScheduleError("nothing to schedule: add a task or milestone first")
    by_id: dict[str, Task] = {}
    for t in tasks:
        if t.id in by_id:
            raise ScheduleError(f"duplicate task id {t.id!r}")
        by_id[t.id] = t
    for t in tasks:
        for p in t.after:
            if p not in by_id:
                raise ScheduleError(f"task {t.id!r} depends on unknown task {p!r}")
    order_index = {t.id: i for i, t in enumerate(tasks)}
    succs: dict[str, list[str]] = {t.id: [] for t in tasks}
    indeg = {t.id: len(set(t.after)) for t in tasks}
    for t in tasks:
        for p in dict.fromkeys(t.after):
            succs[p].append(t.id)
    # Kahn's algorithm; a heap on declaration index keeps the order deterministic.
    heap = [(order_index[t], t) for t, n in indeg.items() if n == 0]
    heapq.heapify(heap)
    topo: list[str] = []
    while heap:
        _, node = heapq.heappop(heap)
        topo.append(node)
        for s in succs[node]:
            indeg[s] -= 1
            if indeg[s] == 0:
                heapq.heappush(heap, (order_index[s], s))
    if len(topo) != len(tasks):
        stuck = [t.id for t in tasks if t.id not in set(topo)]
        cycle = _find_cycle(stuck, {t.id: t.after for t in tasks})
        raise ScheduleError("dependency cycle: " + " -> ".join(cycle))

    base = project_start.toordinal() if project_start else None
    es: dict[str, int] = {}
    ef: dict[str, int] = {}
    for tid in topo:
        t = by_id[tid]
        cands = [ef[p] + t.lag for p in t.after]
        if t.start is not None:
            cands.append(t.start.toordinal())
        if not cands:
            if base is None:
                raise ScheduleError(f"task {tid!r} has no start date and no dependencies")
            cands.append(base)
        es[tid] = max(cands)
        ef[tid] = es[tid] + t.duration
    finish = max(ef.values())
    lf: dict[str, int] = {}
    ls: dict[str, int] = {}
    for tid in reversed(topo):
        cands = [ls[s] - by_id[s].lag for s in succs[tid]]
        lf[tid] = min(cands) if cands else finish
        ls[tid] = lf[tid] - by_id[tid].duration
    out: dict[str, Scheduled] = {}
    for t in tasks:
        slack = ls[t.id] - es[t.id]
        out[t.id] = Scheduled(
            t.id, _dt.date.fromordinal(es[t.id]), _dt.date.fromordinal(ef[t.id]),
            _dt.date.fromordinal(ls[t.id]), _dt.date.fromordinal(lf[t.id]), slack, slack == 0,
        )
    links = tuple(
        (p, t.id) for t in tasks for p in dict.fromkeys(t.after)
        if out[p].critical and out[t.id].critical and ef[p] + t.lag == es[t.id]
    )
    return Schedule(out, _dt.date.fromordinal(min(es.values())), _dt.date.fromordinal(finish),
                    links, tuple(t.id for t in tasks))


# ---------------------------------------------------------------------- palette


@dataclass(frozen=True)
class Palette:
    """Colours of a chart. Built from the diagram's theme; any field can be overridden."""

    bar: str
    bar_stroke: str
    progress: str
    critical: str
    critical_fill: str
    milestone: str
    phase: str
    grid: str
    header: str
    band: str
    today: str
    arrow: str
    event: str
    span: str


def _luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except (ValueError, IndexError):
        return 1.0
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def palette_for(theme) -> Palette:
    """A palette suited to ``theme``: fixed light colours, or theme colours on dark."""
    if _luminance(theme.background) >= 0.5:
        return Palette(
            bar="#C9DAF0", bar_stroke="#4A6FA5", progress="#4A6FA5", critical="#B03A2E",
            critical_fill="#F4CCC6", milestone="#1F2F57", phase="#1F2F57", grid="#DDE1E8",
            header="#EEF1F6", band="#F6F7FA", today="#D35400", arrow="#5A6478",
            event="#1F2F57", span="#E67E22",
        )
    return Palette(
        bar=theme.node_fill, bar_stroke=theme.node_stroke, progress=theme.accent,
        critical="#FF6B6B", critical_fill="#5A2228", milestone=theme.accent, phase=theme.text,
        grid=theme.group_stroke, header=theme.group_bg, band=theme.group_bg, today="#FF9F43",
        arrow=theme.subtext, event=theme.accent, span="#FF9F43",
    )


# ---------------------------------------------------------------------- geometry helpers


def boxes_overlap(a: Box, b: Box, gap: float = 0.0) -> bool:
    """True if two boxes overlap or come closer than ``gap``."""
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def _seg_hits(a: Pt, b: Pt, box: Box) -> bool:
    """True if the axis-aligned segment ab enters the open box."""
    return (max(a[0], b[0]) > box[0] and min(a[0], b[0]) < box[2]
            and max(a[1], b[1]) > box[1] and min(a[1], b[1]) < box[3])


def _segs_run_together(s1: tuple[Pt, Pt], s2: tuple[Pt, Pt], near: float = 4.0) -> bool:
    """True if two axis-aligned segments run along each other closer than ``near``."""
    (a, b), (c, d) = s1, s2
    v1, v2 = a[0] == b[0], c[0] == d[0]
    if v1 != v2:
        return False
    if v1:
        lo, hi = max(min(a[1], b[1]), min(c[1], d[1])), min(max(a[1], b[1]), max(c[1], d[1]))
        return abs(a[0] - c[0]) < near and hi - lo > 1.0
    lo, hi = max(min(a[0], b[0]), min(c[0], d[0])), min(max(a[0], b[0]), max(c[0], d[0]))
    return abs(a[1] - c[1]) < near and hi - lo > 1.0


def _rect_pts(l: float, t: float, r: float, b: float) -> list[Pt]:
    return [(l, t), (r, t), (r, b), (l, b)]


def _safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", s) or "task"


def _choose_step(scale: str, pxs: float, min_px: float) -> tuple[int, bool]:
    """Smallest step of ``scale`` whose nominal tick spacing is at least ``min_px``."""
    nominal = {"minutes": 60, "hours": 3600, "days": DAY, "weeks": 7 * DAY,
               "months": 28 * DAY, "years": 365 * DAY}[scale]
    for step in STEPS[scale]:
        if nominal * step * pxs >= min_px:
            return step, True
    return STEPS[scale][-1], False


# ---------------------------------------------------------------------- Gantt


@dataclass
class GanttLayout:
    """Where everything went; returned by :meth:`GanttChart.draw` for inspection."""

    schedule: Schedule
    scale: str
    step: int
    start: _dt.date
    end: _dt.date
    ticks: list[tuple[_dt.date, float]] = field(default_factory=list)
    bars: dict[str, Box] = field(default_factory=dict)
    phases: dict[str, Box] = field(default_factory=dict)
    labels: list[tuple[str, Box]] = field(default_factory=list)
    arrows: dict[tuple[str, str], list[Pt]] = field(default_factory=dict)
    obstacles: list[Box] = field(default_factory=list)
    today_x: Optional[float] = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class _Phase:
    label: str
    depth: int
    index: int
    parent: Optional[int]


class GanttChart:
    """A Gantt chart drawn onto ``diagram`` when :meth:`draw` is called (or on
    leaving a ``with`` block).

    ``origin`` is the top-left corner of the chart; ``width`` the pixel width of
    the date area (ignored when ``day_width`` gives pixels per day). ``scale`` is
    ``"auto"`` or one of ``days``, ``weeks``, ``months``, ``years``. ``start`` /
    ``end`` widen the date range; ``start`` is also the default start of tasks
    with no date and no dependencies. ``palette`` overrides colours by field name.
    """

    ROW = 28.0
    BAR = 16.0
    #: Half-diagonal of a milestone diamond.
    DIAMOND = 10.0
    TIER = 20.0
    MIN_RUN = 10.0

    def __init__(
        self, diagram: Diagram, *, start: Optional[_dt.date] = None, end: Optional[_dt.date] = None,
        today: Optional[_dt.date] = None, scale: str = "auto", width: float = 720.0,
        day_width: Optional[float] = None, origin: Pt = (40.0, 40.0), row_height: float = ROW,
        critical: bool = True, legend: bool = True, label_header: str = "Task",
        label_width: Optional[float] = None, font_size: float = 12.0,
        palette: Optional[dict[str, str]] = None,
    ) -> None:
        for name, value in (("start", start), ("end", end), ("today", today)):
            if value is not None:
                _check_date(value, name)
        if start and end and end < start:
            raise ValueError("end is before start")
        if scale != "auto" and scale not in DATE_SCALES:
            raise ValueError(f"scale must be 'auto' or one of {list(DATE_SCALES)}, got {scale!r}")
        if width <= 0 or (day_width is not None and day_width <= 0):
            raise ValueError("width and day_width must be positive")
        if row_height < self.BAR + 4:
            raise ValueError(f"row_height must be at least {self.BAR + 4}")
        self.d = diagram
        self.start, self.end, self.today = start, end, today
        self.scale, self.width, self.day_width = scale, float(width), day_width
        self.origin = (float(origin[0]), float(origin[1]))
        self.row_height = float(row_height)
        self.show_critical, self.show_legend = bool(critical), bool(legend)
        self.label_header, self.label_width, self.font_size = label_header, label_width, float(font_size)
        self.palette_overrides = dict(palette or {})
        bad = set(self.palette_overrides) - set(Palette.__dataclass_fields__)
        if bad:
            raise ValueError(f"unknown palette fields: {sorted(bad)}")
        self.tasks: list[Task] = []
        self._phases: list[_Phase] = []
        self._rows: list[tuple[str, int]] = []  # ("phase", phase index) or ("task", task index)
        self._stack: list[int] = []
        self._drawn: Optional[GanttLayout] = None
        self._milestones: set[str] = set()
        self._exits: dict[str, float] = {}

    # ------------------------------------------------------------------ model
    def __enter__(self) -> GanttChart:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None and self._drawn is None:
            self.draw()

    @contextmanager
    def phase(self, label: str) -> Iterator[int]:
        """Group the tasks declared inside the block under a phase row with a summary bar."""
        self._check_open()
        idx = len(self._phases)
        self._phases.append(_Phase(label, len(self._stack), idx, self._stack[-1] if self._stack else None))
        self._rows.append(("phase", idx))
        self._stack.append(idx)
        try:
            yield idx
        finally:
            self._stack.pop()

    def task(
        self, id: str, label: Optional[str] = None, *, start: Optional[_dt.date] = None,
        duration: Optional[int] = None, end: Optional[_dt.date] = None,
        after: Union[str, Sequence[str]] = (), lag: int = 0, progress: Optional[float] = None,
        color: Optional[str] = None,
    ) -> str:
        """Add a task; returns its id.

        Give ``duration`` (calendar days, >= 1) or an inclusive ``end`` with a
        ``start``. ``after`` lists finish-to-start predecessors; ``lag`` days are
        added after them (negative for a lead). ``progress`` is 0..1.
        """
        self._check_open()
        if start is not None:
            _check_date(start, "start")
        if end is not None:
            _check_date(end, "end")
            if start is None:
                raise ValueError(f"task {id!r}: end needs a start")
            if duration is not None:
                raise ValueError(f"task {id!r}: give duration or end, not both")
            if end < start:
                raise ValueError(f"task {id!r}: end {end} is before start {start}")
            duration = (end - start).days + 1
        if duration is None:
            raise ValueError(f"task {id!r} needs a duration (or a start and an end)")
        if isinstance(duration, bool) or not isinstance(duration, int) or duration < 1:
            raise ValueError(f"task {id!r}: duration must be a whole number of days >= 1; use milestone() for 0")
        if progress is not None and not (0.0 <= float(progress) <= 1.0):
            raise ValueError(f"task {id!r}: progress must be between 0 and 1, got {progress!r}")
        return self._add(Task(id, label if label is not None else id, duration, start, _deps(after),
                              int(lag), None if progress is None else float(progress), False, None, color))

    def milestone(
        self, id: str, label: Optional[str] = None, *, date: Optional[_dt.date] = None,
        after: Union[str, Sequence[str]] = (), color: Optional[str] = None,
    ) -> str:
        """Add a zero-duration milestone on ``date`` or when its predecessors finish."""
        self._check_open()
        if date is not None:
            _check_date(date, "date")
        return self._add(Task(id, label if label is not None else id, 0, date, _deps(after), 0,
                              None, True, None, color))

    def _add(self, t: Task) -> str:
        if not isinstance(t.id, str) or not t.id:
            raise ValueError("a task id must be a non-empty string")
        if any(x.id == t.id for x in self.tasks):
            raise ScheduleError(f"duplicate task id {t.id!r}")
        t.index = len(self.tasks)
        t.phase = self._stack[-1] if self._stack else None
        self.tasks.append(t)
        self._rows.append(("task", t.index))
        return t.id

    def _check_open(self) -> None:
        if self._drawn is not None:
            raise RuntimeError("this chart has already been drawn")

    def schedule(self) -> Schedule:
        """Schedule the tasks (CPM) without drawing anything."""
        return schedule(self.tasks, self.start)

    def critical_path(self) -> list[str]:
        """Task ids on the critical path, from the computed schedule."""
        return self.schedule().critical_path

    # ------------------------------------------------------------------ drawing
    def draw(self) -> GanttLayout:
        """Lay the chart out and add it to the diagram; returns the layout."""
        self._check_open()
        sched = self.schedule()
        pal = replace(palette_for(self.d.theme), **self.palette_overrides)
        lo_d = min(sched.start, self.start or sched.start)
        hi_d = max(sched.finish, self.end or sched.finish)
        if hi_d <= lo_d:
            hi_d = lo_d + _dt.timedelta(days=1)
        lo, hi = lo_d.toordinal() * DAY, hi_d.toordinal() * DAY
        scale, step = self._pick_scale(lo, hi)
        if scale == "days":
            lo, hi = lo - DAY, hi + DAY
        else:
            lo, hi = _period_floor(lo, scale), _period_ceil(hi, scale)
        if self.day_width is not None:
            pxs = self.day_width / DAY
        else:
            pxs = self.width / (hi - lo)
            if self.scale == "auto":
                scale, step = self._pick_scale(lo, hi, pxs)
            else:
                step = _choose_step(scale, pxs, self._label_room(scale))[0]
        width = (hi - lo) * pxs
        layout = GanttLayout(sched, scale, step, _dt.date.fromordinal(lo // DAY), _dt.date.fromordinal(hi // DAY))

        x0, y0 = self.origin
        fs = self.font_size
        # Row labels first: their widths size the label column.
        row_texts = []
        for kind, idx in self._rows:
            if kind == "phase":
                ph = self._phases[idx]
                txt = self.d.text(ph.label, size=fs, bold=True, max_width=self.label_width)
                row_texts.append((txt, ph.depth * 14.0))
            else:
                t = self.tasks[idx]
                depth = (self._phases[t.phase].depth + 1) if t.phase is not None else 0
                txt = self.d.text(t.label, size=fs, max_width=self.label_width,
                                  italic=t.milestone)
                row_texts.append((txt, depth * 14.0))
        head = self.d.text(f"**{self.label_header}**", size=fs) if self.label_header else None
        col_w = max([w.bounds.width + ind for w, ind in row_texts] + [head.bounds.width if head else 0.0])
        # Percent complete sits in its own column, so no label stands in the arrows' way.
        has_progress = any(t.progress is not None for t in self.tasks)
        done_head = self.d.text("**Done**", size=fs - 1) if has_progress else None
        done_w = max(done_head.bounds.width, _width("100%", fs - 1)) if done_head else 0.0
        done_right = x0 + col_w + 16.0 + done_w
        cx0 = (done_right if done_head else x0 + col_w) + 18.0
        cx1 = cx0 + width

        def X(s: float) -> float:
            return cx0 + (s - lo) * pxs

        upper = _upper_scale(scale)
        tiers = 2 if upper else 1
        rows_top = y0 + tiers * self.TIER
        heights = [max(self.row_height, txt.bounds.height + 8.0) for txt, _ in row_texts]
        tops = [rows_top]
        for h in heights:
            tops.append(tops[-1] + h)
        rows_bottom = tops[-1]

        def add_label(kind: str, txt) -> None:
            b = txt.bounds
            layout.labels.append((kind, (b.x, b.y, b.right, b.bottom)))

        # Header band, tiers and the label column heading.
        self.d.polygon(_rect_pts(x0, y0, cx1, rows_top), style=Style(fill=pal.header, stroke="none"), z=-4)
        if head is not None:
            head.at(x0, y0 + tiers * self.TIER / 2, anchor="left_center")
            add_label("header", head)
        if done_head is not None:
            done_head.at(done_right, y0 + tiers * self.TIER / 2, anchor="right_center")
            add_label("header", done_head)
        ticks = _ticks_s(lo, hi, scale, step)
        layout.ticks = [(_dt.date.fromordinal(s // DAY), X(s)) for s in ticks]
        grid = [f"M {X(s):.2f} {rows_top:.2f} V {rows_bottom:.2f}" for s in ticks]
        lower_y = y0 + (tiers - 1) * self.TIER
        bounds = ticks + ([hi] if not ticks or ticks[-1] != hi else [])
        if not ticks or ticks[0] != lo:
            bounds = [lo] + bounds
        for a, b in zip(bounds, bounds[1:]):
            if a not in ticks:
                continue  # the partial cell before the first tick stays blank
            text = tick_label(a, scale)
            if X(b) - X(a) >= _width(text, fs - 2) + 4:
                txt = self.d.text(text, size=fs - 2)
                txt.at((X(a) + X(b)) / 2, lower_y + self.TIER / 2, anchor="center")
                add_label("tick", txt)
        seps = [f"M {X(s):.2f} {lower_y:.2f} V {rows_top:.2f}" for s in ticks]
        if upper:
            periods = [s for s in _ticks_s(lo, hi, upper, 1)]
            pb = ([lo] if not periods or periods[0] != lo else []) + periods + ([hi] if periods[-1:] != [hi] else [])
            for a, b in zip(pb, pb[1:]):
                text = f"**{_upper_label(a, upper)}**"
                room, w = X(b) - X(a), _width(text, fs - 1)
                if room >= w + 8:
                    txt = self.d.text(text, size=fs - 1)
                    if room >= w + 40:
                        txt.at(X(a) + 6, y0 + self.TIER / 2, anchor="left_center")
                    else:
                        txt.at((X(a) + X(b)) / 2, y0 + self.TIER / 2, anchor="center")
                    add_label("tick", txt)
            seps += [f"M {X(s):.2f} {y0:.2f} V {rows_top:.2f}" for s in periods if s != lo]
            seps.append(f"M {cx0:.2f} {lower_y:.2f} H {cx1:.2f}")
        self.d.path(" ".join(seps + [f"M {cx0:.2f} {y0:.2f} V {rows_bottom:.2f}"]),
                    style=Style(fill="none", stroke=pal.grid, stroke_width=0.8), z=-3)
        if grid:
            self.d.path(" ".join(grid), style=Style(fill="none", stroke=pal.grid, stroke_width=0.6), z=-3)

        # Rows.
        crit = set(sched.critical) if self.show_critical else set()
        anchor_of: dict[str, tuple[float, float, float, float]] = {}  # id -> (left, right, cy, half)
        obstacles: list[tuple[str, Box]] = []
        phase_span: dict[int, list[int]] = {}
        for t in self.tasks:
            p = t.phase
            st = sched.tasks[t.id]
            while p is not None:
                span = phase_span.setdefault(p, [st.start.toordinal(), st.finish.toordinal()])
                span[0] = min(span[0], st.start.toordinal())
                span[1] = max(span[1], st.finish.toordinal())
                p = self._phases[p].parent
        task_row: dict[str, int] = {}
        for r, ((kind, idx), (txt, indent)) in enumerate(zip(self._rows, row_texts)):
            top, bottom = tops[r], tops[r + 1]
            cy = (top + bottom) / 2
            txt.at(x0 + indent, cy, anchor="left_center")
            add_label("row", txt)
            if kind == "phase":
                self.d.polygon(_rect_pts(x0, top, cx1, bottom), style=Style(fill=pal.band, stroke="none"), z=-5)
                span = phase_span.get(idx)
                if span:
                    a, b = X(span[0] * DAY), X(span[1] * DAY)
                    k = min(5.0, (b - a) / 3)
                    pts = [(a, cy - 4), (b, cy - 4), (b, cy + 6), (b - k, cy + 2), (a + k, cy + 2), (a, cy + 6)]
                    self.d.polygon(pts, style=Style(fill=pal.phase, stroke="none"), z=1)
                    box = (a, cy - 4, b, cy + 6)
                    layout.phases[self._phases[idx].label] = box
                    obstacles.append(("phase", box))
                continue
            t = self.tasks[idx]
            task_row[t.id] = r
            st = sched.tasks[t.id]
            is_crit = t.id in crit
            if t.milestone:
                mx, h = X(st.start.toordinal() * DAY), self.DIAMOND
                fill = t.color or (pal.critical if is_crit else pal.milestone)
                self.d.polygon([(mx, cy - h), (mx + h, cy), (mx, cy + h), (mx - h, cy)],
                               style=Style(fill=fill, stroke=fill, stroke_width=1.0), z=2)
                box = (mx - h, cy - h, mx + h, cy + h)
                anchor_of[t.id] = (mx - h, mx, cy, h)
                self._milestones.add(t.id)
                date_txt = self.d.text(f"{_MONTHS[st.start.month - 1]} {st.start.day}", size=fs - 2)
                date_txt.at(mx + h + 5, cy, anchor="left_center")
                add_label("bar", date_txt)
                obstacles.append((t.id, box))
                ob = date_txt.bounds
                obstacles.append(("", (ob.x, ob.y, ob.right, ob.bottom)))
                layout.bars[t.id] = box
                continue
            a, b = X(st.start.toordinal() * DAY), X(st.finish.toordinal() * DAY)
            half = self.BAR / 2
            fill = t.color or (pal.critical_fill if is_crit else pal.bar)
            stroke = pal.critical if is_crit else pal.bar_stroke
            self.d.polygon(_rect_pts(a, cy - half, b, cy + half), style=Style(fill=fill, stroke="none"), z=0)
            if t.progress:
                done = a + (b - a) * t.progress
                self.d.polygon(_rect_pts(a, cy - half, done, cy + half),
                               style=Style(fill=pal.progress, stroke="none", fill_opacity=0.75), z=1)
            self.d.polygon(_rect_pts(a, cy - half, b, cy + half),
                           style=Style(fill="none", stroke=stroke, stroke_width=1.6 if is_crit else 1.0), z=2)
            box = (a, cy - half, b, cy + half)
            layout.bars[t.id] = box
            anchor_of[t.id] = (a, b, cy, half)
            obstacles.append((t.id, box))
            if t.progress is not None:
                pct = self.d.text(f"{round(t.progress * 100)}%", size=fs - 1)
                pct.at(done_right, cy, anchor="right_center")
                add_label("progress", pct)

        # Today line, with its label under the rows.
        if self.today is not None:
            ts = self.today.toordinal() * DAY
            if lo <= ts <= hi:
                tx = X(ts)
                layout.today_x = tx
                self.d.path(f"M {tx:.2f} {y0:.2f} V {rows_bottom + 2:.2f}",
                            style=Style(fill="none", stroke=pal.today, stroke_width=1.4, dash="5,3"), z=-1)
                tt = self.d.text("today", size=fs - 2, color=pal.today, italic=True)
                tt.at(tx, rows_bottom + 4, anchor="top_center")
                add_label("today", tt)

        # Dependency arrows.
        layout.obstacles = [b for _, b in obstacles]
        self._route_all(layout, sched, task_row, tops, anchor_of, obstacles, crit, pal, cx0)

        # Legend.
        if self.show_legend:
            self._legend(layout, pal, cx0, rows_bottom + 26, crit, fs)
        self._drawn = layout
        for w in layout.warnings:
            warnings.warn(w, stacklevel=2)
        return layout

    def _label_room(self, scale: str) -> float:
        return {"days": 20.0, "weeks": 22.0, "months": 30.0, "years": 36.0}[scale] * self.font_size / 12.0

    def _pick_scale(self, lo: int, hi: int, pxs: Optional[float] = None) -> tuple[str, int]:
        if pxs is None:
            pxs = (self.day_width / DAY) if self.day_width else self.width / max(hi - lo, DAY)
        if self.scale != "auto":
            return self.scale, _choose_step(self.scale, pxs, self._label_room(self.scale))[0]
        # The finest scale whose every cell can hold a label (days only while the
        # chart is short enough to read day by day); then the finest with a coarser step.
        for whole in (True, False):
            for scale in DATE_SCALES:
                step, ok = _choose_step(scale, pxs, self._label_room(scale))
                if ok and (step == 1 or not whole) and not (scale == "days" and (hi - lo) > 45 * DAY):
                    return scale, step
        return "years", STEPS["years"][-1]

    # ------------------------------------------------------------------ routing
    def _route_all(self, layout, sched, task_row, tops, anchor_of, obstacles, crit, pal, cx0) -> None:
        used: list[tuple[tuple[Pt, Pt], str, str]] = []
        sources: dict[tuple[str, float], object] = {}
        targets: dict[tuple[str, Pt], object] = {}
        links = set(sched.critical_links) if self.show_critical else set()
        pairs = [(p, t.id) for t in self.tasks for p in dict.fromkeys(t.after)]
        # Critical links first, so they get the cleanest lines.
        pairs.sort(key=lambda ps: (ps not in links,))
        for pred, succ in pairs:
            pts = self._route(pred, succ, task_row, tops, anchor_of, obstacles, used, cx0, layout)
            layout.arrows[(pred, succ)] = pts
            for seg in zip(pts, pts[1:]):
                used.append((seg, pred, succ))
        # Draw the critical links last, so a trunk they share is drawn in their colour.
        for pred, succ in sorted(layout.arrows, key=lambda ps: (ps in links,)):
            pts = layout.arrows[(pred, succ)]
            key = (pred, pts[0][0])
            if key not in sources:
                sources[key] = self.d.point(*pts[0], id=_unique_id(self.d, f"{_safe_id(pred)}-finish"))
            end = (succ, pts[-1])
            if end not in targets:
                targets[end] = self.d.point(*pts[-1], id=_unique_id(self.d, f"{_safe_id(succ)}-start"))
            is_crit = (pred, succ) in links
            self.d.connect(
                sources[key], targets[end], color=pal.critical if is_crit else pal.arrow,
                manual_waypoints=[Point(*p) for p in pts], width=1.6 if is_crit else 1.1, arrow_size=0.8,
                corner_radius=2.0,
                metadata={"dependency": "finish-to-start", "critical": is_crit},
            )

    def _route(self, pred, succ, task_row, tops, anchor_of, obstacles, used, cx0, layout) -> list[Pt]:
        """An orthogonal finish-to-start line from ``pred`` to ``succ``.

        Candidates, in order of preference, each tried first against every mark
        and then with phase summary bars allowed to be crossed: an L (out of the
        predecessor's bottom, along the successor's row into its left end); for
        a milestone, a dog-leg into its top vertex; and a five-segment route that
        runs along the gap between two rows. A candidate is taken if no segment
        enters a bar, a diamond or a label (inflated by 2 px), and no segment runs
        along an earlier arrow that shares neither end. Fan-outs from one
        predecessor reuse its exit, so they share a trunk.
        """
        pl, pr, pcy, ph = anchor_of[pred]
        sl, sr, scy, sh = anchor_of[succ]
        prow, srow = task_row[pred], task_row[succ]
        down = srow > prow
        sgn = 1.0 if down else -1.0
        exit_y = pcy + sgn * ph
        entry = (sl, scy)
        hard = [b for owner, b in obstacles if owner not in (pred, succ)]
        soft = [b for owner, b in obstacles if owner not in (pred, succ, "phase")]

        def clear(a: Pt, b: Pt, blockers) -> bool:
            if any(_seg_hits(a, b, (o[0] - 3, o[1] - 3, o[2] + 3, o[3] + 3)) for o in blockers):
                return False
            return not any(_segs_run_together((a, b), seg) for seg, p, s in used if p != pred and s != succ)

        def path_clear(pts: list[Pt], blockers) -> bool:
            return all(clear(a, b, blockers) for a, b in zip(pts, pts[1:]))

        if pred in self._milestones:  # leave a diamond from its bottom (or top) vertex
            exits = [pr]
        else:
            scan = []
            x = pr - 4.0
            while x >= pl + 2.0 - 1e-9:
                scan.append(round(x, 2))
                x -= 3.0
            # Prefer exits that leave room for the arrowhead before a successor
            # starting right at the finish; then the rest.
            exits = [x for x in scan if x <= pr - self.MIN_RUN] + [x for x in scan if x > pr - self.MIN_RUN]
            exits = exits or [round((pl + pr) / 2, 2)]
        prev = self._exits.get(pred)
        if prev is not None and prev in exits:
            exits.remove(prev)
            exits.insert(0, prev)
        if down:
            channels = [tops[r + 1] for r in range(srow - 1, prow - 1, -1)]
        else:
            channels = [tops[r] for r in range(srow + 1, prow + 1)]
        cols = []
        x = entry[0] - self.MIN_RUN
        while x >= cx0 + 2:
            cols.append(round(x, 2))
            x -= 3.0

        def candidates_simple():
            for x in exits:
                if entry[0] - x >= self.MIN_RUN:
                    yield [(x, exit_y), (x, scy), entry]
            if succ in self._milestones:
                mx, tip = sr, scy - sgn * sh
                if pred not in self._milestones and pl + 2.0 <= mx <= pr:
                    yield [(mx, exit_y), (mx, tip)]  # the diamond hangs under the bar: drop straight in
                for ych in channels:
                    if abs(tip - ych) < self.MIN_RUN:
                        continue
                    for x in exits:
                        if abs(x - mx) < 1.0:
                            yield [(x, exit_y), (mx, tip)]
                        else:
                            yield [(x, exit_y), (x, ych), (mx, ych), (mx, tip)]

        def candidates_channel(blockers):
            for ych in channels:
                for x in exits:
                    if not clear((x, exit_y), (x, ych), blockers):
                        continue
                    for xc in cols:
                        if abs(xc - x) >= 1.0:
                            yield [(x, exit_y), (x, ych), (xc, ych), (xc, scy), entry]

        for blockers in (hard, soft):
            for pts in candidates_simple():
                if path_clear(pts, blockers):
                    return self._took(pred, pts)
        for blockers in (hard, soft):
            for pts in candidates_channel(blockers):
                if path_clear(pts, blockers):
                    return self._took(pred, pts)
        layout.warnings.append(f"gantt: no clear route for dependency {pred} -> {succ}; drawn over other marks")
        x = exits[0]
        if entry[0] - x >= self.MIN_RUN or not channels:
            return self._took(pred, [(x, exit_y), (x, scy), entry])
        xc = entry[0] - self.MIN_RUN
        return self._took(pred, [(x, exit_y), (x, channels[0]), (xc, channels[0]), (xc, scy), entry])

    def _took(self, pred: str, pts: list[Pt]) -> list[Pt]:
        self._exits.setdefault(pred, pts[0][0])
        return pts

    # ------------------------------------------------------------------ legend
    def _legend(self, layout, pal, x, y, crit, fs) -> None:
        entries: list[tuple[str, str]] = [("bar", "Task")]
        if any(t.progress for t in self.tasks):
            entries.append(("progress", "Complete"))
        if crit:
            entries.append(("critical", "Critical path"))
        if any(t.milestone for t in self.tasks):
            entries.append(("milestone", "Milestone"))
        if layout.today_x is not None:
            entries.append(("today", "Today"))
        cy = y + 8
        for kind, text in entries:
            if kind == "milestone":
                h = 6.0
                self.d.polygon([(x + 9, cy - h), (x + 9 + h, cy), (x + 9, cy + h), (x + 9 - h, cy)],
                               style=Style(fill=pal.milestone, stroke="none"), z=2)
            elif kind == "today":
                self.d.path(f"M {x + 9:.2f} {cy - 8:.2f} V {cy + 8:.2f}",
                            style=Style(fill="none", stroke=pal.today, stroke_width=1.4, dash="5,3"), z=2)
            else:
                fill = {"bar": pal.bar, "progress": pal.progress, "critical": pal.critical_fill}[kind]
                stroke = pal.critical if kind == "critical" else pal.bar_stroke
                self.d.polygon(_rect_pts(x, cy - 6, x + 18, cy + 6),
                               style=Style(fill=fill, stroke=stroke, stroke_width=1.0), z=2)
            txt = self.d.text(text, size=fs - 1)
            txt.at(x + 24, cy, anchor="left_center")
            b = txt.bounds
            layout.labels.append(("legend", (b.x, b.y, b.right, b.bottom)))
            x = b.right + 18


def _deps(after: Union[str, Sequence[str]]) -> tuple[str, ...]:
    if isinstance(after, str):
        return (after,)
    return tuple(after)


def _check_date(value, name: str) -> None:
    if isinstance(value, _dt.datetime) or not isinstance(value, _dt.date):
        raise TypeError(f"{name} must be a datetime.date, got {type(value).__name__}")


def _unique_id(d: Diagram, base: str) -> str:
    taken = {s.id for s in d.shapes}
    if base not in taken:
        return base
    k = 2
    while f"{base}-{k}" in taken:
        k += 1
    return f"{base}-{k}"


def _width(text: str, size: float) -> float:
    """Width of ``text`` (markup allowed) as a diagram Text would set it."""
    return measure(text, TextStyle(size=size))[0]


# ---------------------------------------------------------------------- Timeline


@dataclass
class _Event:
    t: int
    label: str
    side: str
    color: Optional[str]
    marker: str
    bold: bool
    index: int


@dataclass
class _Span:
    a: int
    b: int
    label: str
    color: Optional[str]
    index: int


@dataclass
class TimelineLayout:
    """Where everything went; returned by :meth:`Timeline.draw`."""

    scale: str
    step: int
    ticks: list[tuple[int, float]] = field(default_factory=list)
    events: list[tuple[str, float, int, str, Box]] = field(default_factory=list)  # label, x, level, side, box
    stems: list[tuple[Pt, Pt]] = field(default_factory=list)
    labels: list[tuple[str, Box]] = field(default_factory=list)
    spans: list[tuple[str, Box]] = field(default_factory=list)


def pack_levels(items: Sequence[tuple[float, float]], pad: float = 5.0, gap: float = 8.0) -> list[int]:
    """Stack flag labels: item ``i`` is a stem at ``x`` with a label ``w`` wide to its right.

    Returns a level per item (0 nearest the axis). No two labels overlap and no
    stem crosses another item's label: items are placed from the right, each on
    the lowest level whose label ends before every stem already placed on that
    level or higher. Ties in ``x`` keep the earlier item higher.
    """
    order = sorted(range(len(items)), key=lambda i: (items[i][0], i), reverse=True)
    placed: list[tuple[float, int]] = []  # (stem x, level)
    levels = [0] * len(items)
    for i in order:
        x, w = items[i]
        right = x + pad + w + gap
        k = 0
        while True:
            limit = min((px for px, lv in placed if lv >= k), default=math.inf)
            if right <= limit:
                break
            k += 1
        levels[i] = k
        placed.append((x, k))
    return levels


class Timeline:
    """Dated events on a ruler, labels stacked so that none overlap.

    ``event`` adds a marker with a flag label ``above`` or ``below`` the ruler;
    ``span`` shades a period (an outage, a release train) and labels it in a lane
    under the chart. Dates may be ``date`` or naive ``datetime``. ``width`` is
    the ruler length in pixels; ``label_width`` wraps long labels.
    """

    RULER = 22.0
    STEM0 = 14.0
    VGAP = 6.0
    PAD = 5.0

    def __init__(
        self, diagram: Diagram, *, start: Optional[When] = None, end: Optional[When] = None,
        scale: str = "auto", width: float = 900.0, origin: Pt = (40.0, 40.0),
        label_width: float = 170.0, font_size: float = 12.0,
        palette: Optional[dict[str, str]] = None,
    ) -> None:
        if scale != "auto" and scale not in SCALES:
            raise ValueError(f"scale must be 'auto' or one of {list(SCALES)}, got {scale!r}")
        if width <= 0 or label_width <= 0:
            raise ValueError("width and label_width must be positive")
        self.d = diagram
        self.start = None if start is None else to_seconds(start)
        self.end = None if end is None else to_seconds(end)
        if self.start is not None and self.end is not None and self.end <= self.start:
            raise ValueError("end must be after start")
        self.scale, self.width = scale, float(width)
        self.origin = (float(origin[0]), float(origin[1]))
        self.label_width, self.font_size = float(label_width), float(font_size)
        self.palette_overrides = dict(palette or {})
        bad = set(self.palette_overrides) - set(Palette.__dataclass_fields__)
        if bad:
            raise ValueError(f"unknown palette fields: {sorted(bad)}")
        self.events: list[_Event] = []
        self.spans: list[_Span] = []
        self._drawn: Optional[TimelineLayout] = None

    def __enter__(self) -> Timeline:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None and self._drawn is None:
            self.draw()

    def event(self, when: When, label: str, *, side: str = "above", color: Optional[str] = None,
              marker: str = "dot", bold: bool = False) -> int:
        """Add an event; returns its index."""
        if self._drawn is not None:
            raise RuntimeError("this timeline has already been drawn")
        if side not in ("above", "below"):
            raise ValueError(f"side must be 'above' or 'below', got {side!r}")
        if marker not in ("dot", "diamond"):
            raise ValueError(f"marker must be 'dot' or 'diamond', got {marker!r}")
        self.events.append(_Event(to_seconds(when), label, side, color, marker, bold, len(self.events)))
        return len(self.events) - 1

    def span(self, start: When, end: When, label: str, *, color: Optional[str] = None) -> int:
        """Shade the period from ``start`` to ``end`` and label it in a lane below."""
        if self._drawn is not None:
            raise RuntimeError("this timeline has already been drawn")
        a, b = to_seconds(start), to_seconds(end)
        if b <= a:
            raise ValueError(f"span {label!r}: end must be after start")
        self.spans.append(_Span(a, b, label, color, len(self.spans)))
        return len(self.spans) - 1

    def _range(self) -> tuple[int, int]:
        times = [e.t for e in self.events] + [s.a for s in self.spans] + [s.b for s in self.spans]
        if self.start is not None:
            times.append(self.start)
        if self.end is not None:
            times.append(self.end)
        if not times:
            raise ValueError("nothing to draw: add an event or a span first")
        lo, hi = min(times), max(times)
        if hi == lo:
            pad = DAY // 2 if lo % DAY == 0 else 1800
            return lo - pad, hi + pad
        pad = (hi - lo) // 25
        return (self.start if self.start is not None else lo - pad,
                self.end if self.end is not None else hi + pad)

    def draw(self) -> TimelineLayout:
        """Lay the timeline out and add it to the diagram; returns the layout."""
        if self._drawn is not None:
            raise RuntimeError("this timeline has already been drawn")
        pal = replace(palette_for(self.d.theme), **self.palette_overrides)
        lo, hi = self._range()
        pxs = self.width / (hi - lo)
        x0, y0 = self.origin
        fs = self.font_size

        def X(s: float) -> float:
            return x0 + (s - lo) * pxs

        # Ruler ticks: the finest scale whose centred labels do not touch.
        scales = SCALES if self.scale == "auto" else (self.scale,)
        chosen = None
        for scale in scales:
            for step in STEPS[scale]:
                ts = _ticks_s(lo, hi, scale, step)
                if len(ts) > 60:
                    continue
                ws = [_width(tick_label(s, scale, long=True), fs - 2) for s in ts]
                if len(ts) >= 2 and all(X(b) - X(a) >= (wa + wb) / 2 + 10
                                        for a, b, wa, wb in zip(ts, ts[1:], ws, ws[1:])):
                    chosen = (scale, step, ts)
                    break
                if len(ts) < 2 and self.scale != "auto":
                    chosen = (scale, step, ts)
                    break
            if chosen:
                break
        if chosen is None:
            scale = scales[-1]
            chosen = (scale, STEPS[scale][-1], _ticks_s(lo, hi, scale, STEPS[scale][-1]))
        scale, step, ts = chosen
        out = TimelineLayout(scale, step)

        # Measure the event labels, then pack each side.
        texts = []
        for e in self.events:
            label = f"**{e.label}**" if e.bold else e.label
            texts.append(self.d.text(label, size=fs, max_width=self.label_width))
        levels: dict[int, int] = {}
        for side in ("above", "below"):
            idx = [i for i, e in enumerate(self.events) if e.side == side]
            packed = pack_levels([(X(self.events[i].t), texts[i].bounds.width) for i in idx], self.PAD)
            levels.update(zip(idx, packed))

        def offsets(side: str) -> list[float]:
            hs: dict[int, float] = {}
            for i, e in enumerate(self.events):
                if e.side == side:
                    hs[levels[i]] = max(hs.get(levels[i], 0.0), texts[i].bounds.height)
            off = [self.STEM0]
            for k in range(max(hs, default=-1) + 1):
                off.append(off[-1] + hs.get(k, 0.0) + self.VGAP)
            return off

        up, dn = offsets("above"), offsets("below")
        ruler_top = y0 + (up[-1] - self.VGAP if len(up) > 1 else 0.0)
        ruler_bottom = ruler_top + self.RULER
        top_of_content = y0

        # Ruler band, ticks and their labels.
        self.d.polygon(_rect_pts(X(lo), ruler_top, X(hi), ruler_bottom),
                       style=Style(fill=pal.header, stroke=pal.grid, stroke_width=0.8), z=-2)
        marks = []
        for s in ts:
            x = X(s)
            marks.append(f"M {x:.2f} {ruler_top:.2f} v 4 M {x:.2f} {ruler_bottom:.2f} v -4")
            out.ticks.append((s, x))
            text = tick_label(s, scale, long=True)
            half = _width(text, fs - 2) / 2
            if x - half < X(lo) + 2 or x + half > X(hi) - 2:
                continue  # a label that would stick out of the ruler is left off
            txt = self.d.text(text, size=fs - 2)
            txt.at(x, (ruler_top + ruler_bottom) / 2, anchor="center")
            b = txt.bounds
            out.labels.append(("tick", (b.x, b.y, b.right, b.bottom)))
        if marks:
            self.d.path(" ".join(marks), style=Style(fill="none", stroke=pal.grid, stroke_width=0.8), z=-1)

        # Events: marker on the ruler edge, a stem, and the flag label.
        for i, e in enumerate(self.events):
            x, k, txt = X(e.t), levels[i], texts[i]
            colour = e.color or pal.event
            if e.side == "above":
                edge = ruler_top
                label_bottom = ruler_top - up[k]
                txt.at(x + self.PAD, label_bottom, anchor="bottom_left")
                tip = label_bottom - txt.bounds.height
            else:
                edge = ruler_bottom
                label_top = ruler_bottom + dn[k]
                txt.at(x + self.PAD, label_top, anchor="top_left")
                tip = label_top + txt.bounds.height
            self.d.path(f"M {x:.2f} {edge:.2f} V {tip:.2f}",
                        style=Style(fill="none", stroke=colour, stroke_width=1.0), z=0)
            r = 4.0
            if e.marker == "diamond":
                ring = [(x, edge - r - 1), (x + r + 1, edge), (x, edge + r + 1), (x - r - 1, edge)]
            else:
                ring = [(x + r * math.cos(2 * math.pi * j / 20), edge + r * math.sin(2 * math.pi * j / 20))
                        for j in range(20)]
            self.d.polygon(ring, style=Style(fill=colour, stroke=pal.header, stroke_width=1.0), z=2)
            b = txt.bounds
            box = (b.x, b.y, b.right, b.bottom)
            out.events.append((e.label, x, k, e.side, box))
            out.labels.append(("event", box))
            out.stems.append(((x, edge), (x, tip)))

        # Spans: a shaded band behind everything, labelled in lanes under the chart.
        bottom_of_content = ruler_bottom + (dn[-1] - self.VGAP if len(dn) > 1 else 0)
        lane_top = bottom_of_content + 14
        lanes: list[float] = []  # right edge in each lane
        span_texts = [self.d.text(s.label, size=fs - 1) for s in self.spans]
        for s, txt in sorted(zip(self.spans, span_texts), key=lambda p: (p[0].a, p[0].index)):
            a, b = X(s.a), X(s.b)
            right = max(b, a + 4 + txt.bounds.width) + 10
            lane = next((j for j, r in enumerate(lanes) if r <= a), None)
            if lane is None:
                lanes.append(right)
                lane = len(lanes) - 1
            else:
                lanes[lane] = right
            lane_h = txt.bounds.height + 12
            ly = lane_top + lane * lane_h
            colour = s.color or pal.span
            self.d.polygon(_rect_pts(a, top_of_content - 6, b, ly),
                           style=Style(fill=colour, stroke="none", fill_opacity=0.12), z=-5)
            self.d.polygon(_rect_pts(a, ly, b, ly + 4), style=Style(fill=colour, stroke="none"), z=1)
            txt.at(a + 2, ly + 6, anchor="top_left")
            tb = txt.bounds
            out.labels.append(("span", (tb.x, tb.y, tb.right, tb.bottom)))
            out.spans.append((s.label, (a, ly, b, ly + 4)))
        self._drawn = out
        return out


__all__ = [
    "DATE_SCALES",
    "GanttChart",
    "GanttLayout",
    "Palette",
    "SCALES",
    "Schedule",
    "ScheduleError",
    "Scheduled",
    "Task",
    "Timeline",
    "TimelineLayout",
    "boxes_overlap",
    "date_ticks",
    "pack_levels",
    "palette_for",
    "schedule",
    "tick_label",
    "to_seconds",
]
