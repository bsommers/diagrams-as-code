"""SVG bodies for the built-in icons, drawn on a 24x24 grid.

Each glyph takes the stroke/fill color and stroke width and returns the
markup that ``ShapeLibrary.render_icon`` wraps in a positioned ``<g>``.
Icon names, domains and descriptions live in ``ShapeLibrary._ICON_CATALOG``.
"""
from __future__ import annotations

from typing import Callable

GlyphFn = Callable[[str, float], str]


def _sensor(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 4 4 A 11 11 0 0 1 20 4" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <path d="M 7 7 A 7 7 0 0 1 17 7" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <rect x="10" y="10" width="4" height="11" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="8" y1="17" x2="16" y2="17" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _gateway(color: str, stroke_width: float) -> str:
    return (
        f'  <line x1="6" y1="9" x2="6" y2="3" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="18" y1="9" x2="18" y2="3" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <rect x="3" y="9" width="18" height="12" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="7" cy="15" r="1.5" fill="{color}"/>\n'
        f'  <circle cx="12" cy="15" r="1.5" fill="{color}"/>\n'
        f'  <circle cx="17" cy="15" r="1.5" fill="{color}"/>'
    )


def _broker(color: str, stroke_width: float) -> str:
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


def _database(color: str, stroke_width: float) -> str:
    return (
        f'  <ellipse cx="12" cy="6" rx="8" ry="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 4 12 C 4 15 20 15 20 12" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 4 18 C 4 21 20 21 20 18" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="4" y1="6" x2="4" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="20" y1="6" x2="20" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _queue(color: str, stroke_width: float) -> str:
    return (
        f'  <line x1="2" y1="6" x2="18" y2="6" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="2" y1="18" x2="18" y2="18" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="6" y1="6" x2="6" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="11" y1="6" x2="11" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="16" y1="6" x2="16" y2="18" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 18 12 H 22 M 20 9 L 23 12 L 20 15" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _cloud(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 6.5 19 H 17.5 A 4 4 0 0 0 17.5 11 A 5.5 5.5 0 0 0 7 12 A 4 4 0 0 0 6.5 19 Z" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
    )


def _dashboard(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="3" width="18" height="15" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="3" y1="8" x2="21" y2="8" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <polyline points="6,15 10,11 13,13 17,9" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'  <line x1="9" y1="21" x2="15" y2="21" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="12" y1="18" x2="12" y2="21" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _scada(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="2" y="3" width="20" height="14" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="8" y1="21" x2="16" y2="21" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="12" y1="17" x2="12" y2="21" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <polyline points="5 11 8 8 12 12 16 7 19 10" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _hmi(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="4" width="18" height="14" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="6" cy="20" r="1" fill="{color}"/>\n'
        f'  <circle cx="10" cy="20" r="1" fill="{color}"/>\n'
        f'  <circle cx="14" cy="20" r="1" fill="{color}"/>\n'
        f'  <circle cx="18" cy="20" r="1" fill="{color}"/>\n'
        f'  <rect x="6" y="7" width="12" height="8" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _historian(color: str, stroke_width: float) -> str:
    return (
        f'  <ellipse cx="12" cy="5" rx="8" ry="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 4 5 V 12 C 4 14 20 14 20 12 V 5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 4 12 V 19 C 4 21 20 21 20 19 V 12" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="16" cy="16" r="4" fill="none" stroke="{color}" stroke-width="1.5"/>\n'
        f'  <polyline points="16 14 16 16 18 16" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _robot(color: str, stroke_width: float) -> str:
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


def _vpc(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="3,3"/>\n'
        f'  <rect x="7" y="7" width="10" height="10" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="12" r="1.5" fill="{color}"/>'
    )


def _serverless(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 4 20 L 10 7 L 14 16 L 20 4" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'  <line x1="12" y1="12" x2="18" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _storage(color: str, stroke_width: float) -> str:
    return (
        f'  <ellipse cx="12" cy="6" rx="8" ry="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 4 6 V 18 C 4 20 20 20 20 18 V 6" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 4 12 C 4 14 20 14 20 12" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _api_gateway(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="4" y="3" width="16" height="18" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 8 12 H 16 M 13 9 L 16 12 L 13 15" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _cdn(color: str, stroke_width: float) -> str:
    return (
        f'  <circle cx="12" cy="12" r="9" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <ellipse cx="12" cy="12" rx="4" ry="9" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="3" y1="12" x2="21" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _firewall(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 12 2 L 20 6 V 12 C 20 17 12 22 12 22 C 12 22 4 17 4 12 V 6 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
        f'  <line x1="8" y1="11" x2="16" y2="11" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="12" y1="7" x2="12" y2="15" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _dns(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="4" width="18" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="3" y="14" width="18" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="7" cy="7" r="1.2" fill="{color}"/>\n'
        f'  <circle cx="7" cy="17" r="1.2" fill="{color}"/>\n'
        f'  <line x1="14" y1="7" x2="18" y2="7" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="14" y1="17" x2="18" y2="17" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _brain(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 9.5 2 A 4.5 4.5 0 0 0 5 6.5 A 4 4 0 0 0 4 12 A 4 4 0 0 0 7 17 A 3 3 0 0 0 10 20 L 12 20 L 14 20 A 3 3 0 0 0 17 17 A 4 4 0 0 0 20 12 A 4 4 0 0 0 19 6.5 A 4.5 4.5 0 0 0 14.5 2 C 13.5 2 12.5 2.5 12 3.2 C 11.5 2.5 10.5 2 9.5 2 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
        f'  <line x1="12" y1="4" x2="12" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="2,2"/>'
    )


def _model(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 12 2 L 14 8 L 20 10 L 14 12 L 12 18 L 10 12 L 4 10 L 10 8 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
        f'  <path d="M 18 2 L 18.8 4.2 L 21 5 L 18.8 5.8 L 18 8 L 17.2 5.8 L 15 5 L 17.2 4.2 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
    )


def _agent(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="4" y="8" width="16" height="12" rx="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="12" y1="4" x2="12" y2="8" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="3" r="1.5" fill="{color}"/>\n'
        f'  <circle cx="9" cy="13" r="1.5" fill="{color}"/>\n'
        f'  <circle cx="15" cy="13" r="1.5" fill="{color}"/>\n'
        f'  <line x1="8" y1="17" x2="16" y2="17" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _chip(color: str, stroke_width: float) -> str:
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


def _vector_db(color: str, stroke_width: float) -> str:
    return (
        f'  <ellipse cx="12" cy="5" rx="7" ry="2.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 5 5 V 19 C 5 20.5 19 20.5 19 19 V 5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="9" cy="11" r="1.2" fill="{color}"/>\n'
        f'  <circle cx="15" cy="13" r="1.2" fill="{color}"/>\n'
        f'  <circle cx="11" cy="16" r="1.2" fill="{color}"/>\n'
        f'  <line x1="9" y1="11" x2="15" y2="13" stroke="{color}" stroke-width="1.2"/>\n'
        f'  <line x1="15" y1="13" x2="11" y2="16" stroke="{color}" stroke-width="1.2"/>'
    )


def _vision(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 2 12 C 5 6 19 6 22 12 C 19 18 5 18 2 12 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
        f'  <circle cx="12" cy="12" r="3.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="12" r="1.5" fill="{color}"/>'
    )


def _workflow(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="3" width="6" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="15" y="3" width="6" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="9" y="15" width="6" height="6" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 6 9 V 12 H 12 V 15 M 18 9 V 12 H 12" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _server(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="4" width="18" height="6" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="3" y="14" width="18" height="6" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="6" cy="7" r="1" fill="{color}"/>\n'
        f'  <circle cx="9" cy="7" r="1" fill="{color}"/>\n'
        f'  <circle cx="6" cy="17" r="1" fill="{color}"/>\n'
        f'  <circle cx="9" cy="17" r="1" fill="{color}"/>'
    )


def _terminal(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <polyline points="7,9 10,12 7,15" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'  <line x1="12" y1="15" x2="17" y2="15" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _laptop(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="4" y="5" width="16" height="11" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 2 19 H 22 L 20 16 H 4 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
    )


def _mobile(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="6" y="2" width="12" height="20" rx="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="10" y1="18" x2="14" y2="18" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="10" y1="5" x2="14" y2="5" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _plc(color: str, stroke_width: float) -> str:
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


def _router(color: str, stroke_width: float) -> str:
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


def _server_rack(color: str, stroke_width: float) -> str:
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


def _cluster(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="13" width="7" height="7" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="14" y="13" width="7" height="7" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="8.5" y="3" width="7" height="7" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="12" y1="10" x2="6.5" y2="13" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="12" y1="10" x2="17.5" y2="13" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _storage_array(color: str, stroke_width: float) -> str:
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


def _cooling(color: str, stroke_width: float) -> str:
    return (
        f'  <circle cx="12" cy="12" r="9" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 12 12 A 4 4 0 0 1 12 4 A 4 4 0 0 1 15 11 M 12 12 A 4 4 0 0 1 19 15 A 4 4 0 0 1 11 16 M 12 12 A 4 4 0 0 1 5 9 A 4 4 0 0 1 13 8" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _ups(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="4" y="5" width="16" height="15" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="8" y1="2" x2="8" y2="5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="16" y1="2" x2="16" y2="5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <polygon points="12,8 9,13 12,13 11,17 15,12 12,12" fill="{color}"/>'
    )


def _container(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 3 7 L 12 2 L 21 7 L 12 12 Z M 3 7 V 16 L 12 21 V 12 M 21 7 V 16 L 12 21" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
    )


def _kubernetes(color: str, stroke_width: float) -> str:
    return (
        f'  <circle cx="12" cy="12" r="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 12 2 V 8 M 12 16 V 22 M 2 12 H 8 M 16 12 H 22 M 5 5 L 9 9 M 15 15 L 19 19 M 19 5 L 15 9 M 9 15 L 5 19" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _user(color: str, stroke_width: float) -> str:
    return (
        f'  <circle cx="12" cy="7" r="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 5 21 C 5 16.5 8 14 12 14 C 16 14 19 16.5 19 21" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _document(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 14 2 H 6 A 2 2 0 0 0 4 4 V 20 A 2 2 0 0 0 6 22 H 18 A 2 2 0 0 0 20 20 V 8 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
        f'  <polyline points="14,2 14,8 20,8" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="8" y1="13" x2="16" y2="13" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="8" y1="17" x2="14" y2="17" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _decision(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 12 2 L 21 12 L 12 22 L 3 12 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
        f'  <line x1="12" y1="8" x2="12" y2="13" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <circle cx="12" cy="16" r="1" fill="{color}"/>'
    )


def _message(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <polyline points="4,6 12,13 20,6" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _shield(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 12 2 L 20 6 V 12 C 20 17 12 22 12 22 C 12 22 4 17 4 12 V 6 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
        f'  <polyline points="9,12 11,14 15,10" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _analytics(color: str, stroke_width: float) -> str:
    return (
        f'  <line x1="4" y1="20" x2="20" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="4" y1="4" x2="4" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <rect x="7" y="12" width="3" height="8" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="12" y="8" width="3" height="12" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="17" y="4" width="3" height="16" rx="0.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _lock(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="5" y="11" width="14" height="10" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 8 11 V 7 A 4 4 0 0 1 16 7 V 11" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="16" r="1.5" fill="{color}"/>'
    )


def _key(color: str, stroke_width: float) -> str:
    return (
        f'  <circle cx="8" cy="14" r="5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="12" y1="10" x2="21" y2="3" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="17" y1="5" x2="19" y2="7" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="19" y1="7" x2="21" y2="9" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
    )


def _shield_check(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 12 2 L 20 6 V 12 C 20 17 12 22 12 22 C 12 22 4 17 4 12 V 6 Z" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>\n'
        f'  <polyline points="9,12 11,14 15,9" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _siem(color: str, stroke_width: float) -> str:
    return (
        f'  <circle cx="12" cy="12" r="9" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="12" r="5" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="2 2"/>\n'
        f'  <line x1="12" y1="12" x2="18" y2="8" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <circle cx="12" cy="12" r="2" fill="{color}"/>'
    )


def _soc(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="4" width="18" height="12" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="8" y1="20" x2="16" y2="20" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <line x1="12" y1="16" x2="12" y2="20" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="10" r="2.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="10" r="0.8" fill="{color}"/>'
    )


def _malware_scan(color: str, stroke_width: float) -> str:
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


def _vault(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="3" width="18" height="18" rx="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="12" r="5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="12" y1="7" x2="12" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="12" y1="15" x2="12" y2="17" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="7" y1="12" x2="9" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="15" y1="12" x2="17" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="12" r="1.5" fill="{color}"/>'
    )


def _honeypot(color: str, stroke_width: float) -> str:
    return (
        f'  <ellipse cx="12" cy="5" rx="6" ry="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 6 5 C 4 10 4 17 7 20 C 9 22 15 22 17 20 C 20 17 20 10 18 5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 9 10 C 11 12 13 12 15 10" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _switch(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="2" y="6" width="20" height="12" rx="2" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="6" y1="10" x2="13" y2="10" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <polyline points="11,8 13,10 11,12" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'  <line x1="18" y1="14" x2="11" y2="14" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <polyline points="13,12 11,14 13,16" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _core_router(color: str, stroke_width: float) -> str:
    return (
        f'  <circle cx="12" cy="12" r="9.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="12" y1="4.5" x2="12" y2="19.5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <polyline points="9.5,7 12,4.5 14.5,7" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'  <polyline points="9.5,17 12,19.5 14.5,17" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'  <line x1="4.5" y1="12" x2="19.5" y2="12" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <polyline points="7,9.5 4.5,12 7,14.5" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'  <polyline points="17,9.5 19.5,12 17,14.5" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _bgp(color: str, stroke_width: float) -> str:
    return (
        f'  <circle cx="6" cy="7" r="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="18" cy="7" r="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <circle cx="12" cy="18" r="3" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="9" y1="7" x2="15" y2="7" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="8" y1="9.5" x2="10.5" y2="15.5" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="16" y1="9.5" x2="13.5" y2="15.5" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _mpls(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="5" width="8" height="6" rx="1.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="13" y="5" width="8" height="6" rx="1.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="8" y="14" width="8" height="6" rx="1.5" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 7 11 V 13 H 10 V 14" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <path d="M 17 11 V 13 H 14 V 14" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _firewall_ha(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="3" y="4" width="8" height="16" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="13" y="4" width="8" height="16" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="3" y1="9" x2="11" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="3" y1="15" x2="11" y2="15" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="13" y1="9" x2="21" y2="9" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <line x1="13" y1="15" x2="21" y2="15" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _load_balancer(color: str, stroke_width: float) -> str:
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


def _patch_panel(color: str, stroke_width: float) -> str:
    return (
        f'  <rect x="2" y="7" width="20" height="10" rx="1" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="4" y="10" width="3" height="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="8.5" y="10" width="3" height="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="13" y="10" width="3" height="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'  <rect x="17" y="10" width="3" height="4" fill="none" stroke="{color}" stroke-width="{stroke_width}"/>'
    )


def _fiber_optic(color: str, stroke_width: float) -> str:
    return (
        f'  <path d="M 2 17 C 8 17 9 7 15 7 H 22" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <path d="M 2 20 C 10 20 11 12 17 12 H 22" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>\n'
        f'  <circle cx="21" cy="7" r="1.5" fill="{color}"/>\n'
        f'  <circle cx="21" cy="12" r="1.2" fill="{color}"/>'
    )


GLYPHS: dict[str, GlyphFn] = {
    "sensor": _sensor,
    "gateway": _gateway,
    "broker": _broker,
    "database": _database,
    "queue": _queue,
    "cloud": _cloud,
    "dashboard": _dashboard,
    "scada": _scada,
    "hmi": _hmi,
    "historian": _historian,
    "robot": _robot,
    "vpc": _vpc,
    "serverless": _serverless,
    "storage": _storage,
    "api_gateway": _api_gateway,
    "cdn": _cdn,
    "firewall": _firewall,
    "dns": _dns,
    "brain": _brain,
    "model": _model,
    "agent": _agent,
    "chip": _chip,
    "vector_db": _vector_db,
    "vision": _vision,
    "workflow": _workflow,
    "server": _server,
    "terminal": _terminal,
    "laptop": _laptop,
    "mobile": _mobile,
    "plc": _plc,
    "router": _router,
    "server_rack": _server_rack,
    "cluster": _cluster,
    "storage_array": _storage_array,
    "cooling": _cooling,
    "ups": _ups,
    "container": _container,
    "kubernetes": _kubernetes,
    "user": _user,
    "document": _document,
    "decision": _decision,
    "message": _message,
    "shield": _shield,
    "analytics": _analytics,
    "lock": _lock,
    "key": _key,
    "shield_check": _shield_check,
    "siem": _siem,
    "soc": _soc,
    "malware_scan": _malware_scan,
    "vault": _vault,
    "honeypot": _honeypot,
    "switch": _switch,
    "core_router": _core_router,
    "bgp": _bgp,
    "mpls": _mpls,
    "firewall_ha": _firewall_ha,
    "load_balancer": _load_balancer,
    "patch_panel": _patch_panel,
    "fiber_optic": _fiber_optic,
}
