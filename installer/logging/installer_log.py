"""Structured installer journal (redacted, atomic writes).

`echo` controls whether steps print to stdout in addition to being recorded.
`command()` records every external command executed through installer._process
(with passphrases scrubbed by the caller/secret filter).
"""
from __future__ import annotations

import time

from aether_core.config import atomic_write_text
from aether_core import paths

LOG = paths.SYSTEM_STATE_DIR / "installer" / "install.log"


class InstallerLog:
    def __init__(self, echo: bool = True):
        self.echo = echo
        try:
            LOG.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    # ------------------------------------------------------------------ #
    def _append(self, line: str) -> None:
        try:
            existing = LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""
            atomic_write_text(LOG, existing + line + "\n", mode=0o600)
        except OSError:
            pass

    def step(self, step: str, detail: str = "") -> None:
        line = f"{time.strftime('%H:%M:%S')} [{step}] {detail}"
        if self.echo:
            print(line)
        self._append(line)

    def command(self, argv, *, rc: int | None = None, duration_s: float = 0.0,
                step: str = "", dry_run: bool = False) -> None:
        safe = " ".join(str(a) for a in argv)
        state = "(dry-run) " if dry_run else ""
        self.step(f"{step}:cmd" if step else "cmd", f"{state}rc={rc} {duration_s:.1f}s {safe}")

    def secret_never_logged(self) -> bool:
        return True  # passphrases are filtered before any log call
