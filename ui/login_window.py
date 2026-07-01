"""Tela de login."""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import audit_log, auth
from core.logger import get_logger
from core.startup import (
    auto_login_configurado,
    registrar_inicializacao_windows,
    salvar_auto_login,
)

logger = get_logger(__name__)


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self._on_login_success = on_login_success
        self.setWindowTitle("Controle de Equipamentos - Login")
        self.setFixedSize(360, 200)
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Controle de Equipamentos")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        form = QFormLayout()
        self.campo_login = QLineEdit()
        self.campo_senha = QLineEdit()
        self.campo_senha.setEchoMode(QLineEdit.Password)
        self.campo_senha.returnPressed.connect(self._tentar_login)
        form.addRow("Usuário:", self.campo_login)
        form.addRow("Senha:", self.campo_senha)
        layout.addLayout(form)

        botao_entrar = QPushButton("Entrar")
        botao_entrar.clicked.connect(self._tentar_login)
        layout.addWidget(botao_entrar)

    def _oferecer_startup(self, usuario, senha: str):
        if auto_login_configurado():
            return
        resposta = QMessageBox.question(
            None,
            "Inicialização automática",
            "Deseja que o sistema inicie com o Windows e fique ativo\n"
            "na bandeja do sistema em segundo plano?\n\n"
            "Alertas de calibração e empréstimos aparecerão automaticamente.",
        )
        if resposta == QMessageBox.Yes:
            salvar_auto_login(usuario.login, senha)
            registrar_inicializacao_windows()
            QMessageBox.information(
                None,
                "Inicialização automática",
                "Ativado! Na próxima vez que o Windows iniciar, o sistema\n"
                "será carregado automaticamente na bandeja do sistema.\n\n"
                "Você pode desativar isso em Administração → Configurar inicialização.",
            )

    def _tentar_login(self):
        login = self.campo_login.text().strip()
        senha = self.campo_senha.text()
        if not login or not senha:
            QMessageBox.warning(self, "Login", "Informe usuário e senha.")
            return

        usuario = auth.autenticar(login, senha)
        if usuario is None:
            logger.warning("Tentativa de login inválida para usuário '%s'", login)
            QMessageBox.critical(self, "Login", "Usuário ou senha inválidos.")
            self.campo_senha.clear()
            return

        logger.info("Login efetuado: %s (perfil=%s)", usuario.login, usuario.perfil)
        auth.Sessao.login(usuario)
        audit_log.registrar("login", "Login realizado")
        self._on_login_success(usuario)
        self._oferecer_startup(usuario, senha)
