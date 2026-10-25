"""First-boot model recommendation view data.

Reads the Runtime daemon's *actual* recommendation output over IPC; when the
Runtime is down (an ordinary, supported path) the presentation is "AI setup is
optional / Runtime unavailable", never a fabricated model list.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libraries/libaether-core/python"))
from aether_core.ipc import call  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402

RUNTIME_SOCK = "/run/aether/runtime.sock"


def recommendations(task_class: str = "assistant") -> dict:
    """Actual recommendations + limits from the Runtime (consent gate at
    download time stays inside Runtime.download_start)."""
    try:
        result = call(RUNTIME_SOCK, "Runtime.models_recommend",
                      {"task_class": task_class}, timeout=30)
    except IpcError as e:
        return {"available": False,
                "headline": None,
                "reason": str(e),
                "hint": ("AI setup is optional. You can finish setup without a "
                         "model and add one later in Settings → AI Runtime.")}
    recs = result.get("recommendations", []) if isinstance(result, dict) else []
    if not recs:
        return {"available": True, "recommendations": [],
                "headline": "No compatible model is available for this machine "
                            "right now.",
                "hint": "Setup finishes fine without a model."}
    top = recs[0]
    return {
        "available": True,
        "recommendations": recs,
        "headline": (f"Recommended: {top.get('name', top.get('model_id', ''))} "
                     f"— {top.get('task', task_class)}"),
        "limits": {
            "download_size": top.get("size_bytes"),
            "license": top.get("license"),
            "context": top.get("context"),
            "disk_required": top.get("disk_required_bytes", top.get("size_bytes")),
        },
    }


def summary_line(task_class: str = "assistant") -> str:
    data = recommendations(task_class)
    if not data.get("available"):
        return "Runtime unavailable — AI setup optional; skipping is supported."
    if not data.get("recommendations"):
        return data.get("headline", "")
    return data["headline"] + f" (+{len(data['recommendations']) - 1} more)"
