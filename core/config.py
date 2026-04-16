from __future__ import annotations

from dataclasses import dataclass

from core.constants import DEFAULT_ACCENT, DEFAULT_THEME_MODE


@dataclass(frozen=True, slots=True)
class AppConfig:
    theme_mode: str = DEFAULT_THEME_MODE
    accent_hex: str = DEFAULT_ACCENT
    rtl_enabled: bool = False
