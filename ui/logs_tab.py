"""Aba de auditoria (somente admin): histórico de ações registradas no sistema."""
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core import audit_log, excel_db
from core.logger import get_logger

logger = get_logger(__name__)

COLUNAS_EXIBIDAS = [
    ("timestamp", "Data/Hora"),
    ("usuario", "Usuário"),
    ("acao", "Ação"),
    ("detalhe", "Detalhe"),
]


class LogsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._linhas: list[dict] = []
        self._montar_ui()
        self.carregar()

    def _montar_ui(self):
        layout = QVBoxLayout(self)

        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Buscar:"))
        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Usuário, ação ou detalhe...")
        self.campo_busca.textChanged.connect(self.carregar)
        filtros.addWidget(self.campo_busca)
        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self.carregar)
        filtros.addWidget(botao_atualizar)
        layout.addLayout(filtros)

        self.tabela = QTableWidget(0, len(COLUNAS_EXIBIDAS))
        self.tabela.setHorizontalHeaderLabels([rotulo for _, rotulo in COLUNAS_EXIBIDAS])
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela)

    def carregar(self):
        try:
            todos = audit_log.listar()
        except excel_db.ArquivoEmUsoError as exc:
            QMessageBox.warning(self, "Logs", str(exc))
            return

        busca = self.campo_busca.text().strip().lower()
        self._linhas = [
            linha for linha in todos
            if not busca or busca in " ".join(str(v) for v in linha.values()).lower()
        ]
        self._linhas.sort(key=lambda r: str(r.get("timestamp", "")), reverse=True)

        self.tabela.setRowCount(len(self._linhas))
        for i, linha in enumerate(self._linhas):
            for j, (coluna, _) in enumerate(COLUNAS_EXIBIDAS):
                self.tabela.setItem(i, j, QTableWidgetItem(str(linha.get(coluna, ""))))
