"""GSettings-backed shell settings (schema: org.aether.Shell)."""
from __future__ import annotations

from gi.repository import Gio

SCHEMA_ID = "org.aether.Shell"
KEYS = {
    "distraction-protection": ("b", True),
    "auto-organize": ("b", False),
    "reduced-motion": ("b", False),
    "text-only-mode": ("b", False),
    "focus-minutes": ("i", 25),
    "miso-enabled": ("b", True),
    "high-contrast": ("b", False),
    "font-scale": ("d", 1.0),
}


def schema_xml() -> str:
    parts = [f'<key name="{k}" type="{t}"><default>{v}</default>'
             f"<summary>{k.replace('-', ' ')}</summary></key>"
             for k, (t, v) in KEYS.items()]
    return (f'<schemalist><schema id="{SCHEMA_ID}" path="/org/aether/shell/">'
            + "".join(parts) + "</schema></schemalist>")


def settings() -> Gio.Settings:
    src = Gio.SettingsSchemaSource.get_default()
    schema = src.lookup(SCHEMA_ID, False)
    if schema is None:
        # schema not compiled yet — install-time `glib-compile-schemas` fixes this;
        # fall back to a memory schema so the shell still runs
        import tempfile, os
        d = tempfile.mkdtemp(prefix="aether-schemas")
        (path := __import__("pathlib").Path(d) / "org.aether.Shell.gschema.xml").write_text(schema_xml())
        os.system(f"glib-compile-schemas {d} 2>/dev/null")
        Gio.SettingsSchemaSource.get_default()  # noqa: F841 — reload not guaranteed
        schema = Gio.SettingsSchemaSource.new_from_directory(d, src, False).lookup(SCHEMA_ID, False)
        if schema is None:
            raise RuntimeError("org.aether.Shell schema unavailable")
    return Gio.Settings.new_full(schema, None, None)
