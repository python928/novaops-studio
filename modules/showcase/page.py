from __future__ import annotations

from PyQt6.QtCore import QDate, QDateTime, Qt, QTime
from PyQt6.QtWidgets import (
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTimeEdit,
    QToolBox,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from services.icons import icon
from widgets import (
    ActionTile,
    CommandDeck,
    EmptyStateCard,
    FilterChipBar,
    InfoCard,
    InsightBanner,
    KpiStrip,
    MetricCard,
    PrimaryButton,
    SectionTitle,
    SegmentedControl,
    StatusLozenge,
    StepProgress,
    TimelineFeed,
)
from widgets.controls import AppButton, AppToolButton, SearchComboBox, harmonize_combo_popup


class WidgetShowcasePage(QWidget):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.setObjectName("WidgetShowcasePage")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 18)
        root.setSpacing(12)

        title = QLabel("Widget Showcase")
        title.setObjectName("ShowcaseHeaderTitle")
        title.setProperty("title", "h2")

        subtitle = QLabel(
            "Direct widget gallery with improved dropdowns and date selection."
        )
        subtitle.setObjectName("ShowcaseHeaderSubtitle")
        subtitle.setProperty("muted", True)
        subtitle.setWordWrap(True)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(8)

        scope_label = QLabel("Section")
        scope_label.setProperty("muted", True)

        self._scope_combo = QComboBox()
        self._scope_combo.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._scope_combo.setMinimumWidth(190)
        self._scope_combo.addItems(
            [
                "All Widgets",
                "Inputs",
                "Buttons",
                "Toggles & Progress",
                "Item Views",
                "Containers",
                "Custom Widgets",
            ]
        )
        harmonize_combo_popup(self._scope_combo)
        self._scope_combo.currentTextChanged.connect(
            lambda value: context.events.statusMessage.emit(f"Showcase section: {value}")
        )

        date_label = QLabel("Preview date")
        date_label.setProperty("muted", True)

        self._preview_date = QDateEdit(QDate.currentDate())
        self._preview_date.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._preview_date.setCalendarPopup(True)
        self._preview_date.setDisplayFormat("MMM d, yyyy")
        self._preview_date.setMaximumWidth(188)
        self._preview_date.dateChanged.connect(
            lambda value: context.events.statusMessage.emit(
                f"Showcase date: {value.toString('MMM d, yyyy')}"
            )
        )

        toolbar.addWidget(scope_label)
        toolbar.addWidget(self._scope_combo)
        toolbar.addStretch(1)
        toolbar.addWidget(date_label)
        toolbar.addWidget(self._preview_date)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 6, 0)
        scroll_layout.setSpacing(12)
        scroll_layout.addWidget(self._build_inputs_section())
        scroll_layout.addWidget(self._build_buttons_section())
        scroll_layout.addWidget(self._build_toggles_progress_section())
        scroll_layout.addWidget(self._build_views_section())
        scroll_layout.addWidget(self._build_containers_section())
        scroll_layout.addWidget(self._build_custom_widgets_section())
        scroll_layout.addStretch(1)
        scroll.setWidget(scroll_content)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(toolbar)
        root.addWidget(scroll, 1)

    def _section_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("ShowcaseSectionCard")

        outer = QVBoxLayout(card)
        outer.setContentsMargins(16, 14, 16, 16)
        outer.setSpacing(10)

        header = QLabel(title)
        header.setObjectName("ShowcaseSectionTitle")
        outer.addWidget(header)

        content = QVBoxLayout()
        content.setSpacing(8)
        outer.addLayout(content)
        return card, content

    def _build_inputs_section(self) -> QWidget:
        card, content = self._section_card("Inputs")

        form = QFormLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        line = QLineEdit("Sample text")

        password = QLineEdit("secret")
        password.setEchoMode(QLineEdit.EchoMode.Password)

        combo = QComboBox()
        combo.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        combo.addItems(["Option A", "Option B", "Option C"])
        harmonize_combo_popup(combo)

        editable_combo = QComboBox()
        editable_combo.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        editable_combo.setEditable(True)
        editable_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        editable_combo.setMaxVisibleItems(12)
        editable_combo.addItems(["Editable 1", "Editable 2", "Editable 3"])
        editable_line_edit = editable_combo.lineEdit()
        if editable_line_edit is not None:
            editable_line_edit.setPlaceholderText("Type to search options...")
            editable_line_edit.setClearButtonEnabled(False)

        editable_completer = editable_combo.completer()
        if editable_completer is not None:
            editable_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            editable_completer.setFilterMode(Qt.MatchFlag.MatchContains)
            editable_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            editable_completer.setMaxVisibleItems(editable_combo.maxVisibleItems())

        harmonize_combo_popup(editable_combo)

        search_combo = SearchComboBox(placeholder_text="Search and select a city...")
        search_combo.addItems(
            [
                "Amsterdam",
                "Berlin",
                "Cairo",
                "Dubai",
                "Lisbon",
                "London",
                "Marrakesh",
                "New York",
                "Paris",
                "Singapore",
                "Tokyo",
                "Toronto",
            ]
        )
        search_combo.setCurrentIndex(-1)

        spin = QSpinBox()
        spin.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        spin.setRange(0, 1000)
        spin.setValue(42)

        dspin = QDoubleSpinBox()
        dspin.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        dspin.setRange(0.0, 9999.99)
        dspin.setDecimals(2)
        dspin.setValue(125.75)

        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("MMM d, yyyy")

        time_edit = QTimeEdit(QTime.currentTime())
        time_edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        time_edit.setDisplayFormat("h:mm AP")

        dt_edit = QDateTimeEdit(QDateTime.currentDateTime())
        dt_edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        dt_edit.setCalendarPopup(True)
        dt_edit.setDisplayFormat("MMM d, yyyy h:mm AP")

        form.addRow("QLineEdit", line)
        form.addRow("Password", password)
        form.addRow("QComboBox", combo)
        form.addRow("Editable Combo", editable_combo)
        form.addRow("Search Combo", search_combo)
        form.addRow("QSpinBox", spin)
        form.addRow("QDoubleSpinBox", dspin)
        form.addRow("QDateEdit", date_edit)
        form.addRow("QTimeEdit", time_edit)
        form.addRow("QDateTimeEdit", dt_edit)

        for field in (
            line,
            password,
            combo,
            editable_combo,
            search_combo,
            spin,
            dspin,
            date_edit,
            time_edit,
            dt_edit,
        ):
            label = form.labelForField(field)
            if label is not None:
                label.setProperty("muted", True)

        text_edit = QTextEdit("QTextEdit supports rich text and multiline editing.")
        text_edit.setFixedHeight(86)

        plain_text = QPlainTextEdit("QPlainTextEdit is ideal for plain large text.")
        plain_text.setFixedHeight(86)

        content.addLayout(form)
        content.addWidget(text_edit)
        content.addWidget(plain_text)
        return card

    def _build_buttons_section(self) -> QWidget:
        card, content = self._section_card("Buttons")

        row1 = QHBoxLayout()
        row1.setSpacing(8)

        btn_subtle = QPushButton("Subtle Action")
        btn_subtle.setProperty("subtle", True)

        btn_tonal = QPushButton("Tonal Button")
        btn_tonal.setProperty("tonal", True)

        btn_primary = QPushButton("Primary Button")
        btn_primary.setProperty("primary", True)

        btn_danger = QPushButton("Danger Button")
        btn_danger.setProperty("danger", True)

        row1.addWidget(btn_subtle)
        row1.addWidget(btn_tonal)
        row1.addWidget(btn_primary)
        row1.addWidget(btn_danger)

        row2 = QHBoxLayout()
        row2.setSpacing(8)

        tool_search = QToolButton()
        tool_search.setText("Search")
        tool_search.setIcon(icon("search"))
        tool_search.setProperty("subtle", True)
        tool_search.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        tool_settings = QToolButton()
        tool_settings.setText("Settings")
        tool_settings.setIcon(icon("settings"))
        tool_settings.setProperty("tonal", True)
        tool_settings.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        tool_refresh = QToolButton()
        tool_refresh.setText("Refresh")
        tool_refresh.setIcon(icon("refresh"))
        tool_refresh.setProperty("primary", True)
        tool_refresh.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        row2.addWidget(tool_search)
        row2.addWidget(tool_settings)
        row2.addWidget(tool_refresh)

        content.addLayout(row1)
        content.addLayout(row2)
        return card

    def _build_toggles_progress_section(self) -> QWidget:
        card, content = self._section_card("Toggles & Progress")

        checks = QHBoxLayout()
        checks.setContentsMargins(6, 0, 6, 0)
        checks.setSpacing(12)

        cb1 = QCheckBox("QCheckBox")
        cb1.setChecked(True)
        cb2 = QCheckBox("Disabled")
        cb2.setEnabled(False)

        rb1 = QRadioButton("Option 1")
        rb1.setChecked(True)
        rb2 = QRadioButton("Option 2")

        for option in (cb1, cb2, rb1, rb2):
            option.setProperty("optionChip", True)
            option.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        checks.addWidget(cb1)
        checks.addWidget(cb2)
        checks.addWidget(rb1)
        checks.addWidget(rb2)
        checks.addStretch(1)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(55)

        slider_row = QHBoxLayout()
        slider_row.setSpacing(8)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(55)
        slider.valueChanged.connect(progress.setValue)

        dial = QDial()
        dial.setRange(0, 100)
        dial.setValue(55)
        dial.valueChanged.connect(progress.setValue)
        dial.valueChanged.connect(slider.setValue)
        slider.valueChanged.connect(dial.setValue)

        lcd = QLCDNumber()
        lcd.display(55)
        slider.valueChanged.connect(lcd.display)

        slider_row.addWidget(slider, 1)
        slider_row.addWidget(dial)
        slider_row.addWidget(lcd)

        content.addLayout(checks)
        content.addWidget(progress)
        content.addLayout(slider_row)
        return card

    def _build_views_section(self) -> QWidget:
        card, content = self._section_card("Item Views")

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        list_widget = QListWidget()
        list_widget.setMinimumHeight(120)
        for item in ("Alpha", "Beta", "Gamma", "Delta"):
            QListWidgetItem(item, list_widget)

        tree = QTreeWidget()
        tree.setColumnCount(2)
        tree.setHeaderLabels(["Module", "State"])
        root_item = QTreeWidgetItem(["Core", "Ready"])
        root_item.addChild(QTreeWidgetItem(["Theme Engine", "Active"]))
        root_item.addChild(QTreeWidgetItem(["Event Bus", "Active"]))
        tree.addTopLevelItem(root_item)
        tree.expandAll()
        tree.setMinimumHeight(120)

        table = QTableWidget(4, 3)
        table.setHorizontalHeaderLabels(["ID", "Name", "Value"])
        for row in range(4):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(f"Item {row + 1}"))
            table.setItem(row, 2, QTableWidgetItem(f"{(row + 1) * 10}"))
        table.setMinimumHeight(170)

        grid.addWidget(list_widget, 0, 0)
        grid.addWidget(tree, 0, 1)
        grid.addWidget(table, 1, 0, 1, 2)

        content.addLayout(grid)
        return card

    def _build_containers_section(self) -> QWidget:
        card, content = self._section_card("Containers")

        tabs = QTabWidget()
        tabs.addTab(QLabel("Tab content A"), "QTabWidget A")
        tabs.addTab(QLabel("Tab content B"), "QTabWidget B")
        tabs.addTab(QLabel("Tab content C"), "QTabWidget C")

        toolbox = QToolBox()
        toolbox.addItem(QLabel("ToolBox page 1"), "Page 1")
        toolbox.addItem(QLabel("ToolBox page 2"), "Page 2")
        toolbox.addItem(QLabel("ToolBox page 3"), "Page 3")

        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        calendar.setMinimumHeight(240)

        content.addWidget(tabs)
        content.addWidget(toolbox)
        content.addWidget(calendar)
        return card

    def _build_custom_widgets_section(self) -> QWidget:
        card, content = self._section_card("Custom Enterprise Widgets")

        controls_title = SectionTitle("Shared Controls")

        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)

        controls_row.addWidget(PrimaryButton("PrimaryButton"))
        controls_row.addWidget(AppButton("AppButton Tonal", variant="tonal"))
        controls_row.addWidget(AppButton("AppButton Subtle", variant="subtle"))

        tool_button = AppToolButton("AppToolButton", variant="subtle")
        tool_button.setIcon(icon("refresh"))
        tool_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        controls_row.addWidget(tool_button)
        controls_row.addStretch(1)

        info_cards_row = QHBoxLayout()
        info_cards_row.setSpacing(8)
        info_cards_row.addWidget(InfoCard("InfoCard", "42", "Simple shared metric card"))
        info_cards_row.addWidget(InfoCard("Accent", "#4F8CFF", "Current visual token"))

        segmented = SegmentedControl(["Overview", "Finance", "Risk"], initial="Overview")

        command_deck = CommandDeck(
            "Command-first shell",
            "A reusable search and action layer for opening modules, running workflows, and navigating large systems.",
            badge_text="LAB",
            suggestions=("Create module", "Open dashboard", "Review blockers", "Tune theme"),
        )

        lozenges = QHBoxLayout()
        lozenges.setSpacing(7)
        lozenges.addWidget(StatusLozenge("Healthy"))
        lozenges.addWidget(StatusLozenge("At Risk"))
        lozenges.addWidget(StatusLozenge("Blocked"))
        lozenges.addWidget(StatusLozenge("Review"))
        lozenges.addStretch(1)

        chips = FilterChipBar(
            ["Needs action", "High score", "Large amount", "Recent updates"],
            multi_select=True,
            allow_empty=True,
        )

        strip = KpiStrip(
            [
                ("Healthy", "16,210", "records"),
                ("At Risk", "6,903", "records"),
                ("Blocked", "3,288", "records"),
                ("Coverage", "92%", "data mapped"),
            ]
        )

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(8)

        metrics_row.addWidget(
            MetricCard(
                "SLA",
                "99.8%",
                "Monthly service reliability",
                delta_text="+0.3%",
                trend="up",
                progress=93,
            )
        )
        metrics_row.addWidget(
            MetricCard(
                "Open Risks",
                "12",
                "Items flagged for review",
                delta_text="-4",
                trend="down",
                progress=48,
            )
        )

        action_tiles = QGridLayout()
        action_tiles.setHorizontalSpacing(8)
        action_tiles.setVerticalSpacing(8)
        action_tiles.addWidget(
            ActionTile(
                "New workspace",
                "Create a fresh module surface with shared shell pieces.",
                meta="Template",
                badge_text="+",
                tone="success",
                action_text="Create",
            ),
            0,
            0,
        )
        action_tiles.addWidget(
            ActionTile(
                "Audit UI density",
                "Check whether high-density tables and cards still read clearly.",
                meta="Review",
                badge_text="!",
                tone="warning",
                action_text="Audit",
            ),
            0,
            1,
        )

        progress = StepProgress(
            ["Source", "Normalize", "Validate", "Publish"],
            current_index=2,
        )

        timeline = TimelineFeed("Pipeline Timeline")
        timeline.set_events(
            [
                ("Data imported", "12 files accepted", "1m ago", "success"),
                ("Rules applied", "7 policy checks", "4m ago", "info"),
                ("Review required", "4 rows flagged", "9m ago", "warning"),
                ("Sync blocked", "permissions issue", "17m ago", "danger"),
            ]
        )

        timeline_row = QHBoxLayout()
        timeline_row.setSpacing(8)
        timeline_row.addWidget(progress, 1)
        timeline_row.addWidget(timeline, 1)

        empty_state = EmptyStateCard(
            "Nothing To Review",
            "When filters remove all records, this reusable empty-state component guides the next action.",
            action_text="Acknowledge",
            icon_text="0",
        )
        empty_state.set_action_visible(False)

        banner = InsightBanner(
            "Actionable Insight",
            "Reusable composite widgets are now part of the shared design system and can be dropped into any module.",
            action_text="Nice",
            icon_text="*",
        )
        banner.set_action_visible(False)

        content.addWidget(controls_title)
        content.addLayout(controls_row)
        content.addLayout(info_cards_row)
        content.addWidget(segmented)
        content.addWidget(command_deck)
        content.addLayout(lozenges)
        content.addWidget(chips)
        content.addWidget(strip)
        content.addLayout(metrics_row)
        content.addLayout(action_tiles)
        content.addLayout(timeline_row)
        content.addWidget(empty_state)
        content.addWidget(banner)
        return card

