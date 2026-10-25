"""Screen reader (AT-SPI) configuration."""
from __future__ import annotations

import os


def enable() -> dict:
    os.environ.setdefault("GTK_MODULES", "gail:atk-bridge")
    os.environ.setdefault("NO_AT_BRIDGE", "0")
    return {"atspi": "enabled", "orca": "install orca for speech output"}
