import math
import pytest
import iiot_diagrams
from iiot_diagrams import Point, Size, Rect, Anchor, UnitBasis

def test_package_exports():
    assert hasattr(iiot_diagrams, "Point")
    assert hasattr(iiot_diagrams, "Size")
    assert hasattr(iiot_diagrams, "Rect")
    assert hasattr(iiot_diagrams, "Anchor")
    assert hasattr(iiot_diagrams, "UnitBasis")
    assert {"Point", "Size", "Rect", "Anchor", "UnitBasis"}.issubset(set(iiot_diagrams.__all__))

def test_rect_anchor_points():
    rect = Rect(10, 20, 100, 50)
    assert rect.left == 10
    assert rect.right == 110
    assert rect.top == 20
    assert rect.bottom == 70
    assert rect.center == Point(60, 45)

    # Test all 9 Anchor enum values explicitly with rect.get_anchor
    assert rect.get_anchor(Anchor.TOP_LEFT) == Point(10, 20)
    assert rect.get_anchor(Anchor.TOP_CENTER) == Point(60, 20)
    assert rect.get_anchor(Anchor.TOP_RIGHT) == Point(110, 20)
    assert rect.get_anchor(Anchor.LEFT_CENTER) == Point(10, 45)
    assert rect.get_anchor(Anchor.CENTER) == Point(60, 45)
    assert rect.get_anchor(Anchor.RIGHT_CENTER) == Point(110, 45)
    assert rect.get_anchor(Anchor.BOTTOM_LEFT) == Point(10, 70)
    assert rect.get_anchor(Anchor.BOTTOM_CENTER) == Point(60, 70)
    assert rect.get_anchor(Anchor.BOTTOM_RIGHT) == Point(110, 70)

    # Convenience properties
    assert rect.top_left == Point(10, 20)
    assert rect.top_right == Point(110, 20)
    assert rect.bottom_left == Point(10, 70)
    assert rect.bottom_right == Point(110, 70)

def test_rect_invalid_anchor():
    rect = Rect(0, 0, 10, 10)
    with pytest.raises(ValueError, match="Unknown anchor"):
        rect.get_anchor("invalid_anchor")  # type: ignore

def test_rect_union_and_expand():
    r1 = Rect(10, 10, 40, 40)
    r2 = Rect(60, 60, 20, 20)
    u = r1.union(r2)
    assert u == Rect(10, 10, 70, 70)
    expanded = u.expand(10)
    assert expanded == Rect(0, 0, 90, 90)

    # 2-tuple padding: (top/bottom, left/right)
    expanded_2 = u.expand((5, 15))
    assert expanded_2 == Rect(-5, 5, 100, 80)

    # 4-tuple padding: (top, right, bottom, left)
    expanded_4 = u.expand((1, 2, 3, 4))
    assert expanded_4 == Rect(6, 9, 76, 74)

    # list padding
    expanded_list_2 = u.expand([5, 15])
    assert expanded_list_2 == Rect(-5, 5, 100, 80)
    expanded_list_4 = u.expand([1, 2, 3, 4])
    assert expanded_list_4 == Rect(6, 9, 76, 74)

    # Invalid length
    with pytest.raises(ValueError, match="Padding must be 1, 2, or 4 values"):
        u.expand((1, 2, 3))  # type: ignore

    # Unsupported types
    with pytest.raises(TypeError, match="Unsupported padding type"):
        u.expand("invalid")  # type: ignore

    with pytest.raises(TypeError, match="Unsupported padding type"):
        u.expand({"top": 10})  # type: ignore

def test_unit_basis_conversion():
    basis = UnitBasis(Size(1000, 500))
    assert basis.canvas_size == Size(1000, 500)
    assert basis.reference_size == Size(1000, 500)
    pt = basis.to_absolute(0.25, 0.5)
    assert pt == Point(250.0, 250.0)
    pt_pct = basis.to_absolute("10%", "20%")
    assert pt_pct == Point(100.0, 100.0)
    pt_abs = basis.to_absolute(150, 200)
    assert pt_abs == Point(150.0, 200.0)

    # Boundary tests (0.0, 1.0, "0%", "100%")
    assert basis.to_absolute(0.0, 0.0) == Point(0.0, 0.0)
    assert basis.to_absolute(1.0, 1.0) == Point(1000.0, 500.0)
    assert basis.to_absolute("0%", "0%") == Point(0.0, 0.0)
    assert basis.to_absolute("100%", "100%") == Point(1000.0, 500.0)

    # keyword argument canvas_size
    basis_kw = UnitBasis(canvas_size=Size(800, 600))
    assert basis_kw.canvas_size == Size(800, 600)
    assert basis_kw.to_absolute(0.5, 0.5) == Point(400.0, 300.0)

    with pytest.raises(ValueError, match="A Size reference or canvas_size must be provided"):
        UnitBasis()

def test_immutability():
    pt = Point(1.0, 2.0)
    with pytest.raises(Exception):
        pt.x = 3.0  # type: ignore
    sz = Size(10.0, 20.0)
    with pytest.raises(Exception):
        sz.width = 30.0  # type: ignore


def test_point_arithmetic_operators():
    p1 = Point(10.0, 20.0)
    p2 = Point(3.0, 5.0)

    # Addition
    assert p1 + p2 == Point(13.0, 25.0)
    # Subtraction
    assert p1 - p2 == Point(7.0, 15.0)
    # Scalar multiplication (mul and rmul)
    assert p1 * 2.0 == Point(20.0, 40.0)
    assert 2.5 * p1 == Point(25.0, 50.0)
    assert p1 * 3 == Point(30.0, 60.0)
    assert 3 * p1 == Point(30.0, 60.0)
    # Division
    assert p1 / 2.0 == Point(5.0, 10.0)
    assert p1 / 4 == Point(2.5, 5.0)

    # Type errors / NotImplemented
    with pytest.raises(TypeError):
        _ = p1 + 5  # type: ignore
    with pytest.raises(TypeError):
        _ = p1 - 5  # type: ignore
    with pytest.raises(TypeError):
        _ = p1 * "scalar"  # type: ignore
    with pytest.raises(TypeError):
        _ = "scalar" * p1  # type: ignore
    with pytest.raises(TypeError):
        _ = p1 / "scalar"  # type: ignore

    # distance_to
    assert p1.distance_to(p2) == pytest.approx(math.hypot(7.0, 15.0))
    assert p1.distance_to(Point(10.0, 20.0)) == 0.0


def test_cubic_bezier_evaluation_and_tangents():
    from diagrams_as_code.geometry import CubicBezier

    cb = CubicBezier(
        p0=Point(0.0, 0.0),
        c1=Point(10.0, 20.0),
        c2=Point(20.0, 20.0),
        p3=Point(30.0, 0.0),
    )

    # Endpoints
    assert cb.point_at(0.0) == Point(0.0, 0.0)
    assert cb.point_at(1.0) == Point(30.0, 0.0)

    # Midpoint t = 0.5:
    # x = 0.125 * 0 + 3 * 0.25 * 0.5 * 10 + 3 * 0.5 * 0.25 * 20 + 0.125 * 30 = 3.75 + 7.5 + 3.75 = 15.0
    # y = 0.125 * 0 + 3 * 0.25 * 0.5 * 20 + 3 * 0.5 * 0.25 * 20 + 0.125 * 0 = 7.5 + 7.5 = 15.0
    mid = cb.point_at(0.5)
    assert mid.x == pytest.approx(15.0)
    assert mid.y == pytest.approx(15.0)

    # Tangents at endpoints
    # B'(0) = 3 * (C1 - P0) = 3 * (10, 20) = (30, 60)
    t0 = cb.tangent_at(0.0)
    assert t0.x == pytest.approx(30.0)
    assert t0.y == pytest.approx(60.0)

    # B'(1) = 3 * (P3 - C2) = 3 * (10, -20) = (30, -60)
    t1 = cb.tangent_at(1.0)
    assert t1.x == pytest.approx(30.0)
    assert t1.y == pytest.approx(-60.0)

    # Sample
    pts_16 = cb.sample(16)
    assert len(pts_16) == 16
    assert pts_16[0] == Point(0.0, 0.0)
    assert pts_16[-1] == Point(30.0, 0.0)

    # Guard sample n < 2
    assert cb.sample(1) == [Point(0.0, 0.0), Point(30.0, 0.0)]
    assert cb.sample(0) == [Point(0.0, 0.0), Point(30.0, 0.0)]


def test_cubic_bezier_bbox_vs_numerical_samples():
    from diagrams_as_code.geometry import CubicBezier

    # S-curve with overshoot along both axes
    cb = CubicBezier(
        p0=Point(10.0, 50.0),
        c1=Point(100.0, 200.0),
        c2=Point(50.0, -100.0),
        p3=Point(200.0, 50.0),
    )

    # 1,001 fine samples for ground truth comparison
    fine_samples = cb.sample(1001)
    num_min_x = min(p.x for p in fine_samples)
    num_max_x = max(p.x for p in fine_samples)
    num_min_y = min(p.y for p in fine_samples)
    num_max_y = max(p.y for p in fine_samples)

    bb = cb.bbox()

    # Analytical bbox must enclose all numerical samples
    assert bb.left <= num_min_x + 1e-4
    assert bb.right >= num_max_x - 1e-4
    assert bb.top <= num_min_y + 1e-4
    assert bb.bottom >= num_max_y - 1e-4

    # Tightness: analytical bounds should match within 0.01px to 1001 numerical samples
    assert bb.left == pytest.approx(num_min_x, abs=0.01)
    assert bb.right == pytest.approx(num_max_x, abs=0.01)
    assert bb.top == pytest.approx(num_min_y, abs=0.01)
    assert bb.bottom == pytest.approx(num_max_y, abs=0.01)


def test_cubic_bezier_arc_length_and_midpoint():
    from diagrams_as_code.geometry import CubicBezier

    # Straight line: arc-length should be exact distance
    line = CubicBezier(
        p0=Point(0.0, 0.0),
        c1=Point(10.0, 0.0),
        c2=Point(20.0, 0.0),
        p3=Point(30.0, 0.0),
    )
    assert line.arc_length() == pytest.approx(30.0, rel=1e-4)
    mid_line = line.arc_length_midpoint()
    assert mid_line.x == pytest.approx(15.0, abs=1e-4)
    assert mid_line.y == pytest.approx(0.0, abs=1e-4)

    # Asymmetric curve where arc-length midpoint differs from parametric t=0.5
    asym = CubicBezier(
        p0=Point(0.0, 0.0),
        c1=Point(5.0, 0.0),
        c2=Point(10.0, 0.0),
        p3=Point(100.0, 100.0),
    )
    mid_arc = asym.arc_length_midpoint(num_samples=32)
    mid_param = asym.point_at(0.5)

    # They should differ measurably because curve accelerates near p3
    assert abs(mid_arc.x - mid_param.x) > 5.0

    # Total arc length
    total_l = asym.arc_length(num_samples=64)
    # The arc length up to midpoint should be approximately half total length
    # Check using fine sampling
    samples = asym.sample(1001)
    # find closest sample to mid_arc
    closest_idx = min(range(len(samples)), key=lambda i: samples[i].distance_to(mid_arc))
    len_to_mid = sum(samples[i].distance_to(samples[i + 1]) for i in range(closest_idx))
    assert len_to_mid == pytest.approx(total_l / 2.0, rel=0.02)


def test_cubic_bezier_degenerate_cases():
    from diagrams_as_code.geometry import CubicBezier, Rect

    # Point curve: all 4 points identical
    pt_curve = CubicBezier(
        p0=Point(10.0, 20.0),
        c1=Point(10.0, 20.0),
        c2=Point(10.0, 20.0),
        p3=Point(10.0, 20.0),
    )
    assert pt_curve.bbox() == Rect(10.0, 20.0, 0.0, 0.0)
    assert pt_curve.arc_length() == 0.0
    assert pt_curve.arc_length_midpoint() == Point(10.0, 20.0)

    # Linear curve (derivative quadratic is linear / constant)
    linear = CubicBezier(
        p0=Point(0.0, 0.0),
        c1=Point(10.0, 10.0),
        c2=Point(20.0, 20.0),
        p3=Point(30.0, 30.0),
    )
    bb = linear.bbox()
    assert bb == Rect(0.0, 0.0, 30.0, 30.0)

