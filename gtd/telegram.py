"""Creazione del client Telethon e persistenza cifrata della sessione."""

import logging
import os
import sys

from telethon import TelegramClient
from telethon.sessions import StringSession

from . import APP_NAME, __version__, secret
from .config import data_dir

log = logging.getLogger(__name__)


def _session_file():
    return data_dir() / "session.dat"


def load_session() -> str:
    try:
        return secret.unprotect(_session_file().read_bytes()).decode("utf-8")
    except FileNotFoundError:
        return ""
    except (OSError, ValueError):
        log.warning("Sessione salvata non leggibile: verrà richiesto un nuovo accesso")
        return ""


def save_session(client: TelegramClient) -> None:
    path = _session_file()
    path.write_bytes(secret.protect(client.session.save().encode("utf-8")))
    if sys.platform != "win32":
        os.chmod(path, 0o600)


def clear_session() -> None:
    _session_file().unlink(missing_ok=True)


def make_client(api_id: int, api_hash: str) -> TelegramClient:
    # flood_sleep_threshold=0: ogni FloodWait arriva a noi, così lo mostriamo a schermo
    return TelegramClient(
        StringSession(load_session()), api_id, api_hash,
        flood_sleep_threshold=0,
        device_model=APP_NAME,
        app_version=__version__,
        system_version="Windows" if sys.platform == "win32" else "Linux",
    )
