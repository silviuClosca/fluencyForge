from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QPushButton,
    QFrame,
    Qt,
    QToolButton,
    QMessageBox,
)

from ..core.logic_goals import (
    load_month_goals,
    save_month_goals,
    get_all_goals,
    get_current_month_id,
    auto_archive_past_goals,
)
from .widgets import CircleIndicator
from ..core.models import MonthlyGoals


class GoalsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Auto-archive immediately when opening Goals view
        auto_archive_past_goals(get_current_month_id())

        # Archived banner
        self.banner_frame = QFrame(self)
        banner_layout = QHBoxLayout(self.banner_frame)
        banner_layout.setContentsMargins(6, 4, 6, 4)
        self.banner_label = QLabel("", self.banner_frame)
        banner_layout.addWidget(self.banner_label)
        self.banner_frame.hide()
        layout.addWidget(self.banner_frame)

        top = QHBoxLayout()
        top.addWidget(QLabel("Month"))
        self.month_combo = QComboBox(self)
        top.addWidget(self.month_combo)
        self.show_archived_checkbox = QCheckBox("Show archived months", self)
        top.addWidget(self.show_archived_checkbox)
        layout.addLayout(top)

        # Progress summary
        self.progress_label = QLabel("", self)
        layout.addWidget(self.progress_label)

        # Per-goal cards
        self.cards_container = QVBoxLayout()
        self.cards_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.goal_cards: list[QFrame] = []
        # CircleIndicators used as the visual completion control per goal;
        # we still keep a QCheckBox for logic and autosave.
        self.goal_state_indicators: list[CircleIndicator] = []
        self.goal_checks: list[QCheckBox] = []
        self.goal_edits: list[QLineEdit] = []
        self.goal_delete_buttons: list[QPushButton] = []
        self.category_combos: list[QComboBox] = []
        self.subtasks_layouts: list[QVBoxLayout] = []
        self.subtasks_containers: list[QWidget] = []
        self.subtasks_toggles: list[QToolButton] = []
        self.reflection_edits: list[QTextEdit] = []
        self.reflection_containers: list[QWidget] = []
        self.reflection_toggles: list[QToolButton] = []

        for i in range(3):
            card = QFrame(self)
            card.setFrameShape(QFrame.Shape.StyledPanel)
            card.setFrameShadow(QFrame.Shadow.Plain)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(8, 6, 8, 6)
            card_layout.setSpacing(4)

            # Top row: CircleIndicator, hidden checkbox, text, category, clear
            top_row = QHBoxLayout()
            state_indicator = CircleIndicator(False, size=16, parent=card)
            top_row.addWidget(state_indicator)

            check = QCheckBox(card)
            # Hide the built-in checkbox indicator; CircleIndicator is the
            # visible control.
            check.setTristate(False)
            check.setStyleSheet(
                "QCheckBox::indicator { width: 0px; height: 0px; "
                "border: none; background-color: transparent; }"
            )
            top_row.addWidget(check)

            edit = QLineEdit(card)
            edit.setPlaceholderText(f"Goal {i + 1}")
            edit.setClearButtonEnabled(False)
            top_row.addWidget(edit, 1)

            category = QComboBox(card)
            category.addItems(
                [
                    "General",
                    "Reading",
                    "Listening",
                    "Speaking",
                    "Writing",
                    "Vocabulary",
                    "Grammar",
                ]
            )

            top_row.addWidget(category)

            delete_btn = QPushButton("Clear", card)
            delete_btn.setToolTip("Clear this goal")
            delete_btn.setFixedWidth(60)
            top_row.addWidget(delete_btn)
            card_layout.addLayout(top_row)

            # Subtasks section (collapsible)
            subtasks_header = QHBoxLayout()
            subtasks_toggle = QToolButton(card)
            subtasks_toggle.setCheckable(True)
            # Default collapsed
            subtasks_toggle.setChecked(False)
            subtasks_toggle.setArrowType(Qt.ArrowType.RightArrow)
            subtasks_header.addWidget(subtasks_toggle)
            subtasks_header.addWidget(QLabel("Subtasks", card))
            subtasks_header.addStretch(1)
            card_layout.addLayout(subtasks_header)

            subtasks_widget = QWidget(card)
            subtasks_layout = QVBoxLayout(subtasks_widget)
            subtasks_layout.setContentsMargins(0, 0, 0, 0)
            subtasks_layout.setSpacing(2)
            subtasks_widget.setVisible(False)
            card_layout.addWidget(subtasks_widget)

            add_subtask_btn = QPushButton("Add subtask", card)
            add_subtask_btn.clicked.connect(
                lambda _=False, idx=i: self._on_add_subtask(idx)
            )
            card_layout.addWidget(add_subtask_btn)

            # Reflection section (collapsible)
            refl_header = QHBoxLayout()
            refl_toggle = QToolButton(card)
            refl_toggle.setCheckable(True)
            # Default collapsed
            refl_toggle.setChecked(False)
            refl_toggle.setArrowType(Qt.ArrowType.RightArrow)
            refl_header.addWidget(refl_toggle)
            refl_header.addWidget(QLabel("Reflection", card))
            refl_header.addStretch(1)
            card_layout.addLayout(refl_header)

            refl_widget = QWidget(card)
            refl_layout = QVBoxLayout(refl_widget)
            refl_layout.setContentsMargins(0, 0, 0, 0)
            reflection = QTextEdit(card)
            reflection.setPlaceholderText("Write a short reflection for this goal…")
            refl_layout.addWidget(reflection)
            refl_widget.setVisible(False)
            card_layout.addWidget(refl_widget)

            self.cards_container.addWidget(card)
            self.goal_cards.append(card)
            self.goal_state_indicators.append(state_indicator)
            self.goal_checks.append(check)
            self.goal_edits.append(edit)
            self.goal_delete_buttons.append(delete_btn)
            self.category_combos.append(category)
            self.subtasks_layouts.append(subtasks_layout)
            self.subtasks_containers.append(subtasks_widget)
            self.subtasks_toggles.append(subtasks_toggle)
            self.reflection_edits.append(reflection)
            self.reflection_containers.append(refl_widget)
            self.reflection_toggles.append(refl_toggle)

            # Wire collapsible behavior
            subtasks_toggle.toggled.connect(
                lambda checked, w=subtasks_widget, t=subtasks_toggle: self._on_toggle_section(
                    checked, w, t
                )
            )
            refl_toggle.toggled.connect(
                lambda checked, w=refl_widget, t=refl_toggle: self._on_toggle_section(
                    checked, w, t
                )
            )

            # Delete goal handler
            delete_btn.clicked.connect(lambda _=False, idx=i: self._on_delete_goal(idx))

            # Autosave wiring (excluding Clear, which has its own flow)
            check.toggled.connect(lambda _checked, idx=i: self._auto_save())
            edit.editingFinished.connect(lambda idx=i: self._auto_save())
            edit.textChanged.connect(self._auto_save)
            category.currentIndexChanged.connect(lambda _idx, i=i: self._auto_save())
            reflection.textChanged.connect(self._auto_save)

            # Clicking the CircleIndicator toggles the hidden checkbox,
            # which drives autosave and persistence.
            state_indicator.clicked.connect(lambda _=False, c=check: c.toggle())

        layout.addLayout(self.cards_container)

        # Current in-memory goals
        self._current_goals: MonthlyGoals | None = None

        self._populate_months()
        self.month_combo.currentTextChanged.connect(self._on_month_changed)
        self.show_archived_checkbox.toggled.connect(self._on_show_archived_toggled)

        self._load_month()

    def _current_month_str(self) -> str:
        return datetime.now().strftime("%Y-%m")

    def _populate_months(self) -> None:
        """Populate the month dropdown, optionally including archived months."""

        current = self._current_month_str()
        show_archived = self.show_archived_checkbox.isChecked()

        goals_list: List[MonthlyGoals] = get_all_goals()
        month_to_archived = {g.month: g.archived for g in goals_list}

        months = set(month_to_archived.keys())
        months.add(current)

        # Filter out archived months unless explicitly requested.
        if not show_archived:
            months = {m for m in months if not month_to_archived.get(m, False)}

        self.month_combo.blockSignals(True)
        self.month_combo.clear()
        for m in sorted(months):
            archived = month_to_archived.get(m, False)
            label = f"{m} (archived)" if archived and show_archived else m
            self.month_combo.addItem(label)
        self.month_combo.blockSignals(False)

        # Try to keep current month selected when possible.
        display_current = current
        if show_archived and month_to_archived.get(current, False):
            display_current = f"{current} (archived)"
        idx = self.month_combo.findText(display_current)
        if idx >= 0:
            self.month_combo.setCurrentIndex(idx)

    def _combo_month_value(self) -> str:
        text = self.month_combo.currentText() or self._current_month_str()
        # Entries for archived months are of the form "YYYY-MM (archived)".
        return text.split()[0]

    def _load_month(self) -> None:
        month = self._combo_month_value()
        goals: MonthlyGoals = load_month_goals(month)
        self._current_goals = goals

        for i in range(3):
            text = goals.goals[i] if i < len(goals.goals) else ""
            done = goals.completed[i] if i < len(goals.completed) else False
            category = goals.categories[i] if i < len(goals.categories) else "General"
            reflection = goals.reflections[i] if i < len(goals.reflections) else ""

            self.goal_edits[i].setText(text)
            self.goal_checks[i].setChecked(done)
            if i < len(self.goal_state_indicators):
                self.goal_state_indicators[i].set_completed(done)

            idx = self.category_combos[i].findText(category)
            self.category_combos[i].setCurrentIndex(idx if idx >= 0 else 0)
            self.reflection_edits[i].setPlainText(reflection)

            # Clear and repopulate subtasks (both layouts and child widgets)
            layout = self.subtasks_layouts[i]
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                inner = item.layout()
                if inner is not None:
                    while inner.count():
                        inner_item = inner.takeAt(0)
                        iw = inner_item.widget()
                        if iw is not None:
                            iw.deleteLater()
                if w is not None:
                    w.deleteLater()

            subtasks = goals.subtasks[i] if i < len(goals.subtasks) else []
            subtasks_done = goals.subtasks_done[i] if i < len(goals.subtasks_done) else []
            for s_idx, s_text in enumerate(subtasks):
                row = QHBoxLayout()

                # CircleIndicator as the visible completion control for the
                # subtask, backed by a hidden checkbox for logic.
                initial_done = (
                    subtasks_done[s_idx] if s_idx < len(subtasks_done) else False
                )
                circle = CircleIndicator(
                    initial_done, size=14, parent=self.subtasks_containers[i]
                )
                chk = QCheckBox(self.subtasks_containers[i])
                chk.setTristate(False)
                chk.setChecked(initial_done)
                chk.setStyleSheet(
                    "QCheckBox::indicator { width: 0px; height: 0px; "
                    "border: none; background-color: transparent; }"
                )

                edit = QLineEdit(self.subtasks_containers[i])
                edit.setText(str(s_text))

                row.addWidget(circle)
                row.addWidget(chk)
                row.addWidget(edit, 1)
                layout.addLayout(row)

                # Keep CircleIndicator and checkbox visually in sync
                chk.toggled.connect(lambda checked, circ=circle: circ.set_completed(checked))

                # Autosave when existing subtask is changed
                chk.toggled.connect(self._auto_save)
                edit.textChanged.connect(self._auto_save)
                circle.clicked.connect(lambda _=False, c=chk: c.toggle())

        self._update_banner_and_readonly()
        self._update_progress_label()
        self._update_card_styles()

    def _on_month_changed(self, _text: str) -> None:
        self._load_month()

    def _on_show_archived_toggled(self, _checked: bool) -> None:
        self._populate_months()
        self._load_month()

    def _on_save(self) -> None:
        if self._current_goals is None:
            month = self._combo_month_value()
            self._current_goals = load_month_goals(month)

        goals = self._current_goals
        texts = [e.text() for e in self.goal_edits]
        checks = [c.isChecked() for c in self.goal_checks]
        categories = [c.currentText() for c in self.category_combos]
        reflections = [r.toPlainText() for r in self.reflection_edits]

        # Ensure arrays have 3 entries
        while len(goals.created_at) < 3:
            goals.created_at.append("")
        while len(goals.completed_at) < 3:
            goals.completed_at.append("")

        now_iso = datetime.now().isoformat(timespec="seconds")

        for i in range(3):
            old_text = goals.goals[i] if i < len(goals.goals) else ""
            old_done = goals.completed[i] if i < len(goals.completed) else False
            old_refl = goals.reflections[i] if i < len(goals.reflections) else ""

            new_text = texts[i]
            new_done = checks[i]
            new_refl = reflections[i]

            # Guardrail: if the user hasn't used the explicit Clear button,
            # avoid accidentally wiping an existing goal title or reflection
            # just because the edit field happens to be empty. We keep the
            # previous non-empty value in that case.
            if not new_text.strip() and old_text.strip():
                texts[i] = old_text
                new_text = old_text
            if not new_refl.strip() and old_refl.strip():
                reflections[i] = old_refl
                new_refl = old_refl

            # created_at: first time text becomes non-empty
            if not old_text.strip() and new_text.strip() and not goals.created_at[i]:
                goals.created_at[i] = now_iso

            # completed_at: first time marked done
            if not old_done and new_done and not goals.completed_at[i]:
                goals.completed_at[i] = now_iso

        goals.goals = texts
        goals.completed = checks
        goals.categories = categories
        goals.reflections = reflections

        # Subtasks from layouts. We start from existing subtasks so that goals
        # which currently have no visible subtask rows do not lose their
        # previously saved subtasks when, for example, only the title or
        # reflection is edited.
        existing_subtasks = list(goals.subtasks) if isinstance(goals.subtasks, list) else []
        existing_done = (
            list(goals.subtasks_done)
            if isinstance(goals.subtasks_done, list)
            else []
        )
        while len(existing_subtasks) < 3:
            existing_subtasks.append([])
        while len(existing_done) < 3:
            existing_done.append([])

        new_subtasks: list[list[str]] = []
        new_subtasks_done: list[list[bool]] = []

        for goal_index, layout in enumerate(self.subtasks_layouts):
            s_texts: list[str] = []
            s_done: list[bool] = []
            for idx in range(layout.count()):
                item = layout.itemAt(idx)
                inner = item.layout()
                if inner is None:
                    continue

                # Each subtask row now contains a CircleIndicator, a hidden
                # QCheckBox, and a QLineEdit, in that order. To make this
                # robust, locate the checkbox and line edit by type rather
                # than by fixed positions.
                chk_widget: QCheckBox | None = None
                edit_widget: QLineEdit | None = None
                for j in range(inner.count()):
                    w = inner.itemAt(j).widget()
                    if isinstance(w, QCheckBox) and chk_widget is None:
                        chk_widget = w
                    elif isinstance(w, QLineEdit) and edit_widget is None:
                        edit_widget = w

                if edit_widget is not None:
                    s_texts.append(edit_widget.text())
                    s_done.append(
                        bool(chk_widget.isChecked()) if isinstance(chk_widget, QCheckBox) else False
                    )

            # If there are no rows in the layout, keep whatever subtasks were
            # already stored for this goal instead of overwriting with [].
            if not s_texts and goal_index < len(existing_subtasks):
                new_subtasks.append(existing_subtasks[goal_index])
                # Ensure done flags list matches length.
                prev_done = list(existing_done[goal_index])
                while len(prev_done) < len(existing_subtasks[goal_index]):
                    prev_done.append(False)
                new_subtasks_done.append(prev_done[: len(existing_subtasks[goal_index])])
            else:
                new_subtasks.append(s_texts)
                new_subtasks_done.append(s_done)

        goals.subtasks = new_subtasks
        goals.subtasks_done = new_subtasks_done

        save_month_goals(goals, source="goals_view")
        self._update_progress_label()
        self._update_banner_and_readonly()
        self._update_card_styles()

    def _auto_save(self) -> None:
        """Autosave wrapper used by change signals.

        Skips saving when viewing an archived month.
        """

        if self._current_goals is not None and self._current_goals.archived:
            return
        self._on_save()

    # external API ----------------------------------------------------

    def refresh_current_month(self) -> None:
        """Reload the currently selected month from storage."""

        self._load_month()

    # helpers ---------------------------------------------------------

    def focus_goal_index(self, index: int) -> None:
        """Refresh from storage and expand a specific goal's sections.

        Called from the Dashboard when clicking the pencil icon.
        """

        self.refresh_current_month()
        if index < 0 or index >= len(self.goal_cards):
            return

        # Collapse all subtasks/reflection sections first
        for i in range(len(self.goal_cards)):
            self.subtasks_containers[i].setVisible(False)
            self.subtasks_toggles[i].setChecked(False)
            self.subtasks_toggles[i].setArrowType(Qt.ArrowType.RightArrow)
            self.reflection_containers[i].setVisible(False)
            self.reflection_toggles[i].setChecked(False)
            self.reflection_toggles[i].setArrowType(Qt.ArrowType.RightArrow)

        # Expand the selected goal's subtasks and reflection
        self.subtasks_containers[index].setVisible(True)
        self.subtasks_toggles[index].setChecked(True)
        self.subtasks_toggles[index].setArrowType(Qt.ArrowType.DownArrow)
        self.reflection_containers[index].setVisible(True)
        self.reflection_toggles[index].setChecked(True)
        self.reflection_toggles[index].setArrowType(Qt.ArrowType.DownArrow)

        # Focus the goal title for editing
        if index < len(self.goal_edits):
            self.goal_edits[index].setFocus()

    def _on_add_goal_clicked(self) -> None:
        """Jump focus to the next empty goal slot (or the last one)."""

        # Find first empty goal text box
        for edit in self.goal_edits:
            if not edit.text().strip():
                edit.setFocus()
                return

        # If none are empty, focus the last one
        if self.goal_edits:
            self.goal_edits[-1].setFocus()

    def _update_progress_label(self) -> None:
        if self._current_goals is None:
            self.progress_label.setText("")
            return
        goals = self._current_goals
        total_defined = sum(1 for g in goals.goals if g.strip())
        total_defined = max(total_defined, 1)
        done = 0
        for i, g in enumerate(goals.goals):
            if g.strip() and i < len(goals.completed) and goals.completed[i]:
                done += 1
        percent = round(done / total_defined * 100)
        self.progress_label.setText(f"{done} / 3 goals completed — {percent}%")

    def _update_banner_and_readonly(self) -> None:
        goals = self._current_goals
        if goals is None:
            self.banner_frame.hide()
            return

        if goals.archived:
            self.banner_label.setText("🗂 This month is archived. Goals are read-only.")
            self.banner_frame.show()
        else:
            self.banner_frame.hide()

        readonly = goals.archived
        for card in self.goal_cards:
            card.setEnabled(not readonly)

    def _update_card_styles(self) -> None:
        """Sync per-goal CircleIndicators with completion state."""

        goals = self._current_goals
        if goals is None:
            return

        for i, indicator in enumerate(self.goal_state_indicators):
            done = goals.completed[i] if i < len(goals.completed) else False
            indicator.set_completed(done)

    def _on_add_subtask(self, goal_index: int) -> None:
        """Append a blank subtask row to the given goal card."""

        if goal_index < 0 or goal_index >= len(self.subtasks_layouts):
            return
        # Ensure the subtasks section is expanded when adding a subtask
        self.subtasks_containers[goal_index].setVisible(True)
        self.subtasks_toggles[goal_index].setChecked(True)
        self.subtasks_toggles[goal_index].setArrowType(Qt.ArrowType.DownArrow)

        layout = self.subtasks_layouts[goal_index]
        row = QHBoxLayout()

        # New subtask uses the same CircleIndicator + hidden checkbox pattern.
        circle = CircleIndicator(False, size=14, parent=self.subtasks_containers[goal_index])
        chk = QCheckBox(self.subtasks_containers[goal_index])
        chk.setTristate(False)
        chk.setChecked(False)
        chk.setStyleSheet(
            "QCheckBox::indicator { width: 0px; height: 0px; "
            "border: none; background-color: transparent; }"
        )

        edit = QLineEdit(self.subtasks_containers[goal_index])
        edit.setPlaceholderText("New subtask…")

        row.addWidget(circle)
        row.addWidget(chk)
        row.addWidget(edit, 1)
        layout.addLayout(row)

        # Keep CircleIndicator and checkbox visually in sync
        chk.toggled.connect(lambda checked, circ=circle: circ.set_completed(checked))

        # Autosave when new subtask is modified
        chk.toggled.connect(self._auto_save)
        edit.textChanged.connect(self._auto_save)
        circle.clicked.connect(lambda _=False, c=chk: c.toggle())

    def _on_toggle_section(self, checked: bool, widget: QWidget, button: QToolButton) -> None:
        widget.setVisible(checked)
        button.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)

    def _on_delete_goal(self, index: int) -> None:
        """Clear a goal card (text, completion, subtasks, reflection, metadata)."""

        if self._current_goals is None:
            month = self._combo_month_value()
            self._current_goals = load_month_goals(month)
        goals = self._current_goals

        if index < 0 or index >= 3:
            return

        # Ask for confirmation before wiping the goal.
        if goals.archived:
            return
        reply = QMessageBox.question(
            self,
            "Clear goal",
            "Clear this goal, including subtasks and reflection?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _pad(lst, default):
            lst = list(lst)
            while len(lst) < 3:
                lst.append(default)
            return lst

        goals.goals = _pad(goals.goals, "")
        goals.completed = _pad(goals.completed, False)
        goals.categories = _pad(goals.categories, "General")
        goals.reflections = _pad(goals.reflections, "")
        goals.subtasks = _pad(goals.subtasks, [])
        goals.subtasks_done = _pad(goals.subtasks_done, [])
        goals.created_at = _pad(goals.created_at, "")
        goals.completed_at = _pad(goals.completed_at, "")

        goals.goals[index] = ""
        goals.completed[index] = False
        goals.categories[index] = "General"
        goals.reflections[index] = ""
        goals.subtasks[index] = []
        goals.subtasks_done[index] = []
        goals.created_at[index] = ""
        goals.completed_at[index] = ""

        self.goal_edits[index].clear()
        self.goal_checks[index].setChecked(False)
        cat_idx = self.category_combos[index].findText("General")
        self.category_combos[index].setCurrentIndex(cat_idx if cat_idx >= 0 else 0)
        self.reflection_edits[index].clear()

        layout = self.subtasks_layouts[index]
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        save_month_goals(goals, source="goals_view_clear")
        self._update_progress_label()
        self._update_card_styles()
