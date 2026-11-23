#!/usr/bin/env bash
# Installa Gerard Telegram Downloader per il tuo utente (nessun permesso di amministratore):
# copia il programma in ~/.local/bin e aggiunge la voce nel menu delle applicazioni.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bin="$HOME/.local/bin"
apps="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
icons="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"
mkdir -p "$bin" "$apps" "$icons"
install -m 755 "$here/GerardTelegramDownloader" "$bin/GerardTelegramDownloader"
install -m 644 "$here/gerard-telegram-downloader.png" "$icons/gerard-telegram-downloader.png"
cat > "$apps/gerard-telegram-downloader.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Gerard Telegram Downloader
Comment=Scarica in blocco media e documenti da Telegram
Exec=$bin/GerardTelegramDownloader
Icon=gerard-telegram-downloader
Terminal=false
Categories=Network;FileTransfer;
StartupWMClass=GerardTelegramDownloader
DESKTOP
update-desktop-database "$apps" >/dev/null 2>&1 || true
echo "Installato: lo trovi nel menu delle applicazioni come «Gerard Telegram Downloader»"
echo "(oppure avvialo con: $bin/GerardTelegramDownloader)"
