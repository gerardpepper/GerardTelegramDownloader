"""Genera l'icona dell'app da quella disegnata in gtd.ui.common (usato da build.ps1 e build.sh).

Senza argomenti: assets/icon.ico (Windows). Con «png»: assets/icon.png (Linux, per il collegamento nel menu).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import QSize  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from gtd.ui.common import app_icon  # noqa: E402

fmt = "PNG" if sys.argv[1:] == ["png"] else "ICO"
app = QApplication([])
out = ROOT / "assets" / f"icon.{fmt.lower()}"
out.parent.mkdir(exist_ok=True)
if not app_icon().pixmap(QSize(256, 256)).save(str(out), fmt):
    sys.exit("Impossibile salvare l'icona")
print(f"Icona creata: {out}")
