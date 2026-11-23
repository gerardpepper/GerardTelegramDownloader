"""Impedisce al PC di andare in sospensione mentre l'app lavora (lo schermo può spegnersi).

Windows: SetThreadExecutionState. Linux: systemd-inhibit (se c'è), legato alla vita dell'app.
"""

import ctypes
import logging
import os
import subprocess
import sys

log = logging.getLogger(__name__)

_ES_CONTINUOUS = 0x80000000
_ES_SYSTEM_REQUIRED = 0x00000001

_holders = 0  # download e chat seguite possono lavorare insieme: si torna normali quando hanno finito tutti
_inhibitor: subprocess.Popen | None = None


def keep_awake(enabled: bool) -> None:
    """Ogni keep_awake(True) va chiuso con un keep_awake(False)."""
    global _holders
    _holders = max(0, _holders + (1 if enabled else -1))
    if sys.platform == "win32":
        flags = _ES_CONTINUOUS | (_ES_SYSTEM_REQUIRED if _holders else 0)
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ctypes.c_uint(flags))
        except (AttributeError, OSError):
            pass
    else:
        _linux_inhibit(bool(_holders))


def _linux_inhibit(on: bool) -> None:
    global _inhibitor
    if on and _inhibitor is None:
        try:
            # tail --pid: il blocco finisce da solo anche se l'app viene chiusa male
            _inhibitor = subprocess.Popen(
                ["systemd-inhibit", "--what=sleep:idle", "--who=Gerard Telegram Downloader",
                 "--why=Download in corso", "--mode=block",
                 "tail", f"--pid={os.getpid()}", "-f", "/dev/null"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            log.info("systemd-inhibit non disponibile: il PC potrebbe andare in sospensione durante i download")
    elif not on and _inhibitor is not None:
        _inhibitor.terminate()
        try:
            _inhibitor.wait(timeout=2)
        except subprocess.TimeoutExpired:
            _inhibitor.kill()
        _inhibitor = None
