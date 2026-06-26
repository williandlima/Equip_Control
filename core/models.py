"""Modelos de dados e definição das colunas das planilhas."""
from dataclasses import dataclass, field, fields
from typing import Optional


class StatusEquipamento:
    DISPONIVEL = "Disponível"
    EM_USO = "Em Uso"
    EMPRESTADO = "Emprestado"
    CALIBRACAO_VENCIDA = "Calibração Vencida"
    AGUARDANDO_CALIBRACAO = "Aguardando Calibração"
    FORA_DE_USO = "Fora de Uso"
    DESCALIBRADO = "Descalibrado"

    TODOS = [
        DISPONIVEL,
        EM_USO,
        EMPRESTADO,
        CALIBRACAO_VENCIDA,
        AGUARDANDO_CALIBRACAO,
        FORA_DE_USO,
        DESCALIBRADO,
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
    descricao_status: str = ""
    periodicidade_calibracao_meses: str = ""
    data_ultima_calibracao: str = ""
    data_proxima_calibracao: str = ""
    localizacao: str = ""
    instalacao: str = ""
    condicionamento: str = ""
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
