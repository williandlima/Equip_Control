"""Ponto de entrada do sistema de Controle de Equipamentos.

Dois modos de operação:
- Normal   : exibe a tela de login e depois a janela principal.
- Background: inicia oculto na bandeja do sistema usando auto-login salvo;
              a janela principal aparece apenas quando o usuário clica no ícone.
"""
import sys

from PyQt5.QtWidgets import QApplication

from core import auth
from core.logger import get_logger
from core.startup import auto_login_configurado, carregar_auto_login

logger = get_logger(__name__)


class Aplicacao:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.login_window = None
        self.main_window = None
        self._modo_background = False

    def iniciar(self):
        auth.garantir_admin_padrao()

        login, senha = carregar_auto_login()
        if login and senha:
            usuario = auth.autenticar(login, senha)
            if usuario:
                logger.info("Auto-login efetuado para '%s' — modo background", usuario.login)
                auth.Sessao.login(usuario)
                self._modo_background = True
                self._abrir_main_window(usuario)
                return self.app.exec_()
            else:
                logger.warning("Auto-login falhou (credenciais inválidas); exibindo tela de login")

        self._mostrar_login()
        return self.app.exec_()

    def _mostrar_login(self):
        from ui.login_window import LoginWindow
        janela_anterior = self.main_window
        self.main_window = None
        self.login_window = LoginWindow(self._abrir_main_window)
        self.login_window.show()
        if janela_anterior is not None:
            janela_anterior.close()

    def _abrir_main_window(self, usuario):
        from ui.main_window import MainWindow
        janela_anterior = self.login_window
        self.login_window = None
        self.main_window = MainWindow(
            on_logout=self._mostrar_login,
            background_mode=self._modo_background,
        )
        if not self._modo_background:
            self.main_window.show()
        if janela_anterior is not None:
            janela_anterior.close()


def main():
    logger.info("Aplicação iniciada")
    aplicacao = Aplicacao()
    codigo_saida = aplicacao.iniciar()
    logger.info("Aplicação finalizada (código %s)", codigo_saida)
    sys.exit(codigo_saida)


if __name__ == "__main__":
    main()
