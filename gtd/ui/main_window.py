"""Finestra principale: instrada tra login e pagina di download, menu, notifiche."""

import logging
import os

from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QSystemTrayIcon

from .. import APP_TITLE, __version__, taskbar
from ..taskbar import TaskbarProgress
from .. import i18n
from ..config import Settings, data_dir
from ..i18n import N_, tr
from ..state import StateDB
from ..telegram import clear_session, make_client, save_session
from .common import app_icon, apply_theme, spawn
from .download_page import DownloadPage
from .login_page import LoginPage

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings.load()
        i18n.set_language(self.settings.language)  # prima di creare le pagine
        self.db = StateDB(data_dir() / "state.db")
        self.client = None
        self.taskbar: TaskbarProgress | None = None  # creato al primo uso, quando la finestra esiste

        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(app_icon())
        self.resize(1200, 760)

        self.login_page = LoginPage(self)
        self.download_page = DownloadPage(self)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.download_page)
        self.setCentralWidget(self.stack)
        self.login_page.logged_in.connect(lambda: spawn(self._enter_main()))

        self.tray = QSystemTrayIcon(app_icon(), self)
        self.tray.setToolTip(APP_TITLE)
        self.tray.show()

        self._build_menu()
        apply_theme(self.settings.theme)
        self.login_page.prefill(self.settings.api_id, self.settings.api_hash)
        self.login_page.set_step("api")
        spawn(self._startup())

    def _build_menu(self) -> None:
        """Ricostruito da zero a ogni cambio di lingua."""
        self.menuBar().clear()
        logout_enabled = getattr(self, "logout_action", None) is not None and self.logout_action.isEnabled()
        account = self.menuBar().addMenu(tr("&Account"))
        self.logout_action = QAction(tr("Esci dall'account Telegram"), self)
        self.logout_action.setEnabled(logout_enabled)
        self.logout_action.triggered.connect(self._on_logout)
        account.addAction(self.logout_action)
        open_data = QAction(tr("Apri cartella dati dell'app"), self)
        open_data.triggered.connect(lambda: os.startfile(data_dir()))
        account.addAction(open_data)
        account.addSeparator()
        quit_action = QAction(tr("Esci"), self)
        quit_action.triggered.connect(self.close)
        account.addAction(quit_action)

        view = self.menuBar().addMenu(tr("&Visualizza"))
        theme_menu = view.addMenu(tr("Tema"))
        group = QActionGroup(self)
        for label, key in ((N_("Come il sistema"), "system"), (N_("Chiaro"), "light"), (N_("Scuro"), "dark")):
            action = QAction(tr(label), self, checkable=True)
            action.setChecked(self.settings.theme == key)
            action.triggered.connect(lambda _=False, k=key: self._set_theme(k))
            group.addAction(action)
            theme_menu.addAction(action)

        language_menu = view.addMenu(tr("Lingua"))
        group = QActionGroup(self)
        options = [(tr("Automatica (lingua di Windows)"), "")] + [(name, code) for code, name in i18n.LANGUAGES.items()]
        for label, code in options:
            action = QAction(label, self, checkable=True)
            action.setChecked(self.settings.language == code)
            action.triggered.connect(lambda _=False, c=code: self._set_language(c))
            group.addAction(action)
            language_menu.addAction(action)

        help_menu = self.menuBar().addMenu("&?")
        about = QAction(tr("Informazioni"), self)
        about.triggered.connect(lambda: QMessageBox.about(
            self, APP_TITLE, f"<b>{APP_TITLE}</b> {__version__}<br>"
                             + tr("Download massivo di media e documenti da Telegram.")))
        help_menu.addAction(about)

    def _set_language(self, code: str) -> None:
        """Cambio lingua al volo: menu e pagine vengono riscritti, il registro già scritto resta com'è."""
        self.settings.language = code
        self.settings.save()
        i18n.set_language(code)
        self._build_menu()
        self.login_page.retranslate()
        self.download_page.retranslate()

    def _set_theme(self, key: str) -> None:
        self.settings.theme = key
        self.settings.save()
        apply_theme(key)

    # ---- connessione -----------------------------------------------------

    async def _startup(self) -> None:
        s = self.settings
        if not (s.api_id and s.api_hash):
            self.login_page.info("Benvenuto! Inserisci le chiavi API per iniziare.")
            return
        self.login_page.set_busy(True)
        self.login_page.info("Connessione a Telegram in corso…")
        try:
            await self.connect_client(s.api_id, s.api_hash)
            if await self.client.is_user_authorized():
                await self._enter_main()
                return
            self.login_page._step = "phone"
            self.login_page.info("Inserisci il numero di telefono con prefisso internazionale.")
        except (OSError, ConnectionError) as e:
            self.login_page.error("Connessione non riuscita: {error}. Controlla la rete e premi «Salva e continua».",
                                  error=e)
        finally:
            self.login_page.set_busy(False)

    async def connect_client(self, api_id: int, api_hash: str) -> None:
        if self.client:
            await self.client.disconnect()
        self.settings.api_id, self.settings.api_hash = api_id, api_hash
        self.settings.save()
        self.client = make_client(api_id, api_hash)
        await self.client.connect()

    async def _enter_main(self) -> None:
        me = await self.client.get_me()
        save_session(self.client)
        self.download_page.activate(self.client, me)
        self.stack.setCurrentWidget(self.download_page)
        self.logout_action.setEnabled(True)
        await self.download_page.refresh_dialogs()
        self.download_page.maybe_resume_follow()

    def set_account_actions_enabled(self, enabled: bool) -> None:
        if not hasattr(self, "logout_action"):
            return
        self.logout_action.setEnabled(enabled and self.stack.currentWidget() is self.download_page)

    def _on_logout(self) -> None:
        answer = QMessageBox.question(self, tr("Esci dall'account"),
                                      tr("Vuoi disconnettere questo PC dal tuo account Telegram?"))
        if answer == QMessageBox.StandardButton.Yes:
            spawn(self._logout())

    async def _logout(self) -> None:
        try:
            await self.client.log_out()
        except Exception:
            log.exception("Logout non riuscito, rimuovo comunque la sessione locale")
        clear_session()
        self.client = None
        self.logout_action.setEnabled(False)
        self.stack.setCurrentWidget(self.login_page)
        self.login_page.set_step("api")
        self.login_page.info("Disconnesso. Puoi accedere di nuovo quando vuoi.")

    # ---- notifiche e chiusura --------------------------------------------

    def set_progress_info(self, percent: float | None, details: str = "", state: str = "normal") -> None:
        """Mostra l'avanzamento nel titolo (visibile passando sull'icona nella barra delle applicazioni),
        nel suggerimento dell'icona vicino all'orologio e come barra verde sull'icona della barra delle
        applicazioni. state: normal | paused | waiting (totale ancora sconosciuto).
        percent=None ripristina lo stato normale."""
        if self.taskbar is None:
            self.taskbar = TaskbarProgress(int(self.winId()))
        if percent is None:
            self.setWindowTitle(APP_TITLE)
            self.tray.setToolTip(APP_TITLE)
            self.taskbar.clear()
            return
        self.setWindowTitle(f"{int(percent)}% · {details.splitlines()[0]} — {APP_TITLE}")
        self.tray.setToolTip(f"{APP_TITLE} — {int(percent)}%\n{details}"[:127])  # limite di Windows
        if state == "waiting":
            self.taskbar.set_state(taskbar.INDETERMINATE)
            return
        self.taskbar.set_state(taskbar.PAUSED if state == "paused" else taskbar.NORMAL)
        self.taskbar.set_value(int(percent * 10), 1000)

    def notify(self, title: str, text: str, critical: bool = False) -> None:
        icon = QSystemTrayIcon.MessageIcon.Critical if critical else QSystemTrayIcon.MessageIcon.Information
        self.tray.showMessage(title, text, icon, 10_000)

    def closeEvent(self, event) -> None:
        if self.download_page.running:
            if self.settings.follow_resume:
                text = tr("Stai seguendo una chat. Chiudere comunque?\n"
                          "Alla riapertura l'app riprenderà da sola, recuperando i file arrivati nel frattempo.")
            else:
                text = tr("Ci sono download in corso. Chiudere comunque?\n"
                          "I file parziali verranno ripresi al prossimo avvio.")
            answer = QMessageBox.question(self, tr("Download in corso"), text)
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.download_page.cancel_for_exit()
        if self.stack.currentWidget() is self.download_page:
            self.download_page.save_settings()
        self.db.close()
        self.tray.hide()
        event.accept()
