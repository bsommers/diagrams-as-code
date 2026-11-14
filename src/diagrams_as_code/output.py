"""Write a diagram's SVG, PNG, PDF and Bill of Materials to a directory."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Optional, Union

if TYPE_CHECKING:
    from diagrams_as_code.diagram import Diagram

#: Every format ``render_all`` can write, in the order they are written.
FORMATS: tuple[str, ...] = ("svg", "png", "pdf", "bom")
#: What ``render_all`` writes when no formats are named.
DEFAULT_FORMATS: tuple[str, ...] = ("svg", "png", "bom")


def render_all(
    diag: Diagram,
    out_dir: Union[str, Path],
    stem: str,
    formats: Iterable[str] = DEFAULT_FORMATS,
    readme_name: Optional[str] = None,
) -> dict[str, Path]:
    """Render ``diag`` as ``<stem>.svg``, ``<stem>.png`` and a BOM README.

    Name ``"pdf"`` in ``formats`` to write ``<stem>.pdf`` as well.
    """
    wanted = set(formats)
    unknown = sorted(wanted - set(FORMATS))
    if unknown:
        raise ValueError(f"unknown output format(s) {unknown}; choose from {list(FORMATS)}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_name = f"{stem}.svg"
    written: dict[str, Path] = {}
    for fmt in FORMATS:
        if fmt not in wanted:
            continue
        if fmt == "svg":
            path = out / svg_name
            diag.render_svg(path)
        elif fmt == "png":
            path = out / f"{stem}.png"
            diag.render_png(path)
        elif fmt == "pdf":
            path = out / f"{stem}.pdf"
            diag.render_pdf(path)
        else:
            path = out / (readme_name or f"{stem}_README.md")
            diag.generate_readme(svg_name, path)
        written[fmt] = path
    return written
