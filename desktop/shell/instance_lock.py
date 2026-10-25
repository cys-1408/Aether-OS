"""Single-instance lock for the shell via an abstract unix socket bind."""
from __future__ import annotations

import logging
import os
import socket
from typing import Optional

LOG = logging.getLogger("aether.shell.lock")

LOCK_NAME = "\0aether-shell-instance-lock"


class InstanceLock:
    """Acquire/release an abstract-namespace unix socket as a process lock.

    Abstract sockets are released automatically by the kernel if the process
    dies, which avoids stale lock files on hard crashes.
    """

    def __init__(self) -> None:
        self._socket: Optional[socket.socket] = None

    def acquire(self) -> bool:
        """Try to bind the lock socket; False when another shell owns it."""
        if self._socket is not None:
            return True
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.bind(LOCK_NAME)
        except OSError:
            sock.close()
            return False
        sock.listen(0)
        self._socket = sock
        LOG.debug("instance lock acquired (pid %s)", os.getpid())
        return True

    def release(self) -> None:
        """Release the lock (idempotent)."""
        if self._socket is None:
            return
        try:
            self._socket.close()
        finally:
            self._socket = None
