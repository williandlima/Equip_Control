"""Ponto de entrada do sistema de Controle de Equipamentos."""
import sys

from PyQt5.QtWidgets import QApplication

from core import auth
from core.logger import get_logger
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

logger = get_logger(__name__)


class Aplicacao:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.main_window = None

    def iniciar(self):
        auth.garantir_admin_padrao()
        self._mostrar_login()
        return self.app.exec_()

    def _mostrar_login(self):
        janela_anterior = self.main_window
        self.main_window = None
        self.login_window = LoginWindow(self._abrir_main_window)
        self.login_window.show()
        if janela_anterior is not None:
            janela_anterior.close()

    def _abrir_main_window(self, usuario):
        janela_anterior = self.login_window
        self.login_window = None
        self.main_window = MainWindow(self._mostrar_login)
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
