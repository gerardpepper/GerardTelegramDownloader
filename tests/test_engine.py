"""Test del motore di download con un client Telegram simulato.

Esecuzione:  .venv\\Scripts\\python -m unittest discover -s tests -v
"""

import asyncio
import hashlib
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from telethon import errors
from telethon.tl.types import MessageMediaDocument, PeerChannel

from gtd.engine import CHUNK_SIZE, DownloadEngine, JobOptions, Slots, parse_name_filter
from gtd.state import StateDB

ENTITY = PeerChannel(42)
OTHER = PeerChannel(43)


def make_msg(msg_id: int, name: str, data: bytes, doc_id: int | None = None, caption: str = ""):
    return SimpleNamespace(
        id=msg_id, media=MessageMediaDocument(), sticker=None, photo=None, message=caption,
        document=SimpleNamespace(data=data, id=doc_id if doc_id is not None else msg_id * 1000),
        file=SimpleNamespace(name=name, ext=os.path.splitext(name)[1], size=len(data)),
        date=datetime(2026, 10, 1, tzinfo=timezone.utc), peer_id=ENTITY)


class FakeClient:
    def __init__(self, messages, flood_once=False, fail_after=None, broken_once=False, stall_once=False):
        self.messages = messages
        self.flood_once = flood_once
        self.fail_after = fail_after  # byte dopo cui simulare una disconnessione (una volta)
        self.broken_once = broken_once  # connessione chiusa male da Telegram (il bug del 21/10)
        self.stall_once = stall_once    # Telegram smette di rispondere senza chiudere
        self.offsets = []
        self.events = []
        self.handlers = []

    def add_event_handler(self, callback, event):
        self.handlers.append(callback)

    def remove_event_handler(self, callback, event):
        self.handlers.remove(callback)

    async def get_messages(self, entity, ids):
        by_id = {m.id: m for m in self.messages}
        return [by_id.get(i) for i in ids]

    async def iter_messages(self, entity, reverse=True, offset_id=0):
        for m in sorted(self.messages, key=lambda m: m.id):
            if m.id > offset_id:
                await asyncio.sleep(0.01)  # come la rete reale: l'analisi richiede tempo
                yield m
        self.events.append("fine analisi")

    async def iter_download(self, document, offset=0, request_size=CHUNK_SIZE, file_size=None):
        self.events.append("download")
        self.offsets.append(offset)
        if self.flood_once:
            self.flood_once = False
            raise errors.FloodWaitError(request=None, capture=1)
        if self.broken_once:
            self.broken_once = False
            raise asyncio.IncompleteReadError(b"x" * 758, 1347703872)
        if self.stall_once:
            self.stall_once = False
            await asyncio.sleep(3600)
        pos = offset
        while pos < len(document.data):
            if self.fail_after is not None and pos >= self.fail_after:
                self.fail_after = None
                raise ConnectionError("rete persa")
            yield document.data[pos:pos + request_size]
            pos += request_size


class Recorder:
    def __init__(self):
        self.logs, self.floods = [], []

    def log(self, level, text): self.logs.append((level, text))
    def scan_progress(self, scanned, found, finished): pass
    def overall(self, *a): pass
    def file_started(self, item): pass
    def file_progress(self, item, speed, eta): pass
    def file_finished(self, item, ok, error): pass
    def flood_wait(self, seconds): self.floods.append(seconds)
    def following(self, last_check): self.follow_checks = getattr(self, "follow_checks", 0) + 1
    def new_files(self, count): pass


class EngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dest = self.root / "out"
        self.db = StateDB(self.root / "state.db")
        self.big = os.urandom(3 * CHUNK_SIZE + 1234)
        self.msgs = [make_msg(1, "libro.pdf", self.big), make_msg(2, "foto.png", b"x" * 100),
                     make_msg(3, "video.mp4", os.urandom(5000))]

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def run_job(self, client, **kw):
        opts = JobOptions(entity=ENTITY, source_name="Canale: Prova", destination=self.dest,
                          extensions=kw.pop("extensions", set()), **kw)
        rec = Recorder()
        summary = asyncio.run(DownloadEngine(client, self.db, rec).run(opts))
        return summary, rec

    def test_download_and_skip_on_rerun(self):
        s, _ = self.run_job(FakeClient(self.msgs), parallel=3)
        self.assertEqual((s.completed, s.failed), (3, 0))
        out = self.dest / "Canale_ Prova" / "libro.pdf"
        self.assertEqual(out.read_bytes(), self.big)
        row = self.db.get(self._chat_id(), 1)
        self.assertEqual(row["sha256"], hashlib.sha256(self.big).hexdigest())
        s2, _ = self.run_job(FakeClient(self.msgs), duplicate_policy="rename")
        self.assertEqual((s2.completed, s2.skipped), (0, 3))

    def _chat_id(self):
        from telethon import utils
        return utils.get_peer_id(ENTITY)

    def test_resume_after_disconnect(self):
        client = FakeClient([self.msgs[0]], fail_after=2 * CHUNK_SIZE)
        s, rec = self.run_job(client)
        self.assertEqual(s.completed, 1)
        self.assertEqual(client.offsets, [0, 2 * CHUNK_SIZE])  # ripreso dall'ultimo blocco
        self.assertEqual((self.dest / "Canale_ Prova" / "libro.pdf").read_bytes(), self.big)

    def test_resume_from_partial_file_on_disk(self):
        folder = self.dest / "Canale_ Prova"
        folder.mkdir(parents=True)
        (folder / "libro.pdf.part").write_bytes(self.big[:CHUNK_SIZE + 100])  # resto di un blocco incompleto
        self.db.register(self._chat_id(), 1, "libro.pdf", folder / "libro.pdf", len(self.big))
        client = FakeClient([self.msgs[0]])
        s, _ = self.run_job(client)
        self.assertEqual(client.offsets, [CHUNK_SIZE])
        self.assertEqual((folder / "libro.pdf").read_bytes(), self.big)

    def test_restart_skips_files_already_in_destination(self):
        # primo giro: scarica tutto
        s, _ = self.run_job(FakeClient(self.msgs), folder_by_source=False)
        self.assertEqual(s.completed, 3)
        # riavvio dopo aver perso il database (o file messi a mano): nessun doppione con nessuna regola
        self.db.conn.execute("DELETE FROM downloads")
        for policy in ("skip", "rename"):
            s, _ = self.run_job(FakeClient(self.msgs), folder_by_source=False, duplicate_policy=policy)
            self.assertEqual((s.completed, s.skipped), (0, 3), policy)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()), ["foto.png", "libro.pdf", "video.mp4"])

    def test_rescan_from_start(self):
        """«Ricontrolla da capo» di una chat seguita: rilettura completa (resume_from_last=False)."""
        s, _ = self.run_job(FakeClient(self.msgs), folder_by_source=False, follow=False)
        self.assertEqual(s.completed, 3)
        (self.dest / "video.mp4").unlink()  # cancellato a mano dalla cartella
        s, _ = self.run_job(FakeClient(self.msgs), folder_by_source=False)
        self.assertEqual((s.scanned, s.completed, s.skipped), (3, 1, 2))  # riscarica solo quello che manca
        self.assertEqual((self.dest / "video.mp4").read_bytes(), self.msgs[2].document.data)
        s, _ = self.run_job(FakeClient(self.msgs), folder_by_source=False, duplicate_policy="overwrite")
        self.assertEqual(s.completed, 3)  # «Sovrascrivi»: riscarica tutto, senza creare copie
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()), ["foto.png", "libro.pdf", "video.mp4"])

    def test_only_selected_extension(self):
        msgs = self.msgs + [make_msg(4, "romanzo.EPUB", b"e" * 50), make_msg(5, "altro.epub", b"f" * 60)]
        s, _ = self.run_job(FakeClient(msgs), extensions={".epub"}, folder_by_source=False)
        self.assertEqual(s.completed, 2)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()), ["altro.epub", "romanzo.EPUB"])

    def test_name_filter(self):
        msgs = [make_msg(1, "Offerta_GIANFELICE_v2.pdf", b"a" * 50),
                make_msg(2, "scan001.pdf", b"b" * 50, caption="Contratto di Gianfélice Rossi"),
                make_msg(3, "altro.pdf", b"c" * 50, caption="niente"),
                make_msg(4, "preventivo-mario.epub", b"d" * 50)]
        self.assertEqual(parse_name_filter(" gianfelice , Preventivo Mario;"), ["gianfelice", "preventivo mario"])
        s, _ = self.run_job(FakeClient(msgs), folder_by_source=False,
                            name_words=parse_name_filter("gianfelice, preventivo mario"))
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()),
                         ["Offerta_GIANFELICE_v2.pdf", "preventivo-mario.epub", "scan001.pdf"])
        # senza la didascalia conta solo il nome del file; le estensioni si combinano con il nome
        self.db.conn.execute("DELETE FROM downloads")
        for p in self.dest.iterdir():
            p.unlink()
        self.run_job(FakeClient(msgs), folder_by_source=False, extensions={".pdf"},
                     name_words=["gianfelice", "preventivo mario"], name_in_caption=False)
        self.assertEqual([p.name for p in self.dest.iterdir()], ["Offerta_GIANFELICE_v2.pdf"])

    def test_engines_share_slots(self):
        """Chat seguite: i download contemporanei sono contati tutti insieme."""
        def msgs(peer, start):
            out = [make_msg(i, f"doc{i}.epub", os.urandom(800)) for i in range(start, start + 12)]
            for m in out:
                m.peer_id = peer
            return out

        clients = [FakeClient(msgs(ENTITY, 1)), FakeClient(msgs(OTHER, 100))]
        active, peak = 0, 0
        for client in clients:
            original = client.iter_download

            async def tracked(*args, _original=original, **kwargs):
                nonlocal active, peak
                active += 1
                peak = max(peak, active)
                try:
                    await asyncio.sleep(0.05)
                    async for chunk in _original(*args, **kwargs):
                        yield chunk
                finally:
                    active -= 1

            client.iter_download = tracked

        async def scenario():
            slots = Slots(3)
            jobs = [DownloadEngine(c, self.db, Recorder(), slots=slots).run(
                JobOptions(entity=e, source_name=str(e.channel_id), destination=self.dest, extensions=set()))
                for c, e in zip(clients, (ENTITY, OTHER))]
            return await asyncio.gather(*jobs)

        results = asyncio.run(scenario())
        self.assertEqual([s.completed for s in results], [12, 12])
        self.assertEqual(peak, 3)

    def test_busy_followed_chat_shares_slots_fairly(self):
        """Il caso del 3/11: «LA BIBLIOTECA» con migliaia di file in coda si riprendeva sempre lo slot
        appena liberato e «OPEN», arrivata dopo, non ha scaricato nulla per 7 ore."""
        def slow(client):
            original = client.iter_download

            async def slowly(*args, **kwargs):
                await asyncio.sleep(0.03)
                async for chunk in original(*args, **kwargs):
                    yield chunk
            client.iter_download = slowly
            return client

        busy = slow(FakeClient([make_msg(i, f"biblioteca{i}.epub", os.urandom(300)) for i in range(1, 61)]))
        late = slow(FakeClient([make_msg(i, f"open{i}.mkv", os.urandom(300)) for i in range(1000, 1004)]))
        for m in late.messages:
            m.peer_id = OTHER
        order = []

        class Tracker(Recorder):
            def file_finished(self, item, ok, error):
                order.append(item.name)

        async def scenario():
            slots = Slots(2)
            first = asyncio.create_task(DownloadEngine(busy, self.db, Tracker(), slots=slots).run(
                JobOptions(entity=ENTITY, source_name="A", destination=self.dest, extensions=set())))
            await asyncio.sleep(0.3)  # la prima chat ha già la coda piena e gli slot occupati
            second = DownloadEngine(late, self.db, Tracker(), slots=slots).run(
                JobOptions(entity=OTHER, source_name="B", destination=self.dest, extensions=set()))
            return await asyncio.gather(first, second)

        a, b = asyncio.run(scenario())
        self.assertEqual((a.completed, b.completed), (60, 4))
        last_open = max(i for i, name in enumerate(order) if name.startswith("open"))
        self.assertLess(last_open, 30, order)  # la seconda chat scarica a turno, non dopo tutta la prima

    def test_paused_followed_chat_does_not_block_others(self):
        """Pausa su una chat seguita: i suoi download fermi lasciano gli slot condivisi alle altre."""
        slow = FakeClient([make_msg(i, f"lento{i}.epub", os.urandom(3 * CHUNK_SIZE)) for i in range(1, 4)])
        original = slow.iter_download

        async def slowly(*args, **kwargs):
            async for chunk in original(*args, **kwargs):
                await asyncio.sleep(0.2)
                yield chunk

        slow.iter_download = slowly
        other = FakeClient([make_msg(i, f"doc{i}.epub", os.urandom(500)) for i in range(10, 15)])
        for m in other.messages:
            m.peer_id = OTHER

        async def scenario():
            slots = Slots(2)
            paused = DownloadEngine(slow, self.db, Recorder(), slots=slots)
            task = asyncio.create_task(paused.run(JobOptions(entity=ENTITY, source_name="A", destination=self.dest,
                                                             extensions=set())))
            await asyncio.sleep(0.3)   # i due slot sono occupati dai file lenti
            paused.pause()
            s = await asyncio.wait_for(DownloadEngine(other, self.db, Recorder(), slots=slots).run(
                JobOptions(entity=OTHER, source_name="B", destination=self.dest, extensions=set())), 10)
            self.assertLessEqual(slots.busy, 0)  # la chat in pausa non ha ripreso slot
            paused.resume()
            first = await asyncio.wait_for(task, 20)
            return s, first

        s, first = asyncio.run(scenario())
        self.assertEqual((s.completed, first.completed), (5, 3))

    def test_idle_followed_chat_does_not_block_others(self):
        """Una chat in ascolto senza file da scaricare non deve tenere occupati gli slot condivisi."""
        import gtd.engine as engine
        engine.FOLLOW_GROUPING_DELAY = 0
        idle = FakeClient([])
        busy = FakeClient([make_msg(i, f"doc{i}.epub", os.urandom(500)) for i in range(1, 6)])
        for m in busy.messages:
            m.peer_id = OTHER

        async def scenario():
            slots = Slots(1)
            follower = DownloadEngine(idle, self.db, Recorder(), slots=slots)
            task = asyncio.create_task(follower.run(JobOptions(entity=ENTITY, source_name="A", destination=self.dest,
                                                               extensions=set(), follow=True)))
            while not idle.handlers:
                await asyncio.sleep(0.02)
            s = await asyncio.wait_for(DownloadEngine(busy, self.db, Recorder(), slots=slots).run(
                JobOptions(entity=OTHER, source_name="B", destination=self.dest, extensions=set())), 10)
            follower.cancel()
            await asyncio.wait_for(task, 5)
            return s

        self.assertEqual(asyncio.run(scenario()).completed, 5)

    def test_failing_file_does_not_hold_the_slot_while_waiting(self):
        """Un file che continua a fallire, tra un tentativo e l'altro, lascia lavorare gli altri."""
        import gtd.engine as engine
        bad = make_msg(1, "difettoso.epub", b"x" * 100)
        good = [make_msg(i, f"doc{i}.epub", os.urandom(100)) for i in range(2, 8)]
        client = FakeClient([bad] + good)
        original = client.iter_download
        finished_while_bad_waits = []

        async def flaky(document, **kwargs):
            if document is bad.document:
                finished_while_bad_waits.append(len(list(self.dest.rglob("doc*.epub"))))
                raise asyncio.IncompleteReadError(b"x" * 758, 1347703872)  # la risposta «HTTP» di Telegram
            async for chunk in original(document, **kwargs):
                yield chunk

        client.iter_download = flaky
        old = engine.MAX_ATTEMPTS
        engine.MAX_ATTEMPTS = 3
        try:
            s, _ = self.run_job(client, parallel=1)
        finally:
            engine.MAX_ATTEMPTS = old
        self.assertEqual((s.completed, s.failed), (6, 1))
        self.assertEqual(finished_while_bad_waits[0], 0)
        self.assertGreater(finished_while_bad_waits[-1], 0)  # i buoni sono scesi mentre il difettoso aspettava

    def test_pending_requeued_little_by_little_failed_last(self):
        import gtd.engine as engine
        chat = self._chat_id()
        msgs = [make_msg(i, f"doc{i}.epub", os.urandom(50)) for i in range(1, 301)]
        for m in msgs:
            self.db.register(chat, m.id, m.file.name, self.dest / m.file.name, 50, m.document.id)
        self.db.set_status(chat, 1, "failed")
        self.db.set_last_msg_id(chat, 300)
        self.db.commit()
        self.assertEqual(self.db.pending_msg_ids(chat)[-1], 1)  # i falliti in fondo
        client = FakeClient(msgs)
        calls, original = [], client.get_messages

        async def tracked(entity, ids):
            calls.append(len(ids))
            return await original(entity, ids)

        client.get_messages = tracked
        old = engine.REQUEUE_BATCH, engine.REQUEUE_LOW_WATER
        engine.REQUEUE_BATCH, engine.REQUEUE_LOW_WATER = 50, 10
        try:
            s, _ = self.run_job(client, folder_by_source=False, resume_from_last=True)
        finally:
            engine.REQUEUE_BATCH, engine.REQUEUE_LOW_WATER = old
        self.assertEqual(s.completed, 300)
        self.assertEqual(calls, [50] * 6)

    def test_scan_flood_does_not_stop_downloads(self):
        client = FakeClient([make_msg(1, "a.epub", b"a" * 100)])
        original = client.iter_messages
        state = {"flooded": False}

        async def flooding(entity, reverse=True, offset_id=0):
            async for m in original(entity, reverse=reverse, offset_id=offset_id):
                yield m
            if not state["flooded"]:
                state["flooded"] = True
                raise errors.FloodWaitError(request=None, capture=1)

        client.iter_messages = flooding
        s, rec = self.run_job(client, folder_by_source=False)
        self.assertEqual(s.completed, 1)
        self.assertEqual(rec.floods, [])  # nessun blocco generale dei download
        self.assertTrue(any("i download continuano" in t for _, t in rec.logs))

    def test_rename_and_overwrite_policies(self):
        folder = self.dest
        folder.mkdir(parents=True)
        (folder / "video.mp4").write_bytes(b"vecchio")
        s, _ = self.run_job(FakeClient([self.msgs[2]]), duplicate_policy="rename", folder_by_source=False)
        self.assertTrue((folder / "video_(1).mp4").exists())
        self.assertEqual((folder / "video.mp4").read_bytes(), b"vecchio")

        self.db.conn.execute("DELETE FROM downloads")
        s, _ = self.run_job(FakeClient([self.msgs[2]]), duplicate_policy="overwrite", folder_by_source=False)
        self.assertEqual((folder / "video.mp4").read_bytes(), self.msgs[2].document.data)

    def test_filters_and_auto_folders(self):
        s, _ = self.run_job(FakeClient(self.msgs), extensions={".pdf", ".png"}, min_size=1000,
                            folder_by_source=False, folder_by_type=True, folder_by_date=True)
        self.assertEqual(s.completed, 1)  # foto.png esclusa per dimensione, video per estensione
        self.assertTrue((self.dest / "PDF" / "2026-10" / "libro.pdf").exists())

    def test_downloads_start_while_scanning(self):
        msgs = [make_msg(i, f"doc{i}.pdf", os.urandom(1000)) for i in range(1, 51)]
        client = FakeClient(msgs)
        s, _ = self.run_job(client, parallel=2)
        self.assertEqual(s.completed, 50)
        self.assertLess(client.events.index("download"), client.events.index("fine analisi"))

    def test_cancel_during_scan_stops_everything(self):
        msgs = [make_msg(i, f"doc{i}.pdf", os.urandom(1000)) for i in range(1, 201)]
        client = FakeClient(msgs)
        opts = JobOptions(entity=ENTITY, source_name="X", destination=self.dest, extensions=set())

        async def scenario():
            engine = DownloadEngine(client, self.db, Recorder())
            task = asyncio.create_task(engine.run(opts))
            await asyncio.sleep(0.3)
            engine.cancel()
            return await asyncio.wait_for(task, 5)

        s = asyncio.run(scenario())
        self.assertTrue(s.cancelled)
        self.assertLess(s.scanned, 200)

    def test_flood_wait_is_handled(self):
        s, rec = self.run_job(FakeClient([self.msgs[1]], flood_once=True))
        self.assertEqual(s.completed, 1)
        self.assertTrue(rec.floods and rec.floods[-1] == 0)

    # ---- robustezza, doppioni, chat seguite ----
    def test_broken_connection_does_not_kill_the_batch(self):
        """Il bug del 21/10: IncompleteReadError fermava un download parallelo e il batch «finiva»."""
        msgs = [make_msg(i, f"doc{i}.epub", os.urandom(2000)) for i in range(1, 21)]
        s, _ = self.run_job(FakeClient(msgs, broken_once=True), parallel=3)
        self.assertEqual((s.completed, s.failed), (20, 0))

    def test_up_to_eight_parallel_downloads(self):
        client = FakeClient([make_msg(i, f"doc{i}.epub", os.urandom(1000)) for i in range(1, 31)])
        active, peak = 0, 0
        original = client.iter_download

        async def tracked(*args, **kwargs):
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            try:
                await asyncio.sleep(0.4)  # come un file vero: ci vuole un po', intanto l'analisi ne trova altri
                async for chunk in original(*args, **kwargs):
                    yield chunk
            finally:
                active -= 1

        client.iter_download = tracked
        s, _ = self.run_job(client, parallel=8)
        self.assertEqual(s.completed, 30)
        self.assertEqual(peak, 8)
        s, _ = self.run_job(FakeClient([]), parallel=50)  # oltre il massimo viene limitato, senza errori
        self.assertEqual(s.failed, 0)

    def test_parallel_can_change_during_the_batch(self):
        client = FakeClient([make_msg(i, f"doc{i}.epub", os.urandom(500)) for i in range(1, 61)])
        active, timeline = 0, []
        original = client.iter_download

        async def tracked(*args, **kwargs):
            nonlocal active
            active += 1
            timeline.append((phase, active))
            try:
                await asyncio.sleep(0.15)
                async for chunk in original(*args, **kwargs):
                    yield chunk
            finally:
                active -= 1

        client.iter_download = tracked
        opts = JobOptions(entity=ENTITY, source_name="X", destination=self.dest, extensions=set(),
                          folder_by_source=False, parallel=2)
        phase = "2"

        async def scenario():
            nonlocal phase
            eng = DownloadEngine(client, self.db, Recorder())
            task = asyncio.create_task(eng.run(opts))
            await asyncio.sleep(0.8)
            eng.pause()                      # come nell'app: si cambia in pausa
            phase = "6"
            eng.set_parallel(6)
            eng.resume()
            await asyncio.sleep(0.8)
            eng.pause()
            eng.set_parallel(1)
            await asyncio.sleep(0.3)         # i download già avviati finiscono…
            phase = "1"                      # …e da qui in poi uno alla volta
            eng.resume()
            return await asyncio.wait_for(task, 30)

        s = asyncio.run(scenario())
        self.assertEqual(s.completed, 60)
        peak = {p: max(a for ph, a in timeline if ph == p) for p in ("2", "6")}
        self.assertEqual(peak, {"2": 2, "6": 6})
        later = [a for ph, a in timeline if ph == "1"][3:]  # dopo che quelli già avviati sono finiti
        self.assertTrue(later and max(later) == 1, later)

    def test_stalled_download_is_retried(self):
        import gtd.engine as engine
        old, engine.CHUNK_TIMEOUT = engine.CHUNK_TIMEOUT, 0.3
        try:
            s, rec = self.run_job(FakeClient([self.msgs[2]], stall_once=True))
        finally:
            engine.CHUNK_TIMEOUT = old
        self.assertEqual(s.completed, 1)
        self.assertTrue(any("nessun dato" in t for _, t in rec.logs))

    def test_same_document_reposted_is_skipped(self):
        data = os.urandom(3000)
        msgs = [make_msg(1, "Autore - Titolo.epub", data, doc_id=77),
                make_msg(2, "Autore_Titolo_2024.epub", data, doc_id=77)]
        s, rec = self.run_job(FakeClient(msgs), folder_by_source=False)
        self.assertEqual((s.completed, s.duplicates), (1, 1))
        self.assertTrue(any(lvl == "skip" and "doppione" in t for lvl, t in rec.logs))

    def test_same_content_reuploaded_is_discarded(self):
        data = os.urandom(3000)
        self.run_job(FakeClient([make_msg(1, "a.epub", data, doc_id=1)]), folder_by_source=False)
        s, _ = self.run_job(FakeClient([make_msg(2, "b.epub", data, doc_id=2)]), folder_by_source=False)
        self.assertEqual(s.duplicates, 1)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()), ["a.epub"])

    def test_skips_are_logged_with_reason(self):
        self.run_job(FakeClient(self.msgs))
        _, rec = self.run_job(FakeClient(self.msgs))
        skips = [t for lvl, t in rec.logs if lvl == "skip"]
        self.assertEqual(len(skips), 3)
        self.assertIn("già scaricato in precedenza", skips[0])

    def test_follow_downloads_new_files_when_telegram_notifies(self):
        client = FakeClient([make_msg(1, "vecchio.epub", b"v" * 100)])
        opts = JobOptions(entity=ENTITY, source_name="X", destination=self.dest, extensions=set(),
                          folder_by_source=False, follow=True)

        async def scenario():
            import gtd.engine as engine
            engine.FOLLOW_GROUPING_DELAY = 0
            eng = DownloadEngine(client, self.db, Recorder())
            task = asyncio.create_task(eng.run(opts))
            while not client.handlers:  # analisi iniziale finita, ora è in ascolto
                await asyncio.sleep(0.05)
            client.messages.append(make_msg(2, "nuovo.epub", b"n" * 100))
            await client.handlers[0](None)  # Telegram: «è arrivato un messaggio»
            for _ in range(100):
                if (self.dest / "nuovo.epub").exists():
                    break
                await asyncio.sleep(0.05)
            eng.cancel()
            return await asyncio.wait_for(task, 5)

        s = asyncio.run(scenario())
        self.assertTrue((self.dest / "nuovo.epub").exists())
        self.assertEqual(s.completed, 2)
        self.assertFalse(client.handlers)  # in ascolto disattivato all'uscita

    def test_resume_scans_only_new_messages_and_pending(self):
        self.run_job(FakeClient(self.msgs), folder_by_source=False)
        # un file trovato ma mai scaricato (app chiusa prima) + un messaggio arrivato a app chiusa
        pending = make_msg(4, "in_sospeso.epub", b"p" * 50)
        self.db.register(self._chat_id(), 4, "in_sospeso.epub", self.dest / "in_sospeso.epub", 50, 4000)
        newer = make_msg(5, "arrivato_dopo.epub", b"d" * 60)
        s, _ = self.run_job(FakeClient(self.msgs + [pending, newer]), folder_by_source=False,
                            resume_from_last=True)
        self.assertEqual(s.scanned, 2)   # solo i messaggi 4 e 5, non tutta la chat
        self.assertEqual(s.completed, 2)
        self.assertTrue((self.dest / "in_sospeso.epub").exists())
        self.assertTrue((self.dest / "arrivato_dopo.epub").exists())


if __name__ == "__main__":
    unittest.main()
