"""Modelos de dados e definição das colunas das planilhas."""
from dataclasses import dataclass, field, fields
from typing import Optional


class StatusEquipamento:
    DISPONIVEL = "Disponível"
    EM_USO = "Em Uso"
    EMPRESTADO = "Emprestado"
    CALIBRACAO_VENCIDA = "Calibração Vencida"
    AGUARDANDO_CALIBRACAO = "Aguardando Calibração"
    AGUARDANDO_AVALIACAO = "Aguardando Avaliação"
    FORA_DE_USO = "Fora de Uso"
    DESCALIBRADO = "Descalibrado"
    ISENTO = "Isento"
    SUCATA = "Sucata"
    DESAPARECIDO = "Desaparecido"

    TODOS = [
        DISPONIVEL,
        EM_USO,
        EMPRESTADO,
        CALIBRACAO_VENCIDA,
        AGUARDANDO_CALIBRACAO,
        AGUARDANDO_AVALIACAO,
        FORA_DE_USO,
        DESCALIBRADO,
        ISENTO,
        SUCATA,
        DESAPARECIDO,
    ]


class StatusEmprestimo:
    EM_ANDAMENTO = "Em andamento"
    DEVOLVIDO = "Devolvido"
    ATRASADO = "Atrasado"

    TODOS = [EM_ANDAMENTO, DEVOLVIDO, ATRASADO]


class Perfil:
    ADMIN = "admin"
    USUARIO = "usuario"


@dataclass
class Equipamento:
    codigo: str
    grupo: str = ""
    certificado: str = ""
    descricao: str = ""
    numero_serie: str = ""
    fabricante: str = ""
    fornecedor: str = ""
    status: str = StatusEquipamento.DISPONIVEL
    codigo_status: str = ""
    calibrado_por: str = ""
    usuario_departamento: str = ""
    localizacao: str = ""
    instalacao: str = ""
    instalacao_secundaria: str = ""
    gerencia: str = ""
    modelo: str = ""
    local_calibracao: str = ""

    @classmethod
    def colunas(cls):
        return [f.name for f in fields(cls)]


@dataclass
class Emprestimo:
    id: str
    equipamento_codigo: str
    numero_serie: str = ""
    responsavel: str = ""
    data_retirada: str = ""
    data_prevista_devolucao: str = ""
    data_devolucao_real: str = ""
    status: str = StatusEmprestimo.EM_ANDAMENTO
    observacoes: str = ""
    usuario_registro: str = ""

    @classmethod
    def colunas(cls):
        return [f.name for f in fields(cls)]


@dataclass
class LogAuditoria:
    timestamp: str
    usuario: str
    acao: str
    detalhe: str = ""

    @classmethod
    def colunas(cls):
        return [f.name for f in fields(cls)]


@dataclass
class Usuario:
    login: str
    senha_hash: str = ""
    salt: str = ""
    perfil: str = Perfil.USUARIO
    nome: str = ""
    ativo: str = "1"

    @classmethod
    def colunas(cls):
        return [f.name for f in fields(cls)]
