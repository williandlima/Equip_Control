"""Inicialização com o Windows, auto-login e persistência de alertas notificados."""
import base64
import json
import os
import sys
from typing import Optional

import config
from core.logger import get_logger

logger = get_logger(__name__)

_KEYRING_SERVICE = "EquipControl"
_KEYRING_USER_KEY = "autologin_login"
_KEYRING_PASS_KEY = "autologin_senha"
_AUTO_LOGIN_FILE = os.path.join(config.BASE_DIR, ".autologin")
_ALERTAS_NOTIFICADOS_FILE = os.path.join(config.BASE_DIR, "alertas_notificados.json")

_APP_REGISTRY_NAME = "EquipControl"
_APP_REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


# ─── Utilitário de ofuscação local (fallback sem keyring) ────────────────────

def _maquina_key() -> bytes:
    import hashlib
    import socket
    import uuid
    token = f"{socket.gethostname()}:{uuid.getnode()}"
    return hashlib.sha256(token.encode()).digest()


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _ofuscar(texto: str) -> str:
    encr = _xor_bytes(texto.encode("utf-8"), _maquina_key())
    return base64.b64encode(encr).decode("ascii")


def _desofuscar(token: str) -> str:
    encr = base64.b64decode(token.encode("ascii"))
    return _xor_bytes(encr, _maquina_key()).decode("utf-8")


# ─── Auto-login (keyring no Windows; arquivo local como fallback) ─────────────

def _usar_keyring() -> bool:
    """Usa keyring somente no Windows (Credential Manager); em outros SO usa arquivo local."""
    if sys.platform != "win32":
        return False
    try:
        import keyring as _kr
        _kr.get_password(_KEYRING_SERVICE, "probe")
        return True
    except Exception:
        return False


def salvar_auto_login(login: str, senha: str) -> None:
    try:
        if _usar_keyring():
            import keyring
            keyring.set_password(_KEYRING_SERVICE, _KEYRING_USER_KEY, login)
            keyring.set_password(_KEYRING_SERVICE, _KEYRING_PASS_KEY, senha)
            logger.info("Auto-login salvo via keyring")
            return
    except Exception as exc:
        logger.warning("keyring indisponível, usando arquivo local: %s", exc)

    dados = {"login": _ofuscar(login), "senha": _ofuscar(senha)}
    with open(_AUTO_LOGIN_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f)
    logger.info("Auto-login salvo em arquivo local")


def carregar_auto_login() -> tuple[Optional[str], Optional[str]]:
    try:
        if _usar_keyring():
            import keyring
            login = keyring.get_password(_KEYRING_SERVICE, _KEYRING_USER_KEY)
            senha = keyring.get_password(_KEYRING_SERVICE, _KEYRING_PASS_KEY)
            if login and senha:
                return login, senha
    except Exception as exc:
        logger.warning("keyring indisponível ao carregar auto-login: %s", exc)

    if not os.path.exists(_AUTO_LOGIN_FILE):
        return None, None
    try:
        with open(_AUTO_LOGIN_FILE, encoding="utf-8") as f:
            dados = json.load(f)
        return _desofuscar(dados["login"]), _desofuscar(dados["senha"])
    except Exception as exc:
        logger.warning("Erro ao ler auto-login local: %s", exc)
        return None, None


def remover_auto_login() -> None:
    try:
        if _usar_keyring():
            import keyring
            try:
                keyring.delete_password(_KEYRING_SERVICE, _KEYRING_USER_KEY)
                keyring.delete_password(_KEYRING_SERVICE, _KEYRING_PASS_KEY)
            except Exception:
                pass
    except Exception:
        pass
    if os.path.exists(_AUTO_LOGIN_FILE):
        os.remove(_AUTO_LOGIN_FILE)
    logger.info("Auto-login removido")


def auto_login_configurado() -> bool:
    login, _ = carregar_auto_login()
    return login is not None


# ─── Inicialização com o Windows (somente Windows) ───────────────────────────

def _caminho_executavel() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    main_py = os.path.join(config.BASE_DIR, "main.py")
    return f'"{sys.executable}" "{main_py}"'


def registrar_inicializacao_windows() -> bool:
    if sys.platform != "win32":
        logger.info("registrar_inicializacao_windows: não é Windows, ignorado")
        return False
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _APP_REGISTRY_KEY, 0, winreg.KEY_SET_VALUE
        ) as chave:
            winreg.SetValueEx(chave, _APP_REGISTRY_NAME, 0, winreg.REG_SZ, _caminho_executavel())
        logger.info("Inicialização com Windows registrada")
        return True
    except Exception as exc:
        logger.error("Erro ao registrar inicialização com Windows: %s", exc)
        return False


def remover_inicializacao_windows() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _APP_REGISTRY_KEY, 0, winreg.KEY_SET_VALUE
        ) as chave:
            winreg.DeleteValue(chave, _APP_REGISTRY_NAME)
        logger.info("Inicialização com Windows removida")
        return True
    except FileNotFoundError:
        return True
    except Exception as exc:
        logger.error("Erro ao remover inicialização com Windows: %s", exc)
        return False


def inicializacao_windows_ativa() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _APP_REGISTRY_KEY) as chave:
            winreg.QueryValueEx(chave, _APP_REGISTRY_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


# ─── Persistência de alertas já notificados entre sessões ────────────────────

def carregar_alertas_notificados() -> set[tuple[str, str]]:
    if not os.path.exists(_ALERTAS_NOTIFICADOS_FILE):
        return set()
    try:
        with open(_ALERTAS_NOTIFICADOS_FILE, encoding="utf-8") as f:
            dados = json.load(f)
        return {tuple(item) for item in dados.get("notificados", [])}
    except Exception as exc:
        logger.warning("Erro ao carregar alertas notificados: %s", exc)
        return set()


def salvar_alertas_notificados(chaves: set[tuple[str, str]]) -> None:
    try:
        with open(_ALERTAS_NOTIFICADOS_FILE, "w", encoding="utf-8") as f:
            json.dump({"notificados": [list(k) for k in chaves]}, f)
    except Exception as exc:
        logger.warning("Erro ao salvar alertas notificados: %s", exc)
