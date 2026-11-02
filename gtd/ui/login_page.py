"""Pagina di accesso: chiavi API, numero di telefono, codice OTP e password 2FA."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QWidget)
from telethon import errors

from ..i18n import N_, tr
from ..telegram import save_session
from .common import spawn

if TYPE_CHECKING:
    from .main_window import MainWindow

_INTRO = N_(
    "Per usare l'app servono le <b>chiavi API</b> personali di Telegram (si creano una volta sola):<br>"
    "1. apri <a href='https://my.telegram.org/apps'>my.telegram.org/apps</a> e accedi con il tuo numero;<br>"
    "2. compila il modulo «Create new application» (titolo e nome breve a piacere, piattaforma <i>Desktop</i>);<br>"
    "3. copia qui sotto <b>App api_id</b> e <b>App api_hash</b>.<br>"
    "Le chiavi e la sessione restano solo su questo PC, cifrate con il tuo utente Windows."
)


class LoginPage(QWidget):
    logged_in = pyqtSignal()

    def __init__(self, window: "MainWindow"):
        super().__init__()
        self.win = window
        self._phone = ""
        self._step = "api"
        self._status: tuple[str, str, dict] | None = None  # (stile, testo italiano, valori): ritradotto al volo

        self.box = QGroupBox()
        self.box.setMaximumWidth(620)
        v = QVBoxLayout(self.box)

        self.intro = QLabel()
        self.intro.setWordWrap(True)
        self.intro.setOpenExternalLinks(True)
        self.intro.setTextFormat(Qt.TextFormat.RichText)
        v.addWidget(self.intro)

        form = QFormLayout()
        self.api_id = QLineEdit()
        self.api_id.setValidator(QIntValidator(1, 2_000_000_000))
        self.api_hash = QLineEdit()
        self.api_btn = QPushButton()
        form.addRow("api_id:", self.api_id)
        form.addRow("api_hash:", self.api_hash)
        form.addRow("", self.api_btn)

        self.phone = QLineEdit(placeholderText="+39 333 1234567")
        self.code_btn = QPushButton()
        row = QHBoxLayout()
        row.addWidget(self.phone, 1)
        row.addWidget(self.code_btn)
        self.phone_label = QLabel()
        form.addRow(self.phone_label, row)

        self.code = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_btn = QPushButton()
        self.code_label = QLabel()
        self.password_label = QLabel()
        form.addRow(self.code_label, self.code)
        form.addRow(self.password_label, self.password)
        form.addRow("", self.login_btn)
        v.addLayout(form)

        self.status = QLabel()
        self.status.setWordWrap(True)
        v.addWidget(self.status)

        outer = QVBoxLayout(self)
        outer.addStretch(1)
        h = QHBoxLayout()
        h.addStretch(1)
        h.addWidget(self.box, 3)
        h.addStretch(1)
        outer.addLayout(h)
        outer.addStretch(2)

        self.api_btn.clicked.connect(self._on_api)
        self.api_hash.returnPressed.connect(self._on_api)
        self.code_btn.clicked.connect(self._on_send_code)
        self.phone.returnPressed.connect(self._on_send_code)
        self.login_btn.clicked.connect(self._on_login)
        self.code.returnPressed.connect(self._on_login)
        self.password.returnPressed.connect(self._on_login)
        self.retranslate()

    def retranslate(self) -> None:
        self.box.setTitle(tr("Accesso a Telegram"))
        self.intro.setText(tr(_INTRO))
        self.api_id.setPlaceholderText(tr("es. 1234567"))
        self.api_hash.setPlaceholderText(tr("32 caratteri esadecimali"))
        self.api_btn.setText(tr("Salva e continua"))
        self.phone_label.setText(tr("Telefono:"))
        self.code_btn.setText(tr("Invia codice"))
        self.code_label.setText(tr("Codice:"))
        self.code.setPlaceholderText(tr("codice ricevuto nell'app Telegram"))
        self.password_label.setText(tr("Password 2FA:"))
        self.password.setPlaceholderText(tr("solo se hai attivato la verifica in due passaggi"))
        self.login_btn.setText(tr("Accedi"))
        self._show_status()

    # ---- stato -----------------------------------------------------------

    def prefill(self, api_id: int, api_hash: str) -> None:
        self.api_id.setText(str(api_id) if api_id else "")
        self.api_hash.setText(api_hash)

    def set_step(self, step: str) -> None:
        self._step = step
        order = ["api", "phone", "code", "password"]
        idx = order.index(step)
        self.api_id.setEnabled(True)
        self.api_hash.setEnabled(True)
        self.api_btn.setEnabled(True)
        self.phone.setEnabled(idx >= 1)
        self.code_btn.setEnabled(idx >= 1)
        self.code.setEnabled(idx == 2)
        self.password.setEnabled(idx == 3)
        self.login_btn.setEnabled(idx >= 2)
        if step == "api":
            self.code.clear()
            self.password.clear()
        focus = {"api": self.api_id if not self.api_id.text() else self.api_hash,
                 "phone": self.phone, "code": self.code, "password": self.password}[step]
        focus.setFocus()

    def set_busy(self, busy: bool) -> None:
        for w in (self.api_btn, self.code_btn, self.login_btn):
            w.setEnabled(not busy)
        if not busy:
            self.set_step(self._step)

    def info(self, text: str, **values) -> None:
        """text è il testo italiano (chiave di traduzione): così cambia lingua anche il messaggio già mostrato."""
        self._status = ("", text, values)
        self._show_status()

    def error(self, text: str, **values) -> None:
        self._status = ("color: #d03030;", text, values)
        self._show_status()

    def _show_status(self) -> None:
        if self._status:
            style, text, values = self._status
            self.status.setStyleSheet(style)
            self.status.setText(tr(text, **values))

    # ---- azioni ----------------------------------------------------------

    def _on_api(self) -> None:
        api_id = self.api_id.text().strip()
        api_hash = self.api_hash.text().strip()
        if not api_id.isdigit() or len(api_hash) != 32:
            self.error("Controlla le chiavi: api_id è un numero, api_hash è lungo 32 caratteri.")
            return
        spawn(self._connect(int(api_id), api_hash))

    async def _connect(self, api_id: int, api_hash: str) -> None:
        self.set_busy(True)
        self.info("Connessione a Telegram in corso…")
        try:
            await self.win.connect_client(api_id, api_hash)
            if await self.win.client.is_user_authorized():
                self._finish()
                return
            self._step = "phone"
            self.info("Chiavi salvate. Inserisci il numero di telefono con prefisso internazionale.")
        except (OSError, ConnectionError) as e:
            self.error("Connessione non riuscita: {error}", error=e)
        finally:
            self.set_busy(False)

    def _on_send_code(self) -> None:
        phone = self.phone.text().replace(" ", "")
        if len(phone) < 6:
            self.error("Inserisci il numero completo, es. +393331234567.")
            return
        spawn(self._send_code(phone))

    async def _send_code(self, phone: str) -> None:
        self.set_busy(True)
        self.info("Invio del codice…")
        try:
            await self.win.client.send_code_request(phone)
            self._phone = phone
            self._step = "code"
            self.info("Codice inviato: lo trovi nell'app Telegram (chat «Telegram»).")
        except errors.ApiIdInvalidError:
            self._step = "api"
            self.error("api_id o api_hash non validi: ricontrollali su my.telegram.org.")
        except errors.PhoneNumberInvalidError:
            self.error("Numero di telefono non valido.")
        except errors.FloodWaitError as e:
            self.error("Troppi tentativi: riprova tra {seconds} secondi.", seconds=e.seconds)
        except (errors.RPCError, OSError, ConnectionError) as e:
            self.error("Errore: {error}", error=e)
        finally:
            self.set_busy(False)

    def _on_login(self) -> None:
        if self._step == "code" and self.code.text().strip():
            spawn(self._sign_in_code(self.code.text().strip()))
        elif self._step == "password" and self.password.text():
            spawn(self._sign_in_password(self.password.text()))

    async def _sign_in_code(self, code: str) -> None:
        self.set_busy(True)
        try:
            await self.win.client.sign_in(phone=self._phone, code=code)
            self._finish()
        except errors.SessionPasswordNeededError:
            self._step = "password"
            self.info("Il tuo account ha la verifica in due passaggi: inserisci la password.")
        except (errors.PhoneCodeInvalidError, errors.PhoneCodeEmptyError):
            self.error("Codice errato, riprova.")
        except errors.PhoneCodeExpiredError:
            self.error("Codice scaduto: premi di nuovo «Invia codice».")
        except errors.FloodWaitError as e:
            self.error("Troppi tentativi: riprova tra {seconds} secondi.", seconds=e.seconds)
        except (errors.RPCError, OSError, ConnectionError) as e:
            self.error("Errore: {error}", error=e)
        finally:
            self.set_busy(False)

    async def _sign_in_password(self, password: str) -> None:
        self.set_busy(True)
        try:
            await self.win.client.sign_in(password=password)
            self._finish()
        except errors.PasswordHashInvalidError:
            self.error("Password errata.")
        except errors.FloodWaitError as e:
            self.error("Troppi tentativi: riprova tra {seconds} secondi.", seconds=e.seconds)
        except (errors.RPCError, OSError, ConnectionError) as e:
            self.error("Errore: {error}", error=e)
        finally:
            self.set_busy(False)

    def _finish(self) -> None:
        save_session(self.win.client)
        self.password.clear()
        self.code.clear()
        self.info("Accesso effettuato.")
        self.logged_in.emit()
