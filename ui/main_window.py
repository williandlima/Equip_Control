"""Janela principal: abas de Equipamentos, Empréstimos, Alertas e Logs."""
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
)

import config
from core import audit_log
from core.auth import Sessao
from core.logger import get_logger
from core.startup import (
    auto_login_configurado,
    carregar_alertas_notificados,
    inicializacao_windows_ativa,
    registrar_inicializacao_windows,
    remover_auto_login,
    remover_inicializacao_windows,
    salvar_alertas_notificados,
    salvar_auto_login,
)
from ui.alertas_widget import AlertasWidget
from ui.dialogs import UsuariosManagerDialog
from ui.emprestimos_tab import EmprestimosTab
from ui.equipamentos_tab import EquipamentosTab
from ui.logs_tab import LogsTab

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, on_logout, background_mode: bool = False):
        super().__init__()
        self._on_logout = on_logout
        self._background_mode = background_mode
        # Carrega alertas já notificados de sessões anteriores
        self._alertas_notificados: set[tuple[str, str]] = carregar_alertas_notificados()

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

    # ── Menu ─────────────────────────────────────────────────────────────────

    def _montar_menu(self):
        menu_arquivo = self.menuBar().addMenu("Arquivo")

        acao_mostrar = QAction("Mostrar janela", self)
        acao_mostrar.triggered.connect(self._mostrar_janela)
        menu_arquivo.addAction(acao_mostrar)

        menu_arquivo.addSeparator()

        acao_sair = QAction("Sair", self)
        acao_sair.triggered.connect(self._sair)
        menu_arquivo.addAction(acao_sair)

        if Sessao.is_admin():
            menu_admin = self.menuBar().addMenu("Administração")

            acao_usuarios = QAction("Gerenciar usuários", self)
            acao_usuarios.triggered.connect(self._abrir_gerenciar_usuarios)
            menu_admin.addAction(acao_usuarios)

            menu_admin.addSeparator()

            self.acao_startup = QAction(self)
            self._atualizar_texto_startup()
            self.acao_startup.triggered.connect(self._configurar_startup)
            menu_admin.addAction(self.acao_startup)

    def _atualizar_texto_startup(self):
        ativo = inicializacao_windows_ativa() and auto_login_configurado()
        texto = "Desativar inicialização com o Windows" if ativo else "Ativar inicialização com o Windows"
        self.acao_startup.setText(texto)

    # ── Abas ─────────────────────────────────────────────────────────────────

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

    # ── Tray ─────────────────────────────────────────────────────────────────

    def _montar_tray(self):
        self._tray = None
        icone = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        self._tray = QSystemTrayIcon(icone, self)
        self._tray.setToolTip("Controle de Equipamentos")
        self._tray.activated.connect(self._ao_ativar_tray)

        menu_tray = QMenu()

        acao_abrir = QAction("Abrir sistema", self)
        acao_abrir.triggered.connect(self._mostrar_janela)
        menu_tray.addAction(acao_abrir)

        acao_verificar = QAction("Verificar alertas agora", self)
        acao_verificar.triggered.connect(self._verificar_alertas)
        menu_tray.addAction(acao_verificar)

        menu_tray.addSeparator()

        acao_sair_tray = QAction("Sair", self)
        acao_sair_tray.triggered.connect(self._sair_definitivo)
        menu_tray.addAction(acao_sair_tray)

        self._tray.setContextMenu(menu_tray)
        self._tray.show()

    def _ao_ativar_tray(self, motivo):
        if motivo == QSystemTrayIcon.Trigger:  # clique simples
            self._mostrar_janela()

    def _mostrar_janela(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    # ── Verificação de alertas ────────────────────────────────────────────────

    def _verificar_alertas(self):
        lista = self.aba_alertas.carregar()
        chaves_atuais = {(a.tipo, a.referencia) for a in lista}

        # Remove da memória alertas que foram resolvidos (para notificar novamente se voltarem)
        self._alertas_notificados &= chaves_atuais

        novos = [a for a in lista if (a.tipo, a.referencia) not in self._alertas_notificados]
        if novos and self._tray is not None:
            resumo = "\n".join(a.mensagem for a in novos[:5])
            if len(novos) > 5:
                resumo += f"\n... e mais {len(novos) - 5} alerta(s)."
            self._tray.showMessage(
                "Controle de Equipamentos — Alertas", resumo, QSystemTrayIcon.Warning, 10000
            )
            logger.info("Novos alertas notificados: %d", len(novos))
            self._alertas_notificados |= {(a.tipo, a.referencia) for a in novos}
            salvar_alertas_notificados(self._alertas_notificados)

        # Atualiza tooltip do tray com contagem total
        if self._tray:
            total = len(lista)
            tooltip = f"Controle de Equipamentos — {total} alerta(s) ativo(s)" if total else "Controle de Equipamentos"
            self._tray.setToolTip(tooltip)

    # ── Fechar janela ─────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self._background_mode:
            # No modo background, fechar a janela apenas a oculta (app continua na bandeja)
            event.ignore()
            self.hide()
            if self._tray:
                self._tray.showMessage(
                    "Controle de Equipamentos",
                    "O sistema continua ativo na bandeja. Clique no ícone para reabrir.",
                    QSystemTrayIcon.Information, 4000,
                )
        else:
            event.accept()

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _abrir_gerenciar_usuarios(self):
        dialogo = UsuariosManagerDialog(self)
        dialogo.exec_()

    def _configurar_startup(self):
        ativo = inicializacao_windows_ativa() and auto_login_configurado()
        if ativo:
            resposta = QMessageBox.question(
                self, "Inicialização com Windows",
                "Deseja desativar a inicialização automática com o Windows?\n"
                "O sistema não iniciará mais em segundo plano ao ligar o computador.",
            )
            if resposta == QMessageBox.Yes:
                remover_inicializacao_windows()
                remover_auto_login()
                self._background_mode = False
                QMessageBox.information(
                    self, "Inicialização com Windows",
                    "Inicialização automática desativada.\n"
                    "Ao fechar o programa, ele não ficará mais na bandeja.",
                )
        else:
            resposta = QMessageBox.question(
                self, "Inicialização com Windows",
                "Deseja que o sistema inicie automaticamente com o Windows\n"
                "e fique em segundo plano na bandeja do sistema?\n\n"
                f"As credenciais do usuário atual ({Sessao.usuario_atual.login}) "
                "serão salvas de forma segura para login automático.",
            )
            if resposta == QMessageBox.Yes:
                from PyQt5.QtWidgets import QInputDialog, QLineEdit
                senha, ok = QInputDialog.getText(
                    self, "Confirmar senha",
                    f"Confirme a senha de '{Sessao.usuario_atual.login}' para salvar o auto-login:",
                    QLineEdit.Password,
                )
                if not ok or not senha:
                    return
                usuario = __import__("core.auth", fromlist=["autenticar"]).autenticar(
                    Sessao.usuario_atual.login, senha
                )
                if usuario is None:
                    QMessageBox.critical(self, "Senha incorreta", "Senha incorreta. Auto-login não foi salvo.")
                    return
                salvar_auto_login(Sessao.usuario_atual.login, senha)
                ok_reg = registrar_inicializacao_windows()
                self._background_mode = True
                mensagem = (
                    "Inicialização automática ativada com sucesso!\n\n"
                    "Na próxima vez que o Windows iniciar, o sistema será carregado "
                    "automaticamente na bandeja do sistema."
                )
                if not ok_reg:
                    mensagem += "\n\n⚠ Não foi possível registrar no Windows (talvez não seja Windows). "
                    "O auto-login foi salvo, mas o registro no startup precisa ser feito manualmente."
                QMessageBox.information(self, "Inicialização com Windows", mensagem)

        self._atualizar_texto_startup()

    def _sair(self):
        resposta = QMessageBox.question(self, "Sair", "Deseja sair do sistema?")
        if resposta != QMessageBox.Yes:
            return
        self._sair_definitivo()

    def _sair_definitivo(self):
        logger.info("Encerrando aplicação: %s", Sessao.usuario_atual.login if Sessao.usuario_atual else "?")
        audit_log.registrar("logout", "Logout realizado")
        self._timer_alertas.stop()
        if self._tray:
            self._tray.hide()
        Sessao.logout()
        self._background_mode = False
        if self._on_logout:
            self._on_logout()
        else:
            QApplication.quit()
