# Crea l'eseguibile portabile dist\GerardTelegramDownloader.exe
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) { py -3 -m venv .venv }
.\.venv\Scripts\python -m pip install -q -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { throw "Test falliti: build interrotta" }
.\.venv\Scripts\python tools\make_icon.py
.\.venv\Scripts\pyinstaller --noconfirm --clean --onefile --windowed `
    --name GerardTelegramDownloader --icon assets\icon.ico main.py
Write-Host "Fatto: dist\GerardTelegramDownloader.exe"
