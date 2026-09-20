"""Theme presets and color system for IIoT diagrams."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass(frozen=True)
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


def _build_default_themes() -> dict[str, Theme]:
    defaults = {
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
        "nord": Theme(
            name="nord",
            background="#2E3440",
            group_bg="#3B4252",
            group_stroke="#4C566A",
            node_fill="#434C5E",
            node_stroke="#88C0D0",
            accent="#88C0D0",
            text="#ECEFF4",
            subtext="#D8DEE9",
            edge_color="#81A1C1",
        ),
        "emerald": Theme(
            name="emerald",
            background="#0B1713",
            group_bg="#11241E",
            group_stroke="#1D3D32",
            node_fill="#163028",
            node_stroke="#10B981",
            accent="#10B981",
            text="#ECFDF5",
            subtext="#6EE7B7",
            edge_color="#10B981",
        ),
        "crimson": Theme(
            name="crimson",
            background="#1A0F14",
            group_bg="#26171E",
            group_stroke="#3F2432",
            node_fill="#331E29",
            node_stroke="#F43F5E",
            accent="#F43F5E",
            text="#FFF1F2",
            subtext="#FDA4AF",
            edge_color="#FB7185",
        ),
        "monochrome": Theme(
            name="monochrome",
            background="#FAFAFA",
            group_bg="#F4F4F5",
            group_stroke="#E4E4E7",
            node_fill="#FFFFFF",
            node_stroke="#18181B",
            accent="#18181B",
            text="#09090B",
            subtext="#71717A",
            edge_color="#27272A",
        ),
        "solarized_light": Theme(
            name="solarized_light",
            background="#FDF6E3",
            group_bg="#EEE8D5",
            group_stroke="#93A1A1",
            node_fill="#FFFFFF",
            node_stroke="#268BD2",
            accent="#268BD2",
            text="#073642",
            subtext="#586E75",
            edge_color="#268BD2",
        ),
        "pastel_light": Theme(
            name="pastel_light",
            background="#EFF1F5",
            group_bg="#E6E9EF",
            group_stroke="#CCD0DA",
            node_fill="#FFFFFF",
            node_stroke="#7287FD",
            accent="#7287FD",
            text="#4C4F69",
            subtext="#6C6F85",
            edge_color="#1E66F5",
        ),
        "dracula": Theme(
            name="dracula",
            background="#282A36",
            group_bg="#343746",
            group_stroke="#44475A",
            node_fill="#383A59",
            node_stroke="#BD93F9",
            accent="#FF79C6",
            text="#F8F8F2",
            subtext="#6272A4",
            edge_color="#BD93F9",
        ),
        "synthwave": Theme(
            name="synthwave",
            background="#1A1B26",
            group_bg="#24283B",
            group_stroke="#414868",
            node_fill="#292E42",
            node_stroke="#BB9AF7",
            accent="#7DCFFF",
            text="#C0CAF5",
            subtext="#7AA2F7",
            edge_color="#F7768E",
        ),
        "high_contrast": Theme(
            name="high_contrast",
            background="#000000",
            group_bg="#121212",
            group_stroke="#FFFFFF",
            node_fill="#000000",
            node_stroke="#FFFF00",
            accent="#FFFF00",
            text="#FFFFFF",
            subtext="#E0E0E0",
            edge_color="#FFFF00",
        ),
    }
    defaults["dark"] = defaults["iiot_dark_gold"]
    defaults["light"] = defaults["iiot_light"]
    return defaults


THEMES: dict[str, Theme] = _build_default_themes()

IIOT_DARK_GOLD = THEMES["iiot_dark_gold"]
IIOT_LIGHT = THEMES["iiot_light"]
BLUEPRINT = THEMES["blueprint"]
CYBER_SLATE = THEMES["cyber_slate"]
NORD = THEMES["nord"]
EMERALD = THEMES["emerald"]
CRIMSON = THEMES["crimson"]
MONOCHROME = THEMES["monochrome"]
SOLARIZED_LIGHT = THEMES["solarized_light"]
PASTEL_LIGHT = THEMES["pastel_light"]
DRACULA = THEMES["dracula"]
SYNTHWAVE = THEMES["synthwave"]
HIGH_CONTRAST = THEMES["high_contrast"]

_LIGHT_THEME_NAMES = {"iiot_light", "monochrome", "solarized_light", "pastel_light", "light"}


def list_themes() -> list[str]:
    """Return sorted list of all unique registered theme names."""
    return sorted(list(set(THEMES.keys()) - {"dark", "light"}))


def get_light_themes() -> list[str]:
    """Return list of registered light-palette theme names."""
    return sorted([k for k in list_themes() if k in _LIGHT_THEME_NAMES])


def get_dark_themes() -> list[str]:
    """Return list of registered dark-palette theme names."""
    return sorted([k for k in list_themes() if k not in _LIGHT_THEME_NAMES])


def reset_themes() -> None:
    """Reset global THEMES registry to default built-in presets."""
    global THEMES
    THEMES.clear()
    THEMES.update(_build_default_themes())


def get_theme(name_or_theme: Union[Theme, str] = "iiot_dark_gold") -> Theme:
    """Retrieve theme by name or return copy of Theme instance."""
    if isinstance(name_or_theme, Theme):
        return copy.copy(name_or_theme)
    if not isinstance(name_or_theme, str):
        raise TypeError(
            f"Theme name must be a str or Theme instance, got {type(name_or_theme).__name__}"
        )
    key = name_or_theme.strip().lower()
    selected = THEMES.get(key, THEMES["iiot_dark_gold"])
    return copy.copy(selected)



def register_theme(theme: Theme) -> None:
    """Register a custom Theme in the global theme registry."""
    if not isinstance(theme, Theme):
        raise TypeError(f"Expected Theme instance, got {type(theme).__name__}")
    if not theme.name or not isinstance(theme.name, str) or not theme.name.strip():
        raise ValueError("Theme name must be a non-empty string")
    key = theme.name.strip().lower()
    THEMES[key] = copy.copy(theme)
    THEMES[theme.name] = copy.copy(theme)


def create_theme(
    name: str,
    base: Union[Theme, str] = "iiot_dark_gold",
    **overrides: Any,
) -> Theme:
    """Create a new Theme derived from a base preset with custom overrides."""
    base_theme = get_theme(base)
    fields = {
        "name": name,
        "background": base_theme.background,
        "group_bg": base_theme.group_bg,
        "group_stroke": base_theme.group_stroke,
        "node_fill": base_theme.node_fill,
        "node_stroke": base_theme.node_stroke,
        "accent": base_theme.accent,
        "text": base_theme.text,
        "subtext": base_theme.subtext,
        "edge_color": base_theme.edge_color,
        "font_family": base_theme.font_family,
    }
    fields.update(overrides)
    new_theme = Theme(**fields)
    register_theme(new_theme)
    return new_theme

