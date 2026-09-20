"""Vector shape primitives and built-in IIoT / Domain vector icon library."""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import ClassVar, Optional


class ShapeLibrary:
    """Library for rendering crisp vector shape primitives and domain vector icons."""

    _CANONICAL_ICONS: ClassVar[set[str]] = {
        # Core & IIoT
        "sensor",
        "gateway",
        "broker",
        "database",
        "queue",
        "cloud",
        "dashboard",
        "scada",
        "hmi",
        "historian",
        "robot",
        # Cloud Domain
        "vpc",
        "serverless",
        "storage",
        "api_gateway",
        "cdn",
        "firewall",
        "dns",
        # AI Domain
        "brain",
        "model",
        "agent",
        "chip",
        "vector_db",
        "vision",
        "workflow",
        # Computer Domain
        "server",
        "terminal",
        "laptop",
        "mobile",
        "plc",
        "router",
        # Datacenter Domain
        "server_rack",
        "cluster",
        "storage_array",
        "cooling",
        "ups",
        "container",
        "kubernetes",
        # Business Process Domain
        "user",
        "document",
        "decision",
        "message",
        "shield",
        "analytics",
        # Cybersecurity Domain
        "lock",
        "key",
        "shield_check",
        "siem",
        "soc",
        "malware_scan",
        "vault",
        "honeypot",
        # Network Engineering Domain
        "switch",
        "core_router",
        "bgp",
        "mpls",
        "firewall_ha",
        "load_balancer",
        "patch_panel",
        "fiber_optic",
    }

    _ICON_ALIASES: ClassVar[dict[str, str]] = {
        # Existing IIoT aliases
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
        # Cloud aliases
        "lambda": "serverless",
        "function": "serverless",
        "s3": "storage",
        "bucket": "storage",
        "waf": "firewall",
        "route53": "dns",
        # AI aliases
        "neural": "brain",
        "neural_network": "brain",
        "llm": "model",
        "sparkles": "model",
        "robot": "agent",
        "bot": "agent",
        "gpu": "chip",
        "cpu": "chip",
        "npu": "chip",
        "tpu": "chip",
        "embeddings": "vector_db",
        "camera": "vision",
        "pipeline": "workflow",
        # Computer aliases
        "workstation": "laptop",
        "cli": "terminal",
        "bash": "terminal",
        "phone": "mobile",
        "smartphone": "mobile",
        "transducer": "sensor",
        # Datacenter aliases
        "rack": "server_rack",
        "nodes": "cluster",
        "san": "storage_array",
        "nas": "storage_array",
        "fan": "cooling",
        "battery": "ups",
        "power": "ups",
        "docker": "container",
        "k8s": "kubernetes",
        # Business process aliases
        "actor": "user",
        "stakeholder": "user",
        "contract": "document",
        "file": "document",
        "rule": "decision",
        "gateway_rule": "decision",
        "email": "message",
        "mail": "message",
        "notification": "message",
        "audit": "shield",
        "security": "shield",
        "compliance": "shield",
        "chart": "analytics",
        "kpi": "analytics",
        "metrics": "analytics",
        # Cybersecurity aliases
        "crypto": "lock",
        "encryption": "lock",
        "secret": "key",
        "pki": "key",
        "compliance_gate": "shield_check",
        "radar": "siem",
        "edr": "malware_scan",
        "antivirus": "malware_scan",
        "hsm": "vault",
        "safe": "vault",
        "decoy": "honeypot",
        # Network engineering aliases
        "l2_switch": "switch",
        "l3_switch": "switch",
        "router_core": "core_router",
        "as": "bgp",
        "autonomous_system": "bgp",
        "label_switch": "mpls",
        "lb": "load_balancer",
        "alb": "load_balancer",
        "nlb": "load_balancer",
        "patch": "patch_panel",
        "fiber": "fiber_optic",
        "optic": "fiber_optic",
    }

    def __init__(self) -> None:
        self._custom_icons: dict[str, str] = {}

    def _validate_dimensions(self, w: float, h: float) -> None:
        if w <= 0 or h <= 0:
            raise ValueError(f"Width and height must be positive, got w={w}, h={h}")

    def register_svg_icon(self, name: str, svg_markup: str) -> None:
        """Register custom SVG icon markup under a symbolic name."""
        if not name or not isinstance(name, str):
            raise ValueError("Icon name must be a non-empty string")
        key = name.strip().lower()
        match = re.search(r"<svg[^>]*>(.*?)</svg>", svg_markup, re.DOTALL | re.IGNORECASE)
        content = match.group(1).strip() if match else svg_markup.strip()
        self._custom_icons[key] = content

    def load_icon_file(self, filepath: str | Path, name: Optional[str] = None) -> str:
        """Load an external SVG icon file and register it."""
        p = Path(filepath)
        if not p.is_file():
            raise FileNotFoundError(f"SVG icon file not found: {filepath}")
        svg_text = p.read_text(encoding="utf-8")
        icon_name = name or p.stem
        self.register_svg_icon(icon_name, svg_text)
        return icon_name

    def load_icons_from_directory(self, dirpath: str | Path) -> list[str]:
        """Load all .svg files from a directory recursively."""
        d = Path(dirpath)
        if not d.is_dir():
            raise NotADirectoryError(f"Directory not found: {dirpath}")
        loaded = []
        for svg_file in d.glob("**/*.svg"):
            icon_name = svg_file.stem.lower()
            self.load_icon_file(svg_file, icon_name)
            loaded.append(icon_name)
        return sorted(loaded)

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
        self._validate_dimensions(w, h)
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
        self._validate_dimensions(w, h)
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
        self._validate_dimensions(w, h)
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
        self._validate_dimensions(w, h)
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

    def render_server_rack(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str,
        stroke_width: float = 2.0,
        num_units: int = 4,
    ) -> str:
        """Render an industrial server rack chassis with blade units and LED indicators."""
        self._validate_dimensions(w, h)
        units = max(1, int(num_units))
        margin = 4.0
        blade_w = max(4.0, w - 2 * margin)
        avail_h = max(4.0, h - 2 * margin)
        gap = 3.0
        blade_h = max(2.0, (avail_h - (units - 1) * gap) / units)

        parts = [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
        ]

        # Mounting flanges
        flange_w = min(4.0, w / 8.0)
        parts.append(
            f'<line x1="{x + flange_w}" y1="{y + 2}" x2="{x + flange_w}" y2="{y + h - 2}" '
            f'stroke="{stroke}" stroke-width="1" stroke-dasharray="2,3" />'
        )
        parts.append(
            f'<line x1="{x + w - flange_w}" y1="{y + 2}" x2="{x + w - flange_w}" y2="{y + h - 2}" '
            f'stroke="{stroke}" stroke-width="1" stroke-dasharray="2,3" />'
        )

        for i in range(units):
            uy = y + margin + i * (blade_h + gap)
            ux = x + margin
            parts.append(
                f'<rect x="{ux}" y="{uy}" width="{blade_w}" height="{blade_h}" rx="1.5" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1" />'
            )
            # Drive bays / vents line
            vent_x1 = ux + 6.0
            vent_x2 = max(vent_x1 + 4.0, ux + blade_w - 20.0)
            vent_y = uy + blade_h / 2.0
            if blade_w > 30.0:
                parts.append(
                    f'<line x1="{vent_x1}" y1="{vent_y}" x2="{vent_x2}" y2="{vent_y}" '
                    f'stroke="{stroke}" stroke-width="1" />'
                )
            # Activity LEDs
            led_x1 = ux + blade_w - 12.0
            led_x2 = ux + blade_w - 6.0
            if blade_w > 20.0 and blade_h >= 6.0:
                parts.append(f'<circle cx="{led_x1}" cy="{vent_y}" r="1.2" fill="{stroke}" />')
                parts.append(f'<circle cx="{led_x2}" cy="{vent_y}" r="1.2" fill="{stroke}" />')

        return "\n".join(parts)

    def render_database(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str,
        stroke_width: float = 2.0,
        num_tiers: int = 3,
    ) -> str:
        """Render a multi-tier database cylinder stack container shape."""
        self._validate_dimensions(w, h)
        tiers = max(1, int(num_tiers))
        ry = min(12.0, h / (tiers * 2.0))
        rx = w / 2.0

        # Body outline with curved bottom cap
        body_d = (
            f"M {x} {y + ry} "
            f"L {x} {y + h - ry} "
            f"A {rx} {ry} 0 0 0 {x + w} {y + h - ry} "
            f"L {x + w} {y + ry} "
            f"A {rx} {ry} 0 0 1 {x} {y + ry} Z"
        )
        parts = [
            f'<path d="{body_d}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        ]

        # Intermediate tier shelf curves
        tier_span = (h - 2 * ry) / tiers
        for k in range(1, tiers):
            tier_y = y + ry + k * tier_span
            parts.append(
                f'<path d="M {x} {tier_y} A {rx} {ry} 0 0 0 {x + w} {tier_y}" '
                f'fill="none" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            )

        # Top rim ellipse
        parts.append(
            f'<ellipse cx="{x + rx}" cy="{y + ry}" rx="{rx}" ry="{ry}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )
        return "\n".join(parts)

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
        if font_size <= 0:
            raise ValueError(f"font_size must be positive, got {font_size}")
        if height <= 0:
            raise ValueError(f"height must be positive, got {height}")

        char_w = font_size * 0.62
        badge_w = max(len(text) * char_w + 2 * padding_x, 24.0)
        rx = height / 2.0
        text_x = x + badge_w / 2.0
        text_y = y + height / 2.0 + font_size * 0.35
        escaped_text = html.escape(text)
        escaped_font_family = html.escape(font_family, quote=True)
        return (
            f'<g class="badge">\n'
            f'  <rect x="{x}" y="{y}" width="{badge_w}" height="{height}" rx="{rx}" fill="{fill}" />\n'
            f'  <text x="{text_x}" y="{text_y}" fill="{text_color}" font-size="{font_size}" '
            f'font-family="{escaped_font_family}" font-weight="600" text-anchor="middle">{escaped_text}</text>\n'
            f'</g>'
        )

    def _canonical_icon_name(self, name: str) -> str:
        key = name.strip().lower()
        if key in self._custom_icons:
            return key
        if key in self._CANONICAL_ICONS:
            return key
        if key in self._ICON_ALIASES:
            return self._ICON_ALIASES[key]
        raise KeyError(
            f"Unknown icon '{name}'. Supported icons: {sorted(self._CANONICAL_ICONS | set(self._custom_icons.keys()))}"
        )

    def has_icon(self, name: str) -> bool:
        """Check if icon or alias is available in library."""
        key = name.strip().lower()
        return (
            key in self._custom_icons
            or key in self._CANONICAL_ICONS
            or key in self._ICON_ALIASES
        )

    def list_icons(self) -> list[str]:
        """Return list of supported canonical icon names."""
        return sorted(self._CANONICAL_ICONS | set(self._custom_icons.keys()))

    def _render_icon_content(
        self, canonical: str, color: str, stroke_width: float
    ) -> str:
        # Custom loaded icons
        if canonical in self._custom_icons:
            content = self._custom_icons[canonical]
            content = content.replace("currentColor", color)
            return content

        # Core & IIoT icons
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
        elif canonical == "scada":
            return (
                f'  <rect x="2" y="3" width="20" height="14" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="21" x2="16" y2="21" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="12" y1="17" x2="12" y2="21" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <polyline points="5 11 8 8 12 12 16 7 19 10" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif canonical == "hmi":
            return (
                f'  <rect x="3" y="4" width="18" height="14" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="6" cy="20" r="1" fill="{color}"/>\n'
                f'  <circle cx="10" cy="20" r="1" fill="{color}"/>\n'
                f'  <circle cx="14" cy="20" r="1" fill="{color}"/>\n'
                f'  <circle cx="18" cy="20" r="1" fill="{color}"/>\n'
                f'  <rect x="6" y="7" width="12" height="8" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "historian":
            return (
                f'  <ellipse cx="12" cy="5" rx="8" ry="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 4 5 V 12 C 4 14 20 14 20 12 V 5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 4 12 V 19 C 4 21 20 21 20 19 V 12" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="16" cy="16" r="4" fill="none" stroke="{color}" stroke-width="1.5"/>\n'
                f'  <polyline points="16 14 16 16 18 16" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "robot":
            return (
                f'  <rect x="5" y="6" width="14" height="12" rx="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="9" cy="11" r="1.5" fill="{color}"/>\n'
                f'  <circle cx="15" cy="11" r="1.5" fill="{color}"/>\n'
                f'  <line x1="9" y1="15" x2="15" y2="15" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="2" x2="12" y2="6" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="2" r="1" fill="{color}"/>\n'
                f'  <line x1="2" y1="12" x2="5" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="19" y1="12" x2="22" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>'
            )

        # Cloud Domain icons
        elif canonical == "vpc":
            return (
                f'  <rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="3,3"/>\n'
                f'  <rect x="7" y="7" width="10" height="10" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="12" r="1.5" fill="{color}"/>'
            )
        elif canonical == "serverless":
            return (
                f'  <path d="M 4 20 L 10 7 L 14 16 L 20 4" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <line x1="12" y1="12" x2="18" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "storage":
            return (
                f'  <ellipse cx="12" cy="6" rx="8" ry="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 4 6 V 18 C 4 20 20 20 20 18 V 6" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 4 12 C 4 14 20 14 20 12" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "api_gateway":
            return (
                f'  <rect x="4" y="3" width="16" height="18" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 8 12 H 16 M 13 9 L 16 12 L 13 15" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif canonical == "cdn":
            return (
                f'  <circle cx="12" cy="12" r="9" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <ellipse cx="12" cy="12" rx="4" ry="9" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="3" y1="12" x2="21" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "firewall":
            return (
                f'  <path d="M 12 2 L 20 6 V 12 C 20 17 12 22 12 22 C 12 22 4 17 4 12 V 6 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
                f'  <line x1="8" y1="11" x2="16" y2="11" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="7" x2="12" y2="15" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "dns":
            return (
                f'  <rect x="3" y="4" width="18" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="3" y="14" width="18" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="7" cy="7" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="7" cy="17" r="1.2" fill="{color}"/>\n'
                f'  <line x1="14" y1="7" x2="18" y2="7" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="14" y1="17" x2="18" y2="17" stroke="{color}" stroke-width="{stroke_width}"/>'
            )

        # AI Domain icons
        elif canonical == "brain":
            return (
                f'  <path d="M 9.5 2 A 4.5 4.5 0 0 0 5 6.5 A 4 4 0 0 0 4 12 A 4 4 0 0 0 7 17 A 3 3 0 0 0 10 20 L 12 20 L 14 20 A 3 3 0 0 0 17 17 A 4 4 0 0 0 20 12 A 4 4 0 0 0 19 6.5 A 4.5 4.5 0 0 0 14.5 2 C 13.5 2 12.5 2.5 12 3.2 C 11.5 2.5 10.5 2 9.5 2 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
                f'  <line x1="12" y1="4" x2="12" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="2,2"/>'
            )
        elif canonical == "model":
            return (
                f'  <path d="M 12 2 L 14 8 L 20 10 L 14 12 L 12 18 L 10 12 L 4 10 L 10 8 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
                f'  <path d="M 18 2 L 18.8 4.2 L 21 5 L 18.8 5.8 L 18 8 L 17.2 5.8 L 15 5 L 17.2 4.2 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
            )
        elif canonical == "agent":
            return (
                f'  <rect x="4" y="8" width="16" height="12" rx="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="4" x2="12" y2="8" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="3" r="1.5" fill="{color}"/>\n'
                f'  <circle cx="9" cy="13" r="1.5" fill="{color}"/>\n'
                f'  <circle cx="15" cy="13" r="1.5" fill="{color}"/>\n'
                f'  <line x1="8" y1="17" x2="16" y2="17" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "chip":
            return (
                f'  <rect x="5" y="5" width="14" height="14" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="9" y="9" width="6" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="9" y1="2" x2="9" y2="5" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="15" y1="2" x2="15" y2="5" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="9" y1="19" x2="9" y2="22" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="15" y1="19" x2="15" y2="22" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="2" y1="9" x2="5" y2="9" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="2" y1="15" x2="5" y2="15" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="19" y1="9" x2="22" y2="9" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="19" y1="15" x2="22" y2="15" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "vector_db":
            return (
                f'  <ellipse cx="12" cy="5" rx="7" ry="2.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 5 5 V 19 C 5 20.5 19 20.5 19 19 V 5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="9" cy="11" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="15" cy="13" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="11" cy="16" r="1.2" fill="{color}"/>\n'
                f'  <line x1="9" y1="11" x2="15" y2="13" stroke="{color}" stroke-width="1.2"/>\n'
                f'  <line x1="15" y1="13" x2="11" y2="16" stroke="{color}" stroke-width="1.2"/>'
            )
        elif canonical == "vision":
            return (
                f'  <path d="M 2 12 C 5 6 19 6 22 12 C 19 18 5 18 2 12 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
                f'  <circle cx="12" cy="12" r="3.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="12" r="1.5" fill="{color}"/>'
            )
        elif canonical == "workflow":
            return (
                f'  <rect x="3" y="3" width="6" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="15" y="3" width="6" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="9" y="15" width="6" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 6 9 V 12 H 12 V 15 M 18 9 V 12 H 12" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )

        # Computer Domain icons
        elif canonical == "server":
            return (
                f'  <rect x="3" y="4" width="18" height="6" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="3" y="14" width="18" height="6" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="6" cy="7" r="1" fill="{color}"/>\n'
                f'  <circle cx="9" cy="7" r="1" fill="{color}"/>\n'
                f'  <circle cx="6" cy="17" r="1" fill="{color}"/>\n'
                f'  <circle cx="9" cy="17" r="1" fill="{color}"/>'
            )
        elif canonical == "terminal":
            return (
                f'  <rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <polyline points="7,9 10,12 7,15" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <line x1="12" y1="15" x2="17" y2="15" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "laptop":
            return (
                f'  <rect x="4" y="5" width="16" height="11" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 2 19 H 22 L 20 16 H 4 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
            )
        elif canonical == "mobile":
            return (
                f'  <rect x="6" y="2" width="12" height="20" rx="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="10" y1="18" x2="14" y2="18" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="10" y1="5" x2="14" y2="5" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "plc":
            return (
                f'  <rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="4" y1="9" x2="20" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="4" x2="8" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="4" x2="12" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="16" y1="4" x2="16" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="8" cy="15" r="1.5" fill="{color}"/>\n'
                f'  <circle cx="12" cy="15" r="1.5" fill="{color}"/>\n'
                f'  <circle cx="16" cy="15" r="1.5" fill="{color}"/>'
            )
        elif canonical == "router":
            return (
                f'  <rect x="3" y="12" width="18" height="8" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="7" y1="12" x2="7" y2="5" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="17" y1="12" x2="17" y2="5" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <circle cx="7" cy="4" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="17" cy="4" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="8" cy="16" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="12" cy="16" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="16" cy="16" r="1.2" fill="{color}"/>'
            )

        # Datacenter Domain icons
        elif canonical == "server_rack":
            return (
                f'  <rect x="4" y="2" width="16" height="20" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="4" y1="7" x2="20" y2="7" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="4" y1="12" x2="20" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="4" y1="17" x2="20" y2="17" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="7" cy="4.5" r="0.8" fill="{color}"/>\n'
                f'  <circle cx="7" cy="9.5" r="0.8" fill="{color}"/>\n'
                f'  <circle cx="7" cy="14.5" r="0.8" fill="{color}"/>\n'
                f'  <circle cx="7" cy="19.5" r="0.8" fill="{color}"/>'
            )
        elif canonical == "cluster":
            return (
                f'  <rect x="3" y="13" width="7" height="7" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="14" y="13" width="7" height="7" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="8.5" y="3" width="7" height="7" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="10" x2="6.5" y2="13" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="10" x2="17.5" y2="13" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "storage_array":
            return (
                f'  <rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="3" y1="9" x2="21" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="3" y1="15" x2="21" y2="15" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="6" cy="6" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="6" cy="12" r="1.2" fill="{color}"/>\n'
                f'  <circle cx="6" cy="18" r="1.2" fill="{color}"/>\n'
                f'  <line x1="10" y1="6" x2="18" y2="6" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="10" y1="12" x2="18" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="10" y1="18" x2="18" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "cooling":
            return (
                f'  <circle cx="12" cy="12" r="9" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 12 12 A 4 4 0 0 1 12 4 A 4 4 0 0 1 15 11 M 12 12 A 4 4 0 0 1 19 15 A 4 4 0 0 1 11 16 M 12 12 A 4 4 0 0 1 5 9 A 4 4 0 0 1 13 8" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "ups":
            return (
                f'  <rect x="4" y="5" width="16" height="15" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="2" x2="8" y2="5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="16" y1="2" x2="16" y2="5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <polygon points="12,8 9,13 12,13 11,17 15,12 12,12" fill="{color}"/>'
            )
        elif canonical == "container":
            return (
                f'  <path d="M 3 7 L 12 2 L 21 7 L 12 12 Z M 3 7 V 16 L 12 21 V 12 M 21 7 V 16 L 12 21" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
            )
        elif canonical == "kubernetes":
            return (
                f'  <circle cx="12" cy="12" r="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 12 2 V 8 M 12 16 V 22 M 2 12 H 8 M 16 12 H 22 M 5 5 L 9 9 M 15 15 L 19 19 M 19 5 L 15 9 M 9 15 L 5 19" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )

        # Business Process Domain icons
        elif canonical == "user":
            return (
                f'  <circle cx="12" cy="7" r="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 5 21 C 5 16.5 8 14 12 14 C 16 14 19 16.5 19 21" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "document":
            return (
                f'  <path d="M 14 2 H 6 A 2 2 0 0 0 4 4 V 20 A 2 2 0 0 0 6 22 H 18 A 2 2 0 0 0 20 20 V 8 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
                f'  <polyline points="14,2 14,8 20,8" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="13" x2="16" y2="13" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="8" y1="17" x2="14" y2="17" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "decision":
            return (
                f'  <path d="M 12 2 L 21 12 L 12 22 L 3 12 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
                f'  <line x1="12" y1="8" x2="12" y2="13" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <circle cx="12" cy="16" r="1" fill="{color}"/>'
            )
        elif canonical == "message":
            return (
                f'  <rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <polyline points="4,6 12,13 20,6" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif canonical == "shield":
            return (
                f'  <path d="M 12 2 L 20 6 V 12 C 20 17 12 22 12 22 C 12 22 4 17 4 12 V 6 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
                f'  <polyline points="9,12 11,14 15,10" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif canonical == "analytics":
            return (
                f'  <line x1="4" y1="20" x2="20" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="4" y1="4" x2="4" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <rect x="7" y="12" width="3" height="8" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="12" y="8" width="3" height="12" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="17" y="4" width="3" height="16" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )

        # Cybersecurity Domain icons
        elif canonical == "lock":
            return (
                f'  <rect x="5" y="11" width="14" height="10" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 8 11 V 7 A 4 4 0 0 1 16 7 V 11" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="16" r="1.5" fill="{color}"/>'
            )
        elif canonical == "key":
            return (
                f'  <circle cx="8" cy="14" r="5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="10" x2="21" y2="3" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="17" y1="5" x2="19" y2="7" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="19" y1="7" x2="21" y2="9" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
            )
        elif canonical == "shield_check":
            return (
                f'  <path d="M 12 2 L 20 6 V 12 C 20 17 12 22 12 22 C 12 22 4 17 4 12 V 6 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
                f'  <polyline points="9,12 11,14 15,9" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif canonical == "siem":
            return (
                f'  <circle cx="12" cy="12" r="9" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="12" r="5" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="2 2"/>\n'
                f'  <line x1="12" y1="12" x2="18" y2="8" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <circle cx="12" cy="12" r="2" fill="{color}"/>'
            )
        elif canonical == "soc":
            return (
                f'  <rect x="3" y="4" width="18" height="12" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="20" x2="16" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <line x1="12" y1="16" x2="12" y2="20" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="10" r="2.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="10" r="0.8" fill="{color}"/>'
            )
        elif canonical == "malware_scan":
            return (
                f'  <path d="M 4 8 V 4 H 8" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <path d="M 16 4 H 20 V 8" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <path d="M 4 16 V 20 H 8" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <path d="M 16 20 H 20 V 16" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <circle cx="12" cy="12" r="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="12" x2="6" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="16" y1="12" x2="18" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="8" x2="12" y2="6" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="16" x2="12" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "vault":
            return (
                f'  <rect x="3" y="3" width="18" height="18" rx="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="12" r="5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="7" x2="12" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="15" x2="12" y2="17" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="7" y1="12" x2="9" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="15" y1="12" x2="17" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="12" r="1.5" fill="{color}"/>'
            )
        elif canonical == "honeypot":
            return (
                f'  <ellipse cx="12" cy="5" rx="6" ry="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 6 5 C 4 10 4 17 7 20 C 9 22 15 22 17 20 C 20 17 20 10 18 5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 9 10 C 11 12 13 12 15 10" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )

        # Network Engineering Domain icons
        elif canonical == "switch":
            return (
                f'  <rect x="2" y="6" width="20" height="12" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="6" y1="10" x2="13" y2="10" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <polyline points="11,8 13,10 11,12" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <line x1="18" y1="14" x2="11" y2="14" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <polyline points="13,12 11,14 13,16" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif canonical == "core_router":
            return (
                f'  <circle cx="12" cy="12" r="9.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="12" y1="4.5" x2="12" y2="19.5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <polyline points="9.5,7 12,4.5 14.5,7" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <polyline points="9.5,17 12,19.5 14.5,17" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <line x1="4.5" y1="12" x2="19.5" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <polyline points="7,9.5 4.5,12 7,14.5" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <polyline points="17,9.5 19.5,12 17,14.5" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif canonical == "bgp":
            return (
                f'  <circle cx="6" cy="7" r="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="18" cy="7" r="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <circle cx="12" cy="18" r="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="9" y1="7" x2="15" y2="7" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="9.5" x2="10.5" y2="15.5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="16" y1="9.5" x2="13.5" y2="15.5" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "mpls":
            return (
                f'  <rect x="3" y="5" width="8" height="6" rx="1.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="13" y="5" width="8" height="6" rx="1.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="8" y="14" width="8" height="6" rx="1.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 7 11 V 13 H 10 V 14" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <path d="M 17 11 V 13 H 14 V 14" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "firewall_ha":
            return (
                f'  <rect x="3" y="4" width="8" height="16" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="13" y="4" width="8" height="16" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="3" y1="9" x2="11" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="3" y1="15" x2="11" y2="15" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="13" y1="9" x2="21" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="13" y1="15" x2="21" y2="15" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "load_balancer":
            return (
                f'  <rect x="3" y="10" width="5" height="5" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="8" y1="12.5" x2="13" y2="12.5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="13" y1="6" x2="13" y2="19" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="13" y1="6" x2="16" y2="6" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="13" y1="12.5" x2="16" y2="12.5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <line x1="13" y1="19" x2="16" y2="19" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="16" y="4.5" width="5" height="3" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="16" y="11" width="5" height="3" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="16" y="17.5" width="5" height="3" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "patch_panel":
            return (
                f'  <rect x="2" y="7" width="20" height="10" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="4" y="10" width="3" height="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="8.5" y="10" width="3" height="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="13" y="10" width="3" height="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
                f'  <rect x="17" y="10" width="3" height="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
            )
        elif canonical == "fiber_optic":
            return (
                f'  <path d="M 2 17 C 8 17 9 7 15 7 H 22" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <path d="M 2 20 C 10 20 11 12 17 12 H 22" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
                f'  <circle cx="21" cy="7" r="1.5" fill="{color}"/>\n'
                f'  <circle cx="21" cy="12" r="1.2" fill="{color}"/>'
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
        """Render an icon inside a positioned and scaled SVG group."""
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")
        canonical = self._canonical_icon_name(name)
        scale = size / 24.0
        content = self._render_icon_content(canonical, color, stroke_width)
        return (
            f'<g class="icon icon-{canonical}" transform="translate({x}, {y}) scale({scale})">\n'
            f'{content}\n'
            f'</g>'
        )

    # Convenience helper methods
    def render_sensor(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("sensor", x, y, size, color, stroke_width)

    def render_gateway(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("gateway", x, y, size, color, stroke_width)

    def render_edge(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("edge", x, y, size, color, stroke_width)

    def render_broker(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("broker", x, y, size, color, stroke_width)

    def render_database_icon(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("database", x, y, size, color, stroke_width)

    def render_influx_icon(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("influx", x, y, size, color, stroke_width)

    render_influx = render_database_icon

    def render_queue(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("queue", x, y, size, color, stroke_width)

    def render_kafka(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("kafka", x, y, size, color, stroke_width)

    def render_cloud_icon(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("cloud", x, y, size, color, stroke_width)

    def render_dashboard(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("dashboard", x, y, size, color, stroke_width)

    def render_grafana(self, x: float, y: float, size: float = 24.0, color: str = "#FFC000", stroke_width: float = 2.0) -> str:
        return self.render_icon("grafana", x, y, size, color, stroke_width)


# Alias per plan interface specification
ShapeRenderer = ShapeLibrary
