"""Geração da ficha de empréstimo em PDF (reportlab)."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_ESTILO_TABELA = TableStyle(
    [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
)


def gerar_pdf(caminho: str, equipamento: dict, emprestimo: dict) -> None:
    """Cria a ficha de empréstimo em `caminho` (.pdf) com dados do equipamento
    e do empréstimo, e linhas de assinatura para impressão."""
    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
    )
    estilos = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph("Ficha de Empréstimo de Equipamento", estilos["Title"]))
    elementos.append(Spacer(1, 0.5 * cm))

    dados_equipamento = [
        ["Código (Instrumento)", equipamento.get("codigo", "")],
        ["Descrição", equipamento.get("descricao", "")],
        ["Nº de série", equipamento.get("numero_serie", "")],
        ["Fabricante", equipamento.get("fabricante", "")],
        ["Modelo", equipamento.get("modelo", "")],
        ["Localização habitual", equipamento.get("localizacao", "")],
    ]
    elementos.append(Paragraph("Dados do equipamento", estilos["Heading2"]))
    tabela_eq = Table(dados_equipamento, colWidths=[6 * cm, 10 * cm])
    tabela_eq.setStyle(_ESTILO_TABELA)
    elementos.append(tabela_eq)
    elementos.append(Spacer(1, 0.7 * cm))

    dados_emprestimo = [
        ["Responsável", emprestimo.get("responsavel", "")],
        ["Data de retirada", emprestimo.get("data_retirada", "")],
        ["Devolução prevista", emprestimo.get("data_prevista_devolucao", "")],
        ["Registrado por", emprestimo.get("usuario_registro", "")],
        ["Observações", emprestimo.get("observacoes", "") or "-"],
    ]
    elementos.append(Paragraph("Dados do empréstimo", estilos["Heading2"]))
    tabela_emp = Table(dados_emprestimo, colWidths=[6 * cm, 10 * cm])
    tabela_emp.setStyle(_ESTILO_TABELA)
    elementos.append(tabela_emp)
    elementos.append(Spacer(1, 2 * cm))

    assinaturas = [["", ""], ["Assinatura do responsável", "Assinatura de quem entregou"]]
    tabela_assinaturas = Table(assinaturas, colWidths=[8 * cm, 8 * cm], rowHeights=[1.5 * cm, 0.6 * cm])
    tabela_assinaturas.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 1), (0, 1), 0.8, colors.black),
                ("LINEABOVE", (1, 1), (1, 1), 0.8, colors.black),
                ("FONTSIZE", (0, 1), (-1, 1), 9),
                ("ALIGN", (0, 1), (-1, 1), "CENTER"),
            ]
        )
    )
    elementos.append(tabela_assinaturas)

    doc.build(elementos)
