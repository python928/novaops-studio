from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
import tempfile

from PyQt6.QtGui import QIcon, QPalette
from PyQt6.QtWidgets import QApplication, QStyle


_ICON_DIR = Path(__file__).resolve().parent.parent / "resources" / "icons"
_THEME_ICON_DIR = Path(tempfile.gettempdir()) / "mystock-icons"

_DARK_MODE_ICON_COLOR = "#BAC8DE"
_LIGHT_MODE_ICON_COLOR = "#3D4E68"

_BLACK_LIKE_COLOR = re.compile(r"(?i)#0f172a|#111827|#000000|#000\b|black\b")


def _resolve_icon_path(name: str) -> Path | None:
    svg = _ICON_DIR / f"{name}.svg"
    if svg.exists():
        return svg

    png = _ICON_DIR / f"{name}.png"
    if png.exists():
        return png

    return None


def _is_dark_theme(app: QApplication) -> bool:
    bg = app.palette().color(QPalette.ColorRole.Window)
    luma = (0.299 * bg.red()) + (0.587 * bg.green()) + (0.114 * bg.blue())
    return luma < 140.0


def _icon_tint_hex() -> str:
    app = QApplication.instance()
    if app is None:
        return _LIGHT_MODE_ICON_COLOR
    return _DARK_MODE_ICON_COLOR if _is_dark_theme(app) else _LIGHT_MODE_ICON_COLOR


def _colorize_svg(svg_text: str, color_hex: str) -> str:
    colored = _BLACK_LIKE_COLOR.sub("currentColor", svg_text)

    if " color=" in colored:
        colored = re.sub(r'\scolor="[^"]*"', f' color="{color_hex}"', colored, count=1)
    elif "<svg" in colored:
        colored = colored.replace("<svg", f'<svg color="{color_hex}"', 1)

    return colored


def _themed_svg_path(source: Path, tint_hex: str) -> Path:
    relative = source.relative_to(_ICON_DIR)
    target = _THEME_ICON_DIR / tint_hex.lstrip("#") / relative
    target.parent.mkdir(parents=True, exist_ok=True)

    original = source.read_text(encoding="utf-8")
    colored = _colorize_svg(original, tint_hex)

    if not target.exists() or target.read_text(encoding="utf-8") != colored:
        target.write_text(colored, encoding="utf-8")

    return target


@lru_cache(maxsize=512)
def _icon_for_tint(name: str, tint_hex: str) -> QIcon:
    path = _resolve_icon_path(name)
    if path is None:
        return QIcon()

    if path.suffix.casefold() == ".svg":
        try:
            themed_path = _themed_svg_path(path, tint_hex)
            return QIcon(str(themed_path))
        except OSError:
            return QIcon(str(path))

    return QIcon(str(path))


def clear_icon_cache() -> None:
    _icon_for_tint.cache_clear()
    icon.cache_clear()


@lru_cache(maxsize=256)
def icon(name: str) -> QIcon:
    return _icon_for_tint(name, _icon_tint_hex())


@lru_cache(maxsize=64)
def standard_icon(pixmap: QStyle.StandardPixmap) -> QIcon:
    app = QApplication.instance()
    if app is None:
        return QIcon()
    return app.style().standardIcon(pixmap)
