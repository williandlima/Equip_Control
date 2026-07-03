"""Configuração central de caminhos e parâmetros do sistema."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Pasta onde ficam as planilhas "banco de dados". Em produção, aponte para a
# pasta de rede compartilhada (ex.: r"\\avsfs\Equip_Control\data").
DATA_DIR = os.environ.get("EQUIP_CONTROL_DATA_DIR", os.path.join(BASE_DIR, "data"))

LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

EQUIPAMENTOS_FILE = os.path.join(DATA_DIR, "equipamentos.xlsx")
EMPRESTIMOS_FILE = os.path.join(DATA_DIR, "emprestimos.xlsx")
USUARIOS_FILE = os.path.join(DATA_DIR, "usuarios.xlsx")
LOGS_FILE = os.path.join(DATA_DIR, "logs.xlsx")

# Pasta padrão de sugestão ao salvar fichas de empréstimo em PDF.
FICHAS_DIR = os.path.join(DATA_DIR, "fichas")

# Tempo máximo (segundos) esperando o lock do arquivo antes de avisar o usuário.
LOCK_TIMEOUT_SECONDS = 5

# Intervalo (ms) de recálculo automático dos alertas.
ALERTA_INTERVALO_MS = 30 * 60 * 1000

# Credenciais padrão criadas automaticamente se usuarios.xlsx não existir.
ADMIN_PADRAO_LOGIN = "admin"
ADMIN_PADRAO_SENHA = "admin123"
