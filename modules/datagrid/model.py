from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.table_model import DynamicTableModel, TableColumn
from data.fake_records import DemoRecord


_STATUS_COLORS = {
    "Healthy": QColor("#2FA06C"),
    "At Risk": QColor("#C58A2A"),
    "Blocked": QColor("#D55562"),
    "Review": QColor("#5D87D9"),
}


class DataGridModel(DynamicTableModel[DemoRecord]):
    @staticmethod
    def _as_int(raw_value: Any, _: DemoRecord) -> str:
        return f"{int(raw_value):d}"

    @staticmethod
    def _as_money(raw_value: Any, _: DemoRecord) -> str:
        return f"${float(raw_value):,.2f}"

    @staticmethod
    def _status_color(record: DemoRecord):
        return _STATUS_COLORS.get(record.status)

    @staticmethod
    def _status_tooltip(record: DemoRecord):
        if record.status == "Blocked":
            return "This item needs intervention before it can progress."
        if record.status == "At Risk":
            return "This item should be reviewed soon."
        return None

    COLUMNS: tuple[TableColumn[DemoRecord], ...] = (
        TableColumn(
            key="record_id",
            header="ID",
            value_getter=lambda row: row.record_id,
            display_formatter=_as_int,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        ),
        TableColumn(key="title", header="Title", value_getter=lambda row: row.title),
        TableColumn(key="domain", header="Domain", value_getter=lambda row: row.domain),
        TableColumn(key="owner", header="Owner", value_getter=lambda row: row.owner),
        TableColumn(
            key="status",
            header="Status",
            value_getter=lambda row: row.status,
            foreground_getter=_status_color,
            tooltip_getter=_status_tooltip,
        ),
        TableColumn(
            key="score",
            header="Score",
            value_getter=lambda row: row.score,
            display_formatter=_as_int,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        ),
        TableColumn(
            key="amount",
            header="Amount",
            value_getter=lambda row: row.amount,
            display_formatter=_as_money,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        ),
        TableColumn(key="updated_on", header="Updated", value_getter=lambda row: row.updated_on),
    )

    def __init__(self, records: list[DemoRecord], *, batch_size: int = 1200) -> None:
        super().__init__(records, columns=self.COLUMNS, batch_size=batch_size)

    def set_records(self, records: list[DemoRecord]) -> None:
        self.set_rows(records)
