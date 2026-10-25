"""Priority scheduler with bounded concurrency (interactive first)."""
from __future__ import annotations

import threading
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from inference_api import validate_request  # noqa: E402
from request_router import queue_for  # noqa: E402
from cancellation import register, cancel, finish  # noqa: F401

_interactive = threading.Semaphore(1)
_background = threading.Semaphore(1)
_last_background = [0.0]


def infer_sync(svc, params: dict, stream: bool = False) -> dict:
    req = validate_request(params)
    if not svc.backend or not svc.backend.ensure_loaded():
        raise_error = True
    tok = register(req["request_id"])
    lane = queue_for(req["task_class"])
    sem = _interactive if lane == "interactive" else _background
    with sem:
        if lane == "background":
            _last_background[0] = time.time()
        if tok.cancelled():
            finish(req["request_id"])
            return {"request_id": req["request_id"], "state": "cancelled", "is_final": True}
        started = time.time()
        try:
            result = svc.backend.infer(req)
            finish(req["request_id"])
            return {"request_id": req["request_id"], "state": "final",
                    "text": result["text"], "is_final": True,
                    "usage": {"tokens_in": result.get("tokens_in", 0),
                              "tokens_out": result.get("tokens_out", 0),
                              "latency_ms": result.get("latency_ms",
                                                       int((time.time() - started) * 1000))}}
        except Exception as e:
            finish(req["request_id"])
            return {"request_id": req["request_id"], "state": "error", "is_final": True,
                    "error": {"code": "E_INFER", "message": str(e)}}
