"""Inference API boundary: schema validation + bounds."""
from __future__ import annotations

from aether_core.errors import IpcError

BOUNDS = {"max_tokens": (1, 2048), "timeout_s": (1, 120), "prompt_chars": (1, 131072)}


def validate_request(params: dict) -> dict:
    req = dict(params)
    req.setdefault("task_class", "assistant")
    req.setdefault("max_tokens", 256)
    req.setdefault("temperature", 0.7)
    req.setdefault("timeout_s", 60)
    req.setdefault("stream", False)
    if "request_id" not in req:
        raise IpcError("E_INVALID", "request_id required")
    if not isinstance(req.get("prompt"), str) or not req["prompt"].strip():
        raise IpcError("E_INVALID", "prompt required")
    for key, (lo, hi) in BOUNDS.items():
        if key == "prompt_chars":
            if not (lo <= len(req["prompt"]) <= hi):
                raise IpcError("E_INVALID", f"prompt length out of bounds [{lo},{hi}]")
        else:
            v = req.get(key)
            if not isinstance(v, (int, float)) or not (lo <= v <= hi):
                raise IpcError("E_INVALID", f"{key} out of bounds [{lo},{hi}]")
    if req["task_class"] not in ("assistant", "summarize", "code", "embeddings", "extraction", "concept"):
        raise IpcError("E_INVALID", f"unknown task_class {req['task_class']}")
    return req
