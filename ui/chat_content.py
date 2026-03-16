import markdown as md

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QVBoxLayout, QScrollArea, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt, QTimer
from ui_utils import create_icon_button
from icons import get_send_icon, get_camera_icon, get_stop_icon
from core.db import create_conversation, add_message, get_messages, rename_conversation, get_conversation_name
from core.ai_worker import AIWorker

AI_BUBBLE_STYLE = """
    QTextEdit {
        background-color: #3a3a3f;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 8px 12px;
        font-size: 13px;
    }
    QScrollBar:horizontal {
        height: 6px;
        background: transparent;
    }
    QScrollBar::handle:horizontal {
        background: rgba(255,255,255,60);
        border-radius: 3px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
"""


class ChatContent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_id = None
        self._pending_render = False
        self._render_timer = QTimer()
        self._render_timer.setInterval(50)
        self._render_timer.timeout.connect(self._flush_render)
        self.init_ui()
        self._actualizar_nombre()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_conv_name = QLabel()
        self.lbl_conv_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_conv_name.setStyleSheet("color: rgba(255,255,255,100); font-size: 11px;")
        main_layout.addWidget(self.lbl_conv_name)

        new_chat_btn = QPushButton("+ Nueva conversación")
        new_chat_btn.setFixedHeight(28)
        new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_chat_btn.clicked.connect(self.nueva_conversacion)
        new_chat_btn.setStyleSheet("border-radius: 12px")
        main_layout.addWidget(new_chat_btn)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.messages_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        main_layout.addWidget(self.scroll_area)

        input_container = QHBoxLayout()
        input_container.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Hazme una pregunta...")
        self.input_field.setFixedHeight(45)
        self.input_field.setObjectName("ChatInput")
        self.input_field.returnPressed.connect(self.enviar_mensaje)

        self.btn_enviar = create_icon_button(get_send_icon(), "GradientButton", "enviar", self.enviar_mensaje)
        self.btn_enviar.setObjectName("BtnEnviar")

        self.btn_extra = create_icon_button(
            get_camera_icon(), "GradientButton", "camara",
            lambda name: print(f"Acción: {name}")
        )
        self.btn_extra.setObjectName("BtnExtra")

        self.btn_stop = create_icon_button(get_stop_icon(), "GradientButton", "stop",
                                           lambda _: self.detener_generacion())
        self.btn_stop.setObjectName("BtnStop")
        self.btn_stop.setVisible(False)

        input_container.addWidget(self.input_field)
        input_container.addWidget(self.btn_stop)
        input_container.addWidget(self.btn_enviar)
        input_container.addWidget(self.btn_extra)
        main_layout.addLayout(input_container)

    def _actualizar_nombre(self):
        if self.conversation_id is None:
            self.lbl_conv_name.setText("")
            return
        self.lbl_conv_name.setText(get_conversation_name(self.conversation_id))

    def focus_input(self):
        self.input_field.setFocus()

    def _create_ai_bubble(self):
        bubble = QTextEdit()
        bubble.setReadOnly(True)
        bubble.setFixedWidth(260)
        bubble.setFixedHeight(36)
        bubble.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        bubble.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        bubble.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        bubble.setStyleSheet(AI_BUBBLE_STYLE)
        return bubble

    def _update_bubble_height(self, bubble):
        doc_height = int(bubble.document().size().height())
        bubble.setFixedHeight(doc_height + 20)

    def enviar_mensaje(self, name=None):
        texto = self.input_field.text().strip()
        if not texto:
            return
        if self.conversation_id is None:
            self.conversation_id = create_conversation()
            rename_conversation(self.conversation_id, texto[:45] + "..." if len(texto) > 45 else texto)
            self._actualizar_nombre()
        add_message(self.conversation_id, "user", texto)
        self.add_bubble(texto, "user")
        self.input_field.clear()
        self.input_field.setEnabled(False)

        self.current_response = ""
        self.ai_bubble = self._create_ai_bubble()
        self.messages_layout.addWidget(self.ai_bubble, alignment=Qt.AlignLeft)

        historial = get_messages(self.conversation_id)
        self.worker = AIWorker(historial)
        self.worker.chunk_received.connect(self.on_chunk)
        self.worker.completed.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.btn_stop.setVisible(True)
        self.btn_enviar.setVisible(False)
        self.worker.start()

    def detener_generacion(self):
        self._render_timer.stop()
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
        if hasattr(self, 'current_response') and self.current_response:
            add_message(self.conversation_id, "assistant", self.current_response)
            html = md.markdown(self.current_response, extensions=["fenced_code", "tables"])
            self.ai_bubble.setHtml(f'<div style="color:white;">{html}</div>')
            self._update_bubble_height(self.ai_bubble)
        self.btn_stop.setVisible(False)
        self.btn_enviar.setVisible(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def add_bubble(self, text, role):
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setFixedWidth(220)
        bubble.setContentsMargins(12, 8, 12, 8)
        bubble.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        if role == "user":
            bubble.setStyleSheet("background-color: #4A90E2; color: white; border-radius: 12px;")
        else:
            bubble.setStyleSheet("background-color: #3a3a3f; color: white; border-radius: 12px;")

        h = bubble.heightForWidth(220)
        if h > 0:
            bubble.setFixedHeight(h)

        if role == "user":
            self.messages_layout.addWidget(bubble, alignment=Qt.AlignRight)
        else:
            self.messages_layout.addWidget(bubble, alignment=Qt.AlignLeft)

        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def nueva_conversacion(self):
        self.conversation_id = None
        self._actualizar_nombre()
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _flush_render(self):
        if self._pending_render:
            self.ai_bubble.setPlainText(self.current_response)
            self._update_bubble_height(self.ai_bubble)
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )
            self._pending_render = False
        else:
            self._render_timer.stop()

    def on_chunk(self, text):
        self.current_response += text
        self._pending_render = True
        if not self._render_timer.isActive():
            self._render_timer.start()

    def on_finished(self):
        self._render_timer.stop()
        add_message(self.conversation_id, "assistant", self.current_response)
        html = md.markdown(self.current_response, extensions=["fenced_code", "tables"])
        self.ai_bubble.setHtml(f'<div style="color:white;">{html}</div>')
        self._update_bubble_height(self.ai_bubble)
        self.btn_stop.setVisible(False)
        self.btn_enviar.setVisible(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def on_error(self, error_msg):
        self.ai_bubble.setPlainText(f"Error: {error_msg}")
        self._update_bubble_height(self.ai_bubble)
        self.btn_stop.setVisible(False)
        self.btn_enviar.setVisible(True)
        self.input_field.setEnabled(True)
