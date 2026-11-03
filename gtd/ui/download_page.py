"""Pagina principale: configurazione del batch e monitoraggio in tempo reale."""

from __future__ import annotations

import asyncio
import html
import logging
import re
import subprocess
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QFileDialog, QFormLayout, QGridLayout,
                             QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
                             QProgressBar, QPushButton, QScrollArea, QSpinBox, QSplitter, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)
from telethon import errors, utils
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.types import ChatInviteAlready, ChatInvitePeek, PeerChannel

from ..config import FollowedChat
from ..engine import (MAX_PARALLEL, DownloadEngine, DownloadItem, JobOptions, Summary, human_eta, human_size,
                      parse_name_filter)
from ..i18n import N_, tr
from ..power import keep_awake
from .avatars import AvatarCache, initials_icon
from .common import confirm, spawn
from .logpanel import LogPanel

if TYPE_CHECKING:
    from .main_window import MainWindow

log = logging.getLogger(__name__)

# le chiavi sono salvate nelle impostazioni: restano in italiano, a video passano da tr()
PRESETS = {
    N_("Documenti"): [".pdf", ".docx", ".epub"],
    N_("Video"): [".mp4", ".mkv"],
    N_("Immagini"): [".jpg", ".jpeg", ".png"],
    N_("Archivi"): [".zip", ".rar", ".7z"],
}
DUPLICATE_POLICIES = [(N_("Salta se già presente"), "skip"), (N_("Rinomina (file_(1).ext)"), "rename"),
                      (N_("Sovrascrivi"), "overwrite")]
MB = 1024 * 1024


def extensions_from(presets: list[str], custom: str) -> set[str]:
    """Estensioni scelte: quelle dei tipi spuntati più quelle scritte a mano («epub, .mobi»)."""
    exts: set[str] = set()
    for name in presets:
        exts.update(PRESETS.get(name, []))
    for token in re.split(r"[,;\s]+", custom):
        token = token.strip().lower()
        if token:
            exts.add(token if token.startswith(".") else "." + token)
    return exts


def filter_text(exts: set[str], name_filter: str) -> str:
    """Riassunto dei filtri a parole, per il registro e per la scheda «Segui»."""
    text = tr("solo {extensions}", extensions=", ".join(sorted(exts))) if exts else tr("tutti i tipi")
    if name_filter.strip():
        text += " · " + tr("nome con «{words}»", words=name_filter.strip())
    return text


class DownloadPage(QWidget):
    def __init__(self, window: "MainWindow"):
        super().__init__()
        self.win = window
        self.client = None
        self.me = None
        self.engine: DownloadEngine | None = None
        self.job_peer_id = 0  # chat del batch in corso: non la si può seguire contemporaneamente
        self._job_task: asyncio.Task | None = None
        self._scanning = False
        self._flood_active = False
        self._speed_samples: deque[tuple[float, int]] = deque(maxlen=200)
        self._totals = (0, 0, 0, 0)
        self.avatars = AvatarCache()
        self._avatar_generation = 0
        self._rows: dict[tuple[int, int], tuple[QTableWidgetItem, QProgressBar]] = {}
        self._texts: list[Callable[[], None]] = []  # scritte da riapplicare quando cambia la lingua
        self._build()
        self.retranslate()
        self._load_settings()
        self._set_running(False)

    # ---- costruzione UI --------------------------------------------------

    def _t(self, setter: Callable[[str], None], text: str) -> None:
        """Registra una scritta statica: viene applicata ora e a ogni cambio di lingua."""
        self._texts.append(lambda: setter(tr(text)))

    def _label(self, text: str) -> QLabel:
        label = QLabel()
        self._t(label.setText, text)
        return label

    def _build(self) -> None:
        # colonna sinistra: configurazione
        left = QWidget()
        lv = QVBoxLayout(left)

        g_src = QGroupBox()
        self._t(g_src.setTitle, "Sorgente")
        fs = QFormLayout(g_src)
        self.chat_combo = QComboBox()
        self.chat_combo.setMinimumWidth(240)
        self.chat_combo.setMaxVisibleItems(20)
        self.chat_combo.setIconSize(QSize(26, 26))
        self.refresh_btn = QPushButton()
        self._t(self.refresh_btn.setText, "Aggiorna")
        row = QHBoxLayout()
        row.addWidget(self.chat_combo, 1)
        row.addWidget(self.refresh_btn)
        fs.addRow(self._label("Chat recenti:"), row)
        self.manual_edit = QLineEdit()
        self._t(self.manual_edit.setPlaceholderText, "https://t.me/… oppure @username")
        self._t(self.manual_edit.setToolTip, "Se compilato ha la precedenza sulla chat selezionata sopra")
        self.manual_edit.setClearButtonEnabled(True)
        self.follow_btn = QPushButton()
        self._t(self.follow_btn.setText, "Segui questa chat…")
        self._t(self.follow_btn.setToolTip,
                "Aggiunge la chat alla scheda «Segui», con questa cartella e questi filtri:\n"
                "l'app scaricherà i nuovi file appena arrivano.")
        self.follow_btn.clicked.connect(self._on_follow)
        row = QHBoxLayout()
        row.addWidget(self.manual_edit, 1)
        row.addWidget(self.follow_btn)
        fs.addRow(self._label("Link / @username:"), row)
        lv.addWidget(g_src)

        g_dst = QGroupBox()
        self._t(g_dst.setTitle, "Destinazione")
        hd = QHBoxLayout(g_dst)
        self.dest_edit = QLineEdit()
        self._t(self.dest_edit.setPlaceholderText, "Cartella locale o di rete")
        self.browse_btn = QPushButton()
        self._t(self.browse_btn.setText, "Sfoglia…")
        hd.addWidget(self.dest_edit, 1)
        hd.addWidget(self.browse_btn)
        lv.addWidget(g_dst)

        g_flt = QGroupBox()
        self._t(g_flt.setTitle, "Filtri")
        ff = QFormLayout(g_flt)
        presets_grid = QGridLayout()
        self.preset_checks: dict[str, QCheckBox] = {}
        for i, (name, exts) in enumerate(PRESETS.items()):
            cb = QCheckBox()
            listed = ", ".join(e.lstrip(".") for e in exts)
            self._texts.append(lambda cb=cb, name=name, listed=listed: cb.setText(f"{tr(name)} ({listed})"))
            self.preset_checks[name] = cb
            presets_grid.addWidget(cb, i // 2, i % 2)
            cb.toggled.connect(self._update_filter_summary)
        ff.addRow(self._label("Tipi:"), presets_grid)
        self.custom_ext = QLineEdit()
        self._t(self.custom_ext.setPlaceholderText, "es. .epub oppure .epub, .mobi")
        self.custom_ext.textChanged.connect(self._update_filter_summary)
        ff.addRow(self._label("Estensioni:"), self.custom_ext)
        self.name_edit = QLineEdit()
        self.name_edit.setClearButtonEnabled(True)
        self._t(self.name_edit.setPlaceholderText, "es. fattura oppure preventivo, offerta")
        self._t(self.name_edit.setToolTip,
                "Scarica solo i file che contengono una di queste parole (separate da virgola).\n"
                "Maiuscole e accenti non contano. Vuoto = qualsiasi nome.")
        self.name_edit.textChanged.connect(self._update_filter_summary)
        ff.addRow(self._label("Nome contiene:"), self.name_edit)
        self.caption_chk = QCheckBox()
        self._t(self.caption_chk.setText, "cerca le parole anche nel testo del messaggio")
        self._t(self.caption_chk.setToolTip,
                "Utile per le foto, che non hanno un nome, e per i canali che descrivono il file nel messaggio")
        self.caption_chk.toggled.connect(self._update_filter_summary)
        ff.addRow("", self.caption_chk)
        self.filter_summary = QLabel()
        self.filter_summary.setWordWrap(True)
        ff.addRow(self._label("Scarico:"), self.filter_summary)
        size_row = QHBoxLayout()
        self.min_size = QSpinBox(suffix=" MB", maximum=4096)
        self.max_size = QSpinBox(suffix=" MB", maximum=4096)
        self._t(self.max_size.setSpecialValueText, "nessun limite")
        size_row.addWidget(self._label("da"))
        size_row.addWidget(self.min_size)
        size_row.addWidget(self._label("a"))
        size_row.addWidget(self.max_size)
        size_row.addStretch(1)
        ff.addRow(self._label("Dimensione:"), size_row)
        lv.addWidget(g_flt)

        g_opt = QGroupBox()
        self._t(g_opt.setTitle, "Opzioni")
        fo = QFormLayout(g_opt)
        self.dup_combo = QComboBox()
        for label, value in DUPLICATE_POLICIES:
            self.dup_combo.addItem(label, value)
        self._texts.append(self._retranslate_dup_combo)
        fo.addRow(self._label("File già esistenti:"), self.dup_combo)
        folders_row = QHBoxLayout()
        self.by_source = QCheckBox()
        self._t(self.by_source.setText, "Per sorgente")
        self.by_type = QCheckBox()
        self._t(self.by_type.setText, "Per tipo")
        self.by_date = QCheckBox()
        self._t(self.by_date.setText, "Per data (AAAA-MM)")
        for cb in (self.by_source, self.by_type, self.by_date):
            folders_row.addWidget(cb)
        folders_row.addStretch(1)
        fo.addRow(self._label("Sottocartelle:"), folders_row)
        self.parallel_spin = QSpinBox(minimum=1, maximum=MAX_PARALLEL)
        self._t(self.parallel_spin.setToolTip, "Durante un download si può cambiare mettendo in pausa")
        self.parallel_spin.valueChanged.connect(self._on_parallel_changed)
        fo.addRow(self._label("Download paralleli:"), self.parallel_spin)
        self.dedupe_chk = QCheckBox()
        self._t(self.dedupe_chk.setText, "Salta i doppioni (stesso file ripubblicato con un altro nome)")
        self.notify_chk = QCheckBox()
        self._t(self.notify_chk.setText, "Notifiche di Windows (fine batch, errori, nuovi file)")
        self.shutdown_chk = QCheckBox()
        self._t(self.shutdown_chk.setText, "Spegni il PC al termine")
        for cb in (self.dedupe_chk, self.notify_chk, self.shutdown_chk):
            fo.addRow("", cb)
        lv.addWidget(g_opt)

        buttons = QHBoxLayout()
        self.start_btn = QPushButton()
        self._t(self.start_btn.setText, "Avvia download")
        self.start_btn.setDefault(True)
        self.start_btn.setMinimumHeight(34)
        self.pause_btn = QPushButton()
        self.cancel_btn = QPushButton()
        self._texts.append(self._retranslate_job_buttons)
        buttons.addWidget(self.start_btn, 2)
        buttons.addWidget(self.pause_btn, 1)
        buttons.addWidget(self.cancel_btn, 1)
        lv.addLayout(buttons)
        lv.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._left, self._scroll = left, scroll

        # colonna destra: monitoraggio
        right = QWidget()
        rv = QVBoxLayout(right)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        rv.addWidget(self.status_label)
        self.flood_label = QLabel()
        self.flood_label.setStyleSheet("color: #d08700; font-weight: bold;")
        self.flood_label.hide()
        rv.addWidget(self.flood_label)
        self.overall_bar = QProgressBar(maximum=1000)
        self.overall_bar.setFormat("%p%")
        rv.addWidget(self.overall_bar)
        self.overall_label = QLabel()
        rv.addWidget(self.overall_label)

        self.table = QTableWidget(0, 4)
        self._texts.append(lambda: self.table.setHorizontalHeaderLabels(
            [tr("File in corso"), tr("Avanzamento"), tr("Velocità"), tr("Tempo rimanente")]))
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2, 3):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        # righe compatte: la tabella è alta esattamente quanto i download in parallelo, il resto va al registro
        self._row_height = self.table.fontMetrics().height() + 8
        self.table.verticalHeader().setDefaultSectionSize(self._row_height)
        self.table.verticalHeader().setMinimumSectionSize(self._row_height)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rv.addWidget(self.table)

        self.log_panel = LogPanel()
        self._texts.append(self.log_panel.retranslate)
        rv.addWidget(self.log_panel, 1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(scroll)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        QVBoxLayout(self).addWidget(splitter)

        self.refresh_btn.clicked.connect(lambda: spawn(self.refresh_dialogs()))
        self.browse_btn.clicked.connect(self._browse)
        self.start_btn.clicked.connect(self._on_start)
        self.pause_btn.clicked.connect(self._on_pause)
        self.cancel_btn.clicked.connect(self._on_cancel)

    # ---- lingua ----------------------------------------------------------

    def retranslate(self) -> None:
        """Riapplica tutte le scritte nella lingua attiva (le righe già nel registro restano come sono)."""
        for apply_text in self._texts:
            apply_text()
        self._update_filter_summary()
        if not self.running:
            self.status_label.setText(tr("Pronto."))
        if self.chat_combo.count() and self.chat_combo.itemData(0) is None:
            self.chat_combo.setItemText(0, tr("— seleziona una chat —"))
        self._fit_left_column()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._fit_left_column()  # le misure dei widget nascosti non sono affidabili: si ricalcola alla comparsa

    def _on_parallel_changed(self, value: int) -> None:
        if self.engine:  # modificabile solo in pausa: il motore si adegua alla ripresa
            self.engine.set_parallel(value)
            self.win.settings.parallel = value
            self.win.settings.save()
        self._fit_table_height()

    def _fit_table_height(self) -> None:
        # se i paralleli sono stati ridotti in pausa, restano visibili anche i download già avviati
        rows = max(self.parallel_spin.value(), self.table.rowCount())
        header = self.table.horizontalHeader().sizeHint().height()
        self.table.setFixedHeight(header + rows * self._row_height + 2 * self.table.frameWidth())

    def _fit_left_column(self) -> None:
        """Le lingue hanno frasi di lunghezza diversa: la colonna delle impostazioni si allarga quanto serve."""
        special = self.max_size.specialValueText()
        self.max_size.setMinimumWidth(self.max_size.fontMetrics().horizontalAdvance(special) + 40)
        self._left.layout().activate()
        needed = self._left.sizeHint().width() + self._scroll.verticalScrollBar().sizeHint().width() + 8
        self._scroll.setMinimumWidth(max(460, needed))

    def missing_height(self) -> int:
        """Pixel che mancano perché le impostazioni stiano tutte senza barra di scorrimento."""
        self._left.layout().activate()
        return max(0, self._left.minimumSizeHint().height() - self._scroll.viewport().height())

    def _retranslate_dup_combo(self) -> None:
        for i, (label, _value) in enumerate(DUPLICATE_POLICIES):
            self.dup_combo.setItemText(i, tr(label))

    def _retranslate_job_buttons(self) -> None:
        self.pause_btn.setText(tr("Riprendi") if self.engine and self.engine.paused else tr("Pausa"))
        self.cancel_btn.setText(tr("Annulla"))

    # ---- impostazioni ----------------------------------------------------

    def _load_settings(self) -> None:
        s = self.win.settings
        self.dest_edit.setText(s.destination)
        self.manual_edit.setText(s.last_manual_source)
        for name, cb in self.preset_checks.items():
            cb.setChecked(name in s.presets)
        self.custom_ext.setText(s.custom_extensions)
        self.name_edit.setText(s.name_filter)
        self.caption_chk.setChecked(s.name_in_caption)
        self._update_filter_summary()
        self.min_size.setValue(s.min_size_mb)
        self.max_size.setValue(s.max_size_mb)
        idx = self.dup_combo.findData(s.duplicate_policy)
        self.dup_combo.setCurrentIndex(max(0, idx))
        self.by_source.setChecked(s.folder_by_source)
        self.by_type.setChecked(s.folder_by_type)
        self.by_date.setChecked(s.folder_by_date)
        self.parallel_spin.setValue(s.parallel)
        self._fit_table_height()
        self.notify_chk.setChecked(s.notifications)
        self.dedupe_chk.setChecked(s.skip_duplicates)
        self.log_panel.warnings_chk.setChecked(s.show_warnings)

    def save_settings(self) -> None:
        s = self.win.settings
        s.destination = self.dest_edit.text().strip()
        s.last_manual_source = self.manual_edit.text().strip()
        entity = self.chat_combo.currentData()
        if entity is not None:
            s.last_source_id = utils.get_peer_id(entity)
        s.presets = [n for n, cb in self.preset_checks.items() if cb.isChecked()]
        s.custom_extensions = self.custom_ext.text().strip()
        s.name_filter = self.name_edit.text().strip()
        s.name_in_caption = self.caption_chk.isChecked()
        s.min_size_mb = self.min_size.value()
        s.max_size_mb = self.max_size.value()
        s.duplicate_policy = self.dup_combo.currentData()
        s.folder_by_source = self.by_source.isChecked()
        s.folder_by_type = self.by_type.isChecked()
        s.folder_by_date = self.by_date.isChecked()
        s.parallel = self.parallel_spin.value()
        s.notifications = self.notify_chk.isChecked()
        s.skip_duplicates = self.dedupe_chk.isChecked()
        s.show_warnings = self.log_panel.warnings_chk.isChecked()
        s.save()

    def _update_filter_summary(self) -> None:
        if not hasattr(self, "filter_summary"):
            return
        exts = self._selected_extensions()
        words = self.name_edit.text().strip()
        if exts or words:
            self.filter_summary.setText("<b>" + html.escape(filter_text(exts, words)) + "</b>")
            self.filter_summary.setStyleSheet("")
        else:
            self.filter_summary.setText(tr("<b>tutti i tipi di file</b> (nessun tipo selezionato)"))
            self.filter_summary.setStyleSheet("color: #d08700;")

    def _selected_extensions(self) -> set[str]:
        return extensions_from([n for n, cb in self.preset_checks.items() if cb.isChecked()], self.custom_ext.text())

    # ---- account e chat --------------------------------------------------

    def activate(self, client, me) -> None:
        self.client = client
        self.me = me
        self.log("info", tr("Accesso effettuato come {name}", name=utils.get_display_name(me) or tr("utente")))

    def chat_entries(self) -> list[tuple]:
        """Le chat recenti già caricate (icona, testo, entità): servono anche alla scheda «Segui»."""
        return [(self.chat_combo.itemIcon(i), self.chat_combo.itemText(i), self.chat_combo.itemData(i))
                for i in range(self.chat_combo.count()) if self.chat_combo.itemData(i) is not None]

    def entity_for(self, peer_id: int):
        for _icon, _text, entity in self.chat_entries():
            if utils.get_peer_id(entity) == peer_id:
                return entity
        return None

    async def refresh_dialogs(self) -> None:
        if not self.client:
            return
        self.refresh_btn.setEnabled(False)
        self._avatar_generation += 1
        self.chat_combo.clear()
        self.chat_combo.addItem(tr("Caricamento chat…"), None)
        wanted = self.win.settings.last_source_id
        try:
            entries = []
            async for d in self.client.iter_dialogs(limit=500):
                if d.is_channel and not d.is_group:
                    kind = tr("canale")
                elif d.is_group:
                    kind = tr("gruppo")
                else:
                    kind = tr("chat")
                entries.append((d.name or tr("senza nome"), kind, d.entity, d.id))
            self.chat_combo.clear()
            self.chat_combo.addItem(tr("— seleziona una chat —"), None)
            to_fetch = []
            for name, kind, entity, peer_id in entries:
                icon = self.avatars.cached_icon(entity)
                if icon is None:
                    icon = initials_icon(name, peer_id)
                    if self.avatars.has_photo(entity):
                        to_fetch.append((self.chat_combo.count(), entity))
                self.chat_combo.addItem(icon, f"{name}  ·  {kind}", entity)
                if peer_id == wanted:
                    self.chat_combo.setCurrentIndex(self.chat_combo.count() - 1)
            self.log("info", tr("Caricate {n} chat recenti", n=len(entries)))
            if to_fetch:
                spawn(self._load_avatars(self._avatar_generation, to_fetch))
        except errors.FloodWaitError as e:
            self.chat_combo.clear()
            self.log("warning", tr("Telegram chiede di attendere {seconds}s prima di ricaricare le chat",
                                   seconds=e.seconds))
        except (errors.RPCError, OSError, ConnectionError) as e:
            self.chat_combo.clear()
            self.log("error", tr("Impossibile caricare le chat: {error}", error=e))
        finally:
            self.refresh_btn.setEnabled(True)

    async def _load_avatars(self, generation: int, pending: list) -> None:
        """Scarica in background le foto profilo mancanti (poche alla volta, per non disturbare Telegram)."""
        limit = asyncio.Semaphore(3)

        async def one(index: int, entity) -> None:
            async with limit:
                if generation != self._avatar_generation:
                    return
                try:
                    icon = await self.avatars.fetch_icon(self.client, entity)
                except errors.FloodWaitError:
                    self._avatar_generation += 1  # Telegram chiede di rallentare: le altre al prossimo «Aggiorna»
                    return
                except (errors.RPCError, OSError, ConnectionError, ValueError):
                    return
                if icon and generation == self._avatar_generation and index < self.chat_combo.count():
                    self.chat_combo.setItemIcon(index, icon)

        await asyncio.gather(*(one(i, e) for i, e in pending))

    async def resolve_source(self, manual: str):
        """Link t.me / @username (vuoto = chat scelta nell'elenco) → entità. ValueError con un messaggio per l'utente."""
        if not manual:
            return self.chat_combo.currentData()
        try:
            invite = re.search(r"(?:joinchat/|t\.me/\+|^\+)([\w-]+)", manual)
            if invite:
                res = await self.client(CheckChatInviteRequest(invite.group(1)))
                if isinstance(res, (ChatInviteAlready, ChatInvitePeek)):
                    return res.chat
                raise ValueError(tr("Non sei ancora membro di questa chat: unisciti dal client Telegram e riprova."))
            private = re.search(r"t\.me/c/(\d+)", manual)
            if private:
                return await self.client.get_entity(PeerChannel(int(private.group(1))))
            return await self.client.get_entity(manual)
        except errors.InviteHashExpiredError:
            raise ValueError(tr("Il link di invito è scaduto o non valido."))
        except (errors.RPCError, TypeError) as e:
            raise ValueError(tr("Sorgente non trovata: {error}", error=e))

    # ---- comandi ---------------------------------------------------------

    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, tr("Cartella di destinazione"), self.dest_edit.text())
        if folder:
            self.dest_edit.setText(str(Path(folder)))

    def _on_start(self) -> None:
        dest = self.dest_edit.text().strip()
        manual = self.manual_edit.text().strip()
        if not self.client:
            return
        if not manual and self.chat_combo.currentData() is None:
            QMessageBox.warning(self, tr("Sorgente mancante"),
                                tr("Seleziona una chat oppure inserisci un link o @username."))
            return
        if not dest:
            QMessageBox.warning(self, tr("Destinazione mancante"), tr("Scegli la cartella in cui salvare i file."))
            return
        if self.max_size.value() and self.max_size.value() < self.min_size.value():
            QMessageBox.warning(self, tr("Filtro dimensione"), tr("La dimensione massima è inferiore alla minima."))
            return
        try:
            Path(dest).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            QMessageBox.warning(self, tr("Destinazione non valida"),
                                tr("Impossibile usare la cartella:\n{error}", error=e))
            return
        if self.shutdown_chk.isChecked():
            if not confirm(self, tr("Spegnimento automatico"),
                           tr("Al termine dei download il PC verrà spento (con 2 minuti di preavviso). Confermi?"),
                           tr("Conferma")):
                self.shutdown_chk.setChecked(False)
        self.save_settings()
        self._job_task = spawn(self._run_job(manual, Path(dest)))

    def _on_follow(self) -> None:
        """Propone alla scheda «Segui» la chat scelta qui, con la stessa cartella e gli stessi filtri."""
        manual = self.manual_edit.text().strip()
        entity = None if manual else self.chat_combo.currentData()
        chat = FollowedChat(
            peer_id=utils.get_peer_id(entity) if entity is not None else 0,
            source=manual, name=utils.get_display_name(entity) if entity is not None else "",
            destination=self.dest_edit.text().strip(),
            presets=[n for n, cb in self.preset_checks.items() if cb.isChecked()],
            custom_extensions=self.custom_ext.text().strip(), name_filter=self.name_edit.text().strip(),
            name_in_caption=self.caption_chk.isChecked(), folder_by_source=self.by_source.isChecked(),
            folder_by_type=self.by_type.isChecked(), folder_by_date=self.by_date.isChecked())
        self.win.follow_page.add_chat(chat)

    def _on_pause(self) -> None:
        if not self.engine:
            return
        if self.engine.paused:
            self.engine.resume()
        else:
            self.engine.pause()
        # in pausa si può cambiare il numero di download paralleli
        self.parallel_spin.setEnabled(self.engine.paused)
        self._retranslate_job_buttons()
        self._publish_info()

    def _on_cancel(self) -> None:
        if self.engine:
            self.log("warning", tr("Annullamento in corso… i file parziali verranno ripresi al prossimo avvio"))
            self.engine.cancel()
            self.cancel_btn.setEnabled(False)

    def cancel_for_exit(self) -> None:
        if self.engine:
            self.engine.cancel()

    async def stop(self) -> None:
        """Annulla il batch in corso e aspetta che sia fermo (es. prima del logout)."""
        if self.engine:
            self.engine.cancel()
        if self._job_task and not self._job_task.done():
            await asyncio.wait([self._job_task])

    @property
    def running(self) -> bool:
        return self.engine is not None or self._scanning

    async def _run_job(self, manual: str, dest: Path) -> None:
        self._set_running(True)
        self.overall_bar.setValue(0)
        self.overall_label.clear()
        self._scanning = True
        self._speed_samples.clear()
        self._totals = (0, 0, 0, 0)
        self.status_label.setText(tr("Analisi della chat in corso…"))
        keep_awake(True)  # niente sospensione di Windows mentre lavoriamo (era la causa dei blocchi notturni)
        summary: Summary | None = None
        try:
            try:
                entity = await self.resolve_source(manual)
            except ValueError as e:
                self.log("error", str(e))
                return
            peer_id = utils.get_peer_id(entity)
            name = utils.get_display_name(entity) or str(peer_id)
            if self.win.follow_page.is_following(peer_id):
                self.log("error", tr("«{source}» è già seguita nella scheda «Segui», che ne scarica i file: "
                                     "fermala con ■ se vuoi scaricarla da qui", source=name))
                return
            opts = JobOptions(
                entity=entity, source_name=name, destination=dest,
                extensions=self._selected_extensions(),
                name_words=parse_name_filter(self.name_edit.text()), name_in_caption=self.caption_chk.isChecked(),
                min_size=self.min_size.value() * MB, max_size=self.max_size.value() * MB,
                duplicate_policy=self.dup_combo.currentData(),
                folder_by_source=self.by_source.isChecked(), folder_by_type=self.by_type.isChecked(),
                folder_by_date=self.by_date.isChecked(), parallel=self.parallel_spin.value(),
                skip_duplicates=self.dedupe_chk.isChecked())
            self.log("info", tr("Avvio batch: «{source}» → {destination} (filtro: {filter})", source=name,
                                destination=dest, filter=filter_text(opts.extensions, self.name_edit.text())))
            self.job_peer_id = peer_id
            # FloodWait condiviso con le chat seguite: il limite di Telegram vale per tutto l'account
            self.engine = DownloadEngine(self.client, self.win.db, self, flood=self.win.follow_page.flood)
            self.win.set_progress_info(0, tr("Analisi della chat in corso…"), "waiting")
            summary = await self.engine.run(opts)
        except Exception as e:  # errore imprevisto: lo mostriamo invece di perderlo
            log.exception("Errore durante il batch")
            self.log("error", tr("Errore critico: {error}", error=e))
            self._notify(tr("Errore durante il download"), str(e), critical=True)
            if self.engine:
                self.engine.cancel()  # nessun download deve restare a girare «invisibile»
        finally:
            keep_awake(False)
            self.engine = None
            self.job_peer_id = 0
            self._scanning = False
            self.win.set_progress_info(None)
            self._set_running(False)
            self.flood_label.hide()
            self.table.setRowCount(0)
            self._rows.clear()
        if summary:
            self._report(summary)
        self._retranslate_job_buttons()

    def _report(self, s: Summary) -> None:
        text = tr("{completed} scaricati ({size}), {skipped} saltati (di cui {duplicates} doppioni), "
                  "{failed} non riusciti", completed=s.completed, size=human_size(s.downloaded_bytes),
                  skipped=s.skipped, duplicates=s.duplicates, failed=s.failed)
        if s.cancelled:
            prefix = tr("Annullato.")
            self.status_label.setText(f"{prefix} {text}")
            self.log("warning", f"{prefix} {text}")
            return
        self.status_label.setText(f"{tr('Completato.')} {text}")
        self.log("success" if not s.failed else "warning", tr("Batch terminato: {summary}", summary=text))
        self._notify(tr("Download completati") if not s.failed else tr("Download terminati con errori"), text,
                     critical=bool(s.failed))
        if self.shutdown_chk.isChecked():
            self.shutdown_chk.setChecked(False)
            self._schedule_shutdown()

    def _schedule_shutdown(self) -> None:
        try:
            subprocess.run(["shutdown", "/s", "/t", "120", "/c",
                            "Gerard Telegram Downloader: " + tr("download completati")],
                           check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log("warning", tr("Il PC si spegnerà tra 2 minuti. Per annullare: Win+R → «shutdown /a»"))
        except (OSError, subprocess.CalledProcessError) as e:
            self.log("error", tr("Spegnimento automatico non riuscito: {error}", error=e))

    def _notify(self, title: str, text: str, critical: bool = False) -> None:
        if self.notify_chk.isChecked():
            self.win.notify(title, text, critical)

    def _set_running(self, running: bool) -> None:
        for w in (self.chat_combo, self.refresh_btn, self.manual_edit, self.dest_edit, self.browse_btn,
                  self.custom_ext, self.min_size, self.max_size, self.dup_combo, self.by_source, self.by_type,
                  self.by_date, self.parallel_spin, self.dedupe_chk, self.name_edit, self.caption_chk,
                  self.shutdown_chk, *self.preset_checks.values()):
            w.setEnabled(not running)
        self.start_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running)
        self.cancel_btn.setEnabled(running)
        self._retranslate_job_buttons()

    # ---- registro --------------------------------------------------------

    def log(self, level: str, text: str) -> None:
        """level: info | success | skip | warning | error. skip e warning sono le righe gialle «avvisi»."""
        self.log_panel.add(level, text)
        log.log({"warning": logging.WARNING, "error": logging.ERROR}.get(level, logging.INFO), text)

    # ---- Listener del motore ---------------------------------------------

    # i batch di questa scheda non seguono la chat (lo fa la scheda «Segui»): richiesti solo dal Listener
    def following(self, last_check: datetime) -> None:
        pass

    def new_files(self, count: int) -> None:
        pass

    def scan_progress(self, scanned: int, found: int, finished: bool) -> None:
        self._scanning = not finished
        if finished:
            self.status_label.setText(tr("Analisi completata ({scanned} messaggi, {found} file). Download in corso…",
                                         scanned=scanned, found=found))
        else:
            self.status_label.setText(tr("Analisi in corso: {scanned} messaggi letti, {found} file trovati "
                                         "— i download sono già partiti", scanned=scanned, found=found))

    def overall(self, done_files: int, total_files: int, done_bytes: int, total_bytes: int) -> None:
        self.overall_bar.setValue(int(done_bytes * 1000 / total_bytes) if total_bytes else 0)
        text = tr("{done} di {total} file  ·  {done_size} di {total_size}", done=done_files, total=total_files,
                  done_size=human_size(done_bytes), total_size=human_size(total_bytes))
        if self._scanning:
            text += " " + tr("(in aumento, analisi in corso)")
        self.overall_label.setText(text)
        now = time.monotonic()
        self._speed_samples.append((now, done_bytes))
        while len(self._speed_samples) > 2 and now - self._speed_samples[0][0] > 5:
            self._speed_samples.popleft()
        self._totals = (done_files, total_files, done_bytes, total_bytes)
        self._publish_info()

    def _publish_info(self) -> None:
        """Riepilogo per la barra delle applicazioni e l'icona vicino all'orologio."""
        if not self.engine:
            self.win.set_progress_info(None)
            return
        if not self._speed_samples:
            return
        done_files, total_files, done_bytes, total_bytes = self._totals
        percent = done_bytes * 100 / total_bytes if total_bytes else 0.0
        (t0, b0), (t1, b1) = self._speed_samples[0], self._speed_samples[-1]
        speed = (b1 - b0) / (t1 - t0) if t1 > t0 else 0.0
        bar_state = "normal"
        if self.engine.paused:
            text, bar_state = tr("In pausa"), "paused"
        elif self._flood_active:
            text, bar_state = tr("Attesa limite Telegram"), "paused"
        else:
            eta = human_eta((total_bytes - done_bytes) / speed if speed > 0 else None)
            text = tr("{speed} MB/s · mancano {eta}", speed=f"{speed / MB:.1f}", eta=eta)
            if self._scanning:
                text += " " + tr("(stima, analisi in corso)")
        if not total_bytes:
            bar_state = "waiting"  # nessun file ancora trovato: barra animata
        summary = tr("{done}/{total} file · {done_size} di {total_size}", done=done_files, total=total_files,
                     done_size=human_size(done_bytes), total_size=human_size(total_bytes))
        self.win.set_progress_info(percent, f"{summary}\n{text}", bar_state)

    def file_started(self, item: DownloadItem) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        name_item = QTableWidgetItem(item.name)
        name_item.setToolTip(str(item.target))
        bar = QProgressBar(maximum=1000)
        bar.setFormat("%p%")
        bar.setMaximumHeight(self._row_height - 4)
        self.table.setItem(row, 0, name_item)
        self.table.setCellWidget(row, 1, bar)
        self.table.setItem(row, 2, QTableWidgetItem("—"))
        self.table.setItem(row, 3, QTableWidgetItem("—"))
        self._rows[item.key] = (name_item, bar)
        self._fit_table_height()

    def file_progress(self, item: DownloadItem, speed: float, eta: float | None) -> None:
        entry = self._rows.get(item.key)
        if not entry:
            return
        name_item, bar = entry
        row = self.table.row(name_item)
        bar.setValue(int(item.done * 1000 / item.size) if item.size else 0)
        self.table.item(row, 2).setText(f"{speed / MB:.2f} MB/s")
        self.table.item(row, 3).setText(human_eta(eta))

    def file_finished(self, item: DownloadItem, ok: bool, error: str) -> None:
        entry = self._rows.pop(item.key, None)
        if entry:
            self.table.removeRow(self.table.row(entry[0]))
            self._fit_table_height()

    def flood_wait(self, seconds_left: int) -> None:
        self._flood_active = seconds_left > 0
        if seconds_left <= 0:
            self.flood_label.hide()
        else:
            m, s = divmod(seconds_left, 60)
            self.flood_label.setText(tr("Limite di Telegram: ripresa automatica tra {time}", time=f"{m:02d}:{s:02d}"))
            self.flood_label.show()
        self._publish_info()
