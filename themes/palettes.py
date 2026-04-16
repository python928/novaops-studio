from __future__ import annotations

from PyQt6.QtGui import QColor, QPalette

from themes.tokens import ThemeTokens


def build_palette(tokens: ThemeTokens) -> QPalette:
    palette = QPalette()

    window = QColor(tokens.window)
    surface = QColor(tokens.surface)
    surface_alt = QColor(tokens.surface_alt)
    text = QColor(tokens.text_primary)
    text_muted = QColor(tokens.text_muted)
    accent = QColor(tokens.accent)
    selection = QColor(tokens.selection_bg)
    accent_contrast = QColor(tokens.accent_contrast)

    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, surface)
    palette.setColor(QPalette.ColorRole.AlternateBase, surface_alt)
    palette.setColor(QPalette.ColorRole.ToolTipBase, surface)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, surface)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.BrightText, accent_contrast)
    palette.setColor(QPalette.ColorRole.Highlight, selection)
    palette.setColor(QPalette.ColorRole.HighlightedText, text)
    palette.setColor(QPalette.ColorRole.Link, accent)

    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, text_muted)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, text_muted)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, text_muted)

    accent_role = getattr(QPalette.ColorRole, "Accent", None)
    if accent_role is not None:
        palette.setColor(accent_role, accent)

    return palette
