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
