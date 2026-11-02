"""Impedisce a Windows di andare in sospensione mentre l'app lavora (lo schermo può spegnersi)."""

import ctypes

_ES_CONTINUOUS = 0x80000000
_ES_SYSTEM_REQUIRED = 0x00000001


def keep_awake(enabled: bool) -> None:
    flags = _ES_CONTINUOUS | (_ES_SYSTEM_REQUIRED if enabled else 0)
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ctypes.c_uint(flags))
    except (AttributeError, OSError):
        pass
