"""Authoritative mic state for the shell indicator."""
from microphone_permission import capture_state  # noqa: F401 — reuse real state

from aether_core.config import load_yaml


def indicator_state() -> dict:
    state = capture_state()
    defaults = load_yaml("/etc/aether/privacy-defaults.yaml")
    return state | {"consent_default": (defaults.get("microphone") or {}).get("default", "denied")}
