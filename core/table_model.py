from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, Mapping, Sequence, TypeVar

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QTimer


RowT = TypeVar("RowT")
DisplayFormatter = Callable[[Any, RowT], str]


def _normalize_sort_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.casefold()
    return value


@dataclass(frozen=True, slots=True)
class TableColumn(Generic[RowT]):
    key: str
    header: str
    value_getter: Callable[[RowT], Any]
    header_icon: Any | None = None
    header_tooltip: str | None = None
    sort_getter: Callable[[RowT], Any] | None = None
    display_formatter: DisplayFormatter | None = None
    alignment: Qt.AlignmentFlag | None = None
    foreground_getter: Callable[[RowT], Any] | None = None
    tooltip_getter: Callable[[RowT], Any] | None = None
    extra_roles: Mapping[int, Callable[[RowT], Any]] | None = None

    def display_value(self, row: RowT) -> str:
        raw_value = self.value_getter(row)
        if self.display_formatter is not None:
            return self.display_formatter(raw_value, row)
        if raw_value is None:
            return ""
        return str(raw_value)

    def sort_value(self, row: RowT) -> Any:
        value = self.sort_getter(row) if self.sort_getter is not None else self.value_getter(row)
        return _normalize_sort_value(value)


class DynamicTableModel(QAbstractTableModel, Generic[RowT]):
    SORT_ROLE = int(Qt.ItemDataRole.UserRole) + 1

    def __init__(
        self,
        rows: Sequence[RowT],
        *,
        columns: Sequence[TableColumn[RowT]],
        batch_size: int = 800,
        default_alignment: Qt.AlignmentFlag | None = (
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        ),
        enable_visual_roles: bool = True,
        sync_update_interval_ms: int = 16,
        sync_update_chunk_rows: int = 320,
    ) -> None:
        super().__init__()
        if not columns:
            raise ValueError("columns must not be empty")

        self._rows = list(rows)
        self._columns = tuple(columns)
        self._column_lookup = {column.key: index for index, column in enumerate(self._columns)}
        if len(self._column_lookup) != len(self._columns):
            raise ValueError("column keys must be unique")

        self._batch_size = max(1, batch_size)
        self._visible_count = min(len(self._rows), self._batch_size)
        self._default_alignment = default_alignment
        self._visual_roles_enabled = bool(enable_visual_roles)
        self._search_blob_cache: list[str | None] = [None] * len(self._rows)

        self._sync_update_chunk_rows = max(1, int(sync_update_chunk_rows))
        self._pending_update_rows: set[int] = set()
        self._sync_update_timer = QTimer(self)
        self._sync_update_timer.setSingleShot(True)
        self._sync_update_timer.setInterval(max(1, int(sync_update_interval_ms)))
        self._sync_update_timer.timeout.connect(self._flush_pending_updates)

    @property
    def total_count(self) -> int:
        return len(self._rows)

    @property
    def visible_count(self) -> int:
        return self._visible_count

    def set_rows(self, rows: Sequence[RowT]) -> None:
        self._sync_update_timer.stop()
        self._pending_update_rows.clear()
        self.beginResetModel()
        self._rows = list(rows)
        self._visible_count = min(len(self._rows), self._batch_size)
        self._search_blob_cache = [None] * len(self._rows)
        self.endResetModel()

    def set_columns(self, columns: Sequence[TableColumn[RowT]]) -> None:
        if not columns:
            raise ValueError("columns must not be empty")

        next_columns = tuple(columns)
        next_lookup = {column.key: index for index, column in enumerate(next_columns)}
        if len(next_lookup) != len(next_columns):
            raise ValueError("column keys must be unique")

        self._sync_update_timer.stop()
        self._pending_update_rows.clear()
        self.beginResetModel()
        self._columns = next_columns
        self._column_lookup = next_lookup
        self._search_blob_cache = [None] * len(self._rows)
        self.endResetModel()

    @property
    def visual_roles_enabled(self) -> bool:
        return self._visual_roles_enabled

    def set_visual_roles_enabled(self, enabled: bool) -> None:
        normalized = bool(enabled)
        if normalized == self._visual_roles_enabled:
            return

        self._visual_roles_enabled = normalized
        if self._visible_count <= 0 or not self._columns:
            return
        self.queue_rows_update(range(self._visible_count))

    def queue_row_update(self, row: int) -> None:
        if 0 <= row < self._visible_count:
            self._pending_update_rows.add(row)
            if not self._sync_update_timer.isActive():
                self._sync_update_timer.start()

    def queue_rows_update(self, rows: Sequence[int]) -> None:
        has_new_rows = False
        for row in rows:
            if 0 <= row < self._visible_count and row not in self._pending_update_rows:
                self._pending_update_rows.add(int(row))
                has_new_rows = True

        if has_new_rows and not self._sync_update_timer.isActive():
            self._sync_update_timer.start()

    def flush_queued_updates(self) -> None:
        self._sync_update_timer.stop()
        self._flush_pending_updates()

    def sync_rows(self, rows: Sequence[RowT], *, reset_change_ratio: float = 0.55) -> int:
        """
        Synchronize the model with incoming rows dynamically.

        - If size changed, reset model (safe generic fallback).
        - If many rows changed, reset model (faster for massive churn).
        - Otherwise, update changed rows only and emit coalesced batched updates.
        """
        incoming_rows = list(rows)
        if len(incoming_rows) != len(self._rows):
            self.set_rows(incoming_rows)
            return len(incoming_rows)

        changed_rows: list[int] = []
        for row_index, new_row in enumerate(incoming_rows):
            if self._rows[row_index] == new_row:
                continue
            self._rows[row_index] = new_row
            self._search_blob_cache[row_index] = None
            changed_rows.append(row_index)

        if not changed_rows:
            return 0

        normalized_reset_ratio = max(0.05, min(0.95, float(reset_change_ratio)))
        if (len(changed_rows) / max(1, len(incoming_rows))) >= normalized_reset_ratio:
            self.set_rows(incoming_rows)
            return len(changed_rows)

        self.queue_rows_update(changed_rows)
        return len(changed_rows)

    def _flush_pending_updates(self) -> None:
        if not self._pending_update_rows or self._visible_count <= 0 or not self._columns:
            self._pending_update_rows.clear()
            return

        rows_to_emit = sorted(self._pending_update_rows)
        self._pending_update_rows.clear()

        base_roles = [
            int(Qt.ItemDataRole.DisplayRole),
            int(Qt.ItemDataRole.TextAlignmentRole),
            self.SORT_ROLE,
        ]
        if self._visual_roles_enabled:
            base_roles.extend(
                [
                    int(Qt.ItemDataRole.ForegroundRole),
                    int(Qt.ItemDataRole.ToolTipRole),
                ]
            )

        last_column = len(self._columns) - 1
        range_start = rows_to_emit[0]
        range_end = range_start

        def emit_range(start_row: int, end_row: int) -> None:
            if start_row > end_row:
                return
            top_left = self.index(start_row, 0)
            bottom_right = self.index(end_row, last_column)
            self.dataChanged.emit(top_left, bottom_right, base_roles)

        for current_row in rows_to_emit[1:]:
            is_contiguous = current_row == range_end + 1
            within_chunk = (current_row - range_start + 1) <= self._sync_update_chunk_rows
            if is_contiguous and within_chunk:
                range_end = current_row
                continue

            emit_range(range_start, range_end)
            range_start = current_row
            range_end = current_row

        emit_range(range_start, range_end)

    def row_at(self, row: int) -> RowT | None:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def column_index(self, column_key: str) -> int:
        return self._column_lookup.get(column_key, -1)

    def column_key(self, column: int) -> str | None:
        if 0 <= column < len(self._columns):
            return self._columns[column].key
        return None

    def row_value(self, row: int, column_key: str, *, formatted: bool = False) -> Any:
        row_data = self.row_at(row)
        if row_data is None:
            return None

        column_index = self._column_lookup.get(column_key)
        if column_index is None:
            return None

        spec = self._columns[column_index]
        if formatted:
            return spec.display_value(row_data)
        return spec.value_getter(row_data)

    def search_blob(self, row: int) -> str:
        if not (0 <= row < len(self._rows)):
            return ""

        cached = self._search_blob_cache[row]
        if cached is not None:
            return cached

        row_data = self._rows[row]
        values: list[str] = []
        for spec in self._columns:
            text = spec.display_value(row_data).strip()
            if text:
                values.append(text.casefold())

        blob = " | ".join(values)
        self._search_blob_cache[row] = blob
        return blob

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return self._visible_count

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._columns)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ):
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self._columns):
            spec = self._columns[section]

            if role == int(Qt.ItemDataRole.TextAlignmentRole):
                return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            if role == int(Qt.ItemDataRole.DisplayRole):
                return spec.header

            if role == int(Qt.ItemDataRole.DecorationRole) and spec.header_icon is not None:
                return spec.header_icon

            if role == int(Qt.ItemDataRole.ToolTipRole):
                if spec.header_tooltip:
                    return spec.header_tooltip
                return spec.header or None

            return None

        if role == int(Qt.ItemDataRole.TextAlignmentRole):
            return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        if role == int(Qt.ItemDataRole.DisplayRole):
            return section + 1

        return None

    def data(self, index: QModelIndex, role: int = int(Qt.ItemDataRole.DisplayRole)):
        if not index.isValid() or not (0 <= index.row() < self._visible_count):
            return None

        column = index.column()
        if not (0 <= column < len(self._columns)):
            return None

        row = self._rows[index.row()]
        spec = self._columns[column]

        if role == int(Qt.ItemDataRole.DisplayRole):
            return spec.display_value(row)

        if role == self.SORT_ROLE:
            return spec.sort_value(row)

        if role == int(Qt.ItemDataRole.TextAlignmentRole):
            alignment = spec.alignment if spec.alignment is not None else self._default_alignment
            if alignment is not None:
                return int(alignment)

        if role == int(Qt.ItemDataRole.ForegroundRole) and spec.foreground_getter is not None:
            if not self._visual_roles_enabled:
                return None
            return spec.foreground_getter(row)

        if role == int(Qt.ItemDataRole.ToolTipRole) and spec.tooltip_getter is not None:
            if not self._visual_roles_enabled:
                return None
            return spec.tooltip_getter(row)

        if spec.extra_roles is not None:
            getter = spec.extra_roles.get(role)
            if getter is not None:
                return getter(row)

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def canFetchMore(self, parent: QModelIndex = QModelIndex()) -> bool:
        if parent.isValid():
            return False
        return self._visible_count < len(self._rows)

    def fetchMore(self, parent: QModelIndex = QModelIndex()) -> None:
        if parent.isValid():
            return

        remaining = len(self._rows) - self._visible_count
        items_to_fetch = min(remaining, self._batch_size)
        if items_to_fetch <= 0:
            return

        start = self._visible_count
        end = self._visible_count + items_to_fetch - 1
        self.beginInsertRows(QModelIndex(), start, end)
        self._visible_count += items_to_fetch
        self.endInsertRows()
