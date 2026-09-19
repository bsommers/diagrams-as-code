"""Vector shape primitives and built-in IIoT vector icon library."""
from __future__ import annotations

import html
from typing import ClassVar


class ShapeLibrary:
    """Library for rendering crisp vector shape primitives and built-in IIoT icons."""

    _CANONICAL_ICONS: ClassVar[set[str]] = {
        "sensor",
        "gateway",
        "broker",
        "database",
        "queue",
        "cloud",
        "dashboard",
    }

    _ICON_ALIASES: ClassVar[dict[str, str]] = {
        "edge": "gateway",
        "gateway/edge": "gateway",
        "mqtt": "broker",
        "influx": "database",
        "db": "database",
        "database/influx": "database",
        "kafka": "queue",
        "queue/kafka": "queue",
        "grafana": "dashboard",
        "dashboard/grafana": "dashboard",
    }

    def render_box(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str,
        stroke_width: float = 2.0,
        radius: float = 6.0,
    ) -> str:
        """Render a rounded rectangular box."""
        return (
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
        )

    def render_cylinder(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str,
        stroke_width: float = 2.0,
    ) -> str:
        """Render a 3D isometric cylinder (data storage, tank, silo)."""
        ry = min(12.0, h / 4.0)
        rx = w / 2.0
        return (
            f'<path d="M {x} {y + ry} A {rx} {ry} 0 0 1 {x + w} {y + ry} '
            f'L {x + w} {y + h - ry} A {rx} {ry} 0 0 1 {x} {y + h - ry} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>\n'
            f'<ellipse cx="{x + rx}" cy="{y + ry}" rx="{rx}" ry="{ry}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    def render_diamond(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str,
        stroke_width: float = 2.0,
    ) -> str:
        """Render a diamond / rhombus decision shape."""
        cx = x + w / 2.0
        cy = y + h / 2.0
        d = f"M {cx} {y} L {x + w} {cy} L {cx} {y + h} L {x} {cy} Z"
        return (
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}"/>'
        )

    def render_cloud(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str,
        stroke_width: float = 2.0,
    ) -> str:
        """Render a scalable cloud container shape."""
        d = (
            f"M {x + 0.25 * w} {y + 0.85 * h} "
            f"L {x + 0.75 * w} {y + 0.85 * h} "
            f"C {x + 0.9 * w} {y + 0.85 * h} {x + w} {y + 0.72 * h} {x + w} {y + 0.58 * h} "
            f"C {x + w} {y + 0.44 * h} {x + 0.88 * w} {y + 0.32 * h} {x + 0.75 * w} {y + 0.32 * h} "
            f"C {x + 0.7 * w} {y + 0.15 * h} {x + 0.5 * w} {y + 0.15 * h} {x + 0.4 * w} {y + 0.28 * h} "
            f"C {x + 0.28 * w} {y + 0.22 * h} {x + 0.12 * w} {y + 0.32 * h} {x + 0.12 * w} {y + 0.48 * h} "
            f"C {x} {y + 0.55 * h} {x} {y + 0.75 * h} {x + 0.25 * w} {y + 0.85 * h} Z"
        )
        return (
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}"/>'
        )

    def render_badge(
        self,
        x: float,
        y: float,
        text: str,
        fill: str = "#FFC000",
        text_color: str = "#000000",
        font_size: float = 10.0,
        height: float = 18.0,
        padding_x: float = 8.0,
        font_family: str = (
            "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
        ),
    ) -> str:
        """Render a status or protocol badge pill with centered text."""
        char_w = font_size * 0.62
        badge_w = max(len(text) * char_w + 2 * padding_x, 24.0)
        rx = height / 2.0
        text_x = x + badge_w / 2.0
        text_y = y + height / 2.0 + font_size * 0.35
        escaped_text = html.escape(text)
        return (
            f'<g class="badge">\n'
            f'  <rect x="{x}" y="{y}" width="{badge_w}" height="{height}" rx="{rx}" fill="{fill}" />\n'
            f'  <text x="{text_x}" y="{text_y}" fill="{text_color}" font-size="{font_size}" '
            f'font-family="{font_family}" font-weight="600" text-anchor="middle">{escaped_text}</text>\n'
            f'</g>'
        )

    def _canonical_icon_name(self, name: str) -> str:
        key = name.strip().lower()
        if key in self._CANONICAL_ICONS:
            return key
        if key in self._ICON_ALIASES:
            return self._ICON_ALIASES[key]
        raise KeyError(
            f"Unknown icon '{name}'. Supported icons: {sorted(self._CANONICAL_ICONS)}"
        )

    def has_icon(self, name: str) -> bool:
        """Check if icon or alias is available in library."""
        key = name.strip().lower()
        return key in self._CANONICAL_ICONS or key in self._ICON_ALIASES

    def list_icons(self) -> list[str]:
        """Return list of supported canonical icon names."""
        return sorted(self._CANONICAL_ICONS)

    def _render_icon_content(
        self, canonical: str, color: str, stroke_width: float
    ) -> str:
        if canonical == "sensor":
            return (
                f'  <path d="M 4 4 A 11 11 0 0 1 20 4" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <path d="M 7 7 A 7 7 0 0 1 17 7" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <rect x="10" y="10" width="4" height="11" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="17" x2="16" y2="17" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "gateway":
            return (
                f'  <line x1="6" y1="9" x2="6" y2="3" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="18" y1="9" x2="18" y2="3" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <rect x="3" y="9" width="18" height="12" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="7" cy="15" r="1.5" fill="{color}"/>\n'
                f'  <circle cx="12" cy="15" r="1.5" fill="{color}"/>\n'
                f'  <circle cx="17" cy="15" r="1.5" fill="{color}"/>'
            )
        elif canonical == "broker":
            return (
                f'  <circle cx="12" cy="12" r="3.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="3.5" r="2" fill="{color}"/>\n'
                f'  <circle cx="12" cy="20.5" r="2" fill="{color}"/>\n'
                f'  <circle cx="3.5" cy="12" r="2" fill="{color}"/>\n'
                f'  <circle cx="20.5" cy="12" r="2" fill="{color}"/>\n'
                f'  <line x1="12" y1="5.5" x2="12" y2="8.5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="15.5" x2="12" y2="18.5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="5.5" y1="12" x2="8.5" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="15.5" y1="12" x2="18.5" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "database":
            return (
                f'  <ellipse cx="12" cy="6" rx="8" ry="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 4 12 C 4 15 20 15 20 12" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 4 18 C 4 21 20 21 20 18" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="4" y1="6" x2="4" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="20" y1="6" x2="20" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "queue":
            return (
                f'  <line x1="2" y1="6" x2="18" y2="6" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="2" y1="18" x2="18" y2="18" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="6" y1="6" x2="6" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="11" y1="6" x2="11" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="16" y1="6" x2="16" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 18 12 H 22 M 20 9 L 23 12 L 20 15" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif canonical == "cloud":
            return (
                f'  <path d="M 6.5 19 H 17.5 A 4 4 0 0 0 17.5 11 A 5.5 5.5 0 0 0 7 12 A 4 4 0 0 0 6.5 19 Z" '
                f'fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
            )
        elif canonical == "dashboard":
            return (
                f'  <rect x="3" y="3" width="18" height="15" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="3" y1="8" x2="21" y2="8" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <polyline points="6,15 10,11 13,13 17,9" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <line x1="9" y1="21" x2="15" y2="21" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="12" y1="18" x2="12" y2="21" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        raise KeyError(f"Unhandled icon '{canonical}'")

    def render_icon(
        self,
        name: str,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        """Render an IIoT component icon inside a positioned and scaled SVG group."""
        canonical = self._canonical_icon_name(name)
        scale = size / 24.0
        content = self._render_icon_content(canonical, color, stroke_width)
        return (
            f'<g class="icon icon-{canonical}" transform="translate({x}, {y}) scale({scale})">\n'
            f'{content}\n'
            f'</g>'
        )

    # Convenience icon renderers
    def render_sensor(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("sensor", x, y, size, color, stroke_width)

    def render_gateway(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("gateway", x, y, size, color, stroke_width)

    def render_edge(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("edge", x, y, size, color, stroke_width)

    def render_broker(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("broker", x, y, size, color, stroke_width)

    def render_database(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("database", x, y, size, color, stroke_width)

    def render_influx(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("influx", x, y, size, color, stroke_width)

    def render_queue(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("queue", x, y, size, color, stroke_width)

    def render_kafka(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("kafka", x, y, size, color, stroke_width)

    def render_cloud_icon(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("cloud", x, y, size, color, stroke_width)

    def render_dashboard(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("dashboard", x, y, size, color, stroke_width)

    def render_grafana(
        self,
        x: float,
        y: float,
        size: float = 24.0,
        color: str = "#FFC000",
        stroke_width: float = 2.0,
    ) -> str:
        return self.render_icon("grafana", x, y, size, color, stroke_width)


# Alias per plan interface specification
ShapeRenderer = ShapeLibrary
