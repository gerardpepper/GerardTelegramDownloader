"""Percorsi dati e impostazioni persistenti dell'applicazione."""

import json
import logging
import os
from dataclasses import asdict, dataclass, field, fields
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import APP_NAME, dpapi

log = logging.getLogger(__name__)


def data_dir() -> Path:
    base = Path(os.environ.get("APPDATA") or Path.home())
    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def setup_logging() -> None:
    handler = RotatingFileHandler(data_dir() / "app.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    logging.getLogger("telethon").setLevel(logging.WARNING)
    # «Server closed the connection» compare migliaia di volte ed è normale: Telethon si ricollega da solo
    logging.getLogger("telethon.network").setLevel(logging.ERROR)


@dataclass
class Settings:
    api_id: int = 0
    api_hash: str = ""  # su disco viene salvato cifrato con DPAPI
    destination: str = ""
    last_source_id: int = 0
    last_manual_source: str = ""
    presets: list[str] = field(default_factory=list)
    custom_extensions: str = ""
    min_size_mb: int = 0
    max_size_mb: int = 0
    duplicate_policy: str = "skip"
    folder_by_source: bool = True
    folder_by_type: bool = False
    folder_by_date: bool = False
    parallel: int = 2
    notifications: bool = True
    skip_duplicates: bool = True
    follow: bool = False
    follow_resume: bool = False  # al riavvio riprende a seguire la chat (era in ascolto quando l'app è stata chiusa)
    show_warnings: bool = True
    theme: str = "system"
    language: str = ""  # vuoto = lingua di Windows

    @staticmethod
    def _path() -> Path:
        return data_dir() / "settings.json"

    @classmethod
    def load(cls) -> "Settings":
        try:
            raw = json.loads(cls._path().read_text("utf-8"))
        except (OSError, ValueError):
            return cls()
        known = {f.name for f in fields(cls)} - {"api_hash"}
        settings = cls(**{k: v for k, v in raw.items() if k in known})
        encrypted = raw.get("api_hash_enc", "")
        if encrypted:
            try:
                settings.api_hash = dpapi.unprotect_str(encrypted)
            except (OSError, ValueError):
                log.warning("Impossibile decifrare api_hash salvato")
        return settings

    def save(self) -> None:
        raw = asdict(self)
        api_hash = raw.pop("api_hash")
        raw["api_hash_enc"] = dpapi.protect_str(api_hash) if api_hash else ""
        self._path().write_text(json.dumps(raw, indent=2, ensure_ascii=False), "utf-8")
