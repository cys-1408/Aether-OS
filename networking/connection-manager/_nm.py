"""Low-level NetworkManager (nmcli) helpers shared across AetherOS networking tools.

Rules enforced here (see CONVENTIONS.md section 2):
  * every external command runs from a list argv, never through a shell;
  * every call is bounded by an explicit timeout;
  * missing binaries are reported, never fabricated.

nmcli terse output (``-t``) escapes ``:`` and ``\\`` inside values with a
backslash.  ``parse_terse_line`` reverses that escaping so values may safely
contain colons (BSSIDs, connection names, DNS lists).
"""
from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Iterable, Sequence

LOG = logging.getLogger(__name__)


class ToolNotFound(RuntimeError):
    """Raised when a required external binary is not installed."""

    def __init__(self, tool: str, hint: str = "") -> None:
        self.tool = tool
        self.hint = hint
        super().__init__(f"required tool '{tool}' is not installed" + (f": {hint}" if hint else ""))


def tool_path(tool: str) -> str | None:
    """Return the absolute path of ``tool`` or None when not installed."""
    return shutil.which(tool)


def require_tool(tool: str, hint: str = "") -> str:
    """Return the absolute path of ``tool`` or raise ToolNotFound."""
    path = shutil.which(tool)
    if not path:
        raise ToolNotFound(tool, hint)
    return path


def run(argv: Sequence[str], *, timeout: float = 10.0, input_bytes: bytes | None = None,
        env: dict | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run ``argv`` (list of str) without a shell, bounded by ``timeout``."""
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
        check=False,
        env=env,
        cwd=cwd,
    )


def run_text(argv: Sequence[str], *, timeout: float = 10.0,
             input_bytes: bytes | None = None) -> tuple[int, str, str]:
    """Run ``argv`` and return ``(returncode, stdout_text, stderr_text)``."""
    proc = run(argv, timeout=timeout, input_bytes=input_bytes)
    return (
        proc.returncode,
        proc.stdout.decode("utf-8", "replace"),
        proc.stderr.decode("utf-8", "replace"),
    )


def parse_terse_line(line: str, fields: Sequence[str]) -> dict | None:
    """Parse one ``nmcli -t`` line into a dict keyed by ``fields``.

    Returns None for lines that do not carry the expected number of
    colon-separated fields (headers, blank lines, garbage).
    """
    line = line.rstrip("\n")
    if not line.strip():
        return None
    values: list[str] = []
    buf: list[str] = []
    escaped = False
    for ch in line:
        if escaped:
            buf.append(ch)
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == ":":
            values.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    values.append("".join(buf))
    if len(values) != len(fields):
        return None
    return dict(zip(fields, values))


def parse_terse_output(text: str, fields: Sequence[str]) -> list[dict]:
    """Parse full ``nmcli -t`` output into a list of row dicts."""
    rows: list[dict] = []
    for line in text.splitlines():
        row = parse_terse_line(line, fields)
        if row is not None:
            rows.append(row)
    return rows


def is_none(value: str) -> bool:
    """True when nmcli reports the placeholder value ``(none)`` / ``--`` / empty."""
    return value.strip() in ("", "(none)", "--")


def nmcli_version() -> str | None:
    """Return the nmcli version string, or None when nmcli is not installed."""
    if tool_path("nmcli") is None:
        return None
    rc, out, _ = run_text(["nmcli", "--version"], timeout=5.0)
    if rc != 0:
        return None
    # "nmcli tool, version 1.46.0"
    for token in out.strip().split():
        if token and token[0].isdigit():
            return token
    return out.strip() or None


def nmcli_available() -> bool:
    return tool_path("nmcli") is not None


def format_dns_list(dns: Iterable[str]) -> str:
    """Join a DNS server list the way nmcli expects it (single space-joined arg)."""
    return " ".join(d.strip() for d in dns if d.strip())
