"""Finestra principale: instrada tra login e schede (Download / Segui), menu, notifiche."""

import html
import logging
import os

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QPalette
from PyQt6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QStackedWidget, QSystemTrayIcon, QTabWidget, QToolButton, QVBoxLayout, QWidget)
from telethon import utils

from .. import APP_TITLE, __version__, taskbar
from ..taskbar import TaskbarProgress
from .. import i18n
from ..config import Settings, data_dir
from ..i18n import N_, tr
from ..state import StateDB
from ..telegram import clear_session, make_client, save_session
from .common import app_icon, apply_theme, confirm, logout_icon, spawn
from .download_page import DownloadPage
from .follow_page import FollowPage
from .login_page import API_GUIDE, LoginPage

log = logging.getLogger(__name__)

USAGE_GUIDE = N_(
    "<b>Download</b>: scegli la chat da «Chat recenti» (oppure incolla un link t.me o un @username), "
    "la cartella di destinazione e, se vuoi, i filtri: tipi di file, parole contenute nel nome, dimensione. "
    "Poi premi «Avvia download».<br><br>"
    "<b>Segui</b>: aggiungi una o più chat da tenere d'occhio, ognuna con la sua cartella e i suoi filtri. "
    "L'app resta in ascolto e scarica i nuovi file appena arrivano, anche dopo un riavvio. "
    "Con ■ smetti di seguire una chat, con ⏸ la metti in pausa.<br><br>"
    "<b>Account</b>: «Esci» in alto a destra scollega questo PC dal tuo account Telegram "
    "e, se vuoi, cancella anche le chiavi API."
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings.load()
        i18n.set_language(self.settings.language)  # prima di creare le pagine
        self.db = StateDB(data_dir() / "state.db")
        self.client = None
        self.me = None
        self.taskbar: TaskbarProgress | None = None  # creato al primo uso, quando la finestra esiste

        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(app_icon())
        self.resize(1200, 760)

        self.login_page = LoginPage(self)
        self.download_page = DownloadPage(self)
        self.follow_page = FollowPage(self)
        self.main_area = self._build_main_area()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.main_area)
        self.setCentralWidget(self.stack)
        self.login_page.logged_in.connect(lambda: spawn(self._enter_main()))

        self.tray = QSystemTrayIcon(app_icon(), self)
        self.tray.setToolTip(APP_TITLE)
        self.tray.show()

        self._build_menu()
        self._retranslate_main_area()
        apply_theme(self.settings.theme)
        self._paint_icons()
        self.login_page.prefill(self.settings.api_id, self.settings.api_hash)
        self.login_page.set_step("api")
        spawn(self._startup())

    def _build_main_area(self) -> QWidget:
        area = QWidget()
        v = QVBoxLayout(area)
        v.setContentsMargins(6, 4, 6, 0)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self.download_page, "")
        self.tabs.addTab(self.follow_page, "")
        # account e uscita a destra, sulla stessa riga delle schede: niente riga in più che ruba spazio
        corner = QWidget()
        h = QHBoxLayout(corner)
        h.setContentsMargins(0, 0, 4, 0)
        h.setSpacing(6)
        self.account_label = QLabel()
        self.logout_btn = QToolButton()
        self.logout_btn.setAutoRaise(True)
        self.logout_btn.setIconSize(QSize(20, 20))
        self.logout_btn.clicked.connect(self._on_logout)
        h.addWidget(self.account_label)
        h.addWidget(self.logout_btn)
        self.tabs.setCornerWidget(corner, Qt.Corner.TopRightCorner)
        v.addWidget(self.tabs, 1)
        return area

    def _fit_height(self) -> None:
        """Allunga la finestra quanto basta perché la colonna delle impostazioni non debba scorrere,
        senza uscire dallo schermo."""
        missing = self.download_page.missing_height()
        if not missing or self.isMaximized():
            return
        screen = self.screen().availableGeometry()
        title_bar = self.frameGeometry().height() - self.height()
        height = min(self.height() + missing, screen.height() - title_bar)
        top = min(self.y(), screen.bottom() - height - title_bar)
        self.setGeometry(self.x(), max(screen.top() + title_bar, top), self.width(), height)

    def _paint_icons(self) -> None:
        """L'icona di uscita prende il colore del testo: va ridisegnata quando cambia il tema."""
        self.logout_btn.setIcon(logout_icon(QApplication.palette().color(QPalette.ColorRole.WindowText)))

    def _retranslate_main_area(self) -> None:
        self.logout_btn.setToolTip(tr("Esci dall'account"))
        self.tabs.setTabText(0, tr("Download"))
        self.update_follow_tab()
        if self.me:
            who = utils.get_display_name(self.me) or tr("utente")
            phone = f" (+{self.me.phone})" if getattr(self.me, "phone", None) else ""
            self.account_label.setText(tr("Connesso come {name}", name=f"<b>{html.escape(who)}</b>") + phone)

    def update_follow_tab(self) -> None:
        """Il titolo della scheda dice quante chat si stanno seguendo."""
        n = self.follow_page.following_count
        self.tabs.setTabText(1, tr("Segui ({n})", n=n) if n else tr("Segui"))

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

        confirm_close = QAction(tr("Chiedi conferma alla chiusura se ci sono download in corso"), self,
                                checkable=True)
        confirm_close.setChecked(self.settings.confirm_close)
        confirm_close.toggled.connect(self._set_confirm_close)
        view.addAction(confirm_close)

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
        guide = QAction(tr("Guida"), self)
        guide.triggered.connect(self._show_guide)
        help_menu.addAction(guide)
        about = QAction(tr("Informazioni"), self)
        about.triggered.connect(lambda: QMessageBox.about(
            self, APP_TITLE, f"<b>{APP_TITLE}</b> {__version__}<br>"
                             + tr("Download massivo di media e documenti da Telegram.")))
        help_menu.addAction(about)

    def _show_guide(self) -> None:
        box = QMessageBox(self)
        box.setWindowTitle(tr("Guida"))
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)  # link cliccabile
        box.setText(f"<h3>{tr('Le chiavi API')}</h3>{tr(API_GUIDE)}"
                    f"<h3>{tr('Come si usa')}</h3>{tr(USAGE_GUIDE)}")
        box.setStyleSheet("QLabel { min-width: 560px; }")
        box.exec()

    def _set_language(self, code: str) -> None:
        """Cambio lingua al volo: menu e pagine vengono riscritti, il registro già scritto resta com'è."""
        self.settings.language = code
        self.settings.save()
        i18n.set_language(code)
        self._build_menu()
        self.login_page.retranslate()
        self.download_page.retranslate()
        self.follow_page.retranslate()
        self._retranslate_main_area()
        QTimer.singleShot(0, self._fit_height)  # in altre lingue le frasi possono andare a capo

    def _set_confirm_close(self, enabled: bool) -> None:
        self.settings.confirm_close = enabled
        self.settings.save()

    def _set_theme(self, key: str) -> None:
        self.settings.theme = key
        self.settings.save()
        apply_theme(key)
        self._paint_icons()

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
        self.me = await self.client.get_me()
        save_session(self.client)
        self.download_page.activate(self.client, self.me)
        self.follow_page.activate(self.client)
        self._retranslate_main_area()
        self.stack.setCurrentWidget(self.main_area)
        QTimer.singleShot(0, self._fit_height)  # dopo che Qt ha disposto i widget
        self.logout_action.setEnabled(True)
        await self.download_page.refresh_dialogs()  # serve anche alle chat seguite per ritrovare le chat
        self.follow_page.resume_active()

    def _on_logout(self) -> None:
        text = tr("Vuoi disconnettere questo PC dal tuo account Telegram?")
        if self.download_page.running or self.follow_page.following_count:
            text += "\n" + tr("I download in corso e le chat seguite verranno fermati.")
        forget = QCheckBox(tr("Cancella anche le chiavi API (api_id e api_hash) da questo PC"))
        forget.setToolTip(tr("Al prossimo accesso dovrai inserirle di nuovo"))
        if confirm(self, tr("Esci dall'account"), text, tr("Esci"), forget):
            spawn(self._logout(forget.isChecked()))

    async def _logout(self, forget_keys: bool) -> None:
        self.logout_btn.setEnabled(False)
        self.logout_action.setEnabled(False)
        try:
            await self.download_page.stop()
            await self.follow_page.stop_all(deactivate=True)
            try:
                await self.client.log_out()
            except Exception:
                log.exception("Logout non riuscito, rimuovo comunque la sessione locale")
            clear_session()
            self.client = None
            self.me = None
            if forget_keys:
                self.settings.api_id, self.settings.api_hash = 0, ""
                self.settings.save()
                self.login_page.prefill(0, "")
        finally:
            self.logout_btn.setEnabled(True)
        self.stack.setCurrentWidget(self.login_page)
        self.login_page.set_step("api")
        if forget_keys:
            self.login_page.info("Disconnesso e chiavi API cancellate da questo PC.")
        else:
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
        downloading, following = self.download_page.running, self.follow_page.following_count
        if downloading or following:
            if self.settings.confirm_close:
                if following:
                    text = tr("Stai seguendo {n} chat. Chiudere comunque?\n"
                              "Alla riapertura l'app riprenderà da sola, recuperando i file arrivati nel frattempo.",
                              n=following)
                else:
                    text = tr("Ci sono download in corso. Chiudere comunque?\n"
                              "I file parziali verranno ripresi al prossimo avvio.")
                dont_ask = QCheckBox(tr("Non chiedere più (si riattiva dal menu Visualizza)"))
                if not confirm(self, tr("Download in corso"), text, tr("Chiudi"), dont_ask):
                    event.ignore()
                    return
                if dont_ask.isChecked():
                    self.settings.confirm_close = False
                    self.settings.save()
            self.download_page.cancel_for_exit()
            self.follow_page.cancel_for_exit()
        if self.stack.currentWidget() is self.main_area:
            self.download_page.save_settings()
        self.db.close()
        self.tray.hide()
        event.accept()
