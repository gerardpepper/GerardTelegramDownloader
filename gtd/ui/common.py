"""Utilità condivise dall'interfaccia: task asincroni, icona, temi."""

import asyncio
import logging

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPalette, QPen, QPixmap
from PyQt6.QtWidgets import QApplication

log = logging.getLogger(__name__)
_tasks: set[asyncio.Task] = set()


def spawn(coro) -> asyncio.Task:
    """Avvia una coroutine dal codice Qt mantenendone il riferimento e registrando gli errori."""
    task = asyncio.ensure_future(coro)
    _tasks.add(task)
    task.add_done_callback(_task_done)
    return task


def _task_done(task: asyncio.Task) -> None:
    _tasks.discard(task)
    if not task.cancelled() and task.exception():
        log.error("Errore non gestito in un task", exc_info=task.exception())


def app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.scale(size / 256, size / 256)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#229ED9"))
        p.drawEllipse(8, 8, 240, 240)
        pen = QPen(QColor("white"), 24, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.drawLine(128, 58, 128, 160)
        p.drawPolyline([QPointF(82, 118), QPointF(128, 164), QPointF(174, 118)])
        p.drawLine(74, 200, 182, 200)
        p.end()
        icon.addPixmap(pm)
    return icon


def _dark_palette() -> QPalette:
    pal = QPalette()
    base, window, text, mid = QColor("#1e1f22"), QColor("#2b2d31"), QColor("#e6e6e6"), QColor("#3a3c42")
    accent = QColor("#229ED9")
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
        pal.setColor(group, QPalette.ColorRole.Window, window)
        pal.setColor(group, QPalette.ColorRole.WindowText, text)
        pal.setColor(group, QPalette.ColorRole.Base, base)
        pal.setColor(group, QPalette.ColorRole.AlternateBase, window)
        pal.setColor(group, QPalette.ColorRole.Text, text)
        pal.setColor(group, QPalette.ColorRole.Button, mid)
        pal.setColor(group, QPalette.ColorRole.ButtonText, text)
        pal.setColor(group, QPalette.ColorRole.ToolTipBase, window)
        pal.setColor(group, QPalette.ColorRole.ToolTipText, text)
        pal.setColor(group, QPalette.ColorRole.Highlight, accent)
        pal.setColor(group, QPalette.ColorRole.HighlightedText, QColor("white"))
        pal.setColor(group, QPalette.ColorRole.Link, QColor("#5fb8ec"))
        pal.setColor(group, QPalette.ColorRole.PlaceholderText, QColor("#8a8d93"))
    disabled = QColor("#7a7d83")
    for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
        pal.setColor(QPalette.ColorGroup.Disabled, role, disabled)
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, window)
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, window)
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, window)
    return pal


def apply_theme(name: str) -> None:
    """name: 'system' | 'light' | 'dark'."""
    app = QApplication.instance()
    hints = QGuiApplication.styleHints()
    if hasattr(hints, "setColorScheme"):
        hints.setColorScheme({"light": Qt.ColorScheme.Light, "dark": Qt.ColorScheme.Dark}
                             .get(name, Qt.ColorScheme.Unknown))
    if name == "system":
        dark = hints.colorScheme() == Qt.ColorScheme.Dark
    else:
        dark = name == "dark"
    app.setPalette(_dark_palette() if dark else app.style().standardPalette())
