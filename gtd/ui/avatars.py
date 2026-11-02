"""Icone delle chat: foto profilo Telegram (con cache su disco) o cerchio con iniziali."""

import logging
from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap
from telethon import utils

from ..config import data_dir

log = logging.getLogger(__name__)

PIXELS = 64  # disegnate più grandi del necessario: restano nitide anche con lo zoom di Windows
_COLORS = ["#e17076", "#faa774", "#a695e7", "#7bc862", "#6ec9cb", "#65aadd", "#ee7aae"]


def _circle(pixmap: QPixmap) -> QIcon:
    out = QPixmap(PIXELS, PIXELS)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    path = QPainterPath()
    path.addEllipse(QRectF(0, 0, PIXELS, PIXELS))
    p.setClipPath(path)
    scaled = pixmap.scaled(PIXELS, PIXELS, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation)
    p.drawPixmap((PIXELS - scaled.width()) // 2, (PIXELS - scaled.height()) // 2, scaled)
    p.end()
    return QIcon(out)


def initials_icon(name: str, peer_id: int) -> QIcon:
    """Come fa Telegram: cerchio colorato (colore stabile per chat) con le iniziali."""
    words = [w for w in (name or "?").split() if w[:1].isalnum()]
    letters = "".join(w[0] for w in words[:2]).upper() or (name or "?")[:1].upper()
    pm = QPixmap(PIXELS, PIXELS)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(_COLORS[abs(peer_id) % len(_COLORS)])))
    p.drawEllipse(0, 0, PIXELS, PIXELS)
    font = QFont()
    font.setBold(True)
    font.setPixelSize(int(PIXELS * (0.42 if len(letters) < 2 else 0.36)))
    p.setFont(font)
    p.setPen(QColor("white"))
    p.drawText(QRectF(0, 0, PIXELS, PIXELS), Qt.AlignmentFlag.AlignCenter, letters)
    p.end()
    return QIcon(pm)


def icon_from_bytes(data: bytes) -> QIcon | None:
    pm = QPixmap()
    if not data or not pm.loadFromData(data):
        return None
    return _circle(pm)


class AvatarCache:
    """Salva le foto profilo in %APPDATA%\\GerardTelegramDownloader\\avatars, una per versione della foto."""

    def __init__(self):
        self.folder = data_dir() / "avatars"
        self.folder.mkdir(exist_ok=True)

    def _path(self, entity) -> Path | None:
        photo_id = getattr(getattr(entity, "photo", None), "photo_id", None)
        if not photo_id:
            return None
        return self.folder / f"{utils.get_peer_id(entity)}_{photo_id}.jpg"

    def has_photo(self, entity) -> bool:
        return self._path(entity) is not None

    def cached_icon(self, entity) -> QIcon | None:
        path = self._path(entity)
        if path and path.exists():
            return icon_from_bytes(path.read_bytes())
        return None

    async def fetch_icon(self, client, entity) -> QIcon | None:
        path = self._path(entity)
        if not path:
            return None
        data = await client.download_profile_photo(entity, file=bytes, download_big=False)
        if not data:
            return None
        for old in self.folder.glob(f"{utils.get_peer_id(entity)}_*.jpg"):  # foto precedenti della stessa chat
            old.unlink(missing_ok=True)
        path.write_bytes(data)
        return icon_from_bytes(data)
