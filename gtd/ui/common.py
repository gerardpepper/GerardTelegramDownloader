"""Utilità condivise dall'interfaccia: task asincroni, icona, temi."""

import asyncio
import logging
from typing import Callable

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPalette, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QCheckBox, QHBoxLayout, QMessageBox, QToolButton, QWidget

from ..i18n import tr

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


def confirm(parent: QWidget, title: str, text: str, yes: str, checkbox: QCheckBox | None = None,
            no: str | None = None) -> bool:
    """Domanda con pulsanti nella lingua dell'app (Yes/No standard di Qt restano in inglese)."""
    box = QMessageBox(QMessageBox.Icon.Question, title, text, parent=parent)
    ok = box.addButton(yes, QMessageBox.ButtonRole.AcceptRole)
    box.addButton(no or tr("Annulla"), QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(ok)
    if checkbox is not None:
        box.setCheckBox(checkbox)
    box.exec()
    return box.clickedButton() is ok


def _drawn_icon(color: QColor, draw: Callable[[QPainter], None]) -> QIcon:
    """Icona disegnata su una griglia 24×24 (l'app non ha file di immagini); disabilitata la ingrigisce Qt."""
    icon = QIcon()
    for size in (16, 20, 24, 32, 48):
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.scale(size / 24, size / 24)
        p.setPen(QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(color)
        draw(p)
        p.end()
        icon.addPixmap(pm)
    return icon


def logout_icon(color: QColor) -> QIcon:
    """Porta aperta con freccia verso l'esterno."""
    def draw(p: QPainter) -> None:
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolyline([QPointF(13, 7), QPointF(13, 4), QPointF(4, 4), QPointF(4, 20), QPointF(13, 20), QPointF(13, 17)])
        p.drawLine(QPointF(9, 12), QPointF(21, 12))
        p.drawPolyline([QPointF(17, 8), QPointF(21, 12), QPointF(17, 16)])
    return _drawn_icon(color, draw)


# colori fissi, leggibili sia con il tema chiaro sia con quello scuro
PLAY_COLOR, PAUSE_COLOR, STOP_COLOR = QColor("#2e9d4a"), QColor("#d08700"), QColor("#d03030")


def play_icon() -> QIcon:
    return _drawn_icon(PLAY_COLOR, lambda p: p.drawPolygon([QPointF(7, 4), QPointF(20, 12), QPointF(7, 20)]))


def pause_icon() -> QIcon:
    def draw(p: QPainter) -> None:
        p.drawRoundedRect(QRectF(6, 4, 4, 16), 1, 1)
        p.drawRoundedRect(QRectF(14, 4, 4, 16), 1, 1)
    return _drawn_icon(PAUSE_COLOR, draw)


def stop_icon() -> QIcon:
    return _drawn_icon(STOP_COLOR, lambda p: p.drawRoundedRect(QRectF(5, 5, 14, 14), 2, 2))


RETRY_COLOR = QColor("#229ED9")


def retry_icon() -> QIcon:
    """Freccia circolare."""
    def draw(p: QPainter) -> None:
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(QRectF(5, 5, 14, 14), 60 * 16, 290 * 16)
        p.setBrush(RETRY_COLOR)
        p.drawPolygon([QPointF(12.5, 1.5), QPointF(17.5, 5.5), QPointF(12, 8.5)])
    return _drawn_icon(RETRY_COLOR, draw)


def remove_icon() -> QIcon:
    """Croce."""
    def draw(p: QPainter) -> None:
        p.drawLine(QPointF(7, 7), QPointF(17, 17))
        p.drawLine(QPointF(17, 7), QPointF(7, 17))
    return _drawn_icon(STOP_COLOR, draw)


def icon_button(icon: QIcon, size: int, tooltip: str = "") -> QToolButton:
    """Pulsante solo icona: cosa fa lo dice il suggerimento al passaggio del mouse."""
    button = QToolButton()
    button.setIcon(icon)
    button.setIconSize(QSize(size, size))
    button.setAutoRaise(True)
    button.setToolTip(tooltip)
    return button


def file_actions(on_retry: Callable[[], None], on_drop: Callable[[], None]) -> QWidget:
    """«Riprova ora» e «Togli dalla coda» per una riga dei file in corso."""
    box = QWidget()
    h = QHBoxLayout(box)
    h.setContentsMargins(2, 0, 2, 0)
    h.setSpacing(0)
    retry = icon_button(retry_icon(), 14, tr("Riprova ora: salta l'attesa prima del prossimo tentativo, "
                                             "o ricomincia il download se è fermo (riparte da dove era arrivato)"))
    drop = icon_button(remove_icon(), 14, tr("Togli dalla coda: il file non viene scaricato, nemmeno al prossimo "
                                             "avvio (torna solo rianalizzando tutta la chat)"))
    retry.clicked.connect(on_retry)
    drop.clicked.connect(lambda: (drop.setEnabled(False), retry.setEnabled(False), on_drop()))
    h.addWidget(retry)
    h.addWidget(drop)
    return box


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
