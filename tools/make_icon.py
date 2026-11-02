"""Genera assets/icon.ico dall'icona disegnata in gtd.ui.common (usato da build.ps1)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import QSize  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from gtd.ui.common import app_icon  # noqa: E402

app = QApplication([])
out = ROOT / "assets" / "icon.ico"
out.parent.mkdir(exist_ok=True)
if not app_icon().pixmap(QSize(256, 256)).save(str(out), "ICO"):
    sys.exit("Impossibile salvare l'icona")
print(f"Icona creata: {out}")
