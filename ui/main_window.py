"""Janela principal: abas de Equipamentos, Empréstimos e Alertas."""
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QMainWindow,
    QMessageBox,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
)

import config
from core import audit_log
from core.auth import Sessao
from core.logger import get_logger
from ui.alertas_widget import AlertasWidget
from ui.dialogs import UsuariosManagerDialog
from ui.emprestimos_tab import EmprestimosTab
from ui.equipamentos_tab import EquipamentosTab
from ui.logs_tab import LogsTab

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, on_logout):
        super().__init__()
        self._on_logout = on_logout
        self._alertas_notificados: set[tuple[str, str]] = set()

        usuario = Sessao.usuario_atual
        self.setWindowTitle("Controle de Equipamentos")
        self.resize(1000, 600)

        self._montar_menu()
        self._montar_abas()
        self.statusBar().showMessage(f"Usuário: {usuario.login} ({usuario.perfil})")
        self._montar_tray()

        self._timer_alertas = QTimer(self)
        self._timer_alertas.timeout.connect(self._verificar_alertas)
        self._timer_alertas.start(config.ALERTA_INTERVALO_MS)
        self._verificar_alertas()

    def _montar_menu(self):
        menu_arquivo = self.menuBar().addMenu("Arquivo")
        acao_sair = QAction("Sair", self)
        acao_sair.triggered.connect(self._sair)
        menu_arquivo.addAction(acao_sair)

        if Sessao.is_admin():
            menu_admin = self.menuBar().addMenu("Administração")
            acao_usuarios = QAction("Gerenciar usuários", self)
            acao_usuarios.triggered.connect(self._abrir_gerenciar_usuarios)
            menu_admin.addAction(acao_usuarios)

    def _montar_abas(self):
        self.abas = QTabWidget()
        self.aba_equipamentos = EquipamentosTab()
        self.aba_emprestimos = EmprestimosTab()
        self.aba_alertas = AlertasWidget()
        self.abas.addTab(self.aba_equipamentos, "Equipamentos")
        self.abas.addTab(self.aba_emprestimos, "Empréstimos")
        self.abas.addTab(self.aba_alertas, "Alertas")
        if Sessao.is_admin():
            self.aba_logs = LogsTab()
            self.abas.addTab(self.aba_logs, "Logs")
        else:
            self.aba_logs = None
        self.abas.currentChanged.connect(self._ao_trocar_aba)
        self.setCentralWidget(self.abas)

    def _ao_trocar_aba(self, _indice: int):
        self.aba_equipamentos.carregar()
        self.aba_emprestimos.carregar()
        if self.aba_logs is not None:
            self.aba_logs.carregar()

    def _montar_tray(self):
        self._tray = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icone = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        self._tray = QSystemTrayIcon(icone, self)
        self._tray.setToolTip("Controle de Equipamentos")
        self._tray.show()

    def _verificar_alertas(self):
        lista = self.aba_alertas.carregar()
        chaves_atuais = {(a.tipo, a.referencia) for a in lista}
        novos = [a for a in lista if (a.tipo, a.referencia) not in self._alertas_notificados]

        if novos and self._tray is not None:
            resumo = "\n".join(a.mensagem for a in novos[:5])
            if len(novos) > 5:
                resumo += f"\n... e mais {len(novos) - 5} alerta(s)."
            self._tray.showMessage(
                "Controle de Equipamentos - Novos alertas", resumo, QSystemTrayIcon.Warning, 8000
            )
            logger.info("Novos alertas detectados: %d", len(novos))

        self._alertas_notificados = chaves_atuais

    def _abrir_gerenciar_usuarios(self):
        dialogo = UsuariosManagerDialog(self)
        dialogo.exec_()

    def _sair(self):
        resposta = QMessageBox.question(self, "Sair", "Deseja realmente sair?")
        if resposta != QMessageBox.Yes:
            return
        logger.info("Logout: %s", Sessao.usuario_atual.login)
        audit_log.registrar("logout", "Logout realizado")
        Sessao.logout()
        self.close()
        self._on_logout()
