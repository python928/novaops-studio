from __future__ import annotations

import tempfile
from pathlib import Path

from PyQt6.QtGui import QColor

from themes.tokens import ThemeTokens


_CHEVRON_DOWN_PATH = (
    "M4.21967 6.21967C4.51256 5.92678 4.98744 5.92678 5.28033 6.21967"
    "L8 8.93934L10.7197 6.21967C11.0126 5.92678 11.4874 5.92678 11.7803 6.21967"
    "C12.0732 6.51256 12.0732 6.98744 11.7803 7.28033L8.53033 10.5303"
    "C8.23744 10.8232 7.76256 10.8232 7.46967 10.5303L4.21967 7.28033"
    "C3.92678 6.98744 3.92678 6.51256 4.21967 6.21967Z"
)
_CHEVRON_UP_PATH = (
    "M11.7803 9.78033C11.4874 10.0732 11.0126 10.0732 10.7197 9.78033"
    "L8 7.06066L5.28033 9.78033C4.98744 10.0732 4.51256 10.0732 4.21967 9.78033"
    "C3.92678 9.48744 3.92678 9.01256 4.21967 8.71967L7.46967 5.46967"
    "C7.76256 5.17678 8.23744 5.17678 8.53033 5.46967L11.7803 8.71967"
    "C12.0732 9.01256 12.0732 9.48744 11.7803 9.78033Z"
)
_CHEVRON_LEFT_PATH = (
    "M9.78033 4.21967C10.0732 4.51256 10.0732 4.98744 9.78033 5.28033"
    "L7.06066 8L9.78033 10.7197C10.0732 11.0126 10.0732 11.4874 9.78033 11.7803"
    "C9.48744 12.0732 9.01256 12.0732 8.71967 11.7803L5.46967 8.53033"
    "C5.17678 8.23744 5.17678 7.76256 5.46967 7.46967L8.71967 4.21967"
    "C9.01256 3.92678 9.48744 3.92678 9.78033 4.21967Z"
)
_CHEVRON_RIGHT_PATH = (
    "M6.21967 4.21967C6.51256 3.92678 6.98744 3.92678 7.28033 4.21967"
    "L10.5303 7.46967C10.8232 7.76256 10.8232 8.23744 10.5303 8.53033"
    "L7.28033 11.7803C6.98744 12.0732 6.51256 12.0732 6.21967 11.7803"
    "C5.92678 11.4874 5.92678 11.0126 6.21967 10.7197L8.93934 8"
    "L6.21967 5.28033C5.92678 4.98744 5.92678 4.51256 6.21967 4.21967Z"
)


def _to_hex(color: str, fallback: str) -> str:
    qcolor = QColor(color)
    if not qcolor.isValid():
        qcolor = QColor(fallback)
    return qcolor.name().upper()


def _svg_path_icon(path_data: str, color_hex: str) -> str:
    return (
        '<svg width="16" height="16" viewBox="0 0 16 16" '
        'fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<path fill-rule="evenodd" clip-rule="evenodd" d="{path_data}" fill="{color_hex}"/>'
        "</svg>"
    )


def _build_theme_icon_paths(tokens: ThemeTokens) -> dict[str, str]:
    fallback = {
        "chevron_down": "resources/icons/heroicons/16-solid/chevron-down.svg",
        "chevron_up": "resources/icons/heroicons/16-solid/chevron-up.svg",
        "chevron_left": "resources/icons/tabler/chevron-left.svg",
        "chevron_right": "resources/icons/lucide/chevron-right.svg",
        "chevron_down_muted": "resources/icons/heroicons/16-solid/chevron-down.svg",
        "chevron_up_muted": "resources/icons/heroicons/16-solid/chevron-up.svg",
        "chevron_left_muted": "resources/icons/tabler/chevron-left.svg",
        "chevron_right_muted": "resources/icons/lucide/chevron-right.svg",
    }

    text_secondary = _to_hex(tokens.text_secondary, "#5B6D88")
    text_muted = _to_hex(tokens.text_muted, "#8A9BB7")

    key = "-".join(
        (
            text_secondary.lstrip("#"),
            text_muted.lstrip("#"),
        )
    )

    out_dir = Path(tempfile.gettempdir()) / "mystock-theme-icons" / key
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return fallback

    definitions = {
        "chevron_down": (_CHEVRON_DOWN_PATH, text_secondary),
        "chevron_up": (_CHEVRON_UP_PATH, text_secondary),
        "chevron_left": (_CHEVRON_LEFT_PATH, text_secondary),
        "chevron_right": (_CHEVRON_RIGHT_PATH, text_secondary),
        "chevron_down_muted": (_CHEVRON_DOWN_PATH, text_muted),
        "chevron_up_muted": (_CHEVRON_UP_PATH, text_muted),
        "chevron_left_muted": (_CHEVRON_LEFT_PATH, text_muted),
        "chevron_right_muted": (_CHEVRON_RIGHT_PATH, text_muted),
    }

    paths = fallback.copy()
    for name, (path_data, color_hex) in definitions.items():
        target = out_dir / f"{name}.svg"
        svg_content = _svg_path_icon(path_data, color_hex)
        try:
            needs_write = True
            if target.exists():
                try:
                    needs_write = target.read_text(encoding="utf-8") != svg_content
                except OSError:
                    needs_write = False
            if needs_write:
                target.write_text(svg_content, encoding="utf-8")
            paths[name] = target.as_posix()
        except OSError:
            continue

    return paths


def _rgba(color: str, alpha: int) -> str:
    qcolor = QColor(color)
    clamped = max(0, min(alpha, 255))
    return f"rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {clamped})"


def build_stylesheet(tokens: ThemeTokens) -> str:
    surface_glass = _rgba(tokens.surface, 232)
    surface_alt_glass = _rgba(tokens.surface_alt, 220)
    sidebar_glass = _rgba(tokens.sidebar, 236)
    border_soft = _rgba(tokens.border, 182)
    border_strong = _rgba(tokens.border, 230)
    accent_soft = _rgba(tokens.accent, 48)
    accent_mid = _rgba(tokens.accent, 94)
    accent_focus = _rgba(tokens.accent, 132)
    success_soft = _rgba(tokens.success, 45)
    success_mid = _rgba(tokens.success, 120)
    warning_soft = _rgba(tokens.warning, 45)
    warning_mid = _rgba(tokens.warning, 120)
    danger_soft = _rgba(tokens.danger, 45)
    danger_mid = _rgba(tokens.danger, 120)

    icons = _build_theme_icon_paths(tokens)
    chevron_down_icon = icons["chevron_down"]
    chevron_up_icon = icons["chevron_up"]
    chevron_left_icon = icons["chevron_left"]
    chevron_right_icon = icons["chevron_right"]
    chevron_down_muted_icon = icons["chevron_down_muted"]
    chevron_up_muted_icon = icons["chevron_up_muted"]
    chevron_left_muted_icon = icons["chevron_left_muted"]
    chevron_right_muted_icon = icons["chevron_right_muted"]

    return f"""
    QWidget {{
        color: {tokens.text_primary};
        font-family: "IBM Plex Sans", "Manrope", "Inter", "Segoe UI", "Noto Sans", sans-serif;
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
        min-height: 40px;
        padding: 7px 14px;
        border-radius: 14px;
        border: 1px solid {border_soft};
        background-color: {surface_alt_glass};
        color: {tokens.text_primary};
        font-weight: 600;
        font-size: 13px;
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

    QPushButton:focus,
    QToolButton:focus {{
        border-color: {accent_focus};
        background-color: {surface_glass};
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

    QPushButton[subtle="true"],
    QToolButton[subtle="true"] {{
        background-color: transparent;
        border-color: transparent;
        color: {tokens.text_secondary};
    }}

    QPushButton[subtle="true"]:hover,
    QToolButton[subtle="true"]:hover {{
        background-color: {surface_alt_glass};
        border-color: {border_soft};
        color: {tokens.text_primary};
    }}

    QToolButton[iconOnly="true"] {{
        min-width: 38px;
        max-width: 38px;
        min-height: 38px;
        max-height: 38px;
        padding: 0;
        border-radius: 12px;
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
    QDateTimeEdit {{
        min-height: 40px;
        max-height: 40px;
        border: 1px solid {border_soft};
        border-radius: 14px;
        background-color: {surface_alt_glass};
        color: {tokens.text_primary};
    }}

    QTextEdit,
    QPlainTextEdit {{
        min-height: 40px;
        border: 1px solid {border_soft};
        border-radius: 14px;
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
        padding-left: 12px;
        padding-right: 34px;
    }}

    QComboBox:rtl,
    QDateEdit:rtl,
    QTimeEdit:rtl,
    QDateTimeEdit:rtl,
    QSpinBox:rtl,
    QDoubleSpinBox:rtl {{
        padding-left: 34px;
        padding-right: 12px;
    }}

    QTextEdit,
    QPlainTextEdit {{
        padding: 10px 12px;
    }}

    QLineEdit {{
        placeholder-text-color: {tokens.text_muted};
    }}

    QLineEdit::clear-button,
    QComboBox QLineEdit::clear-button {{
        image: none;
        width: 0px;
        height: 0px;
        margin: 0;
        padding: 0;
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
        border-color: {accent_focus};
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
        subcontrol-position: center right;
        width: 18px;
        border: none;
        border-radius: 0;
        margin: 0 8px 0 0;
        background: transparent;
    }}

    QComboBox:rtl::drop-down {{
        margin: 0 0 0 8px;
    }}

    QComboBox::drop-down:hover,
    QComboBox::drop-down:on {{
        background: transparent;
    }}

    QComboBox:on {{
        border-color: {accent_focus};
        background-color: {surface_glass};
    }}

    QComboBox::down-arrow {{
        image: url({chevron_down_icon});
        width: 12px;
        height: 12px;
    }}

    QComboBox::down-arrow:disabled {{
        image: url({chevron_down_muted_icon});
    }}

    QComboBox QLineEdit {{
        border: none;
        background: transparent;
        padding: 0;
        margin: 0;
        min-height: 0;
        color: {tokens.text_primary};
        selection-background-color: {tokens.selection_bg};
        selection-color: {tokens.text_primary};
    }}

    QComboBox QLineEdit:focus {{
        border: none;
        background: transparent;
    }}

    QComboBox QAbstractItemView,
    QFrame#QComboBoxPrivateContainer QAbstractItemView,
    QAbstractItemView#ComboPopupView {{
        border: 1px solid {border_soft};
        border-radius: 16px;
        padding: 6px;
        background-color: {surface_glass};
        color: {tokens.text_primary};
        selection-background-color: {tokens.selection_bg};
        selection-color: {tokens.text_primary};
        outline: 0;
    }}

    QComboBox QAbstractItemView::item,
    QFrame#QComboBoxPrivateContainer QAbstractItemView::item,
    QAbstractItemView#ComboPopupView::item {{
        min-height: 30px;
        height: 30px;
        padding: 5px 8px;
        border-radius: 8px;
        margin: 0;
        border: 1px solid transparent;
    }}

    QComboBox QAbstractItemView::item:hover,
    QFrame#QComboBoxPrivateContainer QAbstractItemView::item:hover,
    QAbstractItemView#ComboPopupView::item:hover {{
        background-color: {surface_alt_glass};
    }}

    QComboBox QAbstractItemView::item:selected,
    QFrame#QComboBoxPrivateContainer QAbstractItemView::item:selected,
    QAbstractItemView#ComboPopupView::item:selected {{
        background-color: {tokens.selection_bg};
        color: {tokens.text_primary};
        border: 1px solid transparent;
        font-weight: 600;
    }}

    QAbstractSpinBox::up-arrow {{
        image: url({chevron_up_icon});
        width: 12px;
        height: 12px;
    }}

    QAbstractSpinBox::down-arrow {{
        image: url({chevron_down_icon});
        width: 12px;
        height: 12px;
    }}

    QAbstractSpinBox::up-arrow:disabled {{
        image: url({chevron_up_muted_icon});
    }}

    QAbstractSpinBox::down-arrow:disabled {{
        image: url({chevron_down_muted_icon});
    }}

    QAbstractSpinBox::up-button {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 16px;
        border: none;
        border-radius: 0;
        margin: 0 8px 0 0;
        background: transparent;
    }}

    QAbstractSpinBox:rtl::up-button {{
        margin: 0 0 0 8px;
    }}

    QAbstractSpinBox::down-button {{
        subcontrol-origin: padding;
        subcontrol-position: bottom right;
        width: 16px;
        border: none;
        border-radius: 0;
        margin: 0 8px 0 0;
        background: transparent;
    }}

    QAbstractSpinBox:rtl::down-button {{
        margin: 0 0 0 8px;
    }}

    QAbstractSpinBox::up-button:hover,
    QAbstractSpinBox::down-button:hover,
    QComboBox::drop-down:hover {{
        background: transparent;
    }}

    QDateEdit::up-button,
    QDateTimeEdit::up-button,
    QDateEdit::down-button,
    QDateTimeEdit::down-button {{
        width: 0px;
        border: none;
        background: transparent;
    }}

    QDateEdit::drop-down,
    QDateTimeEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 18px;
        border: none;
        border-radius: 0;
        margin: 0 8px 0 0;
        background: transparent;
    }}

    QDateEdit:rtl::drop-down,
    QDateTimeEdit:rtl::drop-down {{
        margin: 0 0 0 8px;
    }}

    QDateEdit::up-arrow,
    QDateTimeEdit::up-arrow {{
        width: 0px;
        height: 0px;
        image: none;
    }}

    QDateEdit::down-arrow,
    QDateTimeEdit::down-arrow {{
        image: url({chevron_down_icon});
        width: 12px;
        height: 12px;
    }}

    QDateEdit::down-arrow:disabled,
    QDateTimeEdit::down-arrow:disabled {{
        image: url({chevron_down_muted_icon});
    }}

    QDateEdit::down-button:hover,
    QDateTimeEdit::down-button:hover {{
        background: transparent;
    }}

    QCheckBox,
    QRadioButton {{
        spacing: 8px;
        color: {tokens.text_primary};
        font-size: 13px;
        font-weight: 500;
    }}

    QCheckBox[optionChip="true"],
    QRadioButton[optionChip="true"] {{
        min-height: 30px;
        padding: 4px 10px;
        border: 1px solid transparent;
        border-radius: 10px;
        background: transparent;
        spacing: 7px;
        color: {tokens.text_secondary};
    }}

    QCheckBox[optionChip="true"]:hover,
    QRadioButton[optionChip="true"]:hover {{
        border-color: {accent_mid};
        background-color: {accent_soft};
        color: {tokens.text_primary};
    }}

    QCheckBox[optionChip="true"]:checked,
    QRadioButton[optionChip="true"]:checked {{
        border-color: {accent_mid};
        background-color: {accent_soft};
        color: {tokens.text_primary};
        font-weight: 600;
    }}

    QCheckBox[optionChip="true"]::indicator,
    QRadioButton[optionChip="true"]::indicator {{
        width: 18px;
        height: 18px;
    }}

    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border-radius: 6px;
        border: 1px solid {border_strong};
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

    QCheckBox::indicator:indeterminate {{
        border-color: {accent_mid};
        background-color: {accent_soft};
        image: url(resources/icons/heroicons/16-solid/minus.svg);
    }}

    QCheckBox::indicator:disabled {{
        border-color: {border_soft};
        background-color: {surface_alt_glass};
    }}

    QRadioButton::indicator {{
        width: 20px;
        height: 20px;
        border-radius: 10px;
        border: 1px solid {border_strong};
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
        border-radius: 16px;
        gridline-color: {tokens.border};
    }}

    QCalendarWidget {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 16px;
    }}

    QMenu {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 16px;
        padding: 6px;
        color: {tokens.text_primary};
    }}

    QMenu::item {{
        min-height: 30px;
        padding: 5px 8px;
        border-radius: 8px;
        margin: 0;
    }}

    QMenu::item:selected {{
        background-color: {tokens.selection_bg};
        color: {tokens.text_primary};
    }}

    QMenu::separator {{
        height: 1px;
        background: {border_soft};
        margin: 5px 8px;
    }}

    QListWidget::item,
    QTreeView::item,
    QTableView::item,
    QTableWidget::item {{
        min-height: 30px;
        padding: 5px 8px;
    }}

    QListWidget::item:hover,
    QTreeView::item:hover,
    QTableView::item:hover,
    QTableWidget::item:hover {{
        background-color: {surface_alt_glass};
        border-radius: 8px;
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
        padding: 11px 8px;
        text-align: center;
        font-weight: 600;
    }}

    QHeaderView::section:hover {{
        background-color: {surface_glass};
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
        border-top-left-radius: 16px;
        border-top-right-radius: 16px;
    }}

    QCalendarWidget QToolButton {{
        min-height: 32px;
        min-width: 32px;
        border-radius: 10px;
        background-color: transparent;
        border: none;
        color: {tokens.text_secondary};
        qproperty-iconSize: 16px 16px;
    }}

    QCalendarWidget QToolButton#qt_calendar_prevmonth,
    QCalendarWidget QToolButton#qt_calendar_nextmonth {{
        min-width: 28px;
        max-width: 28px;
        padding: 0;
    }}

    QCalendarWidget QToolButton#qt_calendar_prevmonth {{
        qproperty-icon: url({chevron_left_icon});
    }}

    QCalendarWidget QToolButton#qt_calendar_nextmonth {{
        qproperty-icon: url({chevron_right_icon});
    }}

    QCalendarWidget QToolButton#qt_calendar_prevmonth:disabled {{
        qproperty-icon: url({chevron_left_muted_icon});
    }}

    QCalendarWidget QToolButton#qt_calendar_nextmonth:disabled {{
        qproperty-icon: url({chevron_right_muted_icon});
    }}

    QCalendarWidget QToolButton#qt_calendar_monthbutton,
    QCalendarWidget QToolButton#qt_calendar_yearbutton {{
        min-width: 72px;
        padding: 0 8px;
        color: {tokens.text_primary};
        font-weight: 700;
    }}

    QCalendarWidget QToolButton#qt_calendar_monthbutton::menu-indicator,
    QCalendarWidget QToolButton#qt_calendar_yearbutton::menu-indicator {{
        image: url({chevron_down_icon});
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 12px;
        height: 12px;
        right: 4px;
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

    QCalendarWidget QTableView {{
        border: none;
        outline: 0;
        background-color: {surface_glass};
        alternate-background-color: {surface_alt_glass};
        color: {tokens.text_primary};
        selection-background-color: {tokens.selection_bg};
        selection-color: {tokens.text_primary};
    }}

    QCalendarWidget QTableView::item {{
        border-radius: 8px;
        padding: 4px 6px;
    }}

    QCalendarWidget QTableView::item:hover {{
        background-color: {surface_alt_glass};
        color: {tokens.text_primary};
    }}

    QCalendarWidget QTableView::item:selected {{
        background-color: {tokens.selection_bg};
        color: {tokens.text_primary};
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

    QFrame#FlutterSectionCard,
    QFrame#ShowcaseSectionCard {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 16px;
    }}

    QLabel#FlutterSectionTitle,
    QLabel#ShowcaseSectionTitle {{
        color: {tokens.text_primary};
        font-size: 17px;
        font-weight: 700;
    }}

    QLabel#ShowcaseHeaderTitle {{
        color: {tokens.text_primary};
        font-size: 26px;
        font-weight: 800;
    }}

    QLabel#ShowcaseHeaderSubtitle {{
        color: {tokens.text_muted};
        font-size: 13px;
        font-weight: 500;
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

    QFrame#CommandDeck {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 22px;
    }}

    QLabel#CommandDeckBadge {{
        min-width: 38px;
        max-width: 38px;
        min-height: 38px;
        max-height: 38px;
        border-radius: 19px;
        border: 1px solid {accent_mid};
        background-color: {accent_soft};
        color: {tokens.accent};
        font-size: 12px;
        font-weight: 800;
    }}

    QLabel#CommandDeckTitle {{
        color: {tokens.text_primary};
        font-size: 26px;
        font-weight: 800;
    }}

    QLabel#CommandDeckBody {{
        color: {tokens.text_secondary};
        font-size: 13px;
    }}

    QLineEdit#CommandDeckSearch {{
        min-height: 44px;
        background-color: {surface_alt_glass};
    }}

    QPushButton[commandChip="true"] {{
        min-height: 32px;
        padding: 0 12px;
        border-radius: 16px;
        font-weight: 600;
    }}

    QFrame#ActionTile {{
        background-color: {surface_alt_glass};
        border: 1px solid {border_soft};
        border-radius: 18px;
    }}

    QFrame#ActionTile:hover {{
        border-color: {accent_mid};
        background-color: {surface_glass};
    }}

    QLabel#ActionTileBadge {{
        min-width: 32px;
        max-width: 32px;
        min-height: 32px;
        max-height: 32px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 800;
    }}

    QLabel#ActionTileBadge[tone="success"] {{
        color: {tokens.success};
        background-color: {success_soft};
        border: 1px solid {success_mid};
    }}

    QLabel#ActionTileBadge[tone="warning"] {{
        color: {tokens.warning};
        background-color: {warning_soft};
        border: 1px solid {warning_mid};
    }}

    QLabel#ActionTileBadge[tone="danger"] {{
        color: {tokens.danger};
        background-color: {danger_soft};
        border: 1px solid {danger_mid};
    }}

    QLabel#ActionTileBadge[tone="info"] {{
        color: {tokens.accent};
        background-color: {accent_soft};
        border: 1px solid {accent_mid};
    }}

    QLabel#ActionTileMeta {{
        background-color: {surface_glass};
        border: 1px solid {border_soft};
        border-radius: 11px;
        padding: 2px 9px;
        color: {tokens.text_secondary};
        font-size: 11px;
        font-weight: 700;
    }}

    QLabel#ActionTileTitle {{
        color: {tokens.text_primary};
        font-size: 16px;
        font-weight: 700;
    }}

    QLabel#ActionTileBody {{
        color: {tokens.text_muted};
        font-size: 13px;
    }}

    QToolButton#ActionTileChevron {{
        font-size: 15px;
        font-weight: 800;
        color: {tokens.text_secondary};
    }}

    QToolTip {{
        background-color: {surface_glass};
        color: {tokens.text_primary};
        border: 1px solid {border_soft};
        border-radius: 10px;
        padding: 8px 10px;
    }}
    """
