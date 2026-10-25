"""Opt-in voice capture: records only after mic consent, hard-stopped."""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from aether_core import paths


def record(seconds: int) -> dict:
    seconds = max(1, min(120, int(seconds)))
    out_path = paths.USER_STATE_DIR / f"voice-capture-{int(time.time())}.wav"
    paths.USER_STATE_DIR.mkdir(parents=True, exist_ok=True)
    rec = shutil.which("pw-record") or shutil.which("parecord")
    if not rec:
        return {"ok": False, "reason": "no recorder (pw-record/parecord) installed"}
    try:
        subprocess.run([rec, "--channels=1", "--format=s16", str(out_path)],
                       timeout=seconds + 2, capture_output=True)
        return {"ok": out_path.exists(), "file": str(out_path), "seconds": seconds}
    except subprocess.TimeoutExpired:
        return {"ok": out_path.exists(), "file": str(out_path), "seconds": seconds}


def last_capture() -> dict | None:
    files = sorted(paths.USER_STATE_DIR.glob("voice-capture-*.wav"))
    return {"file": str(files[-1])} if files else None
