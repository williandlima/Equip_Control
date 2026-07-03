# Cria um atalho "Controle de Equipamentos" na Area de Trabalho do usuario,
# apontando para o Python do venv do projeto (sem abrir janela de console).
$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $PSScriptRoot
$pythonw = Join-Path $projectDir "venv\Scripts\pythonw.exe"
$mainPy = Join-Path $projectDir "main.py"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Controle de Equipamentos.lnk"

if (-not (Test-Path $pythonw)) {
    Write-Host "[aviso] pythonw.exe nao encontrado em $pythonw - atalho nao criado."
    exit 0
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = "`"$mainPy`""
$shortcut.WorkingDirectory = $projectDir
$shortcut.IconLocation = $pythonw
$shortcut.Description = "Controle de Equipamentos"
$shortcut.Save()

Write-Host "Atalho criado em: $shortcutPath"
