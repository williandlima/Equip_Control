"""Regras de alerta: calibração vencendo/vencida e empréstimo atrasado."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

import config
from core import excel_db
from core.logger import get_logger
from core.models import Emprestimo, Equipamento, StatusEmprestimo

logger = get_logger(__name__)

_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


def _parse_data(valor) -> Optional[date]:
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = str(valor).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    logger.warning("Não foi possível interpretar a data: %r", valor)
    return None


@dataclass
class Alerta:
    tipo: str
    nivel: str  # "atencao" ou "critico"
    referencia: str  # código do equipamento ou id do empréstimo
    mensagem: str


def calcular_alertas() -> list[Alerta]:
    alertas: list[Alerta] = []
    hoje = date.today()
    limite_aviso = hoje + timedelta(days=config.ALERTA_CALIBRACAO_DIAS)

    equipamentos = excel_db.read_all(config.EQUIPAMENTOS_FILE, Equipamento.colunas())
    for eq in equipamentos:
        data_proxima = _parse_data(eq.get("data_proxima_calibracao"))
        if data_proxima is None:
            continue
        codigo = eq.get("codigo", "")
        descricao = eq.get("descricao", "")
        if data_proxima < hoje:
            alertas.append(
                Alerta(
                    tipo="calibracao_vencida",
                    nivel="critico",
                    referencia=codigo,
                    mensagem=f"Calibração vencida: {codigo} - {descricao} "
                    f"(venceu em {data_proxima.strftime('%d/%m/%Y')})",
                )
            )
        elif data_proxima <= limite_aviso:
            alertas.append(
                Alerta(
                    tipo="calibracao_vencendo",
                    nivel="atencao",
                    referencia=codigo,
                    mensagem=f"Calibração vencendo: {codigo} - {descricao} "
                    f"(vence em {data_proxima.strftime('%d/%m/%Y')})",
                )
            )

    emprestimos = excel_db.read_all(config.EMPRESTIMOS_FILE, Emprestimo.colunas())
    for emp in emprestimos:
        if emp.get("status") != StatusEmprestimo.EM_ANDAMENTO:
            continue
        data_prevista = _parse_data(emp.get("data_prevista_devolucao"))
        if data_prevista is None or data_prevista >= hoje:
            continue
        alertas.append(
            Alerta(
                tipo="emprestimo_atrasado",
                nivel="critico",
                referencia=emp.get("id", ""),
                mensagem=f"Empréstimo atrasado: equipamento {emp.get('equipamento_codigo')} "
                f"com {emp.get('responsavel')} (previsto para "
                f"{data_prevista.strftime('%d/%m/%Y')})",
            )
        )

    return alertas
