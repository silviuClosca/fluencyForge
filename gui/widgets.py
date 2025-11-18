from __future__ import annotations

from typing import Optional

from aqt.qt import QWidget, QSize, QPainter, QColor, QPen, Qt, QCursor, pyqtSignal


class CircleIndicator(QWidget):
    clicked = pyqtSignal()

    def __init__(self, completed: bool, size: int = 18, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._completed = completed
        self._size = size
        self._hover = False
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

        # Ring colors: light for incomplete, stronger green for completed.
        empty_ring_color = QColor("#BEEAD3")
        completed_ring_color = QColor("#7CC9A3")

        rect = self.rect().adjusted(1, 1, -1, -1)

        # Subtle hover background so the circle responds visually to the mouse.
        if self._hover:
            # Soft light green highlight under both states.
            hover_bg = QColor("#BEEAD3")
            hover_bg.setAlpha(120)
            painter.setBrush(hover_bg)
        else:
            painter.setBrush(QColor(0, 0, 0, 0))

        # Draw circle outline: thin and light when incomplete, thicker and
        # stronger green once completed.
        ring_color = completed_ring_color if self._completed else empty_ring_color
        pen = QPen(ring_color)
        pen.setWidth(2 if self._completed else 1)
        painter.setPen(pen)
        painter.drawEllipse(rect)

        # Draw a green checkmark when completed
        if self._completed:
            # Use the original green for the checkmark so it stays readable.
            check_color = QColor("#7CC9A3")
            pen = QPen(check_color)
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

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._hover = True
        self.update()
        try:
            super().enterEvent(event)
        except Exception:
            pass

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._hover = False
        self.update()
        try:
            super().leaveEvent(event)
        except Exception:
            pass

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
