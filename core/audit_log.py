"""Trilha de auditoria gravada em planilha (logs.xlsx), visível na UI para o admin."""
from datetime import datetime

import config
from core import excel_db
from core.auth import Sessao
from core.logger import get_logger
from core.models import LogAuditoria

logger = get_logger(__name__)


def registrar(acao: str, detalhe: str = "") -> None:
    """Registra uma ação de auditoria do usuário logado na sessão atual."""
    usuario = Sessao.usuario_atual.login if Sessao.usuario_atual else "desconhecido"
    entrada = LogAuditoria(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        usuario=usuario,
        acao=acao,
        detalhe=detalhe,
    )
    try:
        excel_db.append_row(config.LOGS_FILE, LogAuditoria.colunas(), entrada.__dict__)
    except excel_db.ArquivoEmUsoError:
        logger.warning("Não foi possível gravar log de auditoria (arquivo em uso): %s", acao)


def listar() -> list[dict]:
    return excel_db.read_all(config.LOGS_FILE, LogAuditoria.colunas())
