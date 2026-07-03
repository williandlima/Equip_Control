@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ================================================
echo   Controle de Equipamentos - Instalacao Completa
echo ================================================
echo.

rem ── 1. Verificar Python ────────────────────────────────────────────────
where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    echo.
    echo Se voce usa Anaconda/Spyder, abra o "Anaconda Prompt" e rode este
    echo script por la. Caso contrario, instale o Python em python.org
    echo ^(marque "Add python.exe to PATH" na instalacao^) e tente novamente.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo Python encontrado: %%v

rem ── 2. Criar ambiente virtual ───────────────────────────────────────────
if not exist venv (
    echo.
    echo Criando ambiente virtual em venv\...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
) else (
    echo Ambiente virtual ja existe, pulando criacao.
)

set PY=%~dp0venv\Scripts\python.exe

rem ── 3. Instalar dependencias (offline se libs_offline existir) ─────────
echo.
echo Atualizando pip...
"%PY%" -m pip install --upgrade pip -q

if exist libs_offline (
    echo Pasta libs_offline encontrada - instalando OFFLINE ^(sem internet^)...
    "%PY%" -m pip install --no-index --find-links=libs_offline -r requirements.txt
) else (
    echo Instalando dependencias via internet...
    "%PY%" -m pip install -r requirements.txt
)
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar as dependencias.
    echo Se este computador nao tem internet, rode antes o
    echo baixar_dependencias_offline.bat em um computador que tenha,
    echo copie a pasta libs_offline para ca e rode este instalador de novo.
    pause
    exit /b 1
)

rem ── 4. Criar pastas de dados ─────────────────────────────────────────────
if not exist data mkdir data
if not exist data\fichas mkdir data\fichas
if not exist logs mkdir logs

rem ── 5. Verificar instalacao ──────────────────────────────────────────────
echo.
echo Verificando bibliotecas instaladas...
"%PY%" -c "import PyQt5.QtWidgets, openpyxl, filelock, reportlab, keyring" 2>nul
if errorlevel 1 (
    echo [ERRO] Uma ou mais bibliotecas nao foram instaladas corretamente.
    pause
    exit /b 1
)
echo Bibliotecas OK.

rem ── 6. Pasta de rede compartilhada (opcional) ────────────────────────────
echo.
set /p USAR_REDE="Deseja usar uma pasta de rede compartilhada para os dados (recomendado para varios usuarios)? (s/n): "
if /i "!USAR_REDE!"=="s" (
    set /p CAMINHO_REDE="Digite o caminho da pasta de rede ^(ex: \\avsfs\Equip_Control\data^): "
    setx EQUIP_CONTROL_DATA_DIR "!CAMINHO_REDE!" >nul
    echo Configurado. Sera usado a partir da proxima vez que o sistema abrir.
    echo ^(feche e reabra o Prompt de Comando para a mudanca valer nesta sessao^)
) else (
    echo Usando pasta local .\data\ ^(sem compartilhamento entre usuarios^).
)

rem ── 7. Criar atalho na Area de Trabalho ──────────────────────────────────
echo.
echo Criando atalho na Area de Trabalho...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\criar_atalho.ps1"

echo.
echo ================================================
echo   Instalacao concluida com sucesso!
echo ================================================
echo.
echo   Atalho criado na Area de Trabalho: "Controle de Equipamentos"
echo.
echo   Login padrao ^(troque assim que entrar^):
echo     Usuario: admin
echo     Senha:   admin123
echo.
echo   Tambem e possivel rodar direto por:
echo     venv\Scripts\python.exe main.py
echo ================================================
pause
