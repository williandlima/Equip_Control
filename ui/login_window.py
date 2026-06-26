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

from core import auth
from core.logger import get_logger

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
        self._on_login_success(usuario)
