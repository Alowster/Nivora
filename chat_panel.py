import config

import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSvg import QSvgRenderer
from ui_utils import create_icon_button
from icons import get_send_icon, get_camera_icon

class ChatPopup(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(320, 450)  # Dimensiones más cercanas a un chat real

        self.init_ui()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Espacio flexible que empuja la barra de entrada hacia abajo
        main_layout.addStretch()

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
        if texto:
            print(f"Enviando mensaje: {texto}")
            self.input_field.clear()

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


    def set_svg_icon(button, svg_str):
        renderer = QSvgRenderer(svg_str.encode('utf-8'))
        pixmap = QPixmap(button.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        button.setIcon(QIcon(pixmap))
        button.setIconSize(QSize(20, 20))  # Ajusta el tamaño del icono dentro del botón