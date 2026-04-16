from __future__ import annotations

from PyQt6.QtGui import QColor

from themes.tokens import ThemeTokens


def _rgba(color: str, alpha: int) -> str:
    qcolor = QColor(color)
    clamped = max(0, min(alpha, 255))
    return f"rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {clamped})"


def build_stylesheet(tokens: ThemeTokens) -> str:
    surface_glass = _rgba(tokens.surface, 232)
    surface_alt_glass = _rgba(tokens.surface_alt, 220)
    sidebar_glass = _rgba(tokens.sidebar, 236)
    border_soft = _rgba(tokens.border, 182)
    accent_soft = _rgba(tokens.accent, 48)
    accent_mid = _rgba(tokens.accent, 94)
    success_soft = _rgba(tokens.success, 45)
    success_mid = _rgba(tokens.success, 120)
    warning_soft = _rgba(tokens.warning, 45)
    warning_mid = _rgba(tokens.warning, 120)
    danger_soft = _rgba(tokens.danger, 45)
    danger_mid = _rgba(tokens.danger, 120)

    return f"""
    QWidget {{
        color: {tokens.text_primary};
        font-family: "Manrope", "Inter", "Segoe UI", "Noto Sans", sans-serif;
        font-size: 14px;
        selection-background-color: {tokens.selection_bg};
        selection-color: {tokens.text_primary};
    }}

    QWidget:focus {{
        outline: none;
    }}

    QFrame#AppBackground {{
        background-color: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 {tokens.window},
            stop: 0.55 {tokens.sidebar},
            stop: 1 {tokens.surface_alt}
        );
    }}

    QFrame#Sidebar {{
        background-color: {sidebar_glass};
        border-right: 1px solid {border_soft};
    }}

    QFrame#SidebarHeader,
    QFrame#SidebarFooter {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 16px;
    }}

    QFrame#ContentHost {{
        background: transparent;
    }}

    QFrame#TopBar {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 18px;
    }}

    QFrame#ContentViewport {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 20px;
    }}

    QLabel#TopBarMetaChip {{
        background-color: {accent_soft};
        border: 1px solid {accent_mid};
        border-radius: 11px;
        padding: 3px 10px;
        color: {tokens.text_secondary};
        font-size: 12px;
        font-weight: 700;
    }}

    QStatusBar {{
        background-color: {surface_glass};
        border-top: 1px solid {border_soft};
        color: {tokens.text_secondary};
    }}

    QStatusBar::item {{
        border: none;
    }}

    QFrame#Card,
    QGroupBox#Card {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 16px;
    }}

    QGroupBox#Card {{
        margin-top: 12px;
        padding-top: 10px;
    }}

    QGroupBox#Card::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 14px;
        padding: 0 7px;
        color: {tokens.text_secondary};
        background: {surface_glass};
        font-size: 12px;
        font-weight: 700;
    }}

    QLabel#MainRailTitle {{
        font-size: 17px;
        font-weight: 700;
        color: {tokens.text_primary};
        padding-left: 1px;
    }}

    QToolButton#MainRailMenuButton {{
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
        border-radius: 18px;
        border: 1px solid transparent;
        background: transparent;
        color: {tokens.accent};
        padding: 0;
    }}

    QToolButton#MainRailMenuButton:hover {{
        background-color: {accent_soft};
        border-color: {accent_mid};
    }}

    QLabel#MainRailAvatar {{
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        border-radius: 20px;
        border: 1px solid {accent_mid};
        background-color: {accent_soft};
        color: {tokens.text_primary};
        font-size: 12px;
        font-weight: 800;
    }}

    QLabel#PageTitle {{
        font-size: 24px;
        font-weight: 700;
    }}

    QLabel[headline="true"] {{
        font-size: 24px;
        font-weight: 700;
    }}

    QLabel[title="h1"] {{
        font-size: 24px;
        font-weight: 700;
    }}

    QLabel[title="h2"] {{
        font-size: 20px;
        font-weight: 700;
    }}

    QLabel[title="h3"] {{
        font-size: 16px;
        font-weight: 700;
    }}

    QLabel[metric="true"] {{
        font-size: 30px;
        font-weight: 800;
    }}

    QLabel[kicker="true"] {{
        color: {tokens.text_muted};
        font-size: 11px;
        font-weight: 700;
    }}

    QLabel[chip="true"] {{
        background-color: {accent_soft};
        border: 1px solid {accent_mid};
        border-radius: 11px;
        padding: 3px 10px;
        font-size: 12px;
        font-weight: 700;
        color: {tokens.text_secondary};
    }}

    QLabel[muted="true"] {{
        color: {tokens.text_muted};
        font-size: 13px;
    }}

    QPushButton[nav="true"],
    QPushButton[noteTab="true"] {{
        text-align: left;
        min-height: 40px;
        padding: 0 14px;
        border-radius: 12px;
        border: 1px solid transparent;
        background-color: transparent;
        color: {tokens.text_secondary};
        font-weight: 600;
        font-size: 15px;
    }}

    QPushButton[nav="true"]:hover,
    QPushButton[noteTab="true"]:hover {{
        background-color: {surface_alt_glass};
        border-color: {border_soft};
        color: {tokens.text_primary};
    }}

    QPushButton[nav="true"][active="true"],
    QPushButton[noteTab="true"][activeItem="true"] {{
        background-color: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 {tokens.accent},
            stop: 1 {tokens.accent_hover}
        );
        border-color: transparent;
        color: {tokens.accent_contrast};
        font-weight: 700;
    }}

    QPushButton,
    QToolButton {{
        min-height: 38px;
        padding: 7px 14px;
        border-radius: 11px;
        border: 1px solid {border_soft};
        background-color: {surface_alt_glass};
        color: {tokens.text_primary};
        font-weight: 600;
    }}

    QPushButton:hover,
    QToolButton:hover {{
        border-color: {accent_mid};
        background-color: {surface_glass};
    }}

    QPushButton:pressed,
    QToolButton:pressed {{
        background-color: {tokens.selection_bg};
        border-color: {tokens.accent_pressed};
    }}

    QPushButton:disabled,
    QToolButton:disabled {{
        color: {tokens.text_muted};
        border-color: {border_soft};
        background-color: {surface_glass};
    }}

    QPushButton[tonal="true"],
    QToolButton[tonal="true"] {{
        background-color: {accent_soft};
        border-color: {accent_mid};
        color: {tokens.text_primary};
        font-weight: 700;
    }}

    QPushButton[tonal="true"]:hover,
    QToolButton[tonal="true"]:hover {{
        background-color: {tokens.selection_bg};
        border-color: {tokens.accent};
    }}

    QPushButton[sectionTitle="true"] {{
        text-align: left;
        min-height: 28px;
        padding: 0;
        border: none;
        background: transparent;
        color: {tokens.text_secondary};
        font-size: 13px;
        font-weight: 700;
    }}

    QFrame#MetricCard {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 16px;
    }}

    QLabel#MetricTitle {{
        color: {tokens.text_muted};
        font-size: 12px;
        font-weight: 700;
    }}

    QLabel#MetricDeltaChip {{
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 700;
    }}

    QLabel#MetricDeltaChip[trend="up"] {{
        color: {tokens.success};
        background-color: {success_soft};
        border: 1px solid {success_mid};
    }}

    QLabel#MetricDeltaChip[trend="flat"] {{
        color: {tokens.warning};
        background-color: {warning_soft};
        border: 1px solid {warning_mid};
    }}

    QLabel#MetricDeltaChip[trend="down"] {{
        color: {tokens.danger};
        background-color: {danger_soft};
        border: 1px solid {danger_mid};
    }}

    QLabel#MetricSubtitle {{
        color: {tokens.text_muted};
        font-size: 12px;
    }}

    QProgressBar#MetricProgress {{
        min-height: 8px;
        border-radius: 4px;
        border: 1px solid {border_soft};
        background-color: {surface_glass};
    }}

    QProgressBar#MetricProgress::chunk {{
        border-radius: 3px;
        margin: 1px;
        background-color: {tokens.accent};
    }}

    QFrame#InsightBanner {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 16px;
    }}

    QLabel#InsightBannerIcon {{
        min-width: 34px;
        max-width: 34px;
        min-height: 34px;
        max-height: 34px;
        border-radius: 17px;
        color: {tokens.text_primary};
        background-color: {accent_soft};
        border: 1px solid {accent_mid};
        font-size: 15px;
        font-weight: 700;
        qproperty-alignment: AlignCenter;
    }}

    QLabel#InsightBannerTitle {{
        color: {tokens.text_primary};
        font-size: 15px;
        font-weight: 700;
    }}

    QLabel#InsightBannerBody {{
        color: {tokens.text_muted};
        font-size: 13px;
    }}

    QWidget#SegmentedControl {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 12px;
    }}

    QPushButton[segment="true"] {{
        min-height: 32px;
        padding: 0 12px;
        border-radius: 9px;
        border: 1px solid transparent;
        background-color: transparent;
        color: {tokens.text_secondary};
        font-size: 13px;
        font-weight: 600;
    }}

    QPushButton[segment="true"]:hover {{
        background-color: {surface_glass};
    }}

    QPushButton[segment="true"][active="true"] {{
        background-color: {accent_soft};
        border-color: {accent_mid};
        color: {tokens.text_primary};
        font-weight: 700;
    }}

    QLabel#StatusLozenge {{
        min-height: 22px;
        padding: 0 10px;
        border-radius: 11px;
        border: 1px solid {border_soft};
        background-color: {surface_glass};
        color: {tokens.text_secondary};
        font-size: 12px;
        font-weight: 700;
    }}

    QLabel#StatusLozenge[tone="success"] {{
        color: {tokens.success};
        background-color: {success_soft};
        border: 1px solid {success_mid};
    }}

    QLabel#StatusLozenge[tone="warning"] {{
        color: {tokens.warning};
        background-color: {warning_soft};
        border: 1px solid {warning_mid};
    }}

    QLabel#StatusLozenge[tone="danger"] {{
        color: {tokens.danger};
        background-color: {danger_soft};
        border: 1px solid {danger_mid};
    }}

    QLabel#StatusLozenge[tone="info"] {{
        color: {tokens.accent};
        background-color: {accent_soft};
        border: 1px solid {accent_mid};
    }}

    QWidget#ChipFilterBar {{
        background: transparent;
    }}

    QPushButton[filterChip="true"] {{
        min-height: 30px;
        padding: 0 11px;
        border-radius: 10px;
        border: 1px solid {border_soft};
        background-color: {surface_alt_glass};
        color: {tokens.text_secondary};
        font-size: 12px;
        font-weight: 600;
    }}

    QPushButton[filterChip="true"]:hover {{
        border-color: {accent_mid};
        background-color: {surface_glass};
        color: {tokens.text_primary};
    }}

    QPushButton[filterChip="true"][selected="true"] {{
        background-color: {accent_soft};
        border-color: {accent_mid};
        color: {tokens.text_primary};
        font-weight: 700;
    }}

    QFrame#KpiStrip {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 14px;
    }}

    QFrame#KpiStripItem {{
        border: none;
        border-right: 1px solid {border_soft};
        background: transparent;
    }}

    QFrame#KpiStripItem[lastItem="true"] {{
        border-right: none;
    }}

    QLabel#KpiStripValue {{
        color: {tokens.text_primary};
        font-size: 20px;
        font-weight: 700;
    }}

    QLabel#KpiStripLabel {{
        color: {tokens.text_secondary};
        font-size: 12px;
        font-weight: 700;
    }}

    QLabel#KpiStripHint {{
        color: {tokens.text_muted};
        font-size: 11px;
    }}

    QFrame#StepProgress {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 14px;
    }}

    QFrame#StepNode {{
        background: transparent;
        border: none;
    }}

    QLabel#StepNodeBadge {{
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
        border-radius: 12px;
        border: 1px solid {border_soft};
        background-color: {surface_glass};
        color: {tokens.text_muted};
        font-size: 12px;
        font-weight: 700;
    }}

    QLabel#StepNodeBadge[state="current"] {{
        border-color: {accent_mid};
        background-color: {accent_soft};
        color: {tokens.accent};
    }}

    QLabel#StepNodeBadge[state="done"] {{
        border-color: {tokens.accent};
        background-color: {tokens.accent};
        color: {tokens.accent_contrast};
    }}

    QLabel#StepNodeText {{
        color: {tokens.text_muted};
        font-size: 12px;
        font-weight: 600;
    }}

    QLabel#StepNodeText[state="current"],
    QLabel#StepNodeText[state="done"] {{
        color: {tokens.text_primary};
    }}

    QLabel#StepNodeText[state="current"] {{
        font-weight: 700;
    }}

    QFrame#StepConnector {{
        border: none;
        border-radius: 1px;
        background-color: {border_soft};
    }}

    QFrame#StepConnector[state="done"] {{
        background-color: {tokens.accent};
    }}

    QFrame#TimelineFeed {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 14px;
    }}

    QLabel#TimelineFeedTitle {{
        color: {tokens.text_primary};
        font-size: 15px;
        font-weight: 700;
    }}

    QFrame#TimelineRow {{
        background: transparent;
        border: none;
    }}

    QLabel#TimelineDot {{
        min-width: 10px;
        max-width: 10px;
        min-height: 10px;
        max-height: 10px;
        border-radius: 5px;
        background-color: {tokens.text_muted};
    }}

    QLabel#TimelineDot[tone="success"] {{
        background-color: {tokens.success};
    }}

    QLabel#TimelineDot[tone="warning"] {{
        background-color: {tokens.warning};
    }}

    QLabel#TimelineDot[tone="danger"] {{
        background-color: {tokens.danger};
    }}

    QLabel#TimelineDot[tone="info"] {{
        background-color: {tokens.accent};
    }}

    QLabel#TimelineItemTitle {{
        color: {tokens.text_primary};
        font-size: 13px;
        font-weight: 600;
    }}

    QLabel#TimelineItemMeta {{
        color: {tokens.text_muted};
        font-size: 12px;
    }}

    QFrame#EmptyStateCard {{
        background-color: {surface_alt_glass};
        border: 1px dashed {border_soft};
        border-radius: 16px;
    }}

    QLabel#EmptyStateIcon {{
        min-width: 42px;
        max-width: 42px;
        min-height: 42px;
        max-height: 42px;
        border-radius: 21px;
        border: 1px solid {accent_mid};
        background-color: {accent_soft};
        color: {tokens.accent};
        font-size: 16px;
        font-weight: 700;
    }}

    QLabel#EmptyStateTitle {{
        color: {tokens.text_primary};
        font-size: 17px;
        font-weight: 700;
    }}

    QLabel#EmptyStateBody {{
        color: {tokens.text_muted};
        font-size: 13px;
    }}

    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QDateEdit,
    QTimeEdit,
    QDateTimeEdit,
    QTextEdit,
    QPlainTextEdit {{
        min-height: 38px;
        border: 1px solid {border_soft};
        border-radius: 12px;
        background-color: {surface_alt_glass};
        color: {tokens.text_primary};
    }}

    QLineEdit#GlobalSearch {{
        min-width: 280px;
        max-width: 420px;
        font-size: 13px;
    }}

    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QDateEdit,
    QTimeEdit,
    QDateTimeEdit {{
        padding: 6px 12px;
        padding-right: 34px;
    }}

    QTextEdit,
    QPlainTextEdit {{
        padding: 10px 12px;
    }}

    QLineEdit {{
        placeholder-text-color: {tokens.text_muted};
    }}

    QLineEdit:focus,
    QComboBox:focus,
    QSpinBox:focus,
    QDoubleSpinBox:focus,
    QDateEdit:focus,
    QTimeEdit:focus,
    QDateTimeEdit:focus,
    QTextEdit:focus,
    QPlainTextEdit:focus {{
        border-color: {tokens.accent};
        background-color: {surface_glass};
    }}

    QLineEdit:hover,
    QComboBox:hover,
    QSpinBox:hover,
    QDoubleSpinBox:hover,
    QDateEdit:hover,
    QTimeEdit:hover,
    QDateTimeEdit:hover,
    QTextEdit:hover,
    QPlainTextEdit:hover {{
        border-color: {tokens.accent_hover};
    }}

    QLineEdit:disabled,
    QComboBox:disabled,
    QSpinBox:disabled,
    QDoubleSpinBox:disabled,
    QDateEdit:disabled,
    QTimeEdit:disabled,
    QDateTimeEdit:disabled,
    QTextEdit:disabled,
    QPlainTextEdit:disabled {{
        color: {tokens.text_muted};
        background-color: {tokens.window};
        border-color: {border_soft};
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border: none;
        border-left: 1px solid {border_soft};
        border-top-right-radius: 12px;
        border-bottom-right-radius: 12px;
        background-color: {surface_glass};
    }}

    QComboBox::down-arrow {{
        image: url(resources/icons/heroicons/16-solid/chevron-down.svg);
        width: 10px;
        height: 10px;
    }}

    QComboBox QAbstractItemView {{
        border: 1px solid {border_soft};
        border-radius: 10px;
        padding: 6px;
        background-color: {surface_glass};
        color: {tokens.text_primary};
        selection-background-color: {tokens.selection_bg};
        selection-color: {tokens.text_primary};
    }}

    QSpinBox::up-arrow,
    QDoubleSpinBox::up-arrow,
    QTimeEdit::up-arrow {{
        image: url(resources/icons/heroicons/16-solid/chevron-up.svg);
        width: 10px;
        height: 10px;
    }}

    QSpinBox::down-arrow,
    QDoubleSpinBox::down-arrow,
    QTimeEdit::down-arrow {{
        image: url(resources/icons/heroicons/16-solid/chevron-down.svg);
        width: 10px;
        height: 10px;
    }}

    QSpinBox::up-button,
    QDoubleSpinBox::up-button,
    QTimeEdit::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 24px;
        border: none;
        border-left: 1px solid {border_soft};
        border-bottom: 1px solid {border_soft};
        border-top-right-radius: 12px;
        background-color: {surface_glass};
    }}

    QSpinBox::down-button,
    QDoubleSpinBox::down-button,
    QTimeEdit::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 24px;
        border: none;
        border-left: 1px solid {border_soft};
        border-bottom-right-radius: 12px;
        background-color: {surface_glass};
    }}

    QSpinBox::up-button:hover,
    QSpinBox::down-button:hover,
    QDoubleSpinBox::up-button:hover,
    QDoubleSpinBox::down-button:hover,
    QTimeEdit::up-button:hover,
    QTimeEdit::down-button:hover,
    QComboBox::drop-down:hover {{
        background-color: {surface_alt_glass};
    }}

    QDateEdit::up-button,
    QDateTimeEdit::up-button {{
        width: 0px;
        border: none;
        background: transparent;
    }}

    QDateEdit::up-arrow,
    QDateTimeEdit::up-arrow {{
        width: 0px;
        height: 0px;
        image: none;
    }}

    QDateEdit::down-button,
    QDateTimeEdit::down-button {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border: none;
        border-left: 1px solid {border_soft};
        border-top-right-radius: 12px;
        border-bottom-right-radius: 12px;
        background-color: {surface_glass};
    }}

    QDateEdit::down-arrow,
    QDateTimeEdit::down-arrow {{
        image: url(resources/icons/heroicons/16-solid/chevron-down.svg);
        width: 10px;
        height: 10px;
    }}

    QDateEdit::down-button:hover,
    QDateTimeEdit::down-button:hover {{
        background-color: {surface_alt_glass};
    }}

    QCheckBox,
    QRadioButton {{
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 5px;
        border: 1px solid {border_soft};
        background-color: {surface_glass};
    }}

    QCheckBox::indicator:hover {{
        border-color: {tokens.accent};
    }}

    QCheckBox::indicator:checked {{
        border-color: {tokens.accent};
        background-color: {tokens.accent};
        image: url(resources/icons/heroicons/16-solid/check.svg);
    }}

    QCheckBox::indicator:disabled {{
        border-color: {border_soft};
        background-color: {surface_alt_glass};
    }}

    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 1px solid {border_soft};
        background-color: {surface_glass};
    }}

    QRadioButton::indicator:hover {{
        border-color: {tokens.accent};
    }}

    QRadioButton::indicator:checked {{
        border: 5px solid {tokens.accent};
        background-color: {surface_glass};
    }}

    QProgressBar {{
        min-height: 12px;
        border-radius: 6px;
        border: 1px solid {border_soft};
        background-color: {surface_alt_glass};
        text-align: center;
        color: {tokens.text_secondary};
    }}

    QProgressBar::chunk {{
        border-radius: 5px;
        margin: 1px;
        background-color: {tokens.accent};
    }}

    QSlider::groove:horizontal {{
        height: 7px;
        border-radius: 3px;
        background-color: {tokens.border};
    }}

    QSlider::sub-page:horizontal {{
        border-radius: 3px;
        background-color: {tokens.accent};
    }}

    QSlider::add-page:horizontal {{
        border-radius: 3px;
        background-color: {surface_alt_glass};
    }}

    QSlider::handle:horizontal {{
        width: 20px;
        margin: -8px 0;
        border-radius: 10px;
        border: 2px solid {surface_glass};
        background-color: {tokens.accent};
    }}

    QSlider::handle:horizontal:hover {{
        background-color: {tokens.accent_hover};
    }}

    QPushButton[primary="true"],
    QToolButton[primary="true"] {{
        background-color: {tokens.accent};
        border-color: transparent;
        color: {tokens.accent_contrast};
        font-weight: 700;
    }}

    QPushButton[primary="true"]:hover,
    QToolButton[primary="true"]:hover {{
        background-color: {tokens.accent_hover};
        border-color: transparent;
    }}

    QPushButton[danger="true"] {{
        background-color: {tokens.danger};
        border-color: transparent;
        color: #FFFFFF;
        font-weight: 700;
    }}

    QListWidget,
    QTreeWidget,
    QTableWidget,
    QTableView {{
        background-color: {surface_glass};
        alternate-background-color: {tokens.table_alt};
        border: 1px solid {border_soft};
        border-radius: 12px;
        gridline-color: {tokens.border};
    }}

    QCalendarWidget {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 12px;
    }}

    QListWidget::item,
    QTreeView::item,
    QTableView::item,
    QTableWidget::item {{
        min-height: 30px;
        padding: 4px 7px;
    }}

    QListWidget::item:selected,
    QTreeView::item:selected,
    QTableView::item:selected,
    QTableWidget::item:selected {{
        background-color: {tokens.selection_bg};
        color: {tokens.text_primary};
        border-radius: 6px;
    }}

    QTableCornerButton::section {{
        border: 1px solid {border_soft};
        background-color: {surface_alt_glass};
    }}

    QHeaderView::section {{
        background-color: {surface_alt_glass};
        color: {tokens.text_secondary};
        border: none;
        border-right: 1px solid {border_soft};
        border-bottom: 1px solid {border_soft};
        padding: 10px 8px;
        font-weight: 600;
    }}

    QTabWidget::pane {{
        border: 1px solid {border_soft};
        border-radius: 12px;
        background-color: {surface_glass};
        top: -2px;
    }}

    QTabBar::tab {{
        min-height: 34px;
        padding: 0 14px;
        border: 1px solid {border_soft};
        border-bottom: 1px solid {border_soft};
        border-radius: 10px;
        background-color: {surface_alt_glass};
        color: {tokens.text_secondary};
        margin-right: 6px;
    }}

    QTabBar::tab:selected {{
        background-color: {accent_soft};
        border-color: {accent_mid};
        color: {tokens.text_primary};
        font-weight: 700;
    }}

    QTabBar::tab:hover:!selected {{
        background-color: {surface_glass};
    }}

    QToolBox::tab {{
        border: 1px solid {border_soft};
        border-radius: 10px;
        padding: 9px 12px;
        background-color: {surface_alt_glass};
        color: {tokens.text_secondary};
        font-weight: 600;
    }}

    QToolBox::tab:selected {{
        border-color: {accent_mid};
        background-color: {accent_soft};
        color: {tokens.text_primary};
    }}

    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        border: none;
        border-bottom: 1px solid {border_soft};
        background-color: {surface_alt_glass};
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
    }}

    QCalendarWidget QToolButton {{
        min-height: 32px;
        min-width: 32px;
        border-radius: 10px;
        background-color: transparent;
        border: none;
        color: {tokens.text_primary};
    }}

    QCalendarWidget QToolButton:hover {{
        background-color: {surface_glass};
    }}

    QCalendarWidget QSpinBox {{
        min-height: 30px;
        border-radius: 10px;
        border: 1px solid {border_soft};
        background-color: {surface_glass};
    }}

    QLCDNumber {{
        border: 1px solid {border_soft};
        border-radius: 10px;
        background-color: {surface_glass};
        color: {tokens.accent};
    }}

    QCalendarWidget QAbstractItemView:enabled {{
        color: {tokens.text_primary};
        background-color: {surface_glass};
        selection-background-color: {tokens.selection_bg};
        selection-color: {tokens.text_primary};
    }}

    QScrollArea {{
        border: none;
        background: transparent;
    }}

    QScrollBar:vertical {{
        width: 10px;
        border: none;
        margin: 2px;
        background-color: {surface_alt_glass};
        border-radius: 5px;
    }}

    QScrollBar:horizontal {{
        height: 10px;
        border: none;
        margin: 2px;
        background-color: {surface_alt_glass};
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical,
    QScrollBar::handle:horizontal {{
        border-radius: 4px;
        min-height: 30px;
        min-width: 30px;
        background-color: {tokens.border};
    }}

    QScrollBar::handle:vertical:hover,
    QScrollBar::handle:horizontal:hover {{
        background-color: {tokens.text_muted};
    }}

    QScrollBar::add-line,
    QScrollBar::sub-line,
    QScrollBar::add-page,
    QScrollBar::sub-page {{
        border: none;
        background: transparent;
        width: 0px;
        height: 0px;
    }}

    QWidget#FlutterReferenceCanvas {{
        background: transparent;
    }}

    QFrame#FlutterBoard {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 28px;
    }}

    QFrame#FlutterNoteRail {{
        background-color: {sidebar_glass};
        border: none;
        border-right: 1px solid {border_soft};
        border-top-left-radius: 28px;
        border-bottom-left-radius: 28px;
    }}

    QFrame#FlutterNoteBody {{
        background-color: {surface_glass};
        border: none;
        border-top-right-radius: 28px;
        border-bottom-right-radius: 28px;
    }}

    QScrollArea#FlutterBodyScroll {{
        border: none;
        background: transparent;
    }}

    QFrame#FlutterSectionCard {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 16px;
    }}

    QLabel#FlutterSectionTitle {{
        color: {tokens.text_primary};
        font-size: 17px;
        font-weight: 700;
    }}

    QToolButton#FlutterMenuButton {{
        min-width: 34px;
        min-height: 34px;
        border-radius: 17px;
        border: 1px solid transparent;
        background: transparent;
        color: {tokens.accent};
        padding: 0;
    }}

    QToolButton#FlutterMenuButton:hover {{
        background-color: {accent_soft};
        border-color: {accent_mid};
    }}

    QLabel#FlutterAvatar {{
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        border-radius: 20px;
        border: 1px solid {accent_mid};
        background-color: {accent_soft};
        color: {tokens.text_primary};
        font-size: 12px;
        font-weight: 700;
    }}

    QToolButton#FlutterToolbarButton {{
        min-width: 36px;
        min-height: 36px;
        border: 1px solid transparent;
        border-radius: 12px;
        background: transparent;
        color: {tokens.accent};
        padding: 0;
        font-size: 16px;
        font-weight: 700;
    }}

    QToolButton#FlutterToolbarButton[glyph="true"] {{
        font-size: 24px;
        font-weight: 700;
    }}

    QToolButton#FlutterToolbarButton:hover {{
        background-color: {accent_soft};
        border-color: {accent_mid};
    }}

    QToolButton#FlutterToolbarButton[selected="true"] {{
        background-color: {tokens.accent};
        color: {tokens.accent_contrast};
    }}

    QLabel#FlutterTaskTitle {{
        color: {tokens.text_primary};
        font-size: 32px;
        font-weight: 800;
        padding: 2px 0 2px 0;
    }}

    QLabel#FlutterBodySubtitle {{
        color: {tokens.text_muted};
        font-size: 13px;
        font-weight: 500;
        padding-bottom: 4px;
    }}

    QCheckBox[taskCheck="true"] {{
        color: {tokens.text_primary};
        font-size: 16px;
        font-weight: 500;
        spacing: 14px;
    }}

    QCheckBox[taskCheck="true"]::indicator {{
        width: 22px;
        height: 22px;
        border-radius: 6px;
        border: 2px solid {tokens.accent};
        background-color: {surface_glass};
    }}

    QCheckBox[taskCheck="true"]::indicator:checked {{
        border-color: {tokens.accent};
        background-color: {tokens.accent};
        image: url(resources/icons/heroicons/24-solid/check.svg);
    }}

    QToolButton#FlutterActionButton {{
        min-width: 52px;
        max-width: 52px;
        min-height: 52px;
        max-height: 52px;
        border: 1px solid transparent;
        border-radius: 26px;
        background-color: {tokens.accent};
        color: {tokens.accent_contrast};
        padding: 0;
    }}

    QToolButton#FlutterActionButton:hover {{
        background-color: {tokens.accent_hover};
    }}

    QToolButton#FlutterActionButton:pressed {{
        background-color: {tokens.accent_pressed};
    }}

    QFrame#FlutterDotTopRight,
    QFrame#FlutterDotLeftMid,
    QFrame#FlutterDotRightMid,
    QFrame#FlutterDotBottomLeft,
    QFrame#FlutterDotBottomCenter {{
        border: 1px solid transparent;
        border-radius: 999px;
        background-color: {accent_mid};
    }}

    QToolTip {{
        background-color: {surface_glass};
        color: {tokens.text_primary};
        border: 1px solid {border_soft};
        border-radius: 10px;
        padding: 8px 10px;
    }}
    """
