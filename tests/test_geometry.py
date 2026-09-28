from dataclasses import FrozenInstanceError
import math
import pytest
import iiot_diagrams
from iiot_diagrams import Point, Size, Rect, Anchor, UnitBasis, CubicBezier

def test_package_exports():
    assert hasattr(iiot_diagrams, "Point")
    assert hasattr(iiot_diagrams, "Size")
    assert hasattr(iiot_diagrams, "Rect")
    assert hasattr(iiot_diagrams, "Anchor")
    assert hasattr(iiot_diagrams, "UnitBasis")
    assert hasattr(iiot_diagrams, "CubicBezier")
    assert {"Point", "Size", "Rect", "Anchor", "UnitBasis", "CubicBezier"}.issubset(set(iiot_diagrams.__all__))

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


def test_cubic_bezier_immutability():
    cb = CubicBezier(Point(0.0, 0.0), Point(1.0, 1.0), Point(2.0, 2.0), Point(3.0, 3.0))
    with pytest.raises(FrozenInstanceError):
        cb.p0 = Point(4.0, 4.0)  # type: ignore
    with pytest.raises(FrozenInstanceError):
        cb.c1 = Point(4.0, 4.0)  # type: ignore
    with pytest.raises(FrozenInstanceError):
        cb.c2 = Point(4.0, 4.0)  # type: ignore
    with pytest.raises(FrozenInstanceError):
        cb.p3 = Point(4.0, 4.0)  # type: ignore


def test_quadratic_bezier_evaluation_and_tangents():
    from diagrams_as_code.geometry import QuadraticBezier

    qb = QuadraticBezier(
        p0=Point(0.0, 0.0),
        p1=Point(10.0, 20.0),
        p2=Point(30.0, 0.0),
    )

    # Endpoints
    assert qb.point_at(0.0) == Point(0.0, 0.0)
    assert qb.point_at(1.0) == Point(30.0, 0.0)

    # Midpoint t = 0.5:
    # (1-0.5)^2 * (0,0) + 2*(0.5)*(0.5)*(10,20) + 0.5^2 * (30,0) = (5 + 7.5, 10) = (12.5, 10.0)
    mid = qb.point_at(0.5)
    assert mid.x == pytest.approx(12.5)
    assert mid.y == pytest.approx(10.0)

    # Analytical derivative vectors
    # B'(0) = 2 * (P1 - P0) = 2 * (10, 20) = (20, 40)
    t0 = qb.tangent_at(0.0)
    assert t0.x == pytest.approx(20.0)
    assert t0.y == pytest.approx(40.0)

    # B'(1) = 2 * (P2 - P1) = 2 * (20, -20) = (40, -40)
    t1 = qb.tangent_at(1.0)
    assert t1.x == pytest.approx(40.0)
    assert t1.y == pytest.approx(-40.0)

    # Sample
    pts_16 = qb.sample(16)
    assert len(pts_16) == 16
    assert pts_16[0] == Point(0.0, 0.0)
    assert pts_16[-1] == Point(30.0, 0.0)

    # Guard sample n < 2
    assert qb.sample(1) == [Point(0.0, 0.0), Point(30.0, 0.0)]
    assert qb.sample(0) == [Point(0.0, 0.0), Point(30.0, 0.0)]


def test_quadratic_bezier_bbox_vs_numerical_samples():
    from diagrams_as_code.geometry import QuadraticBezier

    # Curve with overshoot / extrema along both axes:
    # x goes from 50 -> 200 -> 100 (overshoot max along x)
    # y goes from 100 -> -50 -> 150 (undershoot min along y)
    qb = QuadraticBezier(
        p0=Point(50.0, 100.0),
        p1=Point(200.0, -50.0),
        p2=Point(100.0, 150.0),
    )

    fine_samples = qb.sample(1001)
    num_min_x = min(p.x for p in fine_samples)
    num_max_x = max(p.x for p in fine_samples)
    num_min_y = min(p.y for p in fine_samples)
    num_max_y = max(p.y for p in fine_samples)

    bb = qb.bbox()

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


def test_quadratic_bezier_arc_length_and_immutability():
    from diagrams_as_code.geometry import QuadraticBezier

    # Collinear points: arc length should equal straight distance
    collinear = QuadraticBezier(
        p0=Point(0.0, 0.0),
        p1=Point(10.0, 0.0),
        p2=Point(20.0, 0.0),
    )
    assert collinear.arc_length(num_samples=16) == pytest.approx(20.0, rel=1e-4)

    # Curved arc length
    curved = QuadraticBezier(
        p0=Point(0.0, 0.0),
        p1=Point(0.0, 20.0),
        p2=Point(20.0, 20.0),
    )
    chord_len = curved.p0.distance_to(curved.p2)
    poly_len = curved.p0.distance_to(curved.p1) + curved.p1.distance_to(curved.p2)
    arc_len = curved.arc_length(num_samples=64)
    assert chord_len < arc_len < poly_len

    # Immutability
    with pytest.raises(FrozenInstanceError):
        curved.p0 = Point(1.0, 1.0)  # type: ignore
    with pytest.raises(FrozenInstanceError):
        curved.p1 = Point(1.0, 1.0)  # type: ignore
    with pytest.raises(FrozenInstanceError):
        curved.p2 = Point(1.0, 1.0)  # type: ignore


def test_cubic_bezier_subdivision():
    from diagrams_as_code.geometry import CubicBezier

    cb = CubicBezier(
        p0=Point(0.0, 10.0),
        c1=Point(20.0, 50.0),
        c2=Point(80.0, 90.0),
        p3=Point(100.0, 20.0),
    )

    # Subdivide at midpoint t = 0.5
    left, right = cb.subdivide(0.5)
    assert left.p0 == cb.p0
    assert right.p3 == cb.p3
    assert left.p3 == right.p0
    assert left.p3.distance_to(cb.point_at(0.5)) < 1e-9

    # Sample subcurves and compare with parent curve evaluations
    assert left.point_at(0.5).distance_to(cb.point_at(0.25)) < 1e-5
    assert right.point_at(0.5).distance_to(cb.point_at(0.75)) < 1e-5

    # Split alias produces identical result
    split_left, split_right = cb.split(0.5)
    assert split_left == left
    assert split_right == right

    # Asymmetric subdivision at t = 0.3
    left_3, right_3 = cb.subdivide(0.3)
    assert left_3.p0 == cb.p0
    assert right_3.p3 == cb.p3
    assert left_3.p3 == right_3.p0
    assert left_3.p3.distance_to(cb.point_at(0.3)) < 1e-9
    # u = 0.5 on left_3 corresponds to t = 0.5 * 0.3 = 0.15
    assert left_3.point_at(0.5).distance_to(cb.point_at(0.15)) < 1e-5
    # u = 0.5 on right_3 corresponds to t = 0.3 + 0.5 * 0.7 = 0.65
    assert right_3.point_at(0.5).distance_to(cb.point_at(0.65)) < 1e-5

    # Parameter boundary handling
    with pytest.raises(ValueError, match=r"Parameter t must be in \[0\.0, 1\.0\]"):
        cb.subdivide(-0.01)
    with pytest.raises(ValueError, match=r"Parameter t must be in \[0\.0, 1\.0\]"):
        cb.subdivide(1.01)


def test_cubic_bezier_intersects_rect_clear_miss():
    from diagrams_as_code.geometry import CubicBezier, Rect

    cb = CubicBezier(Point(0.0, 0.0), Point(10.0, 10.0), Point(20.0, 20.0), Point(30.0, 30.0))
    rect = Rect(100.0, 100.0, 50.0, 50.0)
    assert not cb.intersects_rect(rect)


def test_cubic_bezier_intersects_rect_direct_hit():
    from diagrams_as_code.geometry import CubicBezier, Rect

    cb = CubicBezier(Point(0.0, 50.0), Point(30.0, 50.0), Point(70.0, 50.0), Point(100.0, 50.0))
    rect = Rect(40.0, 40.0, 20.0, 20.0)
    assert cb.intersects_rect(rect)


def test_cubic_bezier_intersects_rect_grazing_corner_miss():
    from diagrams_as_code.geometry import CubicBezier, Rect

    # Curve arcs diagonally near rectangle corner (50, 50)
    cb = CubicBezier(
        p0=Point(30.0, 70.0),
        c1=Point(35.0, 45.0),
        c2=Point(45.0, 35.0),
        p3=Point(70.0, 30.0),
    )
    rect = Rect(50.0, 50.0, 40.0, 40.0)

    # Broadphase AABB intersects: cb.bbox() overlaps [50, 70] x [50, 70]
    assert cb.bbox().intersects(rect)

    # Narrowphase correctly verifies zero intersection with rectangle interior
    assert not cb.intersects_rect(rect)


def test_cubic_bezier_intersects_rect_corner_clipping_hit():
    from diagrams_as_code.geometry import CubicBezier, Rect

    # Curve pushed outward to clip corner (50, 50) of rectangle
    cb = CubicBezier(
        p0=Point(30.0, 70.0),
        c1=Point(55.0, 55.0),
        c2=Point(55.0, 55.0),
        p3=Point(70.0, 30.0),
    )
    rect = Rect(50.0, 50.0, 40.0, 40.0)
    assert cb.intersects_rect(rect)


def test_cubic_bezier_intersects_rect_depth_capping():
    from diagrams_as_code.geometry import CubicBezier, Rect

    cb = CubicBezier(Point(0.0, 50.0), Point(30.0, 50.0), Point(70.0, 50.0), Point(100.0, 50.0))
    rect = Rect(40.0, 40.0, 20.0, 20.0)

    # Verify clamping at lower and upper bounds does not error or cause stack overflow
    assert cb.intersects_rect(rect, max_depth=0)
    assert cb.intersects_rect(rect, max_depth=-5)
    assert cb.intersects_rect(rect, max_depth=1)
    assert cb.intersects_rect(rect, max_depth=100)


def test_routed_path_polyline_bbox_and_translate() -> None:
    from diagrams_as_code.geometry import PathKind, RoutedPath, Point, Rect

    pts = (Point(10.0, 20.0), Point(50.0, 20.0), Point(50.0, 80.0))
    path = RoutedPath(kind=PathKind.POLYLINE, points=pts, corner_radius=0.0)
    assert path.bbox() == Rect(10.0, 20.0, 40.0, 60.0)

    translated = path.translate(5.0, 10.0)
    assert translated.points == (Point(15.0, 30.0), Point(55.0, 30.0), Point(55.0, 90.0))
    assert translated.bbox() == Rect(15.0, 30.0, 40.0, 60.0)


def test_routed_path_bezier_bbox() -> None:
    from diagrams_as_code.geometry import PathKind, RoutedPath, Point

    p0 = Point(0.0, 100.0)
    c1 = Point(30.0, 0.0)
    c2 = Point(70.0, 0.0)
    p3 = Point(100.0, 100.0)
    path = RoutedPath(kind=PathKind.BEZIER_CHAIN, points=(p0, c1, c2, p3))
    bb = path.bbox()
    assert bb.y < 30.0  # Captures arching Bezier curve apex
    assert bb.height > 70.0


def test_routed_path_svg_d_polyline_and_fillet() -> None:
    from diagrams_as_code.geometry import PathKind, RoutedPath, Point

    pts = (Point(0.0, 0.0), Point(100.0, 0.0), Point(100.0, 100.0))
    sharp = RoutedPath(kind=PathKind.POLYLINE, points=pts, corner_radius=0.0)
    assert sharp.svg_d() == "M 0.0 0.0 L 100.0 0.0 L 100.0 100.0"

    filleted = RoutedPath(kind=PathKind.POLYLINE, points=pts, corner_radius=10.0)
    d = filleted.svg_d()
    assert "Q" in d


def test_routed_path_label_anchor() -> None:
    from diagrams_as_code.geometry import PathKind, RoutedPath, Point

    pts = (Point(0.0, 0.0), Point(100.0, 0.0))
    path = RoutedPath(kind=PathKind.POLYLINE, points=pts)
    assert path.label_anchor() == (50.0, 0.0)


def test_routed_path_segments_and_edge_cases() -> None:
    from diagrams_as_code.geometry import PathKind, RoutedPath, Point, Rect, CubicBezier

    # Empty path
    empty_poly = RoutedPath(kind=PathKind.POLYLINE, points=())
    assert empty_poly.segments() == []
    assert empty_poly.bbox() == Rect(0.0, 0.0, 0.0, 0.0)
    assert empty_poly.label_anchor() == (0.0, 0.0)
    assert empty_poly.svg_d() == ""

    # Polyline segments
    pts = (Point(0.0, 0.0), Point(10.0, 0.0), Point(10.0, 10.0))
    poly = RoutedPath(kind=PathKind.POLYLINE, points=pts)
    assert poly.segments() == [(Point(0.0, 0.0), Point(10.0, 0.0)), (Point(10.0, 0.0), Point(10.0, 10.0))]

    # Bezier chain invalid lengths
    assert RoutedPath(kind=PathKind.BEZIER_CHAIN, points=(Point(0.0, 0.0),)).segments() == []
    assert RoutedPath(kind=PathKind.BEZIER_CHAIN, points=(Point(0.0, 0.0), Point(1.0, 1.0), Point(2.0, 2.0))).segments() == []

    # Bezier chain valid multi-segment (7 points -> 2 curves)
    bezier_pts = (
        Point(0.0, 0.0), Point(10.0, 0.0), Point(20.0, 10.0), Point(30.0, 10.0),
        Point(40.0, 10.0), Point(50.0, 20.0), Point(60.0, 20.0),
    )
    bchain = RoutedPath(kind=PathKind.BEZIER_CHAIN, points=bezier_pts)
    segs = bchain.segments()
    assert len(segs) == 2
    assert all(isinstance(s, CubicBezier) for s in segs)
    assert "C" in bchain.svg_d()
    anchor = bchain.label_anchor()
    assert isinstance(anchor, tuple) and len(anchor) == 2

    # Filleted polyline label anchor on longest segment
    long_pts = (Point(0.0, 0.0), Point(10.0, 0.0), Point(10.0, 100.0))
    filleted_long = RoutedPath(kind=PathKind.POLYLINE, points=long_pts, corner_radius=5.0)
    # Longest segment is (10, 0) to (10, 100), midpoint is (10.0, 50.0)
    assert filleted_long.label_anchor() == (10.0, 50.0)



