"""Locale page: list + set system locale via localectl."""
from __future__ import annotations

import subprocess


def available_locales() -> list[str]:
    try:
        out = subprocess.run(["localectl", "list-locales"], capture_output=True, text=True, timeout=10)
        return [l.strip() for l in out.stdout.splitlines() if l.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ["en_US.UTF-8"]


def set_locale(locale: str) -> dict:
    if locale not in available_locales():
        return {"ok": False, "error": f"locale not available: {locale}"}
    try:
        subprocess.run(["localectl", "set-locale", locale], check=True, timeout=15)
        return {"ok": True, "locale": locale}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "error": str(e)}


def run_cli_prompt() -> dict:
    locales = available_locales()
    for i, lc in enumerate(locales[:20], 1):
        print(f"  {i}. {lc}")
    choice = input(f"Choose locale [1-{min(20, len(locales))}] (default 1): ").strip() or "1"
    locale = locales[int(choice) - 1]
    result = set_locale(locale)
    print("locale set" if result.get("ok") else f"locale failed: {result.get('error')} (continuing)")
    return {"locale": locale}


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    combo = Gtk.ComboBoxText()
    for lc in available_locales():
        combo.append_text(lc)
    combo.set_active(0)
    box.pack_start(combo, False, False, 0)
    btn = Gtk.Button(label="Continue")

    def _next(_):
        locale = combo.get_active_text() or "en_US.UTF-8"
        set_locale(locale)
        commit("locale", {"locale": locale})
    btn.connect("clicked", _next)
    box.pack_start(btn, False, False, 0)
    return box
