# Avvia l'app dai sorgenti (per sviluppo)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. .\tools\python.ps1
$python = Get-ProjectPython
& $python main.py
