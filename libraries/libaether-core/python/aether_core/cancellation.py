"""Cooperative cancellation for long operations."""
from __future__ import annotations

import threading
from contextlib import contextmanager

from .errors import AetherError


class CancellationToken:
    """A thread-safe cancellation token passed through long-running work."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def cancelled(self) -> bool:
        return self._event.is_set()

    def wait(self, timeout: float) -> bool:
        """Wait until cancelled. Returns True if cancellation happened."""
        return self._event.wait(timeout)

    @contextmanager
    def scope(self):
        """Context manager: raises AetherError(E_CANCELLED) if cancelled."""
        if self.cancelled():
            raise AetherErrorCancelled()
        yield self
        if self.cancelled():
            raise AetherErrorCancelled()


class AetherErrorCancelled(AetherError):
    def __init__(self) -> None:
        super().__init__("E_CANCELLED", "operation cancelled", retriable=False)
