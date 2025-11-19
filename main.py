from typing import Optional

from aqt import mw, gui_hooks
from aqt.qt import QAction, QDockWidget, Qt, QWidget

from .gui.main_window import LanguageForgeWindow
from .core.logic_dailyplan import load_daily_plan
from .core.logic_settings import load_settings

_ff_dock: Optional[QDockWidget] = None
_ff_widget: Optional[LanguageForgeWindow] = None


def _ensure_dock() -> QDockWidget:
    global _ff_dock, _ff_widget
    if _ff_dock is None:
        _ff_widget = LanguageForgeWindow(mw)
        # Ensure the dock is wide enough that all dashboard content
        # (including the radar) is visible without horizontal resizing.
        _ff_widget.setMinimumWidth(520)

        dock = QDockWidget("LanguageForge", mw)
        dock.setObjectName("LanguageForgeDock")
        dock.setWidget(_ff_widget)
        # Hide the default title bar (text + native buttons); we provide
        # custom pop-out/close buttons inline in the tab bar instead.
        dock.setTitleBarWidget(QWidget(dock))
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        _ff_dock = dock
    return _ff_dock


def _show_languageforge() -> None:
    dock = _ensure_dock()
    dock.show()
    dock.raise_()


def _maybe_show_on_startup() -> None:
    # New behavior: settings.open_on_startup is the main source of truth.
    settings = load_settings()
    show = settings.open_on_startup

    # Backward compatibility: if settings are default and the legacy
    # DailyPlan flag was enabled, respect it once.
    if not show:
        plan = load_daily_plan()
        show = bool(getattr(plan, "show_on_startup", False))

    if not show:
        return

    dock = _ensure_dock()
    dock.show()
    dock.raise_()


def init_addon() -> None:
    action = QAction("LanguageForge – Language System", mw)
    action.triggered.connect(_show_languageforge)
    mw.form.menuTools.addAction(action)

    gui_hooks.main_window_did_init.append(_maybe_show_on_startup)

    # When Anki's theme changes (light <-> dark), update LanguageForge theme
    # immediately if using "anki_auto" mode.
    try:
        if hasattr(gui_hooks, "theme_did_change"):
            def _on_theme_changed() -> None:
                global _ff_widget
                if _ff_widget is not None:
                    # Reload settings to check if we're in anki_auto mode
                    settings = load_settings()
                    if settings.theme == "anki_auto":
                        # Update theme colors and reapply
                        if hasattr(_ff_widget, "_get_current_theme_colors"):
                            _ff_widget._current_theme_colors = _ff_widget._get_current_theme_colors()  # type: ignore[attr-defined]
                        if hasattr(_ff_widget, "_apply_tab_styles"):
                            _ff_widget._apply_tab_styles()  # type: ignore[attr-defined]
                        # First rebuild dashboard resources preview so new
                        # Open buttons exist before we apply theme & font.
                        try:
                            dashboard = getattr(_ff_widget, "dashboard_view", None)
                            if dashboard is not None and hasattr(dashboard, "refresh_resources_from_storage"):
                                dashboard.refresh_resources_from_storage()  # type: ignore[attr-defined]
                        except Exception:
                            # If anything goes wrong, fall back to theme
                            # application only.
                            pass

                        if hasattr(_ff_widget, "_apply_theme_to_all_views"):
                            _ff_widget._apply_theme_to_all_views()  # type: ignore[attr-defined]
                        if hasattr(_ff_widget, "_apply_font_size"):
                            _ff_widget._apply_font_size()  # type: ignore[attr-defined]

            gui_hooks.theme_did_change.append(_on_theme_changed)  # type: ignore[attr-defined]
    except Exception:
        # Older Anki versions may not have theme_did_change; ignore.
        pass
