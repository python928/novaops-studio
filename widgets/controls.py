from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QCompleter,
    QListView,
    QPushButton,
    QStyledItemDelegate,
    QToolButton,
    QWidget,
)


def refresh_style(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def apply_properties(widget: QWidget, /, **properties: object) -> QWidget:
    for name, value in properties.items():
        widget.setProperty(name, value)
    refresh_style(widget)
    return widget


class _ComboPopupItemDelegate(QStyledItemDelegate):
    def __init__(self, *, row_height: int = 30, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._row_height = max(24, row_height)

    def sizeHint(self, option, index):
        hint = super().sizeHint(option, index)
        hint.setHeight(self._row_height)
        return QSize(hint.width(), hint.height())


def _harmonize_popup_view(view: QAbstractItemView, *, popup_name: str) -> None:
    view.setObjectName(popup_name)
    if isinstance(view, QListView):
        view.setUniformItemSizes(True)

    current_delegate = view.itemDelegate()
    if not isinstance(current_delegate, _ComboPopupItemDelegate):
        view.setItemDelegate(_ComboPopupItemDelegate(parent=view))


def harmonize_combo_popup(combo: QComboBox, *, popup_name: str = "ComboPopupView") -> None:
    view = combo.view()
    if view is not None:
        _harmonize_popup_view(view, popup_name=popup_name)

    completer = combo.completer()
    if completer is None:
        return

    popup = completer.popup()
    if popup is None:
        popup = QListView(combo)
        completer.setPopup(popup)

    if popup is not None:
        _harmonize_popup_view(popup, popup_name=popup_name)


class SearchComboBox(QComboBox):
    def __init__(
        self,
        *,
        placeholder_text: str = "Search...",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setMaxVisibleItems(12)

        popup_view = QListView(self)
        popup_view.setObjectName("ComboPopupView")
        self.setView(popup_view)

        line_edit = self.lineEdit()
        if line_edit is not None:
            line_edit.setClearButtonEnabled(False)
            line_edit.setPlaceholderText(placeholder_text)

        completer = self.completer()
        if completer is not None:
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setMaxVisibleItems(self.maxVisibleItems())

        harmonize_combo_popup(self)


class AppButton(QPushButton):
    _VARIANT_FLAGS = ("primary", "tonal", "danger", "subtle")

    def __init__(
        self,
        text: str,
        *,
        variant: str = "tonal",
    ) -> None:
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_variant(variant)

    def set_variant(self, variant: str) -> None:
        normalized = variant.strip().casefold()
        active_variant = normalized if normalized in self._VARIANT_FLAGS else "tonal"

        for flag in self._VARIANT_FLAGS:
            self.setProperty(flag, flag == active_variant)
        refresh_style(self)


class AppToolButton(QToolButton):
    _VARIANT_FLAGS = ("primary", "tonal", "danger", "subtle")

    def __init__(
        self,
        text: str = "",
        *,
        variant: str = "subtle",
        icon_only: bool = False,
    ) -> None:
        super().__init__()
        if text:
            self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("iconOnly", bool(icon_only))
        self.set_variant(variant)

    def set_variant(self, variant: str) -> None:
        normalized = variant.strip().casefold()
        active_variant = normalized if normalized in self._VARIANT_FLAGS else "subtle"

        for flag in self._VARIANT_FLAGS:
            self.setProperty(flag, flag == active_variant)
        refresh_style(self)


class PrimaryButton(AppButton):
    def __init__(self, text: str) -> None:
        super().__init__(text, variant="primary")


class SectionTitle(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setEnabled(False)
        self.setFlat(True)
        self.setProperty("sectionTitle", True)
