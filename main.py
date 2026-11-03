import asyncio
import ctypes
import sys

import qasync
from PyQt6.QtWidgets import QApplication

from gtd import APP_NAME, APP_TITLE
from gtd.config import setup_logging
from gtd.ui.main_window import MainWindow


def _set_app_id() -> None:
    """Identità propria per Windows: avviata da python.exe, la barra delle applicazioni
    mostrerebbe l'icona di Python invece di quella della finestra."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"Gerard.{APP_NAME}")
    except (AttributeError, OSError):
        pass


def main() -> None:
    setup_logging()
    _set_app_id()  # prima di creare qualsiasi finestra
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_TITLE)
    app.setStyle("Fusion")

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()  # termina quando Qt chiude l'applicazione


if __name__ == "__main__":
    main()
