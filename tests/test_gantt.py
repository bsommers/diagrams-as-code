"""Gantt and timeline kit: scheduling, critical path, date ticks, label packing, routing, output."""
from __future__ import annotations

import importlib.util
import os
import random
import subprocess
import sys
import warnings
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.audit import audit_findings
from diagrams_as_code.gantt import (
    GanttChart,
    ScheduleError,
    Task,
    Timeline,
    boxes_overlap,
    date_ticks,
    pack_levels,
    palette_for,
    schedule,
    tick_label,
    to_seconds,
)
from diagrams_as_code.output import render_all
from diagrams_as_code.text import TextStyle, measure
from diagrams_as_code.theme import get_theme

REPO = Path(__file__).resolve().parent.parent
EXAMPLES = sorted((REPO / "examples" / "project_management").glob("*.py"))
D0 = date(2026, 3, 2)  # a Monday


def T(id, dur, after=(), start=None, lag=0):
    return Task(id, id, dur, start, tuple(after), lag)


# ------------------------------------------------------------------ scheduling


def test_chain_dates_are_finish_to_start_with_exclusive_finish():
    s = schedule([T("a", 3, start=D0), T("b", 2, ["a"]), T("c", 1, ["b"])])
    assert s.tasks["a"].start == D0 and s.tasks["a"].finish == D0 + timedelta(3)
    assert s.tasks["b"].start == s.tasks["a"].finish
    assert s.tasks["c"].finish == D0 + timedelta(6)
    assert s.start == D0 and s.finish == D0 + timedelta(6)
    assert s.tasks["b"].duration == 2


def test_lag_and_lead_shift_the_successor():
    s = schedule([T("a", 3, start=D0), T("b", 2, ["a"], lag=2), T("c", 2, ["a"], lag=-1)])
    assert s.tasks["b"].start == D0 + timedelta(5)
    assert s.tasks["c"].start == D0 + timedelta(2)


def test_start_is_a_start_no_earlier_than_constraint():
    s = schedule([T("a", 2, start=D0), T("b", 2, ["a"], start=D0 + timedelta(5)), T("c", 2, ["a"], start=D0)])
    assert s.tasks["b"].start == D0 + timedelta(5)  # later than the predecessor: the constraint wins
    assert s.tasks["c"].start == D0 + timedelta(2)  # earlier: the dependency wins


def test_project_start_is_the_default_start():
    s = schedule([T("a", 2), T("b", 1)], project_start=D0)
    assert s.tasks["a"].start == s.tasks["b"].start == D0


def test_slack_and_critical_tasks():
    # a(5) -> c(2); b(3) -> c. b has 2 days of slack.
    s = schedule([T("a", 5, start=D0), T("b", 3, start=D0), T("c", 2, ["a", "b"])])
    assert s.tasks["b"].slack == 2 and not s.tasks["b"].critical
    assert s.tasks["b"].latest_start == D0 + timedelta(2)
    assert s.critical == ["a", "c"]
    assert s.critical_path == ["a", "c"]
    assert s.critical_links == (("a", "c"),)


def test_critical_path_is_the_longest_path():
    #     /- b(4) -\
    # a(1)          e(1)      the longest path is a-b-e (6) not a-c-d-e (5)
    #     \- c(1) - d(2) /
    tasks = [T("a", 1, start=D0), T("b", 4, ["a"]), T("c", 1, ["a"]), T("d", 2, ["c"]), T("e", 1, ["b", "d"])]
    s = schedule(tasks)
    assert s.critical_path == ["a", "b", "e"]
    assert s.tasks["c"].slack == s.tasks["d"].slack == 1
    assert (s.finish - s.start).days == 6


def test_tied_longest_paths_are_all_critical_and_ordered():
    tasks = [T("a", 1, start=D0), T("x", 3, ["a"]), T("y", 2, ["a"]), T("y2", 1, ["y"]), T("z", 1, ["x", "y2"])]
    s = schedule(tasks)
    assert s.critical == ["a", "x", "y", "y2", "z"]
    assert s.paths() == [["a", "x", "z"], ["a", "y", "y2", "z"]]
    assert s.critical_path == ["a", "x", "z"]  # declaration order breaks the tie


def test_tie_break_follows_declaration_not_ids():
    tasks = [T("start", 1, start=D0), T("zeta", 2, ["start"]), T("alpha", 2, ["start"]), T("end", 1, ["zeta", "alpha"])]
    assert schedule(tasks).critical_path == ["start", "zeta", "end"]


def test_two_independent_critical_roots():
    s = schedule([T("a", 3, start=D0), T("b", 3, start=D0)])
    assert s.paths() == [["a"], ["b"]]


def test_milestones_have_zero_duration_and_can_be_critical():
    tasks = [T("a", 4, start=D0), T("m", 0, ["a"]), T("b", 2, ["m"])]
    s = schedule(tasks)
    assert s.tasks["m"].start == s.tasks["m"].finish == D0 + timedelta(4)
    assert s.critical_path == ["a", "m", "b"]


def test_chart_schedule_matches_function():
    d = Diagram("g", theme="paper")
    g = GanttChart(d)
    g.task("a", start=D0, duration=3)
    g.task("b", after="a", end=D0 + timedelta(9), start=D0 + timedelta(5))  # inclusive end: 5 days
    assert g.schedule().tasks["b"].duration == 5
    # b's start constraint (day 5) is later than a's finish (day 3): a has two days of slack.
    assert g.schedule().tasks["a"].slack == 2
    assert g.critical_path() == ["b"]


@pytest.mark.parametrize(
    "tasks,match",
    [
        ([T("a", 1, start=D0), T("b", 1, ["a", "c"]), T("c", 1, ["b"])], r"cycle: (b -> c -> b|c -> b -> c)"),
        ([T("a", 1, ["a"])], r"cycle: a -> a"),
        ([T("a", 1, start=D0), T("b", 1, ["nope"])], r"unknown task 'nope'"),
        ([T("a", 1, start=D0), T("a", 1, start=D0)], r"duplicate task id 'a'"),
        ([T("a", 1)], r"no start date and no dependencies"),
        ([], r"nothing to schedule"),
    ],
)
def test_schedule_errors(tasks, match):
    with pytest.raises(ScheduleError, match=match):
        schedule(tasks)


def test_cycle_reported_through_chart():
    d = Diagram("g", theme="paper")
    g = GanttChart(d)
    g.task("a", start=D0, duration=1, after="c")
    g.task("b", duration=1, after="a")
    g.task("c", duration=1, after="b")
    with pytest.raises(ScheduleError, match="cycle"):
        g.draw()


@pytest.mark.parametrize(
    "kwargs,exc,match",
    [
        ({"duration": 0, "start": D0}, ValueError, "use milestone"),
        ({"duration": 1.5, "start": D0}, ValueError, "whole number"),
        ({"start": D0}, ValueError, "needs a duration"),
        ({"end": D0}, ValueError, "end needs a start"),
        ({"start": D0, "end": D0 - timedelta(1)}, ValueError, "before start"),
        ({"start": D0, "end": D0, "duration": 1}, ValueError, "not both"),
        ({"start": D0, "duration": 1, "progress": 1.5}, ValueError, "progress"),
        ({"start": datetime(2026, 3, 2, 9), "duration": 1}, TypeError, "datetime.date"),
        ({"start": "2026-03-02", "duration": 1}, TypeError, "datetime.date"),
    ],
)
def test_task_argument_errors(kwargs, exc, match):
    g = GanttChart(Diagram("g", theme="paper"))
    with pytest.raises(exc, match=match):
        g.task("a", **kwargs)


def test_chart_argument_errors():
    d = Diagram("g", theme="paper")
    with pytest.raises(ValueError, match="scale"):
        GanttChart(d, scale="hours")
    with pytest.raises(ValueError, match="end is before start"):
        GanttChart(d, start=D0, end=D0 - timedelta(1))
    with pytest.raises(ValueError, match="palette"):
        GanttChart(d, palette={"nope": "#fff"})
    g = GanttChart(d)
    g.task("a", start=D0, duration=1)
    with pytest.raises(ScheduleError, match="duplicate"):
        g.task("a", start=D0, duration=1)
    g.draw()
    with pytest.raises(RuntimeError, match="already been drawn"):
        g.task("b", start=D0, duration=1)


# ------------------------------------------------------------------ ticks


def test_week_ticks_are_mondays():
    ticks = date_ticks(date(2026, 3, 4), date(2026, 4, 8), "weeks")
    assert ticks[0] == date(2026, 3, 9) and all(t.weekday() == 0 for t in ticks)
    assert [(b - a).days for a, b in zip(ticks, ticks[1:])] == [7] * (len(ticks) - 1)
    two = date_ticks(date(2026, 1, 1), date(2026, 6, 1), "weeks", 2)
    assert all((b - a).days == 14 for a, b in zip(two, two[1:]))
    # A two-week step keeps an absolute parity, so it does not depend on the range start.
    assert set(date_ticks(date(2026, 1, 8), date(2026, 6, 1), "weeks", 2)) <= set(two)


def test_month_quarter_year_ticks():
    assert date_ticks(date(2026, 1, 15), date(2026, 5, 1), "months") == [
        date(2026, 2, 1), date(2026, 3, 1), date(2026, 4, 1), date(2026, 5, 1)]
    assert date_ticks(date(2025, 11, 1), date(2026, 12, 31), "months", 3) == [
        date(2026, 1, 1), date(2026, 4, 1), date(2026, 7, 1), date(2026, 10, 1)]
    assert date_ticks(date(2019, 6, 1), date(2031, 1, 1), "years", 5) == [date(2020, 1, 1), date(2025, 1, 1), date(2030, 1, 1)]
    assert date_ticks(date(2026, 3, 30), date(2026, 4, 2), "days") == [
        date(2026, 3, 30), date(2026, 3, 31), date(2026, 4, 1), date(2026, 4, 2)]


def test_time_ticks_and_labels():
    ticks = date_ticks(datetime(2026, 4, 14, 13, 58), datetime(2026, 4, 14, 14, 31), "minutes", 15)
    assert ticks == [datetime(2026, 4, 14, 14, 0), datetime(2026, 4, 14, 14, 15), datetime(2026, 4, 14, 14, 30)]
    hours = date_ticks(datetime(2026, 4, 14, 22, 0), datetime(2026, 4, 15, 2, 0), "hours", 2)
    assert hours == [datetime(2026, 4, 14, 22), datetime(2026, 4, 15, 0), datetime(2026, 4, 15, 2)]
    assert tick_label(to_seconds(hours[1]), "hours", long=True) == "Apr 15"
    assert tick_label(to_seconds(hours[0]), "hours") == "22:00"
    assert tick_label(to_seconds(date(2026, 3, 9)), "weeks") == "9"
    assert tick_label(to_seconds(date(2026, 3, 9)), "days", long=True) == "Mar 9"
    assert tick_label(to_seconds(date(2026, 3, 1)), "months", long=True) == "Mar 2026"
    assert tick_label(to_seconds(date(2026, 1, 1)), "years") == "2026"


def test_tick_errors_and_time_conversion():
    with pytest.raises(ValueError, match="scale"):
        date_ticks(D0, D0, "fortnights")
    with pytest.raises(ValueError, match="step"):
        date_ticks(D0, D0, "days", 0)
    with pytest.raises(ValueError, match="timezone"):
        to_seconds(datetime(2026, 1, 1, tzinfo=timezone.utc))
    with pytest.raises(TypeError):
        to_seconds("2026-01-01")
    assert to_seconds(datetime(2026, 1, 1, 0, 1)) - to_seconds(date(2026, 1, 1)) == 60


def _chart(days: int, **kw) -> GanttChart:
    g = GanttChart(Diagram("g", theme="paper"), **kw)
    g.task("a", start=D0, duration=days)
    return g


@pytest.mark.parametrize("days,scale", [(10, "days"), (40, "weeks"), (300, "months"), (3000, "years")])
def test_auto_scale_follows_the_span(days, scale):
    assert _chart(days).draw().scale == scale


def test_forced_scale_and_snapped_range():
    lay = _chart(40, scale="months").draw()
    assert lay.scale == "months" and lay.start.day == 1 and lay.end.day == 1
    lay = _chart(20, scale="weeks").draw()
    assert lay.start.weekday() == 0 and lay.end.weekday() == 0
    assert all(t.weekday() == 0 for t, _ in lay.ticks)


def test_day_width_fixes_pixels_per_day():
    lay = _chart(14, day_width=30).draw()
    xs = [x for _, x in lay.ticks]
    assert all(b - a == pytest.approx(30) for a, b in zip(xs, xs[1:]))


def test_header_labels_never_overlap_at_any_density():
    for days in (3, 9, 30, 70, 200, 500, 1400):
        for width in (300, 720, 1600):
            lay = _chart(days, width=width).draw()
            ticks = [b for kind, b in lay.labels if kind == "tick"]
            assert ticks, (days, width)
            assert not any(boxes_overlap(a, b) for i, a in enumerate(ticks) for b in ticks[i + 1:]), (days, width)


# ------------------------------------------------------------------ Gantt layout


def _project(diag: Diagram) -> GanttChart:
    g = GanttChart(diag, today=D0 + timedelta(9))
    with g.phase("Plan"):
        g.task("a", "Scope", start=D0, duration=4, progress=1.0)
        g.task("b", "Design $\\frac{1}{2}$", after="a", duration=6, progress=0.5)
        g.task("c", "Estimate", after="a", duration=2)
    g.milestone("m", "Go", after=["b", "c"])
    with g.phase("Do"):
        g.task("d", "Build", after="m", duration=10)
        g.task("e", "Docs", after="m", duration=3)
        g.task("f", "Test", after=["d", "e"], duration=4)
    g.milestone("z", "Done", after="f")
    return g


def _labels_disjoint(boxes):
    return not any(boxes_overlap(a, b) for i, a in enumerate(boxes) for b in boxes[i + 1:])


def _arrow_problems(lay) -> list[str]:
    bad = []
    label_boxes = [b for _, b in lay.labels]
    for (p, s), pts in lay.arrows.items():
        segs = list(zip(pts, pts[1:]))
        if any(a[0] != b[0] and a[1] != b[1] for a, b in segs):
            bad.append(f"{p}->{s} not orthogonal")
        others = [b for k, b in lay.bars.items() if k not in (p, s)]
        for a, b in segs:
            for box in label_boxes + others:
                if (max(a[0], b[0]) > box[0] and min(a[0], b[0]) < box[2]
                        and max(a[1], b[1]) > box[1] and min(a[1], b[1]) < box[3]):
                    bad.append(f"{p}->{s} crosses {box}")
    return bad


def test_project_layout_is_clean():
    d = Diagram("g", theme="pastel_light")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        lay = _project(d).draw()
    assert _labels_disjoint([b for _, b in lay.labels])
    assert _arrow_problems(lay) == []
    assert lay.warnings == []
    assert not audit_findings(d), [str(f) for f in audit_findings(d)]
    assert set(lay.schedule.critical_path) == {"a", "b", "m", "d", "f", "z"}


def test_arrows_leave_the_predecessor_and_enter_the_successor():
    lay = _project(Diagram("g", theme="paper")).draw()
    for (p, s), pts in lay.arrows.items():
        pb, sb = lay.bars[p], lay.bars[s]
        assert pb[0] <= pts[0][0] <= pb[2] and pts[0][1] in (pb[1], pb[3])
        end = pts[-1]
        assert sb[0] <= end[0] <= sb[2] and sb[1] <= end[1] <= sb[3]
        # Arrives along the successor's row from the left, or down into a diamond's top.
        assert pts[-2][0] < end[0] or (pts[-2][0] == end[0] and pts[-2][1] < end[1])


def test_bars_follow_the_schedule_and_today_line():
    lay = _project(Diagram("g", theme="paper")).draw()
    xs = {t: x for t, x in lay.ticks}
    sched = lay.schedule.tasks
    # The day width is constant, so a bar's width is proportional to its duration.
    widths = {k: lay.bars[k][2] - lay.bars[k][0] for k in "abcdef"}
    per_day = widths["a"] / sched["a"].duration
    for k, w in widths.items():
        assert w == pytest.approx(per_day * sched[k].duration)
    assert lay.today_x == pytest.approx(lay.bars["a"][0] + 9 * per_day)
    assert xs  # the axis has ticks


def test_critical_links_are_drawn_in_the_critical_colour():
    d = Diagram("g", theme="paper")
    lay = _project(d).draw()
    pal = palette_for(d.theme)
    critical = set(lay.schedule.critical_links)
    for e in d.edges:
        key = next(k for k, v in lay.arrows.items() if list(v) == [(p.x, p.y) for p in e.manual_waypoints])
        assert (e.color == pal.critical) == (key in critical)
    # Critical arrows are drawn last, so a shared trunk shows the critical colour.
    flags = [e.metadata["critical"] for e in d.edges]
    assert flags == sorted(flags)


def test_critical_highlighting_can_be_switched_off():
    d = Diagram("g", theme="paper")
    g = _project(d)
    g.show_critical = False
    g.draw()
    assert all(not e.metadata["critical"] for e in d.edges)


def test_upward_dependency_routes_cleanly():
    d = Diagram("g", theme="paper")
    g = GanttChart(d)
    g.task("late", "Depends on a later row", after="first", duration=3)
    g.task("pad", "Unrelated", start=D0, duration=12)
    g.task("first", "Declared last", start=D0, duration=4)
    lay = g.draw()
    pts = lay.arrows[("first", "late")]
    assert pts[0][1] == lay.bars["first"][1]  # leaves from the top
    assert _arrow_problems(lay) == [] and lay.warnings == []


def test_random_projects_route_without_crossing_labels():
    rng = random.Random(7)
    for trial in range(12):
        d = Diagram("g", theme="paper")
        g = GanttChart(d, legend=False)
        ids = []
        for i in range(14):
            deps = rng.sample(ids, k=min(len(ids), rng.choice((0, 1, 1, 2))))
            kw = {"after": deps} if deps else {"start": D0 + timedelta(rng.randrange(6))}
            if rng.random() < 0.15 and deps:
                g.milestone(f"m{i}", f"Gate {i}", **kw)
            else:
                g.task(f"t{i}", f"Task number {i}", duration=rng.randrange(1, 9),
                       progress=rng.choice((None, 0.3, 1.0)), **kw)
            ids.append(ids_last(g))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            lay = g.draw()
        assert _labels_disjoint([b for _, b in lay.labels]), trial
        routed = {k: v for k, v in lay.arrows.items()
                  if not any(f"{k[0]} -> {k[1]}" in w for w in lay.warnings)}
        lay.arrows = routed
        assert _arrow_problems(lay) == [], trial


def ids_last(g: GanttChart) -> str:
    return g.tasks[-1].id


def test_math_labels_are_measured_like_other_text():
    d = Diagram("g", theme="paper")
    lay = _project(d).draw()
    texts = [s for s in d.shapes if getattr(s, "kind", "") == "text" and "frac" in (s.label or "")]
    assert len(texts) == 1
    w, h = measure(texts[0].label, TextStyle(size=12.0))
    assert texts[0].bounds.width == pytest.approx(w) and texts[0].bounds.height == pytest.approx(h)
    assert "<path" in d.render_svg()
    assert lay


def test_dark_theme_palette_uses_theme_colours():
    dark, light = get_theme("dracula"), get_theme("paper")
    assert palette_for(dark).bar == dark.node_fill and palette_for(dark).grid == dark.group_stroke
    assert palette_for(light).bar.startswith("#C9")
    d = Diagram("g", theme="dracula")
    _project(d).draw()
    assert dark.node_fill in d.render_svg()


def test_palette_override():
    d = Diagram("g", theme="paper")
    g = GanttChart(d, palette={"critical": "#123456"})
    g.task("a", start=D0, duration=2)
    g.draw()
    assert "#123456" in d.render_svg()


def test_context_manager_draws_on_exit():
    d = Diagram("g", theme="paper")
    with GanttChart(d) as g:
        g.task("a", start=D0, duration=2)
    assert g._drawn is not None and d.render_svg().count("<path") > 0


# ------------------------------------------------------------------ Timeline


def test_pack_levels_basics():
    assert pack_levels([(0, 50), (100, 50), (200, 50)]) == [0, 0, 0]
    # Crowded: the earliest event climbs highest (a staircase down to the right).
    assert pack_levels([(0, 100), (20, 100), (40, 100)]) == [2, 1, 0]
    # Ties keep the earlier item higher.
    assert pack_levels([(10, 30), (10, 30)]) == [1, 0]
    assert pack_levels([]) == []


def _check_flags(items, levels, pad=5.0, gap=8.0):
    """Labels on one level do not overlap; no stem crosses a label below its own level."""
    boxes = [(x + pad, lv, x + pad + w) for (x, w), lv in zip(items, levels)]
    for i, (l1, lv1, r1) in enumerate(boxes):
        for j, (l2, lv2, r2) in enumerate(boxes):
            if i != j and lv1 == lv2:
                assert r1 + gap <= l2 or r2 + gap <= l1
            # Stem j runs from the axis up to level lv2; a label on a level at or below it must not cover it.
            if i != j and lv1 <= lv2:
                x = items[j][0]
                assert not (l1 - pad < x < r1 + gap), (i, j)


def test_pack_levels_random_property():
    rng = random.Random(11)
    for _ in range(200):
        n = rng.randrange(1, 25)
        items = [(rng.uniform(0, 600), rng.uniform(10, 160)) for _ in range(n)]
        _check_flags(items, pack_levels(items))


def _timeline(theme="paper", **kw) -> tuple[Diagram, Timeline]:
    d = Diagram("t", theme=theme)
    return d, Timeline(d, **kw)


def test_timeline_labels_and_stems_never_collide():
    rng = random.Random(3)
    for trial in range(10):
        d, t = _timeline(width=700)
        base = datetime(2026, 4, 14, 12, 0)
        for i in range(18):
            when = base + timedelta(minutes=rng.randrange(0, 240))
            t.event(when, f"Event {i} " + "word " * rng.randrange(0, 6), side=rng.choice(("above", "below")))
        for i in range(3):
            a = base + timedelta(minutes=rng.randrange(0, 200))
            t.span(a, a + timedelta(minutes=rng.randrange(10, 80)), f"Window {i}")
        lay = t.draw()
        boxes = [b for _, b in lay.labels]
        assert _labels_disjoint(boxes), trial
        for (x, y0), (_, y1) in lay.stems:
            for b in boxes:
                assert not (b[0] < x < b[2] and min(y0, y1) < b[3] and max(y0, y1) > b[1]), trial
        assert not audit_findings(d), [str(f) for f in audit_findings(d)]


def test_timeline_scales_by_span():
    def scale_of(a, b):
        d, t = _timeline(width=900)
        t.event(a, "a")
        t.event(b, "b")
        return t.draw().scale

    assert scale_of(datetime(2026, 1, 1, 9), datetime(2026, 1, 1, 10)) == "minutes"
    assert scale_of(datetime(2026, 1, 1, 0), datetime(2026, 1, 2, 12)) == "hours"
    assert scale_of(date(2026, 1, 1), date(2026, 1, 20)) == "days"
    assert scale_of(date(2026, 1, 1), date(2026, 9, 1)) in ("weeks", "months")
    assert scale_of(date(2020, 1, 1), date(2026, 1, 1)) in ("months", "years")
    assert scale_of(date(1900, 1, 1), date(2026, 1, 1)) == "years"


def test_timeline_single_event_and_errors():
    d, t = _timeline()
    t.event(date(2026, 1, 1), "only")
    assert t.draw().ticks
    d, t = _timeline()
    with pytest.raises(ValueError, match="nothing to draw"):
        t.draw()
    with pytest.raises(ValueError, match="side"):
        t.event(D0, "x", side="left")
    with pytest.raises(ValueError, match="marker"):
        t.event(D0, "x", marker="star")
    with pytest.raises(ValueError, match="end must be after start"):
        t.span(D0, D0, "x")
    with pytest.raises(ValueError, match="timezone"):
        t.event(datetime(2026, 1, 1, tzinfo=timezone.utc), "x")
    with pytest.raises(ValueError, match="scale"):
        Timeline(d, scale="eons")
    with pytest.raises(ValueError, match="end must be after start"):
        Timeline(d, start=D0, end=D0)


def test_timeline_explicit_range_and_scale():
    d, t = _timeline(start=date(2026, 1, 1), end=date(2026, 12, 31), scale="months")
    t.event(date(2026, 6, 15), "mid")
    lay = t.draw()
    assert lay.scale == "months"
    assert [s for s, _ in lay.ticks][0] == to_seconds(date(2026, 1, 1))


def test_span_lanes_do_not_overlap():
    d, t = _timeline(width=600)
    for i in range(6):
        a = date(2026, 1, 1) + timedelta(days=10 * i)
        t.span(a, a + timedelta(days=25), f"Overlapping span {i}")
    lay = t.draw()
    spans = [b for _, b in lay.spans]
    for i, a in enumerate(spans):
        for b in spans[i + 1:]:
            if a[1] == b[1]:  # same lane
                assert a[2] <= b[0] or b[2] <= a[0]
    assert _labels_disjoint([b for _, b in lay.labels])


# ------------------------------------------------------------------ output and determinism


def test_svg_pdf_png_outputs(tmp_path):
    d = Diagram("g", theme="pastel_light")
    _project(d).draw()
    out = render_all(d, tmp_path, "gantt", formats=("svg", "pdf", "bom"))
    assert ET.fromstring(out["svg"].read_text(encoding="utf-8")).tag.endswith("svg")
    assert out["pdf"].read_bytes().startswith(b"%PDF-")
    pytest.importorskip("resvg_py")
    png = render_all(d, tmp_path, "gantt", formats=("png",))["png"]
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_is_byte_stable_within_a_process():
    def svg():
        d = Diagram("g", theme="paper")
        _project(d).draw()
        return d.render_svg()

    assert svg() == svg()


@pytest.mark.parametrize("script", EXAMPLES, ids=lambda p: p.stem)
def test_examples_are_byte_stable_across_processes(script, tmp_path):
    outs = []
    for seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        subprocess.run([sys.executable, str(script), str(tmp_path / seed)], check=True, env=env, cwd=REPO)
        outs.append((tmp_path / seed / f"{script.stem}.svg").read_bytes())
    assert outs[0] == outs[1]


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"_pm_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gantt_and_timeline_examples_come_first():
    stems = [p.stem for p in EXAMPLES]
    assert stems[:3] == ["01_gantt_critical_path", "02_release_train_timeline", "03_incident_timeline"]
    assert stems == sorted(stems)


@pytest.mark.parametrize("script", EXAMPLES, ids=lambda p: p.stem)
def test_example_builds_cleanly(script, tmp_path):
    module = _load(script)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        diagram = module.diagram()
        svg_path = module.build_diagram(tmp_path)
    assert ET.fromstring(svg_path.read_text(encoding="utf-8")).tag.endswith("svg")
    assert not audit_findings(diagram), [str(f) for f in audit_findings(diagram)]
    assert any(s.kind == "caption" for s in diagram.shapes)


@pytest.mark.parametrize("script", EXAMPLES, ids=lambda p: p.stem)
def test_committed_output_matches_the_script(script):
    committed = script.with_suffix(".svg")
    assert committed.exists(), f"run `uv run python {script.relative_to(REPO)}`"
    assert committed.read_text(encoding="utf-8") == _load(script).diagram().render_svg()
