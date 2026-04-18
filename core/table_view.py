from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QTableView


def configure_table_headers(
    table: QTableView,
    *,
    stretch_last_section: bool = False,
    min_section_width: int = 72,
) -> None:
    """Apply a consistent, centered header configuration for any table view."""
    header = table.horizontalHeader()
    header.setStretchLastSection(stretch_last_section)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    header.setMinimumSectionSize(max(36, int(min_section_width)))
    header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

    vheader = table.verticalHeader()
    vheader.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)


def apply_adaptive_column_widths(
    table: QTableView,
    *,
    sample_rows: int = 140,
    min_width: int = 92,
    max_width: int = 620,
    width_ratio_limit: float = 0.32,
    padding: int = 26,
    distribute_extra_space: bool = True,
    fixed_widths: dict[int, int] | None = None,
) -> None:
    """
    Resize columns according to header/content length while preventing oversized columns.

    The algorithm samples a bounded number of rows to preserve speed with large datasets.
    """
    model = table.model()
    if model is None:
        return

    columns = model.columnCount()
    rows = model.rowCount()
    if columns <= 0:
        return

    metrics = table.fontMetrics()
    viewport_width = max(320, table.viewport().width())
    ratio_max = max(
        min_width + 40,
        int(viewport_width * max(0.10, min(width_ratio_limit, 0.95))),
    )
    hard_max_width = max(min_width + 40, min(max_width, ratio_max))

    sample_limit = max(0, min(rows, int(sample_rows)))
    step = max(1, rows // max(1, sample_limit)) if rows > 0 else 1

    computed_widths: list[int] = []

    for column in range(columns):
        header_text = str(
            model.headerData(
                column,
                Qt.Orientation.Horizontal,
                int(Qt.ItemDataRole.DisplayRole),
            )
            or ""
        )
        width = metrics.horizontalAdvance(header_text) + padding + 8

        inspected = 0
        row = 0
        while row < rows and inspected < sample_limit:
            index = model.index(row, column)
            text = str(model.data(index, int(Qt.ItemDataRole.DisplayRole)) or "")
            if text:
                width = max(width, metrics.horizontalAdvance(text) + padding)
                if width >= hard_max_width:
                    break
            inspected += 1
            row += step

        bounded = max(min_width, min(hard_max_width, width))
        computed_widths.append(bounded)

    if not computed_widths:
        return

    fixed: dict[int, int] = {}
    if fixed_widths:
        for column, width in fixed_widths.items():
            if 0 <= int(column) < columns:
                fixed[int(column)] = max(40, int(width))

        for column, width in fixed.items():
            computed_widths[column] = width

    total_width = sum(computed_widths)
    available_width = max(0, viewport_width - 2)

    # When table content is narrower than viewport, distribute free space across columns.
    if distribute_extra_space and total_width < available_width and columns > 0:
        extra_width = available_width - total_width
        adjustable_columns = [index for index in range(columns) if index not in fixed]
        if not adjustable_columns:
            adjustable_columns = list(range(columns))

        weight_sum = max(1, sum(computed_widths[index] for index in adjustable_columns))
        additions = [0] * columns
        for index in adjustable_columns:
            additions[index] = (extra_width * computed_widths[index]) // weight_sum

        remainder = extra_width - sum(additions)
        for index in range(remainder):
            target = adjustable_columns[index % len(adjustable_columns)]
            additions[target] += 1

        computed_widths = [width + add for width, add in zip(computed_widths, additions)]
        total_width = sum(computed_widths)

    for column, width in enumerate(computed_widths):
        table.setColumnWidth(column, width)

    table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
