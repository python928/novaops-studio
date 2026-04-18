from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
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
from widgets import InsightBanner, KpiStrip, SegmentedControl
from widgets.controls import AppButton, PrimaryButton, harmonize_combo_popup


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

        banner = InsightBanner(
            "Theme Strategy",
            "Use one strong primary action and keep secondary controls quieter so large forms stay readable.",
            action_text="Apply now",
            icon_text="T",
        )
        banner.actionTriggered.connect(self._apply)

        preview_strip = KpiStrip(
            [
                ("Theme modes", "2", "dark and light"),
                ("Accent presets", str(len(ACCENT_PRESETS)), "ready to reuse"),
                ("Focus rule", "2px", "clear keyboard visibility"),
                ("Layout", "LTR / RTL", "runtime switch"),
            ]
        )

        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.setContentsMargins(14, 14, 14, 14)
        form.setSpacing(12)

        self._theme_mode = SegmentedControl(["Dark", "Light"], initial="Dark")

        self._accent = QComboBox()
        self._accent.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        for name, color in ACCENT_PRESETS:
            self._accent.addItem(f"{name} ({color})", color)
        harmonize_combo_popup(self._accent)

        self._rtl = QCheckBox("Enable RTL layout direction")

        self._apply_btn = PrimaryButton("Apply Appearance")
        self._apply_btn.clicked.connect(self._apply)

        self._reset_btn = AppButton("Reset Accent", variant="subtle")
        self._reset_btn.clicked.connect(self._reset_accent)

        action_row = QWidget()
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        action_layout.addWidget(self._reset_btn)
        action_layout.addStretch(1)
        action_layout.addWidget(self._apply_btn)

        form.addRow("Theme", self._theme_mode)
        form.addRow("Accent", self._accent)
        form.addRow("RTL", self._rtl)
        form.addRow("", action_row)

        for field in (self._theme_mode, self._accent, self._rtl):
            label = form.labelForField(field)
            if label is not None:
                label.setProperty("muted", True)

        root.addWidget(heading)
        root.addWidget(hint)
        root.addWidget(banner)
        root.addWidget(preview_strip)
        root.addWidget(card)
        root.addStretch(1)

        self._sync_initial_state()

    def _sync_initial_state(self) -> None:
        mode = self._context.theme.mode.value
        accent = self._context.theme.accent
        prefs = self._context.settings.load_ui()

        self._theme_mode.set_current("Light" if mode == ThemeMode.LIGHT.value else "Dark", emit=False)

        accent_index = self._accent.findData(accent)
        if accent_index < 0:
            accent_index = 0
        self._accent.setCurrentIndex(accent_index)

        self._rtl.setChecked(bool(prefs.rtl_enabled))

    def _apply(self) -> None:
        mode = ThemeMode.LIGHT.value if self._theme_mode.current() == "Light" else ThemeMode.DARK.value
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

    def _reset_accent(self) -> None:
        self._accent.setCurrentIndex(0)
