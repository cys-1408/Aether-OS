"""Real PTY sessions: pty.fork + exec of the user's shell, threaded reads."""

from __future__ import annotations

import fcntl
import os
import pty
import select
import signal
import struct
import termios
import threading
import time


def detect_shell() -> str:
    """The user's real login shell: $SHELL, else passwd, else /bin/sh."""
    env_shell = os.environ.get("SHELL")
    if env_shell and os.path.exists(env_shell):
        return env_shell
    try:
        import pwd

        entry = pwd.getpwuid(os.getuid())
        if entry.pw_shell and os.path.exists(entry.pw_shell):
            return entry.pw_shell
    except (KeyError, ImportError):
        pass
    return "/bin/sh"


def default_env() -> dict:
    env = dict(os.environ)
    env.setdefault("TERM", "xterm-256color")
    env.setdefault("COLORTERM", "truecolor")
    env["AETHER_TERMINAL"] = "1"
    env.pop("LINES", None)
    env.pop("COLUMNS", None)
    return env


class PtySession:
    """Owns a forked PTY. Output arrives on a reader thread via callbacks.

    All callbacks run on the reader thread; UI layers must marshal to the
    GTK main loop themselves (GLib.idle_add).
    """

    READ_CHUNK = 65536

    def __init__(self, command: list | None = None, cwd: str | None = None,
                 env: dict | None = None, on_output=None, on_exit=None) -> None:
        self.on_output = on_output
        self.on_exit = on_exit
        self._closed = False
        self._exit_code = None
        argv = command if command else [detect_shell(), "-i"]
        use_env = env if env is not None else default_env()

        pid, master_fd = pty.fork()
        if pid == 0:  # child: exec the shell inside the new pty
            try:
                if cwd and os.path.isdir(cwd):
                    os.chdir(cwd)
                os.execvpe(argv[0], argv, use_env)
            except BaseException:
                os._exit(127)
        self.pid = pid
        self.master_fd = master_fd
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    # -- IO ---------------------------------------------------------------------

    def write(self, data: bytes) -> bool:
        if self._closed or self.master_fd is None:
            return False
        try:
            os.write(self.master_fd, data)
            return True
        except OSError:
            return False

    def write_line(self, text: str) -> bool:
        return self.write(text.encode("utf-8") + b"\n")

    def send_interrupt(self) -> bool:
        """Deliver Ctrl+C (SIGINT) through the terminal line discipline."""
        return self.write(b"\x03")

    def send_eof(self) -> bool:
        return self.write(b"\x04")

    def resize(self, cols: int, rows: int) -> None:
        if self._closed or self.master_fd is None:
            return
        cols = max(int(cols), 2)
        rows = max(int(rows), 2)
        try:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
            os.kill(self.pid, signal.SIGWINCH)
        except (OSError, ProcessLookupError):
            pass

    # -- lifecycle ----------------------------------------------------------------

    def alive(self) -> bool:
        return self._exit_code is None and not self._closed

    def exit_code(self):
        return self._exit_code

    def terminate(self, grace: float = 2.0) -> int:
        """SIGTERM, wait the grace window, then SIGKILL. Returns exit code."""
        if self._closed:
            return self._exit_code if self._exit_code is not None else -1
        try:
            os.kill(self.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            if not self.alive():
                break
            time.sleep(0.05)
        if self.alive():
            try:
                os.kill(self.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        self.close()
        return self._exit_code if self._exit_code is not None else -1

    def close(self) -> None:
        self._closed = True
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None

    # -- internals -------------------------------------------------------------------

    def _read_loop(self) -> None:
        while not self._closed:
            try:
                ready, _, _ = select.select([self.master_fd], [], [], 0.25)
            except (OSError, ValueError):
                break
            if not ready:
                continue
            try:
                data = os.read(self.master_fd, self.READ_CHUNK)
            except OSError:
                break
            if not data:
                break
            if self.on_output is not None:
                self.on_output(data)
        self._reap()

    def _reap(self) -> None:
        code = 0
        try:
            _pid, status = os.waitpid(self.pid, os.WNOHANG)
            if _pid == self.pid:
                code = os.waitstatus_to_exitcode(status)
            else:
                code = 0
        except (ChildProcessError, OSError):
            code = 0
        self._exit_code = code
        self.close()
        if self.on_exit is not None:
            self.on_exit(code)
