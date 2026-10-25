"""Subprocess helpers for the AetherOS network-service.

List argv only, no shell, every call bounded by a timeout; missing tools are
reported, never faked.
"""
from __future__ import annotations

import logging
import shutil
import subprocess

LOG = logging.getLogger(__name__)


class ToolNotFound(RuntimeError):
    def __init__(self, tool: str, hint: str = "") -> None:
        self.tool = tool
        self.hint = hint
        super().__init__(f"required tool '{tool}' is not installed" + (f": {hint}" if hint else ""))


def require_tool(tool: str, hint: str = "") -> str:
    path = shutil.which(tool)
    if not path:
        raise ToolNotFound(tool, hint)
    return path


def run(argv: list[str] | tuple[str, ...], *, timeout: float = 10.0,
        input_bytes: bytes | None = None, check: bool = False) -> subprocess.CompletedProcess:
    if not isinstance(argv, (list, tuple)) or not all(isinstance(a, str) for a in argv):
        raise TypeError("argv must be a sequence of plain strings")
    argv = [str(a) for a in argv]
    LOG.debug("exec argv=%s timeout=%.1fs", argv, timeout)
    return subprocess.run(
        argv,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=check,
    )


def run_text(argv: list[str] | tuple[str, ...], *, timeout: float = 10.0,
             input_bytes: bytes | None = None) -> tuple[int, str, str]:
    proc = run(argv, timeout=timeout, input_bytes=input_bytes)
    return (proc.returncode,
            proc.stdout.decode("utf-8", "replace"),
            proc.stderr.decode("utf-8", "replace"))
