from __future__ import annotations

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QDateEdit,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from widgets import (
    ActionTile,
    CommandDeck,
    InsightBanner,
    KpiStrip,
    MetricCard,
    SegmentedControl,
    StatusLozenge,
    StepProgress,
    TimelineFeed,
)


class DashboardPage(QWidget):
    def __init__(self, context: AppContext) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget()
        page_root = QVBoxLayout(page)
        page_root.setContentsMargins(20, 20, 20, 20)
        page_root.setSpacing(16)

        scroll.setWidget(page)
        root.addWidget(scroll)

        root = page_root

        eyebrow = QLabel("Workspace control layer")
        eyebrow.setProperty("kicker", True)

        title = QLabel("Large-Scale Operations Workspace")
        title.setProperty("title", "h1")

        subtitle = QLabel(
            "A reusable command surface for ERP, CRM, internal tools, and data-heavy admin products."
        )
        subtitle.setProperty("muted", True)

        hero_row = QHBoxLayout()
        hero_row.setContentsMargins(0, 0, 0, 0)
        hero_row.setSpacing(12)

        self._command_deck = CommandDeck(
            "What do you want to do next?",
            "Use this as the shared starting point for modules, commands, automations, and record lookups.",
            badge_text="OS",
            placeholder="Open module, run sync, search records, or jump to settings...",
            submit_text="Execute",
            suggestions=(
                "Open data grid",
                "Run nightly sync",
                "Review blockers",
                "Change accent theme",
            ),
        )
        self._command_deck.submitted.connect(
            lambda value: context.events.statusMessage.emit(
                f"Workspace command: {value or 'No command entered'}"
            )
        )
        self._command_deck.shortcutTriggered.connect(
            lambda value: context.events.statusMessage.emit(f"Quick command selected: {value}")
        )

        actions_grid = QGridLayout()
        actions_grid.setHorizontalSpacing(10)
        actions_grid.setVerticalSpacing(10)

        action_specs = (
            (
                "Create workspace",
                "Bootstrap a new module with the shared shell, tokens, and control patterns.",
                "Template",
                "+",
                "success",
                "Start now",
            ),
            (
                "Review blockers",
                "Surface items that need decisions before they slow the rest of the flow.",
                "Risk",
                "!",
                "warning",
                "Inspect",
            ),
            (
                "Connect automations",
                "Attach imports, approvals, and sync jobs without rebuilding the UI structure.",
                "Flow",
                "~",
                "info",
                "Configure",
            ),
            (
                "Audit readiness",
                "Validate density, table clarity, and theme consistency before shipping a module.",
                "Quality",
                "#",
                "danger",
                "Run audit",
            ),
        )

        for index, (tile_title, body, meta, badge, tone, action_text) in enumerate(action_specs):
            tile = ActionTile(
                tile_title,
                body,
                meta=meta,
                badge_text=badge,
                tone=tone,
                action_text=action_text,
            )
            tile.activated.connect(
                lambda value, label=tile_title: context.events.statusMessage.emit(f"Action tile: {label}")
            )
            actions_grid.addWidget(tile, index // 2, index % 2)

        hero_row.addWidget(self._command_deck, 3)
        hero_row.addLayout(actions_grid, 2)

        filter_row = QHBoxLayout()
        filter_row.setContentsMargins(0, 0, 0, 0)
        filter_row.setSpacing(10)

        timeframe_label = QLabel("View horizon")
        timeframe_label.setProperty("muted", True)

        self._timeframe = SegmentedControl(["Today", "Week", "Month", "Quarter"], initial="Month")
        self._timeframe.selectionChanged.connect(
            lambda value: context.events.statusMessage.emit(f"Dashboard horizon: {value}")
        )

        date_label = QLabel("As of")
        date_label.setProperty("muted", True)

        self._as_of_date = QDateEdit(QDate.currentDate())
        self._as_of_date.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._as_of_date.setCalendarPopup(True)
        self._as_of_date.setDisplayFormat("MMM d, yyyy")
        self._as_of_date.setMaximumWidth(168)
        self._as_of_date.dateChanged.connect(
            lambda value: context.events.statusMessage.emit(
                f"Dashboard date: {value.toString('MMM d, yyyy')}"
            )
        )

        filter_row.addWidget(timeframe_label)
        filter_row.addWidget(self._timeframe)
        filter_row.addStretch(1)
        filter_row.addWidget(date_label)
        filter_row.addWidget(self._as_of_date)
        filter_row.addWidget(StatusLozenge("Healthy"))
        filter_row.addWidget(StatusLozenge("At Risk"))
        filter_row.addWidget(StatusLozenge("Blocked"))
        filter_row.addWidget(StatusLozenge("Review"))

        strip = KpiStrip(
            [
                ("Active workspaces", "12", "shared shell instances"),
                ("Automation packs", "42", "running workflows"),
                ("Pending approvals", "19", "cross-team handoffs"),
                ("Release confidence", "94%", "theme and data coverage"),
            ]
        )

        cards = QGridLayout()
        cards.setHorizontalSpacing(12)
        cards.setVerticalSpacing(12)
        cards.addWidget(
            MetricCard(
                "Design System Coverage",
                "84%",
                "Reusable controls, cards, tables, and shell elements",
                delta_text="+12% this cycle",
                trend="up",
                progress=84,
            ),
            0,
            0,
        )
        cards.addWidget(
            MetricCard(
                "Module Startup Time",
                "Fast",
                "Shared tokens and widgets reduce per-project UI setup",
                delta_text="Stable",
                trend="flat",
                progress=67,
            ),
            0,
            1,
        )
        cards.addWidget(
            MetricCard(
                "Dense Data Readiness",
                "30K+",
                "Virtualized rendering for large records and enterprise tables",
                delta_text="+rows",
                trend="up",
                progress=91,
            ),
            1,
            0,
        )
        cards.addWidget(
            MetricCard(
                "Interaction Clarity",
                "Focused",
                "One primary action, quieter secondary actions, stronger focus cues",
                delta_text="Refined",
                trend="flat",
                progress=88,
            ),
            1,
            1,
        )

        banner = InsightBanner(
            "Design Intent",
            "This dashboard is now structured as a command-first workspace so future modules can scale without ad-hoc surfaces.",
            action_text="Focus command deck",
            icon_text="i",
        )
        banner.actionTriggered.connect(self._command_deck.focus_search)

        lower_row = QHBoxLayout()
        lower_row.setContentsMargins(0, 0, 0, 0)
        lower_row.setSpacing(12)

        rollout = StepProgress(
            ["Bootstrap", "Wire data", "Tune workflows", "Ship module"],
            current_index=2,
        )
        rollout.stepChanged.connect(
            lambda index, step: context.events.statusMessage.emit(
                f"Workspace rollout step {index + 1}: {step}"
            )
        )

        timeline = TimelineFeed("Workspace Timeline")
        timeline.set_events(
            [
                ("Command deck initialized", "Shared quick actions are ready", "Just now", "success"),
                ("Risk cluster detected", "4 blockers need attention", "12 min ago", "warning"),
                ("Theme tokens refreshed", "Accent and density previews updated", "24 min ago", "info"),
                ("Audit reminder", "Review table interactions before shipping", "1h ago", "danger"),
            ]
        )

        lower_row.addWidget(rollout, 1, Qt.AlignmentFlag.AlignTop)
        lower_row.addWidget(timeline, 1, Qt.AlignmentFlag.AlignTop)

        root.addWidget(eyebrow)
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(hero_row)
        root.addLayout(filter_row)
        root.addWidget(strip)
        root.addLayout(cards)
        root.addWidget(banner, 0, Qt.AlignmentFlag.AlignTop)
        root.addLayout(lower_row)
        root.addStretch(1)
