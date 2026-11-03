"""Impedisce a Windows di andare in sospensione mentre l'app lavora (lo schermo può spegnersi)."""

import ctypes

_ES_CONTINUOUS = 0x80000000
_ES_SYSTEM_REQUIRED = 0x00000001

_holders = 0  # download e chat seguite possono lavorare insieme: si torna normali quando hanno finito tutti


def keep_awake(enabled: bool) -> None:
    """Ogni keep_awake(True) va chiuso con un keep_awake(False)."""
    global _holders
    _holders = max(0, _holders + (1 if enabled else -1))
    flags = _ES_CONTINUOUS | (_ES_SYSTEM_REQUIRED if _holders else 0)
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ctypes.c_uint(flags))
    except (AttributeError, OSError):
        pass
