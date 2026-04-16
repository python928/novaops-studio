from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, Mapping, Sequence, TypeVar

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt


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

    @property
    def total_count(self) -> int:
        return len(self._rows)

    @property
    def visible_count(self) -> int:
        return self._visible_count

    def set_rows(self, rows: Sequence[RowT]) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self._visible_count = min(len(self._rows), self._batch_size)
        self.endResetModel()

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
        if role != int(Qt.ItemDataRole.DisplayRole):
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self._columns):
            return self._columns[section].header
        return section + 1

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

        if role == int(Qt.ItemDataRole.TextAlignmentRole) and spec.alignment is not None:
            return int(spec.alignment)

        if role == int(Qt.ItemDataRole.ForegroundRole) and spec.foreground_getter is not None:
            return spec.foreground_getter(row)

        if role == int(Qt.ItemDataRole.ToolTipRole) and spec.tooltip_getter is not None:
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
