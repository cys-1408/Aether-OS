"""Apply accessibility profiles via GSettings."""
from __future__ import annotations

import sys
from pathlib import Path
import yaml

PROFILES = Path(__file__).resolve().parent / "accessibility_profiles.yaml"


def apply(profile: str) -> dict:
    data = yaml.safe_load(PROFILES.read_text())
    spec = (data.get("profiles") or {}).get(profile)
    if not spec:
        return {"applied": False, "reason": f"unknown profile {profile!r}"}
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gio
        s = Gio.Settings.new("org.aether.Shell")
        s.set_boolean("reduced-motion", bool(spec.get("reduced_motion")))
        s.set_boolean("high-contrast", bool(spec.get("high_contrast")))
        s.set_boolean("text-only-mode", bool(spec.get("text_only")))
        s.set_double("font-scale", float(spec.get("font_scale", 1.0)))
        return {"applied": profile}
    except Exception as e:  # noqa: BLE001
        return {"applied": False, "reason": str(e)}
