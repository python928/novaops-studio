from __future__ import annotations

import argparse
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from core.app_context import AppContext
from core.config import AppConfig
from core.constants import APP_NAME, APP_VERSION, normalize_hex
from core.event_bus import AppEventBus
from core.logging import setup_logging
from core.settings import SettingsStore
from i18n import apply_layout_direction
from themes import ThemeManager
from ui.shell import MainWindow


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    setup_logging()

    app = QApplication([])
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyle("Fusion")

    settings = SettingsStore()
    prefs = settings.load_ui()

    config = AppConfig(
        theme_mode=args.theme or prefs.theme_mode,
        accent_hex=normalize_hex(args.accent or prefs.accent_hex),
        rtl_enabled=prefs.rtl_enabled if args.rtl is None else args.rtl,
    )

    events = AppEventBus()
    theme = ThemeManager(app, config.theme_mode, config.accent_hex)
    theme.apply(force=True)
    apply_layout_direction(app, config.rtl_enabled)

    context = AppContext(settings=settings, events=events, theme=theme)
    window = MainWindow(context)

    if args.screenshot:
        _capture_window(app, window, args.screenshot)
        return app.exec()

    window.show()
    return app.exec()


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NovaOps Studio desktop shell")
    parser.add_argument("--theme", choices=("dark", "light"), help="Initial theme mode")
    parser.add_argument("--accent", help="Accent color as hex, e.g. #2F6FED")
    parser.add_argument("--rtl", dest="rtl", action="store_true", help="Enable RTL layout")
    parser.add_argument("--ltr", dest="rtl", action="store_false", help="Force LTR layout")
    parser.add_argument("--screenshot", help="Save a screenshot to this file and exit")
    parser.set_defaults(rtl=None)
    return parser.parse_args(argv)


def _capture_window(app: QApplication, window: MainWindow, output_path: str) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    def capture() -> None:
        window.resize(1440, 900)
        app.processEvents()
        pixmap = window.grab()
        pixmap.save(str(target))
        app.quit()

    window.show()
    QTimer.singleShot(250, capture)
