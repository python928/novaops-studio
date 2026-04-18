from __future__ import annotations

from collections import Counter
import random
from typing import Callable

from PyQt6.QtCore import QEvent, QModelIndex, QRect, QSize, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QPalette, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from core.constants import TABLE_BATCH_SIZE, TABLE_DEMO_ROW_COUNT
from core.table_view import apply_adaptive_column_widths, configure_table_headers
from data.fake_records import DemoRecord, generate_demo_records
from modules.datagrid.model import DataGridModel
from modules.datagrid.proxy import DataGridProxyModel
from services.icons import icon
from widgets.controls import harmonize_combo_popup
from widgets import EmptyStateCard, FilterChipBar, InsightBanner, KpiStrip, SegmentedControl


class ActionButtonsDelegate(QStyledItemDelegate):
    actionTriggered = pyqtSignal(QModelIndex, str)

    def __init__(
        self,
        parent: QWidget,
        *,
        action_ids_getter: Callable[[], tuple[str, ...]],
        icon_getter: Callable[[str], QIcon],
    ) -> None:
        super().__init__(parent)
        self._action_ids_getter = action_ids_getter
        self._icon_getter = icon_getter
        self._button_extent = 20
        self._gap = 5
        self._horizontal_padding = 8

    def preferred_width(self, font_metrics) -> int:
        action_count = len(self._action_ids_getter())
        icons_width = self._icons_row_width(action_count)
        header_width = font_metrics.horizontalAdvance("Actions") + (self._horizontal_padding * 2)
        return max(96, header_width, icons_width + (self._horizontal_padding * 2))

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        _ = index
        row_height = max(26, option.fontMetrics.height() + 12)
        return QSize(self.preferred_width(option.fontMetrics), row_height)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        item_option = QStyleOptionViewItem(option)
        self.initStyleOption(item_option, index)
        item_option.text = ""
        item_option.icon = QIcon()

        style = item_option.widget.style() if item_option.widget is not None else QApplication.style()
        style.drawControl(
            QStyle.ControlElement.CE_ItemViewItem,
            item_option,
            painter,
            item_option.widget,
        )

        action_rects = self._button_rects(option)
        if not action_rects:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        border_color = option.palette.color(QPalette.ColorRole.Mid)
        base_color = option.palette.color(QPalette.ColorRole.Base)
        alt_color = option.palette.color(QPalette.ColorRole.AlternateBase)
        highlight = option.palette.color(QPalette.ColorRole.Highlight)

        if option.state & QStyle.StateFlag.State_Selected:
            chip_fill = highlight.darker(128) if highlight.lightness() > 144 else highlight.lighter(122)
        else:
            chip_fill = alt_color if alt_color != base_color else (
                base_color.darker(106) if base_color.lightness() > 130 else base_color.lighter(112)
            )

        painter.setPen(QPen(border_color, 1))
        for action_id, rect in action_rects:
            painter.setBrush(chip_fill)
            painter.drawRoundedRect(rect, 4, 4)

            icon_ref = self._icon_getter(action_id)
            if icon_ref.isNull():
                continue

            icon_rect = rect.adjusted(2, 2, -2, -2)
            icon_ref.paint(
                painter,
                icon_rect,
                Qt.AlignmentFlag.AlignCenter,
                QIcon.Mode.Normal,
                QIcon.State.Off,
            )

        painter.restore()

    def editorEvent(self, event, model, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        _ = model
        if event.type() not in (
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.MouseButtonDblClick,
        ):
            return super().editorEvent(event, model, option, index)

        if hasattr(event, "button") and event.button() != Qt.MouseButton.LeftButton:
            return False

        if hasattr(event, "position"):
            point = event.position().toPoint()
        else:
            point = event.pos()

        for action_id, rect in self._button_rects(option):
            if rect.contains(point):
                self.actionTriggered.emit(index, action_id)
                return True

        return False

    def _button_rects(self, option: QStyleOptionViewItem) -> list[tuple[str, QRect]]:
        action_ids = tuple(self._action_ids_getter())
        if not action_ids:
            return []

        total_width = self._icons_row_width(len(action_ids))
        start_x = option.rect.x() + max(0, (option.rect.width() - total_width) // 2)
        start_y = option.rect.y() + max(0, (option.rect.height() - self._button_extent) // 2)

        rects: list[tuple[str, QRect]] = []
        for action_id in action_ids:
            rect = QRect(start_x, start_y, self._button_extent, self._button_extent)
            rects.append((action_id, rect))
            start_x += self._button_extent + self._gap

        return rects

    def _icons_row_width(self, action_count: int) -> int:
        if action_count <= 0:
            return 0
        return (action_count * self._button_extent) + ((action_count - 1) * self._gap)


class DataGridPage(QWidget):
    _ACTION_LABEL_TO_ID = {
        "View": "view",
        "Edit": "edit",
        "Delete": "delete",
    }

    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context

        initial_action_ids = tuple(self._ACTION_LABEL_TO_ID.values())

        self._records = generate_demo_records(TABLE_DEMO_ROW_COUNT)
        self._model = DataGridModel(
            self._records,
            batch_size=TABLE_BATCH_SIZE,
            enable_color_roles=True,
            visible_actions=initial_action_ids,
        )
        self._proxy = DataGridProxyModel()
        self._proxy.setSourceModel(self._model)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(10)

        title = QLabel("Operations Data Grid")
        title.setProperty("title", "h2")

        subtitle = QLabel(
            "Fast filtering and sorting for large datasets using model/proxy architecture."
        )
        subtitle.setProperty("muted", True)

        tip_banner = InsightBanner(
            "Filtering Strategy",
            "Apply domain and status first, then use text search for faster triage on large datasets.",
            action_text="Show tips",
            icon_text="i",
        )
        tip_banner.actionTriggered.connect(
            lambda: self._search.setFocus(Qt.FocusReason.ShortcutFocusReason)
        )

        self._summary_strip = KpiStrip()
        self._refresh_summary_strip()

        controls_card = QFrame()
        controls_card.setObjectName("Card")
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(12, 12, 12, 12)
        controls_layout.setSpacing(10)

        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(8)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search across all columns...")
        self._search.setClearButtonEnabled(False)
        self._search.textChanged.connect(self._proxy.set_search_text)

        self._domain_filter = QComboBox()
        self._domain_filter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._domain_filter.setMinimumWidth(170)
        self._domain_filter.currentTextChanged.connect(self._proxy.set_domain_filter)
        harmonize_combo_popup(self._domain_filter)

        self._status_filter = SegmentedControl(
            ["All", "Healthy", "At Risk", "Blocked", "Review"],
            initial="All",
        )
        self._status_filter.selectionChanged.connect(self._proxy.set_status_filter)

        self._render_mode = SegmentedControl(
            ["Color write", "Fast write"],
            initial="Color write",
        )
        self._render_mode.selectionChanged.connect(self._on_render_mode_changed)

        self._density = SegmentedControl(
            ["Comfort", "Compact", "Tight"],
            initial="Comfort",
        )
        self._density.selectionChanged.connect(self._apply_density)

        self._quick_filters = FilterChipBar(
            ["Needs action", "High score", "Large amount", "Recent updates"],
            multi_select=True,
            allow_empty=True,
        )
        self._quick_filters.selectionChanged.connect(self._proxy.set_quick_filters)

        self._action_columns = FilterChipBar(
            list(self._ACTION_LABEL_TO_ID.keys()),
            multi_select=True,
            allow_empty=True,
            initial=list(self._ACTION_LABEL_TO_ID.keys()),
        )
        self._action_columns.selectionChanged.connect(self._on_action_columns_changed)

        self._reload_button = QPushButton("Reload")
        self._reload_button.setIcon(icon("refresh"))
        self._reload_button.setProperty("tonal", True)
        self._reload_button.clicked.connect(self._reload_data)

        self._count_label = QLabel("")
        self._count_label.setProperty("chip", True)

        toolbar_layout.addWidget(self._search, 1)
        toolbar_layout.addWidget(self._domain_filter)
        toolbar_layout.addWidget(self._status_filter)
        toolbar_layout.addWidget(self._render_mode)
        toolbar_layout.addWidget(self._density)
        toolbar_layout.addWidget(self._reload_button)
        toolbar_layout.addWidget(self._count_label)

        quick_filters_row = QWidget()
        quick_filters_layout = QHBoxLayout(quick_filters_row)
        quick_filters_layout.setContentsMargins(0, 0, 0, 0)
        quick_filters_layout.setSpacing(8)

        quick_filters_label = QLabel("Quick filters")
        quick_filters_label.setProperty("muted", True)
        quick_filters_layout.addWidget(quick_filters_label)
        quick_filters_layout.addWidget(self._quick_filters, 1)

        actions_row = QWidget()
        actions_layout = QHBoxLayout(actions_row)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        actions_label = QLabel("Visible actions")
        actions_label.setProperty("muted", True)
        actions_layout.addWidget(actions_label)
        actions_layout.addWidget(self._action_columns, 1)

        self._table = QTableView()
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.setShowGrid(False)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setWordWrap(False)
        self._table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self._table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(30)
        self._table.setModel(self._proxy)
        self._table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        configure_table_headers(self._table, stretch_last_section=False)

        self._actions_delegate = ActionButtonsDelegate(
            self._table,
            action_ids_getter=lambda: self._model.visible_action_ids,
            icon_getter=self._model.action_icon,
        )
        self._actions_delegate.actionTriggered.connect(self._on_action_triggered)
        self._install_actions_delegate()

        self._column_width_timer = QTimer(self)
        self._column_width_timer.setSingleShot(True)
        self._column_width_timer.setInterval(70)
        self._column_width_timer.timeout.connect(self._apply_adaptive_column_widths)
        self._initial_widths_applied = False

        self._empty_state = EmptyStateCard(
            "No Rows Match Current Filters",
            "Try clearing some filters or broadening your search query.",
            action_text="Clear Filters",
            icon_text="0",
        )
        self._empty_state.actionTriggered.connect(self._clear_filters)

        self._table_stack = QStackedWidget()
        self._table_stack.addWidget(self._table)
        self._table_stack.addWidget(self._empty_state)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(tip_banner)
        root.addWidget(self._summary_strip)
        controls_layout.addWidget(toolbar)
        controls_layout.addWidget(quick_filters_row)
        controls_layout.addWidget(actions_row)
        root.addWidget(controls_card)
        root.addWidget(self._table_stack, 1)

        # Keep model visual-role state aligned with the active segmented option.
        self._on_render_mode_changed(self._render_mode.current())
        self._apply_density(self._density.current())

        self._setup_domain_filter()
        self._attach_count_signals()
        self._refresh_count_label()
        self._queue_adaptive_column_widths()
        self._context.theme.themeChanged.connect(self._on_theme_changed)

    def _setup_domain_filter(self) -> None:
        domains = sorted({record.domain for record in self._records})
        self._domain_filter.clear()
        self._domain_filter.addItem("All")
        self._domain_filter.addItems(domains)

    def _attach_count_signals(self) -> None:
        self._proxy.modelReset.connect(self._refresh_count_label)
        self._proxy.layoutChanged.connect(self._refresh_count_label)
        self._proxy.rowsInserted.connect(lambda *_: self._refresh_count_label())
        self._proxy.rowsRemoved.connect(lambda *_: self._refresh_count_label())

        self._proxy.modelReset.connect(self._queue_adaptive_column_widths)
        self._proxy.layoutChanged.connect(self._queue_adaptive_column_widths)
        self._proxy.rowsInserted.connect(lambda *_: self._queue_adaptive_column_widths())
        self._proxy.rowsRemoved.connect(lambda *_: self._queue_adaptive_column_widths())

    def _install_actions_delegate(self) -> None:
        action_column = self._model.action_column_index()
        if action_column < 0:
            return
        self._table.setItemDelegateForColumn(action_column, self._actions_delegate)

    def _refresh_count_label(self) -> None:
        visible = self._proxy.rowCount()
        total = self._model.total_count
        self._count_label.setText(f"Rows: {visible:,} / {total:,}")
        self._table_stack.setCurrentWidget(self._empty_state if visible == 0 else self._table)

    def _on_render_mode_changed(self, mode: str) -> None:
        enable_colors = mode.strip().casefold() == "color write"
        self._model.set_visual_roles_enabled(enable_colors)

    def _apply_density(self, density: str) -> None:
        normalized = density.strip().casefold()
        if normalized == "tight":
            row_height = 28
        elif normalized == "compact":
            row_height = 32
        else:
            row_height = 38

        self._table.verticalHeader().setDefaultSectionSize(row_height)
        self._table.updateGeometries()
        self._context.events.statusMessage.emit(f"Data grid density: {density}")
        self._queue_adaptive_column_widths()

    def _queue_adaptive_column_widths(self, *_args) -> None:
        if self.isVisible() and not self._initial_widths_applied:
            self._apply_adaptive_column_widths()
        self._column_width_timer.start()

    def _apply_adaptive_column_widths(self) -> None:
        if self._table.model() is None:
            return

        fixed_widths = self._fixed_column_widths()

        apply_adaptive_column_widths(
            self._table,
            sample_rows=130,
            min_width=84,
            max_width=620,
            width_ratio_limit=0.52,
            padding=28,
            distribute_extra_space=True,
            fixed_widths=fixed_widths,
        )
        self._initial_widths_applied = True

    def _fixed_column_widths(self) -> dict[int, int]:
        action_column = self._model.action_column_index()
        if action_column < 0:
            return {}
        preferred = self._actions_delegate.preferred_width(self._table.fontMetrics())
        return {action_column: preferred}

    def _on_action_columns_changed(self, labels: list[str]) -> None:
        action_ids = [
            self._ACTION_LABEL_TO_ID[label]
            for label in labels
            if label in self._ACTION_LABEL_TO_ID
        ]

        self._model.set_visible_actions(action_ids)
        self._table.viewport().update()
        self._install_actions_delegate()
        self._queue_adaptive_column_widths()

        visible_text = ", ".join(labels) if labels else "none"
        self._context.events.statusMessage.emit(f"Visible actions: {visible_text}")

    def _on_action_triggered(self, proxy_index: QModelIndex, action_id: str) -> None:
        source_index = self._proxy.mapToSource(proxy_index)
        if not source_index.isValid():
            return

        record = self._model.row_at(source_index.row())
        if record is None:
            return

        self._dispatch_row_action(action_id, record)

    def _dispatch_row_action(self, action_id: str, record: DemoRecord) -> None:
        if action_id == "view":
            self._context.events.statusMessage.emit(
                f"View record #{record.record_id}: {record.title}"
            )
            return

        if action_id == "edit":
            self._context.events.statusMessage.emit(
                f"Edit record #{record.record_id}: {record.title}"
            )
            return

        if action_id == "delete":
            self._context.events.statusMessage.emit(
                f"Delete request for record #{record.record_id}: {record.title}"
            )
            return

        self._context.events.statusMessage.emit(
            f"Action '{action_id}' on record #{record.record_id}"
        )

    def _refresh_summary_strip(self) -> None:
        counts = Counter(record.status for record in self._records)
        total_amount = sum(record.amount for record in self._records)

        self._summary_strip.set_items(
            [
                ("Healthy", f"{counts.get('Healthy', 0):,}", "stable items"),
                ("At Risk", f"{counts.get('At Risk', 0):,}", "needs attention"),
                ("Blocked", f"{counts.get('Blocked', 0):,}", "critical"),
                ("Value", f"${total_amount:,.0f}", "portfolio amount"),
            ]
        )

    def _clear_filters(self) -> None:
        self._search.clear()
        self._domain_filter.setCurrentIndex(0)
        self._status_filter.set_current("All")
        self._quick_filters.clear_selection()
        self._proxy.invalidateFilter()
        self._refresh_count_label()

    def _reload_data(self) -> None:
        fresh_records = generate_demo_records(
            TABLE_DEMO_ROW_COUNT,
            seed=random.randint(1, 1_000_000),
        )
        self._model.sync_records(fresh_records, reset_change_ratio=0.62)
        self._records = fresh_records
        self._setup_domain_filter()
        self._refresh_summary_strip()
        self._proxy.invalidate()
        self._refresh_count_label()

    def _on_theme_changed(self, _mode: str, _accent: str) -> None:
        self._reload_button.setIcon(icon("refresh"))
        self._model.refresh_action_icons()
        self._table.viewport().update()
        self._install_actions_delegate()
        self._queue_adaptive_column_widths()

    def refresh_icons(self) -> None:
        self._on_theme_changed("", "")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._queue_adaptive_column_widths()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._queue_adaptive_column_widths()
