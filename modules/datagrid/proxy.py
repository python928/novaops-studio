from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt

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
        self._domain_column_index = -1
        self._status_column_index = -1
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortRole(DynamicTableModel.SORT_ROLE)
        self.setDynamicSortFilter(False)

    def setSourceModel(self, source_model: QAbstractItemModel | None) -> None:
        previous = self.sourceModel()
        if previous is not None:
            self._disconnect_model_signals(previous)

        super().setSourceModel(source_model)

        if source_model is not None:
            source_model.modelReset.connect(self._refresh_column_cache)
            source_model.layoutChanged.connect(self._refresh_column_cache)
            source_model.columnsInserted.connect(self._refresh_column_cache)
            source_model.columnsRemoved.connect(self._refresh_column_cache)

        self._refresh_column_cache()

    def _disconnect_model_signals(self, model: QAbstractItemModel) -> None:
        for signal in (
            model.modelReset,
            model.layoutChanged,
            model.columnsInserted,
            model.columnsRemoved,
        ):
            try:
                signal.disconnect(self._refresh_column_cache)
            except (TypeError, RuntimeError):
                pass

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

    def _refresh_column_cache(self, *_args) -> None:
        self._domain_column_index = self._resolve_column_index(self._domain_column_key, QModelIndex())
        self._status_column_index = self._resolve_column_index(self._status_column_key, QModelIndex())
        self.invalidateFilter()

    def _column_display_value(
        self,
        source_row: int,
        source_parent: QModelIndex,
        *,
        key: str,
        fallback_column: int,
    ) -> str:
        model = self.sourceModel()
        if model is None:
            return ""

        row_value = getattr(model, "row_value", None)
        if callable(row_value):
            value = row_value(source_row, key, formatted=True)
            return str(value or "")

        column = fallback_column
        if column < 0:
            column = self._resolve_column_index(key, source_parent)
        if column < 0:
            return ""

        idx = model.index(source_row, column, source_parent)
        return str(model.data(idx, int(Qt.ItemDataRole.DisplayRole)) or "")

    def _matches_search(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self._search_text:
            return True

        model = self.sourceModel()
        if model is None:
            return False

        search_blob = getattr(model, "search_blob", None)
        if callable(search_blob):
            return self._search_text in str(search_blob(source_row))

        for column in range(model.columnCount(source_parent)):
            idx = model.index(source_row, column, source_parent)
            value = str(model.data(idx, int(Qt.ItemDataRole.DisplayRole)) or "")
            if self._search_text in value.casefold():
                return True
        return False

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        if model is None:
            return False

        row_getter = getattr(model, "row_at", None)
        record = row_getter(source_row) if callable(row_getter) else None

        if self._domain_filter != "All":
            domain_value = self._column_display_value(
                source_row,
                source_parent,
                key=self._domain_column_key,
                fallback_column=self._domain_column_index,
            )
            if domain_value != self._domain_filter:
                return False

        if self._status_filter != "All":
            status_value = self._column_display_value(
                source_row,
                source_parent,
                key=self._status_column_key,
                fallback_column=self._status_column_index,
            )
            if status_value != self._status_filter:
                return False

        if self._quick_filters and record is not None:
            if not self._record_matches_quick_filters(record):
                return False

        return self._matches_search(source_row, source_parent)

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
