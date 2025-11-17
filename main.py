from typing import Optional

from aqt import mw, gui_hooks
from aqt.qt import QAction, QDockWidget, Qt

from .gui.main_window import FluencyForgeWindow
from .core.logic_dailyplan import load_daily_plan

_ff_dock: Optional[QDockWidget] = None
_ff_widget: Optional[FluencyForgeWindow] = None


def _ensure_dock() -> QDockWidget:
    global _ff_dock, _ff_widget
    if _ff_dock is None:
        _ff_widget = FluencyForgeWindow(mw)
        # Ensure the dock is wide enough that all dashboard content
        # (including the radar) is visible without horizontal resizing.
        _ff_widget.setMinimumWidth(600)

        dock = QDockWidget("FluencyForge", mw)
        dock.setObjectName("FluencyForgeDock")
        dock.setWidget(_ff_widget)
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        _ff_dock = dock
    return _ff_dock


def _show_fluencyforge() -> None:
    dock = _ensure_dock()
    dock.show()
    dock.raise_()


def _maybe_show_on_startup() -> None:
    plan = load_daily_plan()
    if not plan.show_on_startup:
        return

    dock = _ensure_dock()
    dock.show()
    dock.raise_()


def init_addon() -> None:
    action = QAction("FluencyForge – Language System", mw)
    action.triggered.connect(_show_fluencyforge)
    mw.form.menuTools.addAction(action)

    gui_hooks.main_window_did_init.append(_maybe_show_on_startup)
