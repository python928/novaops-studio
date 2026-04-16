from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PyQt6.QtCore import QSettings

from core.constants import (
    APP_NAME,
    APP_ORGANIZATION,
    DEFAULT_ACCENT,
    DEFAULT_THEME_MODE,
    normalize_hex,
)


@dataclass(frozen=True, slots=True)
class UiPreferences:
    theme_mode: str
    accent_hex: str
    rtl_enabled: bool


class SettingsStore:
    def __init__(self) -> None:
        self._settings = QSettings(APP_ORGANIZATION, APP_NAME)

    def load_ui(self) -> UiPreferences:
        theme_mode = str(self._settings.value("ui/theme_mode", DEFAULT_THEME_MODE))
        accent_hex = normalize_hex(str(self._settings.value("ui/accent_hex", DEFAULT_ACCENT)))
        rtl_enabled = _as_bool(self._settings.value("ui/rtl_enabled", False))
        return UiPreferences(theme_mode=theme_mode, accent_hex=accent_hex, rtl_enabled=rtl_enabled)

    def save_theme_mode(self, theme_mode: str) -> None:
        self._settings.setValue("ui/theme_mode", theme_mode)

    def save_accent(self, accent_hex: str) -> None:
        self._settings.setValue("ui/accent_hex", normalize_hex(accent_hex))

    def save_rtl_enabled(self, enabled: bool) -> None:
        self._settings.setValue("ui/rtl_enabled", bool(enabled))



def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)
