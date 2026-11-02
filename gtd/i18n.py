"""Traduzioni dell'interfaccia.

Il testo italiano è la chiave: tr("Pausa") restituisce la traduzione nella lingua attiva (o l'italiano se manca).
I segnaposto si scrivono come in str.format: tr("{n} file trovati", n=12).
Le traduzioni stanno in gtd/locales/<codice>.py (dizionario STRINGS); tests/test_i18n.py verifica che siano complete.
"""

from __future__ import annotations

from PyQt6.QtCore import QLocale

from .locales import en, es, fr  # import espliciti: così PyInstaller li include nell'exe

_CATALOGS = {"en": en.STRINGS, "fr": fr.STRINGS, "es": es.STRINGS}

# nome di ogni lingua scritto nella lingua stessa (così è riconoscibile anche se non la capisci)
LANGUAGES = {"it": "Italiano", "en": "English", "fr": "Français", "es": "Español"}
DEFAULT = "en"  # per un Windows in una lingua non supportata

_language = "it"
_strings: dict[str, str] = {}


def system_language() -> str:
    code = QLocale.system().name().split("_")[0].lower()
    return code if code in LANGUAGES else DEFAULT


def set_language(code: str) -> str:
    """code vuoto = lingua di Windows. Ritorna la lingua effettivamente attivata."""
    global _language, _strings
    code = code if code in LANGUAGES else system_language()
    _language = code
    _strings = _CATALOGS.get(code, {})
    return code


def current_language() -> str:
    return _language


def N_(text: str) -> str:
    """Segna un testo da tradurre più tardi con tr() (es. costanti): non lo traduce, serve al controllo."""
    return text


def tr(text: str, **values) -> str:
    translated = _strings.get(text, text)
    return translated.format(**values) if values else translated
