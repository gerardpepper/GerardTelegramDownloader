"""Stato persistente dei download (SQLite) per la ripresa dopo interruzioni."""

import sqlite3
from datetime import datetime
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS downloads (
    chat_id    INTEGER NOT NULL,
    msg_id     INTEGER NOT NULL,
    file_name  TEXT    NOT NULL,
    target     TEXT    NOT NULL,
    size       INTEGER NOT NULL,
    downloaded INTEGER NOT NULL DEFAULT 0,
    status     TEXT    NOT NULL,          -- pending | partial | completed | failed
    sha256     TEXT,
    updated_at TEXT    NOT NULL,
    PRIMARY KEY (chat_id, msg_id)
);
CREATE TABLE IF NOT EXISTS chats (
    chat_id     INTEGER PRIMARY KEY,
    last_msg_id INTEGER NOT NULL           -- ultimo messaggio già analizzato (per seguire la chat)
);
"""

# colonne aggiunte dopo la prima versione: create al volo sui database esistenti
_MIGRATIONS = [
    ("doc_id", "ALTER TABLE downloads ADD COLUMN doc_id INTEGER"),
]
_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_downloads_doc ON downloads(doc_id)",
    "CREATE INDEX IF NOT EXISTS idx_downloads_sha ON downloads(sha256)",
]


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class StateDB:
    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(_SCHEMA)
        columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(downloads)")}
        for column, sql in _MIGRATIONS:
            if column not in columns:
                self.conn.execute(sql)
        for sql in _INDEXES:
            self.conn.execute(sql)
        self.conn.commit()

    def get(self, chat_id: int, msg_id: int):
        return self.conn.execute(
            "SELECT * FROM downloads WHERE chat_id=? AND msg_id=?", (chat_id, msg_id)).fetchone()

    def register(self, chat_id: int, msg_id: int, file_name: str, target: Path, size: int,
                 doc_id: int | None = None) -> None:
        self.conn.execute(
            """INSERT INTO downloads (chat_id, msg_id, file_name, target, size, downloaded, status, updated_at, doc_id)
               VALUES (?, ?, ?, ?, ?, 0, 'pending', ?, ?)
               ON CONFLICT(chat_id, msg_id) DO UPDATE SET
                   file_name=excluded.file_name, target=excluded.target, size=excluded.size, doc_id=excluded.doc_id,
                   status=CASE WHEN downloads.target=excluded.target THEN downloads.status ELSE 'pending' END,
                   updated_at=excluded.updated_at""",
            (chat_id, msg_id, file_name, str(target), size, _now(), doc_id))

    def find_completed_doc(self, doc_id: int):
        """Un file di Telegram (stesso documento) già scaricato, anche da un altro messaggio o chat."""
        return self.conn.execute(
            "SELECT * FROM downloads WHERE doc_id=? AND status='completed' LIMIT 1", (doc_id,)).fetchone()

    def find_completed_sha(self, sha256: str, chat_id: int, msg_id: int):
        """Un altro file già scaricato con contenuto identico."""
        return self.conn.execute(
            """SELECT * FROM downloads WHERE sha256=? AND status='completed'
               AND NOT (chat_id=? AND msg_id=?) LIMIT 1""", (sha256, chat_id, msg_id)).fetchone()

    def pending_msg_ids(self, chat_id: int) -> list[int]:
        return [row["msg_id"] for row in self.conn.execute(
            "SELECT msg_id FROM downloads WHERE chat_id=? AND status IN ('pending','partial','failed') ORDER BY msg_id",
            (chat_id,))]

    def set_progress(self, chat_id: int, msg_id: int, downloaded: int) -> None:
        self.conn.execute(
            "UPDATE downloads SET downloaded=?, status='partial', updated_at=? WHERE chat_id=? AND msg_id=?",
            (downloaded, _now(), chat_id, msg_id))
        self.conn.commit()

    def set_completed(self, chat_id: int, msg_id: int, size: int, sha256: str, target: Path | None = None) -> None:
        """target diverso dall'originale: il file era un doppione di un file già presente in quel percorso."""
        self.conn.execute(
            """UPDATE downloads SET downloaded=?, size=?, status='completed', sha256=?, updated_at=?,
                   target=COALESCE(?, target)
               WHERE chat_id=? AND msg_id=?""",
            (size, size, sha256, _now(), str(target) if target else None, chat_id, msg_id))
        self.conn.commit()

    def set_status(self, chat_id: int, msg_id: int, status: str) -> None:
        self.conn.execute("UPDATE downloads SET status=?, updated_at=? WHERE chat_id=? AND msg_id=?",
                          (status, _now(), chat_id, msg_id))
        self.conn.commit()

    def last_msg_id(self, chat_id: int) -> int:
        row = self.conn.execute("SELECT last_msg_id FROM chats WHERE chat_id=?", (chat_id,)).fetchone()
        return row["last_msg_id"] if row else 0

    def set_last_msg_id(self, chat_id: int, msg_id: int) -> None:
        self.conn.execute(
            """INSERT INTO chats (chat_id, last_msg_id) VALUES (?, ?)
               ON CONFLICT(chat_id) DO UPDATE SET last_msg_id=MAX(last_msg_id, excluded.last_msg_id)""",
            (chat_id, msg_id))
        self.conn.commit()

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()
