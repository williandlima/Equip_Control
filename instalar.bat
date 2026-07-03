@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Controle de Equipamentos - Instalacao
echo ============================================

where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH. Instale o Python 3.10+ e tente novamente.
    pause
    exit /b 1
)

if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
) else (
    echo Ambiente virtual ja existe, pulando criacao.
)

echo Atualizando pip...
call venv\Scripts\python.exe -m pip install --upgrade pip

echo Instalando dependencias...
call venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo ============================================
echo  Instalacao concluida!
echo  Para rodar: venv\Scripts\python.exe main.py
echo  ou abra o projeto no VSCode e pressione F5.
echo ============================================
pause
