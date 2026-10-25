"""Bounded harmless inference proving the model actually works (measured)."""
from __future__ import annotations

import time


def smoke_check(backend) -> dict:
    if not backend or not backend.ensure_loaded():
        return {"ok": False, "reason": "backend not loaded"}
    started = time.time()
    try:
        result = backend.infer({"prompt": "Reply with the single word: ready",
                                "max_tokens": 8, "temperature": 0.0, "timeout_s": 30})
        text = (result.get("text") or "").strip()
        latency = int((time.time() - started) * 1000)
        return {"ok": bool(text), "reply": text[:40], "latency_ms": latency,
                "note": "measured on-device; tok/s available in usage"}
    except Exception as e:  # noqa: BLE001 — truthful failure
        return {"ok": False, "reason": str(e)}
