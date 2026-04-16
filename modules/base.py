from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PyQt6.QtWidgets import QWidget

from core.app_context import AppContext


PageFactory = Callable[[AppContext], QWidget]


@dataclass(frozen=True, slots=True)
class ModuleSpec:
    key: str
    title: str
    icon_name: str
    page_factory: PageFactory
    lazy: bool = True
