"""Diálogos modais: cadastro de equipamento, novo empréstimo, gestão de usuários."""
from datetime import date, datetime

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from core import audit_log, auth, excel_db
import config
from core.models import Equipamento, Perfil, StatusEquipamento, Usuario


def _validar_data(texto: str) -> bool:
    if not texto.strip():
        return True
    try:
        datetime.strptime(texto.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


class EquipamentoDialog(QDialog):
    """Cadastro/edição de equipamento."""

    def __init__(self, parent=None, equipamento: dict | None = None):
        super().__init__(parent)
        self._editando = equipamento is not None
        self.setWindowTitle("Editar equipamento" if self._editando else "Novo equipamento")
        self.setMinimumWidth(420)
        self._campos: dict[str, QLineEdit | QComboBox] = {}
        self._montar_ui(equipamento or {})

    def _montar_ui(self, dados: dict):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        def add_linha(nome_coluna: str, rotulo: str, somente_leitura: bool = False):
            campo = QLineEdit(str(dados.get(nome_coluna, "") or ""))
            campo.setReadOnly(somente_leitura)
            form.addRow(rotulo, campo)
            self._campos[nome_coluna] = campo

        add_linha("codigo", "Código (Instrumento):", somente_leitura=self._editando)
        add_linha("grupo", "Grupo:")
        add_linha("certificado", "Certificado:")
        add_linha("descricao", "Descrição:")
        add_linha("numero_serie", "Nº de série:")
        add_linha("fabricante", "Fabricante:")
        add_linha("fornecedor", "Fornecedor:")

        combo_status = QComboBox()
        combo_status.addItems(StatusEquipamento.TODOS)
        status_atual = dados.get("status", StatusEquipamento.DISPONIVEL)
        if status_atual in StatusEquipamento.TODOS:
            combo_status.setCurrentText(status_atual)
        form.addRow("Status:", combo_status)
        self._campos["status"] = combo_status

        add_linha("descricao_status", "Descrição do status:")
        add_linha("periodicidade_calibracao_meses", "Periodicidade calibração (meses):")
        add_linha("data_ultima_calibracao", "Última calibração (AAAA-MM-DD):")
        add_linha("data_proxima_calibracao", "Próxima calibração (AAAA-MM-DD):")
        add_linha("localizacao", "Localização:")
        add_linha("instalacao", "Instalação:")
        add_linha("condicionamento", "Condicionamento:")
        add_linha("modelo", "Modelo:")
        add_linha("local_calibracao", "Local de calibração:")

        layout.addLayout(form)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self._validar_e_aceitar)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def _validar_e_aceitar(self):
        dados = self.dados()
        if not dados["codigo"].strip():
            QMessageBox.warning(self, "Validação", "Informe o código do equipamento.")
            return
        for campo_data in ("data_ultima_calibracao", "data_proxima_calibracao"):
            if not _validar_data(dados[campo_data]):
                QMessageBox.warning(
                    self, "Validação", f"Data inválida em '{campo_data}'. Use AAAA-MM-DD."
                )
                return
        self.accept()

    def dados(self) -> dict:
        resultado = {}
        for nome, campo in self._campos.items():
            if isinstance(campo, QComboBox):
                resultado[nome] = campo.currentText()
            else:
                resultado[nome] = campo.text().strip()
        return resultado


class EmprestimoDialog(QDialog):
    """Registro de novo empréstimo para um equipamento disponível."""

    def __init__(self, parent=None, equipamento_codigo: str = "", descricao: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Novo empréstimo")
        self.setMinimumWidth(380)
        self._montar_ui(equipamento_codigo, descricao)

    def _montar_ui(self, codigo: str, descricao: str):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.label_equipamento = QLineEdit(f"{codigo} - {descricao}")
        self.label_equipamento.setReadOnly(True)
        form.addRow("Equipamento:", self.label_equipamento)

        self.campo_responsavel = QLineEdit()
        form.addRow("Responsável:", self.campo_responsavel)

        self.data_retirada = QDateEdit(QDate.currentDate())
        self.data_retirada.setCalendarPopup(True)
        form.addRow("Data de retirada:", self.data_retirada)

        self.data_prevista = QDateEdit(QDate.currentDate().addDays(7))
        self.data_prevista.setCalendarPopup(True)
        form.addRow("Devolução prevista:", self.data_prevista)

        self.campo_observacoes = QTextEdit()
        self.campo_observacoes.setFixedHeight(60)
        form.addRow("Observações:", self.campo_observacoes)

        layout.addLayout(form)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self._validar_e_aceitar)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def _validar_e_aceitar(self):
        if not self.campo_responsavel.text().strip():
            QMessageBox.warning(self, "Validação", "Informe o responsável pelo empréstimo.")
            return
        self.accept()

    def dados(self) -> dict:
        return {
            "responsavel": self.campo_responsavel.text().strip(),
            "data_retirada": self.data_retirada.date().toString("yyyy-MM-dd"),
            "data_prevista_devolucao": self.data_prevista.date().toString("yyyy-MM-dd"),
            "observacoes": self.campo_observacoes.toPlainText().strip(),
        }


class NovoUsuarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo usuário")
        self.setMinimumWidth(320)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.campo_login = QLineEdit()
        form.addRow("Login:", self.campo_login)
        self.campo_nome = QLineEdit()
        form.addRow("Nome:", self.campo_nome)
        self.campo_senha = QLineEdit()
        self.campo_senha.setEchoMode(QLineEdit.Password)
        form.addRow("Senha inicial:", self.campo_senha)
        self.combo_perfil = QComboBox()
        self.combo_perfil.addItems([Perfil.USUARIO, Perfil.ADMIN])
        form.addRow("Perfil:", self.combo_perfil)

        layout.addLayout(form)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self._validar_e_aceitar)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def _validar_e_aceitar(self):
        if not self.campo_login.text().strip() or not self.campo_senha.text():
            QMessageBox.warning(self, "Validação", "Informe login e senha.")
            return
        self.accept()

    def dados(self) -> dict:
        return {
            "login": self.campo_login.text().strip(),
            "nome": self.campo_nome.text().strip(),
            "senha": self.campo_senha.text(),
            "perfil": self.combo_perfil.currentText(),
        }


class UsuariosManagerDialog(QDialog):
    """Tela de administração de usuários (somente admin)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar usuários")
        self.setMinimumSize(520, 360)
        self._montar_ui()
        self._carregar()

    def _montar_ui(self):
        layout = QVBoxLayout(self)

        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(["Login", "Nome", "Perfil", "Ativo"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabela)

        linha_botoes = QHBoxLayout()
        botao_novo = QPushButton("Novo usuário")
        botao_novo.clicked.connect(self._novo_usuario)
        botao_resetar = QPushButton("Resetar senha")
        botao_resetar.clicked.connect(self._resetar_senha)
        botao_alternar = QPushButton("Ativar/Desativar")
        botao_alternar.clicked.connect(self._alternar_ativo)
        linha_botoes.addWidget(botao_novo)
        linha_botoes.addWidget(botao_resetar)
        linha_botoes.addWidget(botao_alternar)
        layout.addLayout(linha_botoes)

    def _carregar(self):
        usuarios = excel_db.read_all(config.USUARIOS_FILE, Usuario.colunas())
        self.tabela.setRowCount(len(usuarios))
        for i, u in enumerate(usuarios):
            self.tabela.setItem(i, 0, QTableWidgetItem(str(u.get("login", ""))))
            self.tabela.setItem(i, 1, QTableWidgetItem(str(u.get("nome", ""))))
            self.tabela.setItem(i, 2, QTableWidgetItem(str(u.get("perfil", ""))))
            ativo = "Sim" if str(u.get("ativo", "1")) in ("1", "True", "true") else "Não"
            self.tabela.setItem(i, 3, QTableWidgetItem(ativo))

    def _login_selecionado(self) -> str | None:
        linha = self.tabela.currentRow()
        if linha < 0:
            return None
        return self.tabela.item(linha, 0).text()

    def _novo_usuario(self):
        dialogo = NovoUsuarioDialog(self)
        if dialogo.exec_() == QDialog.Accepted:
            dados = dialogo.dados()
            criado = auth.criar_usuario(
                dados["login"], dados["senha"], dados["perfil"], dados["nome"]
            )
            if not criado:
                QMessageBox.warning(self, "Usuários", "Já existe um usuário com esse login.")
                return
            audit_log.registrar("criacao_usuario", f"Usuário {dados['login']} criado (perfil {dados['perfil']})")
            self._carregar()

    def _resetar_senha(self):
        login = self._login_selecionado()
        if not login:
            QMessageBox.information(self, "Usuários", "Selecione um usuário na lista.")
            return
        nova_senha, ok = _pedir_senha(self)
        if ok and nova_senha:
            auth.alterar_senha(login, nova_senha)
            audit_log.registrar("reset_senha", f"Senha de {login} redefinida")
            QMessageBox.information(self, "Usuários", f"Senha de '{login}' redefinida.")

    def _alternar_ativo(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.information(self, "Usuários", "Selecione um usuário na lista.")
            return
        login = self.tabela.item(linha, 0).text()
        ativo_atual = self.tabela.item(linha, 3).text() == "Sim"
        novo_valor = "0" if ativo_atual else "1"
        excel_db.update_row(
            config.USUARIOS_FILE, Usuario.colunas(), "login", login, {"ativo": novo_valor}
        )
        acao = "ativacao_usuario" if novo_valor == "1" else "desativacao_usuario"
        audit_log.registrar(acao, f"Usuário {login} {'ativado' if novo_valor == '1' else 'desativado'}")
        self._carregar()


def _pedir_senha(parent):
    from PyQt5.QtWidgets import QInputDialog

    return QInputDialog.getText(
        parent, "Resetar senha", "Nova senha:", QLineEdit.Password
    )
