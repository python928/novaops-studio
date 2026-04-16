from __future__ import annotations

from PyQt6.QtWidgets import QPushButton


class PrimaryButton(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setProperty("primary", True)


class SectionTitle(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setEnabled(False)
        self.setFlat(True)
        self.setProperty("sectionTitle", True)
