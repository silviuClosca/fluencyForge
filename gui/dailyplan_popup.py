from __future__ import annotations

from typing import Callable, Optional

from aqt import mw
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    Qt,
)

from ..core.models import DailyPlan


class DailyPlanPopup(QDialog):
    """Minimalist read-only Day View for today's plan.

    Can be shown on startup or from other views (Dashboard, Daily Plan).
    """

    def __init__(
        self,
        plan: DailyPlan,
        parent: Optional[object] = None,
        open_main_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent if parent is not None else mw)
        self.setWindowTitle("Today's Plan")
        self._open_main_callback = open_main_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Heading
        title = QLabel("<b>Today's Plan</b>")
        layout.addWidget(title)

        # Morning
        layout.addWidget(QLabel("Morning"))
        self.morning_view = QTextEdit(self)
        self.morning_view.setReadOnly(True)
        self.morning_view.setPlainText(plan.morning or "–")
        self.morning_view.setMinimumHeight(50)
        layout.addWidget(self.morning_view)

        # Afternoon
        layout.addWidget(QLabel("Afternoon"))
        self.afternoon_view = QTextEdit(self)
        self.afternoon_view.setReadOnly(True)
        self.afternoon_view.setPlainText(plan.afternoon or "–")
        self.afternoon_view.setMinimumHeight(50)
        layout.addWidget(self.afternoon_view)

        # Evening
        layout.addWidget(QLabel("Evening"))
        self.evening_view = QTextEdit(self)
        self.evening_view.setReadOnly(True)
        self.evening_view.setPlainText(plan.evening or "–")
        self.evening_view.setMinimumHeight(50)
        layout.addWidget(self.evening_view)

        # Buttons row
        buttons = QHBoxLayout()
        buttons.addStretch(1)

        if self._open_main_callback is not None:
            self.open_main_button = QPushButton("Open FluencyForge", self)
            self.open_main_button.clicked.connect(self._on_open_main)
            buttons.addWidget(self.open_main_button)

        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)

        layout.addLayout(buttons)

        # Size & behavior
        self.setMinimumWidth(320)
        self.setMaximumWidth(480)
        self.setWindowModality(Qt.WindowModality.NonModal)

    def _on_open_main(self) -> None:
        if self._open_main_callback is not None:
            self._open_main_callback()
        self.close()
