from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon

from core.table_model import DynamicTableModel, TableColumn
from data.fake_records import DemoRecord
from services.icons import icon


_STATUS_COLORS = {
    "Healthy": QColor("#2FA06C"),
    "At Risk": QColor("#C58A2A"),
    "Blocked": QColor("#D55562"),
    "Review": QColor("#5D87D9"),
}

_CENTER = Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter


_ACTIONS_COLUMN_KEY = "actions"
_ACTIONS_COLUMN_HEADER = "Actions"


@dataclass(frozen=True, slots=True)
class ActionSpec:
    action_id: str
    label: str
    icon_name: str
    row_tooltip: str


_ACTION_SPECS: tuple[ActionSpec, ...] = (
    ActionSpec(
        action_id="view",
        label="View",
        icon_name="heroicons/16-solid/eye",
        row_tooltip="View record",
    ),
    ActionSpec(
        action_id="edit",
        label="Edit",
        icon_name="heroicons/16-solid/pencil-square",
        row_tooltip="Edit record",
    ),
    ActionSpec(
        action_id="delete",
        label="Delete",
        icon_name="heroicons/16-solid/trash",
        row_tooltip="Delete record",
    ),
)

_ACTION_SPEC_BY_ID = {spec.action_id: spec for spec in _ACTION_SPECS}
_DEFAULT_ACTION_IDS: tuple[str, ...] = tuple(spec.action_id for spec in _ACTION_SPECS)


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

    BASE_COLUMNS: tuple[TableColumn[DemoRecord], ...] = (
        TableColumn(
            key="record_id",
            header="ID",
            value_getter=lambda row: row.record_id,
            display_formatter=_as_int,
            alignment=_CENTER,
        ),
        TableColumn(
            key="title",
            header="Title",
            value_getter=lambda row: row.title,
            alignment=_CENTER,
        ),
        TableColumn(
            key="domain",
            header="Domain",
            value_getter=lambda row: row.domain,
            alignment=_CENTER,
        ),
        TableColumn(
            key="owner",
            header="Owner",
            value_getter=lambda row: row.owner,
            alignment=_CENTER,
        ),
        TableColumn(
            key="status",
            header="Status",
            value_getter=lambda row: row.status,
            alignment=_CENTER,
            foreground_getter=_status_color,
            tooltip_getter=_status_tooltip,
        ),
        TableColumn(
            key="score",
            header="Score",
            value_getter=lambda row: row.score,
            display_formatter=_as_int,
            alignment=_CENTER,
        ),
        TableColumn(
            key="amount",
            header="Amount",
            value_getter=lambda row: row.amount,
            display_formatter=_as_money,
            alignment=_CENTER,
        ),
        TableColumn(
            key="updated_on",
            header="Updated",
            value_getter=lambda row: row.updated_on,
            alignment=_CENTER,
        ),
    )

    @classmethod
    def available_action_ids(cls) -> tuple[str, ...]:
        return _DEFAULT_ACTION_IDS

    @classmethod
    def available_action_labels(cls) -> tuple[str, ...]:
        return tuple(spec.label for spec in _ACTION_SPECS)

    @staticmethod
    def _normalize_action_ids(action_ids: list[str] | tuple[str, ...]) -> tuple[str, ...]:
        normalized: list[str] = []
        seen: set[str] = set()
        for raw in action_ids:
            action_id = str(raw).strip().casefold()
            if not action_id or action_id in seen:
                continue
            if action_id in _ACTION_SPEC_BY_ID:
                normalized.append(action_id)
                seen.add(action_id)
        return tuple(normalized)

    @staticmethod
    def _build_action_icons(action_ids: tuple[str, ...]) -> dict[str, QIcon]:
        icons_by_id: dict[str, QIcon] = {}
        for action_id in action_ids:
            spec = _ACTION_SPEC_BY_ID.get(action_id)
            if spec is None:
                continue
            icons_by_id[action_id] = icon(spec.icon_name)
        return icons_by_id

    @staticmethod
    def _build_actions_column() -> TableColumn[DemoRecord]:
        return TableColumn(
            key=_ACTIONS_COLUMN_KEY,
            header=_ACTIONS_COLUMN_HEADER,
            value_getter=lambda _row: "",
            sort_getter=lambda _row: 0,
            alignment=_CENTER,
            tooltip_getter=lambda _row: "Choose an action for this record",
        )

    @classmethod
    def _build_columns(cls) -> tuple[TableColumn[DemoRecord], ...]:
        return cls.BASE_COLUMNS + (cls._build_actions_column(),)

    def __init__(
        self,
        records: list[DemoRecord],
        *,
        batch_size: int = 1200,
        enable_color_roles: bool = True,
        visible_actions: tuple[str, ...] | list[str] | None = None,
    ) -> None:
        self._visible_action_ids = self._normalize_action_ids(
            list(visible_actions) if visible_actions is not None else list(_DEFAULT_ACTION_IDS)
        )
        self._action_icons = self._build_action_icons(self._visible_action_ids)
        super().__init__(
            records,
            columns=self._build_columns(),
            batch_size=batch_size,
            enable_visual_roles=enable_color_roles,
            sync_update_interval_ms=12,
            sync_update_chunk_rows=260,
        )

    @property
    def visible_action_ids(self) -> tuple[str, ...]:
        return self._visible_action_ids

    def set_visible_actions(self, action_ids: tuple[str, ...] | list[str]) -> None:
        normalized = self._normalize_action_ids(list(action_ids))
        if normalized == self._visible_action_ids:
            return

        self._visible_action_ids = normalized
        self._action_icons = self._build_action_icons(self._visible_action_ids)
        self._emit_actions_column_changed()

    def refresh_action_icons(self) -> None:
        self._action_icons = self._build_action_icons(self._visible_action_ids)
        self._emit_actions_column_changed()

    def _emit_actions_column_changed(self) -> None:
        column = self.action_column_index()
        if column < 0:
            return

        visible_rows = self.rowCount()
        if visible_rows > 0:
            top_left = self.index(0, column)
            bottom_right = self.index(visible_rows - 1, column)
            self.dataChanged.emit(
                top_left,
                bottom_right,
                [
                    int(Qt.ItemDataRole.DisplayRole),
                    int(Qt.ItemDataRole.DecorationRole),
                    int(Qt.ItemDataRole.ToolTipRole),
                ],
            )

        self.headerDataChanged.emit(Qt.Orientation.Horizontal, column, column)

    def action_column_index(self) -> int:
        return self.column_index(_ACTIONS_COLUMN_KEY)

    def action_icon(self, action_id: str) -> QIcon:
        icon_ref = self._action_icons.get(action_id)
        if icon_ref is not None:
            return icon_ref

        spec = _ACTION_SPEC_BY_ID.get(action_id)
        if spec is None:
            return QIcon()

        icon_ref = icon(spec.icon_name)
        self._action_icons[action_id] = icon_ref
        return icon_ref

    def action_tooltip(self, action_id: str) -> str | None:
        spec = _ACTION_SPEC_BY_ID.get(action_id)
        if spec is None:
            return None
        return spec.row_tooltip

    def set_records(self, records: list[DemoRecord]) -> None:
        self.set_rows(records)

    def sync_records(self, records: list[DemoRecord], *, reset_change_ratio: float = 0.55) -> int:
        return self.sync_rows(records, reset_change_ratio=reset_change_ratio)
