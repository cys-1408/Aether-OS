"""Session entry: launch sway with the Aether config, then the shell."""
from __future__ import annotations

import os
import shutil
import subprocess

SWAY_CONFIG = "/etc/aether/sway-session.config"


def ensure_config() -> str:
    src = shutil.which("sway")
    if not src:
        raise RuntimeError("sway not installed")
    if not os.path.exists(SWAY_CONFIG):
        here = os.path.dirname(__file__)
        default = os.path.join(here, "compositor_policy.conf")
        return default if os.path.exists(default) else SWAY_CONFIG
    return SWAY_CONFIG


def start_session() -> int:
    config = ensure_config()
    env = dict(os.environ)
    env.setdefault("AETHER_SESSION", "1")
    return subprocess.call(["sway", "-c", config], env=env)
