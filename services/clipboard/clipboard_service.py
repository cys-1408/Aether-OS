"""Clipboard access via wl-clipboard; history ONLY when policy enables it."""
from __future__ import annotations

import shutil
import subprocess
import time

from aether_core.config import load_yaml
from aether_core import paths

HISTORY_FILE = paths.USER_STATE_DIR / "clipboard-history.json"


def enabled() -> bool:
    defaults = load_yaml("/etc/aether/privacy-defaults.yaml")
    return bool((defaults.get("clipboard") or {}).get("history_enabled", False))


def get() -> dict:
    if not shutil.which("wl-paste"):
        return {"supported": False, "reason": "wl-clipboard not installed"}
    try:
        out = subprocess.run(["wl-paste", "--no-newline"], capture_output=True, text=True, timeout=5)
        return {"supported": True, "text": out.stdout[:10000]}
    except subprocess.TimeoutExpired:
        return {"supported": False, "reason": "wl-paste timed out"}


def set_clip(text: str) -> dict:
    if not shutil.which("wl-copy"):
        return {"ok": False, "reason": "wl-clipboard not installed"}
    proc = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE, text=True)
    proc.communicate(text[:1_000_000])
    if enabled():
        _record(text)
    return {"ok": True}


def history() -> dict:
    if not enabled():
        return {"history_enabled": False, "reason": "disabled by privacy policy"}
    import json
    items = json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else []
    return {"history_enabled": True, "items": items[-50:]}


def _record(text: str) -> None:
    import json
    from sensitive_content_filter import is_sensitive
    if is_sensitive(text):
        return
    items = json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else []
    items.append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "preview": text[:120]})
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    import json as _json
    HISTORY_FILE.write_text(_json.dumps(items[-200:]))


def clear() -> dict:
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    return {"cleared": True}
