"""Clean shutdown: save session, stop IPC, stop timers."""
from __future__ import annotations


def shutdown(shell) -> None:
    try:
        shell._server.stop()
    except Exception:
        pass
    try:
        shell.miso.stop()
    except Exception:
        pass
    try:
        shell.focus.end()
    except Exception:
        pass
