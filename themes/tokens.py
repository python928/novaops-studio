from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from PyQt6.QtGui import QColor


class ThemeMode(str, Enum):
    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True, slots=True)
class ThemeTokens:
    window: str
    surface: str
    surface_alt: str
    sidebar: str
    border: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent: str
    accent_hover: str
    accent_pressed: str
    accent_contrast: str
    success: str
    warning: str
    danger: str
    selection_bg: str
    table_alt: str


def parse_theme_mode(value: str) -> ThemeMode:
    try:
        return ThemeMode(value)
    except ValueError:
        return ThemeMode.DARK


def build_tokens(theme_mode: ThemeMode, accent_hex: str) -> ThemeTokens:
    accent = _normalize_hex(accent_hex, "#2F6FED")
    accent_contrast = "#0A0F1A" if _is_light_color(accent) else "#FFFFFF"

    if theme_mode == ThemeMode.LIGHT:
        return ThemeTokens(
            window="#F3F6FC",
            surface="#FFFFFF",
            surface_alt="#EBF0F9",
            sidebar="#E9EFF8",
            border="#CCD7E7",
            text_primary="#101A2C",
            text_secondary="#3D4E68",
            text_muted="#6C7F9D",
            accent=accent,
            accent_hover=_mix_hex(accent, "#FFFFFF", 0.18),
            accent_pressed=_mix_hex(accent, "#000000", 0.18),
            accent_contrast=accent_contrast,
            success="#1F9D6C",
            warning="#B77A15",
            danger="#C24E60",
            selection_bg=_mix_hex(accent, "#FFFFFF", 0.84),
            table_alt="#F5F8FF",
        )

    return ThemeTokens(
        window="#0D111A",
        surface="#131B28",
        surface_alt="#1A2535",
        sidebar="#0F1724",
        border="#2B3950",
        text_primary="#E7EEF9",
        text_secondary="#BAC8DE",
        text_muted="#8496B3",
        accent=accent,
        accent_hover=_mix_hex(accent, "#FFFFFF", 0.20),
        accent_pressed=_mix_hex(accent, "#000000", 0.30),
        accent_contrast=accent_contrast,
        success="#35BF89",
        warning="#D2A74E",
        danger="#E57C90",
        selection_bg=_mix_hex(accent, "#0B111B", 0.62),
        table_alt="#162234",
    )


def _normalize_hex(color: str, fallback: str) -> str:
    value = (color or "").strip().lstrip("#")
    if len(value) == 3 and all(ch in "0123456789ABCDEFabcdef" for ch in value):
        value = "".join(ch * 2 for ch in value)
    if len(value) == 6 and all(ch in "0123456789ABCDEFabcdef" for ch in value):
        return f"#{value.upper()}"
    return fallback


def _mix_hex(color_a: str, color_b: str, ratio: float) -> str:
    a = QColor(color_a)
    b = QColor(color_b)
    r = int(round((1.0 - ratio) * a.red() + ratio * b.red()))
    g = int(round((1.0 - ratio) * a.green() + ratio * b.green()))
    b_value = int(round((1.0 - ratio) * a.blue() + ratio * b.blue()))
    return f"#{r:02X}{g:02X}{b_value:02X}"


def _is_light_color(color: str) -> bool:
    qcolor = QColor(color)
    luma = (0.299 * qcolor.red()) + (0.587 * qcolor.green()) + (0.114 * qcolor.blue())
    return luma >= 186.0
