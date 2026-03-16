from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from core.db import get_all_conversations

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

class ListaContent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(15, 15, 15, 15)

        self.cargar_y_agrupar()
        self.init_ui()

    def init_ui(self):
        # Header del mes
        fila = QHBoxLayout()
        self.btn_anterior = QPushButton("<")
        self.btn_anterior.clicked.connect(self._mes_anterior)
        self.btn_anterior.setProperty("class", "NavButton")
        self.btn_anterior.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_mes = QLabel()
        self.lbl_mes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_siguiente = QPushButton(">")
        self.btn_siguiente.clicked.connect(self._mes_siguiente)
        self.btn_siguiente.setProperty("class", "NavButton")
        self.btn_siguiente.setCursor(Qt.CursorShape.PointingHandCursor)

        fila.addWidget(self.btn_anterior)
        fila.addWidget(self.lbl_mes)
        fila.addWidget(self.btn_siguiente)
        self.layout_principal.addLayout(fila)

        # Lista de conversaciones
        self.lista_layout = QVBoxLayout()
        self.lista_layout.setSpacing(4)
        self.layout_principal.addLayout(self.lista_layout)

        self.layout_principal.addStretch()

        self._actualizar_header()

    def cargar_y_agrupar(self):
        conversaciones = get_all_conversations()
        self._grupos = {}
        for conv in conversaciones:
            fecha = conv["created_at"][:7]
            anyo, mes = fecha.split("-")
            clave = (int(anyo), int(mes))
            self._grupos.setdefault(clave, []).append(conv)
        self._meses = sorted(self._grupos.keys(), reverse=True)
        self._mes_idx = 0

    def _actualizar_header(self):
        if not self._meses:
            self.lbl_mes.setText("Sin conversaciones")
            self.btn_anterior.setEnabled(False)
            self.btn_siguiente.setEnabled(False)
            return
        anyo, mes = self._meses[self._mes_idx]
        self.lbl_mes.setText(f"{MESES_ES[mes]} {anyo}")
        self.btn_anterior.setEnabled(self._mes_idx < len(self._meses) - 1)
        self.btn_siguiente.setEnabled(self._mes_idx > 0)
        self._mostrar_mes()

    def _mostrar_mes(self):
        while self.lista_layout.count():
            item = self.lista_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        convs = self._grupos[self._meses[self._mes_idx]]

        cot = 0
        for conv in convs:
            cot += 1
            if cot == 7:
                break

            btn = QPushButton(conv["name"])
            btn.setProperty("class", "ConvButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.lista_layout.addWidget(btn)

    def _mes_anterior(self):
        if self._mes_idx < len(self._meses) - 1:
            self._mes_idx += 1
            self._actualizar_header()

    def _mes_siguiente(self):
        if self._mes_idx > 0:
            self._mes_idx -= 1
            self._actualizar_header()
