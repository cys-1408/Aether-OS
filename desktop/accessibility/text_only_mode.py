"""Text-only assistant mode: transcript-only panel, animation off."""
from __future__ import annotations

from shell_settings import settings


def enabled() -> bool:
    return settings().get_boolean("text-only-mode")


def set_enabled(on: bool, shell=None) -> None:
    settings().set_boolean("text-only-mode", on)
    if shell is not None:
        if on and hasattr(shell, "miso"):
            shell.miso.enable_reduced_motion()
        if hasattr(shell, "miso_panel"):
            shell.miso_panel.set_visible(not on) or shell.miso_panel.show_all()
