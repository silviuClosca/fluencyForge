from __future__ import annotations

from typing import Optional

from aqt.qt import QWidget, QSize, QPainter, QColor, QPen, Qt, QCursor, pyqtSignal


class CircleIndicator(QWidget):
    clicked = pyqtSignal()

    def __init__(self, completed: bool, size: int = 18, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._completed = completed
        self._size = size
        self.setMinimumSize(size, size)
        self.setMaximumSize(size, size)
        # Make it clear this is interactive wherever it is used.
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def set_completed(self, completed: bool) -> None:
        if self._completed != completed:
            self._completed = completed
            self.update()

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(self._size, self._size)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        try:
            hint = QPainter.RenderHint.Antialiasing
        except AttributeError:
            hint = QPainter.Antialiasing  # type: ignore[attr-defined]
        painter.setRenderHint(hint)

        border_color = QColor("#7CC9A3")

        rect = self.rect().adjusted(1, 1, -1, -1)

        # Draw circle outline only
        pen = QPen(border_color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawEllipse(rect)

        # Draw a green checkmark when completed
        if self._completed:
            pen = QPen(border_color)
            pen.setWidth(2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

            # Simple checkmark path inside the circle
            x1 = rect.left() + rect.width() * 0.25
            y1 = rect.top() + rect.height() * 0.55
            x2 = rect.left() + rect.width() * 0.45
            y2 = rect.bottom() - rect.height() * 0.25
            x3 = rect.right() - rect.width() * 0.2
            y3 = rect.top() + rect.height() * 0.3

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            painter.drawLine(int(x2), int(y2), int(x3), int(y3))

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        self.clicked.emit()
        try:
            super().mousePressEvent(event)
        except Exception:
            pass


_SKILL_EMOJIS = {
    "reading": "📖",
    "listening": "🎧",
    "speaking": "🗣️",
    "writing": "✍️",
}

_SKILL_LABELS = {
    "reading": "Reading",
    "listening": "Listening",
    "speaking": "Speaking",
    "writing": "Writing",
}


def get_skill_emoji(skill: str) -> str:
    return _SKILL_EMOJIS.get(skill, "")


def get_skill_label(skill: str) -> str:
    return _SKILL_LABELS.get(skill, skill.capitalize())
