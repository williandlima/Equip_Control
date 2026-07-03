# Controle de Equipamentos

Sistema desktop em Python/PyQt5 para controle de equipamentos/instrumentos de
calibração, com login, empréstimo/devolução e alertas de calibração vencida ou
empréstimo atrasado. Os dados ficam em planilhas Excel (`.xlsx`), pensadas para
serem colocadas numa pasta de rede compartilhada por um pequeno grupo de
usuários (2 a 5 pessoas simultâneas).

## Instalação

```bash
pip install -r requirements.txt
```

No Windows, `instalar.bat` cria o ambiente virtual e instala tudo
automaticamente (duplo clique).

### Instalação em computador sem internet

Se o computador de destino não tem acesso à internet (comum em redes
corporativas fechadas), baixe as dependências em outro computador antes:

1. Em um computador **com internet** (Windows), dentro da pasta do projeto,
   rode `baixar_dependencias_offline.bat`. Isso baixa todos os pacotes e
   suas dependências em `libs_offline\`.
2. Copie a pasta do projeto **inteira** (incluindo `libs_offline\`) para um
   pendrive e leve para o computador da empresa.
3. No computador sem internet, rode `instalar_offline.bat`. Ele cria o
   ambiente virtual e instala tudo a partir de `libs_offline\`, sem
   precisar baixar nada da internet.

**Usando com Spyder:** o Spyder normalmente roda com o Python do
Anaconda/Miniconda, que é separado do ambiente virtual (`venv`) criado por
esses scripts. Para usar este projeto dentro do Spyder, aponte o
interpretador para o Python do `venv`: `Ferramentas > Preferências >
Interpretador Python > Usar o seguinte interpretador` e selecione
`venv\Scripts\python.exe`. Alternativamente, rode `venv\Scripts\python.exe
main.py` direto pelo Prompt de Comando/Anaconda Prompt — como este é um
app de janela (PyQt5), pode ser mais estável rodar fora do console
integrado do Spyder.

## Execução

```bash
python main.py
```

No primeiro uso, um usuário administrador padrão é criado automaticamente:

- **Login:** `admin`
- **Senha:** `admin123`

> Troque a senha padrão logo após o primeiro login (menu Administração >
> Gerenciar usuários > Resetar senha).

## Onde ficam os dados

Por padrão, as planilhas são criadas em `./data/`:

- `equipamentos.xlsx`
- `emprestimos.xlsx`
- `usuarios.xlsx`

Para usar uma pasta de rede compartilhada, defina a variável de ambiente
`EQUIP_CONTROL_DATA_DIR` apontando para o caminho desejado antes de iniciar o
programa, por exemplo (Windows):

```bat
set EQUIP_CONTROL_DATA_DIR=\\avsfs\Equip_Control\data
python main.py
```

Cada gravação é protegida por um lock de arquivo (`<arquivo>.xlsx.lock`), que
evita que dois usuários gravem ao mesmo tempo. Se o arquivo estiver em uso, a
aplicação avisa e pede para tentar novamente em alguns segundos.

## Perfis de usuário

- **admin**: cadastra/edita/exclui equipamentos, gerencia usuários.
- **usuario**: consulta equipamentos, registra empréstimos e devoluções.

## Alertas

A aplicação verifica periodicamente (a cada 30 minutos, e também ao abrir).
Como o controle de calibração é feito manualmente pelo campo "Status" do
equipamento (do jeito que já era feito na planilha), o alerta dispara quando o
status for um destes:

- Calibração Vencida
- Aguardando Calibração
- Aguardando Avaliação
- Desaparecido

Além disso, empréstimos com devolução em atraso também geram alerta.

Os alertas aparecem na aba "Alertas" e como notificação na bandeja do sistema.

## Importando a planilha existente

Se você já tem uma planilha de equipamentos, use `scripts/importar_planilha.py`
(ou arraste o arquivo sobre `importar_planilha.bat`) para trazer os dados de
uma vez, sem recadastrar tudo manualmente. Veja `modelos/modelo_planilha_equipamentos.xlsx`
para o formato de colunas reconhecido (inclui uma aba de instruções).

## Logs

Logs técnicos da aplicação ficam em `logs/app.log` (rotativo).

## Próximos passos (fora do MVP atual)

- Tela de auditoria/histórico de logs na interface.
