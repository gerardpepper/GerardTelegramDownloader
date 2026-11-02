"""Barra di avanzamento sull'icona nella barra delle applicazioni di Windows (ITaskbarList3/4).

Chiamate COM dirette via ctypes; se qualcosa non è disponibile la classe diventa silenziosamente inattiva.
"""

import ctypes
import logging
import uuid
from ctypes import HRESULT, POINTER, byref, c_void_p, wintypes

log = logging.getLogger(__name__)

_CLSID_TASKBARLIST = "56FDF344-FD6D-11d0-958A-006097C9A090"
# ITaskbarList4 (estende ITaskbarList3, stessi indici nella vtable): è quella che Windows 11 espone in modo affidabile
_IID_ITASKBARLIST4 = "C43DC798-95D1-4BEA-9030-BB99E2983A1A"
_CLSCTX_INPROC_SERVER = 0x1

# indici nella vtable: IUnknown (0-2), ITaskbarList (3-7), ITaskbarList2 (8), ITaskbarList3 (9-)
_HRINIT, _SET_PROGRESS_VALUE, _SET_PROGRESS_STATE = 3, 9, 10

NO_PROGRESS, INDETERMINATE, NORMAL, ERROR, PAUSED = 0x0, 0x1, 0x2, 0x4, 0x8


class _GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD),
                ("Data4", ctypes.c_ubyte * 8)]

    @classmethod
    def parse(cls, text: str) -> "_GUID":
        return cls.from_buffer_copy(uuid.UUID(text).bytes_le)


class TaskbarProgress:
    def __init__(self, hwnd: int):
        self.hwnd = wintypes.HWND(hwnd)
        self._obj = None
        self._state = None
        try:
            ole32 = ctypes.OleDLL("ole32")
            ole32.CoInitializeEx(None, 0x2)  # già inizializzato da Qt: va bene comunque
        except OSError:
            pass
        try:
            ole32 = ctypes.OleDLL("ole32")
            ole32.CoCreateInstance.argtypes = [POINTER(_GUID), c_void_p, wintypes.DWORD, POINTER(_GUID),
                                               POINTER(c_void_p)]
            obj = c_void_p()
            ole32.CoCreateInstance(byref(_GUID.parse(_CLSID_TASKBARLIST)), None, _CLSCTX_INPROC_SERVER,
                                   byref(_GUID.parse(_IID_ITASKBARLIST4)), byref(obj))
            self._vtbl = ctypes.cast(obj, POINTER(POINTER(c_void_p))).contents
            self._obj = obj
            self._call(_HRINIT, [])
        except OSError:
            log.warning("Barra di avanzamento nella barra delle applicazioni non disponibile", exc_info=True)
            self._obj = None

    def _call(self, index: int, argtypes: list, *args) -> None:
        proto = ctypes.WINFUNCTYPE(HRESULT, c_void_p, *argtypes)
        proto(self._vtbl[index])(self._obj, *args)

    def set_state(self, state: int) -> None:
        if self._obj is None or state == self._state:
            return
        try:
            self._call(_SET_PROGRESS_STATE, [wintypes.HWND, ctypes.c_int], self.hwnd, state)
            self._state = state
        except OSError:
            pass

    def set_value(self, done: int, total: int) -> None:
        if self._obj is None:
            return
        try:
            self._call(_SET_PROGRESS_VALUE, [wintypes.HWND, ctypes.c_ulonglong, ctypes.c_ulonglong],
                       self.hwnd, max(0, done), max(1, total))
            if self._state in (None, NO_PROGRESS, INDETERMINATE):
                self._state = NORMAL  # Windows passa da solo allo stato normale
        except OSError:
            pass

    def clear(self) -> None:
        self.set_state(NO_PROGRESS)
