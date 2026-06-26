"""Aba de empréstimos e devoluções."""
from datetime import date

from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import config
from core import excel_db
from core.auth import Sessao
from core.logger import get_logger
from core.models import Emprestimo, Equipamento, StatusEmprestimo, StatusEquipamento

logger = get_logger(__name__)

COLUNAS_EXIBIDAS = [
    ("id", "ID"),
    ("equipamento_codigo", "Equipamento"),
    ("responsavel", "Responsável"),
    ("data_retirada", "Retirada"),
    ("data_prevista_devolucao", "Devolução prevista"),
    ("data_devolucao_real", "Devolução real"),
    ("status", "Status"),
]


class EmprestimosTab(QWidget):
    def __init__(self):
        super().__init__()
        self._linhas: list[dict] = []
        self._montar_ui()
        self.carregar()

    def _montar_ui(self):
        layout = QVBoxLayout(self)

        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Status:"))
        self.combo_status = QComboBox()
        self.combo_status.addItem("Todos")
        self.combo_status.addItems(StatusEmprestimo.TODOS)
        self.combo_status.setCurrentText(StatusEmprestimo.EM_ANDAMENTO)
        self.combo_status.currentIndexChanged.connect(self.carregar)
        filtros.addWidget(self.combo_status)
        filtros.addStretch()
        layout.addLayout(filtros)

        self.tabela = QTableWidget(0, len(COLUNAS_EXIBIDAS))
        self.tabela.setHorizontalHeaderLabels([rotulo for _, rotulo in COLUNAS_EXIBIDAS])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabela)

        botoes = QHBoxLayout()
        self.botao_devolver = QPushButton("Devolver")
        self.botao_devolver.clicked.connect(self._devolver)
        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self.carregar)
        botoes.addWidget(self.botao_devolver)
        botoes.addStretch()
        botoes.addWidget(botao_atualizar)
        layout.addLayout(botoes)

    def carregar(self):
        try:
            todos = excel_db.read_all(config.EMPRESTIMOS_FILE, Emprestimo.colunas())
        except excel_db.ArquivoEmUsoError as exc:
            QMessageBox.warning(self, "Empréstimos", str(exc))
            return

        status_filtro = self.combo_status.currentText()
        self._linhas = [
            linha for linha in todos
            if status_filtro == "Todos" or linha.get("status") == status_filtro
        ]
        self._linhas.sort(key=lambda r: str(r.get("data_retirada", "")), reverse=True)

        self.tabela.setRowCount(len(self._linhas))
        for i, linha in enumerate(self._linhas):
            for j, (coluna, _) in enumerate(COLUNAS_EXIBIDAS):
                self.tabela.setItem(i, j, QTableWidgetItem(str(linha.get(coluna, ""))))

    def _linha_selecionada(self) -> dict | None:
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self._linhas):
            return None
        return self._linhas[linha]

    def _devolver(self):
        linha = self._linha_selecionada()
        if not linha:
            QMessageBox.information(self, "Empréstimos", "Selecione um empréstimo na lista.")
            return
        if linha.get("status") not in (StatusEmprestimo.EM_ANDAMENTO, StatusEmprestimo.ATRASADO):
            QMessageBox.warning(self, "Empréstimos", "Este empréstimo já foi devolvido.")
            return

        resposta = QMessageBox.question(
            self, "Devolver", f"Confirmar devolução do equipamento {linha['equipamento_codigo']}?"
        )
        if resposta != QMessageBox.Yes:
            return

        try:
            excel_db.update_row(
                config.EMPRESTIMOS_FILE, Emprestimo.colunas(), "id", linha["id"],
                {
                    "data_devolucao_real": date.today().strftime("%Y-%m-%d"),
                    "status": StatusEmprestimo.DEVOLVIDO,
                },
            )
            excel_db.update_row(
                config.EQUIPAMENTOS_FILE, Equipamento.colunas(), "codigo", linha["equipamento_codigo"],
                {"status": StatusEquipamento.DISPONIVEL},
            )
        except excel_db.ArquivoEmUsoError as exc:
            QMessageBox.critical(self, "Empréstimos", str(exc))
            return

        logger.info(
            "Empréstimo devolvido: %s (equipamento %s) por %s",
            linha["id"], linha["equipamento_codigo"], Sessao.usuario_atual.login,
        )
        self.carregar()
