"""Target configuration persisted to user config."""
from __future__ import annotations

from pathlib import Path

from aether_core.config import atomic_write_yaml, load_yaml
from aether_core import paths

CONF = paths.USER_CONFIG_DIR / "backup.yaml"


def current() -> dict:
    return load_yaml(CONF)


def set_target(target: str) -> dict:
    cfg = current()
    cfg["targets"] = [target]
    atomic_write_yaml(CONF, cfg)
    return {"target": target}


def choose_target(app, silent: bool = False) -> str | None:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    from desktop.dialogs.file_picker_adapter import choose_folder
    if silent:
        return (current().get("targets") or [None])[0]
    folder = choose_folder(None, "Choose backup target folder")
    if folder:
        set_target(folder)
    return folder
