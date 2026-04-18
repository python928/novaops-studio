from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from modules import ModuleSpec, default_module_specs
from services.icons import icon
from themes.tokens import ThemeMode
from widgets.controls import harmonize_combo_popup


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        self._specs: dict[str, ModuleSpec] = {
            spec.key: spec for spec in default_module_specs(context)
        }
        self._pages: dict[str, QWidget] = {}
        self._nav_buttons: dict[str, QPushButton] = {}
        self._module_hints = {
            "showcase": "Reference board for every control and interaction state.",
            "dashboard": "High-signal overview for operations and KPIs.",
            "datagrid": "Large dataset workflow with filter and sort controls.",
            "settings": "Theme, accent, and layout preferences.",
        }

        self.setWindowTitle("NovaOps Studio")
        self.resize(1360, 860)

        central = QFrame()
        central.setObjectName("AppBackground")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 10)
        root.setSpacing(12)

        sidebar = self._build_sidebar()
        content = self._build_content_area()

        root.addWidget(sidebar, 0)
        root.addWidget(content, 1)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self._context.events.statusMessage.connect(status_bar.showMessage)

        self._context.theme.themeChanged.connect(self._on_theme_changed)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        self._on_theme_changed(self._context.theme.mode.value, self._context.theme.accent)

        first_key = next(iter(self._specs.keys()))
        self._activate_module(first_key)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(304)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        header_card = QFrame()
        header_card.setObjectName("SidebarHeader")
        header_card_layout = QVBoxLayout(header_card)
        header_card_layout.setContentsMargins(12, 10, 12, 12)
        header_card_layout.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        menu_button = QToolButton()
        menu_button.setObjectName("MainRailMenuButton")
        menu_button.setIcon(icon("heroicons/24-solid/bars-3"))
        menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        menu_button.clicked.connect(
            lambda: self._context.events.statusMessage.emit("Main menu is ready for custom actions")
        )
        self._menu_button = menu_button

        avatar = QLabel("UI")
        avatar.setObjectName("MainRailAvatar")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addWidget(menu_button)
        header.addStretch(1)
        header.addWidget(avatar)
        header_card_layout.addLayout(header)
        header_card_layout.addSpacing(2)

        brand = QLabel("Nova Workspace")
        brand.setObjectName("MainRailTitle")
        subtitle = QLabel("Scalable shell for enterprise modules")
        subtitle.setProperty("muted", True)

        header_card_layout.addWidget(brand)
        header_card_layout.addWidget(subtitle)
        layout.addWidget(header_card)

        section_label = QLabel("MODULES")
        section_label.setProperty("kicker", True)
        layout.addWidget(section_label)

        for key, spec in self._specs.items():
            button = QPushButton(spec.title)
            button.setProperty("nav", True)
            button.setProperty("active", False)
            button.setIcon(icon(spec.icon_name))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _=False, module_key=key: self._activate_module(module_key))
            self._nav_buttons[key] = button
            layout.addWidget(button)

        layout.addStretch(1)

        footer_card = QFrame()
        footer_card.setObjectName("SidebarFooter")
        footer_layout = QVBoxLayout(footer_card)
        footer_layout.setContentsMargins(12, 12, 12, 12)
        footer_layout.setSpacing(8)

        footer_title = QLabel("Need guidance?")
        footer_title.setProperty("title", "h3")

        footer_hint = QLabel("Theme and widgets are tuned for data-heavy enterprise screens.")
        footer_hint.setProperty("muted", True)
        footer_hint.setWordWrap(True)

        footer_button = QPushButton("Open Support")
        footer_button.setProperty("primary", True)
        footer_button.clicked.connect(
            lambda: self._context.events.statusMessage.emit("Support workflow can be connected here")
        )

        footer_layout.addWidget(footer_title)
        footer_layout.addWidget(footer_hint)
        footer_layout.addWidget(footer_button)
        layout.addWidget(footer_card)
        return sidebar

    def _build_content_area(self) -> QWidget:
        content = QFrame()
        content.setObjectName("ContentHost")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        topbar = QFrame()
        topbar.setObjectName("TopBar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(16, 10, 16, 10)
        topbar_layout.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)

        self._page_title = QLabel("-")
        self._page_title.setObjectName("PageTitle")

        self._page_subtitle = QLabel("Scalable module surface")
        self._page_subtitle.setProperty("muted", True)

        title_col.addWidget(self._page_title)
        title_col.addWidget(self._page_subtitle)
        topbar_layout.addLayout(title_col, 1)

        self._global_search = QLineEdit()
        self._global_search.setObjectName("GlobalSearch")
        self._global_search.setPlaceholderText("Quick search or command...")
        self._global_search.setClearButtonEnabled(False)
        self._global_search.returnPressed.connect(self._emit_search_status)

        self._mode_chip = QLabel("-")
        self._mode_chip.setObjectName("TopBarMetaChip")

        self._theme_toggle = QPushButton("Toggle Theme")
        self._theme_toggle.setProperty("tonal", True)
        self._theme_toggle.clicked.connect(self._toggle_theme)

        topbar_layout.addWidget(self._global_search)
        topbar_layout.addWidget(self._mode_chip)
        topbar_layout.addWidget(self._theme_toggle)

        viewport = QFrame()
        viewport.setObjectName("ContentViewport")
        viewport_layout = QVBoxLayout(viewport)
        viewport_layout.setContentsMargins(2, 2, 2, 2)
        viewport_layout.setSpacing(0)

        self._stack = QStackedWidget()
        viewport_layout.addWidget(self._stack)

        layout.addWidget(topbar)
        layout.addWidget(viewport, 1)
        return content

    def _activate_module(self, module_key: str) -> None:
        spec = self._specs[module_key]

        page = self._pages.get(module_key)
        if page is None:
            page = spec.page_factory(self._context)
            self._pages[module_key] = page
            self._stack.addWidget(page)

        self._stack.setCurrentWidget(page)
        self._harmonize_dropdowns(page)
        self._page_title.setText(spec.title)
        self._page_subtitle.setText(self._module_hints.get(module_key, "Scalable module surface"))
        self._context.events.moduleChanged.emit(module_key)
        self._update_nav_state(module_key)

    def _harmonize_dropdowns(self, root: QWidget | None = None) -> None:
        target = root if root is not None else self

        if isinstance(target, QComboBox):
            harmonize_combo_popup(target)

        for combo in target.findChildren(QComboBox):
            harmonize_combo_popup(combo)

    def _update_nav_state(self, active_key: str) -> None:
        for key, button in self._nav_buttons.items():
            button.setProperty("active", key == active_key)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def _toggle_theme(self) -> None:
        self._context.theme.toggle_mode()
        self._context.settings.save_theme_mode(self._context.theme.mode.value)

    def _emit_search_status(self) -> None:
        query = self._global_search.text().strip()
        if query:
            self._context.events.statusMessage.emit(f"Quick search: {query}")
            return
        self._context.events.statusMessage.emit("Enter a query to use quick search")

    def _on_theme_changed(self, mode: str, accent: str) -> None:
        is_dark = mode == ThemeMode.DARK.value
        self._menu_button.setIcon(icon("heroicons/24-solid/bars-3"))
        for key, spec in self._specs.items():
            button = self._nav_buttons.get(key)
            if button is not None:
                button.setIcon(icon(spec.icon_name))

        for page in self._pages.values():
            refresh_icons = getattr(page, "refresh_icons", None)
            if callable(refresh_icons):
                refresh_icons()

        self._harmonize_dropdowns(self)

        self._mode_chip.setText("Dark Mode" if is_dark else "Light Mode")
        self._theme_toggle.setIcon(icon("sun" if is_dark else "moon"))
        self._theme_toggle.setText("Switch To Light" if is_dark else "Switch To Dark")
        self._context.events.statusMessage.emit(f"Theme: {mode}, accent: {accent}")

    def eventFilter(self, obj, event) -> bool:
        if isinstance(obj, QComboBox) and event.type() in (
            QEvent.Type.Show,
            QEvent.Type.Polish,
        ):
            harmonize_combo_popup(obj)

        return super().eventFilter(obj, event)
