from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.event_bus import AppEventBus
from core.settings import SettingsStore

if TYPE_CHECKING:
    from themes.manager import ThemeManager


@dataclass(slots=True)
class AppContext:
    settings: SettingsStore
    events: AppEventBus
    theme: "ThemeManager"
