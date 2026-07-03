@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
    echo Uso: arraste o arquivo .xlsx da planilha antiga sobre este .bat
    echo   ou rode: importar_planilha.bat "caminho\planilha.xlsx" [--listar-colunas] [--sobrescrever]
    pause
    exit /b 1
)

if not exist venv\Scripts\python.exe (
    echo [ERRO] Ambiente virtual nao encontrado. Rode instalar_completo.bat primeiro.
    pause
    exit /b 1
)

echo Passo 1: listando colunas encontradas na planilha...
venv\Scripts\python.exe scripts\importar_planilha.py %1 --listar-colunas

echo.
set /p CONFIRMA="As colunas acima foram reconhecidas corretamente? Continuar com a importacao? (s/n): "
if /i not "%CONFIRMA%"=="s" (
    echo Importacao cancelada. Ajuste o MAPEAMENTO em scripts\importar_planilha.py e tente novamente.
    pause
    exit /b 0
)

venv\Scripts\python.exe scripts\importar_planilha.py %*

pause
