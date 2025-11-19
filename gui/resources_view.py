from __future__ import annotations

import uuid
import webbrowser
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.themes import ThemeColors

from aqt import mw
from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QLabel,
    Qt,
    QComboBox,
    QHeaderView,
    QColor,
)

from ..core.logic_resources import load_resources, save_resources
from ..core.models import ResourceItem


class ResourceDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, item: Optional[ResourceItem] = None, theme_colors: Optional['ThemeColors'] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Resource")
        self._theme_colors = theme_colors

        layout = QFormLayout(self)

        # Predefined types mapped to icons in _icon_for_type; keep editable.
        self.type_edit = QComboBox(self)
        self.type_edit.setEditable(True)
        self.type_edit.addItems([
            "Book",
            "Podcast",
            "Video",
            "App",
            "Website",
            "Other",
        ])
        self.name_edit = QLineEdit(self)
        self.link_edit = QLineEdit(self)
        self.notes_edit = QTextEdit(self)
        self.deck_combo = QComboBox(self)
        self.deck_combo.setEditable(True)
        self._populate_decks()
        self.tags_edit = QLineEdit(self)
        self.tags_edit.setPlaceholderText(
            "Tags (comma-separated: listening, JLPT, grammar)"
        )

        layout.addRow("Type", self.type_edit)
        layout.addRow("Name", self.name_edit)
        layout.addRow("Link", self.link_edit)
        layout.addRow("Notes", self.notes_edit)
        layout.addRow("Deck", self.deck_combo)
        layout.addRow("Tags", self.tags_edit)

        button_row = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)
        layout.addRow(button_row)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self._item_id: Optional[str] = None

        if item is not None:
            self._item_id = item.id
            # Try to select existing type; fall back to free text if custom.
            idx = self.type_edit.findText(item.type, Qt.MatchFlag.MatchFixedString)
            if idx >= 0:
                self.type_edit.setCurrentIndex(idx)
            else:
                self.type_edit.setEditText(item.type)
            self.name_edit.setText(item.name)
            self.link_edit.setText(item.link)
            self.notes_edit.setPlainText(item.notes)
            self.deck_combo.setEditText(item.deck_name or "")
            if item.tags:
                self.tags_edit.setText(", ".join(tag for tag in item.tags if tag.strip()))
        
        # Apply theme styling
        if self._theme_colors:
            self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply theme colors to dialog components."""
        if not self._theme_colors:
            return
        
        colors = self._theme_colors
        
        # Style the dialog background
        self.setStyleSheet(
            f"QDialog {{"
            f"  background-color: {colors.background};"
            f"  color: {colors.text};"
            f"}}"
            f"QLabel {{"
            f"  color: {colors.text};"
            f"}}"
            f"QLineEdit {{"
            f"  border: 1px solid {colors.input_border};"
            f"  border-radius: 3px;"
            f"  padding: 4px 8px;"
            f"  background-color: {colors.input_bg};"
            f"  color: {colors.input_text};"
            f"}}"
            f"QLineEdit:focus {{"
            f"  border-color: {colors.input_focus_border};"
            f"}}"
            f"QTextEdit {{"
            f"  border: 1px solid {colors.input_border};"
            f"  border-radius: 3px;"
            f"  padding: 4px 8px;"
            f"  background-color: {colors.input_bg};"
            f"  color: {colors.input_text};"
            f"}}"
            f"QTextEdit:focus {{"
            f"  border-color: {colors.input_focus_border};"
            f"}}"
            f"QComboBox {{"
            f"  border: 1px solid {colors.input_border};"
            f"  border-radius: 3px;"
            f"  padding: 4px 8px;"
            f"  background-color: {colors.input_bg};"
            f"  color: {colors.input_text};"
            f"}}"
            f"QComboBox:hover {{"
            f"  border-color: {colors.input_focus_border};"
            f"}}"
            f"QComboBox::drop-down {{"
            f"  border: none;"
            f"}}"
            f"QComboBox::down-arrow {{"
            f"  image: none;"
            f"  border-left: 4px solid transparent;"
            f"  border-right: 4px solid transparent;"
            f"  border-top: 5px solid {colors.text};"
            f"}}"
            f"QComboBox QAbstractItemView {{"
            f"  background-color: {colors.input_bg};"
            f"  color: {colors.input_text};"
            f"  border: 1px solid {colors.input_border};"
            f"  selection-background-color: {colors.accent};"
            f"  selection-color: {colors.background};"
            f"}}"
            f"QComboBox QAbstractItemView::item {{"
            f"  background-color: {colors.input_bg};"
            f"  color: {colors.input_text};"
            f"  padding: 4px;"
            f"}}"
            f"QComboBox QAbstractItemView::item:selected {{"
            f"  background-color: {colors.accent};"
            f"  color: {colors.background};"
            f"}}"
            f"QPushButton {{"
            f"  border: 1px solid {colors.button_border};"
            f"  border-radius: 4px;"
            f"  padding: 6px 12px;"
            f"  background-color: {colors.button_bg};"
            f"  color: {colors.button_text};"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {colors.button_hover_bg};"
            f"  border-color: {colors.button_hover_border};"
            f"}}"
        )

    def to_item(self) -> ResourceItem:
        item_id = self._item_id or str(uuid.uuid4())
        raw_tags = self.tags_edit.text() or ""
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
        return ResourceItem(
            id=item_id,
            type=self.type_edit.currentText(),
            name=self.name_edit.text(),
            link=self.link_edit.text(),
            notes=self.notes_edit.toPlainText(),
            deck_name=(self.deck_combo.currentText() or "").strip() or None,
            tags=tags,
        )

    def _populate_decks(self) -> None:
        """Populate deck dropdown with installed Anki decks.

        Keeps the list simple (names only) and falls back silently if the
        collection is not available, so the field remains usable as free text.
        """

        self.deck_combo.clear()
        try:
            if mw is None or mw.col is None:
                return
            for deck in mw.col.decks.all():
                name = str(deck.get("name", "")).strip()
                if name:
                    self.deck_combo.addItem(name)
        except Exception:
            # If anything goes wrong, leave the combo empty; user can still
            # type a deck name manually.
            return


class ResourcesView(QWidget):
    # Columns: Icon, Name, Link, Deck, Tags
    headers = ["", "Name", "Link", "Deck", "Tags"]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Theme colors
        self._theme_colors: Optional['ThemeColors'] = None

        layout = QVBoxLayout(self)

        # Main container for search + table.
        container = QWidget(self)
        container_layout = QVBoxLayout(container)

        # Search / filter bar
        search_row = QHBoxLayout()
        search_label = QLabel("Search:", self)
        self.search_edit = QLineEdit(self)
        self.search_edit.setPlaceholderText(
            "Filter by name, type, deck, or tags (use tag:JLPT for tags)"
        )
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_edit, 1)
        container_layout.addLayout(search_row)

        self.table = QTableWidget(self)
        # Slightly larger font for better readability in the resources list.
        table_font = self.table.font()
        if table_font.pointSize() > 0:
            table_font.setPointSize(table_font.pointSize() + 2)
            self.table.setFont(table_font)
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        # Let the table use the parent/Anki background instead of its own and
        # remove all visible borders/grid so it blends with Anki.
        self.table.setShowGrid(False)
        self.table.setStyleSheet(
            "QTableWidget { background-color: transparent; border: none; }"  # table frame
            "QTableWidget::item { border: none; }"  # individual cells
            "QHeaderView::section { background-color: transparent; border: none; }"  # header cells
        )
        # Hide row numbers; only show data columns.
        self.table.verticalHeader().setVisible(False)
        # Enable hover feedback for clickable link/deck cells.
        self.table.setMouseTracking(True)
        # Column sizing: icon is narrow, Name fills remaining space, others
        # keep content-based widths.
        fm = self.fontMetrics()
        icon_width = fm.horizontalAdvance("MMM") + 8
        link_width = fm.horizontalAdvance("https://example.com") + 16
        deck_width = fm.horizontalAdvance("My Deck Name") + 16
        tags_width = fm.horizontalAdvance("tag1, tag2, tag3") + 16

        self.table.setColumnWidth(0, icon_width)
        self.table.setColumnWidth(2, link_width)
        self.table.setColumnWidth(3, deck_width)
        self.table.setColumnWidth(4, tags_width)

        header = self.table.horizontalHeader()
        # Icon, Link, Deck, Tags columns fixed
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        # Name column stretches to fill remaining space
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        container_layout.addWidget(self.table)

        layout.addWidget(container)

        buttons = QHBoxLayout()
        self.add_button = QPushButton("Add", self)
        self.edit_button = QPushButton("Edit", self)
        self.delete_button = QPushButton("Delete", self)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        layout.addLayout(buttons)

        self.items: List[ResourceItem] = []  # full list
        self._row_ids: List[str] = []  # map table row -> ResourceItem.id
        self._hovered_link_cell: Optional[tuple[int, int]] = None

        self.add_button.clicked.connect(self._on_add)
        self.edit_button.clicked.connect(self._on_edit)
        self.delete_button.clicked.connect(self._on_delete)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.cellEntered.connect(self._on_cell_entered)
        self.search_edit.textChanged.connect(self._on_search_changed)

        self._load_items()

    def _load_items(self) -> None:
        raw = load_resources()
        self.items = []
        for obj in raw:
            try:
                tags_raw = obj.get("tags") or []
                if not isinstance(tags_raw, list):
                    tags_raw = []
                tags = [str(t) for t in tags_raw if str(t).strip()]
                item = ResourceItem(
                    id=str(obj.get("id", "")),
                    type=str(obj.get("type", "")),
                    name=str(obj.get("name", "")),
                    link=str(obj.get("link", "")),
                    notes=str(obj.get("notes", "")),
                    deck_name=obj.get("deck_name"),
                    tags=tags,
                )
            except Exception:
                continue
            self.items.append(item)
        self._refresh_table(self.items)

    def _refresh_table(self, items: List[ResourceItem]) -> None:
        self.table.setRowCount(len(items))
        self._row_ids = []
        for row, item in enumerate(items):
            icon = self._icon_for_type(item.type)
            tags_str = ", ".join(item.tags)
            display_tags = tags_str
            if len(tags_str) > 40:
                display_tags = tags_str[:37] + "…"

            # Icon, Name, Link, Deck, Tags
            values = [
                icon,
                item.name,
                item.link,
                item.deck_name or "",
                display_tags,
            ]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                # Store id so selection/edit/delete still work after filtering/sorting.
                cell.setData(Qt.ItemDataRole.UserRole, item.id)
                if col == 0:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    # Type is only visible as tooltip on the icon column.
                    cell.setToolTip(item.type or "")
                elif col == 2 and item.link.strip():
                    # Link column is clickable, use a custom blue.
                    cell.setForeground(QColor("#58a6ff"))
                elif col == 3 and (item.deck_name or "").strip():
                    # Deck column clickable, use the same custom blue.
                    cell.setForeground(QColor("#58a6ff"))
                if col == 4 and tags_str:
                    cell.setToolTip(tags_str)
                self.table.setItem(row, col, cell)

            self._row_ids.append(item.id)

    def _on_add(self) -> None:
        dialog = ResourceDialog(self, theme_colors=self._theme_colors)
        if dialog.exec():
            item = dialog.to_item()
            self.items.append(item)
            save_resources(self.items)
            self._apply_filter_and_refresh()

    def _selected_index(self) -> Optional[int]:
        """Return the index into self.items for the currently selected row.

        This delegates to _index_for_row so that Edit/Delete buttons use the
        same row→item mapping as double-clicks and single-click handlers.
        """

        row = self.table.currentRow()
        return self._index_for_row(row)

    def _on_edit(self) -> None:
        index = self._selected_index()
        if index is None:
            return
        item = self.items[index]
        dialog = ResourceDialog(self, item, theme_colors=self._theme_colors)
        if dialog.exec():
            self.items[index] = dialog.to_item()
            save_resources(self.items)
            self._apply_filter_and_refresh()

    def _on_delete(self) -> None:
        index = self._selected_index()
        if index is None:
            return
        del self.items[index]
        save_resources(self.items)
        self._apply_filter_and_refresh()

    def _on_cell_double_clicked(self, row: int, column: int) -> None:
        # Double-click on Name opens link when available; Deck opens deck.
        item_index = self._index_for_row(row)
        if item_index is None:
            return
        resource = self.items[item_index]

        if column in (1, 2) and resource.link.strip():
            webbrowser.open(resource.link)
            return
        if column == 3 and (resource.deck_name or "").strip():
            self._open_deck(resource.deck_name or "")
            return

        # Fallback: edit dialog
        self.table.selectRow(row)
        self._on_edit()

    def _on_cell_clicked(self, row: int, column: int) -> None:
        # Single-click on Link or Deck column opens the URL or deck.
        item_index = self._index_for_row(row)
        if item_index is None:
            return
        resource = self.items[item_index]

        if column == 2 and resource.link.strip():
            webbrowser.open(resource.link)
            return
        if column == 3 and (resource.deck_name or "").strip():
            self._open_deck(resource.deck_name or "")

    def _on_cell_entered(self, row: int, column: int) -> None:
        """Hover feedback for Link and Deck columns.

        When the mouse is over a clickable Link/Deck cell, underline the text
        and show a pointing-hand cursor. Reset styling when leaving.
        """

        # Reset previous hovered cell, if any.
        if self._hovered_link_cell is not None:
            prev_row, prev_col = self._hovered_link_cell
            prev_item = self.table.item(prev_row, prev_col)
            if prev_item is not None:
                prev_font = prev_item.font()
                prev_font.setUnderline(False)
                prev_item.setFont(prev_font)
        self._hovered_link_cell = None
        self.table.setCursor(Qt.CursorShape.ArrowCursor)

        item_index = self._index_for_row(row)
        if item_index is None:
            return
        resource = self.items[item_index]

        is_link_cell = column == 2 and resource.link.strip()
        is_deck_cell = column == 3 and (resource.deck_name or "").strip()
        if not (is_link_cell or is_deck_cell):
            return

        cell = self.table.item(row, column)
        if cell is None:
            return

        font = cell.font()
        font.setUnderline(True)
        cell.setFont(font)
        self._hovered_link_cell = (row, column)
        self.table.setCursor(Qt.CursorShape.PointingHandCursor)

    def select_row(self, index: int) -> None:
        if 0 <= index < self.table.rowCount():
            self.table.selectRow(index)

    # filtering / helpers -------------------------------------------------

    def _on_search_changed(self, _text: str) -> None:
        self._apply_filter_and_refresh()

    def _apply_filter_and_refresh(self) -> None:
        query = (self.search_edit.text() or "").strip().lower()
        if not query:
            filtered = list(self.items)
        else:
            tag_filter = None
            if query.startswith("tag:"):
                tag_filter = query[4:].strip()

            filtered = []
            for item in self.items:
                name = item.name.lower()
                type_ = item.type.lower()
                deck = (item.deck_name or "").lower()
                tags_str = ",".join(item.tags).lower()

                if tag_filter is not None:
                    if tag_filter and tag_filter in tags_str:
                        filtered.append(item)
                    continue

                haystack = " ".join([name, type_, deck, tags_str])
                if query in haystack:
                    filtered.append(item)

        self._refresh_table(filtered)

    def _index_for_row(self, row: int) -> Optional[int]:
        if row < 0 or row >= self.table.rowCount():
            return None
        cell = self.table.item(row, 1)  # Name column
        if cell is None:
            return None
        res_id = cell.data(Qt.ItemDataRole.UserRole)
        if not res_id:
            return None
        for idx, item in enumerate(self.items):
            if item.id == res_id:
                return idx
        return None

    def _icon_for_type(self, type_str: str) -> str:
        t = (type_str or "").strip().lower()
        if t == "book":
            return "📘"
        if t == "podcast":
            return "🎧"
        if t == "video":
            return "🎬"
        if t == "app":
            return "📱"
        if t == "website":
            return "🌐"
        return "📌"

    def _open_deck(self, deck_name: str) -> None:
        try:
            deck = mw.col.decks.byName(deck_name)
            if not deck:
                return
            mw.col.decks.select(deck["id"])
            mw.reset()
        except Exception:
            # Fail silently if deck cannot be opened.
            return

    def apply_theme(self, colors: 'ThemeColors') -> None:
        """Apply theme colors to resources view components."""
        self._theme_colors = colors
        
        # Update search input styling
        if hasattr(self, 'search_edit'):
            self.search_edit.setStyleSheet(
                f"QLineEdit {{"
                f"  border: 1px solid {colors.input_border};"
                f"  border-radius: 4px;"
                f"  padding: 4px 8px;"
                f"  background-color: {colors.input_bg};"
                f"  color: {colors.input_text};"
                f"}}"
                f"QLineEdit:focus {{"
                f"  border-color: {colors.input_focus_border};"
                f"}}"
            )
        
        # Update table styling
        if hasattr(self, 'table'):
            self.table.setStyleSheet(
                f"QTableWidget {{"
                f"  background-color: transparent;"
                f"  border: none;"
                f"  color: {colors.text};"
                f"}}"
                f"QTableWidget::item {{"
                f"  border: none;"
                f"  padding: 4px;"
                f"}}"
                f"QTableWidget::item:selected {{"
                f"  background-color: {colors.accent};"
                f"  color: {colors.tab_bg};"
                f"}}"
                f"QHeaderView::section {{"
                f"  background-color: {colors.resource_table_header_bg};"
                f"  border: none;"
                f"  padding: 4px;"
                f"  color: {colors.text_secondary};"
                f"  font-weight: bold;"
                f"}}"
            )
        
        # Update buttons
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(
                f"QPushButton {{"
                f"  border: 1px solid {colors.button_border};"
                f"  border-radius: 4px;"
                f"  padding: 6px 12px;"
                f"  background-color: {colors.button_bg};"
                f"  color: {colors.button_text};"
                f"}}"
                f"QPushButton:hover {{"
                f"  background-color: {colors.button_hover_bg};"
                f"  border-color: {colors.button_hover_border};"
                f"}}"
            )
