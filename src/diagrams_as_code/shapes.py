"""Vector shape primitives and built-in IIoT / Domain vector icon library."""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import ClassVar, Optional
from diagrams_as_code.icon_glyphs import GLYPHS


class ShapeLibrary:
    """Library for rendering crisp vector shape primitives and domain vector icons."""

    _ICON_CATALOG: ClassVar[dict[str, tuple[str, str]]] = {
        "agent": ("ai", "Autonomous AI agent / multi-step orchestrator"),
        "analytics": ("business_process", "KPI reporting / business intelligence analytics"),
        "api_gateway": ("cloud", "API Gateway ingress proxy & route dispatcher"),
        "bgp": ("network_engineering", "Border Gateway Protocol mesh / Autonomous System"),
        "brain": ("ai", "Deep learning neural network / cognitive model"),
        "broker": ("iiot", "Enterprise MQTT broker cluster / UNS message broker"),
        "cdn": ("cloud", "Content Delivery Network global edge pop"),
        "chip": ("ai", "Hardware accelerator / GPU / NPU tensor core"),
        "cloud": ("cloud", "Cloud infrastructure platform / global network"),
        "cluster": ("datacenter", "High-availability multi-node cluster"),
        "container": ("datacenter", "OCI container runtime / microservice unit"),
        "cooling": ("datacenter", "HVAC in-row precision cooling & airflow"),
        "core_router": ("network_engineering", "Autonomous system core router / BGP gateway"),
        "dashboard": ("iiot", "Operational metrics dashboard / monitoring panel"),
        "database": ("iiot", "Relational or time-series database store"),
        "decision": ("business_process", "Business rule decision gateway / approval fork"),
        "dns": ("cloud", "Domain Name System authoritative resolver"),
        "document": ("business_process", "Business contract / structured document / record"),
        "fiber_optic": ("network_engineering", "High-speed optical fiber backbone link"),
        "firewall": ("cloud", "Stateful network perimeter firewall / WAF"),
        "firewall_ha": ("network_engineering", "High-Availability redundant stateful firewall pair"),
        "gateway": ("iiot", "Industrial IoT edge gateway / protocol converter"),
        "historian": ("iiot", "Process telemetry time-series enterprise historian"),
        "hmi": ("iiot", "Human-Machine Interface touch panel operator console"),
        "honeypot": ("cybersecurity", "Deception honeypot trap & decoy sensor"),
        "key": ("cybersecurity", "Secret key / PKI private key & certificate token"),
        "kubernetes": ("datacenter", "Kubernetes container orchestration cluster"),
        "laptop": ("computer", "Client workstation / engineer laptop"),
        "load_balancer": ("network_engineering", "Traffic distribution load balancer appliance"),
        "lock": ("cybersecurity", "Cryptographic lock / data encryption at rest & in transit"),
        "malware_scan": ("cybersecurity", "Antivirus / EDR malware scanning & threat hunter"),
        "message": ("business_process", "Notification dispatch / event message queue"),
        "mobile": ("computer", "Mobile smartphone / field tablet client"),
        "model": ("ai", "Large language model / generative AI foundation"),
        "mpls": ("network_engineering", "Multi-Protocol Label Switching (MPLS) provider network"),
        "patch_panel": ("network_engineering", "19-inch structured cabling patch panel"),
        "plc": ("computer", "Programmable Logic Controller / industrial IPC"),
        "queue": ("iiot", "Message queue / ordered work backlog"),
        "robot": ("iiot", "Industrial robotic manipulator / automated assembly cell"),
        "router": ("computer", "Network switch / wireless edge router"),
        "scada": ("iiot", "Supervisory Control and Data Acquisition host"),
        "sensor": ("iiot", "Field instrumentation transducer / IoT sensor node"),
        "server": ("computer", "Standard compute host server / worker node"),
        "server_rack": ("datacenter", "High-density 42U equipment rack enclosure"),
        "serverless": ("cloud", "Event-driven compute / Lambda micro-functions"),
        "shield": ("business_process", "Regulatory compliance & security audit gate"),
        "shield_check": ("cybersecurity", "Verified security posture / compliance gate"),
        "siem": ("cybersecurity", "SIEM radar telemetry & security analytics engine"),
        "soc": ("cybersecurity", "Security Operations Center monitoring console"),
        "storage": ("cloud", "Distributed object store / S3 storage bucket"),
        "storage_array": ("datacenter", "Enterprise SAN / NAS storage shelf"),
        "switch": ("network_engineering", "Layer 2/3 Ethernet network switch"),
        "terminal": ("computer", "Developer CLI / terminal console environment"),
        "ups": ("datacenter", "Uninterruptible Power Supply & battery backup"),
        "user": ("business_process", "Human stakeholder / operator / actor"),
        "vault": ("cybersecurity", "Hardware Security Module (HSM) / secrets vault"),
        "vector_db": ("ai", "High-dimensional vector embedding database"),
        "vision": ("ai", "Computer vision perception & object detector"),
        "vpc": ("cloud", "Isolated Virtual Private Cloud network boundary"),
        "workflow": ("ai", "Automated pipeline DAG / training workflow"),
    }

    #: Canonical icon names, derived from the catalog so the engine, the
    #: generated ``icons/`` tree and its manifests can never disagree.
    #: Regenerate the tree with ``uv run python tools/generate_icons.py``.
    _CANONICAL_ICONS: ClassVar[frozenset[str]] = frozenset(_ICON_CATALOG)

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

        glyph = GLYPHS.get(canonical)
        if glyph is None:
            raise KeyError(f"Unhandled icon '{canonical}'")
        return glyph(color, stroke_width)

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
