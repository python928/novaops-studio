from __future__ import annotations

from collections.abc import Iterable, Sequence

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from widgets.controls import AppButton, AppToolButton, refresh_style


def _refresh_style(widget: QWidget) -> None:
    refresh_style(widget)


def _clear_layout(layout: QLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.hide()
            widget.setParent(None)
            widget.deleteLater()
        elif child_layout is not None:
            _clear_layout(child_layout)


class MetricCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str = "",
        *,
        delta_text: str = "",
        trend: str = "flat",
        progress: int | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("MetricCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(7)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("MetricTitle")

        self._delta_label = QLabel("")
        self._delta_label.setObjectName("MetricDeltaChip")

        header.addWidget(self._title_label)
        header.addStretch(1)
        header.addWidget(self._delta_label)

        self._value_label = QLabel(value)
        self._value_label.setProperty("metric", True)

        self._subtitle_label = QLabel(subtitle)
        self._subtitle_label.setObjectName("MetricSubtitle")
        self._subtitle_label.setWordWrap(True)

        self._progress_bar = QProgressBar()
        self._progress_bar.setObjectName("MetricProgress")
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setTextVisible(False)

        root.addLayout(header)
        root.addWidget(self._value_label)
        root.addWidget(self._subtitle_label)
        root.addWidget(self._progress_bar)

        self.set_delta(delta_text, trend=trend)
        self.set_progress(progress)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)

    def set_delta(self, text: str, *, trend: str = "flat") -> None:
        normalized = trend if trend in {"up", "down", "flat"} else "flat"
        self._delta_label.setText(text or "-")
        self._delta_label.setProperty("trend", normalized)
        _refresh_style(self._delta_label)

    def set_progress(self, value: int | None) -> None:
        if value is None:
            self._progress_bar.hide()
            return
        self._progress_bar.show()
        self._progress_bar.setValue(max(0, min(100, int(value))))


class StatusLozenge(QLabel):
    _TONES = {
        "healthy": "success",
        "ok": "success",
        "at risk": "warning",
        "review": "info",
        "blocked": "danger",
    }

    def __init__(self, text: str, *, status: str | None = None) -> None:
        super().__init__()
        self.setObjectName("StatusLozenge")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_status(status or text, text=text)

    def set_status(self, status: str, *, text: str | None = None) -> None:
        normalized = (status or "").strip().casefold()
        tone = self._TONES.get(normalized, "neutral")
        self.setText(text if text is not None else status)
        self.setProperty("tone", tone)
        _refresh_style(self)


class FilterChipBar(QWidget):
    selectionChanged = pyqtSignal(list)

    def __init__(
        self,
        options: Iterable[str],
        *,
        multi_select: bool = True,
        allow_empty: bool = True,
        initial: Sequence[str] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("ChipFilterBar")
        self._multi_select = multi_select
        self._allow_empty = allow_empty
        self._syncing = False
        self._buttons: dict[str, QPushButton] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        for option in options:
            label = str(option).strip()
            if not label or label in self._buttons:
                continue

            button = QPushButton(label)
            button.setCheckable(True)
            button.setProperty("filterChip", True)
            button.setProperty("selected", False)
            button.toggled.connect(lambda checked, value=label: self._on_toggled(value, checked))
            self._buttons[label] = button
            layout.addWidget(button)

        layout.addStretch(1)

        if initial:
            self.set_selected(initial, emit=False)
        elif not self._allow_empty and self._buttons:
            first = next(iter(self._buttons.keys()))
            self.set_selected([first], emit=False)

        self._sync_button_states(emit=False)

    def selected(self) -> list[str]:
        return [label for label, button in self._buttons.items() if button.isChecked()]

    def clear_selection(self) -> None:
        self.set_selected([], emit=True)

    def set_selected(self, values: Sequence[str], *, emit: bool = True) -> None:
        selected = [value for value in values if value in self._buttons]
        if not self._multi_select and selected:
            selected = selected[:1]
        if not selected and not self._allow_empty and self._buttons:
            selected = [next(iter(self._buttons.keys()))]

        self._syncing = True
        try:
            targets = set(selected)
            for label, button in self._buttons.items():
                button.setChecked(label in targets)
        finally:
            self._syncing = False

        self._sync_button_states(emit=emit)

    def _on_toggled(self, value: str, checked: bool) -> None:
        if self._syncing:
            return

        self._syncing = True
        try:
            if checked and not self._multi_select:
                for label, button in self._buttons.items():
                    if label != value and button.isChecked():
                        button.setChecked(False)

            if not self._allow_empty and not any(button.isChecked() for button in self._buttons.values()):
                fallback = self._buttons.get(value)
                if fallback is not None:
                    fallback.setChecked(True)
        finally:
            self._syncing = False

        self._sync_button_states(emit=True)

    def _sync_button_states(self, *, emit: bool) -> None:
        for button in self._buttons.values():
            is_selected = button.isChecked()
            button.setProperty("selected", is_selected)
            _refresh_style(button)

        if emit:
            self.selectionChanged.emit(self.selected())


class InsightBanner(QFrame):
    actionTriggered = pyqtSignal()

    def __init__(
        self,
        title: str,
        message: str,
        *,
        action_text: str = "Open",
        icon_text: str = "i",
    ) -> None:
        super().__init__()
        self.setObjectName("InsightBanner")

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        self._icon = QLabel(icon_text)
        self._icon.setObjectName("InsightBannerIcon")

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("InsightBannerTitle")

        self._body_label = QLabel(message)
        self._body_label.setObjectName("InsightBannerBody")
        self._body_label.setWordWrap(True)

        text_col.addWidget(self._title_label)
        text_col.addWidget(self._body_label)

        self._action_button = QPushButton(action_text)
        self._action_button.setObjectName("InsightBannerAction")
        self._action_button.setProperty("tonal", True)
        self._action_button.clicked.connect(self.actionTriggered.emit)

        root.addWidget(self._icon)
        root.addLayout(text_col, 1)
        root.addWidget(self._action_button)

    def set_action_visible(self, visible: bool) -> None:
        self._action_button.setVisible(visible)


class SegmentedControl(QWidget):
    selectionChanged = pyqtSignal(str)

    def __init__(self, options: Iterable[str], *, initial: str | None = None) -> None:
        super().__init__()
        self.setObjectName("SegmentedControl")

        self._buttons: dict[str, QPushButton] = {}
        self._current = ""

        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(4)

        for option in options:
            label = str(option).strip()
            if not label or label in self._buttons:
                continue

            button = QPushButton(label)
            button.setCheckable(True)
            button.setProperty("segment", True)
            button.setProperty("active", False)
            button.clicked.connect(lambda _checked=False, value=label: self.set_current(value))
            layout.addWidget(button)
            self._buttons[label] = button

        if self._buttons:
            start = initial if initial in self._buttons else next(iter(self._buttons.keys()))
            self.set_current(start, emit=False)

    def current(self) -> str:
        return self._current

    def set_current(self, value: str, *, emit: bool = True) -> None:
        if value not in self._buttons or value == self._current:
            return

        self._current = value
        for label, button in self._buttons.items():
            is_active = label == value
            button.setChecked(is_active)
            button.setProperty("active", is_active)
            _refresh_style(button)

        if emit:
            self.selectionChanged.emit(value)


class CommandDeck(QFrame):
    submitted = pyqtSignal(str)
    shortcutTriggered = pyqtSignal(str)

    def __init__(
        self,
        title: str,
        message: str,
        *,
        badge_text: str = "AI",
        placeholder: str = "Search commands, modules, or records...",
        submit_text: str = "Run",
        suggestions: Sequence[str] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("CommandDeck")
        self._chip_buttons: dict[str, QPushButton] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        badge = QLabel(badge_text)
        badge.setObjectName("CommandDeckBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        meta = QLabel("Command Deck")
        meta.setProperty("chip", True)

        top_row.addWidget(badge)
        top_row.addWidget(meta)
        top_row.addStretch(1)

        self._title = QLabel(title)
        self._title.setObjectName("CommandDeckTitle")

        self._body = QLabel(message)
        self._body.setObjectName("CommandDeckBody")
        self._body.setWordWrap(True)

        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(8)

        self._search = QLineEdit()
        self._search.setObjectName("CommandDeckSearch")
        self._search.setPlaceholderText(placeholder)
        self._search.setClearButtonEnabled(False)
        self._search.returnPressed.connect(self._emit_submit)

        self._submit = AppButton(submit_text, variant="primary")
        self._submit.setObjectName("CommandDeckSubmit")
        self._submit.clicked.connect(self._emit_submit)

        search_row.addWidget(self._search, 1)
        search_row.addWidget(self._submit)

        self._chip_row = QHBoxLayout()
        self._chip_row.setContentsMargins(0, 0, 0, 0)
        self._chip_row.setSpacing(6)

        root.addLayout(top_row)
        root.addWidget(self._title)
        root.addWidget(self._body)
        root.addLayout(search_row)
        root.addLayout(self._chip_row)

        self.set_suggestions(suggestions or [])

    def text(self) -> str:
        return self._search.text().strip()

    def set_text(self, value: str) -> None:
        self._search.setText(value)

    def focus_search(self) -> None:
        self._search.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def set_suggestions(self, suggestions: Sequence[str]) -> None:
        _clear_layout(self._chip_row)
        self._chip_buttons.clear()

        for label in suggestions:
            text = str(label).strip()
            if not text or text in self._chip_buttons:
                continue

            button = AppButton(text, variant="subtle")
            button.setProperty("commandChip", True)
            button.clicked.connect(lambda _checked=False, value=text: self._emit_shortcut(value))
            self._chip_buttons[text] = button
            self._chip_row.addWidget(button)

        self._chip_row.addStretch(1)

    def _emit_submit(self) -> None:
        self.submitted.emit(self.text())

    def _emit_shortcut(self, value: str) -> None:
        self._search.setText(value)
        self.shortcutTriggered.emit(value)


class ActionTile(QFrame):
    activated = pyqtSignal(str)

    def __init__(
        self,
        title: str,
        body: str,
        *,
        meta: str = "",
        badge_text: str = "+",
        tone: str = "info",
        action_text: str = "Open",
    ) -> None:
        super().__init__()
        self.setObjectName("ActionTile")
        self.setProperty("tone", tone)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 15, 16, 15)
        root.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        self._badge = QLabel(badge_text)
        self._badge.setObjectName("ActionTileBadge")
        self._badge.setProperty("tone", tone)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._meta = QLabel(meta)
        self._meta.setObjectName("ActionTileMeta")
        self._meta.setVisible(bool(meta))

        top_row.addWidget(self._badge)
        top_row.addStretch(1)
        top_row.addWidget(self._meta)

        self._title = QLabel(title)
        self._title.setObjectName("ActionTileTitle")
        self._title.setWordWrap(True)

        self._body = QLabel(body)
        self._body.setObjectName("ActionTileBody")
        self._body.setWordWrap(True)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(8)

        self._action = AppButton(action_text, variant="subtle")
        self._action.setObjectName("ActionTileAction")
        self._action.clicked.connect(lambda: self.activated.emit(title))

        chevron = AppToolButton(variant="subtle", icon_only=True)
        chevron.setObjectName("ActionTileChevron")
        chevron.setText(">")
        chevron.clicked.connect(lambda: self.activated.emit(title))

        footer.addWidget(self._action)
        footer.addStretch(1)
        footer.addWidget(chevron)

        root.addLayout(top_row)
        root.addWidget(self._title)
        root.addWidget(self._body)
        root.addStretch(1)
        root.addLayout(footer)


class StepProgress(QFrame):
    stepChanged = pyqtSignal(int, str)

    def __init__(self, steps: Sequence[str], *, current_index: int = 0) -> None:
        super().__init__()
        self.setObjectName("StepProgress")

        self._steps = [str(step).strip() for step in steps if str(step).strip()]
        self._nodes: list[tuple[QFrame, QLabel, QLabel]] = []
        self._connectors: list[QFrame] = []
        self._current_index = -1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        if not self._steps:
            placeholder = QLabel("No steps configured")
            placeholder.setProperty("muted", True)
            layout.addWidget(placeholder)
            return

        for index, step in enumerate(self._steps):
            node = QFrame()
            node.setObjectName("StepNode")

            node_layout = QVBoxLayout(node)
            node_layout.setContentsMargins(0, 0, 0, 0)
            node_layout.setSpacing(3)

            badge = QLabel(str(index + 1))
            badge.setObjectName("StepNodeBadge")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

            text = QLabel(step)
            text.setObjectName("StepNodeText")
            text.setAlignment(Qt.AlignmentFlag.AlignCenter)

            node_layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignHCenter)
            node_layout.addWidget(text)

            layout.addWidget(node)
            self._nodes.append((node, badge, text))

            if index < len(self._steps) - 1:
                connector = QFrame()
                connector.setObjectName("StepConnector")
                connector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                connector.setFixedHeight(2)
                layout.addWidget(connector, 1, Qt.AlignmentFlag.AlignVCenter)
                self._connectors.append(connector)

        self.set_current_index(current_index, emit=False)

    def current_index(self) -> int:
        return self._current_index

    def set_current_index(self, index: int, *, emit: bool = True) -> None:
        if not self._steps:
            return

        clamped = max(0, min(len(self._steps) - 1, int(index)))
        if clamped == self._current_index:
            return

        self._current_index = clamped

        for node_index, (node, badge, text) in enumerate(self._nodes):
            if node_index < clamped:
                state = "done"
            elif node_index == clamped:
                state = "current"
            else:
                state = "todo"

            for widget in (node, badge, text):
                widget.setProperty("state", state)
                _refresh_style(widget)

        for connector_index, connector in enumerate(self._connectors):
            connector_state = "done" if connector_index < clamped else "todo"
            connector.setProperty("state", connector_state)
            _refresh_style(connector)

        if emit:
            self.stepChanged.emit(clamped, self._steps[clamped])


class TimelineFeed(QFrame):
    def __init__(self, title: str = "Recent Activity") -> None:
        super().__init__()
        self.setObjectName("TimelineFeed")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(8)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("TimelineFeedTitle")
        root.addWidget(self._title_label)

        self._rows_layout = QVBoxLayout()
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(7)
        root.addLayout(self._rows_layout)

        root.addStretch(1)

    def set_events(self, events: Sequence[tuple[str, str, str, str]]) -> None:
        _clear_layout(self._rows_layout)

        for title, detail, stamp, tone in events:
            row = QFrame()
            row.setObjectName("TimelineRow")

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            dot = QLabel("")
            dot.setObjectName("TimelineDot")
            dot.setProperty("tone", tone)
            _refresh_style(dot)

            text_col = QVBoxLayout()
            text_col.setContentsMargins(0, 0, 0, 0)
            text_col.setSpacing(1)

            title_label = QLabel(title)
            title_label.setObjectName("TimelineItemTitle")

            meta_label = QLabel(f"{detail}  {stamp}")
            meta_label.setObjectName("TimelineItemMeta")

            text_col.addWidget(title_label)
            text_col.addWidget(meta_label)

            row_layout.addWidget(dot, 0, Qt.AlignmentFlag.AlignTop)
            row_layout.addLayout(text_col, 1)

            self._rows_layout.addWidget(row)


class EmptyStateCard(QFrame):
    actionTriggered = pyqtSignal()

    def __init__(
        self,
        title: str,
        message: str,
        *,
        action_text: str = "Create",
        icon_text: str = "?",
    ) -> None:
        super().__init__()
        self.setObjectName("EmptyStateCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(8)

        self._icon = QLabel(icon_text)
        self._icon.setObjectName("EmptyStateIcon")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._title = QLabel(title)
        self._title.setObjectName("EmptyStateTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._body = QLabel(message)
        self._body.setObjectName("EmptyStateBody")
        self._body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._body.setWordWrap(True)

        self._action = QPushButton(action_text)
        self._action.setProperty("primary", True)
        self._action.clicked.connect(self.actionTriggered.emit)

        root.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(self._title)
        root.addWidget(self._body)
        root.addWidget(self._action, 0, Qt.AlignmentFlag.AlignHCenter)

    def set_action_visible(self, visible: bool) -> None:
        self._action.setVisible(visible)


class KpiStrip(QFrame):
    def __init__(self, items: Sequence[tuple[str, str, str]] | None = None) -> None:
        super().__init__()
        self.setObjectName("KpiStrip")

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(8)

        self.set_items(items or [])

    def set_items(self, items: Sequence[tuple[str, str, str]]) -> None:
        _clear_layout(self._layout)

        if not items:
            placeholder = QLabel("No KPIs available")
            placeholder.setProperty("muted", True)
            self._layout.addWidget(placeholder)
            return

        for index, (label, value, hint) in enumerate(items):
            item = QFrame()
            item.setObjectName("KpiStripItem")
            item.setProperty("lastItem", index == len(items) - 1)

            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(8, 4, 8, 4)
            item_layout.setSpacing(1)

            value_label = QLabel(value)
            value_label.setObjectName("KpiStripValue")

            title_label = QLabel(label)
            title_label.setObjectName("KpiStripLabel")

            hint_label = QLabel(hint)
            hint_label.setObjectName("KpiStripHint")

            item_layout.addWidget(value_label)
            item_layout.addWidget(title_label)
            item_layout.addWidget(hint_label)

            self._layout.addWidget(item)
