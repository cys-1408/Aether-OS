"""Per-service configuration with user-override merge."""
from __future__ import annotations

from pathlib import Path
from aether_core.config import load_yaml
from aether_core import paths


def service_config(name: str, *, user_scoped: bool = False) -> dict:
    """Merge /etc/aether/<name>.yaml with user override when user-scoped."""
    system_cfg = load_yaml(paths.SYSTEM_CONFIG_DIR / f"{name}.yaml")
    if not user_scoped:
        return system_cfg
    user_cfg = load_yaml(paths.USER_CONFIG_DIR / f"{name}.yaml")
    merged = dict(system_cfg)
    merged.update(user_cfg)
    return merged
