"""Helper compartilhado para gerar a ficha de empréstimo em PDF a partir da UI."""
import os

from PyQt5.QtWidgets import QFileDialog, QMessageBox

import config
from core import audit_log
from core.logger import get_logger
from reports import ficha_emprestimo

logger = get_logger(__name__)


def gerar_ficha_pdf_interativo(parent, emprestimo: dict, equipamento: dict) -> None:
    """Pede ao usuário onde salvar e gera o PDF da ficha de empréstimo."""
    os.makedirs(config.FICHAS_DIR, exist_ok=True)
    nome_sugerido = os.path.join(
        config.FICHAS_DIR, f"ficha_emprestimo_{emprestimo.get('id', 'sem_id')}.pdf"
    )
    caminho, _ = QFileDialog.getSaveFileName(
        parent, "Salvar ficha de empréstimo", nome_sugerido, "PDF (*.pdf)"
    )
    if not caminho:
        return

    try:
        ficha_emprestimo.gerar_pdf(caminho, equipamento, emprestimo)
    except Exception as exc:
        logger.exception("Erro ao gerar ficha de empréstimo em PDF")
        QMessageBox.critical(parent, "Ficha de empréstimo", f"Erro ao gerar PDF: {exc}")
        return

    audit_log.registrar(
        "geracao_ficha_pdf", f"Ficha de empréstimo {emprestimo.get('id', '')} gerada em {caminho}"
    )
    QMessageBox.information(parent, "Ficha de empréstimo", f"Ficha salva em:\n{caminho}")
