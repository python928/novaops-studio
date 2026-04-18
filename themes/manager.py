from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from core.constants import normalize_hex
from themes.palettes import build_palette
from themes.qss_builder import build_stylesheet
from themes.tokens import ThemeMode, build_tokens, parse_theme_mode


class ThemeManager(QObject):
    themeChanged = pyqtSignal(str, str)

    def __init__(
        self,
        app: QApplication,
        initial_mode: str,
        initial_accent: str,
    ) -> None:
        super().__init__()
        self._app = app
        self._mode = parse_theme_mode(initial_mode)
        self._accent = normalize_hex(initial_accent)
        self._cache: dict[str, str] = {}

    @property
    def mode(self) -> ThemeMode:
        return self._mode

    @property
    def accent(self) -> str:
        return self._accent

    def toggle_mode(self) -> None:
        next_mode = ThemeMode.LIGHT if self._mode == ThemeMode.DARK else ThemeMode.DARK
        self.apply(theme_mode=next_mode)

    def apply(
        self,
        theme_mode: ThemeMode | str | None = None,
        accent_hex: str | None = None,
        *,
        force: bool = False,
    ) -> None:
        mode = parse_theme_mode(str(theme_mode or self._mode.value))
        accent = normalize_hex(accent_hex or self._accent)

        if not force and mode == self._mode and accent == self._accent:
            return

        tokens = build_tokens(mode, accent)
        self._app.setPalette(build_palette(tokens))

        cache_key = f"{mode.value}:{accent}"
        stylesheet = self._cache.get(cache_key)
        if stylesheet is None:
            stylesheet = build_stylesheet(tokens)
            self._cache[cache_key] = stylesheet

        self._app.setStyleSheet(stylesheet)

        # Icons are tinted from the active palette, so clear icon caches when theme changes.
        try:
            from services.icons import clear_icon_cache

            clear_icon_cache()
        except Exception:
            pass

        self._mode = mode
        self._accent = accent
        self.themeChanged.emit(mode.value, accent)
