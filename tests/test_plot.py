"""Plot kit: tick maths, data-to-pixel mapping, clipping, curves, regions, fields, ODEs."""
from __future__ import annotations

import math
import re

import pytest

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.plot import Plot, nice_step, ticks


def _plot(**kw):
    d = Diagram("plot", theme="paper")
    kw.setdefault("x", (0, 4))
    kw.setdefault("y", (0, 4))
    kw.setdefault("origin", (100, 300))
    kw.setdefault("size", (400, 200))
    return d, Plot(d, **kw)


def _path_data(d: Diagram) -> list[str]:
    svg = d.render_svg()
    return re.findall(r'<path[^>]* d="([^"]*)"', svg)


# ------------------------------------------------------------------ ticks


@pytest.mark.parametrize("span,expected", [(10, 2), (1, 0.2), (100, 20), (0.6, 0.1), (7, 2), (60, 10)])
def test_nice_step_is_1_2_5_multiple(span, expected):
    assert nice_step(span) == pytest.approx(expected)


def test_nice_step_degenerate_span():
    assert nice_step(0) == 1.0 and nice_step(-3) == 1.0


def test_ticks_cover_window_on_multiples():
    assert ticks(0, 10, 2) == [0, 2, 4, 6, 8, 10]
    assert ticks(-1, 1, 0.5) == [-1, -0.5, 0, 0.5, 1]
    assert ticks(0.5, 3.5, 1) == [1, 2, 3]
    t = ticks(0, 7)
    assert all(0 <= v <= 7 for v in t) and len(t) >= 3


# ------------------------------------------------------------------ mapping / validation


def test_px_linear_corners():
    _, p = _plot()
    assert p.px(0, 0) == pytest.approx((100, 300))
    assert p.px(4, 4) == pytest.approx((500, 100))
    assert p.px(4, 0) == pytest.approx((500, 300))
    assert p.px(0, 4) == pytest.approx((100, 100))
    assert p.px(2, 1) == pytest.approx((300, 250))


def test_px_log_axes():
    _, p = _plot(x=(1, 100), y=(1, 1000), xscale="log", yscale="log")
    assert p.px(1, 1) == pytest.approx((100, 300))
    assert p.px(100, 1000) == pytest.approx((500, 100))
    assert p.px(10, 10) == pytest.approx((300, 300 - 200 / 3))


@pytest.mark.parametrize("kw", [
    {"x": (1, 1)}, {"x": (2, 1)}, {"y": (3, 0)},
    {"xscale": "sqrt"}, {"yscale": "bad"},
    {"x": (0, 10), "xscale": "log"}, {"y": (-1, 10), "yscale": "log"},
])
def test_constructor_validation(kw):
    d = Diagram("v", theme="paper")
    args = {"x": (0, 1), "y": (0, 1)}
    args.update(kw)
    with pytest.raises(ValueError):
        Plot(d, **args)


# ------------------------------------------------------------------ clipping / runs


def test_clip_segment_crossing_window():
    _, p = _plot()
    a, b = p._clip_segment((-2, 2), (6, 2))
    assert a == pytest.approx((0, 2)) and b == pytest.approx((4, 2))
    a, b = p._clip_segment((-1, -1), (5, 5))
    assert a == pytest.approx((0, 0)) and b == pytest.approx((4, 4))


def test_clip_segment_inside_and_outside():
    _, p = _plot()
    assert p._clip_segment((1, 1), (2, 3)) == ((1, 1), (2, 3))
    assert p._clip_segment((5, 0), (6, 4)) is None
    assert p._clip_segment((-1, 5), (5, 6)) is None
    assert p._clip_segment((-1, 0.5), (-1, 3)) is None  # parallel, outside


def test_runs_none_breaks_curve():
    _, p = _plot()
    runs = p._runs([(0, 0), (1, 1), None, (2, 2), (3, 3)])
    assert runs == [[(0, 0), (1, 1)], [(2, 2), (3, 3)]]


def test_runs_nonfinite_breaks_and_isolated_points_dropped():
    _, p = _plot()
    runs = p._runs([(0, 0), (1, 1), (float("nan"), 1), (2, 2), None, (3, 3)])
    assert runs == [[(0, 0), (1, 1)]]


def test_runs_clips_leaving_segment():
    _, p = _plot()
    runs = p._runs([(1, 1), (2, 2), (6, 6)])
    assert len(runs) == 1
    assert runs[0][0] == (1, 1) and runs[0][-1] == pytest.approx((4, 4))


def test_runs_fully_outside_segment_dropped():
    _, p = _plot()
    assert p._runs([(5, 5), (6, 6), (7, 7)]) == []
    runs = p._runs([(1, 1), (2, 2), (6, 9), (7, 9), (3, 3), (2, 1)])
    assert all(all(0 <= x <= 4 and 0 <= y <= 4 for x, y in r) for r in runs)
    assert len(runs) == 2


def test_runs_reentering_curve_starts_new_run():
    _, p = _plot()
    runs = p._runs([(1, 1), (2, 6), (3, 6), (3, 1)])
    assert len(runs) == 2


# ------------------------------------------------------------------ sample / function


def test_sample_zero_division_becomes_break():
    _, p = _plot(x=(-1, 1))
    pts = p.sample(lambda x: 1 / x, n=2)  # x = -1, 0, 1
    assert pts[0] == (-1, -1.0) and pts[1] is None and pts[2] == (1, 1.0)


def test_sample_nonfinite_and_value_error_become_breaks():
    _, p = _plot(x=(-1, 1))
    pts = p.sample(lambda x: math.sqrt(x), n=2)
    assert pts[0] is None and pts[1] == (0, 0.0)
    pts = p.sample(lambda x: float("inf") if x == 0 else 1.0, n=2)
    assert pts[1] is None


def test_sample_log_spacing():
    _, p = _plot(x=(1, 100), y=(0, 1), xscale="log")
    xs = [pt[0] for pt in p.sample(lambda x: 0.5, n=2)]
    assert xs == pytest.approx([1, 10, 100])


def test_function_tan_pole_breaks_into_runs():
    # The pole of tan at pi/2 lies inside the window (0, 3).
    d, p = _plot(x=(0, 3), y=(-5, 5))
    p.function(math.tan, jump=3, n=400)
    data = [s for s in _path_data(d) if "M" in s]
    curve = max(data, key=lambda s: s.count("M"))
    assert curve.count("M") >= 2


def test_function_jump_prevents_joining_across_discontinuity():
    step = lambda x: 0.0 if x < 2 else 3.0
    d1, p1 = _plot()
    p1.function(step, n=100)
    d2, p2 = _plot()
    p2.function(step, n=100, jump=1.0)
    assert max(s.count("M") for s in _path_data(d1)) == 1
    assert max(s.count("M") for s in _path_data(d2)) == 2


def test_function_pole_without_jump_still_clipped_to_window():
    d, p = _plot(x=(0, 3), y=(-2, 2))
    p.function(math.tan, n=300)
    assert _path_data(d)


# ------------------------------------------------------------------ bars / ode / trajectory


def test_bars_riemann_sums_for_x_squared():
    f = lambda x: x * x
    sums = {}
    for rule in ("left", "right", "mid", "lower", "upper"):
        d, p = _plot(x=(0, 1), y=(0, 1))
        before = len(d.shapes)
        sums[rule] = p.bars(0, 1, f, 4, rule=rule)
        assert len(d.shapes) - before == 4
    assert sums["left"] == pytest.approx((0 + 1 + 4 + 9) / 16 / 4)      # 14/64
    assert sums["right"] == pytest.approx((1 + 4 + 9 + 16) / 16 / 4)    # 30/64
    assert sums["mid"] == pytest.approx((1 + 9 + 25 + 49) / 64 / 4)     # midpoints (k+.5)/4
    assert sums["lower"] == pytest.approx(sums["left"])  # increasing: min at left edge
    assert sums["upper"] == pytest.approx(sums["right"])
    assert sums["left"] < 1 / 3 < sums["right"]
    assert abs(sums["mid"] - 1 / 3) < abs(sums["left"] - 1 / 3)


def test_solve_ode_exponential_hits_e():
    d, p = _plot(x=(0, 1), y=(0, 3))
    pts = p.solve_ode(lambda x, y: y, 0, 1, 1, steps=400)
    assert pts[0] == (0, 1)
    assert pts[-1][0] == pytest.approx(1.0)
    assert abs(pts[-1][1] - math.e) < 1e-6
    assert len(pts) == 401


def test_solve_ode_default_endpoint_is_window_right_edge():
    _, p = _plot(x=(0, 2), y=(0, 10))
    pts = p.solve_ode(lambda x, y: 1.0, 0, 0, steps=10)
    assert pts[-1][0] == pytest.approx(2.0) and pts[-1][1] == pytest.approx(2.0)


def test_trajectory_rotation_stays_on_circle():
    _, p = _plot(x=(-2, 2), y=(-2, 2))
    pts = p.trajectory(lambda x, y: (-y, x), (1.0, 0.0), t_end=2 * math.pi, steps=600)
    assert len(pts) == 601
    assert all(abs(math.hypot(x, y) - 1) < 1e-6 for x, y in pts)
    assert pts[-1] == pytest.approx((1.0, 0.0), abs=1e-6)


# ------------------------------------------------------------------ drawing + rendering


def test_all_drawing_methods_add_elements_and_render(tmp_path):
    d, p = _plot(x=(-2, 4), y=(-1, 4))
    steps = []

    def step(name, fn):
        before = (len(d.shapes), len(d.edges), len(getattr(d, "texts", [])), len(d.render_svg()))
        fn()
        after = (len(d.shapes), len(d.edges), len(getattr(d, "texts", [])), len(d.render_svg()))
        assert after != before, f"{name} added nothing"
        steps.append(name)

    step("grid", p.grid)
    step("axes", lambda: p.axes(xlabel="$x$", ylabel="$y$"))
    step("area", lambda: p.area(lambda x: x * x / 4, 0, 3))
    step("bar_chart", lambda: p.bar_chart([(0, 1), (1, 2), (2, 3)]))
    step("candles", lambda: p.candles([(0, 1, 3, 0.5, 2), (1, 2, 3, 1, 1.5)]))
    step("slope_field", lambda: p.slope_field(lambda x, y: x - y))
    step("vector_field", lambda: p.vector_field(lambda x, y: (-y, x)))
    step("function", lambda: p.function(math.sin))
    step("polyline", lambda: p.polyline([(0, 0), (1, 1)]))
    step("frame", p.frame)
    assert len(steps) == 10

    out = render_all(d, tmp_path, "plot", formats=["svg"])
    svg = out["svg"].read_text()
    assert svg.startswith("<svg") or "<svg" in svg[:200]
    assert "</svg>" in svg


def test_area_polygon_has_closed_outline_points():
    d, p = _plot(x=(0, 4), y=(0, 4))
    p.area(lambda x: x, 0, 2, n=10)
    assert len(d.shapes) == 1
    svg = d.render_svg()
    attrs = re.findall(r'<(?:polygon|path)[^>]*? (?:points|d)="([^"]*)"', svg)
    nums = max((re.findall(r"-?\d+\.?\d*", a) for a in attrs), key=len)
    assert len(nums) // 2 >= 22  # 11 top + 11 base vertices


def test_candles_and_bar_chart_counts():
    d, p = _plot(x=(0, 5), y=(0, 5))
    p.bar_chart([(1, 2), (2, 3), (3, 1)])
    assert len(d.shapes) == 3
    d, p = _plot(x=(0, 5), y=(0, 5))
    p.candles([(1, 1, 3, 0.5, 2), (2, 3, 4, 2, 2.5)])
    assert len(d.shapes) >= 2
