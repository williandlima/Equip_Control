@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Baixar dependencias para instalacao offline
echo ============================================
echo Rode este script em um computador COM internet
echo (o mesmo Windows/arquitetura do PC de destino, se possivel).
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    pause
    exit /b 1
)

if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Atualizando pip...
call venv\Scripts\python.exe -m pip install --upgrade pip

if not exist libs_offline mkdir libs_offline

echo Baixando pacotes e dependencias em libs_offline\...
call venv\Scripts\python.exe -m pip download -r requirements.txt -d libs_offline

echo.
echo ============================================
echo  Concluido!
echo  Copie a pasta do projeto INTEIRA (incluindo
echo  a pasta libs_offline) para um pendrive e leve
echo  para o computador da empresa.
echo  La, rode instalar_completo.bat (ele detecta libs_offline automaticamente)
echo ============================================
pause
