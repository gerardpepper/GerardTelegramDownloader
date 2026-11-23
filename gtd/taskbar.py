"""Barra di avanzamento sull'icona nella barra delle applicazioni.

Solo su Windows (ITaskbarList3/4); sugli altri sistemi TaskbarProgress non fa niente.
"""

import sys

NO_PROGRESS, INDETERMINATE, NORMAL, ERROR, PAUSED = 0x0, 0x1, 0x2, 0x4, 0x8

if sys.platform == "win32":
    from ._taskbar_win import TaskbarProgress  # noqa: E402,F401
else:
    class TaskbarProgress:
        def __init__(self, hwnd: int):
            pass

        def set_state(self, state: int) -> None:
            pass

        def set_value(self, done: int, total: int) -> None:
            pass

        def clear(self) -> None:
            pass
