from __future__ import annotations

from core.app_context import AppContext
from modules.base import ModuleSpec
from modules.dashboard.page import DashboardPage
from modules.datagrid.page import DataGridPage
from modules.settings.page import SettingsPage
from modules.showcase.page import WidgetShowcasePage


def default_module_specs(_: AppContext) -> tuple[ModuleSpec, ...]:
    return (
        ModuleSpec("showcase", "Widget Showcase", "sliders", lambda ctx: WidgetShowcasePage(ctx), lazy=True),
        ModuleSpec("dashboard", "Dashboard", "dashboard", lambda ctx: DashboardPage(ctx), lazy=True),
        ModuleSpec("datagrid", "Data Grid", "table", lambda ctx: DataGridPage(ctx), lazy=True),
        ModuleSpec("settings", "Settings", "settings", lambda ctx: SettingsPage(ctx), lazy=True),
    )
