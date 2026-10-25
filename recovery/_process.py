"""Process helpers for the recovery environment: strict argv, no shell."""

from __future__ import annotations

import shutil
import subprocess


class CommandResult:
    __slots__ = ("argv", "rc", "stdout", "stderr", "dry_run")

    def __init__(self, argv, rc, stdout, stderr, dry_run=False):
        self.argv = argv
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr
        self.dry_run = dry_run

    @property
    def ok(self) -> bool:
        return self.rc == 0


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise FileNotFoundError(f"required tool not installed: {name}")
    return path


def resolve_binary(name: str, *, dry_run: bool = False) -> str:
    path = shutil.which(name)
    if path is None:
        if dry_run:
            return name
        raise FileNotFoundError(f"required tool not installed: {name}")
    return path


def run_argv(argv: list[str], *, dry_run: bool = False,
             input_bytes: bytes | None = None, timeout: float = 1800.0,
             check: bool = False) -> CommandResult:
    argv = [str(a) for a in argv]
    if dry_run:
        result = CommandResult(argv, 0, "", "(dry-run: not executed)", True)
    else:
        proc = subprocess.run(  # noqa: S603 - argv list, no shell
            argv, input=input_bytes, capture_output=True, timeout=timeout,
        )
        result = CommandResult(
            argv, proc.returncode,
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"),
        )
    if check and not result.ok and not dry_run:
        raise RuntimeError(
            f"command failed rc={result.rc}: {' '.join(argv)}\n{result.stderr[-2000:]}"
        )
    return result


def is_root() -> bool:
    import os

    return os.geteuid() == 0
