# Crea l'eseguibile portabile dist\GerardTelegramDownloader.exe
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. .\tools\python.ps1
$python = Get-ProjectPython

Invoke-Checked "Installazione delle librerie non riuscita" {
    & $python -m pip install -q --disable-pip-version-check -r requirements.txt -r requirements-dev.txt
}
Invoke-Checked "Test falliti: build interrotta" { & $python -m unittest discover -s tests }
Invoke-Checked "Creazione dell'icona non riuscita" { & $python tools\make_icon.py }
Invoke-Checked "PyInstaller non riuscito" {
    & $python -m PyInstaller --noconfirm --clean --onefile --windowed `
        --name GerardTelegramDownloader --icon assets\icon.ico main.py
}
Write-Host "Fatto: dist\GerardTelegramDownloader.exe"
