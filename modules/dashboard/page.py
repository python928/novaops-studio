from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.app_context import AppContext
from widgets import (
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
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        title = QLabel("Program Overview")
        title.setProperty("title", "h1")

        subtitle = QLabel(
            "A unified dashboard layer for ERP, CRM, operations, and admin programs with shared UX patterns."
        )
        subtitle.setProperty("muted", True)

        timeframe_row = QHBoxLayout()
        timeframe_row.setContentsMargins(0, 0, 0, 0)
        timeframe_row.setSpacing(8)

        timeframe_label = QLabel("Time range")
        timeframe_label.setProperty("muted", True)

        self._timeframe = SegmentedControl(["Today", "Week", "Month", "Quarter"], initial="Month")
        self._timeframe.selectionChanged.connect(
            lambda value: context.events.statusMessage.emit(f"Dashboard range: {value}")
        )

        timeframe_row.addWidget(timeframe_label)
        timeframe_row.addWidget(self._timeframe)
        timeframe_row.addStretch(1)

        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        status_row.setSpacing(8)

        status_row.addWidget(StatusLozenge("Healthy"))
        status_row.addWidget(StatusLozenge("At Risk"))
        status_row.addWidget(StatusLozenge("Blocked"))
        status_row.addWidget(StatusLozenge("Review"))
        status_row.addStretch(1)

        strip = KpiStrip(
            [
                ("Active users", "1,284", "online this hour"),
                ("Automations", "42", "running workflows"),
                ("SLA breaches", "3", "last 24h"),
                ("Pending approvals", "19", "cross-team handoffs"),
            ]
        )

        cards = QGridLayout()
        cards.setSpacing(12)
        cards.addWidget(
            MetricCard(
                "Program Modules",
                "4",
                "Showcase, Dashboard, Data Grid, Settings",
                delta_text="+1 this week",
                trend="up",
                progress=82,
            ),
            0,
            0,
        )
        cards.addWidget(
            MetricCard(
                "Theme Profiles",
                "2",
                "Dark and light with live accent updates",
                delta_text="Stable",
                trend="flat",
                progress=65,
            ),
            0,
            1,
        )
        cards.addWidget(
            MetricCard(
                "Data Capacity",
                "30K",
                "Incremental rendering via QAbstractTableModel",
                delta_text="-2.1% load",
                trend="down",
                progress=91,
            ),
            1,
            0,
        )
        cards.addWidget(
            MetricCard(
                "Automation",
                "74%",
                "Shared style and behavior across modules",
                delta_text="+6% this sprint",
                trend="up",
                progress=74,
            ),
            1,
            1,
        )

        banner = InsightBanner(
            "Production Hint",
            "Connect these widgets to your real APIs and user roles for immediate enterprise reuse.",
            action_text="Open checklist",
            icon_text="!",
        )
        banner.actionTriggered.connect(
            lambda: context.events.statusMessage.emit("Checklist: API hooks, auth scopes, and analytics wiring")
        )

        lower_row = QHBoxLayout()
        lower_row.setContentsMargins(0, 0, 0, 0)
        lower_row.setSpacing(12)

        rollout = StepProgress(
            ["Connect data", "Map roles", "Automate checks", "Go live"],
            current_index=2,
        )
        rollout.stepChanged.connect(
            lambda index, step: context.events.statusMessage.emit(
                f"Program rollout step {index + 1}: {step}"
            )
        )

        timeline = TimelineFeed("Recent Activity")
        timeline.set_events(
            [
                ("Finance sync completed", "12,410 rows refreshed", "2 min ago", "success"),
                ("Risk rule triggered", "4 items moved to review", "11 min ago", "warning"),
                ("Approval delayed", "Owner reassignment required", "35 min ago", "danger"),
                ("Nightly backup", "Archive validated", "1h ago", "info"),
            ]
        )

        lower_row.addWidget(rollout, 1, Qt.AlignmentFlag.AlignTop)
        lower_row.addWidget(timeline, 1, Qt.AlignmentFlag.AlignTop)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(timeframe_row)
        root.addLayout(status_row)
        root.addWidget(strip)
        root.addLayout(cards)
        root.addWidget(banner, 0, Qt.AlignmentFlag.AlignTop)
        root.addLayout(lower_row)
        root.addStretch(1)
