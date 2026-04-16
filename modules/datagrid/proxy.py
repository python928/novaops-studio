from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import QModelIndex, QSortFilterProxyModel, Qt

from core.table_model import DynamicTableModel


class DataGridProxyModel(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self._search_text = ""
        self._domain_filter = "All"
        self._status_filter = "All"
        self._quick_filters: frozenset[str] = frozenset()
        self._domain_column_key = "domain"
        self._status_column_key = "status"
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortRole(DynamicTableModel.SORT_ROLE)
        self.setDynamicSortFilter(False)

    def set_search_text(self, value: str) -> None:
        text = value.strip().casefold()
        if text == self._search_text:
            return
        self._search_text = text
        self.invalidateFilter()

    def set_domain_filter(self, value: str) -> None:
        text = value.strip() or "All"
        if text == self._domain_filter:
            return
        self._domain_filter = text
        self.invalidateFilter()

    def set_status_filter(self, value: str) -> None:
        text = value.strip() or "All"
        if text == self._status_filter:
            return
        self._status_filter = text
        self.invalidateFilter()

    def set_quick_filters(self, values: list[str]) -> None:
        normalized = frozenset(
            value.strip().casefold() for value in values if str(value).strip()
        )
        if normalized == self._quick_filters:
            return
        self._quick_filters = normalized
        self.invalidateFilter()

    def _resolve_column_index(self, key: str, parent: QModelIndex) -> int:
        model = self.sourceModel()
        if model is None:
            return -1

        column_index = getattr(model, "column_index", None)
        if callable(column_index):
            index = int(column_index(key))
            if index >= 0:
                return index

        for column in range(model.columnCount(parent)):
            header = str(model.headerData(column, Qt.Orientation.Horizontal, int(Qt.ItemDataRole.DisplayRole)) or "")
            if header.strip().casefold() == key.casefold():
                return column

        return -1

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        if model is None:
            return False

        row_getter = getattr(model, "row_at", None)
        record = row_getter(source_row) if callable(row_getter) else None

        if self._domain_filter != "All":
            domain_col = self._resolve_column_index(self._domain_column_key, source_parent)
            if domain_col >= 0:
                idx = model.index(source_row, domain_col, source_parent)
                value = str(model.data(idx, int(Qt.ItemDataRole.DisplayRole)) or "")
                if value != self._domain_filter:
                    return False

        if self._status_filter != "All":
            status_col = self._resolve_column_index(self._status_column_key, source_parent)
            if status_col >= 0:
                idx = model.index(source_row, status_col, source_parent)
                value = str(model.data(idx, int(Qt.ItemDataRole.DisplayRole)) or "")
                if value != self._status_filter:
                    return False

        if self._quick_filters and record is not None:
            if not self._record_matches_quick_filters(record):
                return False

        if not self._search_text:
            return True

        for column in range(model.columnCount(source_parent)):
            idx = model.index(source_row, column, source_parent)
            value = str(model.data(idx, int(Qt.ItemDataRole.DisplayRole)) or "")
            if self._search_text in value.casefold():
                return True

        return False

    def _record_matches_quick_filters(self, record) -> bool:
        for filter_name in self._quick_filters:
            if filter_name == "needs action":
                if record.status not in {"At Risk", "Blocked"}:
                    return False
                continue

            if filter_name == "high score":
                if int(record.score) < 80:
                    return False
                continue

            if filter_name == "large amount":
                if float(record.amount) < 60000.0:
                    return False
                continue

            if filter_name == "recent updates":
                try:
                    updated = date.fromisoformat(str(record.updated_on))
                except ValueError:
                    return False
                if updated < (date.today() - timedelta(days=14)):
                    return False
                continue

        return True
