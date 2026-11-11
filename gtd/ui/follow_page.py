"""Scheda «Segui»: più chat tenute d'occhio insieme, ognuna con la sua cartella e i suoi filtri."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
                             QFormLayout, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
                             QMenu, QProgressBar, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QToolButton,
                             QVBoxLayout, QWidget)
from telethon import errors, utils

from ..config import FollowedChat
from ..engine import (MAX_PARALLEL, DownloadEngine, FloodGate, JobOptions, Slots, human_eta, human_size,
                      parse_name_filter)
from ..i18n import N_, tr
from ..power import keep_awake
from .common import confirm, file_actions, icon_button, pause_icon, play_icon, spawn, stop_icon
from .download_page import DUPLICATE_POLICIES, MB, PRESETS, extensions_from, filter_text
from .logpanel import LogPanel

if TYPE_CHECKING:
    from .main_window import MainWindow

log = logging.getLogger(__name__)

RETRY_SECONDS = 60  # se una chat seguita si ferma da sola (rete assente a lungo, chat non trovata) si riprova


def _filters(chat: FollowedChat) -> tuple:
    """Cosa decide quali file scaricare: se cambia, ha senso riguardare anche i messaggi vecchi."""
    return (set(chat.presets), extensions_from([], chat.custom_extensions), parse_name_filter(chat.name_filter),
            chat.name_in_caption)


class FollowDialog(QDialog):
    """Aggiunta o modifica di una chat seguita."""

    def __init__(self, parent: QWidget, page: "FollowPage", chat: FollowedChat, editing: bool):
        super().__init__(parent)
        self.setWindowTitle(tr("Modifica chat seguita") if editing else tr("Segui una chat"))
        self.setMinimumWidth(560)
        self.chat = chat
        form = QFormLayout(self)

        self.chat_combo = QComboBox()
        self.chat_combo.setIconSize(QSize(22, 22))
        self.chat_combo.setMaxVisibleItems(20)
        self.chat_combo.addItem(tr("— seleziona una chat —"), None)
        for icon, text, entity in page.win.download_page.chat_entries():
            self.chat_combo.addItem(icon, text, entity)
            if chat.peer_id and utils.get_peer_id(entity) == chat.peer_id:
                self.chat_combo.setCurrentIndex(self.chat_combo.count() - 1)
        if chat.peer_id and self.chat_combo.currentIndex() == 0 and chat.name:  # chat non più nell'elenco
            self.chat_combo.addItem(chat.name, None)
            self.chat_combo.setCurrentIndex(self.chat_combo.count() - 1)
        self.link_edit = QLineEdit(chat.source)
        self.link_edit.setPlaceholderText(tr("https://t.me/… oppure @username"))
        self.link_edit.setToolTip(tr("Se compilato ha la precedenza sulla chat selezionata sopra"))
        self.link_edit.setClearButtonEnabled(True)
        form.addRow(tr("Chat:"), self.chat_combo)
        form.addRow(tr("Link / @username:"), self.link_edit)
        if editing:  # la chat non si cambia: per un'altra chat se ne aggiunge una nuova
            self.chat_combo.setEnabled(False)
            self.link_edit.setEnabled(False)

        dest_row = QHBoxLayout()
        self.dest_edit = QLineEdit(chat.destination)
        self.dest_edit.setPlaceholderText(tr("Cartella locale o di rete"))
        browse = QPushButton(tr("Sfoglia…"))
        browse.clicked.connect(self._browse)
        dest_row.addWidget(self.dest_edit, 1)
        dest_row.addWidget(browse)
        form.addRow(tr("Destinazione:"), dest_row)

        presets = QGridLayout()
        self.preset_checks: dict[str, QCheckBox] = {}
        for i, (name, exts) in enumerate(PRESETS.items()):
            cb = QCheckBox(f"{tr(name)} ({', '.join(e.lstrip('.') for e in exts)})")
            cb.setChecked(name in chat.presets)
            self.preset_checks[name] = cb
            presets.addWidget(cb, i // 2, i % 2)
        form.addRow(tr("Tipi:"), presets)
        self.ext_edit = QLineEdit(chat.custom_extensions)
        self.ext_edit.setPlaceholderText(tr("es. .epub oppure .epub, .mobi"))
        form.addRow(tr("Estensioni:"), self.ext_edit)
        self.name_edit = QLineEdit(chat.name_filter)
        self.name_edit.setPlaceholderText(tr("es. fattura oppure preventivo, offerta"))
        self.name_edit.setClearButtonEnabled(True)
        form.addRow(tr("Nome contiene:"), self.name_edit)
        self.caption_chk = QCheckBox(tr("cerca le parole anche nel testo del messaggio"))
        self.caption_chk.setChecked(chat.name_in_caption)
        form.addRow("", self.caption_chk)

        folders = QHBoxLayout()
        self.by_source = QCheckBox(tr("Per sorgente"))
        self.by_source.setChecked(chat.folder_by_source)
        self.by_type = QCheckBox(tr("Per tipo"))
        self.by_type.setChecked(chat.folder_by_type)
        self.by_date = QCheckBox(tr("Per data (AAAA-MM)"))
        self.by_date.setChecked(chat.folder_by_date)
        for cb in (self.by_source, self.by_type, self.by_date):
            folders.addWidget(cb)
        folders.addStretch(1)
        form.addRow(tr("Sottocartelle:"), folders)

        # come nella scheda Download
        self.dup_combo = QComboBox()
        for label, value in DUPLICATE_POLICIES:
            self.dup_combo.addItem(tr(label), value)
        self.dup_combo.setCurrentIndex(max(0, self.dup_combo.findData(chat.duplicate_policy)))
        form.addRow(tr("File già esistenti:"), self.dup_combo)
        self.dedupe_chk = QCheckBox(tr("Salta i doppioni (stesso file ripubblicato con un altro nome)"))
        self.dedupe_chk.setChecked(chat.skip_duplicates)
        form.addRow("", self.dedupe_chk)
        self.downloaded_chk = QCheckBox(tr("Non riscaricare i file già scaricati in passato, anche se non sono più nella cartella"))
        self.downloaded_chk.setToolTip(tr("Utile se sposti i file altrove (per esempio in un archivio .7z): l'app ricorda cosa ha già scaricato e non lo riscarica, nemmeno con «Ricontrolla da capo»"))
        self.downloaded_chk.setChecked(chat.skip_downloaded)
        form.addRow("", self.downloaded_chk)

        self.history_chk = QCheckBox(tr("Scarica anche i file già presenti nella chat"))
        self.history_chk.setToolTip(tr("Senza spunta vengono scaricati solo i file che arrivano da adesso in poi"))
        if not editing:
            form.addRow("", self.history_chk)

        self.error = QLabel()
        self.error.setStyleSheet("color: #d03030;")
        self.error.hide()
        form.addRow(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(tr("Aggiorna") if editing else tr("Segui"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Annulla"))
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, tr("Cartella di destinazione"), self.dest_edit.text())
        if folder:
            self.dest_edit.setText(str(Path(folder)))

    def _accept(self) -> None:
        link = self.link_edit.text().strip()
        entity = self.chat_combo.currentData()
        if not link and entity is None and not (self.chat.peer_id and not self.chat_combo.isEnabled()):
            return self._fail(tr("Seleziona una chat oppure inserisci un link o @username."))
        dest = self.dest_edit.text().strip()
        if not dest:
            return self._fail(tr("Scegli la cartella in cui salvare i file."))
        try:
            Path(dest).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return self._fail(tr("Impossibile usare la cartella:\n{error}", error=e))
        if self.chat_combo.isEnabled():
            self.chat.source = link
            self.chat.peer_id = 0 if link or entity is None else utils.get_peer_id(entity)
            self.chat.name = "" if link or entity is None else utils.get_display_name(entity)
        self.chat.destination = dest
        self.chat.presets = [n for n, cb in self.preset_checks.items() if cb.isChecked()]
        self.chat.custom_extensions = self.ext_edit.text().strip()
        self.chat.name_filter = self.name_edit.text().strip()
        self.chat.name_in_caption = self.caption_chk.isChecked()
        self.chat.folder_by_source = self.by_source.isChecked()
        self.chat.folder_by_type = self.by_type.isChecked()
        self.chat.folder_by_date = self.by_date.isChecked()
        self.chat.duplicate_policy = self.dup_combo.currentData()
        self.chat.skip_duplicates = self.dedupe_chk.isChecked()
        self.chat.skip_downloaded = self.downloaded_chk.isChecked()
        self.accept()

    def _fail(self, text: str) -> None:
        self.error.setText(text)
        self.error.show()


class _FollowRun:
    """Una chat seguita in esecuzione: fa da Listener del suo motore e tiene lo stato mostrato in tabella."""

    def __init__(self, page: "FollowPage", chat: FollowedChat, with_history: bool):
        self.page = page
        self.chat = chat
        self.with_history = with_history  # solo al primo giro dopo l'aggiunta
        self.engine: DownloadEngine | None = None
        self.task: asyncio.Task | None = None
        self.stop_event = asyncio.Event()
        self.state: tuple[str, dict] = (N_("Avvio…"), {})
        self.last_check: datetime | None = None
        self.new_count = 0
        self.listening = False
        self.done = self.total = 0
        self.done_bytes = self.total_bytes = 0
        self.last_error = ""
        self.paused = False

    @property
    def stopping(self) -> bool:
        return self.stop_event.is_set()

    def set_paused(self, paused: bool) -> None:
        """Vale anche tra un tentativo e l'altro, quando il motore non c'è: lo si applica al prossimo."""
        self.paused = paused
        if self.engine:
            if paused:
                self.engine.pause()
            else:
                self.engine.resume()

    def stop(self) -> None:
        self.stop_event.set()
        if self.engine:
            self.engine.cancel()

    def set_state(self, text: str, **values) -> None:
        """text è il testo italiano: viene tradotto quando si ridisegna la tabella."""
        self.state = (text, values)
        self.page.refresh_row(self.chat)

    @property
    def requeue_left(self) -> int:
        """File sospesi dall'ultima volta non ancora rimessi in coda: per questo il totale cresce."""
        return self.engine.requeue_left if self.engine else 0

    def _update_state(self) -> None:
        percent = int(self.done_bytes * 100 / self.total_bytes) if self.total_bytes else 0
        if self.requeue_left:
            self.set_state(N_("Scarico {done} di {total} file ({percent}%) · il totale cresce: "
                              "altri {left} file in sospeso da riprendere"),
                           done=self.done, total=self.total, percent=percent, left=self.requeue_left)
        elif self.total > self.done:
            self.set_state(N_("Scarico {done} di {total} file ({percent}%)"),
                           done=self.done, total=self.total, percent=percent)
        elif self.listening:
            self.set_state(N_("In ascolto"))

    # ---- Listener --------------------------------------------------------

    def log(self, level: str, text: str) -> None:
        self.page.log(level, text, self.chat.name)

    def scan_progress(self, scanned: int, found: int, finished: bool) -> None:
        if not finished:
            self.set_state(N_("Analisi: {scanned} messaggi letti, {found} file"), scanned=scanned, found=found)

    def overall(self, done_files: int, total_files: int, done_bytes: int, total_bytes: int) -> None:
        self.done, self.total, self.done_bytes, self.total_bytes = done_files, total_files, done_bytes, total_bytes
        self._update_state()
        self.page.update_overall()

    def file_started(self, item) -> None:
        self.page.file_started(self.chat.name, item, self.engine)

    def file_waiting(self, item, text: str) -> None:
        self.page.file_waiting(item, text)

    def file_progress(self, item, speed: float, eta: float | None) -> None:
        self.page.file_progress(item, speed, eta)

    def file_finished(self, item, ok: bool, error: str) -> None:
        self.page.file_finished(item)

    def flood_wait(self, seconds_left: int) -> None:
        self.page.flood_wait(seconds_left)

    def following(self, last_check: datetime) -> None:
        self.listening = True
        self.last_check = last_check
        self._update_state()
        self.page.refresh_row(self.chat)

    def new_files(self, count: int) -> None:
        self.new_count += count
        self.page.refresh_row(self.chat)
        self.page.notify(tr("Nuovi file in arrivo"),
                         tr("{n} nuovi file da «{source}»", n=count, source=self.chat.name))


class FollowPage(QWidget):
    COLUMNS = [N_("Chat"), N_("Destinazione"), N_("Filtri"), N_("Stato"), N_("Ultimo controllo"), N_("Nuovi file")]
    FILE_COLUMNS = [N_("Chat"), N_("File in corso"), N_("Avanzamento"), N_("Velocità"), N_("Tempo rimanente"), ""]

    def __init__(self, window: "MainWindow"):
        super().__init__()
        self.win = window
        self.client = None
        self.flood = FloodGate()  # condiviso anche con la scheda Download: il limite vale per tutto l'account
        self.slots = Slots(window.settings.follow_parallel)  # tutte le chat seguite insieme
        self._runs: dict[int, _FollowRun] = {}  # id(FollowedChat) → esecuzione
        self._flood_left = 0

        v = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.add_btn = QPushButton()
        self.edit_btn = QPushButton()
        self.remove_btn = QPushButton()
        self.rescan_btn = QPushButton()
        self.start_all_btn = icon_button(play_icon(), 22)
        self.stop_all_btn = icon_button(stop_icon(), 22)
        for b in (self.add_btn, self.edit_btn, self.remove_btn, self.rescan_btn):
            bar.addWidget(b)
        bar.addSpacing(16)
        bar.addWidget(self.start_all_btn)
        bar.addWidget(self.stop_all_btn)
        bar.addStretch(1)
        self.parallel_label = QLabel()
        self.parallel_spin = QSpinBox(minimum=1, maximum=MAX_PARALLEL)
        self.parallel_spin.setValue(self.slots.limit)
        bar.addWidget(self.parallel_label)
        bar.addWidget(self.parallel_spin)
        v.addLayout(bar)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        v.addWidget(self.status_label)

        # colonna 0: pulsanti pausa e avvia/ferma della chat; poi le colonne di COLUMNS
        self.table = QTableWidget(0, len(self.COLUMNS) + 1)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(self.fontMetrics().height() + 14)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = self.table.horizontalHeader()
        for col in range(len(self.COLUMNS) + 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1 + self.COLUMNS.index("Stato"), QHeaderView.ResizeMode.Stretch)
        self._controls: dict[int, tuple[QToolButton, QToolButton]] = {}  # id(FollowedChat) → (pausa, avvia/ferma)
        v.addWidget(self.table, 2)

        # avanzamento di tutte le chat seguite insieme (come nella scheda Download)
        self.overall_bar = QProgressBar(maximum=1000)
        self.overall_bar.setFormat("%p%")
        v.addWidget(self.overall_bar)
        self.overall_label = QLabel()
        v.addWidget(self.overall_label)
        self._speed_samples: deque[tuple[float, int]] = deque(maxlen=200)

        # file che si stanno scaricando adesso, di tutte le chat (come nella scheda Download)
        self.files = QTableWidget(0, len(self.FILE_COLUMNS))
        self.files.verticalHeader().hide()
        self.files.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.files.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        fheader = self.files.horizontalHeader()
        fheader.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        fheader.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in (2, 3, 4, 5):
            fheader.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self._row_height = self.files.fontMetrics().height() + 8
        self.files.verticalHeader().setDefaultSectionSize(self._row_height)
        self.files.verticalHeader().setMinimumSectionSize(self._row_height)
        self.files.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._file_rows: dict[tuple[int, int], tuple[QTableWidgetItem, QProgressBar]] = {}
        v.addWidget(self.files)
        self._fit_files_height()

        self.log_panel = LogPanel()
        self.log_panel.warnings_chk.setChecked(window.settings.follow_show_warnings)
        self.log_panel.warnings_chk.toggled.connect(self._on_warnings_toggled)
        v.addWidget(self.log_panel, 3)

        self.add_btn.clicked.connect(lambda: self.add_chat(FollowedChat(destination=self.win.settings.destination)))
        self.edit_btn.clicked.connect(self._on_edit)
        self.remove_btn.clicked.connect(self._on_remove)
        self.rescan_btn.clicked.connect(lambda: self._on_rescan(self._selected()))
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)
        self.start_all_btn.clicked.connect(self._on_start_all)
        self.stop_all_btn.clicked.connect(self._on_stop_all)
        self.table.itemDoubleClicked.connect(lambda _item: self._on_edit())
        self.table.itemSelectionChanged.connect(self._update_buttons)
        self.parallel_spin.valueChanged.connect(self._on_parallel_changed)
        self.retranslate()
        self._fill_table()

    # ---- testi -----------------------------------------------------------

    def retranslate(self) -> None:
        self.add_btn.setText(tr("Aggiungi chat…"))
        self.edit_btn.setText(tr("Modifica…"))
        self.remove_btn.setText(tr("Rimuovi"))
        self.rescan_btn.setText(tr("Ricontrolla da capo…"))
        self.rescan_btn.setToolTip(tr("Rilegge tutta la chat dall'inizio e scarica i file che mancano\n"
                                      "(o tutti, se la chat è impostata per sovrascrivere i file già esistenti)"))
        self.start_all_btn.setToolTip(tr("Avvia tutte"))
        self.stop_all_btn.setToolTip(tr("Ferma tutte"))
        self.files.setHorizontalHeaderLabels([tr(c) if c else "" for c in self.FILE_COLUMNS])
        self.parallel_label.setText(tr("Download paralleli:"))
        self.parallel_spin.setToolTip(tr("Per tutte le chat seguite insieme"))
        self.log_panel.retranslate()
        self.update_overall()
        self.table.setHorizontalHeaderLabels([""] + [tr(c) for c in self.COLUMNS])
        self._fill_table()

    def _update_status(self) -> None:
        n = self.following_count
        if self._flood_left > 0:
            m, s = divmod(self._flood_left, 60)
            self.status_label.setText(tr("Limite di Telegram: ripresa automatica tra {time}", time=f"{m:02d}:{s:02d}"))
            self.status_label.setStyleSheet("color: #d08700; font-weight: bold;")
            return
        self.status_label.setStyleSheet("")
        if not self.win.settings.followed:
            self.status_label.setText(tr("Nessuna chat seguita. Premi «Aggiungi chat…» oppure, nella scheda Download, "
                                         "«Segui questa chat…». L'app scaricherà i nuovi file appena arrivano."))
        elif n:
            self.status_label.setText(tr("Stai seguendo {n} chat: i nuovi file vengono scaricati appena arrivano, "
                                         "anche dopo un riavvio dell'app.", n=n))
        else:
            self.status_label.setText(tr("Nessuna chat attiva: premi ▶ accanto a quelle da seguire."))

    # ---- tabella ---------------------------------------------------------

    def _fill_table(self) -> None:
        chats = self.win.settings.followed
        self.table.setRowCount(len(chats))
        self._controls.clear()
        for row, chat in enumerate(chats):
            self.table.setCellWidget(row, 0, self._make_controls(chat))
            self._fill_row(row, chat)
        self._update_buttons()
        self._update_status()
        if hasattr(self.win, "tabs"):  # alla creazione la finestra non ha ancora le schede
            self.win.update_follow_tab()

    def _make_controls(self, chat: FollowedChat) -> QWidget:
        box = QWidget()
        h = QHBoxLayout(box)
        h.setContentsMargins(4, 0, 4, 0)
        h.setSpacing(2)
        pause = icon_button(pause_icon(), 16)
        play_stop = icon_button(play_icon(), 16)
        pause.clicked.connect(lambda: self._toggle_pause(chat))
        play_stop.clicked.connect(lambda: self._set_active(chat, not chat.active))
        h.addWidget(pause)
        h.addWidget(play_stop)
        self._controls[id(chat)] = (pause, play_stop)
        return box

    def _update_controls(self, chat: FollowedChat) -> None:
        pause, play_stop = self._controls.get(id(chat), (None, None))
        if pause is None:
            return
        run = self._runs.get(id(chat))
        pause.setEnabled(run is not None)
        if run and run.paused:
            pause.setIcon(play_icon())
            pause.setToolTip(tr("Riprendi"))
        else:
            pause.setIcon(pause_icon())
            pause.setToolTip(tr("Pausa: si ferma un momento, senza smettere di seguire la chat"))
        if chat.active:
            play_stop.setIcon(stop_icon())
            play_stop.setToolTip(tr("Ferma: smette di seguire la chat (anche ai prossimi avvii)"))
        else:
            play_stop.setIcon(play_icon())
            play_stop.setToolTip(tr("Avvia: segue la chat e scarica i nuovi file"))

    def _fill_row(self, row: int, chat: FollowedChat) -> None:
        run = self._runs.get(id(chat))
        name = QTableWidgetItem(chat.name or chat.source or str(chat.peer_id))
        exts = extensions_from(chat.presets, chat.custom_extensions)
        if run and run.paused:
            state = tr("In pausa")
        elif run:
            text, values = run.state
            state = tr(text, **values)
        else:
            state = tr("Ferma") if not chat.active else tr("Avvio…")
        cells = [name, QTableWidgetItem(chat.destination), QTableWidgetItem(filter_text(exts, chat.name_filter)),
                 QTableWidgetItem(state),
                 QTableWidgetItem(f"{run.last_check:%H:%M}" if run and run.last_check else "—"),
                 QTableWidgetItem(str(run.new_count) if run and run.new_count else "—")]
        cells[1].setToolTip(chat.destination)
        if run and run.last_error:
            cells[3].setToolTip(run.last_error)
        for col, item in enumerate(cells):
            self.table.setItem(row, col + 1, item)
        self._update_controls(chat)

    def refresh_row(self, chat: FollowedChat) -> None:
        for row, other in enumerate(self.win.settings.followed):
            if other is chat:
                self._fill_row(row, chat)
                break

    def _selected(self) -> FollowedChat | None:
        row = self.table.currentRow()
        chats = self.win.settings.followed
        return chats[row] if 0 <= row < len(chats) and self.table.selectedItems() else None

    def _update_buttons(self) -> None:
        chat = self._selected()
        self.edit_btn.setEnabled(chat is not None)
        self.remove_btn.setEnabled(chat is not None)
        self.rescan_btn.setEnabled(chat is not None)
        chats = self.win.settings.followed
        paused = any(run.paused for run in self._runs.values())
        self.start_all_btn.setEnabled(paused or any(not c.active for c in chats))
        self.stop_all_btn.setEnabled(bool(self._runs) or any(c.active for c in chats))

    # ---- comandi ---------------------------------------------------------

    def add_chat(self, prefill: FollowedChat) -> None:
        """Dalla scheda Download («Segui questa chat…») o da «Aggiungi chat…»."""
        self.win.tabs.setCurrentWidget(self)
        dialog = FollowDialog(self, self, replace(prefill, presets=list(prefill.presets)), editing=False)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        chat = dialog.chat
        for other in self.win.settings.followed:
            if (chat.peer_id and other.peer_id == chat.peer_id) or (chat.source and other.source == chat.source):
                QMessageBox.information(self, tr("Chat già seguita"),
                                        tr("«{source}» è già nell'elenco: usa «Modifica…» per cambiarne le impostazioni.",
                                           source=other.name or other.source))
                return
        chat.active = True
        self.win.settings.followed.append(chat)
        self.win.settings.save()
        self._fill_table()
        self._start(chat, with_history=dialog.history_chk.isChecked())

    def _on_edit(self) -> None:
        chat = self._selected()
        if chat is None:
            return
        draft = replace(chat, presets=list(chat.presets))
        if FollowDialog(self, self, draft, editing=True).exec() != QDialog.DialogCode.Accepted:
            return
        rescan = False
        if _filters(draft) != _filters(chat):
            # di solito i filtri valgono solo per i messaggi nuovi: chi li cambia spesso li vuole anche sui vecchi
            rescan = confirm(self, tr("Filtri cambiati"),
                             tr("Applicare i nuovi filtri anche ai messaggi già arrivati in «{source}»?\n"
                                "L'app rilegge la chat dall'inizio e scarica i file che ora corrispondono; "
                                "quelli già scaricati vengono saltati.", source=chat.name or chat.source),
                             tr("Sì, ricontrolla la chat"), no=tr("Solo ai messaggi nuovi"))
        spawn(self._apply_edit(chat, draft, rescan))

    async def _apply_edit(self, chat: FollowedChat, draft: FollowedChat, rescan: bool) -> None:
        was_running = id(chat) in self._runs
        await self._stop(chat)
        for name in ("destination", "presets", "custom_extensions", "name_filter", "name_in_caption",
                     "folder_by_source", "folder_by_type", "folder_by_date", "duplicate_policy", "skip_duplicates",
                     "skip_downloaded"):
            setattr(chat, name, getattr(draft, name))
        self.log("info", tr("Impostazioni aggiornate"), chat.name)
        if rescan:
            self._begin_rescan(chat)
        else:
            self.win.settings.save()
            if was_running and chat.active:
                self._start(chat)
        self._fill_table()

    def _on_rescan(self, chat: FollowedChat | None) -> None:
        if chat is None:
            return
        source = chat.name or chat.source
        if chat.duplicate_policy == "overwrite":
            text = tr("Rileggo tutta «{source}» dall'inizio e riscarico TUTTI i file che corrispondono ai filtri, "
                      "sovrascrivendo quelli già presenti nella cartella.\n"
                      "Su una chat grande può richiedere molto tempo.", source=source)
        elif chat.skip_downloaded:
            text = tr("Rileggo tutta «{source}» dall'inizio e scarico solo i file mai scaricati prima "
                      "(per esempio quelli che rientrano in filtri nuovi).\n"
                      "I file già scaricati in passato vengono saltati, anche se non sono più nella cartella. "
                      "Su una chat grande la lettura richiede qualche minuto.", source=source)
        else:
            text = tr("Rileggo tutta «{source}» dall'inizio e scarico solo i file che mancano: quelli cancellati "
                      "o spostati dalla cartella e quelli che rientrano nei filtri ma non erano stati scaricati.\n"
                      "I file già presenti vengono saltati. Su una chat grande la lettura richiede qualche minuto.",
                      source=source)
        if confirm(self, tr("Ricontrolla da capo"), text, tr("Ricontrolla")):
            spawn(self._rescan(chat))

    async def _rescan(self, chat: FollowedChat) -> None:
        await self._stop(chat)
        self._begin_rescan(chat)
        self._fill_table()

    def _begin_rescan(self, chat: FollowedChat) -> None:
        """Un giro di lettura completa della chat, poi di nuovo in ascolto come sempre."""
        chat.active = True
        self.win.settings.save()
        self.log("info", tr("Ricontrollo la chat da capo"), chat.name)
        if id(chat) in self._runs:
            # ripartita nel frattempo (es. «Modifica…» confermata mentre si fermava): va fermata di nuovo,
            # altrimenti la rilettura completa verrebbe ignorata
            spawn(self._rescan(chat))
            return
        self._start(chat, with_history=True)

    def _on_context_menu(self, pos) -> None:
        row = self.table.rowAt(pos.y())
        chats = self.win.settings.followed
        if not 0 <= row < len(chats):
            return
        self.table.selectRow(row)
        chat = chats[row]
        run = self._runs.get(id(chat))
        menu = QMenu(self)
        if run:
            menu.addAction(play_icon() if run.paused else pause_icon(),
                           tr("Riprendi") if run.paused else tr("Pausa"), lambda: self._toggle_pause(chat))
        menu.addAction(stop_icon() if chat.active else play_icon(), tr("Ferma") if chat.active else tr("Avvia"),
                       lambda: self._set_active(chat, not chat.active))
        menu.addSeparator()
        menu.addAction(tr("Ricontrolla da capo…"), lambda: self._on_rescan(chat))
        menu.addAction(tr("Modifica…"), self._on_edit)
        menu.addAction(tr("Rimuovi"), self._on_remove)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _on_remove(self) -> None:
        chat = self._selected()
        if chat is None:
            return
        if confirm(self, tr("Rimuovi chat"),
                   tr("Smettere di seguire «{source}» e toglierla dall'elenco?\n"
                      "I file già scaricati restano dove sono.", source=chat.name or chat.source),
                   tr("Rimuovi")):
            spawn(self._remove(chat))

    async def _remove(self, chat: FollowedChat) -> None:
        await self._stop(chat)
        self.win.settings.followed = [c for c in self.win.settings.followed if c is not chat]
        self.win.settings.save()
        self._fill_table()

    def _toggle_pause(self, chat: FollowedChat) -> None:
        """Pausa temporanea: la chat resta seguita (e al prossimo avvio riparte da sola)."""
        run = self._runs.get(id(chat))
        if run is None:
            return
        run.set_paused(not run.paused)
        self.refresh_row(chat)
        self._update_buttons()

    def _on_start_all(self) -> None:
        for chat in self.win.settings.followed:
            run = self._runs.get(id(chat))
            if run and run.paused:
                run.set_paused(False)
            elif not chat.active:
                self._set_active(chat, True)
        self._fill_table()

    def _on_stop_all(self) -> None:
        if self._runs:
            self.log("info", tr("Smetto di seguire tutte le chat"))
        spawn(self.stop_all(deactivate=True))

    def _set_active(self, chat: FollowedChat, active: bool) -> None:
        """Pulsante avvia/ferma: la scelta resta anche al prossimo avvio dell'app."""
        if active == chat.active and (id(chat) in self._runs) == active:
            return
        chat.active = active
        self.win.settings.save()
        if active:
            self._start(chat)
        else:
            self.log("info", tr("Smetto di seguire la chat"), chat.name)
            spawn(self._stop(chat))
        self._fill_table()

    def _on_parallel_changed(self, value: int) -> None:
        self.slots.set_limit(value)  # se aumentano, i download in fila partono subito
        self.win.settings.follow_parallel = value
        self.win.settings.save()
        self._fit_files_height()

    # ---- esecuzione ------------------------------------------------------

    def activate(self, client) -> None:
        self.client = client

    def resume_active(self) -> None:
        """Dopo l'accesso: riprende le chat che erano seguite quando l'app è stata chiusa."""
        active = [c for c in self.win.settings.followed if c.active and id(c) not in self._runs]
        if active:
            self.log("info", tr("Riprendo a seguire {n} chat (recupero dei file arrivati mentre l'app era chiusa)",
                                n=len(active)))
        for chat in active:
            self._start(chat)

    @property
    def following_count(self) -> int:
        return len(self._runs)

    def is_following(self, peer_id: int) -> bool:
        return any(run.chat.peer_id == peer_id for run in self._runs.values())

    def _start(self, chat: FollowedChat, with_history: bool = False) -> None:
        if not self.client or id(chat) in self._runs:
            return
        run = _FollowRun(self, chat, with_history)
        self._runs[id(chat)] = run
        run.task = spawn(self._run(run))
        self._fill_table()

    async def _stop(self, chat: FollowedChat) -> None:
        run = self._runs.get(id(chat))
        if run:
            run.stop()
            await asyncio.wait([run.task])

    async def stop_all(self, deactivate: bool) -> None:
        runs = list(self._runs.values())
        for run in runs:
            run.stop()
        if runs:
            await asyncio.wait([run.task for run in runs])
        if deactivate:
            for chat in self.win.settings.followed:
                chat.active = False
            self.win.settings.save()
        self._fill_table()

    def cancel_for_exit(self) -> None:
        """Chiusura dell'app: si fermano i motori ma le chat restano avviate, così ripartono al prossimo avvio."""
        for run in self._runs.values():
            run.stop()

    async def _resolve(self, chat: FollowedChat):
        dl = self.win.download_page
        if chat.source:
            return await dl.resolve_source(chat.source)
        entity = dl.entity_for(chat.peer_id)
        if entity is None:
            try:
                entity = await self.client.get_entity(chat.peer_id)
            except (ValueError, TypeError):
                raise ValueError(tr("Chat non trovata tra le chat recenti: premi «Aggiorna» nella scheda Download"))
        return entity

    async def _run(self, run: _FollowRun) -> None:
        chat = run.chat
        keep_awake(True)
        try:
            while not run.stopping:
                error = ""
                try:
                    entity = await self._resolve(chat)
                    peer_id = utils.get_peer_id(entity)
                    name = utils.get_display_name(entity) or str(peer_id)
                    if (chat.peer_id, chat.name) != (peer_id, name):
                        chat.peer_id, chat.name = peer_id, name
                        self.win.settings.save()
                    if self.win.download_page.job_peer_id == peer_id:
                        raise ValueError(tr("la chat è in download nella scheda Download: riparto quando ha finito"))
                    if await self._follow(run, entity):
                        break  # fermata da te
                except ValueError as e:
                    error = str(e)
                except (errors.RPCError, OSError, ConnectionError) as e:
                    error = str(e) or type(e).__name__
                except Exception as e:  # imprevisto: lo registriamo e si riprova, la chat non deve fermarsi
                    log.exception("Errore seguendo %s", chat.name)
                    error = str(e) or type(e).__name__
                if run.stopping:
                    break
                if error and error != run.last_error:  # stesso errore ogni minuto: lo si scrive una volta sola
                    self.log("error", error, chat.name or chat.source)
                run.last_error = error
                run.listening = False
                run.set_state(N_("In attesa: nuovo tentativo tra un minuto"))
                try:
                    await asyncio.wait_for(run.stop_event.wait(), RETRY_SECONDS)
                except asyncio.TimeoutError:
                    pass
        finally:
            keep_awake(False)
            run.engine = None
            self._runs.pop(id(chat), None)
            self._fill_table()
            self.update_overall()

    async def _follow(self, run: _FollowRun, entity) -> bool:
        """Un giro del motore: analisi dei messaggi nuovi e poi ascolto. True se fermato da te."""
        chat = run.chat
        peer_id = utils.get_peer_id(entity)
        full_scan = run.with_history
        if not run.with_history and not self.win.db.last_msg_id(peer_id):
            # mai vista prima: si parte da adesso, senza scaricare tutta la storia della chat
            latest = await self.client.get_messages(entity, limit=1)
            if latest:
                self.win.db.set_last_msg_id(peer_id, latest[0].id)
        run.with_history = False
        opts = JobOptions(
            entity=entity, source_name=chat.name, destination=Path(chat.destination),
            extensions=extensions_from(chat.presets, chat.custom_extensions),
            name_words=parse_name_filter(chat.name_filter), name_in_caption=chat.name_in_caption,
            folder_by_source=chat.folder_by_source, folder_by_type=chat.folder_by_type,
            folder_by_date=chat.folder_by_date, parallel=self.slots.limit,
            duplicate_policy=chat.duplicate_policy, skip_duplicates=chat.skip_duplicates,
            skip_downloaded=chat.skip_downloaded, follow=True, resume_from_last=not full_scan)
        run.engine = DownloadEngine(self.client, self.win.db, run, slots=self.slots, flood=self.flood)
        if run.stopping:  # fermata mentre si risolveva la chat
            return True
        if run.paused:  # messa in pausa mentre si aspettava un nuovo tentativo
            run.engine.pause()
        run.last_error = ""
        summary = await run.engine.run(opts)
        run.engine = None
        return summary.cancelled

    # ---- registro e notifiche -------------------------------------------

    def _on_warnings_toggled(self, checked: bool) -> None:
        self.win.settings.follow_show_warnings = checked
        self.win.settings.save()

    def update_overall(self) -> None:
        """Somma l'avanzamento delle chat in esecuzione: file e byte, velocità sugli ultimi 5 secondi."""
        runs = list(self._runs.values())
        done = sum(r.done for r in runs)
        total = sum(r.total for r in runs)
        done_bytes = sum(r.done_bytes for r in runs)
        total_bytes = sum(r.total_bytes for r in runs)
        self.overall_bar.setValue(int(done_bytes * 1000 / total_bytes) if total_bytes else 0)
        if not runs:
            self._speed_samples.clear()
            self.overall_label.setText("")
            return
        now = time.monotonic()
        self._speed_samples.append((now, done_bytes))
        while len(self._speed_samples) > 2 and now - self._speed_samples[0][0] > 5:
            self._speed_samples.popleft()
        (t0, b0), (t1, b1) = self._speed_samples[0], self._speed_samples[-1]
        speed = max(0.0, (b1 - b0) / (t1 - t0)) if t1 > t0 else 0.0
        text = tr("{done} di {total} file  ·  {done_size} di {total_size}", done=done, total=total,
                  done_size=human_size(done_bytes), total_size=human_size(total_bytes))
        if total > done:
            eta = human_eta((total_bytes - done_bytes) / speed if speed > 0 else None)
            text += "  ·  " + tr("{speed} MB/s · mancano {eta}", speed=f"{speed / MB:.1f}", eta=eta)
        left = sum(r.requeue_left for r in runs)
        if left:  # il tempo rimanente vale solo per i file già in coda
            text += "  ·  " + tr("il totale cresce: altri {left} file in sospeso da riprendere", left=left)
        self.overall_label.setText(text)

    def log(self, level: str, text: str, chat_name: str = "") -> None:
        self.log_panel.add(level, text, chat_name)
        log.log({"warning": logging.WARNING, "error": logging.ERROR}.get(level, logging.INFO),
                f"[{chat_name}] {text}" if chat_name else text)

    def notify(self, title: str, text: str) -> None:
        if self.win.download_page.notify_chk.isChecked():
            self.win.notify(title, text)

    def flood_wait(self, seconds_left: int) -> None:
        self._flood_left = seconds_left
        self._update_status()

    # ---- file in corso ---------------------------------------------------

    def _fit_files_height(self) -> None:
        """Alta quanto i download in parallelo: il resto dello spazio va al registro."""
        rows = max(self.slots.limit, self.files.rowCount())
        header = self.files.horizontalHeader().sizeHint().height()
        self.files.setFixedHeight(header + rows * self._row_height + 2 * self.files.frameWidth())

    def file_started(self, chat_name: str, item, engine: DownloadEngine) -> None:
        row = self.files.rowCount()
        self.files.insertRow(row)
        name_item = QTableWidgetItem(item.name)
        name_item.setToolTip(str(item.target))
        bar = QProgressBar(maximum=1000)
        bar.setFormat("%p%")
        bar.setMaximumHeight(self._row_height - 4)
        self.files.setItem(row, 0, QTableWidgetItem(chat_name))
        self.files.setItem(row, 1, name_item)
        self.files.setCellWidget(row, 2, bar)
        self.files.setItem(row, 3, QTableWidgetItem("—"))
        self.files.setItem(row, 4, QTableWidgetItem("—"))
        self.files.setCellWidget(row, 5, file_actions(lambda: engine.retry_now(item), lambda: engine.drop(item)))
        self._file_rows[item.key] = (name_item, bar)
        self._fit_files_height()

    def file_waiting(self, item, text: str) -> None:
        """File iniziato ma fermo (in attesa di riprovare, di un posto libero, in pausa): si dice perché."""
        entry = self._file_rows.get(item.key)
        if entry:
            row = self.files.row(entry[0])
            self.files.item(row, 3).setText(text)
            self.files.item(row, 4).setText("—")

    def file_progress(self, item, speed: float, eta: float | None) -> None:
        entry = self._file_rows.get(item.key)
        if not entry:
            return
        name_item, bar = entry
        row = self.files.row(name_item)
        bar.setValue(int(item.done * 1000 / item.size) if item.size else 0)
        self.files.item(row, 3).setText(f"{speed / MB:.2f} MB/s")
        self.files.item(row, 4).setText(human_eta(eta))

    def file_finished(self, item) -> None:
        entry = self._file_rows.pop(item.key, None)
        if entry:
            self.files.removeRow(self.files.row(entry[0]))
            self._fit_files_height()
