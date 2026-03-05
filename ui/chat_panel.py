import config

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget, QScrollArea, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath
from ui_utils import create_icon_button
from icons import get_send_icon, get_camera_icon
from core.db import create_conversation, add_message, get_messages
from core.ai_worker import AIWorker



class ChatPopup(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(320, 450)  # Dimensiones más cercanas a un chat real

        self.conversation_id = create_conversation()

        self.init_ui()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Contenedor interno del scroll (aquí se añadirán las burbujas)
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)

        # Boton de nueva conversacion
        new_chat_btn = QPushButton("+ Nueva conversación")
        new_chat_btn.setFixedHeight(28)
        new_chat_btn.clicked.connect(self.nueva_conversacion)
        main_layout.addWidget(new_chat_btn)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.messages_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        main_layout.addWidget(self.scroll_area)

        # Contenedor de la barra de entrada (Input Bar)
        input_container = QHBoxLayout()
        input_container.setSpacing(10)

        # Configuración del Input Field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Hazme una pregunta...")
        self.input_field.setFixedHeight(45)
        self.input_field.setObjectName("ChatInput")

        # Creamos los botones usando tu utilidad externa
        # Pasamos self.enviar_mensaje como callback para el botón de enviar
        self.btn_enviar = create_icon_button(
            get_send_icon(),
            "GradientButton",
            "enviar",
            self.enviar_mensaje
        )
        self.btn_enviar.setObjectName("BtnEnviar")

        self.btn_extra = create_icon_button(
            get_camera_icon(),
            "GradientButton",
            "camara",
            lambda name: print(f"Acción: {name}")
        )
        self.btn_extra.setObjectName("BtnExtra")

        # Organizar el layout
        input_container.addWidget(self.input_field)
        input_container.addWidget(self.btn_enviar)
        input_container.addWidget(self.btn_extra)

        main_layout.addLayout(input_container)

    def enviar_mensaje(self, name=None):
        texto = self.input_field.text().strip()
        if not texto:
            return
        # mostrar y guardar mensaje de usuario
        add_message(self.conversation_id, "user", texto)
        self.add_bubble(texto, "user")
        self.input_field.clear()
        self.input_field.setEnabled(False)

        # crear burbuja vacia
        self.current_response = ""
        self.ai_bubble = QLabel("")
        self.ai_bubble.setWordWrap(True)
        self.ai_bubble.setMaximumWidth(220)
        self.ai_bubble.setStyleSheet("""
          background-color: #3a3a3f;
          color: white;
          border-radius: 12px;
          padding: 8px 12px;
        """)
        self.messages_layout.addWidget(self.ai_bubble, alignment=Qt.AlignLeft)

        # lanzar hilo con el historial de chat
        historial = get_messages(self.conversation_id)
        self.worker = AIWorker(historial)
        self.worker.chunk_received.connect(self.on_chunk)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fondo oscuro principal
        rect = self.rect().adjusted(2, 2, -2, -2)
        radius = 25
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # Usamos un color oscuro sólido similar al de la imagen
        painter.setBrush(QBrush(QColor(*config.BACKGROUND_COLOR)))
        painter.setPen(QPen(QColor(*config.BORDER_COLOR), 1.5))
        painter.drawPath(path)


    def add_bubble(self, text, role):
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(220)

        if role == "user":
            bubble.setStyleSheet("""
                  background-color: #4A90E2;
                  color: white;
                  border-radius: 12px;
                  padding: 8px 12px;
              """)
            self.messages_layout.addWidget(bubble, alignment=Qt.AlignRight)
        else:
            bubble.setStyleSheet("""
                  background-color: #3a3a3f;
                  color: white;
                  border-radius: 12px;
                  padding: 8px 12px;
              """)
            self.messages_layout.addWidget(bubble, alignment=Qt.AlignLeft)

        # Scroll automático al último mensaje
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def nueva_conversacion(self):
        self.conversation_id = create_conversation()
        # Limpiar burbujas del scroll
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


    def on_chunk(self, text):
        self.current_response += text
        self.ai_bubble.setText(self.current_response)
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def on_finished(self):
        add_message(self.conversation_id, "assistant", self.current_response)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def on_error(self, error_msg):
        self.ai_bubble.setText(f"Error: {error_msg}")
        self.input_field.setEnabled(True)
