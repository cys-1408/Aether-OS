"""XWayland handling: enabled by default; legacy apps run under it."""
from __future__ import annotations

LEGACY_APPS = ("xterm", "gimp", "steam")
POLICY = "xwayland enabled; per-app quirks documented in hardware/known-limitations.md"


def supports_xwayland() -> bool:
    from compositor_adapter import CompositorAdapter
    return CompositorAdapter().run("xwayland enable").get("ok", False)
