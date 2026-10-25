"""Shell process ownership: spawn, environment, graceful termination."""

from __future__ import annotations

import os
import signal
import time

from pty_session import PtySession, default_env, detect_shell

TERM_GRACE_SECONDS = 2.0


class ShellProcess:
    """Wraps a PtySession with shell-specific semantics (env, cwd, kill)."""

    def __init__(self, cwd: str | None = None, command: list | None = None,
                 on_output=None, on_exit=None) -> None:
        self.cwd = cwd or os.getcwd()
        env = default_env()
        env["PWD"] = self.cwd
        if command:
            env["SHELL"] = command[0]
        self.session = PtySession(
            command=command if command else [detect_shell(), "-i"],
            cwd=self.cwd,
            env=env,
            on_output=on_output,
            on_exit=on_exit,
        )

    @property
    def pid(self) -> int:
        return self.session.pid

    def alive(self) -> bool:
        return self.session.alive()

    def write(self, data: bytes) -> bool:
        return self.session.write(data)

    def resize(self, cols: int, rows: int) -> None:
        self.session.resize(cols, rows)

    def terminate(self) -> int:
        """SIGTERM then SIGKILL after the grace window (real, ordered kill)."""
        return self.session.terminate(grace=TERM_GRACE_SECONDS)

    def interrupt(self) -> bool:
        return self.session.send_interrupt()

    @staticmethod
    def kill_tree(pid: int, sig: int = signal.SIGTERM) -> bool:
        """Signal a process group when possible (children included)."""
        try:
            os.killpg(os.getpgid(pid), sig)
            return True
        except (ProcessLookupError, PermissionError, OSError):
            try:
                os.kill(pid, sig)
                return True
            except (ProcessLookupError, PermissionError):
                return False


def wait_until_exited(pid: int, timeout: float) -> bool:
    """Poll waitpid without blocking the caller for longer than timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            found, _status = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            return True
        if found == pid:
            return True
        time.sleep(0.05)
    return False
