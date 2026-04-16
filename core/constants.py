from __future__ import annotations

APP_ORGANIZATION = "python928"
APP_NAME = "QtScalableTemplate"
APP_VERSION = "0.1.0"

DEFAULT_THEME_MODE = "dark"
DEFAULT_ACCENT = "#2F6FED"

ACCENT_PRESETS: tuple[tuple[str, str], ...] = (
    ("Blue", "#2F6FED"),
    ("Teal", "#0B9AAE"),
    ("Emerald", "#1F9D6C"),
    ("Amber", "#CF8B17"),
    ("Rose", "#C14A68"),
)

NAV_ITEMS: tuple[tuple[str, str, str], ...] = (
    ("showcase", "Widget Showcase", "sliders"),
    ("dashboard", "Dashboard", "dashboard"),
    ("datagrid", "Data Grid", "table"),
    ("settings", "Settings", "settings"),
)

TABLE_BATCH_SIZE = 1200
TABLE_DEMO_ROW_COUNT = 30000


def normalize_hex(color: str, fallback: str = DEFAULT_ACCENT) -> str:
    value = (color or "").strip().lstrip("#")
    if len(value) == 3 and all(ch in "0123456789ABCDEFabcdef" for ch in value):
        value = "".join(ch * 2 for ch in value)
    if len(value) == 6 and all(ch in "0123456789ABCDEFabcdef" for ch in value):
        return f"#{value.upper()}"
    if fallback == color:
        return DEFAULT_ACCENT
    return normalize_hex(fallback, DEFAULT_ACCENT)
