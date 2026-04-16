from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class InfoCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str = "") -> None:
        super().__init__()
        self.setObjectName("Card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setProperty("muted", True)

        value_label = QLabel(value)
        value_label.setProperty("metric", True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setProperty("muted", True)
            layout.addWidget(subtitle_label)
