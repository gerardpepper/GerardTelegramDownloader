#!/usr/bin/env bash
# Crea l'eseguibile per Linux dist/linux/GerardTelegramDownloader (va eseguito su Linux;
# da Windows usare build-linux.ps1, che lo esegue in Docker).
set -euo pipefail
cd "$(dirname "$0")"

if [ -n "${GTD_PYTHON:-}" ]; then
    python="$GTD_PYTHON"                     # ambiente già pronto (es. l'immagine Docker)
else
    [ -x .venv-linux/bin/python ] || python3 -m venv .venv-linux
    python=.venv-linux/bin/python
fi

echo "== Librerie"
"$python" -m pip install -q --disable-pip-version-check -r requirements.txt -r requirements-dev.txt
echo "== Test"
QT_QPA_PLATFORM=offscreen "$python" -m unittest discover -s tests
echo "== Icona"
QT_QPA_PLATFORM=offscreen "$python" tools/make_icon.py png
echo "== PyInstaller"
"$python" -m PyInstaller --noconfirm --clean --onefile --windowed --name GerardTelegramDownloader \
    --distpath dist/linux --workpath build/linux --specpath build/linux main.py
cp assets/icon.png dist/linux/gerard-telegram-downloader.png
cp tools/linux/installa.sh dist/linux/installa.sh
chmod +x dist/linux/GerardTelegramDownloader dist/linux/installa.sh
echo "Fatto: dist/linux/GerardTelegramDownloader"
