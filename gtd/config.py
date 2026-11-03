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
class FollowedChat:
    """Una chat della scheda «Segui», con le sue impostazioni."""
    peer_id: int = 0
    source: str = ""                # link / @username, se la chat è stata indicata così
    name: str = ""
    destination: str = ""
    presets: list[str] = field(default_factory=list)
    custom_extensions: str = ""
    name_filter: str = ""
    name_in_caption: bool = True
    folder_by_source: bool = True
    folder_by_type: bool = False
    folder_by_date: bool = False
    duplicate_policy: str = "skip"   # skip | rename | overwrite, come nella scheda Download
    skip_duplicates: bool = True
    active: bool = True             # avviata (▶): la si segue, anche al prossimo avvio dell'app

    @classmethod
    def from_dict(cls, raw: dict) -> "FollowedChat":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in raw.items() if k in known})


@dataclass
class Settings:
    api_id: int = 0
    api_hash: str = ""  # su disco viene salvato cifrato con DPAPI
    destination: str = ""
    last_source_id: int = 0
    last_manual_source: str = ""
    presets: list[str] = field(default_factory=list)
    custom_extensions: str = ""
    name_filter: str = ""
    name_in_caption: bool = True
    min_size_mb: int = 0
    max_size_mb: int = 0
    duplicate_policy: str = "skip"
    folder_by_source: bool = True
    folder_by_type: bool = False
    folder_by_date: bool = False
    parallel: int = 2
    notifications: bool = True
    skip_duplicates: bool = True
    followed: list[FollowedChat] = field(default_factory=list)
    follow_parallel: int = 2  # download contemporanei di tutte le chat seguite insieme
    follow_show_warnings: bool = True
    confirm_close: bool = True  # alla chiusura con download in corso chiede conferma
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
        known = {f.name for f in fields(cls)} - {"api_hash", "followed"}
        settings = cls(**{k: v for k, v in raw.items() if k in known})
        settings.followed = [FollowedChat.from_dict(d) for d in raw.get("followed", [])]
        if raw.get("follow") and (raw.get("last_source_id") or raw.get("last_manual_source")):
            # versione precedente: si poteva seguire una sola chat, con le impostazioni della pagina Download
            settings.followed.append(FollowedChat(
                peer_id=settings.last_source_id, source=settings.last_manual_source,
                destination=settings.destination, presets=list(settings.presets),
                custom_extensions=settings.custom_extensions, folder_by_source=settings.folder_by_source,
                folder_by_type=settings.folder_by_type, folder_by_date=settings.folder_by_date,
                duplicate_policy=settings.duplicate_policy, skip_duplicates=settings.skip_duplicates,
                active=bool(raw.get("follow_resume"))))
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
