# Crea l'eseguibile portabile dist\GerardTelegramDownloader.exe
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. .\tools\python.ps1
$python = Get-ProjectPython

& $python -m pip install -q -r requirements.txt -r requirements-dev.txt
& $python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { throw "Test falliti: build interrotta" }
& $python tools\make_icon.py
& $python -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name GerardTelegramDownloader --icon assets\icon.ico main.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller non riuscito" }
Write-Host "Fatto: dist\GerardTelegramDownloader.exe"
