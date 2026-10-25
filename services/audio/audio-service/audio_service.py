"""PipeWire audio via wpctl (pactl fallback) — real device/volume control."""
from __future__ import annotations

import re
import shutil
import subprocess


def _run(argv: list[str], timeout: int = 8) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def backend() -> dict:
    if shutil.which("wpctl"):
        try:
            out = _run(["wpctl", "status"])
            if out.returncode == 0:
                return {"server": "PipeWire", "tool": "wpctl"}
        except subprocess.TimeoutExpired:
            pass
    if shutil.which("pactl"):
        return {"server": "PulseAudio-compatible", "tool": "pactl"}
    return {"server": None, "reason": "no audio server reachable"}


def devices() -> dict:
    tool = backend().get("tool")
    sinks, sources = [], []
    if tool == "wpctl":
        try:
            out = _run(["wpctl", "status"])
            section = None
            for line in out.stdout.splitlines():
                if "Sinks:" in line:
                    section = "sink"
                elif "Sources:" in line:
                    section = "source"
                elif line.strip() and not line.startswith((" ", "\t")):
                    section = None
                m = re.match(r"\s*[\* ]?(\d+)\.(\d+\.)?\s+(.+?)(\s+\[Vol:.*\])?$", line)
                if m and section:
                    entry = {"id": int(m.group(1)), "name": m.group(3).strip(),
                             "default": "*" in line}
                    (sinks if section == "sink" else sources).append(entry)
        except subprocess.TimeoutExpired:
            pass
    return {"sinks": sinks, "sources": sources}


def set_volume(target: str, percent: int) -> dict:
    percent = max(0, min(150, int(percent)))
    tool = backend().get("tool")
    if tool == "wpctl":
        tid = "@DEFAULT_AUDIO_SINK@" if target == "sink" else ("@DEFAULT_AUDIO_SOURCE@" if target == "source" else target)
        try:
            out = _run(["wpctl", "set-volume", tid, f"{percent}%"])
            return {"ok": out.returncode == 0, "volume": percent}
        except FileNotFoundError:
            return {"ok": False, "error": "wpctl missing"}
    return {"ok": False, "error": "no audio tool"}


def set_default(kind: str, node_id: int) -> dict:
    tool = backend().get("tool")
    if tool == "wpctl":
        try:
            out = _run(["wpctl", "set-default", str(node_id)])
            return {"ok": out.returncode == 0, "kind": kind, "node": node_id}
        except FileNotFoundError:
            return {"ok": False, "error": "wpctl missing"}
    return {"ok": False, "error": "no audio tool"}
