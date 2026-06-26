"""Autenticação de usuários: hash de senha (PBKDF2 + salt) e sessão atual."""
import hashlib
import os
import secrets
from typing import Optional

import config
from core import excel_db
from core.logger import get_logger
from core.models import Perfil, Usuario

logger = get_logger(__name__)

_PBKDF2_ITERATIONS = 200_000


def _hash_senha(senha: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ITERATIONS
    )
    return dk.hex()


def _gerar_salt() -> str:
    return secrets.token_hex(16)


def _criar_usuario(login: str, senha: str, perfil: str, nome: str = "") -> None:
    salt = _gerar_salt()
    usuario = Usuario(
        login=login,
        senha_hash=_hash_senha(senha, salt),
        salt=salt,
        perfil=perfil,
        nome=nome or login,
        ativo="1",
    )
    excel_db.append_row(config.USUARIOS_FILE, Usuario.colunas(), usuario.__dict__)
    logger.info("Usuário criado: %s (perfil=%s)", login, perfil)


def garantir_admin_padrao() -> None:
    """Garante que existe ao menos um usuário admin (criado no primeiro uso)."""
    excel_db.ensure_file(config.USUARIOS_FILE, Usuario.colunas())
    usuarios = excel_db.read_all(config.USUARIOS_FILE, Usuario.colunas())
    if not usuarios:
        _criar_usuario(
            config.ADMIN_PADRAO_LOGIN,
            config.ADMIN_PADRAO_SENHA,
            Perfil.ADMIN,
            nome="Administrador",
        )


def autenticar(login: str, senha: str) -> Optional[Usuario]:
    """Retorna o Usuario autenticado ou None se login/senha inválidos."""
    registro = excel_db.find_one(config.USUARIOS_FILE, Usuario.colunas(), "login", login)
    if not registro:
        return None
    if str(registro.get("ativo", "1")) not in ("1", "True", "true"):
        return None
    senha_hash = _hash_senha(senha, str(registro.get("salt", "")))
    if senha_hash != registro.get("senha_hash"):
        return None
    return Usuario(**registro)


def alterar_senha(login: str, nova_senha: str) -> bool:
    salt = _gerar_salt()
    novo_hash = _hash_senha(nova_senha, salt)
    return excel_db.update_row(
        config.USUARIOS_FILE,
        Usuario.colunas(),
        "login",
        login,
        {"senha_hash": novo_hash, "salt": salt},
    )


def criar_usuario(login: str, senha: str, perfil: str, nome: str = "") -> bool:
    existente = excel_db.find_one(config.USUARIOS_FILE, Usuario.colunas(), "login", login)
    if existente:
        return False
    _criar_usuario(login, senha, perfil, nome)
    return True


class Sessao:
    """Mantém o usuário autenticado durante a execução do programa."""

    usuario_atual: Optional[Usuario] = None

    @classmethod
    def login(cls, usuario: Usuario) -> None:
        cls.usuario_atual = usuario

    @classmethod
    def logout(cls) -> None:
        cls.usuario_atual = None

    @classmethod
    def is_admin(cls) -> bool:
        return bool(cls.usuario_atual and cls.usuario_atual.perfil == Perfil.ADMIN)
