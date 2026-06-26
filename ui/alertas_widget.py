"""Aba/painel de alertas (calibração e empréstimos atrasados)."""
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core import alerts
from core.logger import get_logger

logger = get_logger(__name__)


class AlertasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._montar_ui()
        self.carregar()

    def _montar_ui(self):
        layout = QVBoxLayout(self)

        cabecalho = QHBoxLayout()
        self.label_contagem = QLabel("0 alertas")
        self.label_contagem.setStyleSheet("font-weight: bold;")
        cabecalho.addWidget(self.label_contagem)
        cabecalho.addStretch()
        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self.carregar)
        cabecalho.addWidget(botao_atualizar)
        layout.addLayout(cabecalho)

        self.tabela = QTableWidget(0, 2)
        self.tabela.setHorizontalHeaderLabels(["Nível", "Mensagem"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela)

    def carregar(self) -> list[alerts.Alerta]:
        lista = alerts.calcular_alertas()
        self.tabela.setRowCount(len(lista))
        for i, alerta in enumerate(lista):
            self.tabela.setItem(i, 0, QTableWidgetItem(alerta.nivel.upper()))
            self.tabela.setItem(i, 1, QTableWidgetItem(alerta.mensagem))
        self.label_contagem.setText(f"{len(lista)} alerta(s)")
        return lista
