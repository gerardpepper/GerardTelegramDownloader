"""Protezione locale di chiavi API e sessione.

Windows: cifratura DPAPI, legata all'utente Windows (copiata su un altro PC non funziona).
Linux e altri: nessuna cifratura di sistema affidabile ovunque (il portachiavi non c'è sempre), quindi i dati
restano in file leggibili solo dal tuo utente, nella cartella dati con permessi 700 (come Telegram Desktop).
"""

import base64
import sys

if sys.platform == "win32":
    from .dpapi import protect, unprotect
else:
    _PREFIX = b"GTD-PLAIN-1:"

    def protect(data: bytes) -> bytes:
        return _PREFIX + data

    def unprotect(data: bytes) -> bytes:
        if not data.startswith(_PREFIX):
            raise ValueError("dati salvati da un altro sistema")
        return data[len(_PREFIX):]


def protect_str(text: str) -> str:
    return base64.b64encode(protect(text.encode("utf-8"))).decode("ascii")


def unprotect_str(text: str) -> str:
    return unprotect(base64.b64decode(text)).decode("utf-8")
