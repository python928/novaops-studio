from __future__ import annotations

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from core.constants import ACCENT_PRESETS
from i18n import apply_layout_direction
from themes.tokens import ThemeMode
from widgets.controls import PrimaryButton


class SettingsPage(QWidget):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        heading = QLabel("Appearance Settings")
        heading.setProperty("title", "h2")

        hint = QLabel(
            "Theme, accent, and layout preferences are saved to QSettings and restored automatically."
        )
        hint.setProperty("muted", True)

        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(10)

        self._theme_mode = QComboBox()
        self._theme_mode.addItem("Dark", ThemeMode.DARK.value)
        self._theme_mode.addItem("Light", ThemeMode.LIGHT.value)

        self._accent = QComboBox()
        for name, color in ACCENT_PRESETS:
            self._accent.addItem(f"{name} ({color})", color)

        self._rtl = QCheckBox("Enable RTL layout direction")

        self._apply_btn = PrimaryButton("Apply Appearance")
        self._apply_btn.clicked.connect(self._apply)

        form.addRow("Theme", self._theme_mode)
        form.addRow("Accent", self._accent)
        form.addRow("RTL", self._rtl)
        form.addRow("", self._apply_btn)

        for field in (self._theme_mode, self._accent, self._rtl):
            label = form.labelForField(field)
            if label is not None:
                label.setProperty("muted", True)

        root.addWidget(heading)
        root.addWidget(hint)
        root.addWidget(card)
        root.addStretch(1)

        self._sync_initial_state()

    def _sync_initial_state(self) -> None:
        mode = self._context.theme.mode.value
        accent = self._context.theme.accent
        prefs = self._context.settings.load_ui()

        mode_index = self._theme_mode.findData(mode)
        if mode_index >= 0:
            self._theme_mode.setCurrentIndex(mode_index)

        accent_index = self._accent.findData(accent)
        if accent_index < 0:
            accent_index = 0
        self._accent.setCurrentIndex(accent_index)

        self._rtl.setChecked(bool(prefs.rtl_enabled))

    def _apply(self) -> None:
        mode = str(self._theme_mode.currentData())
        accent = str(self._accent.currentData())
        rtl_enabled = self._rtl.isChecked()

        self._context.theme.apply(theme_mode=mode, accent_hex=accent)
        self._context.settings.save_theme_mode(mode)
        self._context.settings.save_accent(accent)
        self._context.settings.save_rtl_enabled(rtl_enabled)

        app = QApplication.instance()
        if app is not None:
            apply_layout_direction(app, rtl_enabled)

        self._context.events.statusMessage.emit("Appearance updated")
