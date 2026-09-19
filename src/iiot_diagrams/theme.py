"""Theme presets and color system for IIoT diagrams."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Theme:
    """Configurable color palette and typography theme for diagram styling."""

    name: str
    background: str
    group_bg: str
    group_stroke: str
    node_fill: str
    node_stroke: str
    accent: str
    text: str
    subtext: str
    edge_color: str
    font_family: str = (
        "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    )

    @property
    def accent_gold(self) -> str:
        """Alias for accent color matching corporate design specifications."""
        return self.accent

    @property
    def text_color(self) -> str:
        """Alias for primary text color."""
        return self.text

    @property
    def subtext_color(self) -> str:
        """Alias for secondary text color."""
        return self.subtext


THEMES: dict[str, Theme] = {
    "iiot_dark_gold": Theme(
        name="iiot_dark_gold",
        background="#000000",
        group_bg="#1A1A1E",
        group_stroke="#2E2E36",
        node_fill="#24242A",
        node_stroke="#FFC000",
        accent="#FFC000",
        text="#FFFFFF",
        subtext="#A0A0AA",
        edge_color="#FFC000",
    ),
    "iiot_light": Theme(
        name="iiot_light",
        background="#FFFFFF",
        group_bg="#F4F4F6",
        group_stroke="#E0E0E6",
        node_fill="#FFFFFF",
        node_stroke="#0066CC",
        accent="#0066CC",
        text="#111111",
        subtext="#666666",
        edge_color="#0066CC",
    ),
    "blueprint": Theme(
        name="blueprint",
        background="#0B1E36",
        group_bg="#0E2A4D",
        group_stroke="#1D4573",
        node_fill="#133663",
        node_stroke="#4DA6FF",
        accent="#00D2FF",
        text="#FFFFFF",
        subtext="#8CB9E5",
        edge_color="#00D2FF",
    ),
    "cyber_slate": Theme(
        name="cyber_slate",
        background="#181B20",
        group_bg="#22262E",
        group_stroke="#363C48",
        node_fill="#2B313B",
        node_stroke="#00E5A3",
        accent="#00E5A3",
        text="#F0F3F6",
        subtext="#94A3B8",
        edge_color="#00E5A3",
    ),
}

# Theme aliases
THEMES["dark"] = THEMES["iiot_dark_gold"]
THEMES["light"] = THEMES["iiot_light"]

IIOT_DARK_GOLD = THEMES["iiot_dark_gold"]
IIOT_LIGHT = THEMES["iiot_light"]
BLUEPRINT = THEMES["blueprint"]
CYBER_SLATE = THEMES["cyber_slate"]


def get_theme(name: str = "iiot_dark_gold") -> Theme:
    """Retrieve theme by name with case-insensitivity and default fallback."""
    if not isinstance(name, str):
        raise TypeError(f"Theme name must be a str, got {type(name).__name__}")
    key = name.strip().lower()
    return THEMES.get(key, THEMES["iiot_dark_gold"])


def register_theme(theme: Theme) -> None:
    """Register a custom Theme in the global theme registry."""
    if not isinstance(theme, Theme):
        raise TypeError(f"Expected Theme instance, got {type(theme).__name__}")
    if not theme.name or not isinstance(theme.name, str) or not theme.name.strip():
        raise ValueError("Theme name must be a non-empty string")
    key = theme.name.strip().lower()
    THEMES[key] = theme
    THEMES[theme.name] = theme
