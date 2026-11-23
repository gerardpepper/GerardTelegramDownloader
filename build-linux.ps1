# Crea l'eseguibile per Linux dist\linux\GerardTelegramDownloader usando Docker (Docker Desktop deve essere avviato).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. .\tools\python.ps1

Invoke-Checked "Creazione dell'ambiente Docker non riuscita" {
    docker build -t gerard-telegram-downloader-build -f tools/linux/Dockerfile .
}
New-Item -ItemType Directory -Force dist\linux | Out-Null
$src = (Resolve-Path .).Path
$out = (Resolve-Path dist\linux).Path
# il codice viene copiato nel contenitore (senza ambienti Python e build di Windows), il risultato torna in dist\linux
Invoke-Checked "Build Linux non riuscita" {
    docker run --rm -v "${src}:/src:ro" -v "${out}:/out" gerard-telegram-downloader-build bash -c `
        "mkdir /work && tar -C /src --exclude='./.venv*' --exclude=./build --exclude=./dist --exclude=./.git -cf - . | tar -C /work -xf - && cd /work && bash build.sh && cp dist/linux/* /out/"
}
Write-Host "Fatto: dist\linux\GerardTelegramDownloader"
