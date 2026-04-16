from __future__ import annotations

from collections import Counter

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from core.constants import TABLE_BATCH_SIZE, TABLE_DEMO_ROW_COUNT
from data.fake_records import generate_demo_records
from modules.datagrid.model import DataGridModel
from modules.datagrid.proxy import DataGridProxyModel
from services.icons import icon
from widgets import EmptyStateCard, FilterChipBar, InsightBanner, KpiStrip, SegmentedControl


class DataGridPage(QWidget):
    def __init__(self, _: AppContext) -> None:
        super().__init__()

        self._records = generate_demo_records(TABLE_DEMO_ROW_COUNT)
        self._model = DataGridModel(self._records, batch_size=TABLE_BATCH_SIZE)
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

        toolbar = QFrame()
        toolbar.setObjectName("Card")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(8)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search across all columns...")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._proxy.set_search_text)

        self._domain_filter = QComboBox()
        self._domain_filter.setMinimumWidth(170)
        self._domain_filter.currentTextChanged.connect(self._proxy.set_domain_filter)

        self._status_filter = SegmentedControl(
            ["All", "Healthy", "At Risk", "Blocked", "Review"],
            initial="All",
        )
        self._status_filter.selectionChanged.connect(self._proxy.set_status_filter)

        self._quick_filters = FilterChipBar(
            ["Needs action", "High score", "Large amount", "Recent updates"],
            multi_select=True,
            allow_empty=True,
        )
        self._quick_filters.selectionChanged.connect(self._proxy.set_quick_filters)

        self._reload_button = QPushButton("Reload")
        self._reload_button.setIcon(icon("refresh"))
        self._reload_button.setProperty("tonal", True)
        self._reload_button.clicked.connect(self._reload_data)

        self._count_label = QLabel("")
        self._count_label.setProperty("chip", True)

        toolbar_layout.addWidget(self._search, 1)
        toolbar_layout.addWidget(self._domain_filter)
        toolbar_layout.addWidget(self._status_filter)
        toolbar_layout.addWidget(self._reload_button)
        toolbar_layout.addWidget(self._count_label)

        self._table = QTableView()
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.setShowGrid(False)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setWordWrap(False)
        self._table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(30)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setModel(self._proxy)
        self._table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

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
        root.addWidget(toolbar)
        root.addWidget(self._quick_filters)
        root.addWidget(self._table_stack, 1)

        self._setup_domain_filter()
        self._attach_count_signals()
        self._refresh_count_label()

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

    def _refresh_count_label(self) -> None:
        visible = self._proxy.rowCount()
        total = self._model.total_count
        self._count_label.setText(f"Rows: {visible:,} / {total:,}")
        self._table_stack.setCurrentWidget(self._empty_state if visible == 0 else self._table)

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
        self._records = generate_demo_records(TABLE_DEMO_ROW_COUNT)
        self._model.set_records(self._records)
        self._setup_domain_filter()
        self._refresh_summary_strip()
        self._proxy.invalidate()
        self._refresh_count_label()
