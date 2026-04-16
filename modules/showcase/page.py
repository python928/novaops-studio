from __future__ import annotations

from PyQt6.QtCore import QDate, QDateTime, QSize, Qt, QTime
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
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
    QSizePolicy,
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
    EmptyStateCard,
    FilterChipBar,
    InsightBanner,
    KpiStrip,
    MetricCard,
    SegmentedControl,
    StatusLozenge,
    StepProgress,
    TimelineFeed,
)


class WidgetShowcasePage(QWidget):
    def __init__(self, _: AppContext) -> None:
        super().__init__()
        self.setObjectName("FlutterReferenceCanvas")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 12, 20, 18)
        root.setSpacing(0)
        root.addStretch(1)

        self._board = self._build_board()
        root.addWidget(self._board, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addStretch(1)

        self._dots = self._create_decorative_dots()

    def _build_board(self) -> QWidget:
        board = QFrame()
        board.setObjectName("FlutterBoard")
        board.setMinimumSize(860, 620)
        board.setMaximumWidth(1160)
        board.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        shadow = QGraphicsDropShadowEffect(board)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(40, 72, 140, 45))
        board.setGraphicsEffect(shadow)

        board_layout = QHBoxLayout(board)
        board_layout.setContentsMargins(0, 0, 0, 0)
        board_layout.setSpacing(0)
        board_layout.addWidget(self._build_note_rail())
        board_layout.addWidget(self._build_note_body(), 1)
        return board

    def _build_note_rail(self) -> QWidget:
        rail = QFrame()
        rail.setObjectName("FlutterNoteRail")
        rail.setFixedWidth(308)

        layout = QVBoxLayout(rail)
        layout.setContentsMargins(16, 14, 14, 16)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)

        menu_button = QToolButton()
        menu_button.setObjectName("FlutterMenuButton")
        menu_button.setIcon(icon("heroicons/24-solid/bars-3"))
        menu_button.setIconSize(QSize(22, 22))
        menu_button.setCursor(Qt.CursorShape.PointingHandCursor)

        avatar = QLabel("AM")
        avatar.setObjectName("FlutterAvatar")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addWidget(menu_button, 0, Qt.AlignmentFlag.AlignLeft)
        header.addStretch(1)
        header.addWidget(avatar)
        header.addStretch(1)
        layout.addLayout(header)
        layout.addSpacing(10)

        note_items = (
            "Meeting Points #1",
            "Important notes",
            "Veggies Needed",
            "Prince food",
            "Remainders",
            "List of Tasks",
            "Lectures",
        )
        for label in note_items:
            button = QPushButton(label)
            button.setProperty("noteTab", True)
            button.setProperty("activeItem", label == "Veggies Needed")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(button)

        layout.addStretch(1)
        return rail

    def _build_note_body(self) -> QWidget:
        body = QFrame()
        body.setObjectName("FlutterNoteBody")

        layout = QVBoxLayout(body)
        layout.setContentsMargins(26, 22, 26, 20)
        layout.setSpacing(16)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        toolbar_icons = (
            ("Tt", None, True),
            ("", "heroicons/24-solid/viewfinder-circle", False),
            ("", "heroicons/24-solid/check-circle", True),
            ("", "heroicons/24-solid/paper-clip", False),
            ("", "heroicons/24-solid/code-bracket", False),
            ("", "heroicons/24-solid/microphone", False),
            ("", "heroicons/24-solid/video-camera", False),
        )
        for text, icon_name, selected in toolbar_icons:
            button = QToolButton()
            button.setObjectName("FlutterToolbarButton")
            button.setProperty("selected", selected)
            if text:
                button.setText(text)
                button.setProperty("glyph", True)
            if icon_name:
                button.setIcon(icon(icon_name))
                button.setIconSize(QSize(18, 18))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            toolbar.addWidget(button)

        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        title = QLabel("All Widgets Gallery")
        title.setObjectName("FlutterTaskTitle")
        layout.addWidget(title)

        subtitle = QLabel("Everything in one place with the same reference-style pattern.")
        subtitle.setObjectName("FlutterBodySubtitle")
        subtitle.setProperty("muted", True)
        layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setObjectName("FlutterBodyScroll")
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
        layout.addWidget(scroll, 1)

        actions = QHBoxLayout()
        actions.setSpacing(18)
        actions.addStretch(1)

        action_icons = (
            "heroicons/24-solid/pencil-square",
            "heroicons/24-solid/bold",
            "heroicons/24-solid/document",
            "heroicons/24-solid/trash",
            "heroicons/24-solid/paper-airplane",
        )
        for icon_name in action_icons:
            button = QToolButton()
            button.setObjectName("FlutterActionButton")
            button.setIcon(icon(icon_name))
            button.setIconSize(QSize(20, 20))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            actions.addWidget(button)

        actions.addStretch(1)
        layout.addLayout(actions)
        return body

    def _section_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("FlutterSectionCard")

        outer = QVBoxLayout(card)
        outer.setContentsMargins(16, 14, 16, 16)
        outer.setSpacing(10)

        header = QLabel(title)
        header.setObjectName("FlutterSectionTitle")
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
        combo.addItems(["Option A", "Option B", "Option C"])

        editable_combo = QComboBox()
        editable_combo.setEditable(True)
        editable_combo.addItems(["Editable 1", "Editable 2", "Editable 3"])

        spin = QSpinBox()
        spin.setRange(0, 1000)
        spin.setValue(42)

        dspin = QDoubleSpinBox()
        dspin.setRange(0.0, 9999.99)
        dspin.setDecimals(2)
        dspin.setValue(125.75)

        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("MMM d, yyyy")

        time_edit = QTimeEdit(QTime.currentTime())
        time_edit.setDisplayFormat("h:mm AP")

        dt_edit = QDateTimeEdit(QDateTime.currentDateTime())
        dt_edit.setCalendarPopup(True)
        dt_edit.setDisplayFormat("MMM d, yyyy h:mm AP")

        form.addRow("QLineEdit", line)
        form.addRow("Password", password)
        form.addRow("QComboBox", combo)
        form.addRow("Editable Combo", editable_combo)
        form.addRow("QSpinBox", spin)
        form.addRow("QDoubleSpinBox", dspin)
        form.addRow("QDateEdit", date_edit)
        form.addRow("QTimeEdit", time_edit)
        form.addRow("QDateTimeEdit", dt_edit)

        for field in (line, password, combo, editable_combo, spin, dspin, date_edit, time_edit, dt_edit):
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

        btn_default = QPushButton("Default Button")
        btn_default.setProperty("tonal", True)

        btn_primary = QPushButton("Primary Button")
        btn_primary.setProperty("primary", True)

        btn_danger = QPushButton("Danger Button")
        btn_danger.setProperty("danger", True)

        row1.addWidget(btn_default)
        row1.addWidget(btn_primary)
        row1.addWidget(btn_danger)

        row2 = QHBoxLayout()
        row2.setSpacing(8)

        tool_search = QToolButton()
        tool_search.setText("Search")
        tool_search.setIcon(icon("search"))
        tool_search.setProperty("tonal", True)
        tool_search.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        tool_settings = QToolButton()
        tool_settings.setText("Settings")
        tool_settings.setIcon(icon("settings"))
        tool_settings.setProperty("tonal", True)
        tool_settings.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        tool_refresh = QToolButton()
        tool_refresh.setText("Refresh")
        tool_refresh.setIcon(icon("refresh"))
        tool_refresh.setProperty("tonal", True)
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
        checks.setSpacing(10)

        cb1 = QCheckBox("QCheckBox")
        cb1.setChecked(True)
        cb2 = QCheckBox("Disabled")
        cb2.setEnabled(False)

        rb1 = QRadioButton("Option 1")
        rb1.setChecked(True)
        rb2 = QRadioButton("Option 2")

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

        segmented = SegmentedControl(["Overview", "Finance", "Risk"], initial="Overview")

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

        content.addWidget(segmented)
        content.addLayout(lozenges)
        content.addWidget(chips)
        content.addWidget(strip)
        content.addLayout(metrics_row)
        content.addLayout(timeline_row)
        content.addWidget(empty_state)
        content.addWidget(banner)
        return card

    def _create_decorative_dots(self) -> dict[str, QFrame]:
        names = (
            "FlutterDotTopRight",
            "FlutterDotLeftMid",
            "FlutterDotRightMid",
            "FlutterDotBottomLeft",
            "FlutterDotBottomCenter",
        )
        dots: dict[str, QFrame] = {}
        for name in names:
            dot = QFrame(self)
            dot.setObjectName(name)
            dot.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            dot.lower()
            dots[name] = dot
        return dots

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        width = self.width()
        height = self.height()
        dot_specs = {
            "FlutterDotTopRight": (width - 190, 4, 168),
            "FlutterDotLeftMid": (max(6, width // 12), height // 3, 58),
            "FlutterDotRightMid": (width - 130, (height * 2) // 3 - 26, 62),
            "FlutterDotBottomLeft": (-118, height - 244, 296),
            "FlutterDotBottomCenter": (width // 2 - 34, height - 104, 68),
        }
        accent = self.palette().color(QPalette.ColorRole.Link).name()
        for name, (x_pos, y_pos, size) in dot_specs.items():
            dot = self._dots.get(name)
            if dot is not None:
                dot.setGeometry(x_pos, y_pos, size, size)
                dot.setStyleSheet(
                    f"background-color: {accent}; border: none; border-radius: {size // 2}px;"
                )
