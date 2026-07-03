"""Aba de cadastro/consulta de equipamentos."""
import uuid

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
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

import config
from core import audit_log, excel_db
from core.auth import Sessao
from core.logger import get_logger
from core.models import Emprestimo, Equipamento, StatusEmprestimo, StatusEquipamento
from ui.dialogs import EmprestimoDialog, EquipamentoDialog
from ui.pdf_helpers import gerar_ficha_pdf_interativo

logger = get_logger(__name__)

COLUNAS_EXIBIDAS = [
    ("codigo", "Instrumento"),
    ("grupo", "Grupo"),
    ("descricao", "Descrição"),
    ("numero_serie", "Nº Série"),
    ("fabricante", "Fabricante"),
    ("status", "Status"),
    ("localizacao", "Localização"),
    ("usuario_departamento", "Usuário"),
    ("modelo", "Modelo"),
]


class EquipamentosTab(QWidget):
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
        self.combo_status.addItems(StatusEquipamento.TODOS)
        self.combo_status.currentIndexChanged.connect(self.carregar)
        filtros.addWidget(self.combo_status)

        filtros.addWidget(QLabel("Buscar:"))
        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Código, descrição, série...")
        self.campo_busca.textChanged.connect(self.carregar)
        filtros.addWidget(self.campo_busca)
        layout.addLayout(filtros)

        self.tabela = QTableWidget(0, len(COLUNAS_EXIBIDAS))
        self.tabela.setHorizontalHeaderLabels([rotulo for _, rotulo in COLUNAS_EXIBIDAS])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabela)

        botoes = QHBoxLayout()
        self.botao_novo = QPushButton("Novo")
        self.botao_novo.clicked.connect(self._novo)
        self.botao_editar = QPushButton("Editar")
        self.botao_editar.clicked.connect(self._editar)
        self.botao_excluir = QPushButton("Excluir")
        self.botao_excluir.clicked.connect(self._excluir)
        self.botao_emprestar = QPushButton("Emprestar")
        self.botao_emprestar.clicked.connect(self._emprestar)
        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self.carregar)

        botoes.addWidget(self.botao_novo)
        botoes.addWidget(self.botao_editar)
        botoes.addWidget(self.botao_excluir)
        botoes.addWidget(self.botao_emprestar)
        botoes.addStretch()
        botoes.addWidget(botao_atualizar)
        layout.addLayout(botoes)

        is_admin = Sessao.is_admin()
        self.botao_novo.setVisible(is_admin)
        self.botao_editar.setVisible(is_admin)
        self.botao_excluir.setVisible(is_admin)

    def carregar(self):
        try:
            todos = excel_db.read_all(config.EQUIPAMENTOS_FILE, Equipamento.colunas())
        except excel_db.ArquivoEmUsoError as exc:
            QMessageBox.warning(self, "Equipamentos", str(exc))
            return

        status_filtro = self.combo_status.currentText()
        busca = self.campo_busca.text().strip().lower()

        self._linhas = []
        for linha in todos:
            if status_filtro != "Todos" and linha.get("status") != status_filtro:
                continue
            if busca:
                texto = " ".join(str(v) for v in linha.values()).lower()
                if busca not in texto:
                    continue
            self._linhas.append(linha)

        self.tabela.setRowCount(len(self._linhas))
        for i, linha in enumerate(self._linhas):
            for j, (coluna, _) in enumerate(COLUNAS_EXIBIDAS):
                self.tabela.setItem(i, j, QTableWidgetItem(str(linha.get(coluna, ""))))

    def _linha_selecionada(self) -> dict | None:
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self._linhas):
            return None
        return self._linhas[linha]

    def _novo(self):
        dialogo = EquipamentoDialog(self)
        if dialogo.exec_() != QDialog.Accepted:
            return
        dados = dialogo.dados()
        if excel_db.find_one(config.EQUIPAMENTOS_FILE, Equipamento.colunas(), "codigo", dados["codigo"]):
            QMessageBox.warning(self, "Equipamentos", "Já existe um equipamento com esse código.")
            return
        try:
            excel_db.append_row(config.EQUIPAMENTOS_FILE, Equipamento.colunas(), dados)
        except excel_db.ArquivoEmUsoError as exc:
            QMessageBox.critical(self, "Equipamentos", str(exc))
            return
        logger.info("Equipamento cadastrado: %s por %s", dados["codigo"], Sessao.usuario_atual.login)
        audit_log.registrar("cadastro_equipamento", f"Equipamento {dados['codigo']} cadastrado")
        self.carregar()

    def _editar(self):
        linha = self._linha_selecionada()
        if not linha:
            QMessageBox.information(self, "Equipamentos", "Selecione um equipamento na lista.")
            return
        dialogo = EquipamentoDialog(self, equipamento=linha)
        if dialogo.exec_() != QDialog.Accepted:
            return
        dados = dialogo.dados()
        try:
            excel_db.update_row(
                config.EQUIPAMENTOS_FILE, Equipamento.colunas(), "codigo", linha["codigo"], dados
            )
        except excel_db.ArquivoEmUsoError as exc:
            QMessageBox.critical(self, "Equipamentos", str(exc))
            return
        logger.info("Equipamento editado: %s por %s", linha["codigo"], Sessao.usuario_atual.login)
        audit_log.registrar("edicao_equipamento", f"Equipamento {linha['codigo']} editado")
        self.carregar()

    def _excluir(self):
        linha = self._linha_selecionada()
        if not linha:
            QMessageBox.information(self, "Equipamentos", "Selecione um equipamento na lista.")
            return
        resposta = QMessageBox.question(
            self, "Excluir", f"Excluir o equipamento {linha['codigo']}?"
        )
        if resposta != QMessageBox.Yes:
            return
        try:
            excel_db.delete_row(config.EQUIPAMENTOS_FILE, Equipamento.colunas(), "codigo", linha["codigo"])
        except excel_db.ArquivoEmUsoError as exc:
            QMessageBox.critical(self, "Equipamentos", str(exc))
            return
        logger.info("Equipamento excluído: %s por %s", linha["codigo"], Sessao.usuario_atual.login)
        audit_log.registrar("exclusao_equipamento", f"Equipamento {linha['codigo']} excluído")
        self.carregar()

    def _emprestar(self):
        linha = self._linha_selecionada()
        if not linha:
            QMessageBox.information(self, "Empréstimo", "Selecione um equipamento na lista.")
            return
        if linha.get("status") != StatusEquipamento.DISPONIVEL:
            QMessageBox.warning(
                self, "Empréstimo",
                f"Equipamento não está disponível para empréstimo (status atual: {linha.get('status')})."
            )
            return

        dialogo = EmprestimoDialog(self, linha["codigo"], linha.get("descricao", ""))
        if dialogo.exec_() != QDialog.Accepted:
            return
        dados = dialogo.dados()
        emprestimo = Emprestimo(
            id=uuid.uuid4().hex[:8],
            equipamento_codigo=linha["codigo"],
            numero_serie=linha.get("numero_serie", ""),
            responsavel=dados["responsavel"],
            data_retirada=dados["data_retirada"],
            data_prevista_devolucao=dados["data_prevista_devolucao"],
            status=StatusEmprestimo.EM_ANDAMENTO,
            observacoes=dados["observacoes"],
            usuario_registro=Sessao.usuario_atual.login,
        )
        try:
            excel_db.append_row(config.EMPRESTIMOS_FILE, Emprestimo.colunas(), emprestimo.__dict__)
            excel_db.update_row(
                config.EQUIPAMENTOS_FILE, Equipamento.colunas(), "codigo", linha["codigo"],
                {"status": StatusEquipamento.EMPRESTADO},
            )
        except excel_db.ArquivoEmUsoError as exc:
            QMessageBox.critical(self, "Empréstimo", str(exc))
            return
        logger.info(
            "Empréstimo registrado: %s -> %s por %s",
            linha["codigo"], dados["responsavel"], Sessao.usuario_atual.login,
        )
        audit_log.registrar(
            "emprestimo",
            f"Equipamento {linha['codigo']} emprestado para {dados['responsavel']}",
        )
        self.carregar()

        resposta = QMessageBox.question(
            self, "Ficha de empréstimo",
            "Empréstimo registrado. Deseja gerar a ficha de empréstimo em PDF agora?",
        )
        if resposta == QMessageBox.Yes:
            gerar_ficha_pdf_interativo(self, emprestimo.__dict__, linha)
