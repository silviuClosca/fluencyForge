from __future__ import annotations

from typing import Optional

from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QCheckBox,
)

from ..core.logic_dailyplan import load_daily_plan, save_daily_plan
from ..core.models import DailyPlan
from .dailyplan_popup import DailyPlanPopup


class DailyPlanView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Morning
        layout.addWidget(QLabel("Morning"))
        self.morning_edit = QTextEdit(self)
        self.morning_edit.setMinimumHeight(80)
        layout.addWidget(self.morning_edit)

        # Afternoon
        layout.addWidget(QLabel("Afternoon"))
        self.afternoon_edit = QTextEdit(self)
        self.afternoon_edit.setMinimumHeight(80)
        layout.addWidget(self.afternoon_edit)

        # Evening
        layout.addWidget(QLabel("Evening"))
        self.evening_edit = QTextEdit(self)
        self.evening_edit.setMinimumHeight(80)
        layout.addWidget(self.evening_edit)

        # Behavior: show on startup
        self.show_on_startup_checkbox = QCheckBox(
            "Open Today's Plan on startup", self
        )
        layout.addWidget(self.show_on_startup_checkbox)

        # Actions row
        actions_row = QHBoxLayout()
        self.preview_button = QPushButton("Preview Day View", self)
        self.save_button = QPushButton("Save Plan", self)
        actions_row.addWidget(self.preview_button)
        actions_row.addStretch(1)
        actions_row.addWidget(self.save_button)
        layout.addLayout(actions_row)

        # Optional status label
        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

        self.save_button.clicked.connect(self._on_save)
        self.preview_button.clicked.connect(self._on_preview)

        self._load()

    def _load(self) -> None:
        plan: DailyPlan = load_daily_plan()
        self.morning_edit.setPlainText(plan.morning)
        self.afternoon_edit.setPlainText(plan.afternoon)
        self.evening_edit.setPlainText(plan.evening)
        self.show_on_startup_checkbox.setChecked(plan.show_on_startup)

    def _on_save(self) -> None:
        current = load_daily_plan()
        plan = DailyPlan(
            morning=self.morning_edit.toPlainText(),
            afternoon=self.afternoon_edit.toPlainText(),
            evening=self.evening_edit.toPlainText(),
            show_on_startup=self.show_on_startup_checkbox.isChecked(),
        )
        save_daily_plan(plan)
        self.status_label.setText("Plan saved")

    def _on_preview(self) -> None:
        """Open the read-only Day View popup for the current plan."""

        # Use the current text in the editors so preview matches unsaved changes.
        plan = DailyPlan(
            morning=self.morning_edit.toPlainText(),
            afternoon=self.afternoon_edit.toPlainText(),
            evening=self.evening_edit.toPlainText(),
            show_on_startup=self.show_on_startup_checkbox.isChecked(),
        )
        popup = DailyPlanPopup(plan, parent=self)
        popup.show()
