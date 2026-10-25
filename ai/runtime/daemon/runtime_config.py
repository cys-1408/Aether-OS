"""Runtime config: /etc/aether/runtime.yaml + user override."""
from __future__ import annotations

from pathlib import Path

from aether_core.config import load_yaml

DEFAULTS = {
    "model_store": "~/.local/share/aether/models",
    "catalog_path": "/usr/share/aether/ai/catalog/catalog.json",
    "endpoint_bind": "127.0.0.1",
    "inference": {"max_tokens": 2048, "default_timeout_s": 60, "max_timeout_s": 120},
    "memory": {"os_reserve_mb": 1024, "desktop_reserve_mb": 1024},
    "unload": {"idle_timeout_s": 900},
}


def load_runtime_config() -> dict:
    cfg = load_yaml("/etc/aether/runtime.yaml")
    user = load_yaml(Path.home() / ".config/aether/runtime.yaml")
    merged = dict(DEFAULTS)
    merged.update(cfg or {})
    merged.update(user or {})
    return merged
