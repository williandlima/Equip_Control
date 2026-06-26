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

A aplicação verifica periodicamente (a cada 30 minutos, e também ao abrir):

- Equipamentos com calibração vencida ou vencendo nos próximos 15 dias
  (configurável em `config.py`).
- Empréstimos com devolução em atraso.

Os alertas aparecem na aba "Alertas" e como notificação na bandeja do sistema.

## Logs

Logs técnicos da aplicação ficam em `logs/app.log` (rotativo).

## Próximos passos (fora do MVP atual)

- Tela de auditoria/histórico de logs na interface.
- Geração de ficha de empréstimo em PDF para impressão/assinatura.
- Importação de planilha real de equipamentos existente.
