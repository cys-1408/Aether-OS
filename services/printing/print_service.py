"""CUPS printing via lp/lpstat — truthful when CUPS is absent."""
from __future__ import annotations

import shutil
import subprocess


def _run(argv: list[str], timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def status() -> dict:
    if not shutil.which("lpstat"):
        return {"supported": False, "reason": "CUPS not installed (lpstat missing)"}
    try:
        out = _run(["lpstat", "-p", "-d"])
        if out.returncode != 0:
            return {"supported": True, "printers": [], "default": None}
        printers, default = [], None
        for line in out.stdout.splitlines():
            if line.startswith("printer "):
                parts = line.split()
                printers.append({"name": parts[1], "state": " ".join(parts[2:])})
            if line.startswith("system default destination:"):
                default = line.split(":")[1].strip()
        return {"supported": True, "printers": printers, "default": default}
    except subprocess.TimeoutExpired:
        return {"supported": False, "reason": "lpstat timed out"}


def queue(printer: str | None = None) -> dict:
    if not shutil.which("lpstat"):
        return {"supported": False, "reason": "CUPS not installed"}
    argv = ["lpstat", "-W", "not-completed"]
    if printer:
        argv.append("-P" + printer)
    out = _run(argv)
    jobs = []
    for line in out.stdout.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4:
            jobs.append({"id": parts[0], "user": parts[1], "size": parts[2], "name": parts[3]})
    return {"jobs": jobs}


def print_file(path: str, printer: str | None = None, copies: int = 1) -> dict:
    if not shutil.which("lp"):
        return {"ok": False, "reason": "CUPS not installed"}
    argv = ["lp", "-n", str(max(1, min(99, copies)))]
    if printer:
        argv += ["-d", printer]
    argv.append(path)
    out = _run(argv)
    return {"ok": out.returncode == 0, "error": None if out.returncode == 0 else out.stderr.strip()}


def cancel(job_id: str) -> dict:
    if not shutil.which("cancel"):
        return {"ok": False, "reason": "CUPS not installed"}
    out = _run(["cancel", job_id])
    return {"ok": out.returncode == 0, "error": None if out.returncode == 0 else out.stderr.strip()}
