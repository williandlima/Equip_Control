@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Instalacao OFFLINE - Controle de Equipamentos
echo ============================================

if not exist libs_offline (
    echo [ERRO] Pasta libs_offline nao encontrada.
    echo Copie a pasta do projeto inteira, gerada pelo
    echo baixar_dependencias_offline.bat, incluindo libs_offline.
    pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    echo Se voce usa o Python do Anaconda/Spyder, abra o
    echo "Anaconda Prompt" para rodar este script, ou adicione
    echo o Python do Anaconda ao PATH.
    pause
    exit /b 1
)

if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
) else (
    echo Ambiente virtual ja existe, pulando criacao.
)

echo Instalando dependencias a partir de libs_offline\ (sem internet)...
call venv\Scripts\python.exe -m pip install --no-index --find-links=libs_offline -r requirements.txt

echo.
echo ============================================
echo  Instalacao concluida!
echo  Para rodar: venv\Scripts\python.exe main.py
echo.
echo  Para usar no Spyder: Ferramentas ^> Preferencias ^>
echo  Interpretador Python ^> Usar o seguinte interpretador
echo  ^> aponte para: %cd%\venv\Scripts\python.exe
echo ============================================
pause
