"""Every name a package advertises in ``__all__`` is importable from it."""
from __future__ import annotations

import pytest

import diagrams_as_code
import iiot_diagrams

#: Public symbols added by the auto-layout/CLI work (spec §2, §3, §5).
NEW_SYMBOLS = (
    "LayeredLayout",
    "LayoutWarning",
    "export_layout",
    "load_layout_file",
    "render_all",
)


@pytest.mark.parametrize("package", [diagrams_as_code, iiot_diagrams])
def test_every_advertised_name_is_reachable(package) -> None:
    missing = [name for name in package.__all__ if not hasattr(package, name)]
    assert missing == []


@pytest.mark.parametrize("package", [diagrams_as_code, iiot_diagrams])
def test_new_layout_and_output_symbols_are_exported(package) -> None:
    assert set(NEW_SYMBOLS).issubset(package.__all__)


def test_the_facade_mirrors_the_canonical_package() -> None:
    assert iiot_diagrams.__all__ == diagrams_as_code.__all__


@pytest.mark.parametrize("package", [diagrams_as_code, iiot_diagrams])
def test_cubic_bezier_is_exported(package) -> None:
    assert "CubicBezier" in package.__all__
    assert hasattr(package, "CubicBezier")


@pytest.mark.parametrize("package", [diagrams_as_code, iiot_diagrams])
def test_curve_routing_symbols_are_exported(package) -> None:
    for name in ("CurveRouter", "EdgeRouter", "PORT_NORMALS"):
        assert name in package.__all__
        assert hasattr(package, name)


@pytest.mark.parametrize("package", [diagrams_as_code, iiot_diagrams])
def test_quadratic_bezier_is_exported(package) -> None:
    assert "QuadraticBezier" in package.__all__
    assert hasattr(package, "QuadraticBezier")


