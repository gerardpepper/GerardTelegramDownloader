"""Cifratura locale tramite Windows DPAPI (legata all'utente Windows corrente)."""

import base64
import ctypes
from ctypes import wintypes

_CRYPTPROTECT_UI_FORBIDDEN = 0x01
_ENTROPY = b"GerardTelegramDownloader/v1"


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


_crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

_crypt32.CryptProtectData.argtypes = [
    ctypes.POINTER(_DataBlob), wintypes.LPCWSTR, ctypes.POINTER(_DataBlob),
    ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_DataBlob),
]
_crypt32.CryptProtectData.restype = wintypes.BOOL
_crypt32.CryptUnprotectData.argtypes = [
    ctypes.POINTER(_DataBlob), ctypes.c_void_p, ctypes.POINTER(_DataBlob),
    ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_DataBlob),
]
_crypt32.CryptUnprotectData.restype = wintypes.BOOL
_kernel32.LocalFree.argtypes = [ctypes.c_void_p]
_kernel32.LocalFree.restype = ctypes.c_void_p


def _to_blob(data: bytes):
    buf = ctypes.create_string_buffer(data, len(data))
    blob = _DataBlob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    return blob, buf  # buf va mantenuto vivo finché si usa il blob


def _take(blob: _DataBlob) -> bytes:
    try:
        return ctypes.string_at(blob.pbData, blob.cbData)
    finally:
        _kernel32.LocalFree(ctypes.cast(blob.pbData, ctypes.c_void_p))


def protect(data: bytes) -> bytes:
    src, _buf = _to_blob(data)
    ent, _ebuf = _to_blob(_ENTROPY)
    out = _DataBlob()
    if not _crypt32.CryptProtectData(ctypes.byref(src), "GTD", ctypes.byref(ent),
                                     None, None, _CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(out)):
        raise ctypes.WinError(ctypes.get_last_error())
    return _take(out)


def unprotect(data: bytes) -> bytes:
    src, _buf = _to_blob(data)
    ent, _ebuf = _to_blob(_ENTROPY)
    out = _DataBlob()
    if not _crypt32.CryptUnprotectData(ctypes.byref(src), None, ctypes.byref(ent),
                                       None, None, _CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(out)):
        raise ctypes.WinError(ctypes.get_last_error())
    return _take(out)


def protect_str(text: str) -> str:
    return base64.b64encode(protect(text.encode("utf-8"))).decode("ascii")


def unprotect_str(text: str) -> str:
    return unprotect(base64.b64decode(text)).decode("utf-8")
