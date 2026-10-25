"""Login flow configuration: greetd + sway session."""
from __future__ import annotations

from pathlib import Path

GREETD_CONFIG = Path("/etc/greetd/config.toml")

DEFAULT_GREETD = """[terminal]
vt = 7

[default_session]
command = "sway --config /etc/aether/sway-session.config"
user = "greeter"
"""


def render_config() -> str:
    return DEFAULT_GREETD


def installed_config_ok() -> dict:
    if not GREETD_CONFIG.exists():
        return {"installed": False, "expected": DEFAULT_GREETD}
    return {"installed": True, "content": GREETD_CONFIG.read_text()}
