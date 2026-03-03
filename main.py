"""
main.py - Aplicación Island Window
Una ventana flotante tipo "Dynamic Island" con diseño modular
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton,
                               QHBoxLayout, QGraphicsDropShadowEffect,
                               QMenu, QSystemTrayIcon)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QPainterPath,
                           QRegion, QIcon)
from chat_panel import ChatPopup
from ui_utils import create_icon_button, create_svg_icon

import config
import icons


class IslandWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.initUI()

    def initUI(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Tamaño de la ventana desde config
        self.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # Posicionar en la parte superior central
        self.center_window()

        # Layout principal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(
            config.LAYOUT_MARGIN_HORIZONTAL,
            config.LAYOUT_MARGIN_VERTICAL,
            config.LAYOUT_MARGIN_HORIZONTAL,
            config.LAYOUT_MARGIN_VERTICAL
        )
        main_layout.setSpacing(config.BUTTON_SPACING)

        self.main_layout = main_layout

        # Crear botones con iconos
        self.button1 = create_icon_button(icons.get_chat_icon(), "GradientButton", "chat", self.on_button_clicked)
        self.button2 = create_icon_button(icons.get_clock_icon(), "OutlineButton", "lista", self.on_button_clicked)
        self.button3 = create_icon_button(icons.get_sparkles_icon(), "OutlineButton", "macros", self.on_button_clicked)

        main_layout.addWidget(self.button1)
        main_layout.addWidget(self.button2)
        main_layout.addWidget(self.button3)

        # Espaciador
        main_layout.addSpacing(10)

        # Botón de menú
        self.menu_button = self.create_menu_button()
        main_layout.addWidget(self.menu_button)

        self.setLayout(main_layout)

        # Aplicar sombra
        self.apply_shadow()

        self.tray_icon = QSystemTrayIcon(self)
        icon_pixmap = create_svg_icon(icons.get_chat_icon()).pixmap(64, 64)
        self.tray_icon.setIcon(QIcon(icon_pixmap))
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Mostrar Island")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Salir por completo")
        quit_action.triggered.connect(QApplication.instance().quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def center_window(self):
        """Centra la ventana en la parte superior de la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - config.WINDOW_WIDTH) // 2
        y = config.WINDOW_TOP_MARGIN
        self.move(x, y)

    def create_menu_button(self):
        """Crea el botón de menú con 3 puntos verticales"""
        button = QPushButton()
        button.setFixedSize(config.MENU_BUTTON_WIDTH, config.BUTTON_SIZE)
        button.setProperty("class", "MenuButton")
        button.setText("⋮")
        button.clicked.connect(self.on_menu_clicked)
        return button

    def apply_shadow(self):
        """Aplica el efecto de sombra a la ventana"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(config.SHADOW_BLUR_RADIUS)
        shadow.setXOffset(config.SHADOW_OFFSET_X)
        shadow.setYOffset(config.SHADOW_OFFSET_Y)
        shadow.setColor(QColor(*config.SHADOW_COLOR))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        """Dibuja el fondo de la ventana con forma de píldora"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Ajustar el rectángulo para la sombra
        rect = self.rect().adjusted(8, 8, -8, -8)
        radius = rect.height() / 2

        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), radius, radius)

        painter.setBrush(QBrush(QColor(*config.BACKGROUND_COLOR)))
        painter.setPen(QPen(QColor(*config.BORDER_COLOR), 1.5))
        painter.drawPath(path)

        inner_path = QPainterPath()
        inner_rect = rect.adjusted(1, 1, -1, -1)
        inner_path.addRoundedRect(
            inner_rect.x(), inner_rect.y(),
            inner_rect.width(), inner_rect.height(),
            radius - 1, radius - 1
        )
        painter.setPen(QPen(QColor(*config.INNER_BORDER_COLOR), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(inner_path)

        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def mousePressEvent(self, event):
        """Permite arrastrar la ventana"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Mueve la ventana mientras se arrastra"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def on_button_clicked(self, button_name):
        """Maneja los clics en los botones principales"""
        print(f"Botón presionado: {button_name}")

        if button_name == "chat":
            if hasattr(self, 'chat_window') and self.chat_window.isVisible():
                self.chat_window.hide()
            else:
                if not hasattr(self, 'chat_window') or not self.chat_window:
                    self.chat_window = ChatPopup(self)
                container = self.main_layout.parentWidget()
                if container is None:
                    container = self

                menu_width = self.chat_window.width()

                container_rect = container.rect()

                target_x = container.mapToGlobal(container_rect.center()).x() - (menu_width // 2)
                target_y = container.mapToGlobal(container_rect.bottomLeft()).y()

                self.chat_window.move(target_x, target_y)
                self.chat_window.show()
                self.chat_window.input_field.setFocus()

    def on_menu_clicked(self):
        """Muestra menú contextual"""
        menu = QMenu(self)

        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)

        close_action = menu.addAction("Minimizar")
        close_action.triggered.connect(self.close)

        exit_action = menu.addAction("Salir")
        exit_action.triggered.connect(QApplication.instance().quit)

        menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().center()) - QPoint(menu.sizeHint().width() // 2, (-self.menu_button.height() - 20) // 2))

def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = IslandWindow()
    window.show()

    style_path = os.path.join(os.path.dirname(__file__), config.STYLES_FILE)
    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())

    print("Aplicación Island iniciada")

    sys.exit(app.exec())

if __name__ == '__main__':
    main()