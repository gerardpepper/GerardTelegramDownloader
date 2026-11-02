import asyncio
import sys

import qasync
from PyQt6.QtWidgets import QApplication

from gtd import APP_NAME, APP_TITLE
from gtd.config import setup_logging
from gtd.ui.main_window import MainWindow


def main() -> None:
    setup_logging()
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
