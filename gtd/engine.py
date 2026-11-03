"""Motore di download: enumerazione messaggi, filtri, download a blocchi con ripresa, chat seguite."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import re
import time
import unicodedata
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol

from telethon import TelegramClient, errors, events, utils
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

from .i18n import tr
from .state import StateDB

log = logging.getLogger(__name__)

CHUNK_SIZE = 512 * 1024          # dimensione blocco richiesto a Telegram (massimo consentito)
PERSIST_EVERY = 8 * 1024 * 1024  # ogni quanti byte salvare l'avanzamento su SQLite
MAX_ATTEMPTS = 6
MAX_PARALLEL = 8                 # oltre, con file piccoli non si guadagna e Telegram chiede più spesso di rallentare
CHUNK_TIMEOUT = 120              # secondi senza dati prima di considerare bloccato un download
PHOTO_TIMEOUT = 300
FOLLOW_CHECK_SECONDS = 600       # controllo di sicurezza periodico quando si segue una chat
FOLLOW_GROUPING_DELAY = 3        # attesa dopo un nuovo messaggio, per prendere insieme gli album
REQUEUE_BATCH = 100              # file sospesi chiesti a Telegram in una volta
REQUEUE_LOW_WATER = 50           # se ne chiedono altri solo quando in coda ne restano meno di così

# errori di rete/Telegram da cui si riparte: IncompleteReadError (EOFError) è quello che bloccava i download
_TRANSIENT = (errors.RPCError, OSError, ConnectionError, EOFError, asyncio.TimeoutError)

_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL",
                   *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def sanitize(name: str, fallback: str = "file") -> str:
    """Rende un nome valido come file/cartella Windows."""
    name = _INVALID_CHARS.sub("_", name).strip().rstrip(". ")
    if not name:
        name = fallback
    stem, ext = os.path.splitext(name)
    if stem.upper() in _RESERVED_NAMES:
        stem = "_" + stem
    if len(stem) > 150:
        stem = stem[:150].rstrip(". ")
    return stem + ext


def _fold(text: str) -> str:
    """Testo per i confronti: minuscolo, senza accenti, con _ - . trattati come spazi («Mario_Rossi» = «mario rossi»)."""
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.sub(r"[_\-.]+", " ", text).split())


def parse_name_filter(text: str) -> list[str]:
    """«fattura, preventivo» → parole da cercare (basta che ne compaia una). Le virgole separano, gli spazi no."""
    return [w for w in (_fold(part) for part in re.split(r"[,;]+", text)) if w]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


class Cancelled(Exception):
    pass


class IntegrityError(Exception):
    pass


class Slots:
    """Download contemporanei. Più motori possono condividerli (es. tutte le chat seguite insieme)."""

    def __init__(self, limit: int = 1):
        self.limit = max(1, min(MAX_PARALLEL, limit))
        self.busy = 0
        self.changed = asyncio.Event()

    def release(self) -> None:
        self.busy -= 1
        self.changed.set()


class FloodGate:
    """Pausa imposta da Telegram (FloodWait): vale per tutto l'account, quindi è condivisa tra i motori."""

    def __init__(self):
        self.until = 0.0  # time.monotonic() fino a cui non si fanno richieste
        self.streak = 0   # FloodWait consecutivi: l'attesa aggiuntiva cresce

    def left(self) -> float:
        return max(0.0, self.until - time.monotonic())


class Listener(Protocol):
    def log(self, level: str, text: str) -> None: ...  # level: info | success | skip | warning | error
    def scan_progress(self, scanned: int, found: int, finished: bool) -> None: ...
    def overall(self, done_files: int, total_files: int, done_bytes: int, total_bytes: int) -> None: ...
    def file_started(self, item: "DownloadItem") -> None: ...
    def file_progress(self, item: "DownloadItem", speed: float, eta: float | None) -> None: ...
    def file_finished(self, item: "DownloadItem", ok: bool, error: str) -> None: ...
    def flood_wait(self, seconds_left: int) -> None: ...
    def following(self, last_check: datetime) -> None: ...
    def new_files(self, count: int) -> None: ...


@dataclass
class JobOptions:
    entity: object
    source_name: str
    destination: Path
    extensions: set[str]            # vuoto = tutti i tipi
    name_words: list[str] = field(default_factory=list)  # da parse_name_filter; vuoto = qualsiasi nome
    name_in_caption: bool = True    # le parole valgono anche se sono nel testo del messaggio
    min_size: int = 0               # byte
    max_size: int = 0               # byte, 0 = nessun limite
    duplicate_policy: str = "skip"  # skip | rename | overwrite
    folder_by_source: bool = True
    folder_by_type: bool = False
    folder_by_date: bool = False
    parallel: int = 2
    skip_duplicates: bool = True    # salta lo stesso file ripubblicato con un altro nome
    follow: bool = False            # dopo l'analisi resta in ascolto dei nuovi messaggi
    resume_from_last: bool = False  # analizza solo dopo l'ultimo messaggio visto (+ i file rimasti in sospeso)


@dataclass
class DownloadItem:
    message: object
    chat_id: int
    name: str
    size: int
    target: Path
    is_photo: bool
    done: int = 0
    _samples: deque = field(default_factory=lambda: deque(maxlen=40), repr=False)
    _last_emit: float = 0.0
    _last_persist: int = 0

    @property
    def msg_id(self) -> int:
        return self.message.id

    @property
    def key(self) -> tuple[int, int]:
        return self.chat_id, self.message.id

    @property
    def part(self) -> Path:
        return self.target.with_name(self.target.name + ".part")

    def speed(self) -> float:
        """Velocità in byte/s calcolata sugli ultimi ~3 secondi."""
        now = time.monotonic()
        while len(self._samples) > 2 and now - self._samples[0][0] > 3:
            self._samples.popleft()
        if len(self._samples) < 2:
            return 0.0
        (t0, b0), (t1, b1) = self._samples[0], self._samples[-1]
        return (b1 - b0) / (t1 - t0) if t1 > t0 else 0.0


@dataclass
class Summary:
    scanned: int = 0
    queued: int = 0
    completed: int = 0
    skipped: int = 0
    duplicates: int = 0
    failed: int = 0
    downloaded_bytes: int = 0
    cancelled: bool = False


class DownloadEngine:
    def __init__(self, client: TelegramClient, db: StateDB, listener: Listener,
                 slots: Slots | None = None, flood: FloodGate | None = None):
        self.client = client
        self.db = db
        self.l = listener
        self._running = asyncio.Event()
        self._running.set()
        self._wake = asyncio.Event()
        self._cancel_event = asyncio.Event()
        self._cancelled = False
        # condivisi se più motori lavorano insieme sullo stesso account
        self._flood = flood or FloodGate()
        self._slots = slots or Slots()
        self._shared_slots = slots is not None
        self._total_files = 0
        self._total_bytes = 0
        self._done_files = 0
        self._done_bytes = 0
        self._last_overall = 0.0
        self._reserved: set[str] = set()
        self._seen_docs: dict[int, str] = {}
        self._queued: set[tuple[int, int]] = set()  # messaggi già messi in coda in questo batch
        self._last_id = 0
        self._opts: JobOptions | None = None
        self.requeue_left = 0  # file sospesi non ancora rimessi in coda: il totale dei file crescerà ancora

    # ---- controllo -------------------------------------------------------

    @property
    def paused(self) -> bool:
        return not self._running.is_set()

    def pause(self) -> None:
        self._running.clear()
        self.l.log("warning", tr("Download in pausa"))

    def resume(self) -> None:
        self._running.set()
        self.l.log("info", tr("Download ripreso"))

    def cancel(self) -> None:
        self._cancelled = True
        self._cancel_event.set()
        self._running.set()
        self._wake.set()

    @property
    def parallel(self) -> int:
        return self._slots.limit

    def set_parallel(self, n: int) -> None:
        """Cambia i download contemporanei. Se diminuiscono, quelli già iniziati finiscono e poi ci si allinea."""
        n = max(1, min(MAX_PARALLEL, n))
        if n == self._slots.limit:
            return
        self._slots.limit = n
        self._slots.changed.set()
        self.l.log("info", tr("Download paralleli: {n}", n=n))

    async def _wait(self, event: asyncio.Event) -> None:
        """Attende l'evento, ma esce subito (Cancelled) se questo motore viene annullato."""
        if not event.is_set():
            waiters = [asyncio.ensure_future(event.wait()), asyncio.ensure_future(self._cancel_event.wait())]
            try:
                await asyncio.wait(waiters, return_when=asyncio.FIRST_COMPLETED)
            finally:
                for w in waiters:
                    w.cancel()
        if self._cancelled:
            raise Cancelled

    async def _take_slot(self) -> None:
        slots = self._slots
        while True:
            if self._shared_slots and not self._running.is_set():
                await self._wait(self._running)  # in pausa non si prendono slot condivisi con altre chat
            if slots.busy < slots.limit:
                break
            slots.changed.clear()
            await self._wait(slots.changed)
        slots.busy += 1

    async def _sleep_without_slot(self, seconds: float) -> None:
        """Attesa prima di un nuovo tentativo: intanto lo slot va a un altro file
        (un file che non scende non deve bloccare gli altri download)."""
        await self._wait_without_slot(self._sleep(seconds))

    async def _download_checkpoint(self) -> None:
        """Come _checkpoint, ma dentro un download (slot occupato): in pausa lo slot passa
        alle altre chat seguite, che condividono gli stessi slot."""
        if self._shared_slots and not self._running.is_set() and not self._cancelled:
            await self._wait_without_slot(self._wait(self._running))
        await self._checkpoint()

    async def _wait_without_slot(self, waiting) -> None:
        self._slots.release()
        try:
            await waiting
        finally:
            try:
                await self._take_slot()
            except Cancelled:
                self._slots.busy += 1  # il worker lo rilascia uscendo: i conti tornano
                raise

    async def _checkpoint(self) -> None:
        if self._cancelled:
            raise Cancelled
        if not self._running.is_set():
            await self._wait(self._running)
        if self._flood.left() > 0:
            await self._wait_flood(report=False)
        if self._cancelled:
            raise Cancelled

    async def _sleep(self, seconds: float) -> None:
        end = time.monotonic() + seconds
        while (left := end - time.monotonic()) > 0:
            if self._cancelled:
                raise Cancelled
            await asyncio.sleep(min(0.5, left))

    async def _handle_flood(self, seconds: int) -> None:
        """Attende il FloodWait richiesto da Telegram, con backoff esponenziale se si ripete."""
        gate = self._flood
        if gate.left() > 0:  # un altro download (anche di un'altra chat) sta già aspettando
            await self._wait_flood(report=False)
            return
        gate.streak += 1
        wait = seconds + min(2 ** gate.streak, 300)
        gate.until = time.monotonic() + wait
        self.l.log("warning", tr("Limite di Telegram (FloodWait): pausa di {seconds} secondi", seconds=wait))
        await self._wait_flood(report=True)

    async def _wait_flood(self, report: bool) -> None:
        """report: mostra il conto alla rovescia (solo chi ha ricevuto il FloodWait, gli altri aspettano e basta)."""
        try:
            while (left := self._flood.left()) > 0:
                if self._cancelled:
                    raise Cancelled
                if report:
                    self.l.flood_wait(int(left + 0.999))
                await asyncio.sleep(min(1.0, left))
        finally:
            if report:
                self.l.flood_wait(0)

    # ---- esecuzione ------------------------------------------------------

    async def run(self, opts: JobOptions) -> Summary:
        """Analizza la chat e scarica in parallelo: i download partono appena viene trovato il primo file.
        Con opts.follow resta poi in ascolto dei nuovi messaggi finché non viene annullato."""
        self._opts = opts
        summary = Summary()
        chat_id = utils.get_peer_id(opts.entity)
        if not self._shared_slots:  # se condivisi, il limite lo decide chi li ha creati
            self._slots.limit = max(1, min(MAX_PARALLEL, opts.parallel))
        parallel = self._slots.limit
        queue: asyncio.Queue[DownloadItem | None] = asyncio.Queue()
        # sempre MAX_PARALLEL worker: quanti lavorano davvero lo decide il limite degli slot (vedi _take_slot)
        workers = [asyncio.create_task(self._worker(queue, summary)) for _ in range(MAX_PARALLEL)]
        requeue: asyncio.Task | None = None
        try:
            after_id = 0
            if opts.resume_from_last:
                after_id = self.db.last_msg_id(chat_id)
                # i sospesi possono essere decine di migliaia: si rimettono in coda poco alla volta,
                # intanto si controllano i messaggi nuovi
                requeue = asyncio.create_task(self._requeue_pending(opts, chat_id, summary, queue))
            if after_id:
                self.l.log("info", tr("«{source}»: controllo dei messaggi arrivati dopo l'ultimo visto",
                                       source=opts.source_name))
            else:
                self.l.log("info", tr("Analisi di «{source}» avviata: i download partono man mano ({n} in parallelo)",
                                       source=opts.source_name, n=parallel))
            await self._scan(opts, chat_id, summary, queue, after_id)
            if opts.follow:
                await self._follow(opts, chat_id, summary, queue)
            elif requeue:
                await requeue  # batch: finisce dopo aver rimesso in coda tutti i sospesi
        except Cancelled:
            pass
        except Exception as e:
            log.exception("Analisi interrotta")
            self.l.log("error", tr("Analisi interrotta ({error}): completo i {n} file già in coda",
                                    error=e, n=summary.queued))
        finally:
            if requeue and not requeue.done():
                requeue.cancel()
                await asyncio.gather(requeue, return_exceptions=True)
            for _ in workers:
                queue.put_nowait(None)  # segnale di fine coda per ogni worker
        for result in await asyncio.gather(*workers, return_exceptions=True):
            if isinstance(result, BaseException):
                log.error("Worker terminato con errore", exc_info=result)
        self.db.commit()
        summary.cancelled = self._cancelled
        return summary

    async def _worker(self, queue: asyncio.Queue, summary: Summary) -> None:
        while True:
            # prima il file, poi lo slot: un worker senza lavoro non deve tenere occupato uno slot
            # (con le chat seguite gli slot sono condivisi e una chat ferma bloccherebbe le altre)
            item = await queue.get()
            if item is None or self._cancelled:
                return
            try:
                await self._take_slot()
            except Cancelled:
                return
            try:
                await self._process(item, summary)
            except Exception:  # un errore su un file non deve mai fermare gli altri download
                log.exception("Errore imprevisto su %s", item.name)
                self.l.log("error", tr("{name}: errore imprevisto, file saltato", name=item.name))
            finally:
                self._slots.release()

    def _enqueue(self, item: DownloadItem, summary: Summary, queue: asyncio.Queue) -> None:
        self._queued.add(item.key)
        summary.queued += 1
        self._total_files += 1
        self._total_bytes += item.size
        queue.put_nowait(item)
        self._emit_overall()

    # ---- scansione -------------------------------------------------------

    async def _scan(self, opts: JobOptions, chat_id: int, summary: Summary, queue: asyncio.Queue,
                    after_id: int, incremental: bool = False) -> int:
        """Legge i messaggi successivi ad after_id e mette in coda i file. Ritorna quanti ne ha trovati."""
        last_id = after_id
        failures = 0
        found = 0
        scanned_before, skipped_before = summary.scanned, summary.skipped
        while True:
            try:
                async for msg in self.client.iter_messages(opts.entity, reverse=True, offset_id=last_id):
                    await self._checkpoint()
                    last_id = msg.id
                    failures = 0
                    summary.scanned += 1
                    item = self._make_item(msg, chat_id, opts, summary)
                    if item:
                        found += 1
                        self._enqueue(item, summary, queue)
                    if summary.scanned % 200 == 0:
                        self.db.set_last_msg_id(chat_id, last_id)
                        if not incremental:
                            self.l.scan_progress(summary.scanned, summary.queued, False)
                break
            except errors.FloodWaitError as e:
                await self._scan_flood(e.seconds)
            except _TRANSIENT as e:
                failures += 1
                if failures >= MAX_ATTEMPTS:
                    raise
                delay = min(2 ** failures, 60)
                self.l.log("warning", tr("Analisi: errore ({error}), riprendo dal messaggio {msg_id} tra {seconds}s",
                                         error=e or type(e).__name__, msg_id=last_id, seconds=delay))
                await self._sleep(delay)
        self._last_id = max(self._last_id, last_id)
        self.db.set_last_msg_id(chat_id, self._last_id)
        if not incremental:
            self.l.scan_progress(summary.scanned, summary.queued, True)
            self._emit_overall(force=True)
            self.l.log("info", tr("Analisi completata: {scanned} messaggi, {found} file da scaricare ({size}), "
                                  "{skipped} saltati perché già presenti",
                                  scanned=summary.scanned - scanned_before, found=found,
                                  size=human_size(self._total_bytes), skipped=summary.skipped - skipped_before))
        return found

    async def _requeue_pending(self, opts: JobOptions, chat_id: int, summary: Summary,
                               queue: asyncio.Queue) -> None:
        """Rimette in coda i file trovati in passato ma mai completati (app chiusa, errori…).
        Un blocco alla volta, solo quando la coda si sta svuotando: chiederli tutti insieme a Telegram
        (anche 40.000) fa scattare i limiti e rallenta tutto."""
        ids = self.db.pending_msg_ids(chat_id)
        if not ids:
            return
        self.l.log("info", tr("{n} file rimasti in sospeso dall'ultima volta: li rimetto in coda poco alla volta",
                               n=len(ids)))
        self.requeue_left = len(ids)
        try:
            for start in range(0, len(ids), REQUEUE_BATCH):
                while queue.qsize() > REQUEUE_LOW_WATER:
                    await self._sleep(1)
                await self._checkpoint()
                batch = ids[start:start + REQUEUE_BATCH]
                failures = 0
                while True:
                    try:
                        messages = await self.client.get_messages(opts.entity, ids=batch)
                        break
                    except errors.FloodWaitError as e:
                        await self._scan_flood(e.seconds)
                    except _TRANSIENT as e:
                        failures += 1
                        if failures >= MAX_ATTEMPTS:
                            raise
                        await self._sleep(min(2 ** failures, 60))
                self.requeue_left = len(ids) - start - len(batch)
                for msg in messages:
                    if msg is not None:
                        item = self._make_item(msg, chat_id, opts, summary)
                        if item:
                            self._enqueue(item, summary, queue)
        except Cancelled:
            pass
        except Exception as e:  # gira accanto all'analisi: l'errore non deve perdersi
            log.exception("Ripresa dei file sospesi interrotta")
            self.l.log("error", tr("Ripresa dei file in sospeso interrotta ({error}): riprovo al prossimo avvio",
                                    error=e))
        finally:
            self.requeue_left = 0
            self._emit_overall(force=True)

    async def _scan_flood(self, seconds: int) -> None:
        """FloodWait sulla lettura dei messaggi: aspetta solo l'analisi, i download continuano
        (il limite di Telegram vale per il tipo di richiesta)."""
        wait = seconds + 1
        self.l.log("warning", tr("Analisi: Telegram chiede di rallentare, riprendo tra {seconds}s "
                                 "(i download continuano)", seconds=wait))
        await self._sleep(wait)

    async def _follow(self, opts: JobOptions, chat_id: int, summary: Summary, queue: asyncio.Queue) -> None:
        """Resta in ascolto: Telegram avvisa dei nuovi messaggi, più un controllo di sicurezza periodico."""
        async def on_new_message(_event) -> None:
            self._wake.set()

        new_messages = events.NewMessage(chats=opts.entity)
        self.client.add_event_handler(on_new_message, new_messages)
        self.l.log("info", tr("In ascolto di «{source}»: i nuovi file verranno scaricati appena arrivano",
                               source=opts.source_name))
        try:
            while True:
                self.l.following(datetime.now())
                try:
                    await asyncio.wait_for(self._wake.wait(), FOLLOW_CHECK_SECONDS)
                except asyncio.TimeoutError:
                    pass
                if self._cancelled:
                    raise Cancelled
                if self._wake.is_set():
                    await self._sleep(FOLLOW_GROUPING_DELAY)
                self._wake.clear()
                await self._checkpoint()
                try:
                    found = await self._scan(opts, chat_id, summary, queue, self._last_id, incremental=True)
                except Cancelled:
                    raise
                except Exception as e:  # la rete tornerà: si riprova al prossimo giro
                    self.l.log("warning", tr("Controllo nuovi messaggi non riuscito ({error}), riprovo più tardi",
                                              error=e))
                    continue
                if found:
                    self.l.log("info", tr("{n} nuovi file da «{source}»", n=found, source=opts.source_name))
                    self.l.new_files(found)
        finally:
            self.client.remove_event_handler(on_new_message, new_messages)

    def _skip(self, summary: Summary, name: str, reason: str, duplicate: bool = False) -> None:
        summary.skipped += 1
        if duplicate:
            summary.duplicates += 1
        self.l.log("skip", tr("Saltato: {name} — {reason}", name=name, reason=reason))

    def _make_item(self, msg, chat_id: int, opts: JobOptions, summary: Summary) -> DownloadItem | None:
        media = msg.media
        if not isinstance(media, (MessageMediaDocument, MessageMediaPhoto)) or msg.file is None:
            return None
        if msg.sticker:
            return None
        is_photo = isinstance(media, MessageMediaPhoto)
        if (is_photo and not msg.photo) or (not is_photo and not msg.document):
            return None  # media scaduto / autodistruttivo
        if (chat_id, msg.id) in self._queued:
            return None  # già in coda (es. ripreso dai «sospesi» e poi rivisto dall'analisi)

        f = msg.file
        ext = (os.path.splitext(f.name)[1] if f.name else (f.ext or "")).lower()
        if ext == ".jpe":
            ext = ".jpg"
        if opts.extensions and ext not in opts.extensions:
            return None
        if opts.name_words:
            # le foto non hanno un nome: per loro conta solo il testo del messaggio
            text = f.name or ""
            if opts.name_in_caption:
                text += " " + (getattr(msg, "message", None) or "")
            text = _fold(text)
            if not any(word in text for word in opts.name_words):
                return None
        size = f.size or 0
        if size < opts.min_size or (opts.max_size and size > opts.max_size):
            return None

        name = sanitize(f.name or f"{chat_id}_{msg.id}{ext}")
        folder = opts.destination
        if opts.folder_by_source:
            folder = folder / sanitize(opts.source_name, "chat")
        if opts.folder_by_type:
            folder = folder / (ext.lstrip(".").upper() or "ALTRO")
        if opts.folder_by_date:
            folder = folder / msg.date.astimezone().strftime("%Y-%m")
        target = folder / name
        policy = opts.duplicate_policy
        doc_id = (msg.photo if is_photo else msg.document).id
        reserved = self._reserved

        record = self.db.get(chat_id, msg.id)
        if record and policy != "overwrite":
            previous = Path(record["target"])
            if (record["status"] == "completed" and previous.exists()
                    and previous.stat().st_size == record["size"]):
                self._skip(summary, name, tr("già scaricato in precedenza"))
                return None
            partial = previous.with_name(previous.name + ".part")
            if record["status"] != "completed" and partial.exists() and previous.parent == target.parent:
                reserved.add(str(previous).lower())
                self._seen_docs[doc_id] = previous.name
                return DownloadItem(msg, chat_id, previous.name, size, previous, is_photo)

        if opts.skip_duplicates and policy != "overwrite":
            if doc_id in self._seen_docs:
                self._skip(summary, name, tr("doppione di «{other}» (già in coda)", other=self._seen_docs[doc_id]),
                           duplicate=True)
                return None
            other = self.db.find_completed_doc(doc_id)
            if other and Path(other["target"]).exists():
                self._skip(summary, name, tr("doppione di «{other}» già scaricato", other=Path(other["target"]).name),
                           duplicate=True)
                return None

        key = str(target).lower()
        if target.exists() or key in reserved:
            on_disk_same = target.exists() and key not in reserved and target.stat().st_size == size
            if policy != "overwrite" and on_disk_same:  # stesso nome e stessa dimensione: è già lì
                self._skip(summary, name, tr("già presente nella cartella"))
                return None
            if not (policy == "overwrite" and key not in reserved):
                target = _unique_path(target, reserved)

        reserved.add(str(target).lower())
        self._seen_docs[doc_id] = target.name
        self.db.register(chat_id, msg.id, target.name, target, size, doc_id)
        return DownloadItem(msg, chat_id, target.name, size, target, is_photo)

    # ---- download --------------------------------------------------------

    async def _process(self, item: DownloadItem, summary: Summary) -> None:
        self.l.file_started(item)
        ok, duplicate, error, attempt = False, False, "", 0
        while attempt < MAX_ATTEMPTS:
            try:
                await self._download_checkpoint()
                duplicate = await self._transfer(item)
                ok = True
                break
            except Cancelled:
                error = tr("annullato")
                break
            except errors.FloodWaitError as e:
                try:
                    await self._handle_flood(e.seconds)
                except Cancelled:
                    error = tr("annullato")
                    break
                continue  # il FloodWait non consuma tentativi
            except errors.FileReferenceExpiredError:
                attempt += 1
                try:
                    fresh = await self.client.get_messages(item.message.peer_id, ids=item.msg_id)
                except _TRANSIENT as e:
                    error = tr("aggiornamento riferimento non riuscito: {error}", error=e)
                    continue
                if fresh is None or fresh.file is None:
                    error = tr("messaggio non più disponibile")
                    break
                item.message = fresh
            except Exception as e:  # rete, Telegram, disco: si riprova con attesa crescente
                attempt += 1
                error = str(e) or type(e).__name__
                if not isinstance(e, (*_TRANSIENT, IntegrityError)):
                    log.exception("Errore imprevisto durante il download di %s", item.name)
                if attempt >= MAX_ATTEMPTS:
                    break
                delay = min(2 ** attempt, 60)
                self.l.log("warning", tr("{name}: errore ({error}), nuovo tentativo {attempt}/{max} tra {seconds}s",
                                         name=item.name, error=error, attempt=attempt + 1,
                                         max=MAX_ATTEMPTS, seconds=delay))
                try:
                    await self._sleep_without_slot(delay)
                except Cancelled:
                    error = tr("annullato")
                    break

        if ok:
            self._done_files += 1
            self._flood.streak = 0
            if duplicate:
                summary.skipped += 1
                summary.duplicates += 1
            else:
                summary.completed += 1
                summary.downloaded_bytes += item.size
        elif self._cancelled:
            self.db.set_progress(*item.key, item.done)
        else:
            summary.failed += 1
            self._done_files += 1
            self.db.set_status(*item.key, "failed")
            self.l.log("error", tr("{name}: download non riuscito ({error})", name=item.name, error=error))
        self.l.file_finished(item, ok, error)
        self._emit_overall(force=True)

    async def _transfer(self, item: DownloadItem) -> bool:
        """Scarica il file. Ritorna True se si è rivelato un doppione (e quindi è stato scartato)."""
        item.target.parent.mkdir(parents=True, exist_ok=True)
        if item.is_photo:
            await asyncio.wait_for(self._transfer_photo(item), PHOTO_TIMEOUT)
        else:
            await self._transfer_document(item)

        actual = item.part.stat().st_size
        if item.is_photo:
            self._total_bytes += actual - item.size
            item.size = actual
            self._set_done(item, actual)
        elif actual != item.size:
            if actual > item.size:
                item.part.unlink(missing_ok=True)
            raise IntegrityError(tr("dimensione {actual} diversa da quella attesa {expected}",
                                     actual=actual, expected=item.size))

        digest = await asyncio.to_thread(sha256_file, item.part)
        opts = self._opts
        if opts and opts.skip_duplicates and opts.duplicate_policy != "overwrite":
            other = self.db.find_completed_sha(digest, *item.key)
            if other and Path(other["target"]).exists() and Path(other["target"]) != item.target:
                item.part.unlink(missing_ok=True)
                self.db.set_completed(*item.key, item.size, digest, target=Path(other["target"]))
                self.l.log("skip", tr("Scartato: {name} — contenuto identico a «{other}»", name=item.name,
                                       other=Path(other["target"]).name))
                return True

        os.replace(item.part, item.target)
        self.db.set_completed(*item.key, item.size, digest)
        self.l.log("success", tr("Completato: {name} ({size}, SHA-256 {digest}…)", name=item.name,
                                 size=human_size(item.size), digest=digest[:12]))
        return False

    async def _transfer_document(self, item: DownloadItem) -> None:
        part = item.part
        offset = part.stat().st_size if part.exists() else 0
        if offset > item.size:
            offset = 0
        offset -= offset % CHUNK_SIZE  # riparte dall'ultimo blocco intero verificato
        if offset:
            self.l.log("info", tr("Ripresa di {name} da {size}", name=item.name, size=human_size(offset)))
        self._set_done(item, offset)
        item._last_persist = offset
        item._samples.clear()

        with open(part, "r+b" if part.exists() else "wb") as f:
            f.truncate(offset)
            f.seek(offset)
            if offset < item.size:
                chunks = self.client.iter_download(
                    item.message.document, offset=offset, request_size=CHUNK_SIZE, file_size=item.size).__aiter__()
                while True:
                    try:
                        # se Telegram smette di rispondere non restiamo appesi: si riprova da capo blocco
                        chunk = await asyncio.wait_for(chunks.__anext__(), CHUNK_TIMEOUT)
                    except StopAsyncIteration:
                        break
                    except asyncio.TimeoutError:
                        raise asyncio.TimeoutError(tr("nessun dato da {seconds} secondi", seconds=CHUNK_TIMEOUT)) from None
                    await self._download_checkpoint()
                    chunk = chunk[:item.size - item.done]
                    f.write(chunk)
                    self._set_done(item, item.done + len(chunk))
                    if item.done - item._last_persist >= PERSIST_EVERY:
                        f.flush()
                        os.fsync(f.fileno())
                        self.db.set_progress(*item.key, item.done)
                        item._last_persist = item.done
                    if item.done >= item.size:
                        break
            f.flush()
            os.fsync(f.fileno())

    async def _transfer_photo(self, item: DownloadItem) -> None:
        self._set_done(item, 0)
        item._samples.clear()
        await self.client.download_media(
            item.message, file=str(item.part),
            progress_callback=lambda current, _total: self._set_done(item, current))

    # ---- avanzamento -----------------------------------------------------

    def _set_done(self, item: DownloadItem, done: int) -> None:
        self._done_bytes += done - item.done
        item.done = done
        now = time.monotonic()
        item._samples.append((now, done))
        if now - item._last_emit >= 0.25 or done >= item.size:
            item._last_emit = now
            speed = item.speed()
            eta = (item.size - done) / speed if speed > 0 else None
            self.l.file_progress(item, speed, eta)
        self._emit_overall()

    def _emit_overall(self, force: bool = False) -> None:
        now = time.monotonic()
        if force or now - self._last_overall >= 0.25:
            self._last_overall = now
            self.l.overall(self._done_files, self._total_files, self._done_bytes, self._total_bytes)


def _unique_path(path: Path, reserved: set[str]) -> Path:
    stem, ext = os.path.splitext(path.name)
    n = 1
    while True:
        candidate = path.with_name(f"{stem}_({n}){ext}")
        part = candidate.with_name(candidate.name + ".part")
        if not candidate.exists() and not part.exists() and str(candidate).lower() not in reserved:
            return candidate
        n += 1


def human_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"


def human_eta(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
