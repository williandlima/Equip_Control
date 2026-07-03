"""Regras de alerta: status de calibração e empréstimo atrasado."""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

import config
from core import excel_db
from core.logger import get_logger
from core.models import Emprestimo, Equipamento, StatusEmprestimo, StatusEquipamento

logger = get_logger(__name__)

_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")

# Status de equipamento que geram alerta, e o nível de severidade de cada um.
_STATUS_ALERTA = {
    StatusEquipamento.CALIBRACAO_VENCIDA: ("calibracao_vencida", "critico", "Calibração vencida"),
    StatusEquipamento.AGUARDANDO_CALIBRACAO: ("aguardando_calibracao", "atencao", "Aguardando calibração"),
    StatusEquipamento.AGUARDANDO_AVALIACAO: ("aguardando_avaliacao", "atencao", "Aguardando avaliação"),
    StatusEquipamento.DESAPARECIDO: ("equipamento_desaparecido", "critico", "Equipamento desaparecido"),
}


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

    equipamentos = excel_db.read_all(config.EQUIPAMENTOS_FILE, Equipamento.colunas())
    for eq in equipamentos:
        status = eq.get("status", "")
        info = _STATUS_ALERTA.get(status)
        if info is None:
            continue
        tipo, nivel, rotulo = info
        codigo = eq.get("codigo", "")
        descricao = eq.get("descricao", "")
        alertas.append(
            Alerta(
                tipo=tipo,
                nivel=nivel,
                referencia=codigo,
                mensagem=f"{rotulo}: {codigo} - {descricao}",
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
