"""Registro a video, uguale nelle schede Download e Segui: righe colorate e avvisi nascondibili."""

from __future__ import annotations

import html
from collections import deque
from datetime import datetime

from PyQt6.QtGui import QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from ..i18n import tr

LOG_LIMIT = 20_000                     # righe conservate nel registro a video
WARNING_LEVELS = ("skip", "warning")   # righe gialle, nascondibili con «Mostra avvisi»


def log_line_html(level: str, text: str, prefix: str = "") -> str:
    """Riga del registro: ora in grigio, testo colorato per livello, prefix (es. nome della chat) in grassetto."""
    color = {"warning": "#d08700", "skip": "#d08700", "error": "#d03030", "success": "#2e9d4a"}.get(level)
    body = html.escape(text)
    if color:
        body = f'<span style="color:{color}">{body}</span>'
    if prefix:
        body = f"<b>{html.escape(prefix)}</b>&nbsp; {body}"
    stamp = datetime.now().strftime("%H:%M:%S")
    return f'<span style="color:gray">{stamp}</span>&nbsp; {body}'


class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._lines: deque[tuple[bool, str]] = deque(maxlen=LOG_LIMIT)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        header = QHBoxLayout()
        self.title = QLabel()
        header.addWidget(self.title)
        header.addStretch(1)
        self.warnings_chk = QCheckBox()
        self.warnings_chk.setChecked(True)
        self.warnings_chk.toggled.connect(self._rebuild)
        header.addWidget(self.warnings_chk)
        v.addLayout(header)
        self.view = QPlainTextEdit(readOnly=True)
        self.view.setMaximumBlockCount(LOG_LIMIT)
        v.addWidget(self.view, 1)
        self.retranslate()

    def retranslate(self) -> None:
        self.title.setText(tr("Registro"))
        self.warnings_chk.setText(tr("Mostra avvisi (righe gialle: file saltati, tentativi…)"))

    def add(self, level: str, text: str, prefix: str = "") -> None:
        """level: info | success | skip | warning | error. skip e warning sono le righe gialle «avvisi»."""
        line = log_line_html(level, text, prefix)
        is_warning = level in WARNING_LEVELS
        self._lines.append((is_warning, line))
        if not is_warning or self.warnings_chk.isChecked():
            self.view.appendHtml(line)

    def _rebuild(self) -> None:
        """Mostra o nasconde le righe gialle anche a posteriori: il registro le conserva comunque."""
        show = self.warnings_chk.isChecked()
        self.view.clear()
        cursor = QTextCursor(self.view.document())
        cursor.beginEditBlock()  # un solo aggiornamento a video: ~1 s anche con 20.000 righe
        first = True
        for is_warning, line in self._lines:
            if is_warning and not show:
                continue
            if not first:
                cursor.insertBlock()
            cursor.setCharFormat(QTextCharFormat())  # il colore di una riga non deve passare alla successiva
            cursor.insertHtml(line)
            first = False
        cursor.endEditBlock()
        self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().maximum())
