"""Creazione del client Telethon e persistenza cifrata della sessione."""

import logging

from telethon import TelegramClient
from telethon.sessions import StringSession

from . import APP_NAME, __version__, dpapi
from .config import data_dir

log = logging.getLogger(__name__)


def _session_file():
    return data_dir() / "session.dat"


def load_session() -> str:
    try:
        return dpapi.unprotect(_session_file().read_bytes()).decode("utf-8")
    except FileNotFoundError:
        return ""
    except OSError:
        log.warning("Sessione salvata non leggibile: verrà richiesto un nuovo accesso")
        return ""


def save_session(client: TelegramClient) -> None:
    _session_file().write_bytes(dpapi.protect(client.session.save().encode("utf-8")))


def clear_session() -> None:
    _session_file().unlink(missing_ok=True)


def make_client(api_id: int, api_hash: str) -> TelegramClient:
    # flood_sleep_threshold=0: ogni FloodWait arriva a noi, così lo mostriamo a schermo
    return TelegramClient(
        StringSession(load_session()), api_id, api_hash,
        flood_sleep_threshold=0,
        device_model=APP_NAME,
        app_version=__version__,
        system_version="Windows",
    )
