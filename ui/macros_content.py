from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QEvent
from core.db import get_all_macros, create_macro, update_macro_hotkey
import subprocess

class HotkeyBadge(QWidget):
    def __init__(self, macro_id, hotkey):
        super().__init__()
        self.macro_id = macro_id

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.badge = QPushButton()
        if hotkey:
            self.badge.setText(hotkey)
            self.badge.setProperty("class", "HotkeyBadge")
        else:
            self.badge.setText("+")
            self.badge.setProperty("class", "HotkeyBadge--empty")
        self.badge.clicked.connect(self._enter_edit)

        self.editor = QLineEdit()
        self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.editor.hide()
        self.editor.editingFinished.connect(self._confirm)
        self.editor.installEventFilter(self)

        layout.addWidget(self.badge)
        layout.addWidget(self.editor)

    def _enter_edit(self):
        texto_actual = self.badge.text()
        self.editor.setText("" if texto_actual == "+" else texto_actual)
        self.badge.hide()
        self.editor.show()
        self.editor.setFocus()
        self.editor.selectAll()
        print("Enter edit mode")

    def _confirm(self):
        nuevo = self.editor.text().strip()
        update_macro_hotkey(self.macro_id, nuevo or None)
        self.badge.setText(nuevo if nuevo else "+")
        clase = "HotkeyBadge" if nuevo else "HotkeyBadge--empty"
        self.badge.setProperty("class", clase)
        self.badge.style().unpolish(self.badge)
        self.editor.hide()
        self.badge.show()
        print("Confirming edit")

    def eventFilter(self, obj, event):
        if obj is self.editor and event.type() == QEvent.Type.FocusOut:
            QTimer.singleShot(0, self._confirm)
        print("Event filter")
        return super().eventFilter(obj, event)

class MacroRow(QFrame):
    def __init__(self, macro, on_execute):
        super().__init__()
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        nombre = QPushButton(macro["name"])
        nombre.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        nombre.setFlat(True)
        nombre.clicked.connect(on_execute)

        badge = HotkeyBadge(macro["id"], macro["hotkey"])
