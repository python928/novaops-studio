from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


def apply_layout_direction(app: QApplication, rtl_enabled: bool) -> None:
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl_enabled else Qt.LayoutDirection.LeftToRight)
