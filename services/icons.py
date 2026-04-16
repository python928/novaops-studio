from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QStyle


_ICON_DIR = Path(__file__).resolve().parent.parent / "resources" / "icons"


@lru_cache(maxsize=256)
def icon(name: str) -> QIcon:
    path = _ICON_DIR / f"{name}.svg"
    if path.exists():
        return QIcon(str(path))
    return QIcon()


@lru_cache(maxsize=64)
def standard_icon(pixmap: QStyle.StandardPixmap) -> QIcon:
    app = QApplication.instance()
    if app is None:
        return QIcon()
    return app.style().standardIcon(pixmap)
