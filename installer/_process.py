"""Process execution helpers for the installer.

Every external command runs through here: strict argv lists, no shell
invocation, passphrases supplied via stdin bytes only, and every execution
logged (with secret redaction applied by the logger).
"""

from __future__ import annotations

import shutil
import subprocess

from .logging.installer_log import InstallerLog


class CommandResult:
    __slots__ = ("argv", "rc", "stdout", "stderr", "duration_s", "dry_run")

    def __init__(self, argv, rc, stdout, stderr, duration_s, dry_run=False):
        self.argv = argv
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr
        self.duration_s = duration_s
        self.dry_run = dry_run

    @property
    def ok(self) -> bool:
        return self.rc == 0

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CommandResult rc={self.rc} argv={self.argv[0]!r}>"


def require_binary(name: str) -> str:
    """Return the resolved path for a binary or raise FileNotFoundError."""
    path = shutil.which(name)
    if path is None:
        raise FileNotFoundError(f"required tool not installed: {name}")
    return path


def resolve_binary(name: str, *, dry_run: bool = False) -> str:
    """Like require_binary, but tolerates missing tools on dry runs."""
    path = shutil.which(name)
    if path is None:
        if dry_run:
            return name
        raise FileNotFoundError(f"required tool not installed: {name}")
    return path


def run_argv(
    argv: list[str],
    *,
    log: InstallerLog | None = None,
    step: str = "",
    dry_run: bool = False,
    input_bytes: bytes | None = None,
    timeout: float = 3600.0,
    check: bool = False,
    env_extra: dict | None = None,
) -> CommandResult:
    """Execute argv exactly (no shell). In dry_run, nothing is executed."""
    argv = [str(a) for a in argv]
    if dry_run:
        result = CommandResult(argv, 0, "", "(dry-run: not executed)", 0.0, dry_run=True)
    else:
        import time

        started = time.monotonic()
        env = None
        if env_extra:
            import os

            env = dict(os.environ)
            env.update(env_extra)
        proc = subprocess.run(  # noqa: S603 - argv list, no shell, audited
            argv,
            input=input_bytes,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
        duration = time.monotonic() - started
        result = CommandResult(
            argv, proc.returncode,
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"),
            duration,
        )
    if log is not None:
        log.command(argv, rc=result.rc, duration_s=result.duration_s, step=step,
                    dry_run=dry_run)
    if check and not result.ok and not dry_run:
        raise RuntimeError(
            f"command failed rc={result.rc}: {' '.join(argv)}\n{result.stderr[-2000:]}"
        )
    return result
