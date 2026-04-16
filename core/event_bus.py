from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class AppEventBus(QObject):
    moduleChanged = pyqtSignal(str)
    statusMessage = pyqtSignal(str)
